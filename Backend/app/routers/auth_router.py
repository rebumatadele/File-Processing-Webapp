# app/routers/auth_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.utils.email_utils import send_email
from app.schemas.user_schemas import UserCreate, UserLogin, UserResponse, Token
from app.models.user import User
from app.utils.password_utils import hash_password, verify_password
from app.providers.auth import create_access_token, decode_access_token, get_db
from datetime import timedelta
from app.settings import settings
from fastapi.responses import RedirectResponse

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

@router.post("/signup", response_model=UserResponse, summary="Sign up a new user")
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    """
    Public endpoint for user registration.
    """
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    hashed_pw = hash_password(user.password)
    new_user = User(
        email=user.email,
        hashed_password=hashed_pw,
        is_verified=False  # Mark as not verified initially
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create email verification token
    verification_data = {"sub": new_user.id, "email": new_user.email, "action": "verify_email"}
    verification_expires = timedelta(hours=24)  # Token valid for 24 hours
    verification_token = create_access_token(data=verification_data, expires_delta=verification_expires)

    # Use backend_url to create the verification link
    verification_link = f"{settings.backend_url}/auth/verify-email?token={verification_token}"

    # Send verification email
    subject = "Verify Your Email"
    body = f"""
    <p>Hi {new_user.email},</p>
    <p>Thanks for signing up. Please verify your email by clicking the link below:</p>
    <p><a href="{verification_link}">Verify Email</a></p>
    <p>This link will expire in 24 hours.</p>
    """
    await send_email(subject, [new_user.email], body)

    return new_user

@router.post("/login", response_model=Token, summary="Log in a user to obtain a token")
def login(user: UserLogin, db: Session = Depends(get_db)):
    """
    Public endpoint for user login and token generation.
    """
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not db_user.is_verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email not verified")

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": db_user.id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/verify-email", summary="Verify user's email")
def verify_email(token: str, db: Session = Depends(get_db)):
    token_data = decode_access_token(token)
    if not token_data or token_data.user_id is None:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = db.query(User).filter(User.id == token_data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_verified = True
    db.commit()

    # Redirect to the frontend login page after verification
    login_url = f"{settings.frontend_url}/login"
    return RedirectResponse(url=login_url)