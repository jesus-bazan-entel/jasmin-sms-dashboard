import uuid
from pydantic import BaseModel
from typing import Optional, Dict, Any
from typing import List
from datetime import datetime

# Base schema with common fields for a connector
class ConnectorBase(BaseModel):
    name: str
    connector_type: str
    config: Dict[str, Any]
    is_active: bool = True

# Schema for creating a new connector
class ConnectorCreate(ConnectorBase):
    pass

# Schema for updating an existing connector
class ConnectorUpdate(BaseModel):
    name: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

# Schema for returning a connector in API responses
class ConnectorResponse(ConnectorBase):
    id: uuid.UUID

    class Config:
        from_attributes = True

# Schema for returning a list of connectors
class ConnectorListResponse(BaseModel):
    items: List[ConnectorResponse]
    total: int

# Schema for creating a new route
class RouteCreate(BaseModel):
    route_type: str
    connector_id: uuid.UUID
    order: int
    filters: Optional[Dict[str, Any]] = None

# Schema for updating an existing route
class RouteUpdate(BaseModel):
    order: Optional[int] = None
    filters: Optional[Dict[str, Any]] = None

# Schema for returning route data
class RouteResponse(RouteCreate):
    id: uuid.UUID

    class Config:
        from_attributes = True

# Schema for creating a new filter
class FilterCreate(BaseModel):
    filter_type: str
    connector_id: uuid.UUID
    config: Dict[str, Any]

# Schema for updating an existing filter
class FilterUpdate(BaseModel):
    config: Optional[Dict[str, Any]] = None

# Schema for returning filter data
class FilterResponse(FilterCreate):
    id: uuid.UUID

    class Config:
        from_attributes = True

# Schema for returning connector log data
class ConnectorLogResponse(BaseModel):
    id: uuid.UUID
    timestamp: datetime
    level: str
    message: str

    class Config:
        from_attributes = True

# Schema for returning connector statistics
class ConnectorStatsResponse(BaseModel):
    messages_sent: int
    messages_received: int
    uptime_seconds: float
    throughput_mps: float
