"""Generic login page training scenario.

Simulates a captive portal login page. Does NOT store credentials.
"""
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from wifitest.logger import SessionLogger

HTML = """<!DOCTYPE html>
<html><head><title>Network Login</title>
<style>
body { font-family: sans-serif; background: linear-gradient(135deg, #667eea, #764ba2);
       min-height: 100vh; display: flex; align-items: center; justify-content: center; }
.banner { position: fixed; top: 0; left: 0; right: 0; background: #ffeb3b;
          padding: 0.75rem; text-align: center; font-weight: bold; z-index: 100; }
.card { background: white; padding: 2.5rem; border-radius: 12px; width: 100%;
        max-width: 400px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); }
h1 { color: #333; margin-bottom: 0.5rem; }
p { color: #666; margin-bottom: 1.5rem; }
input { width: 100%; padding: 0.75rem; margin: 0.5rem 0; border: 1px solid #ddd;
        border-radius: 6px; box-sizing: border-box; font-size: 1rem; }
button { width: 100%; background: #667eea; color: white; padding: 0.75rem;
         border: none; border-radius: 6px; cursor: pointer; font-size: 1rem;
         margin-top: 1rem; }
button:hover { background: #5568d3; }
</style></head>
<body>
<div class="banner">️ TRAINING SCENARIO - Simulated captive portal. No data stored.</div>
<div class="card">
<h1>Welcome to Guest WiFi</h1>
<p>Please sign in to access the internet.</p>
<form onsubmit="event.preventDefault(); alert('Training demo - no data sent.');">
<input type="email" placeholder="Email address" autocomplete="off">
<input type="password" placeholder="Password" autocomplete="off">
<button type="submit">Sign In</button>
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
        length = int(self.headers.get("Content-Length", 0))
        if length:
            self.rfile.read(length)
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(b"<h1>Training demo - no credentials stored.</h1>")

    def log_message(self, format, *args):
        pass


def start_server(port: int = 80, logger: SessionLogger = None) -> threading.Thread:
    server = HTTPServer(("0.0.0.0", port), Handler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    if logger:
        logger.event("scenario_started", scenario="login", port=port)
    return t
