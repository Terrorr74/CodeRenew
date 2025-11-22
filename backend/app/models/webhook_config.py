"""
WebhookConfig model for storing user webhook configurations
"""
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base


class WebhookConfig(Base):
    """
    Webhook configuration for user notifications
    
    Supports Slack, Microsoft Teams, Email, and custom HTTP webhooks
    """
    __tablename__ = "webhook_configs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False, index=True)  # 'slack', 'teams', 'email', 'http'
    url = Column(Text, nullable=True)  # Encrypted webhook URL (nullable for email type)
    enabled = Column(Boolean, default=True, nullable=False, index=True)
    events = Column(JSON, nullable=False)  # List of event types: ['scan_completed', 'vulnerability_found']
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="webhook_configs")
    deliveries = relationship("WebhookDelivery", back_populates="webhook_config", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<WebhookConfig(id={self.id}, name={self.name}, type={self.type}, enabled={self.enabled})>"
