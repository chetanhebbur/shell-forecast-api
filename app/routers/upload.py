from fastapi import APIRouter, HTTPException
from app.models.schemas import UploadRequest, UploadResponse
from app.services import data_store

router = APIRouter(prefix="/wells", tags=["Upload"])

@router.post("/upload", response_model=UploadResponse)
def upload_json(payload: UploadRequest):
    if not payload.records:
        raise HTTPException(status_code=400, detail="No records provided")
    saved, errors, blob_path = data_store.save_records(payload.records)
    return UploadResponse(
        status="SUCCESS" if not errors else "PARTIAL",
        records_received=len(payload.records),
        records_saved=saved,
        rejected=len(errors),
        errors=errors,
        blob_path=blob_path,
    )
