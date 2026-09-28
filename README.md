# 재검 진행 상황 트래킹 웹앱 — 서버 배포 안내

베트남 법인 작업자가 매일 실적(정규생산·디캡리웍·P/M선별·선별리웍·출하실적)을 입력하고,
본사·법인이 같은 화면(Summary / 보고용)을 보는 사내 웹앱입니다. 한국어/베트남어 화면 전환을 지원합니다.

## 1. 구성 (파일 5종 + static 폴더)

| 파일 | 설명 |
|---|---|
| `app.py` | 웹서버 (Python / Flask). 화면 제공 + 데이터 읽기·쓰기 API |
| `index.html` | 웹 화면 전체 (파일 1개) |
| `static/` | 이미지·엑셀 내보내기용 라이브러리 (외부 인터넷 없이 동작하도록 포함) |
| `seed_data.json` | 초기 데이터 (기존 엑셀 이력). **최초 실행 시 1회만** 자동 적재 |
| `requirements.txt` | 설치할 Python 패키지 (Flask, waitress) |
| `data.db` | **DB 파일. 최초 실행 시 자동 생성됨** (SQLite, 별도 DB 서버 설치 불필요) |

## 2. 요구 사항

- Python 3.9 이상
- 본사·베트남 법인 **양쪽 네트워크에서 접속 가능한 주소/포트** (기본 8000)
- 외부 인터넷은 필수 아님 (구글 폰트만 인터넷이 있을 때 적용되고, 없으면 PC 기본 한글 폰트로 표시됩니다)
- 로그인 기능 없음 (요청사항). 접근 제한은 사내망/VPN 범위로 부탁드립니다

## 3. 설치 및 실행

```bash
cd jingum-server-app
pip install -r requirements.txt
```

**빠른 확인용** (개발용 서버, 창을 닫으면 종료):
```bash
python app.py            # 기본 포트 8000 (다른 포트: PORT=9000 python app.py)
```

**운영 권장** (상시 구동용, Windows/Linux 공용):
```bash
waitress-serve --host=0.0.0.0 --port=8000 app:app
```

> Windows에서 `pip` / `python` 명령이 인식되지 않으면 `py -m pip install -r requirements.txt`, `py app.py` 로 실행하세요.
> (`waitress-serve`가 인식되지 않으면 `py -m waitress --host=0.0.0.0 --port=8000 app:app`)

접속: `http://서버IP:8000` (또는 서버 관리자님이 지정하는 주소)

## 4. 상시 구동 (재부팅 후 자동 시작)

- **Windows**: 작업 스케줄러 → "시스템 시작 시" 트리거로 위 waitress 명령 실행 (또는 NSSM으로 서비스 등록)
- **Linux (systemd 예시)**
  ```ini
  [Unit]
  Description=Jingum tracker
  After=network.target
  [Service]
  WorkingDirectory=/opt/jingum-server-app
  ExecStart=/usr/bin/python3 -m waitress --host=0.0.0.0 --port=8000 app:app
  Restart=always
  [Install]
  WantedBy=multi-user.target
  ```
- 방화벽에서 해당 포트(기본 8000)를 열어주세요.
- 리버스 프록시(하위 경로, 예: `/jingum/`) 뒤에 두셔도 됩니다. 화면이 상대경로(`api/…`, `static/…`)를 사용합니다.

## 5. 데이터 / 백업

- 데이터는 **`data.db` 파일 하나**에 저장됩니다. 이 파일만 정기 백업하면 됩니다 (일 1회 복사 권장).
- `seed_data.json`은 `data.db`가 **없을 때만** 1회 적재됩니다. 이미 있으면 재시작해도 건드리지 않습니다.
- 초기화가 필요하면 서버 중지 → `data.db` 삭제 → 재시작 (**입력된 데이터가 모두 삭제되니 주의**).
- 저장 구조: 표 1개 `records(collection, doc_id, data(JSON), updated_at)`.
  collection 종류: `production_normal`, `production_decap`, `pmSelection`, `sortRework`, `shipment`, `reportHistory`(일별 기록), `meta`(목표수량·비고).
- 회사 표준 DB(MySQL/MSSQL 등)로 옮기실 경우 `app.py`의 `get_conn()`과 `api_all` / `api_save` / `api_delete` 3개 함수만 바꾸면 됩니다.

## 6. API (참고)

| 경로 | 설명 |
|---|---|
| `GET /` | 웹 화면 |
| `GET /api/all` | 전체 데이터 조회 |
| `POST /api/save` | `{collection, doc_id, data}` 저장(덮어쓰기) |
| `POST /api/delete` | `{collection, doc_id}` 삭제 |

공개되는 정적 파일은 `static/` 폴더뿐이며, `data.db`·`app.py` 등은 외부에서 내려받을 수 없습니다.

## 7. 화면 갱신 방식

여러 사람이 동시에 입력해도 **20초마다 자동으로 최신 데이터를 다시 받아옵니다** (입력 중인 값은 유지됩니다).

## 8. 업데이트 방법

- `index.html`만 교체: 서버 재시작 불필요, 데이터 영향 없음.
- `app.py` 교체: 서버 재시작 필요, 데이터(`data.db`)는 그대로 유지됩니다.

## 9. 문제 해결

| 증상 | 확인 |
|---|---|
| 화면 상단에 "서버에 연결할 수 없습니다" | 서버가 꺼져 있거나 주소/포트/방화벽 문제 |
| `index.html`을 더블클릭해서 열었더니 데이터가 비어 있음 | 파일로 열면 안 되고, 반드시 `http://서버IP:포트` 주소로 접속해야 합니다 |
| 이미지·엑셀 내보내기 버튼 | 내부 파일(`static/`)만 사용하므로 인터넷이 없어도 동작합니다 |
