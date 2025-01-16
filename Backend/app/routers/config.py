# app/routers/config.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.providers.auth import get_current_user, get_db
from app.schemas.user_config_schemas import UserConfigResponse, ConfigRequest
from app.models.user_config import UserConfig
from app.config.api_config import configure_openai, configure_anthropic, configure_gemini
from app.utils.file_utils import handle_error

router = APIRouter(
    prefix="/config",
    tags=["Configuration"],
    responses={404: {"description": "Not found"}},
)

@router.post("/save", summary="Save User Configuration", response_model=UserConfigResponse)
def save_configuration(
    config_request: ConfigRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Save a user's configuration, including API keys.
    """
    try:
        user_config = db.query(UserConfig).filter(UserConfig.user_id == current_user.id).first()
        
        # Update or create user configuration
        if user_config:
            if config_request.provider_choice == "OpenAI":
                user_config.openai_api_key = config_request.api_key
            elif config_request.provider_choice == "Anthropic":
                user_config.anthropic_api_key = config_request.api_key
            elif config_request.provider_choice == "Gemini":
                user_config.gemini_api_key = config_request.api_key
            else:
                raise HTTPException(status_code=400, detail="Invalid provider choice.")
        else:
            user_config = UserConfig(
                user_id=current_user.id,
                openai_api_key=config_request.api_key if config_request.provider_choice == "OpenAI" else None,
                anthropic_api_key=config_request.api_key if config_request.provider_choice == "Anthropic" else None,
                gemini_api_key=config_request.api_key if config_request.provider_choice == "Gemini" else None,
            )
            db.add(user_config)
        
        db.commit()
        db.refresh(user_config)
        
        return user_config
    except Exception as e:
        handle_error("APIError", f"Failed to save user configuration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save user configuration: {e}",
        )


@router.get("/get", summary="Get User Configuration", response_model=UserConfigResponse)
def get_configuration(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve the current user's configuration.
    """
    try:
        user_config = db.query(UserConfig).filter(UserConfig.user_id == current_user.id).first()
        if not user_config:
            raise HTTPException(status_code=404, detail="User configuration not found.")
        return user_config
    except Exception as e:
        handle_error("APIError", f"Failed to retrieve user configuration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user configuration: {e}",
        )