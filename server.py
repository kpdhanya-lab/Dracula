"""
🌊 BasinShift Disaster Intelligence Platform - Unified Local Server & Groq API Bridge
Serves frontend static assets on port 3000 and provides /api/groq_query endpoint.
"""

import os
import sys
import json
import urllib.request
import urllib.error
from http.server import SimpleHTTPRequestHandler, HTTPServer
from datetime import datetime, timezone

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

PORT = int(os.getenv("PORT", 3000))
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "stitch_floodcast_disaster_intelligence_platform")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://kgdyupauslkdqojqcwkw.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

def call_groq(user_query, telemetry_context=""):
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
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
        "User-Agent": "BasinShift-Copilot/1.0"
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ],
        "temperature": 0.2
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        return res["choices"][0]["message"]["content"]

def log_to_supabase(session_id, catchment_id, user_prompt, assistant_response):
    try:
        url = f"{SUPABASE_URL}/rest/v1/copilot_messages"
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
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
        urllib.request.urlopen(req)
    except Exception as e:
        print(f"Notice: Supabase log warning: {e}")

class BasinShiftHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=FRONTEND_DIR, **kwargs)

    def do_GET(self):
        if self.path == "/api/config":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            config_payload = {
                "supabaseUrl": SUPABASE_URL,
                "supabaseKey": SUPABASE_KEY
            }
            self.wfile.write(json.dumps(config_payload).encode("utf-8"))
            return
        return super().do_GET()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_POST(self):
        if self.path == "/api/groq_query":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            try:
                data = json.loads(body)
                query = data.get("query", "")
                catchment_id = data.get("catchment_id", "camels_05503800")
                session_id = data.get("session_id", "default-session")
                context = data.get("context", "")

                print(f"🤖 Processing query via Groq: '{query[:60]}...'")
                answer = call_groq(query, context)
                
                # Async background log to Supabase
                log_to_supabase(session_id, catchment_id, query, answer)

                response_data = {
                    "success": True,
                    "query": query,
                    "response": answer,
                    "model": GROQ_MODEL
                }

                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps(response_data).encode("utf-8"))

            except Exception as e:
                print(f"❌ Groq Query Error: {e}")
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

def run_server():
    server = HTTPServer(("0.0.0.0", PORT), BasinShiftHandler)
    print(f"🌊 BasinShift Server running on http://localhost:{PORT}")
    print(f"⚡ Groq LLM Engine: {GROQ_MODEL}")
    server.serve_forever()

if __name__ == "__main__":
    run_server()

