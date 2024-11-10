# app/routers/prompts.py

from fastapi import APIRouter, HTTPException
from typing import List
from app.models.prompt import Prompt
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
def list_prompts():
    """
    Retrieve a list of saved prompts.
    """
    try:
        prompts = list_saved_prompts()
        if "Default Prompt" not in prompts:
            prompts.insert(0, "Default Prompt")
        return prompts
    except Exception as e:
        handle_error("ProcessingError", f"Failed to list prompts: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list prompts: {e}")

@router.get("/{prompt_name}", summary="Load a Specific Prompt", response_model=Prompt)
def load_specific_prompt(prompt_name: str):
    """
    Load the content of a specific prompt.
    """
    try:
        content = load_prompt(prompt_name)
        if not content:
            raise HTTPException(status_code=404, detail="Prompt not found.")
        return Prompt(name=prompt_name, content=content)
    except HTTPException as he:
        raise he
    except Exception as e:
        handle_error("ProcessingError", f"Failed to load prompt: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load prompt: {e}")

@router.post("/save", summary="Save a New Prompt")
def save_new_prompt(prompt: Prompt):
    """
    Save a new prompt or overwrite an existing one.
    """
    try:
        save_prompt(prompt.name, prompt.content)
        return {"message": f"Prompt '{prompt.name}' saved successfully!"}
    except Exception as e:
        handle_error("ProcessingError", f"Failed to save prompt: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save prompt: {e}")

@router.delete("/{prompt_name}", summary="Delete a Prompt")
def delete_specific_prompt(prompt_name: str):
    """
    Delete a specific saved prompt.
    """
    try:
        delete_prompt(prompt_name)
        return {"message": f"Prompt '{prompt_name}' deleted successfully!"}
    except Exception as e:
        handle_error("ProcessingError", f"Failed to delete prompt: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete prompt: {e}")
