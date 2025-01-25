# app/routers/claude_callback.py

from fastapi import APIRouter, Request, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import httpx

from app.config.database import SessionLocal
from app.models.claude_batch import Batch
from app.utils.error_utils import handle_error
from app.utils.file_utils import save_processed_result
from app.routers.ws_results import broadcast_new_result

router = APIRouter(
    prefix="/processing/claude",
    tags=["Claude Integration Callback"],
)

@router.post("/batch_callback")
async def claude_integration_callback(request: Request):
    db: Session = SessionLocal()  # Initialize session at the beginning
    try:
        data = await request.json()
        job_id = data.get("job_id")
        final_result = data.get("final_result")

        if not job_id or final_result is None:
            raise HTTPException(status_code=400, detail="Missing job_id or final_result.")

        batch = db.query(Batch).filter(Batch.external_batch_id == job_id).first()
        if not batch:
            raise HTTPException(status_code=404, detail="No batch found for this job_id.")

        batch.status = "ended"
        batch.ended_at = datetime.utcnow()
        db.commit()

        user_id = batch.user_id
        uploaded_file_id = batch.uploaded_file_id  # Retrieve uploaded_file_id

        # e.g. save final text as processed file
        filename = f"{job_id}_final.txt"
        save_processed_result(db, filename, final_result, uploaded_file_id)  # Pass uploaded_file_id

        # Broadcast the result
        await broadcast_new_result({
            "job_id": job_id,
            "final_result": final_result,
            "timestamp": datetime.utcnow().isoformat()
        })
        return {"message": f"Callback received for job_id={job_id}"}

    except HTTPException as he:
        # Re-raise HTTP exceptions as they are
        raise he
    except Exception as e:
        handle_error("CallbackError", f"Callback processing failed: {e}", user_id=None, db=db)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()  # Ensure the session is closed in all cases
