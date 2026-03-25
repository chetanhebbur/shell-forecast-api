import logging
from datetime import date
from typing import Dict, List, Optional
import pandas as pd

logger = logging.getLogger(__name__)

_store: Dict[str, List[dict]] = {}

def _seed_data():
    global _store
    records = [
        *[{"well_id":"SHELL-NL-001","field_name":"Groningen","operator":"Shell",
           "production_date": f"202{2 if i<12 else 3}-{((i%12)+1):02d}-01",
           "oil_bopd": round(1250 * (0.96**i), 0),
           "gas_mmscfd": round(2.45 * (0.96**i), 2),
           "water_bwpd": round(320 * (1.04**i), 0),
           "wellhead_pressure_psi": round(2800 - i*16, 0),
           "tubing_pressure_psi": round(2200 - i*13, 0),
           "status": "ACTIVE"} for i in range(24)],
        *[{"well_id":"SHELL-NG-002","field_name":"Bonga","operator":"Shell",
           "production_date": f"202{2 if i<12 else 3}-{((i%12)+1):02d}-01",
           "oil_bopd": round(8500 * (0.97**i), 0),
           "gas_mmscfd": round(12.3 * (0.97**i), 2),
           "water_bwpd": round(1200 * (1.03**i), 0),
           "wellhead_pressure_psi": round(4200 - i*18, 0),
           "tubing_pressure_psi": round(3800 - i*15, 0),
           "status": "ACTIVE"} for i in range(24)],
        *[{"well_id":"SHELL-AU-003","field_name":"Prelude","operator":"Shell",
           "production_date": f"202{2 if i<12 else 3}-{((i%12)+1):02d}-01",
           "oil_bopd": round(3200 * (0.98**i), 0),
           "gas_mmscfd": round(18.5 * (0.98**i), 2),
           "water_bwpd": round(580 * (1.02**i), 0),
           "wellhead_pressure_psi": round(5100 - i*12, 0),
           "tubing_pressure_psi": round(4600 - i*10, 0),
           "status": "ACTIVE"} for i in range(24)],
    ]
    for r in records:
        _store.setdefault(r["well_id"], []).append(r)
    logger.info(f"Seeded {len(records)} records for {len(_store)} wells")

_seed_data()

def list_wells():
    summaries = []
    for well_id, records in _store.items():
        df = pd.DataFrame(records)
        df["production_date"] = pd.to_datetime(df["production_date"])
        summaries.append({
            "well_id": well_id,
            "field_name": df["field_name"].iloc[0],
            "operator": df["operator"].iloc[0],
            "status": df["status"].iloc[-1],
            "first_date": df["production_date"].min().date(),
            "last_date": df["production_date"].max().date(),
            "record_count": len(df),
            "avg_oil_bopd": round(df["oil_bopd"].mean(), 1),
            "avg_gas_mmscfd": round(df["gas_mmscfd"].mean(), 3),
        })
    return summaries

def get_production(well_id, from_date=None, to_date=None):
    records = _store.get(well_id)
    if records is None:
        return None
    df = pd.DataFrame(records)
    df["production_date"] = pd.to_datetime(df["production_date"])
    if from_date:
        df = df[df["production_date"] >= pd.Timestamp(from_date)]
    if to_date:
        df = df[df["production_date"] <= pd.Timestamp(to_date)]
    return df.sort_values("production_date").to_dict("records")

def save_records(records):
    saved, errors = 0, []
    for r in records:
        try:
            _store.setdefault(r.well_id, []).append(r.model_dump())
            saved += 1
        except Exception as e:
            errors.append(str(e))
    return saved, errors, None
