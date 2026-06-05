"""
Local dev launcher with HubSpot callback path support.

Streamlit does not serve /auth/hubspot/callback by itself. This script:
  - runs Streamlit on STREAMLIT_INTERNAL_PORT (default 8505)
  - listens on PORT (default 8504) and redirects
      /auth/hubspot/callback?...  ->  http://localhost:8505/?...
  - redirects all other /8504/* traffic to Streamlit on 8505

Use:
  python run_app.py

Open the app at http://localhost:8505 (proxy) or http://localhost:8505 (direct).
Keep HUBSPOT_REDIRECT_URI=http://localhost:8505/auth/hubspot/callback in .env.
"""

from __future__ import annotations

import os
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from urllib.parse import urlparse

PUBLIC_PORT = int(os.environ.get("PORT", "8504"))
STREAMLIT_PORT = int(os.environ.get("STREAMLIT_INTERNAL_PORT", "8505"))


class _RedirectHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        target_base = f"http://localhost:{STREAMLIT_PORT}"
        if parsed.path.rstrip("/") == "/auth/hubspot/callback":
            location = f"{target_base}/"
            if parsed.query:
                location = f"{location}?{parsed.query}"
        else:
            location = f"{target_base}{self.path}"
        self.send_response(302)
        self.send_header("Location", location)
        self.end_headers()


def _start_redirect_server() -> HTTPServer:
    server = HTTPServer(("0.0.0.0", PUBLIC_PORT), _RedirectHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def main() -> None:
    app_dir = os.path.dirname(os.path.abspath(__file__))
    redirect_server = _start_redirect_server()
    print(f"HubSpot callback proxy: http://localhost:{PUBLIC_PORT}/auth/hubspot/callback")
    print(f"Streamlit app: http://localhost:{STREAMLIT_PORT}/")
    print(f"Open app via proxy: http://localhost:{PUBLIC_PORT}/ (redirects to Streamlit)")

    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "streamlit_app.py",
        "--server.port",
        str(STREAMLIT_PORT),
        "--server.headless",
        "true",
    ]
    try:
        subprocess.run(cmd, cwd=app_dir, check=False)
    finally:
        redirect_server.shutdown()


if __name__ == "__main__":
    main()
