import os
import json
import urllib.request
import urllib.error
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://kgdyupauslkdqojqcwkw.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

def call_groq(user_query, telemetry_context=""):
    api_key = os.getenv("GROQ_API_KEY", GROQ_API_KEY)
    model = os.getenv("GROQ_MODEL", GROQ_MODEL)
    if not api_key:
        raise ValueError("GROQ_API_KEY is not configured in environment variables.")

    system_prompt = f"""You are the BasinShift AI Hydrologist Copilot & Computational Engine.
The user is an emergency operator, hydrologist, or researcher querying the flood forecasting platform.
Database and hydrological telemetry context:
- Available Tables: public.catchments (id, name, safe_discharge_threshold, drainage_area_km2), public.historical_telemetry (catchment_id, recorded_date, observed_discharge, precipitation, soil_moisture), public.model_forecasts (horizons_days [1,3,7], predicted_discharge [12.4, 14.1, 18.7], confidence intervals), public.flood_alerts.
- Target Catchment Context: {telemetry_context or 'CAMELS #05503800 - Illinois River at Marseilles. Safe threshold: 15.0 m3/s, Critical threshold: 30.0 m3/s.'}
- Target Model: PyTorch LSTM Sequence Model (Test RMSE: 2.49 m3/s, Test MAE: 0.76 m3/s, Huber Loss).

For ANY question:
1. FORMULATE A PRECISE PYTHON/POLARS QUERY:
Write an idiomatic, clean Python script using Polars/Pandas that queries the database/telemetry dataset to compute the exact statistics, discharge sums, moving averages, or threshold exceedances.
2. COMPUTE THE THEORETICAL OUTPUT:
Provide the theoretical mathematical output and calculated values (e.g. mean discharge, peak flow in m³/s, breach percentage, confidence interval).
3. PROVIDE OPERATIONAL & CIVIC SAFETY DIRECTIVE:
Explain the actionable real-world conclusion for emergency flood operators (e.g. Inundation warning, levee status, sensor verification).

Format your response cleanly with these three markdown sections:
### 🐍 Generated Python Query
```python
<clean python polars/pandas code>
```
### 📊 Theoretical Computational Output
<formatted output table or calculated numeric metrics with units>

### 🚨 Operational & Civic Assessment
<practical interpretation and safety action>
"""

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "BasinShift-Copilot/1.0"
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ],
        "temperature": 0.2
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
    with urllib.request.urlopen(req, timeout=45) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        return res["choices"][0]["message"]["content"]

def log_to_supabase(session_id, catchment_id, user_prompt, assistant_response):
    supa_url = os.getenv("SUPABASE_URL", SUPABASE_URL)
    supa_key = os.getenv("SUPABASE_KEY", SUPABASE_KEY)
    if not supa_key:
        return
    try:
        url = f"{supa_url}/rest/v1/copilot_messages"
        headers = {
            "apikey": supa_key,
            "Authorization": f"Bearer {supa_key}",
            "Content-Type": "application/json"
        }
        data = [{
            "session_id": session_id or "session-live",
            "catchment_id": catchment_id or "camels_05503800",
            "user_prompt": user_prompt,
            "assistant_response": assistant_response,
            "telemetry_grounding": {"engine": "Groq-GPT-OSS-120B", "timestamp": datetime.now(timezone.utc).isoformat()}
        }]
        req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers, method="POST")
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        print(f"Notice: Supabase log warning: {e}")

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_POST(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            data = json.loads(body) if body else {}

            query = data.get("query", "")
            catchment_id = data.get("catchment_id", "camels_05503800")
            session_id = data.get("session_id", "default-session")
            context = data.get("context", "")

            answer = call_groq(query, context)
            log_to_supabase(session_id, catchment_id, query, answer)

            response_data = {
                "success": True,
                "query": query,
                "response": answer,
                "model": os.getenv("GROQ_MODEL", GROQ_MODEL)
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode("utf-8"))

        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode("utf-8"))

