# app/config/database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.settings import settings

DATABASE_URL = settings.database_url  # e.g. "postgresql+psycopg2://file_processor:4213@localhost:5432/my_database"

# For Postgres, we do NOT need connect_args
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
