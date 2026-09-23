"""
재검 진행 상황 트래킹 - 사내 서버용 백엔드

구성:
  - Flask 웹 서버가 index.html(프런트엔드)을 그대로 서빙합니다.
  - 데이터는 MariaDB의 records 테이블에 저장됩니다.
  - 모든 레코드는 (collection, doc_id, data-JSON) 한 가지 형태로 저장됩니다.
    프런트엔드가 쓰는 "카테고리별 문서" 구조와 1:1로 대응됩니다.

실행:
  pip install -r requirements.txt
  python app.py
  (기본 포트 8000 — 아래 PORT 값 또는 환경변수 PORT로 변경 가능)

최초 실행 시 records 테이블이 비어 있고 seed_data.json이 있으면
자동으로 한 번만 불러와 채워둡니다.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

from database import get_conn

BASE_DIR = Path(__file__).resolve().parent
SEED_PATH = BASE_DIR / "seed_data.json"
STATIC_FILE = "index.html"
PORT = int(os.environ.get("PORT", 8000))

# Only index.html is served explicitly; project and configuration files stay private.
app = Flask(__name__, static_folder=None)


def seed_if_empty():
    """최초 실행 시 한 번만 seed_data.json 내용을 채워 넣습니다."""
    if not SEED_PATH.exists():
        return
    conn = get_conn()
    try:
        count = conn.execute("SELECT COUNT(*) FROM records").fetchone()[0]
        if count > 0:
            return  # 이미 데이터가 있으면 건드리지 않음
        with open(SEED_PATH, encoding="utf-8") as f:
            records = json.load(f)
        now = datetime.now(timezone.utc).isoformat()
        for rec in records:
            conn.execute(
                "INSERT OR REPLACE INTO records(collection, doc_id, data, updated_at) VALUES (?, ?, ?, ?)",
                (rec["collection"], rec["doc_id"], json.dumps(rec["data"], ensure_ascii=False), now),
            )
        conn.commit()
        print(f"[seed] {len(records)}건의 초기 데이터를 불러왔습니다.")
    finally:
        conn.close()


@app.route("/")
def index():
    return send_from_directory(str(BASE_DIR), STATIC_FILE)


@app.route("/api/all")
def api_all():
    conn = get_conn()
    try:
        rows = conn.execute("SELECT collection, doc_id, data FROM records").fetchall()
    finally:
        conn.close()

    out = {
        "production_normal": {},
        "production_decap": {},
        "pmSelection": [],
        "sortRework": [],
        "shipment": [],
        "targets": {},
        "report": {"comment": ""},
    }
    for collection, doc_id, data_json in rows:
        data = json.loads(data_json)
        if collection == "production_normal":
            out["production_normal"][doc_id] = data
        elif collection == "production_decap":
            out["production_decap"][doc_id] = data
        elif collection == "pmSelection":
            out["pmSelection"].append({**data, "id": doc_id})
        elif collection == "sortRework":
            out["sortRework"].append({**data, "id": doc_id})
        elif collection == "shipment":
            out["shipment"].append({**data, "id": doc_id})
        elif collection == "meta" and doc_id == "targets":
            out["targets"] = data
        elif collection == "meta" and doc_id == "report":
            out["report"] = data
    return jsonify(out)


@app.route("/api/save", methods=["POST"])
def api_save():
    body = request.get_json(force=True, silent=True) or {}
    collection = body.get("collection")
    doc_id = body.get("doc_id")
    data = body.get("data")
    if not collection or not doc_id or data is None:
        return jsonify({"error": "collection, doc_id, data가 모두 필요합니다."}), 400

    conn = get_conn()
    try:
        conn.execute(
            "INSERT OR REPLACE INTO records(collection, doc_id, data, updated_at) VALUES (?, ?, ?, ?)",
            (collection, doc_id, json.dumps(data, ensure_ascii=False), datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
    finally:
        conn.close()
    return jsonify({"ok": True})


@app.route("/api/delete", methods=["POST"])
def api_delete():
    body = request.get_json(force=True, silent=True) or {}
    collection = body.get("collection")
    doc_id = body.get("doc_id")
    if not collection or not doc_id:
        return jsonify({"error": "collection, doc_id가 필요합니다."}), 400

    conn = get_conn()
    try:
        conn.execute("DELETE FROM records WHERE collection = ? AND doc_id = ?", (collection, doc_id))
        conn.commit()
    finally:
        conn.close()
    return jsonify({"ok": True})


if __name__ == "__main__":
    get_conn().close()  # 테이블 생성 보장
    seed_if_empty()
    print(f"재검 진행 상황 트래킹 서버 시작 — http://0.0.0.0:{PORT} (사내망에서는 서버 IP:{PORT} 로 접속)")
    app.run(host="0.0.0.0", port=PORT, debug=False)
