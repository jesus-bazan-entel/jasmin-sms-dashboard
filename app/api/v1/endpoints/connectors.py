"""
SMPP Connector management endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
import uuid

from app.core.database import get_db
from app.core.security import get_db 
from app.core.security import get_current_user, require_permission
from app.models.user import User
from app.models.connector import SMPPConnector, Route, Filter, ConnectorLog
from app.schemas.connector import (
    ConnectorCreate,
    ConnectorUpdate,
    ConnectorResponse,
    ConnectorListResponse,
    RouteCreate,
    RouteUpdate,
    RouteResponse,
    FilterCreate,
    FilterUpdate,
    FilterResponse,
    ConnectorLogResponse,
    ConnectorStatsResponse
)
from app.services.jasmin_service import JasminService
from app.services.connector_service import ConnectorService
from app.websocket.manager import ConnectionManager

router = APIRouter()

# Initialize services
jasmin_service = JasminService()
connection_manager = ConnectionManager()

@router.get("/", response_model=ConnectorListResponse)
async def list_connectors(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List SMPP connectors with filtering and pagination"""
    require_permission(current_user.role, "connector:read")
    
    query = select(SMPPConnector).where(SMPPConnector.user_id == current_user.id)
    
    # Apply filters
    if status:
        query = query.where(SMPPConnector.status == status)
    
    if search:
        query = query.where(
            SMPPConnector.label.ilike(f"%{search}%") |
            SMPPConnector.cid.ilike(f"%{search}%") |
            SMPPConnector.host.ilike(f"%{search}%")
        )
    
    # Get total count
    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar()
    
    # Apply pagination
    query = query.offset(skip).limit(limit).order_by(SMPPConnector.created_at.desc())
    
    result = await db.execute(query)
    connectors = result.scalars().all()
    
    # Get real-time status from Jasmin
    connector_status = await jasmin_service.get_connector_status()
    
    connector_responses = []
    for connector in connectors:
        # Update status from Jasmin if available
        jasmin_status = connector_status.get(connector.cid, {})
        if jasmin_status:
            connector.status = jasmin_status.get("status", connector.status)
        
        connector_responses.append(ConnectorResponse.from_orm(connector))
    
    return ConnectorListResponse(
        connectors=connector_responses,
        total=total,
        skip=skip,
        limit=limit
    )

@router.post("/", response_model=ConnectorResponse)
async def create_connector(
    connector_data: ConnectorCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new SMPP connector"""
    require_permission(current_user.role, "connector:create")
    
    # Check if CID already exists
    existing = await db.execute(
        select(SMPPConnector).where(SMPPConnector.cid == connector_data.cid)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Connector with CID '{connector_data.cid}' already exists"
        )
    
    # Create connector in database
    connector = SMPPConnector(
        user_id=current_user.id,
        **connector_data.dict()
    )
    
    db.add(connector)
    await db.commit()
    await db.refresh(connector)
    
    # Create connector in Jasmin
    try:
        jasmin_config = {
            "cid": connector.cid,
            "host": connector.host,
            "port": connector.port,
            "username": connector.username,
            "password": connector.password,
            "system_id": connector.system_id,
            "system_type": connector.system_type,
            "bind_type": connector.bind_type.value,
            "bind_to": connector.bind_to,
            "submit_throughput": connector.submit_throughput,
            "deliver_throughput": connector.deliver_throughput
        }
        
        success = await jasmin_service.create_connector(jasmin_config)
        if not success:
            # Rollback database creation if Jasmin creation fails
            await db.delete(connector)
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create connector in Jasmin SMS Gateway"
            )
    
    except Exception as e:
        # Rollback database creation
        await db.delete(connector)
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create connector: {str(e)}"
        )
    
    # Send real-time update
    await connection_manager.broadcast_to_channel("connectors", {
        "type": "connector_created",
        "connector": ConnectorResponse.from_orm(connector).dict()
    })
    
    return ConnectorResponse.from_orm(connector)

@router.get("/{connector_id}", response_model=ConnectorResponse)
async def get_connector(
    connector_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get connector by ID"""
    require_permission(current_user.role, "connector:read")
    
    result = await db.execute(
        select(SMPPConnector)
        .where(SMPPConnector.id == connector_id)
        .where(SMPPConnector.user_id == current_user.id)
        .options(selectinload(SMPPConnector.routes))
    )
    connector = result.scalar_one_or_none()
    
    if not connector:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connector not found"
        )
    
    # Get real-time status from Jasmin
    try:
        jasmin_status = await jasmin_service.get_connector_status(connector.cid)
        if jasmin_status:
            connector.status = jasmin_status.get("status", connector.status)
            connector.last_connected = jasmin_status.get("last_activity")
    except Exception:
        pass  # Use database status if Jasmin is unavailable
    
    return ConnectorResponse.from_orm(connector)

