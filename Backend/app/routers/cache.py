# app/routers/cache.py

from fastapi import APIRouter
from app.utils.file_utils import clear_cache, handle_error

router = APIRouter(
    prefix="/cache",
    tags=["Cache Management"],
    responses={404: {"description": "Not found"}},
)

@router.post("/clear", summary="Clear Cache")
def clear_cache_endpoint():
    """
    Clear the application cache.
    """
    try:
        clear_cache()
        return {"message": "Cache cleared successfully."}
    except Exception as e:
        handle_error("ProcessingError", f"Failed to clear cache: {e}")
        return {"message": f"Failed to clear cache: {e}"}
