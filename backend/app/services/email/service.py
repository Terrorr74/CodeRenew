"""
Production Email Service
Supports multiple providers: SMTP, SendGrid, AWS SES, Resend
Uses Jinja2 for template rendering
"""
import logging
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

logger = logging.getLogger(__name__)

# Template directory
TEMPLATE_DIR = Path(__file__).parent / "templates"


class EmailProvider(str, Enum):
    """Supported email providers"""
    SMTP = "smtp"
    SENDGRID = "sendgrid"
    AWS_SES = "ses"
    RESEND = "resend"


class EmailResult:
    """Result of an email send operation"""
    def __init__(self, success: bool, message_id: Optional[str] = None, error: Optional[str] = None):
        self.success = success
        self.message_id = message_id
        self.error = error

    def __repr__(self):
        return f"EmailResult(success={self.success}, message_id={self.message_id}, error={self.error})"


class BaseEmailProvider(ABC):
    """Abstract base class for email providers"""

    @abstractmethod
    async def send(
        self,
        to: List[str],
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
        reply_to: Optional[str] = None,
    ) -> EmailResult:
        """Send an email"""
        pass


class SMTPProvider(BaseEmailProvider):
    """SMTP email provider using aiosmtplib"""

    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        use_tls: bool = True,
        start_tls: bool = False,
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.start_tls = start_tls

    async def send(
        self,
        to: List[str],
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
        reply_to: Optional[str] = None,
    ) -> EmailResult:
        try:
            import aiosmtplib
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText

            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{from_name} <{from_email}>" if from_name else from_email
            msg["To"] = ", ".join(to)
            if reply_to:
                msg["Reply-To"] = reply_to

            if text_content:
                msg.attach(MIMEText(text_content, "plain"))
            msg.attach(MIMEText(html_content, "html"))

            await aiosmtplib.send(
                msg,
                hostname=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                use_tls=self.use_tls,
                start_tls=self.start_tls,
            )
            return EmailResult(success=True, message_id="smtp-sent")
        except Exception as e:
            logger.error(f"SMTP send error: {e}")
            return EmailResult(success=False, error=str(e))


class SendGridProvider(BaseEmailProvider):
    """SendGrid email provider"""

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def send(
        self,
        to: List[str],
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
        reply_to: Optional[str] = None,
    ) -> EmailResult:
        try:
            import httpx

            data = {
                "personalizations": [{"to": [{"email": addr} for addr in to]}],
                "from": {"email": from_email, "name": from_name} if from_name else {"email": from_email},
                "subject": subject,
                "content": [{"type": "text/html", "value": html_content}],
            }
            if text_content:
                data["content"].insert(0, {"type": "text/plain", "value": text_content})
            if reply_to:
                data["reply_to"] = {"email": reply_to}

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.sendgrid.com/v3/mail/send",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=data,
                )
                if response.status_code in (200, 202):
                    message_id = response.headers.get("X-Message-Id", "sendgrid-sent")
                    return EmailResult(success=True, message_id=message_id)
                return EmailResult(success=False, error=f"SendGrid error: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"SendGrid send error: {e}")
            return EmailResult(success=False, error=str(e))


class AWSSESProvider(BaseEmailProvider):
    """AWS SES email provider"""

    def __init__(self, region: str, access_key_id: str, secret_access_key: str):
        self.region = region
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key

    async def send(
        self,
        to: List[str],
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
        reply_to: Optional[str] = None,
    ) -> EmailResult:
        try:
            import aioboto3

            session = aioboto3.Session(
                aws_access_key_id=self.access_key_id,
                aws_secret_access_key=self.secret_access_key,
                region_name=self.region,
            )

            source = f"{from_name} <{from_email}>" if from_name else from_email
            body = {"Html": {"Data": html_content, "Charset": "UTF-8"}}
            if text_content:
                body["Text"] = {"Data": text_content, "Charset": "UTF-8"}

            async with session.client("ses") as ses:
                response = await ses.send_email(
                    Source=source,
                    Destination={"ToAddresses": to},
                    Message={
                        "Subject": {"Data": subject, "Charset": "UTF-8"},
                        "Body": body,
                    },
                    ReplyToAddresses=[reply_to] if reply_to else [],
                )
                return EmailResult(success=True, message_id=response.get("MessageId"))
        except Exception as e:
            logger.error(f"AWS SES send error: {e}")
            return EmailResult(success=False, error=str(e))


class ResendProvider(BaseEmailProvider):
    """Resend email provider"""

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def send(
        self,
        to: List[str],
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
        reply_to: Optional[str] = None,
    ) -> EmailResult:
        try:
            import httpx

            data = {
                "from": f"{from_name} <{from_email}>" if from_name else from_email,
                "to": to,
                "subject": subject,
                "html": html_content,
            }
            if text_content:
                data["text"] = text_content
            if reply_to:
                data["reply_to"] = reply_to

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.resend.com/emails",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=data,
                )
                if response.status_code == 200:
                    result = response.json()
                    return EmailResult(success=True, message_id=result.get("id"))
                return EmailResult(success=False, error=f"Resend error: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Resend send error: {e}")
            return EmailResult(success=False, error=str(e))


