import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from dateutil.relativedelta import relativedelta
import warnings
warnings.filterwarnings("ignore")

def _exp(t, qi, di): return qi * np.exp(-di * t)
def _hyp(t, qi, di, b): return qi / np.power(np.maximum(1 + b * di * t, 1e-10), 1.0 / b)
def _harm(t, qi, di): return qi / np.maximum(1 + di * t, 1e-10)

def _fit(t, q, model):
    try:
        qi0 = float(q[0])
        if model == "exponential":
            popt, _ = curve_fit(_exp, t, q, p0=[qi0, 0.05], bounds=([0, 1e-6], [qi0*3, 0.99]), maxfev=8000)
            q_fit = _exp(t, *popt)
            params = {"qi": popt[0], "di": popt[1], "b": 0.0}
        elif model == "hyperbolic":
            popt, _ = curve_fit(_hyp, t, q, p0=[qi0, 0.05, 0.5], bounds=([0, 1e-6, 0.01], [qi0*3, 0.99, 1.99]), maxfev=8000)
            q_fit = _hyp(t, *popt)
            params = {"qi": popt[0], "di": popt[1], "b": popt[2]}
        else:
            popt, _ = curve_fit(_harm, t, q, p0=[qi0, 0.05], bounds=([0, 1e-6], [qi0*3, 0.99]), maxfev=8000)
            q_fit = _harm(t, *popt)
            params = {"qi": popt[0], "di": popt[1], "b": 1.0}
        ss_res = np.sum((q - q_fit) ** 2)
        ss_tot = np.sum((q - np.mean(q)) ** 2)
        r2 = float(1 - ss_res / ss_tot) if ss_tot > 1e-10 else 0.0
        return params, round(r2, 4)
    except:
        return None, -999.0

def run_dca(records, forecast_months=24, model="auto"):
    df = pd.DataFrame(records)
    df["production_date"] = pd.to_datetime(df["production_date"])
    df = df.sort_values("production_date").reset_index(drop=True)
    t = np.arange(len(df), dtype=float)
    q_oil = df["oil_bopd"].values.astype(float)
    q_gas = df["gas_mmscfd"].values.astype(float)
    gor = float(np.mean(q_gas / np.maximum(q_oil, 0.1)))
    models_to_try = ["exponential", "hyperbolic", "harmonic"] if model == "auto" else [model]
    best_params, best_r2, best_model = None, -999.0, "exponential"
    for m in models_to_try:
        params, r2 = _fit(t, q_oil, m)
        if params and r2 > best_r2:
            best_params, best_r2, best_model = params, r2, m
    if best_params is None:
        raise ValueError("DCA fit failed")
    last_date = df["production_date"].iloc[-1].date()
    t_last = float(len(df) - 1)
    forecast_points = []
    for i in range(1, forecast_months + 1):
        t_f = t_last + i
        if best_model == "exponential": q_f = _exp(t_f, best_params["qi"], best_params["di"])
        elif best_model == "hyperbolic": q_f = _hyp(t_f, best_params["qi"], best_params["di"], best_params["b"])
        else: q_f = _harm(t_f, best_params["qi"], best_params["di"])
        q_f = max(float(q_f), 0.0)
        forecast_points.append({
            "forecast_date": last_date + relativedelta(months=i),
            "forecast_month": i,
            "oil_forecast_bopd": round(q_f, 2),
            "gas_forecast_mmscfd": round(q_f * gor, 4),
        })
    return {
        "dca_model_used": best_model,
        "qi_oil": round(best_params["qi"], 2),
        "di_oil": round(best_params["di"], 6),
        "b_factor": round(best_params["b"], 4),
        "r2_score": best_r2,
        "forecast_months": forecast_months,
        "forecast": forecast_points,
    }
