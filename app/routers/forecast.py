from fastapi import APIRouter, HTTPException, Query
from app.models.schemas import ForecastResponse, ForecastPoint, DCAModel
from app.services import data_store, dca_engine

router = APIRouter(prefix="/wells", tags=["Forecast"])

@router.get("/{well_id}/forecast", response_model=ForecastResponse)
def get_forecast(
    well_id: str,
    forecast_months: int = Query(24, ge=1, le=120),
    model: DCAModel = Query(DCAModel.auto),
):
    records = data_store.get_production(well_id)
    if records is None:
        raise HTTPException(status_code=404, detail=f"Well {well_id} not found")
    if len(records) < 6:
        raise HTTPException(status_code=422, detail="Need at least 6 months history")
    try:
        result = dca_engine.run_dca(records=records, forecast_months=forecast_months, model=model.value)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return ForecastResponse(
        well_id=well_id,
        field_name=records[0]["field_name"],
        operator=records[0]["operator"],
        forecast=[ForecastPoint(**p) for p in result["forecast"]],
        **{k: v for k, v in result.items() if k != "forecast"},
    )
