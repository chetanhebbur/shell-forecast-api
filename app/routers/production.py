from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import date
from app.models.schemas import ProductionResponse, ProductionRecord
from app.services import data_store

router = APIRouter(prefix="/wells", tags=["Production"])

@router.get("/{well_id}/production", response_model=ProductionResponse)
def get_production(
    well_id: str,
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    limit: int = Query(500, ge=1, le=500),
):
    records = data_store.get_production(well_id, from_date, to_date)
    if records is None:
        raise HTTPException(status_code=404, detail=f"Well {well_id} not found")
    if not records:
        raise HTTPException(status_code=404, detail="No data in date range")
    records = records[:limit]
    return ProductionResponse(
        well_id=well_id,
        field_name=records[0]["field_name"],
        operator=records[0]["operator"],
        from_date=from_date,
        to_date=to_date,
        total=len(records),
        records=[ProductionRecord(**r) for r in records],
    )
