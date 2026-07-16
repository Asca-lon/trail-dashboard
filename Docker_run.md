# DOCKER_RUN.md — Docker로 실행하기 (팀원용)

`git clone` 후 **명령 한 줄**로 대시보드+API를 띄운다. Python 설치도, 가상환경도, 패키지 설치도 필요 없다 — 전부 컨테이너 안에서 처리된다.

> 서버(API-LXC)에 SSH로 접속해 uvicorn을 직접 띄우는 방법은 [`server_RUN.md`](./server_RUN.md)를 본다. 이 문서는 **자기 PC에서 Docker로** 띄우는 방법이다.

---

## 0. 준비물 (최초 1회)

| | 필요한 것 | 확인 |
|---|---|---|
| 1 | **Git** | `git --version` |
| 2 | **Docker** | `docker --version` |

Docker가 없으면 아래 "Docker 설치"로 먼저 간다. 있으면 1번(Clone)으로.

---

## Docker 설치

### Windows / macOS — Docker Desktop

1. https://www.docker.com/products/docker-desktop 에서 자기 OS용 설치 파일을 받는다.
   - Windows: **WSL2 기반**으로 설치된다. 설치 중 WSL 설치를 요구하면 그대로 진행하고, 끝나면 재부팅.
   - macOS: 칩에 맞는 것(Apple Silicon / Intel)을 받는다.
2. 설치 후 **Docker Desktop 앱을 실행한다.**
3. 작업표시줄(Windows) / 메뉴바(Mac)의 **고래 아이콘**을 확인한다.
   - 고래가 **가만히 있으면** = 준비 완료
   - 고래가 **움직이면** = 아직 시작 중, 30초~1분 기다린다

> ⚠️ **가장 흔한 실수:** Docker Desktop 앱을 켜지 않고 `docker compose up` 을 실행하면
> `cannot find the file ... dockerDesktopLinuxEngine` 같은 에러가 난다.
> 에러가 아니라 **앱이 안 켜져 있다는 뜻.** 앱을 먼저 실행하고 고래가 멈출 때까지 기다린다.

### Linux — Docker Engine

Ubuntu/Debian 기준. (배포판 기본 패키지 대신 **공식 저장소**를 쓴다 — `docker compose` v2가 함께 설치된다.)

```bash
# 1) 기존 잔재 제거
sudo apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null

# 2) 저장소 준비
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# 3) 저장소 등록 (Debian이면 'ubuntu'를 'debian'으로)
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" | \
sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 4) 설치
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 5) 기동·확인
sudo systemctl enable --now docker
sudo docker run --rm hello-world
```

`sudo` 없이 쓰려면: `sudo usermod -aG docker $USER` 후 로그아웃·재로그인.

### 설치 확인

```bash
docker --version
docker compose version    # 'compose' (하이픈 없음) = v2. 정상.
```

---

## 1. Clone

```bash
git clone https://github.com/Asca-lon/trail-dashboard.git
cd trail-dashboard
```

VS Code에서는 `Ctrl+Shift+P` → `Git: Clone` → 위 주소로도 된다.

---

## 2. 실행

```bash
docker compose up --build
```

- 첫 실행은 이미지 빌드 때문에 **몇 분** 걸린다(파이썬 이미지 다운로드 + 패키지 설치).
- `--build`는 처음 한 번, 그리고 코드가 바뀌었을 때만 필요하다. 이후엔 `docker compose up` 만.
- 로그 마지막에 `Uvicorn running on http://0.0.0.0:8000` 이 뜨면 준비 완료.

---

## 3. 접속

브라우저에서 **http://localhost:8000**

대시보드가 뜨면 성공. 터미널로도 확인할 수 있다(새 터미널 탭):

```bash
curl http://localhost:8000/health
# {"status":"ok","mode":"mock"}
```

`"mode":"mock"` 이면 지금은 mock 모드 — A의 DB 없이 가짜 데이터로 도는 정상 상태다.

---

## 4. 종료

`docker compose up` 이 떠 있는 터미널에서 **`Ctrl+C`**.

컨테이너까지 완전히 정리하려면:

```bash
docker compose down
```

---

## 5. mock 모드 ↔ DB 모드

기본은 **mock 모드**다. 가짜 데이터로 화면이 도니, 화면만 볼 거면 여기서 끝이다.

실제 데이터로 돌리려면 **DB 모드**로 가야 하고, 그러려면 데이터를 직접 수집해야 한다(아래 6번).

```bash
# DB 컨테이너까지 함께 기동
USE_MOCK=0 docker compose --profile db up --build -d
```