@router.put("/{connector_id}", response_model=ConnectorResponse)
async def update_connector(
    connector_id: uuid.UUID,
    connector_data: ConnectorUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update connector configuration"""
    require_permission(current_user.role, "connector:update")
    
    result = await db.execute(
        select(SMPPConnector)
        .where(SMPPConnector.id == connector_id)
        .where(SMPPConnector.user_id == current_user.id)
    )
    connector = result.scalar_one_or_none()
    
    if not connector:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connector not found"
        )
    
    # Update connector in database
    update_data = connector_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(connector, field, value)
    
    await db.commit()
    await db.refresh(connector)
    
    # Update connector in Jasmin (if needed)
    try:
        # Stop connector if running
        if connector.status in ["started", "bound"]:
            await jasmin_service.stop_connector(connector.cid)
        
        # Update configuration would require recreating in Jasmin
        # This is a simplified approach - in production, you might want
        # to support partial updates
        
    except Exception as e:
        print(f"Warning: Failed to update connector in Jasmin: {e}")
    
    # Send real-time update
    await connection_manager.broadcast_to_channel("connectors", {
        "type": "connector_updated",
        "connector": ConnectorResponse.from_orm(connector).dict()
    })
    
    return ConnectorResponse.from_orm(connector)

@router.delete("/{connector_id}")
async def delete_connector(
    connector_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete connector"""
    require_permission(current_user.role, "connector:delete")
    
    result = await db.execute(
        select(SMPPConnector)
        .where(SMPPConnector.id == connector_id)
        .where(SMPPConnector.user_id == current_user.id)
    )
    connector = result.scalar_one_or_none()
    
    if not connector:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connector not found"
        )
    
    # Stop and remove from Jasmin first
    try:
        if connector.status in ["started", "bound"]:
            await jasmin_service.stop_connector(connector.cid)
        
        # Remove from Jasmin (implementation depends on Jasmin API)
        # await jasmin_service.delete_connector(connector.cid)
        
    except Exception as e:
        print(f"Warning: Failed to remove connector from Jasmin: {e}")
    
    # Delete from database
    await db.delete(connector)
    await db.commit()
    
    # Send real-time update
    await connection_manager.broadcast_to_channel("connectors", {
        "type": "connector_deleted",
        "connector_id": str(connector_id)
    })
    
    return {"message": "Connector deleted successfully"}

@router.post("/{connector_id}/start")
async def start_connector(
    connector_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Start SMPP connector"""
    require_permission(current_user.role, "connector:update")
    
    result = await db.execute(
        select(SMPPConnector)
        .where(SMPPConnector.id == connector_id)
        .where(SMPPConnector.user_id == current_user.id)
    )
    connector = result.scalar_one_or_none()
    
    if not connector:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connector not found"
        )
    
    # Start connector in Jasmin
    try:
        success = await jasmin_service.start_connector(connector.cid)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to start connector in Jasmin SMS Gateway"
            )
        
        # Update status in database
        connector.status = "starting"
        await db.commit()
        
        # Send real-time update
        await connection_manager.send_connector_update(
            connector.cid,
            "starting",
            {"message": "Connector is starting"}
        )
        
        return {"message": "Connector start command sent successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start connector: {str(e)}"
        )

@router.post("/{connector_id}/stop")
async def stop_connector(
    connector_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Stop SMPP connector"""
    require_permission(current_user.role, "connector:update")
    
    result = await db.execute(
        select(SMPPConnector)
        .where(SMPPConnector.id == connector_id)
        .where(SMPPConnector.user_id == current_user.id)
    )
    connector = result.scalar_one_or_none()
    
    if not connector:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connector not found"
        )
    
    # Stop connector in Jasmin
    try:
        success = await jasmin_service.stop_connector(connector.cid)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to stop connector in Jasmin SMS Gateway"
            )
        
        # Update status in database
        connector.status = "stopping"
        await db.commit()
        
        # Send real-time update
        await connection_manager.send_connector_update(
            connector.cid,
            "stopping",
            {"message": "Connector is stopping"}
        )
        
        return {"message": "Connector stop command sent successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop connector: {str(e)}"
        )

