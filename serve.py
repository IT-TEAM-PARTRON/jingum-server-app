"""Production WSGI entry point used by PM2."""

import os

from waitress import serve

from app import app, seed_if_empty
from database import init_db


if __name__ == "__main__":
    init_db()
    seed_if_empty()
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8000))
    print(f"Jingum server listening on http://{host}:{port}", flush=True)
    serve(app, host=host, port=port, threads=8)
