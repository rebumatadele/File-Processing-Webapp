# app/routers/prompts.py

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.models.prompt import Prompt
from app.models.user import User
from app.providers.auth import get_current_user
from app.schemas.prompt_schemas import PromptSchema, PromptCreate, PromptUpdate
from app.utils.error_utils import handle_error
from app.utils.file_utils import (
    list_saved_prompts,
    load_prompt,
    save_prompt,
    delete_prompt
)
from app.dependencies.database import get_db

router = APIRouter(
    prefix="/prompts",
    tags=["Prompt Management"],
    responses={404: {"description": "Not found"}},
)

class PromptListResponse(BaseModel):
    prompts: List[str]
    total: int
    page: int
    size: int

@router.get("/", summary="List Saved Prompts", response_model=PromptListResponse)
def list_prompts(
    search: Optional[str] = Query(None),
    tags: Optional[List[str]] = Query(None),
    page: int = 1,
    size: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        all_prompts = list_saved_prompts(db, user_id=current_user.id, search=search, tags=tags)
        total = len(all_prompts)
        start = (page - 1) * size
        end = start + size
        paginated = all_prompts[start:end]

        return PromptListResponse(prompts=paginated, total=total, page=page, size=size)
    except Exception as e:
        handle_error("ProcessingError", f"Failed to list prompts: {e}", user_id=current_user.id)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{prompt_name}", summary="Load a Specific Prompt", response_model=PromptSchema)
def load_specific_prompt(
    prompt_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        content = load_prompt(db, name=prompt_name, user_id=current_user.id)
        if content is None:
            raise HTTPException(status_code=404, detail="Prompt not found.")

        prompt = db.query(Prompt).filter_by(user_id=current_user.id, name=prompt_name).first()
        if not prompt:
            raise HTTPException(status_code=404, detail="Prompt not found in DB.")
        return PromptSchema(
            id=prompt.id,
            user_id=prompt.user_id,
            name=prompt.name,
            description=prompt.description,
            tags=prompt.tags.split(",") if prompt.tags else [],
            content=prompt.content,
            created_at=prompt.created_at,
            updated_at=prompt.updated_at
        )
    except Exception as e:
        handle_error("ProcessingError", f"Failed to load prompt '{prompt_name}': {e}", user_id=current_user.id)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/save", summary="Save a New Prompt")
def save_new_prompt(
    prompt: PromptCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        existing_prompts = list_saved_prompts(db, user_id=current_user.id)
        overwrite = prompt.name in existing_prompts

        save_prompt(
            db,
            name=prompt.name,
            content=prompt.content,
            user_id=current_user.id,
            description=prompt.description,
            tags=prompt.tags
        )
        msg = f"Prompt '{prompt.name}' updated" if overwrite else f"Prompt '{prompt.name}' created"
        return {"message": f"{msg} successfully!"}
    except Exception as e:
        handle_error("ProcessingError", f"Failed to save prompt '{prompt.name}': {e}", user_id=current_user.id)
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{prompt_name}", summary="Update an Existing Prompt")
def update_prompt(
    prompt_name: str,
    prompt_update: PromptUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        existing_prompts = list_saved_prompts(db, user_id=current_user.id)
        if prompt_name not in existing_prompts:
            raise HTTPException(status_code=404, detail="Prompt not found.")

        existing_content = load_prompt(db, name=prompt_name, user_id=current_user.id)
        if existing_content is None:
            raise HTTPException(status_code=404, detail="Prompt not found in DB.")

        new_content = prompt_update.content if prompt_update.content is not None else existing_content
        new_description = prompt_update.description
        new_tags = prompt_update.tags

        save_prompt(
            db,
            name=prompt_name,
            content=new_content,
            user_id=current_user.id,
            description=new_description,
            tags=new_tags
        )
        return {"message": f"Prompt '{prompt_name}' updated successfully!"}
    except Exception as e:
        handle_error("ProcessingError", f"Failed to update prompt '{prompt_name}': {e}", user_id=current_user.id)
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{prompt_name}", summary="Delete a Prompt")
def delete_specific_prompt(
    prompt_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        existing_prompts = list_saved_prompts(db, user_id=current_user.id)
        if prompt_name not in existing_prompts:
            raise HTTPException(status_code=404, detail="Prompt not found.")

        delete_prompt(db, name=prompt_name, user_id=current_user.id)
        return {"message": f"Prompt '{prompt_name}' deleted successfully!"}
    except Exception as e:
        handle_error("ProcessingError", f"Failed to delete prompt '{prompt_name}': {e}", user_id=current_user.id)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bulk_delete", summary="Bulk Delete Prompts")
def bulk_delete_prompts(
    prompt_names: List[str],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        deleted = []
        not_found = []
        for name in prompt_names:
            existing_prompts = list_saved_prompts(db, user_id=current_user.id)
            if name in existing_prompts:
                delete_prompt(db, name=name, user_id=current_user.id)
                deleted.append(name)
            else:
                not_found.append(name)
        msg = f"Deleted: {deleted}" if deleted else ""
        if not_found:
            msg += f". Not found: {not_found}"
        return {"message": msg}
    except Exception as e:
        handle_error("ProcessingError", f"Failed to bulk delete prompts: {e}", user_id=current_user.id)
        raise HTTPException(status_code=500, detail=str(e))
