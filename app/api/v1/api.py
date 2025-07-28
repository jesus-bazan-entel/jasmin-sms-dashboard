"""
Main API router for v1 endpoints
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    users,
    campaigns,
    contacts,
    messages,
    connectors,
    billing,
    analytics,
    webhooks,
    templates
)

api_router = APIRouter()

# Authentication endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# User management endpoints
api_router.include_router(users.router, prefix="/users", tags=["users"])

# Campaign management endpoints
api_router.include_router(campaigns.router, prefix="/campaigns", tags=["campaigns"])

# Contact management endpoints
api_router.include_router(contacts.router, prefix="/contacts", tags=["contacts"])

# Message endpoints
api_router.include_router(messages.router, prefix="/messages", tags=["messages"])

# SMPP Connector endpoints
api_router.include_router(connectors.router, prefix="/connectors", tags=["connectors"])

# Billing and subscription endpoints
api_router.include_router(billing.router, prefix="/billing", tags=["billing"])

# Analytics and reporting endpoints
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])

# Webhook endpoints
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])

# Template endpoints
api_router.include_router(templates.router, prefix="/templates", tags=["templates"])