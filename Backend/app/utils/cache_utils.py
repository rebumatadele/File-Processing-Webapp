# app/utils/cache_utils.py
from sqlalchemy.orm import Session
from app.models.cache import CachedResult
from typing import Optional, List

def get_cached_result(
    db: Session,
    chunk: str,
    provider_choice: str,
    model_choice: Optional[str],
    user_id: Optional[str] = None
) -> Optional[str]:
    """
    Check if there's a cached response in the database for the given chunk/user/provider/model.
    Return the response if found, else None.
    """
    query = db.query(CachedResult).filter(
        CachedResult.chunk == chunk,
        CachedResult.provider_choice == provider_choice,
    )
    if model_choice:
        query = query.filter(CachedResult.model_choice == model_choice)
    if user_id:
        query = query.filter(CachedResult.user_id == user_id)

    record = query.first()
    return record.response if record else None

def set_cached_result(
    db: Session,
    chunk: str,
    provider_choice: str,
    model_choice: Optional[str],
    response: str,
    user_id: Optional[str] = None
):
    """
    Store a new cached response in the database.
    """
    cache_entry = CachedResult(
        user_id=user_id,
        provider_choice=provider_choice,
        model_choice=model_choice,
        chunk=chunk,
        response=response
    )
    db.add(cache_entry)
    db.commit()
    db.refresh(cache_entry)

def clear_cache_for_user(db: Session, user_id: str):
    """
    Deletes all cached results for the given user from the DB.
    """
    db.query(CachedResult).filter_by(user_id=user_id).delete()
    db.commit()

def get_cache_size_for_user(db: Session, user_id: str) -> int:
    """
    Returns the total count of cached results for the user 
    or you could sum sizes of responses if you prefer.
    """
    return db.query(CachedResult).filter_by(user_id=user_id).count()

def list_cache_for_user(db: Session, user_id: str) -> List[str]:
    """
    Lists all 'chunk' keys cached for the given user. 
    Or adapt to return a list of provider/model pairs, etc.
    """
    records = db.query(CachedResult).filter_by(user_id=user_id).all()
    return [r.chunk for r in records]
