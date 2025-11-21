"""
Email service module
"""
from .service import (
    EmailService,
    EmailResult,
    EmailProvider,
    BaseEmailProvider,
    SMTPProvider,
    SendGridProvider,
    AWSSESProvider,
    ResendProvider,
    MockProvider,
    get_email_service,
    create_email_service_from_settings,
)

__all__ = [
    "EmailService",
    "EmailResult",
    "EmailProvider",
    "BaseEmailProvider",
    "SMTPProvider",
    "SendGridProvider",
    "AWSSESProvider",
    "ResendProvider",
    "MockProvider",
    "get_email_service",
    "create_email_service_from_settings",
]
