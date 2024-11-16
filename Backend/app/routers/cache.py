# app/routers/cache.py

from fastapi import APIRouter
from app.utils.file_utils import (
    clear_cache,
    get_cache_size,
    list_cache_contents,
    handle_error
)

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

@router.get("/size", summary="Get Cache Size")
def get_cache_size_endpoint():
    """
    Get the total size of the cache in bytes.
    """
    try:
        size = get_cache_size()
        return {"cache_size_bytes": size}
    except Exception as e:
        handle_error("ProcessingError", f"Failed to get cache size: {e}")
        return {"message": f"Failed to get cache size: {e}"}

@router.get("/contents", summary="List Cache Contents")
def list_cache_contents_endpoint():
    """
    List all items currently in the cache.
    """
    try:
        contents = list_cache_contents()
        return {"cache_contents": contents}
    except Exception as e:
        handle_error("ProcessingError", f"Failed to list cache contents: {e}")
        return {"message": f"Failed to list cache contents: {e}"}
