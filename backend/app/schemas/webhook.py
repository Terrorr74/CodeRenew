"""
Pydantic schemas for webhook configurations and deliveries
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, validator, HttpUrl
import re


# ============================================================================
# Webhook Config Schemas
# ============================================================================

class WebhookConfigBase(BaseModel):
    """Base schema for webhook configuration"""
    name: str = Field(..., min_length=1, max_length=255, description="User-friendly name for the webhook")
    type: str = Field(..., description="Webhook type: slack, teams, email, or http")
    url: Optional[str] = Field(None, description="Webhook URL (not required for email type)")
    enabled: bool = Field(True, description="Whether the webhook is active")
    events: List[str] = Field(..., description="List of events to trigger webhook: scan_completed, vulnerability_found")
    
    @validator('type')
    def validate_type(cls, v):
        """Validate webhook type"""
        allowed_types = ['slack', 'teams', 'email', 'http']
        if v not in allowed_types:
            raise ValueError(f"Type must be one of: {', '.join(allowed_types)}")
        return v
    
    @validator('url')
    def validate_url(cls, v, values):
        """Validate URL based on webhook type"""
        webhook_type = values.get('type')
        
        # Email type doesn't need URL
        if webhook_type == 'email':
            return v
        
        # Other types require URL
        if not v:
            raise ValueError(f"URL is required for {webhook_type} webhooks")
        
        # Validate URL format
        if not v.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")
        
        # Slack-specific validation
        if webhook_type == 'slack' and not v.startswith('https://hooks.slack.com/'):
            raise ValueError("Slack webhook URL must start with https://hooks.slack.com/")
        
        # Teams-specific validation
        if webhook_type == 'teams' and 'webhook.office.com' not in v:
            raise ValueError("Teams webhook URL must contain webhook.office.com")
        
        return v
    
    @validator('events')
    def validate_events(cls, v):
        """Validate event types"""
        allowed_events = ['scan_completed', 'vulnerability_found']
        if not v:
            raise ValueError("At least one event must be specified")
        
        for event in v:
            if event not in allowed_events:
                raise ValueError(f"Event must be one of: {', '.join(allowed_events)}")
        
        return v


class WebhookConfigCreate(WebhookConfigBase):
    """Schema for creating a webhook configuration"""
    pass


class WebhookConfigUpdate(BaseModel):
    """Schema for updating a webhook configuration"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    url: Optional[str] = None
    enabled: Optional[bool] = None
    events: Optional[List[str]] = None
    
    @validator('events')
    def validate_events(cls, v):
        """Validate event types if provided"""
        if v is not None:
            allowed_events = ['scan_completed', 'vulnerability_found']
            if not v:
                raise ValueError("At least one event must be specified")
            
            for event in v:
                if event not in allowed_events:
                    raise ValueError(f"Event must be one of: {', '.join(allowed_events)}")
        
        return v


class WebhookConfigResponse(BaseModel):
    """Schema for webhook configuration response (URL masked for security)"""
    id: str
    user_id: str
    name: str
    type: str
    url_masked: Optional[str] = Field(None, description="Masked webhook URL for security")
    enabled: bool
    events: List[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
    
    @staticmethod
    def mask_url(url: Optional[str]) -> Optional[str]:
        """Mask URL for security (show only first 20 and last 10 chars)"""
        if not url:
            return None
        if len(url) <= 30:
            return url[:10] + "..." + url[-5:]
        return url[:20] + "..." + url[-10:]


# ============================================================================
# Webhook Delivery Schemas
# ============================================================================

class WebhookDeliveryResponse(BaseModel):
    """Schema for webhook delivery response"""
    id: str
    webhook_config_id: str
    event_type: str
    payload: dict
    status: str
    attempts: int
    last_attempt_at: Optional[datetime]
    response_code: Optional[int]
    response_body: Optional[str] = Field(None, max_length=1000, description="Truncated response body")
    error_message: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class WebhookDeliveryListResponse(BaseModel):
    """Paginated list of webhook deliveries"""
    deliveries: List[WebhookDeliveryResponse]
    total: int
    page: int
    per_page: int


class WebhookTestRequest(BaseModel):
    """Schema for testing a webhook"""
    test_message: Optional[str] = Field("This is a test webhook from CodeRenew", description="Custom test message")


class WebhookTestResponse(BaseModel):
    """Schema for webhook test response"""
    success: bool
    message: str
    delivery_id: Optional[str]
    response_code: Optional[int]
    error: Optional[str]
