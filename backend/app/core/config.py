
"""
Application configuration settings
Uses Pydantic Settings for environment variable management
"""
from typing import List, Union, Any, Literal
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, field_validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Project Info
    PROJECT_NAME: str = "CodeRenew API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str

    # JWT Authentication
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Anthropic Claude API
    ANTHROPIC_API_KEY: str
    CLAUDE_MODEL: str = "claude-3-5-sonnet-20241022"

    # Stripe
    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str = ""  # Secret for webhook signature verification

    # Email Configuration
    EMAIL_PROVIDER: Literal["smtp", "sendgrid", "ses", "resend"] = "resend"
    EMAILS_FROM_EMAIL: str = "onboarding@resend.dev"
    EMAILS_FROM_NAME: str = "CodeRenew"
    FRONTEND_URL: str = "http://localhost:3000"

    # Resend
    RESEND_API_KEY: str = ""

    # SMTP Settings (optional)
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_USE_TLS: bool = True
    SMTP_START_TLS: bool = False

    # SendGrid (optional)
    SENDGRID_API_KEY: str = ""

    # AWS SES (optional)
    AWS_SES_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""

    # File Upload
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 52428800  # 50MB

    # MCP Settings
    WORDPRESS_MCP_ENABLED: bool = True
    WORDPRESS_MCP_URL: str = "https://wordpress.com/mcp"
    WORDPRESS_MCP_API_KEY: str = ""
    
    # Scanner Settings
    SCANNER_MAX_TOKENS_PER_BATCH: int = 150000
    SCANNER_MAX_RETRIES: int = 3

    # CORS
    ALLOWED_ORIGINS: Any = ["http://localhost:3000"]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        """Parse ALLOWED_ORIGINS from comma-separated string or list"""
        if v is None:
            return ["http://localhost:3000"]
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        if isinstance(v, list):
            return v
        return ["http://localhost:3000"]

    # Application Settings
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Redis Settings
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_ENABLED: bool = True
    REDIS_MAX_CONNECTIONS: int = 20
    REDIS_DEFAULT_TTL: int = 300  # 5 minutes

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
