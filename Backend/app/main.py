# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import config, errors, cache, prompts, files, processing, results
from app.utils.environment import load_environment_variables
from dotenv import load_dotenv

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

# Include routers with tags for Swagger grouping
app.include_router(config.router)
app.include_router(errors.router)
app.include_router(cache.router)
app.include_router(prompts.router)
app.include_router(files.router)
app.include_router(processing.router)
app.include_router(results.router)

@app.get("/", summary="Root Endpoint")
def read_root():
    return {"message": "Welcome to the Text Processor with Generative AI!"}
