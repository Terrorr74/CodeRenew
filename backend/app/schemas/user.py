"""
User Pydantic schemas
Request and response models for user operations
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional

from app.core.password_policy import validate_password_strength, PasswordValidationError
from app.core.input_sanitization import sanitize_html


class UserBase(BaseModel):
    """Base user schema with common fields"""
    email: EmailStr


class UserCreate(UserBase):
    """Schema for user registration"""
    password: str = Field(..., min_length=8, max_length=128)
    name: Optional[str] = Field(None, max_length=255)
    company: Optional[str] = Field(None, max_length=255)

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password meets security requirements"""
        try:
            return validate_password_strength(v)
        except PasswordValidationError as e:
            raise ValueError(str(e))

    @field_validator('name', 'company')
    @classmethod
    def sanitize_text_fields(cls, v: Optional[str]) -> Optional[str]:
        """Sanitize text fields to prevent XSS"""
        if v is None:
            return v
        return sanitize_html(v)


class UserLogin(UserBase):
    """Schema for user login"""
    password: str


class UserResponse(UserBase):
    """Schema for user response"""
    id: int
    name: str
    company: Optional[str] = None
    is_verified: bool
    onboarding_completed: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserOnboardingUpdate(BaseModel):
    """Schema for completing user onboarding"""
    name: str = Field(..., min_length=1, max_length=255)
    company: Optional[str] = Field(None, max_length=255)

    @field_validator('name', 'company')
    @classmethod
    def sanitize_text_fields(cls, v: Optional[str]) -> Optional[str]:
        """Sanitize text fields to prevent XSS"""
        if v is None:
            return v
        return sanitize_html(v)


class UserProfileUpdate(BaseModel):
    """Schema for updating user profile"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    company: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None

    @field_validator('name', 'company')
    @classmethod
    def sanitize_text_fields(cls, v: Optional[str]) -> Optional[str]:
        """Sanitize text fields to prevent XSS"""
        if v is None:
            return v
        return sanitize_html(v)


class PasswordChange(BaseModel):
    """Schema for changing password (logged in)"""
    old_password: str
    new_password: str = Field(..., min_length=8, max_length=128)

    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        """Validate new password meets security requirements"""
        try:
            return validate_password_strength(v)
        except PasswordValidationError as e:
            raise ValueError(str(e))


class PasswordResetRequest(BaseModel):
    """Schema for requesting password reset"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for confirming password reset"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)

    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        """Validate new password meets security requirements"""
        try:
            return validate_password_strength(v)
        except PasswordValidationError as e:
            raise ValueError(str(e))


class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"


class TokenWithUser(Token):
    """Schema for JWT token response with user data"""
    user: UserResponse


class TokenData(BaseModel):
    """Schema for token payload data"""
    user_id: Optional[int] = None
    email: Optional[str] = None
