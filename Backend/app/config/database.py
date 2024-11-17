# app/config/database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.settings import settings

DATABASE_URL = settings.database_url  # Defined in settings.py

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})  # For SQLite
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
