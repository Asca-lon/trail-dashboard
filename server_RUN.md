# RUN.md — 서버 실행 안내 (팀원용)

API-LXC 컨테이너에서 **대시보드와 API를 한 서버로** 띄우는 방법.
Tailscale VPN에 연결된 팀원 PC의 브라우저에서 접속한다.

---

## 1. 접속 정보

| 항목 | 값 |
|---|---|
| 컨테이너 | API-LXC (`~/trail-dashboard`) |
| 주소 | `http://100.81.215.29:8000/` |
| Tailscale IP 확인 | 컨테이너에서 `tailscale ip -4` (`100.x.y.z` 형태) |

---

## 2. 실행
윈도우 cmd 창에서
```bash
ssh root@100.81.215.29
```


컨테이너에 SSH로 접속한 뒤:

```bash
cd ~/trail-dashboard
source .venv/bin/activate
uvicorn serve:app --host 0.0.0.0 --port 8000
```

**`--host 0.0.0.0` 은 필수.** 생략하면 `127.0.0.1` 에만 바인딩돼서
Tailscale로 들어오는 요청을 받지 못한다(컨테이너 안에서만 열림).

### SSH를 끊어도 계속 띄워두려면

```bash
nohup uvicorn serve:app --host 0.0.0.0 --port 8000 > uvicorn.log 2>&1 &
```

끄기: `pkill -f "uvicorn serve:app"` · 로그: `tail -f uvicorn.log`

---

## 3. 최초 1회 설정 (컨테이너를 새로 만들었을 때만)

```bash
sudo apt update && sudo apt install -y python3 python3-venv git
cd ~/trail-dashboard
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
cp .env.example .env          # 기본값 USE_MOCK=1 로 바로 동작
```

---

## 4. 파일 설명

| 파일 | 설명 |
|---|---|
| `serve.py` | **실행 진입점.** FastAPI 한 프로세스가 프론트 + mock + API 를 모두 서빙 |
| `backend/api.py` | API 엔드포인트 (CONTRACT §5) |
| `backend/models.py` | 응답 모델 = 계약을 코드로 |
| `backend/db.py` | DB 조회 전용 (읽기 전용) |
| `frontend/dashboard.html` `dashboard.js` `style.css` | C의 대시보드 |
| `mock/*.json` | 가짜 데이터. `USE_MOCK=1` 일 때 API가 이걸 읽어 응답 |
| `.env` | 설정 (`USE_MOCK`, `DATABASE_URL`) — git에 올리지 않음 |

### `serve.py` 가 하는 일

프론트와 API가 **같은 오리진**(`:8000`)에서 서빙되므로 CORS 문제가 없다.

```
GET /                -> frontend/dashboard.html
GET /dashboard.js /style.css /assets/*
GET /mock/*.json     -> mock/*.json  (정적)
그 외               -> backend/api.py 의 API 라우트
```

---

## 5. mock 모드 ↔ DB 모드 전환

`.env` 의 한 줄만 바꾸고 서버를 재시작한다. **프론트 코드는 건드리지 않는다.**

```bash
USE_MOCK=1    # mock/*.json 으로 응답 (A의 DB 없이 동작)
USE_MOCK=0    # 실제 DB 조회 (DATABASE_URL 필요, 읽기 전용 계정)
```

두 모드 모두 같은 `models.py` 를 거쳐 **같은 계약 모양**으로 응답한다.
현재 모드는 `/health` 로 확인.

> DB 모드는 A의 집계 테이블(`station_vulnerability`, `segment_vulnerability`)이
> 채워진 뒤에 의미가 있다. 그 전까지는 `USE_MOCK=1` 로 둔다.


---

## 7. 알아둘 것

- **대시보드는 이제 mock 파일이 아니라 API를 호출한다.** `dashboard.js` 의 URL 상수 6개가
  `/alerts/active`, `/lines` 등 API 엔드포인트를 가리킨다. 화면 내용은 (mock 모드에선) 동일하다.
- **B는 DB에 쓰지 않는다.** DB 모드에서도 읽기 전용 계정으로만 접속한다 (CONTRACT §2-1).

