# app/routers/auth_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.user_schemas import UserCreate, UserLogin, UserResponse, Token
from app.models.user import User
from app.utils.password_utils import hash_password, verify_password
from app.providers.auth import create_access_token, get_db
from datetime import timedelta
from app.settings import settings

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

@router.post("/signup", response_model=UserResponse, summary="Sign up a new user")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    """
    Public endpoint for user registration.
    """
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pw = hash_password(user.password)
    new_user = User(
        email=user.email,
        hashed_password=hashed_pw
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=Token, summary="Log in a user to obtain a token")
def login(user: UserLogin, db: Session = Depends(get_db)):
    """
    Public endpoint for user login and token generation.
    """
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": db_user.id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
