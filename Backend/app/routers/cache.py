# app/routers/cache.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.models.user import User
from app.providers.auth import get_current_user, get_db
from app.utils.cache_utils import clear_cache_for_user, get_cache_size_for_user, list_cache_for_user
from app.utils.error_utils import handle_error

router = APIRouter(
    prefix="/cache",
    tags=["Cache Management"],
    responses={404: {"description": "Not found"}},
)

@router.post("/clear", summary="Clear Cache")
def clear_cache_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        clear_cache_for_user(db, current_user.id)
        return {"message": "Cache cleared successfully."}
    except Exception as e:
        handle_error("ProcessingError", f"Failed to clear cache: {e}")
        return {"message": f"Failed to clear cache: {e}"}

@router.get("/size", summary="Get Cache Size")
def get_cache_size_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        size = get_cache_size_for_user(db, current_user.id)
        return {"cache_size": size}
    except Exception as e:
        handle_error("ProcessingError", f"Failed to get cache size: {e}")
        return {"message": f"Failed to get cache size: {e}"}

@router.get("/contents", summary="List Cache Contents")
def list_cache_contents_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        chunks = list_cache_for_user(db, current_user.id)
        return {"cache_contents": chunks}
    except Exception as e:
        handle_error("ProcessingError", f"Failed to list cache contents: {e}")
        return {"message": f"Failed to list cache contents: {e}"}
