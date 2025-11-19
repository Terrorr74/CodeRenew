from sqlalchemy import Column, String, Integer, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.models.base import Base


class Order(Base):
    """
    Order model for tracking CodeRenew landing page purchases
    Represents a paid WordPress compatibility analysis order
    """
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Payment information
    stripe_payment_id = Column(String(255), unique=True, nullable=True)  # payment_intent ID
    stripe_session_id = Column(String(255), unique=True, nullable=False)
    payment_status = Column(String(50), default="pending", nullable=False)
    amount_paid = Column(Integer, nullable=False)  # in cents

    # Agency/Customer information
    agency_name = Column(String(255), nullable=False)
    contact_email = Column(String(255), nullable=False, index=True)

    # Site details
    site_name = Column(String(255), nullable=False)
    site_url = Column(String(500), nullable=True)
    wp_current_version = Column(String(50), nullable=False)
    wp_target_version = Column(String(50), nullable=False)
    plugin_list = Column(Text, nullable=False)
    theme_name = Column(String(255), nullable=True)
    theme_version = Column(String(50), nullable=True)
    custom_notes = Column(Text, nullable=True)

    # Analysis tracking
    analysis_status = Column(String(50), default="pending", nullable=False, index=True)
    report_url = Column(String(500), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<Order {self.id} - {self.agency_name} - {self.site_name}>"
