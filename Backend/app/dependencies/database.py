# app/dependencies/database.py

from sqlalchemy.orm import Session
from app.config.database import SessionLocal
from fastapi import Depends

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