- `--profile db` 를 붙여야 **PostgreSQL 컨테이너**가 뜬다. 안 붙이면 API만 뜬다.
  이후 모든 compose 명령에도 붙여야 한다(`docker compose --profile db ps` 등).
  매번 치기 번거로우면 `export COMPOSE_PROFILES=db` 로 고정할 수 있다.
- 최초 기동 시 `db/init_schema.sql` + `db/seed_stations.sql` 이 자동 실행되어
  **빈 스키마와 10개 역**이 만들어진다. 데이터는 없다.
- 두 모드 모두 같은 계약(`CONTRACT.md` §5) 모양으로 응답하므로 **프론트 코드는 안 바뀐다.**

Windows PowerShell은 환경변수 문법이 다르다:

```powershell
$env:USE_MOCK=0; docker compose --profile db up --build -d
```

확인:

```bash
docker compose --profile db exec db psql -U trail -d trail -c "SELECT count(*) FROM stations;"
# → 10  (seed 정상)
curl http://localhost:8000/health
# → {"status":"ok","mode":"db"}
```

---

## 6. 실데이터 채우기 (DB 모드)

DB 모드로 띄워도 **테이블이 비어 있으면 화면은 빈 채로 나온다.** 아래 4단계를 순서대로 돌려야 한다.

### 준비 — `.env` 에 API 키

```bash
cp .env.example .env    # 또는 직접 생성
```

`.env` 에 최소 이 세 줄이 있어야 한다:

```
USE_MOCK=0
PUBLIC_DATA_API_KEY=발급받은_공공데이터포털_키
KMA_API_KEY=발급받은_기상청_API허브_키
DATABASE_URL=postgresql://trail:trail@localhost:5432/trail
```

> `.env` 는 `.gitignore` 대상이라 clone 해도 없다. 키는 각자 발급받아 넣는다.
> `DATABASE_URL` 의 host 가 `localhost` 인 이유: 호스트에서 스크립트를 직접 돌릴 때 쓰는 값이다.
> **컨테이너 안에서는 compose 가 자동으로 `db` 로 바꿔준다** — 손대지 말 것.

### ① 계획시각 CSV 생성 ← **반드시 먼저**

```bash
docker compose exec api python -u collector/excel_to_csv.py
```

`collector/*.xlsx`(KTX 시각표)를 읽어 `collector/gyeongbu_plan_total.csv` 를 만든다.

> ⚠️ **이 단계를 건너뛰면 지연이 전부 0 이 된다.**
> 지연 = 실제도착 − 계획도착 인데, 계획시각이 없으면 실제시각으로 대체되어 항상 0 이 나온다.
> CSV 는 `.gitignore` 대상(엑셀에서 재생성 가능한 파생물)이라 clone 직후엔 없다.
> 안전장치로, CSV 가 없으면 `rail_collector` 가 수집을 시작하지 않고 중단한다.

컨테이너 안에서 만든 CSV 는 **재빌드하면 사라진다.** 호스트에도 두려면:

```bash
docker compose cp api:/app/collector/gyeongbu_plan_total.csv collector/gyeongbu_plan_total.csv
```

> `docker compose exec api cat ... > ...` 같은 리다이렉트는 쓰지 말 것.
> 셸이 대상 파일을 먼저 비워서 **0바이트 파일**이 된다.

### ② 열차 실적 90일 백필

```bash
docker compose exec api sh -c 'for i in $(seq 1 90); do python -u collector/rail_collector.py --date $(date -d "-$i day" +%Y-%m-%d); done' 2>&1 | tee ~/backfill.log
```

- **5시간 안팎** 걸린다(전국 데이터를 받아 경부선 KTX 만 걸러냄).
- 첫 줄에 `🗓️ 계획시각 3,607건 로드됨` 과 `🎯 수집 대상: 경부선 10개 역` 이 떠야 정상이다.
- 중간에 끊겨도 안전하다 — 다시 돌리면 이미 받은 날짜는 갱신되고 빠진 날짜만 채워진다.
- 502 등 일시 오류는 자동 재시도한다. 재시도가 소진되면 그 날짜를 알려주니 나중에 그 날짜만 다시 돌린다.

끝난 뒤 실패한 날짜 확인:

```bash
grep -E "❌|미완성" ~/backfill.log
```

### ③ 기상 특보 90일 백필

```bash
docker compose exec api python -u collector/weather_collector.py --backfill 90
```

API 호출 **1회**로 90일치를 받으므로 몇 초면 끝난다.

### ④ 취약도 집계 ← **이걸 돌려야 화면이 바뀐다**

```bash
docker compose exec api python -u processor/vulnerability.py
```

