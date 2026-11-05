import os
import json
from http.server import BaseHTTPRequestHandler

# Attempt to load local .env if available during local development
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        payload = {
            "supabaseUrl": os.getenv("SUPABASE_URL", "https://kgdyupauslkdqojqcwkw.supabase.co"),
            "supabaseKey": os.getenv("SUPABASE_KEY", "")
        }
        self.wfile.write(json.dumps(payload).encode("utf-8"))

