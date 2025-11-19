from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class OrderCreate(BaseModel):
    """Schema for creating a new order from intake form"""
    stripe_session_id: str = Field(..., description="Stripe checkout session ID")
    agency_name: str = Field(..., min_length=1, max_length=255)
    contact_email: EmailStr
    site_name: str = Field(..., min_length=1, max_length=255)
    site_url: Optional[str] = Field(None, max_length=500)
    wp_current_version: str = Field(..., min_length=1, max_length=50)
    wp_target_version: str = Field(..., min_length=1, max_length=50)
    plugin_list: str = Field(..., min_length=1, description="List of plugins with versions")
    theme_name: Optional[str] = Field(None, max_length=255)
    theme_version: Optional[str] = Field(None, max_length=50)
    custom_notes: Optional[str] = None


class OrderUpdate(BaseModel):
    """Schema for updating order status"""
    payment_status: Optional[str] = None
    analysis_status: Optional[str] = None
    report_url: Optional[str] = None
    completed_at: Optional[datetime] = None


class OrderResponse(BaseModel):
    """Schema for order response"""
    id: UUID
    stripe_session_id: str
    payment_status: str
    amount_paid: int
    agency_name: str
    contact_email: str
    site_name: str
    site_url: Optional[str]
    wp_current_version: str
    wp_target_version: str
    plugin_list: str
    theme_name: Optional[str]
    theme_version: Optional[str]
    custom_notes: Optional[str]
    analysis_status: str
    report_url: Optional[str]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    """Schema for listing orders"""
    orders: list[OrderResponse]
    total: int
    page: int
    per_page: int
