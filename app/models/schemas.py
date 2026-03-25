from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import date
from enum import Enum

class DCAModel(str, Enum):
    exponential = "exponential"
    hyperbolic = "hyperbolic"
    harmonic = "harmonic"
    auto = "auto"

class WellStatus(str, Enum):
    active = "ACTIVE"
    inactive = "INACTIVE"
    suspended = "SUSPENDED"

class WellSummary(BaseModel):
    well_id: str
    field_name: str
    operator: str
    status: WellStatus
    first_date: date
    last_date: date
    record_count: int
    avg_oil_bopd: float
    avg_gas_mmscfd: float

class WellListResponse(BaseModel):
    total: int
    wells: List[WellSummary]

class ProductionRecord(BaseModel):
    production_date: date
    oil_bopd: float
    gas_mmscfd: float
    water_bwpd: float
    wellhead_pressure_psi: Optional[float] = None
    tubing_pressure_psi: Optional[float] = None
    status: WellStatus

class ProductionResponse(BaseModel):
    well_id: str
    field_name: str
    operator: str
    from_date: Optional[date] = None
    to_date: Optional[date] = None
    records: List[ProductionRecord]
    total: int

class ForecastPoint(BaseModel):
    forecast_date: date
    forecast_month: int
    oil_forecast_bopd: float
    gas_forecast_mmscfd: float

class ForecastResponse(BaseModel):
    well_id: str
    field_name: str
    operator: str
    dca_model_used: DCAModel
    qi_oil: float
    di_oil: float
    b_factor: float
    r2_score: float
    forecast_months: int
    forecast: List[ForecastPoint]

class UploadedRecord(BaseModel):
    well_id: str
    field_name: str
    operator: str
    production_date: str
    oil_bopd: float
    gas_mmscfd: float
    water_bwpd: float
    wellhead_pressure_psi: Optional[float] = None
    tubing_pressure_psi: Optional[float] = None
    status: str = "ACTIVE"

    @field_validator("production_date")
    @classmethod
    def validate_date(cls, v):
        from datetime import datetime
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError("production_date must be YYYY-MM-DD")

class UploadRequest(BaseModel):
    records: List[UploadedRecord]

class UploadResponse(BaseModel):
    status: str
    records_received: int
    records_saved: int
    rejected: int
    errors: List[str]
    blob_path: Optional[str] = None
