# app/routers/prompts.py

from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.models.user import User
from app.providers.auth import get_current_user
from app.schemas.prompt_schemas import PromptSchema
from app.utils.file_utils import (
    list_saved_prompts,
    load_prompt,
    save_prompt,
    delete_prompt,
    handle_error
)

router = APIRouter(
    prefix="/prompts",
    tags=["Prompt Management"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", summary="List Saved Prompts", response_model=List[str])
def list_prompts(
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve a list of saved prompts for the current user.
    """
    try:
        prompts = list_saved_prompts(user_id=current_user.id)
        if "Default Prompt" not in prompts:
            prompts.insert(0, "Default Prompt")
        return prompts
    except Exception as e:
        handle_error("ProcessingError", f"Failed to list prompts: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list prompts: {e}")

@router.get("/{prompt_name}", summary="Load a Specific Prompt", response_model=PromptSchema)
def load_specific_prompt(
    prompt_name: str,
    current_user: User = Depends(get_current_user)
):
    """
    Load the content of a specific prompt for the current user.
    """
    try:
        content = load_prompt(prompt_name, user_id=current_user.id)
        if not content:
            raise HTTPException(status_code=404, detail="Prompt not found.")
        return PromptSchema(name=prompt_name, content=content)
    except Exception as e:
        handle_error("ProcessingError", f"Failed to load prompt: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load prompt: {e}")

@router.post("/save", summary="Save a New Prompt")
def save_new_prompt(
    prompt: PromptSchema,
    current_user: User = Depends(get_current_user)
):
    """
    Save a new prompt or overwrite an existing one for the current user.
    """
    try:
        save_prompt(prompt.name, prompt.content, user_id=current_user.id)
        return {"message": f"Prompt '{prompt.name}' saved successfully!"}
    except Exception as e:
        handle_error("ProcessingError", f"Failed to save prompt: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save prompt: {e}")

@router.delete("/{prompt_name}", summary="Delete a Prompt")
def delete_specific_prompt(
    prompt_name: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a specific saved prompt for the current user.
    """
    try:
        delete_prompt(prompt_name, user_id=current_user.id)
        return {"message": f"Prompt '{prompt_name}' deleted successfully!"}
    except Exception as e:
        handle_error("ProcessingError", f"Failed to delete prompt: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete prompt: {e}")
