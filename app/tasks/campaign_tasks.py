"""
Celery tasks for campaign processing
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any
from celery import current_task
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
import logging

from app.tasks import celery_app
from app.core.database import AsyncSessionLocal
from app.models.campaign import Campaign, CampaignStatus, CampaignContact
from app.models.contact import Contact
from app.models.message import Message, MessageStatus, MessageQueue
from app.models.user import User
from app.services.jasmin_service import JasminService
from app.websocket.manager import ConnectionManager
from app.services.billing_service import BillingService

logger = logging.getLogger(__name__)

@celery_app.task(bind=True)
def process_scheduled_campaigns(self):
    """Process campaigns scheduled to start"""
    return asyncio.run(_process_scheduled_campaigns_async(self))

async def _process_scheduled_campaigns_async(task):
    """Async implementation of scheduled campaign processing"""
    async with AsyncSessionLocal() as db:
        try:
            # Get campaigns scheduled to start
            now = datetime.utcnow()
            result = await db.execute(
                select(Campaign)
                .where(Campaign.status == CampaignStatus.SCHEDULED)
                .where(Campaign.scheduled_at <= now)
            )
            campaigns = result.scalars().all()
            
            processed_count = 0
            for campaign in campaigns:
                try:
                    await _start_campaign(db, campaign)
                    processed_count += 1
                    logger.info(f"Started campaign {campaign.id}")
                    
                except Exception as e:
                    logger.error(f"Failed to start campaign {campaign.id}: {e}")
                    campaign.status = CampaignStatus.FAILED
                    await db.commit()
            
            await db.commit()
            return f"Processed {processed_count} scheduled campaigns"
            
        except Exception as e:
            logger.error(f"Error processing scheduled campaigns: {e}")
            await db.rollback()
            raise

async def _start_campaign(db: AsyncSession, campaign: Campaign):
    """Start a campaign by creating message queue entries"""
    # Update campaign status
    campaign.status = CampaignStatus.RUNNING
    campaign.started_at = datetime.utcnow()
    
    # Get campaign contacts
    if campaign.contact_list_ids:
        # Get contacts from specified lists
        contacts_query = select(Contact).join(
            ContactListMembership
        ).where(
            ContactListMembership.contact_list_id.in_(campaign.contact_list_ids)
        ).where(
            Contact.status == ContactStatus.ACTIVE
        ).where(
            Contact.opted_in == True
        )
    else:
        # Get all user contacts if no specific lists
        contacts_query = select(Contact).where(
            Contact.user_id == campaign.user_id
        ).where(
            Contact.status == ContactStatus.ACTIVE
        ).where(
            Contact.opted_in == True
        )
    
    # Apply additional filters if specified
    if campaign.contact_filter:
        contacts_query = _apply_contact_filters(contacts_query, campaign.contact_filter)
    
    result = await db.execute(contacts_query)
    contacts = result.scalars().all()
    
    # Update estimated recipients
    campaign.total_recipients = len(contacts)
    campaign.estimated_recipients = len(contacts)
    
    # Create campaign contacts and queue messages
    batch_size = 1000
    for i in range(0, len(contacts), batch_size):
        batch_contacts = contacts[i:i + batch_size]
        await _queue_campaign_messages(db, campaign, batch_contacts)
    
    await db.commit()
    
    # Send WebSocket update
    connection_manager = ConnectionManager()
    await connection_manager.send_campaign_update(
        str(campaign.id),
        "running",
        {
            "total_recipients": campaign.total_recipients,
            "started_at": campaign.started_at.isoformat()
        }
    )

def _apply_contact_filters(query, filters: Dict[str, Any]):
    """Apply dynamic filters to contact query"""
    # This is a simplified implementation
    # In production, you'd want a more sophisticated filter system
    
    for field, condition in filters.items():
        if field == "tags" and "contains" in condition:
            query = query.where(Contact.tags.contains(condition["contains"]))
        elif field == "country" and "equals" in condition:
            query = query.where(Contact.country == condition["equals"])
        elif field == "custom_fields" and "contains" in condition:
            for key, value in condition["contains"].items():
                query = query.where(Contact.custom_fields[key].astext == value)
    
    return query

async def _queue_campaign_messages(db: AsyncSession, campaign: Campaign, contacts: List[Contact]):
    """Queue messages for a batch of contacts"""
    message_entries = []
    
    for contact in contacts:
        # Create campaign contact association
        campaign_contact = CampaignContact(
            campaign_id=campaign.id,
            contact_id=contact.id,
            personalized_message=_personalize_message(campaign.message_content, contact),
            personalization_data=_get_personalization_data(contact)
        )
        db.add(campaign_contact)
        
        # Create message queue entry
        message_data = {
            "campaign_id": str(campaign.id),
            "contact_id": str(contact.id),
            "user_id": str(campaign.user_id),
            "from_number": campaign.sender_id,
            "to_number": contact.phone_number,
            "content": campaign_contact.personalized_message,
            "priority": campaign.priority.value,
            "scheduled_at": datetime.utcnow().isoformat()
        }
        
        queue_entry = MessageQueue(
            queue_name="campaign_messages",
            priority=_get_priority_value(campaign.priority),
            message_data=message_data,
            scheduled_at=datetime.utcnow(),
            campaign_id=campaign.id
        )
        db.add(queue_entry)
    
    await db.commit()

def _personalize_message(template: str, contact: Contact) -> str:
    """Personalize message template with contact data"""
    personalized = template
    
    # Replace common placeholders
    replacements = {
        "{first_name}": contact.first_name or "",
        "{last_name}": contact.last_name or "",
        "{full_name}": contact.full_name or contact.display_name,
        "{company}": contact.company or "",
        "{phone}": contact.phone_number or ""
    }
    
    # Add custom fields
    if contact.custom_fields:
        for key, value in contact.custom_fields.items():
            replacements[f"{{{key}}}"] = str(value) if value else ""
    
    # Apply replacements
    for placeholder, value in replacements.items():
        personalized = personalized.replace(placeholder, value)
    
    return personalized

def _get_personalization_data(contact: Contact) -> Dict[str, Any]:
    """Get personalization data for contact"""
    return {
        "first_name": contact.first_name,
        "last_name": contact.last_name,
        "full_name": contact.full_name,
        "company": contact.company,
        "phone": contact.phone_number,
        "email": contact.email,
        "custom_fields": contact.custom_fields or {}
    }

def _get_priority_value(priority) -> int:
    """Convert priority enum to numeric value"""
    priority_map = {
        "low": 1,
        "normal": 5,
        "high": 8,
        "urgent": 10
    }
    return priority_map.get(priority.value, 5)

@celery_app.task(bind=True)
def process_campaign_completion(self, campaign_id: str):
    """Check and process campaign completion"""
    return asyncio.run(_process_campaign_completion_async(campaign_id))

async def _process_campaign_completion_async(campaign_id: str):
    """Async implementation of campaign completion processing"""
    async with AsyncSessionLocal() as db:
        try:
            # Get campaign
            result = await db.execute(
                select(Campaign).where(Campaign.id == uuid.UUID(campaign_id))
            )
            campaign = result.scalar_one_or_none()
            
            if not campaign:
                return f"Campaign {campaign_id} not found"
            
            # Check if all messages are processed
            pending_result = await db.execute(
                select(MessageQueue).where(
                    MessageQueue.campaign_id == campaign.id
                ).where(
                    MessageQueue.status.in_(["pending", "processing"])
                )
            )
            pending_messages = pending_result.scalars().all()
            
            if not pending_messages:
                # Campaign is complete
                campaign.status = CampaignStatus.COMPLETED
                campaign.completed_at = datetime.utcnow()
                
                # Calculate final statistics
                await _calculate_campaign_stats(db, campaign)
                
                await db.commit()
                
                # Send completion notification
                connection_manager = ConnectionManager()
                await connection_manager.send_campaign_update(
                    str(campaign.id),
                    "completed",
                    {
                        "completed_at": campaign.completed_at.isoformat(),
                        "total_sent": campaign.messages_sent,
                        "total_delivered": campaign.messages_delivered,
                        "delivery_rate": campaign.delivery_rate
                    }
                )
                
                return f"Campaign {campaign_id} completed successfully"
            
            return f"Campaign {campaign_id} still has {len(pending_messages)} pending messages"
            
        except Exception as e:
            logger.error(f"Error processing campaign completion: {e}")
            await db.rollback()
            raise

async def _calculate_campaign_stats(db: AsyncSession, campaign: Campaign):
    """Calculate final campaign statistics"""
    # Get message statistics
    from sqlalchemy import func
    
    stats_result = await db.execute(
        select(
            func.count(Message.id).label("total_sent"),
            func.sum(
                func.case(
                    (Message.status == MessageStatus.DELIVERED, 1),
                    else_=0
                )
            ).label("delivered"),
            func.sum(
                func.case(
                    (Message.status.in_([MessageStatus.FAILED, MessageStatus.REJECTED]), 1),
                    else_=0
                )
            ).label("failed"),
            func.sum(Message.cost).label("total_cost")
        ).where(Message.campaign_id == campaign.id)
    )
    
    stats = stats_result.first()
    
    # Update campaign statistics
    campaign.messages_sent = stats.total_sent or 0
    campaign.messages_delivered = stats.delivered or 0
    campaign.messages_failed = stats.failed or 0
    campaign.total_cost = float(stats.total_cost or 0)
    
    # Get click statistics
    click_result = await db.execute(
        select(
            func.count(ClickEvent.id).label("total_clicks"),
            func.count(func.distinct(ClickEvent.message_id)).label("unique_clicks")
        ).join(Message).where(Message.campaign_id == campaign.id)
    )
    
    click_stats = click_result.first()
    campaign.clicks_count = click_stats.total_clicks or 0
    campaign.unique_clicks = click_stats.unique_clicks or 0

@celery_app.task(bind=True)
def pause_campaign(self, campaign_id: str):
    """Pause a running campaign"""
    return asyncio.run(_pause_campaign_async(campaign_id))

async def _pause_campaign_async(campaign_id: str):
    """Async implementation of campaign pausing"""
    async with AsyncSessionLocal() as db:
        try:
            # Get campaign
            result = await db.execute(
                select(Campaign).where(Campaign.id == uuid.UUID(campaign_id))
            )
            campaign = result.scalar_one_or_none()
            
            if not campaign:
                return f"Campaign {campaign_id} not found"
            
            if campaign.status != CampaignStatus.RUNNING:
                return f"Campaign {campaign_id} is not running"
            
            # Pause campaign
            campaign.status = CampaignStatus.PAUSED
            
            # Pause pending message queue entries
            await db.execute(
                update(MessageQueue)
                .where(MessageQueue.campaign_id == campaign.id)
                .where(MessageQueue.status == "pending")
                .values(status="paused")
            )
            
            await db.commit()
            
            # Send WebSocket update
            connection_manager = ConnectionManager()
            await connection_manager.send_campaign_update(
                str(campaign.id),
                "paused",
                {"paused_at": datetime.utcnow().isoformat()}
            )
            
            return f"Campaign {campaign_id} paused successfully"
            
        except Exception as e:
            logger.error(f"Error pausing campaign: {e}")
            await db.rollback()
            raise

@celery_app.task(bind=True)
def resume_campaign(self, campaign_id: str):
    """Resume a paused campaign"""
    return asyncio.run(_resume_campaign_async(campaign_id))

async def _resume_campaign_async(campaign_id: str):
    """Async implementation of campaign resuming"""
    async with AsyncSessionLocal() as db:
        try:
            # Get campaign
            result = await db.execute(
                select(Campaign).where(Campaign.id == uuid.UUID(campaign_id))
            )
            campaign = result.scalar_one_or_none()
            
            if not campaign:
                return f"Campaign {campaign_id} not found"
            
            if campaign.status != CampaignStatus.PAUSED:
                return f"Campaign {campaign_id} is not paused"
            
            # Resume campaign
            campaign.status = CampaignStatus.RUNNING
            
            # Resume paused message queue entries
            await db.execute(
                update(MessageQueue)
                .where(MessageQueue.campaign_id == campaign.id)
                .where(MessageQueue.status == "paused")
                .values(status="pending")
            )
            
            await db.commit()
            
            # Send WebSocket update
            connection_manager = ConnectionManager()
            await connection_manager.send_campaign_update(
                str(campaign.id),
                "running",
                {"resumed_at": datetime.utcnow().isoformat()}
            )
            
            return f"Campaign {campaign_id} resumed successfully"
            
        except Exception as e:
            logger.error(f"Error resuming campaign: {e}")
            await db.rollback()
            raise

@celery_app.task(bind=True)
def cancel_campaign(self, campaign_id: str):
    """Cancel a campaign"""
    return asyncio.run(_cancel_campaign_async(campaign_id))

async def _cancel_campaign_async(campaign_id: str):
    """Async implementation of campaign cancellation"""
    async with AsyncSessionLocal() as db:
        try:
            # Get campaign
            result = await db.execute(
                select(Campaign).where(Campaign.id == uuid.UUID(campaign_id))
            )
            campaign = result.scalar_one_or_none()
            
            if not campaign:
                return f"Campaign {campaign_id} not found"
            
            if campaign.status in [CampaignStatus.COMPLETED, CampaignStatus.CANCELLED]:
                return f"Campaign {campaign_id} is already {campaign.status.value}"
            
            # Cancel campaign
            campaign.status = CampaignStatus.CANCELLED
            campaign.completed_at = datetime.utcnow()
            
            # Cancel pending message queue entries
            await db.execute(
                update(MessageQueue)
                .where(MessageQueue.campaign_id == campaign.id)
                .where(MessageQueue.status.in_(["pending", "paused"]))
                .values(status="cancelled")
            )
            
            # Calculate final statistics
            await _calculate_campaign_stats(db, campaign)
            
            await db.commit()
            
            # Send WebSocket update
            connection_manager = ConnectionManager()
            await connection_manager.send_campaign_update(
                str(campaign.id),
                "cancelled",
                {
                    "cancelled_at": campaign.completed_at.isoformat(),
                    "messages_sent": campaign.messages_sent
                }
            )
            
            return f"Campaign {campaign_id} cancelled successfully"
            
        except Exception as e:
            logger.error(f"Error cancelling campaign: {e}")
            await db.rollback()
            raise

@celery_app.task(bind=True)
def process_recurring_campaigns(self):
    """Process recurring campaigns that need to be executed"""
    return asyncio.run(_process_recurring_campaigns_async())

async def _process_recurring_campaigns_async():
    """Async implementation of recurring campaign processing"""
    async with AsyncSessionLocal() as db:
        try:
            # Get recurring campaigns due for execution
            now = datetime.utcnow()
            result = await db.execute(
                select(Campaign)
                .where(Campaign.is_recurring == True)
                .where(Campaign.status == CampaignStatus.SCHEDULED)
                .where(Campaign.next_run_at <= now)
            )
            campaigns = result.scalars().all()
            
            processed_count = 0
            for campaign in campaigns:
                try:
                    # Create a new campaign instance for this execution
                    new_campaign = Campaign(
                        name=f"{campaign.name} - {now.strftime('%Y-%m-%d %H:%M')}",
                        description=campaign.description,
                        user_id=campaign.user_id,
                        campaign_type=campaign.campaign_type,
                        status=CampaignStatus.RUNNING,
                        priority=campaign.priority,
                        message_content=campaign.message_content,
                        sender_id=campaign.sender_id,
                        contact_list_ids=campaign.contact_list_ids,
                        contact_filter=campaign.contact_filter,
                        delivery_speed=campaign.delivery_speed,
                        track_clicks=campaign.track_clicks,
                        cost_per_message=campaign.cost_per_message
                    )
                    
                    db.add(new_campaign)
                    await db.flush()  # Get the ID
                    
                    # Start the new campaign
                    await _start_campaign(db, new_campaign)
                    
                    # Update next run time for the recurring campaign
                    campaign.next_run_at = _calculate_next_run_time(
                        campaign.recurrence_pattern,
                        now
                    )
                    
                    processed_count += 1
                    logger.info(f"Created recurring campaign execution {new_campaign.id}")
                    
                except Exception as e:
                    logger.error(f"Failed to process recurring campaign {campaign.id}: {e}")
            
            await db.commit()
            return f"Processed {processed_count} recurring campaigns"
            
        except Exception as e:
            logger.error(f"Error processing recurring campaigns: {e}")
            await db.rollback()
            raise

def _calculate_next_run_time(recurrence_pattern: Dict[str, Any], current_time: datetime) -> datetime:
    """Calculate next run time based on recurrence pattern"""
    pattern_type = recurrence_pattern.get("type", "daily")
    interval = recurrence_pattern.get("interval", 1)
    
    if pattern_type == "daily":
        return current_time + timedelta(days=interval)
    elif pattern_type == "weekly":
        return current_time + timedelta(weeks=interval)
    elif pattern_type == "monthly":
        # Simplified monthly calculation
        return current_time + timedelta(days=30 * interval)
    else:
        # Default to daily
        return current_time + timedelta(days=1)