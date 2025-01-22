# app/routers/auth_router.py

from fastapi import APIRouter, Depends, HTTPException, status, Body
from pydantic import EmailStr
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import timedelta
from fastapi.responses import RedirectResponse

from app.utils.email_utils import send_email
from app.schemas.user_schemas import UserCreate, UserLogin, UserResponse, Token
from app.models.user import User
from app.utils.password_utils import hash_password, verify_password
from app.providers.auth import create_access_token, decode_access_token, get_db
from app.settings import settings

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.post("/signup", response_model=UserResponse, summary="Sign up a new user")
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    hashed_pw = hash_password(user.password)
    new_user = User(
        email=user.email,
        hashed_password=hashed_pw,
        is_verified=False
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    verification_data = {"sub": new_user.id, "email": new_user.email, "action": "verify_email"}
    verification_expires = timedelta(hours=24)
    verification_token = create_access_token(data=verification_data, expires_delta=verification_expires)

    verification_link = f"{settings.backend_url}/auth/verify-email?token={verification_token}"
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
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not db_user.is_verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email not verified")

    access_token = create_access_token(data={"sub": db_user.id}, expires_delta=None)
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

    login_url = f"{settings.frontend_url}/login"
    return RedirectResponse(url=login_url)

@router.post("/forgot-password", summary="Request Password Reset")
async def forgot_password(email: EmailStr, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    reset_token_data = {
        "sub": user.id,
        "email": user.email,
        "action": "reset_password"
    }
    reset_token = create_access_token(data=reset_token_data, expires_delta=None)
    
    reset_link = f"{settings.frontend_url}/reset-password?token={reset_token}"
    
    subject = "Password Reset Request"
    body = f"""
    <p>Hello {user.email},</p>
    <p>You requested a password reset. Click the link below to reset your password:</p>
    <p><a href="{reset_link}">Reset Password</a></p>
    <p>If you didn't request this, please ignore this email.</p>
    """
    await send_email(subject, [user.email], body)
    
    return {"message": "If that email is in our system, a reset link was sent."}

@router.post("/reset-password", summary="Reset Password")
def reset_password(
    new_password: str = Body(...),
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    token_data = decode_access_token(token)
    if not token_data or token_data.user_id is None:
        raise HTTPException(status_code=400, detail="Invalid or expired token.")

    if getattr(token_data, "action", None) != "reset_password":
        raise HTTPException(status_code=400, detail="Token is not for password resets.")

    user = db.query(User).filter(User.id == token_data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    hashed_pw = hash_password(new_password)
    user.hashed_password = hashed_pw
    db.commit()

    return {"message": "Password has been reset successfully."}
