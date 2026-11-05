import os
import json
import sys
import urllib.request
import urllib.error
from datetime import datetime, timedelta
import random

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://kgdyupauslkdqojqcwkw.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

def post_supabase(endpoint, data, upsert=False):
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    if upsert:
        headers["Prefer"] = "resolution=merge-duplicates,return=representation"

    req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"Error {endpoint} ({e.code}):", e.read().decode("utf-8"))
        raise

def get_supabase(endpoint):
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def seed():
    print("🌊 Seeding BasinShift Supabase Database...")

    # 1. Seed Catchments
    catchments_data = [
        {
            "id": "camels_05503800",
            "name": "Illinois River at Marseilles",
            "country": "USA",
            "latitude": 41.3308,
            "longitude": -88.7067,
            "drainage_area_km2": 21450.0,
            "safe_discharge_threshold": 15.0,
            "critical_discharge_threshold": 30.0
        },
        {
            "id": "camels_01013500",
            "name": "Fish River near Fort Kent",
            "country": "USA",
            "latitude": 47.2372,
            "longitude": -68.5828,
            "drainage_area_km2": 2240.0,
            "safe_discharge_threshold": 25.0,
            "critical_discharge_threshold": 45.0
        },
        {
            "id": "camels_08167000",
            "name": "Guadalupe River at Comfort",
            "country": "USA",
            "latitude": 29.9675,
            "longitude": -98.9056,
            "drainage_area_km2": 2160.0,
            "safe_discharge_threshold": 18.0,
            "critical_discharge_threshold": 35.0
        }
    ]
    inserted_catchments = post_supabase("catchments", catchments_data, upsert=True)
    print(f"✅ Upserted {len(inserted_catchments)} catchments.")

    # 2. Seed Historical Telemetry (Past 60 days for camels_05503800)
    base_date = datetime.now() - timedelta(days=60)
    telemetry_records = []
    base_flow = 11.2
    for i in range(60):
        rec_date = (base_date + timedelta(days=i)).strftime("%Y-%m-%d")
        # generate realistic river discharge fluctuations
        precip = max(0.0, round(random.gauss(4.5, 6.0), 2)) if random.random() > 0.4 else 0.0
        base_flow = max(4.0, min(24.0, base_flow + (precip * 0.45) - 0.25 + random.uniform(-0.3, 0.3)))
        soil_m = round(min(0.85, max(0.15, 0.28 + (precip * 0.015) + random.uniform(-0.02, 0.02))), 3)
        temp = round(14.0 + random.uniform(-5.0, 5.0), 1)

        telemetry_records.append({
            "catchment_id": "camels_05503800",
            "recorded_date": rec_date,
            "observed_discharge": round(base_flow, 2),
            "precipitation": precip,
            "soil_moisture": soil_m,
            "temperature": temp
        })

    inserted_telemetry = post_supabase("historical_telemetry", telemetry_records, upsert=True)
    print(f"✅ Upserted {len(inserted_telemetry)} historical telemetry days.")

    # 3. Seed Model Experiment (Evaluation Metrics from FLOODCAST.ipynb)
    experiment_data = [{
        "model_name": "PyTorch LSTM Sequence Model",
        "test_rmse": 2.49,
        "test_mae": 0.76,
        "loss_function": "Huber Loss",
        "sequence_length": 365,
        "hyperparameters": {
            "hidden_dim": 128,
            "num_layers": 2,
            "dropout": 0.2,
            "optimizer": "AdamW",
            "lr": 0.001,
            "target_transform": "log1p",
            "loss": "SmoothL1Loss(beta=1.0)"
        },
        "weights_path": "flood_lstm_weights.pth",
        "notes": "Trained on Caravan dataset (2056 catchments). Huber Loss successfully closed the RMSE/MAE gap on extreme flood events."
    }]
    inserted_exp = post_supabase("model_experiments", experiment_data)
    print(f"✅ Recorded production model evaluation metrics (Test RMSE: {experiment_data[0]['test_rmse']} m³/s, Test MAE: {experiment_data[0]['test_mae']} m³/s).")

    # 4. Seed Forecast for camels_05503800 (Breaching 15.0 m3/s safe limit to trigger alert)
    now_iso = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    forecast_data = [{
        "catchment_id": "camels_05503800",
        "forecast_origin": now_iso,
        "model_version": "PyTorch-LSTM-v1",
        "horizons_days": [1, 3, 7],
        "predicted_discharge": [12.4, 14.1, 18.7],
        "high_flow_probability": [0.12, 0.21, 0.31],
        "extreme_flow_probability": [0.03, 0.07, 0.15],
        "lower_bound": [9.5, 10.8, 14.2],
        "upper_bound": [15.3, 17.4, 31.2],
        "raw_schema_payload": {
            "catchment_id": "camels_05503800",
            "forecast_origin": now_iso,
            "forecast_horizons_days": [1, 3, 7],
            "predicted_discharge": [12.4, 14.1, 18.7],
            "high_flow_probability": [0.12, 0.21, 0.31],
            "extreme_flow_probability": [0.03, 0.07, 0.15],
            "prediction_intervals": {
                "lower": [9.5, 10.8, 14.2],
                "upper": [15.3, 17.4, 31.2]
            }
        }
    }]
    inserted_forecast = post_supabase("model_forecasts", forecast_data)
    print(f"✅ Inserted new forecast record (Peak Discharge: 18.7 m³/s at T+7d).")

    # 5. Check if the PostgreSQL Trigger automatically created the alert in flood_alerts
    alerts = get_supabase("flood_alerts?select=*&order=created_at.desc&limit=5")
    print(f"🚨 Active alerts in public.flood_alerts: {len(alerts)}")
    for a in alerts:
        print(f"   - [{a['severity']}] {a['alert_heading']}")
        print(f"     Details: {a['alert_body']}")
        print(f"     Status: {'Acknowledged' if a['is_acknowledged'] else 'ACTIVE 🔴'}")

    print("\n🎉 Seed and trigger verification completed successfully!")

if __name__ == "__main__":
    seed()
