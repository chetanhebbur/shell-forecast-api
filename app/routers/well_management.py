from fastapi import APIRouter, HTTPException
from app.models.schemas import UploadedRecord
from app.services import data_store

router = APIRouter(prefix="/wells", tags=["Well Management"])

@router.put("/{well_id}")
def update_well(well_id: str, record: UploadedRecord):
    records = data_store.get_production(well_id)
    if records is None:
        raise HTTPException(status_code=404, detail=f"Well {well_id} not found")
    data_store._store[well_id].append(record.model_dump())
    return {
        "status": "UPDATED",
        "well_id": well_id,
        "message": f"Well {well_id} updated successfully",
        "total_records": len(data_store._store[well_id])
    }

@router.delete("/{well_id}")
def delete_well(well_id: str):
    records = data_store.get_production(well_id)
    if records is None:
        raise HTTPException(status_code=404, detail=f"Well {well_id} not found")
    record_count = len(data_store._store[well_id])
    del data_store._store[well_id]
    return {
        "status": "DELETED",
        "well_id": well_id,
        "message": f"Well {well_id} and {record_count} records deleted successfully"
    }
