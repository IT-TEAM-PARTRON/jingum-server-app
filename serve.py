"""Production entry point used by PM2."""

import os
from pathlib import Path

from dotenv import load_dotenv
from waitress import serve


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

from app import app  # noqa: E402  (load environment before importing app)


def main():
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    print(f"Jingum server listening on http://{host}:{port}", flush=True)
    serve(app, host=host, port=port)


if __name__ == "__main__":
    main()
