# app/routers/config.py

from fastapi import APIRouter, HTTPException
from app.models.config import ConfigRequest
from app.models.user_config import UserConfig
from app.config.api_config import configure_openai, configure_anthropic, configure_gemini
from app.utils.file_utils import handle_error, save_user_config, get_user_config

router = APIRouter(
    prefix="/config",
    tags=["Configuration"],
    responses={404: {"description": "Not found"}},
)

@router.post("/configure", summary="Configure AI Provider")
def configure_provider(config: ConfigRequest):
    """
    Configure the AI provider with the selected model and API key.
    """
    try:
        if config.provider_choice == "OpenAI":
            configure_openai(config.api_key)
        elif config.provider_choice == "Anthropic":
            configure_anthropic(config.api_key)
        elif config.provider_choice == "Gemini":
            configure_gemini(config.api_key)
        else:
            raise HTTPException(status_code=400, detail="Invalid provider choice.")
        return {"message": f"{config.provider_choice} configured successfully!"}
    except Exception as e:
        handle_error("APIError", f"Configuration failed: {e}")
        raise HTTPException(status_code=500, detail=f"Configuration failed: {e}")

@router.post("/save", summary="Save User Configuration", response_model=dict)
def save_configuration(user_config: UserConfig):
    """
    Save a user's configuration, including API keys.
    """
    try:
        config_dict = {
            "openai_api_key": user_config.openai_api_key,
            "anthropic_api_key": user_config.anthropic_api_key,
            "gemini_api_key": user_config.gemini_api_key
        }
        save_user_config(user_config.user_id, config_dict)
        return {"message": "User configuration saved successfully."}
    except Exception as e:
        handle_error("APIError", f"Failed to save user configuration: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save user configuration: {e}")

@router.get("/get/{user_id}", summary="Get User Configuration", response_model=UserConfig)
def get_configuration(user_id: str):
    """
    Retrieve a user's configuration by user ID.
    """
    try:
        config = get_user_config(user_id)
        if not config:
            raise HTTPException(status_code=404, detail="User configuration not found.")
        return UserConfig(user_id=user_id, **config)
    except HTTPException as he:
        raise he
    except Exception as e:
        handle_error("APIError", f"Failed to retrieve user configuration: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve user configuration: {e}")
