"""
Authentication endpoints
User registration, login, and verification
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.db.session import get_db
from app.schemas.user import UserCreate, UserResponse, UserLogin, Token, TokenWithUser, UserOnboardingUpdate
from app.core.security import get_password_hash, verify_password, create_access_token
from app.api.dependencies import get_current_user
from app.models.user import User
from app.core.rate_limiting import (
    limiter,
    LOGIN_RATE_LIMIT,
    REGISTER_RATE_LIMIT,
    PASSWORD_RESET_RATE_LIMIT
)

router = APIRouter()

# Account lockout configuration
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 30


@router.post("/register", response_model=TokenWithUser, status_code=status.HTTP_201_CREATED)
@limiter.limit(REGISTER_RATE_LIMIT)
async def register(request: Request, user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user and return access token (auto-login)

    Rate limited to prevent spam account creation

    Args:
        request: FastAPI Request object (required for rate limiting)
        user_data: User registration data
        db: Database session

    Returns:
        JWT token and created user object
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        name=user_data.name or "",  # Default to empty string if not provided
        company=user_data.company,
        is_verified=False,  # TODO: Implement email verification
        onboarding_completed=False
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Create access token for auto-login
    access_token = create_access_token(
        data={"user_id": db_user.id, "email": db_user.email}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": db_user
    }


@router.post("/login", response_model=Token)
@limiter.limit(LOGIN_RATE_LIMIT)
async def login(request: Request, credentials: UserLogin, db: Session = Depends(get_db)):
    """
    User login with account lockout protection

    Rate limited to prevent brute force attacks.
    Account locked for 30 minutes after 5 failed attempts.

    Args:
        request: FastAPI Request object (required for rate limiting)
        credentials: Login credentials
        db: Database session

    Returns:
        JWT access token

    Raises:
        HTTPException: 403 if account is locked, 401 if credentials invalid
    """
    # Find user by email
    user = db.query(User).filter(User.email == credentials.email).first()

    # Check if account exists (do this in constant time to avoid user enumeration)
    if not user:
        # Return same error as wrong password to avoid user enumeration
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if account is locked
    if user.locked_until and user.locked_until > datetime.utcnow():
        lockout_remaining = (user.locked_until - datetime.utcnow()).seconds // 60
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account is locked due to multiple failed login attempts. "
                   f"Please try again in {lockout_remaining} minutes.",
        )

    # Verify password
    if not verify_password(credentials.password, user.hashed_password):
        # Increment failed login attempts
        user.failed_login_attempts += 1
        user.last_failed_login = datetime.utcnow()

        # Check if we need to lock the account
        if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
            user.locked_until = datetime.utcnow() + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
            db.commit()

            # Send email notification about account lockout
            try:
                from app.services.email import send_account_locked_email
                send_account_locked_email(user.email, LOCKOUT_DURATION_MINUTES)
            except Exception as e:
                # Log error but don't fail the request
                print(f"Failed to send account lockout email: {e}")

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Account has been locked due to {MAX_FAILED_ATTEMPTS} failed login attempts. "
                       f"Please try again in {LOCKOUT_DURATION_MINUTES} minutes. "
                       f"A notification email has been sent to {user.email}.",
            )

        db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Successful login - reset failed attempts and unlock account
    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_failed_login = None
    db.commit()

    # Create access token
    access_token = create_access_token(
        data={"user_id": user.id, "email": user.email}
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user information

    Args:
        current_user: Current authenticated user

    Returns:
        User object
    """
    return current_user


@router.put("/onboarding/complete", response_model=UserResponse)
async def complete_onboarding(
    onboarding_data: UserOnboardingUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Complete user onboarding by updating profile information

    Args:
        onboarding_data: Onboarding data (name and company)
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated user object
    """
    # Update user information
    current_user.name = onboarding_data.name
    current_user.company = onboarding_data.company
    current_user.onboarding_completed = True

    db.commit()
    db.refresh(current_user)

    return current_user


# Import the dependency here to avoid circular imports
from app.api.dependencies import get_current_user
from app.schemas.user import (
    UserProfileUpdate,
    PasswordChange,
    PasswordResetRequest,
    PasswordResetConfirm
)
from app.services.email import send_reset_password_email
import uuid
from datetime import datetime, timedelta


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user profile information
    """
    # Check if email is being changed and if it's already taken
    if profile_data.email and profile_data.email != current_user.email:
        existing_user = db.query(User).filter(User.email == profile_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        current_user.email = profile_data.email

    if profile_data.name is not None:
        current_user.name = profile_data.name
    
    if profile_data.company is not None:
        current_user.company = profile_data.company

    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change user password
    """
    if not verify_password(password_data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect old password"
        )

    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()
    
    return {"message": "Password updated successfully"}


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
@limiter.limit(PASSWORD_RESET_RATE_LIMIT)
async def forgot_password(
    request: Request,
    reset_data: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """
    Request password reset

    Rate limited to prevent abuse and email bombing

    Args:
        request: FastAPI Request object (required for rate limiting)
        reset_data: Password reset request data
        db: Database session
    """
    user = db.query(User).filter(User.email == reset_data.email).first()
    if not user:
        # Don't reveal that the user doesn't exist
        return {"message": "If the email exists, a reset link has been sent"}

    # Generate reset token
    token = str(uuid.uuid4())
    user.reset_token = token
    user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
    db.commit()

    # Send email
    try:
        send_reset_password_email(user.email, token)
    except Exception as e:
        print(f"Failed to send email: {e}")
        # In production, you might want to log this error properly
        pass

    return {"message": "If the email exists, a reset link has been sent"}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
@limiter.limit(PASSWORD_RESET_RATE_LIMIT)
async def reset_password(
    request: Request,
    reset_data: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """
    Reset password using token

    Rate limited to prevent brute force token guessing

    Args:
        request: FastAPI Request object (required for rate limiting)
        reset_data: Password reset confirmation data
        db: Database session
    """
    user = db.query(User).filter(
        User.reset_token == reset_data.token,
        User.reset_token_expires > datetime.utcnow()
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )

    # Update password and clear token
    user.hashed_password = get_password_hash(reset_data.new_password)
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()

    return {"message": "Password reset successfully"}

