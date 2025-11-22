"""
WebhookDelivery model for tracking webhook delivery attempts
"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base


class WebhookDelivery(Base):
    """
    Audit log of webhook delivery attempts
    
    Tracks status, retries, responses, and errors for each webhook delivery
    """
    __tablename__ = "webhook_deliveries"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    webhook_config_id = Column(String(36), ForeignKey("webhook_configs.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    payload = Column(JSON, nullable=False)
    status = Column(String(50), nullable=False, index=True)  # 'pending', 'delivered', 'failed'
    attempts = Column(Integer, default=0, nullable=False)
    last_attempt_at = Column(DateTime, nullable=True)
    response_code = Column(Integer, nullable=True)
    response_body = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    webhook_config = relationship("WebhookConfig", back_populates="deliveries")
    
    def __repr__(self):
        return f"<WebhookDelivery(id={self.id}, event_type={self.event_type}, status={self.status}, attempts={self.attempts})>"
