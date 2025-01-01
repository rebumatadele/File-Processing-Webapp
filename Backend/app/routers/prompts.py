# app/routers/prompts.py

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from app.models.prompt import Prompt
from app.models.user import User
from app.providers.auth import get_current_user
from app.schemas.prompt_schemas import PromptSchema, PromptCreate, PromptUpdate
from app.utils.file_utils import (
    list_saved_prompts,
    load_prompt,
    save_prompt,
    delete_prompt,
    handle_error
)
from pydantic import BaseModel
from app.dependencies.database import get_db  # Create this dependency
from sqlalchemy.orm import Session

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
    search: Optional[str] = Query(None, description="Search term for prompt names"),
    tags: Optional[List[str]] = Query(None, description="Filter prompts by tags"),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    size: int = Query(10, ge=1, le=100, description="Number of prompts per page"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve a paginated list of saved prompts for the current user.
    Supports searching by name and filtering by tags.
    """
    try:
        all_prompts = list_saved_prompts(session=db, user_id=current_user.id, search=search, tags=tags)
        total = len(all_prompts)
        start = (page - 1) * size
        end = start + size
        paginated_prompts = all_prompts[start:end]

        return PromptListResponse(
            prompts=paginated_prompts,
            total=total,
            page=page,
            size=size
        )
    except Exception as e:
        handle_error("ProcessingError", f"Failed to list prompts: {e}", user_id=current_user.id)
        raise HTTPException(status_code=500, detail=f"Failed to list prompts: {e}")

@router.get("/{prompt_name}", summary="Load a Specific Prompt", response_model=PromptSchema)
def load_specific_prompt(
    prompt_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Load the content and metadata of a specific prompt for the current user.
    """
    try:
        prompt_content = load_prompt(session=db, name=prompt_name, user_id=current_user.id)
        if prompt_content is None:
            raise HTTPException(status_code=404, detail="Prompt not found.")

        # Fetch prompt details for metadata
        prompt = db.query(Prompt).filter_by(user_id=current_user.id, name=prompt_name).first()
        return PromptSchema(
            name=prompt.name,
            description=prompt.description,
            tags=prompt.tags.split(",") if prompt.tags else [],
            content=prompt.content,
            id=prompt.id,
            user_id=prompt.user_id,
            created_at=prompt.created_at,
            updated_at=prompt.updated_at
        )
    except Exception as e:
        handle_error("ProcessingError", f"Failed to load prompt '{prompt_name}': {e}", user_id=current_user.id)
        raise HTTPException(status_code=500, detail=f"Failed to load prompt '{prompt_name}': {e}")

@router.post("/save", summary="Save a New Prompt", response_model=dict)
def save_new_prompt(
    prompt: PromptCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Save a new prompt or overwrite an existing one for the current user.
    """
    try:
        # Check if prompt with the same name exists
        existing_prompts = list_saved_prompts(session=db, user_id=current_user.id)
        if prompt.name in existing_prompts:
            overwrite = True
        else:
            overwrite = False

        save_prompt(
            session=db,
            name=prompt.name,
            content=prompt.content,
            user_id=current_user.id,
            description=prompt.description,
            tags=prompt.tags
        )
        if overwrite:
            message = f"Prompt '{prompt.name}' updated successfully!"
        else:
            message = f"Prompt '{prompt.name}' created successfully!"
        return {"message": message}
    except Exception as e:
        handle_error("ProcessingError", f"Failed to save prompt '{prompt.name}': {e}", user_id=current_user.id)
        raise HTTPException(status_code=500, detail=f"Failed to save prompt '{prompt.name}': {e}")

@router.put("/{prompt_name}", summary="Update an Existing Prompt", response_model=dict)
def update_prompt(
    prompt_name: str,
    prompt_update: PromptUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update the description, tags, or content of an existing prompt.
    """
    try:
        # Ensure the prompt exists
        existing_prompts = list_saved_prompts(session=db, user_id=current_user.id)
        if prompt_name not in existing_prompts:
            raise HTTPException(status_code=404, detail="Prompt not found.")

        # Load existing content
        existing_content = load_prompt(session=db, name=prompt_name, user_id=current_user.id)
        if existing_content is None:
            raise HTTPException(status_code=404, detail="Prompt not found.")

        # Update the prompt with new data
        new_content = prompt_update.content if prompt_update.content is not None else existing_content
        new_description = prompt_update.description
        new_tags = prompt_update.tags

        save_prompt(
            session=db,
            name=prompt_name,
            content=new_content,
            user_id=current_user.id,
            description=new_description,
            tags=new_tags
        )
        return {"message": f"Prompt '{prompt_name}' updated successfully!"}
    except Exception as e:
        handle_error("ProcessingError", f"Failed to update prompt '{prompt_name}': {e}", user_id=current_user.id)
        raise HTTPException(status_code=500, detail=f"Failed to update prompt '{prompt_name}': {e}")

@router.delete("/{prompt_name}", summary="Delete a Prompt", response_model=dict)
def delete_specific_prompt(
    prompt_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a specific saved prompt for the current user.
    """
    try:
        # Check if the prompt exists
        existing_prompts = list_saved_prompts(session=db, user_id=current_user.id)
        if prompt_name not in existing_prompts:
            raise HTTPException(status_code=404, detail="Prompt not found.")

        delete_prompt(session=db, name=prompt_name, user_id=current_user.id)
        return {"message": f"Prompt '{prompt_name}' deleted successfully!"}
    except Exception as e:
        handle_error("ProcessingError", f"Failed to delete prompt '{prompt_name}': {e}", user_id=current_user.id)
        raise HTTPException(status_code=500, detail=f"Failed to delete prompt '{prompt_name}': {e}")

@router.post("/bulk_delete", summary="Bulk Delete Prompts", response_model=dict)
def bulk_delete_prompts(
    prompt_names: List[str],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete multiple prompts at once for the current user.
    """
    try:
        deleted = []
        not_found = []
        for name in prompt_names:
            existing_prompts = list_saved_prompts(session=db, user_id=current_user.id)
            if name in existing_prompts:
                delete_prompt(session=db, name=name, user_id=current_user.id)
                deleted.append(name)
            else:
                not_found.append(name)
        message = f"Deleted prompts: {', '.join(deleted)}."
        if not_found:
            message += f" Prompts not found: {', '.join(not_found)}."
        return {"message": message}
    except Exception as e:
        handle_error("ProcessingError", f"Failed to bulk delete prompts: {e}", user_id=current_user.id)
        raise HTTPException(status_code=500, detail=f"Failed to bulk delete prompts: {e}")