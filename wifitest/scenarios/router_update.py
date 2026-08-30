"""Router firmware update training scenario.

Simulates a fake router admin page prompting a firmware update.
Does NOT store credentials. Shows a clear "this is a training page" banner.
"""
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from wifitest.logger import SessionLogger

HTML = """<!DOCTYPE html>
<html><head><title>Router Admin - Firmware Update</title>
<style>
body { font-family: sans-serif; background: #f0f0f0; padding: 2rem; }
.banner { background: #ffeb3b; padding: 1rem; border-radius: 8px;
          margin-bottom: 1rem; font-weight: bold; }
.card { background: white; padding: 2rem; border-radius: 8px;
        max-width: 500px; margin: 0 auto; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
h1 { color: #333; }
input { width: 100%; padding: 0.5rem; margin: 0.5rem 0; border: 1px solid #ccc;
        border-radius: 4px; box-sizing: border-box; }
button { background: #1976d2; color: white; padding: 0.75rem 1.5rem;
         border: none; border-radius: 4px; cursor: pointer; }
</style></head>
<body>
<div class="banner">⚠️ TRAINING SCENARIO - This is a simulated phishing page.
No credentials are stored.</div>
<div class="card">
<h1>Router Firmware Update Required</h1>
<p>Your router firmware is out of date. Please log in to apply the update.</p>
<form onsubmit="event.preventDefault(); alert('This is a training demo. No data was sent.');">
<label>Admin Username</label>
<input type="text" placeholder="admin" autocomplete="off">
<label>Password</label>
<input type="password" placeholder="••••••••" autocomplete="off">
<button type="submit">Apply Update</button>
</form>
</div>
</body></html>"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(HTML.encode())

    def do_POST(self):
        # SECURITY: Intentionally discard all POST data. Never store credentials.
        length = int(self.headers.get("Content-Length", 0))
        if length:
            self.rfile.read(length)
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(b"<h1>This is a training demo. No data was stored.</h1>")

    def log_message(self, format, *args):
        pass  # Suppress default logging


def start_server(port: int = 80, logger: SessionLogger = None) -> threading.Thread:
    """Start the router update scenario server in a background thread."""
    server = HTTPServer(("0.0.0.0", port), Handler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    if logger:
        logger.event("scenario_started", scenario="router-update", port=port)
    return t
