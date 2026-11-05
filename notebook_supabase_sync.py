"""
🌊 BasinShift: Floodcast Jupyter Notebook to Supabase Synchronization Module
Use this module directly in FLOODCAST.ipynb or Colab to sync models, metrics, and forecasts.
"""

import os
import sys
import json
import numpy as np
from datetime import datetime, timezone
import urllib.request
import urllib.error

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

DEFAULT_SUPABASE_URL = os.getenv("SUPABASE_URL", "https://kgdyupauslkdqojqcwkw.supabase.co")
DEFAULT_SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

class BasinShiftSupabaseSync:
    def __init__(self, supabase_url=None, supabase_key=None):
        self.url = (supabase_url or os.getenv("SUPABASE_URL") or DEFAULT_SUPABASE_URL).rstrip("/")
        self.key = supabase_key or os.getenv("SUPABASE_KEY") or DEFAULT_SUPABASE_KEY

    def _request(self, endpoint, data=None, method="GET", upsert=False):
        full_url = f"{self.url}/rest/v1/{endpoint}"
        headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        if upsert:
            headers["Prefer"] = "resolution=merge-duplicates,return=representation"

        body = json.dumps(data).encode("utf-8") if data is not None else None
        req = urllib.request.Request(full_url, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req) as resp:
                resp_text = resp.read().decode("utf-8")
                return json.loads(resp_text) if resp_text else None
        except urllib.error.HTTPError as e:
            err_msg = e.read().decode("utf-8")
            print(f"❌ Supabase API Error ({endpoint} - {e.code}): {err_msg}")
            raise

    def sync_catchment(self, catchment_id, name, country="USA", lat=None, lon=None, drainage_area=None, safe_thresh=15.0, crit_thresh=30.0):
        """Upsert a catchment's metadata and flood thresholds."""
        record = [{
            "id": catchment_id,
            "name": name,
            "country": country,
            "latitude": lat,
            "longitude": lon,
            "drainage_area_km2": drainage_area,
            "safe_discharge_threshold": safe_thresh,
            "critical_discharge_threshold": crit_thresh
        }]
        return self._request("catchments", data=record, method="POST", upsert=True)

    def sync_forecast(self, catchment_id, forecast_origin, horizons, raw_preds, residuals_std=0.5, model_version="PyTorch-LSTM-HuberLoss"):
        """
        Formats raw model predictions and pushes to Supabase model_forecasts.
        Automatically triggers alert generation if safe threshold is exceeded.
        """
        preds = [float(p) for p in raw_preds]
        horizons_list = [int(h) for h in horizons]
        
        high_flow_prob = [float(np.clip(p / 30.0, 0.0, 1.0)) for p in preds]
        extreme_flow_prob = [float(np.clip(p / 50.0, 0.0, 1.0)) for p in preds]
        lower_bound = [float(round(p - 1.96 * residuals_std, 2)) for p in preds]
        upper_bound = [float(round(p + 1.96 * residuals_std, 2)) for p in preds]

        raw_payload = {
            "catchment_id": catchment_id,
            "forecast_origin": forecast_origin,
            "forecast_horizons_days": horizons_list,
            "predicted_discharge": preds,
            "high_flow_probability": high_flow_prob,
            "extreme_flow_probability": extreme_flow_prob,
            "prediction_intervals": {"lower": lower_bound, "upper": upper_bound}
        }

        record = [{
            "catchment_id": catchment_id,
            "forecast_origin": forecast_origin,
            "model_version": model_version,
            "horizons_days": horizons_list,
            "predicted_discharge": preds,
            "high_flow_probability": high_flow_prob,
            "extreme_flow_probability": extreme_flow_prob,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            "raw_schema_payload": raw_payload
        }]

        result = self._request("model_forecasts", data=record, method="POST")
        print(f"✅ Synced forecast for {catchment_id} to Supabase (Peak: {max(preds)} m³/s)")
        return result

    def log_model_experiment(self, model_name, test_rmse, test_mae, loss_function="Huber Loss", hyperparameters=None, weights_path=None, notes=None):
        """Logs model training run and evaluation metrics for the Model Lab UI."""
        record = [{
            "model_name": model_name,
            "test_rmse": float(test_rmse),
            "test_mae": float(test_mae),
            "loss_function": loss_function,
            "hyperparameters": hyperparameters or {},
            "weights_path": weights_path or "flood_lstm_weights.pth",
            "notes": notes or "Automated run from FLOODCAST.ipynb"
        }]
        result = self._request("model_experiments", data=record, method="POST")
        print(f"✅ Logged experiment metrics for {model_name}: RMSE={test_rmse}, MAE={test_mae}")
        return result

    def sync_historical_telemetry(self, records):
        """Batch upsert historical daily observations into historical_telemetry."""
        result = self._request("historical_telemetry", data=records, method="POST", upsert=True)
        print(f"✅ Upserted {len(records)} telemetry records.")
        return result

# Simple test execution
if __name__ == "__main__":
    client = BasinShiftSupabaseSync()
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    client.sync_forecast(
        catchment_id="camels_05503800",
        forecast_origin=now_str,
        horizons=[1, 3, 7],
        raw_preds=[13.2, 14.8, 19.4],
        model_version="PyTorch-LSTM-Production"
    )
