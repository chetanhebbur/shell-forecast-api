from fastapi import APIRouter
from app.models.schemas import WellListResponse, WellSummary
from app.services import data_store

router = APIRouter(prefix="/wells", tags=["Wells"])

@router.get("", response_model=WellListResponse)
def list_wells():
    wells = data_store.list_wells()
    return WellListResponse(total=len(wells), wells=[WellSummary(**w) for w in wells])