class MockProvider(BaseEmailProvider):
    """Mock provider for testing/development"""

    async def send(
        self,
        to: List[str],
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
        reply_to: Optional[str] = None,
    ) -> EmailResult:
        logger.info(f"[MOCK EMAIL] To: {to}, Subject: {subject}")
        return EmailResult(success=True, message_id="mock-id")


class EmailService:
    """
    Production email service with template rendering and multi-provider support.
    """

    def __init__(
        self,
        provider: BaseEmailProvider,
        from_email: str,
        from_name: str = "CodeRenew",
        frontend_url: str = "http://localhost:3000",
    ):
        self.provider = provider
        self.from_email = from_email
        self.from_name = from_name
        self.frontend_url = frontend_url

        # Initialize Jinja2 template environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(TEMPLATE_DIR)),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def _render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render an HTML template with the given context"""
        # Add common context
        context.setdefault("frontend_url", self.frontend_url)
        context.setdefault("company_name", "CodeRenew")
        context.setdefault("support_email", self.from_email)

        template = self.jinja_env.get_template(template_name)
        return template.render(**context)

    async def send_email(
        self,
        to: str | List[str],
        subject: str,
        template: str,
        context: Dict[str, Any],
        reply_to: Optional[str] = None,
    ) -> EmailResult:
        """
        Send an email using a template.

        Args:
            to: Recipient email(s)
            subject: Email subject
            template: Template filename (e.g., "welcome.html")
            context: Template context variables
            reply_to: Optional reply-to address
        """
        if isinstance(to, str):
            to = [to]

        try:
            html_content = self._render_template(template, context)
            return await self.provider.send(
                to=to,
                subject=subject,
                html_content=html_content,
                from_email=self.from_email,
                from_name=self.from_name,
                reply_to=reply_to,
            )
        except Exception as e:
            logger.error(f"Email send error: {e}")
            return EmailResult(success=False, error=str(e))

    async def send_welcome_email(self, email: str, name: str) -> EmailResult:
        """Send welcome/registration email"""
        return await self.send_email(
            to=email,
            subject="Welcome to CodeRenew!",
            template="welcome.html",
            context={"name": name, "email": email},
        )

    async def send_password_reset_email(self, email: str, token: str) -> EmailResult:
        """Send password reset email"""
        reset_url = f"{self.frontend_url}/auth/reset-password?token={token}"
        return await self.send_email(
            to=email,
            subject="Reset your password - CodeRenew",
            template="password_reset.html",
            context={"reset_url": reset_url},
        )

    async def send_scan_complete_email(
        self,
        email: str,
        scan_id: int,
        risk_level: str,
        issue_count: int,
    ) -> EmailResult:
        """Send scan completion notification"""
        scan_url = f"{self.frontend_url}/scans/{scan_id}"
        return await self.send_email(
            to=email,
            subject=f"Scan Complete: {issue_count} issues found - CodeRenew",
            template="scan_complete.html",
            context={
                "scan_url": scan_url,
                "scan_id": scan_id,
                "risk_level": risk_level,
                "issue_count": issue_count,
            },
        )

    async def send_account_lockout_email(self, email: str, lockout_minutes: int) -> EmailResult:
        """Send account lockout notification"""
        return await self.send_email(
            to=email,
            subject="Security Alert: Your account has been locked - CodeRenew",
            template="account_lockout.html",
            context={"lockout_minutes": lockout_minutes},
        )


def create_email_service_from_settings() -> EmailService:
    """
    Factory function to create EmailService from application settings.
    """
    from app.core.config import settings

    provider: BaseEmailProvider

    # Determine provider based on configuration
    if settings.EMAIL_PROVIDER == EmailProvider.SMTP:
        provider = SMTPProvider(
            host=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USERNAME,
            password=settings.SMTP_PASSWORD,
            use_tls=settings.SMTP_USE_TLS,
            start_tls=settings.SMTP_START_TLS,
        )
    elif settings.EMAIL_PROVIDER == EmailProvider.SENDGRID:
        provider = SendGridProvider(api_key=settings.SENDGRID_API_KEY)
    elif settings.EMAIL_PROVIDER == EmailProvider.AWS_SES:
        provider = AWSSESProvider(
            region=settings.AWS_SES_REGION,
            access_key_id=settings.AWS_ACCESS_KEY_ID,
            secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
    elif settings.EMAIL_PROVIDER == EmailProvider.RESEND:
        if settings.RESEND_API_KEY:
            provider = ResendProvider(api_key=settings.RESEND_API_KEY)
        else:
            logger.warning("RESEND_API_KEY not set, using mock provider")
            provider = MockProvider()
    else:
        logger.warning("No email provider configured, using mock provider")
        provider = MockProvider()

    return EmailService(
        provider=provider,
        from_email=settings.EMAILS_FROM_EMAIL,
        from_name=settings.EMAILS_FROM_NAME,
        frontend_url=settings.FRONTEND_URL,
    )


# Global email service instance (lazy initialization)
_email_service: Optional[EmailService] = None


def get_email_service() -> EmailService:
    """Get or create the global email service instance"""
    global _email_service
    if _email_service is None:
        _email_service = create_email_service_from_settings()
    return _email_service
