# app/main.py

import requests
import threading
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from app.routers import (
    auth_router, config, errors, cache, prompts, files, 
    processing, results, claude_batch, claude_callback, ws_results, usage
)
from app.utils.environment import load_environment_variables
from dotenv import load_dotenv
from app.config.database import engine, Base
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.openapi.models import OAuth2 as OAuth2Model

# Load environment variables at the very start
load_environment_variables()

app = FastAPI(
    title="Text Processor with Generative AI",
    description="A FastAPI backend for processing text files using multiple AI providers.",
    version="1.0.0",
    contact={
        "name": "Rebuma Tadele",
        "email": "rebumatadele2@gmail.com",
    },
)

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://fileprocessor.netlify.app/",
    "https://fileprocessor.netlify.app/"
    # Add your frontend URL here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust as needed for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
Base.metadata.create_all(bind=engine)

# Include routers with tags for Swagger grouping
app.include_router(auth_router.router)
app.include_router(config.router)
app.include_router(prompts.router)
app.include_router(files.router)
app.include_router(processing.router)
app.include_router(claude_batch.router)
app.include_router(results.router)
app.include_router(errors.router)
app.include_router(cache.router)
app.include_router(claude_callback.router)
app.include_router(ws_results.router)
app.include_router(usage.router)

@app.get("/", summary="Root Endpoint")
def read_root():
    return {"message": "Welcome to the Text Processor with Generative AI!"}

# Define a custom OAuth2 schema for Swagger UI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def keep_alive():
    while True:
        try:
            # Ping this application
            requests.get("https://file-processing-webapp.onrender.com/")
            # Ping the other backend
            requests.get("https://claude-integration-service-1.onrender.com/")
            print("Pinging successful")
        except Exception as e:
            print(f"Failed to ping: {e}")
        # Wait 5 minutes (300 seconds)
        threading.Event().wait(300)

@app.on_event("startup")
async def startup_event():
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")

    # Customize OpenAPI schema for Swagger UI
    if not app.openapi_schema:
        openapi_schema = app.openapi()
        # Update security scheme to require only the token
        openapi_schema["components"]["securitySchemes"]["OAuth2PasswordBearer"] = {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",  # Indicate you're using a JWT token
        }
        app.openapi_schema = openapi_schema

    # Start the keep-alive thread
    threading.Thread(target=keep_alive, daemon=True).start()