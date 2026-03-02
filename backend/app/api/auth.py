from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_refresh_token,
    create_reset_token,
    decode_token,
    verify_password,
    verify_refresh_token,
)
from app.crud.user import create_user, get_user_by_email, update_user_password
from app.db.database import get_db
from app.models.user import User
from app.schemas.auth import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    LoginResponse,
    MessageResponse,
    RefreshTokenRequest,
    RegisterRequest,
    ResetPasswordRequest,
    UserResponse,
)
from app.services.email_services import send_welcome_email, send_password_reset_email

router = APIRouter(prefix="/auth", tags=["Authentication"])


def serialize_user(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        phone=user.phone,
        role=user.role,
    )


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=MessageResponse)
async def register(user: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    try:
        db_user = create_user(db, user)
        
        # Send welcome email asynchronously
        try:
            await send_welcome_email(email=user.email, name=user.name)
        except Exception as e:
            # Log email sending error but don't fail the registration
            print(f"Failed to send welcome email to {user.email}: {str(e)}")
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email or phone already registered")

    return {"message": "User registered successfully"}


@router.post("/login", response_model=LoginResponse)
def login(user: LoginRequest, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, user.email)
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token(db_user.email, db_user.role)
    refresh_token = create_refresh_token(db_user.email)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": serialize_user(db_user),
        "token_type": "bearer",
    }


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    # Do not expose account existence details
    db_user = get_user_by_email(db, payload.email)
    
    if db_user:
        try:
            # Generate reset token
            reset_token = create_reset_token(db_user.email)
            
            # Send password reset email
            await send_password_reset_email(email=db_user.email, reset_token=reset_token)
        except Exception as e:
            # Log email sending error but don't fail the request
            print(f"Failed to send password reset email to {payload.email}: {str(e)}")
    
    # Always return the same message regardless of whether email was sent or user exists
    return {"message": "If the email exists, password reset instructions will be sent."}


@router.post("/refresh", response_model=LoginResponse)
def refresh_access_token(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Get new access token using refresh token"""
    try:
        decoded = verify_refresh_token(payload.refresh_token)
        email = decoded.get("sub")
        
        db_user = get_user_by_email(db, email)
        if not db_user:
            raise HTTPException(status_code=401, detail="User not found")
        
        new_access_token = create_access_token(db_user.email, db_user.role)
        new_refresh_token = create_refresh_token(db_user.email)
        
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "user": serialize_user(db_user),
            "token_type": "bearer",
        }
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/reset-password", response_model=MessageResponse)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    try:
        decoded = decode_token(payload.token)
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    if decoded.get("type") != "reset":
        raise HTTPException(status_code=400, detail="Invalid reset token")

    email = decoded.get("sub")
    if not email:
        raise HTTPException(status_code=400, detail="Invalid reset token")

    db_user = get_user_by_email(db, email)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    update_user_password(db, db_user, payload.new_password)
    return {"message": "Password reset successful"}