@router.get("/{connector_id}/logs", response_model=List[ConnectorLogResponse])
async def get_connector_logs(
    connector_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    level: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get connector logs"""
    require_permission(current_user.role, "logs:read")
    
    # Verify connector ownership
    result = await db.execute(
        select(SMPPConnector)
        .where(SMPPConnector.id == connector_id)
        .where(SMPPConnector.user_id == current_user.id)
    )
    connector = result.scalar_one_or_none()
    
    if not connector:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connector not found"
        )
    
    # Build query
    query = select(ConnectorLog).where(ConnectorLog.connector_id == connector_id)
    
    if level:
        query = query.where(ConnectorLog.level == level.upper())
    
    query = query.order_by(ConnectorLog.timestamp.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    logs = result.scalars().all()
    
    return [ConnectorLogResponse.from_orm(log) for log in logs]

@router.get("/{connector_id}/stats", response_model=ConnectorStatsResponse)
async def get_connector_stats(
    connector_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get connector statistics"""
    require_permission(current_user.role, "connector:read")
    
    result = await db.execute(
        select(SMPPConnector)
        .where(SMPPConnector.id == connector_id)
        .where(SMPPConnector.user_id == current_user.id)
    )
    connector = result.scalar_one_or_none()
    
    if not connector:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connector not found"
        )
    
    # Get real-time stats from Jasmin
    try:
        jasmin_stats = await jasmin_service.get_connector_status(connector.cid)
        
        return ConnectorStatsResponse(
            connector_id=str(connector.id),
            cid=connector.cid,
            status=jasmin_stats.get("status", connector.status),
            total_sent=jasmin_stats.get("messages_sent", connector.total_sent),
            total_received=jasmin_stats.get("messages_received", connector.total_received),
            total_failed=jasmin_stats.get("messages_failed", connector.total_failed),
            connection_count=connector.connection_count,
            error_count=connector.error_count,
            uptime_percentage=connector.uptime_percentage,
            last_connected=connector.last_connected,
            last_error=connector.last_error
        )
        
    except Exception:
        # Return database stats if Jasmin is unavailable
        return ConnectorStatsResponse(
            connector_id=str(connector.id),
            cid=connector.cid,
            status=connector.status,
            total_sent=connector.total_sent,
            total_received=connector.total_received,
            total_failed=connector.total_failed,
            connection_count=connector.connection_count,
            error_count=connector.error_count,
            uptime_percentage=connector.uptime_percentage,
            last_connected=connector.last_connected,
            last_error=connector.last_error
        )

@router.get("/status/all")
async def get_all_connectors_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get real-time status of all user's connectors"""
    require_permission(current_user.role, "connector:read")
    
    # Get user's connectors
    result = await db.execute(
        select(SMPPConnector).where(SMPPConnector.user_id == current_user.id)
    )
    connectors = result.scalars().all()
    
    # Get status from Jasmin
    try:
        jasmin_status = await jasmin_service.get_connector_status()
        
        status_data = {}
        for connector in connectors:
            connector_status = jasmin_status.get(connector.cid, {})
            status_data[connector.cid] = {
                "id": str(connector.id),
                "cid": connector.cid,
                "label": connector.label,
                "status": connector_status.get("status", connector.status),
                "host": connector.host,
                "port": connector.port,
                "last_activity": connector_status.get("last_activity"),
                "messages_sent": connector_status.get("messages_sent", 0),
                "messages_received": connector_status.get("messages_received", 0)
            }
        
        return {"connectors": status_data}
        
    except Exception as e:
        # Return database status if Jasmin is unavailable
        status_data = {}
        for connector in connectors:
            status_data[connector.cid] = {
                "id": str(connector.id),
                "cid": connector.cid,
                "label": connector.label,
                "status": connector.status,
                "host": connector.host,
                "port": connector.port,
                "error": f"Unable to get real-time status: {str(e)}"
            }
        
        return {"connectors": status_data, "warning": "Real-time status unavailable"}

@router.get("/")
async def get_connectors(db: AsyncSession = Depends(get_db)):
    connector_service = ConnectorService(db)
    return await connector_service.get_all_connectors()
