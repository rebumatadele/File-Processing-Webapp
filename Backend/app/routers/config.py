# app/routers/config.py

from fastapi import APIRouter, HTTPException
from app.models.config import ConfigRequest
from app.config.api_config import configure_openai, configure_anthropic, configure_gemini
from app.utils.file_utils import handle_error

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
    