수집기는 원시 데이터만 넣는다. **열차 지연 × 기상 특보를 엮는 건 이 단계다.**
역·구간 집계가 한 번에 돌아간다.

### 확인

```bash
docker compose --profile db exec db psql -U trail -d trail -c "
SELECT s.station_name, v.alert_type, v.alert_level, v.avg_delay, v.sample_n
FROM station_vulnerability v JOIN stations s ON s.station_code = v.station_code
ORDER BY v.avg_delay DESC NULLS LAST LIMIT 10;"
```

`avg_delay` 가 **0이 아닌 값**이면 성공. 전부 0이면 ①(계획시각 CSV)을 건너뛴 것이다.

브라우저에서 http://localhost:8000 → `Ctrl+Shift+R`

### 매일 자동 갱신 (선택)

서버에 상주시킬 경우, 위 ②③④를 하루 한 번 도는 스크립트가 있다.

```bash
chmod +x scripts/daily_update.sh
crontab -e
# 0 5 * * * /경로/trail-dashboard/scripts/daily_update.sh
```

> 05시인 이유: 철도 실적은 1일 지연으로 들어온다. 새벽에 전일자가 확정된 뒤 돌린다.
> 로그는 `logs/daily_YYYYMMDD.log` 에 남고 30일 뒤 자동 삭제된다.

---

## 자주 겪는 문제

| 증상 | 원인 · 해결 |
|---|---|
| `cannot find the file ... dockerDesktopLinuxEngine` | Docker Desktop 앱이 안 켜져 있음. 앱을 실행하고 고래가 멈출 때까지 기다린 뒤 재시도. |
| `port is already allocated` / `bind: address already in use` | 8000 포트를 다른 게 쓰는 중. 그걸 끄거나, `docker-compose.yml` 의 `"8000:8000"` 을 `"8080:8000"` 으로 바꿔 http://localhost:8080 으로 접속. |
| 화면은 뜨는데 데이터가 안 나옴 | 브라우저가 옛 파일을 캐시. **`Ctrl+Shift+R`** (강력 새로고침). |
| 코드를 고쳤는데 반영 안 됨 | `--build` 없이 띄웠을 때. `docker compose up --build` 로 다시. |
| 빌드가 느리거나 멈춤 | 첫 빌드는 원래 느리다(이미지 다운로드). 네트워크 확인하고 기다린다. |
| `docker: command not found` | Docker 미설치 또는 PATH 문제. 위 "Docker 설치" 참고. Windows면 Docker Desktop 재설치. |
| `service "db" is not running` | `--profile db` 를 빠뜨림. db 는 프로파일로 격리돼 있어 모든 compose 명령에 붙여야 한다. |
| 지연(`avg_delay`)이 전부 **0** | 계획시각 CSV 를 안 만듦. §6-① `excel_to_csv.py` 실행. |
| `❌ 계획시각 CSV 로딩 실패: No columns to parse` | CSV 가 0바이트. `docker compose exec ... > file` 리다이렉트로 만들면 이렇게 된다. `docker compose cp` 를 쓸 것. |
| 백필이 `🎯 수집 대상` 만 찍고 끝남 | API 오류(쿼터 초과·키 오류). 로그의 `resultCode` 확인. 쿼터면 다음 날 재개(중복 안 쌓임). |
| 집계가 `0행` / 화면이 빔 | ④ `vulnerability.py` 를 안 돌림. 수집만으로는 화면이 안 바뀐다. |
| `ModuleNotFoundError: requests` | 호스트에서 실행함. 의존성은 컨테이너 안에만 있다 → `docker compose exec api python ...` |

---

## 명령 요약

```bash
git clone https://github.com/Asca-lon/trail-dashboard.git
cd trail-dashboard
docker compose up --build      # 실행 (첫 실행/코드 변경 시)
docker compose up              # 재실행 (변경 없을 때)
docker compose down            # 종료·정리
# → http://localhost:8000
```

실데이터까지 채우려면(§6):

```bash
# .env 에 API 키 2개 + USE_MOCK=0 넣은 뒤
USE_MOCK=0 docker compose --profile db up --build -d
docker compose exec api python -u collector/excel_to_csv.py                  # ① 계획시각 (필수!)
docker compose exec api sh -c 'for i in $(seq 1 90); do python -u collector/rail_collector.py --date $(date -d "-$i day" +%Y-%m-%d); done'   # ② 열차 5시간
docker compose exec api python -u collector/weather_collector.py --backfill 90  # ③ 기상 수초
docker compose exec api python -u processor/vulnerability.py                 # ④ 집계
```
