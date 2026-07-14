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

## 2. 실행 - 프로젝트 루트에서

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

기본은 **mock 모드**다. A의 집계 테이블(`station_vulnerability`, `segment_vulnerability`)이 채워지기 전까지는 이대로 둔다.

DB까지 함께 띄우려면(A의 집계 준비 후):

```bash
USE_MOCK=0 docker compose --profile db up --build
```

- `--profile db` 를 붙이면 **PostgreSQL 컨테이너**가 함께 뜬다. 안 붙이면 API만 뜬다.
- 최초 기동 시 `db/init_schema.sql` 이 1회 자동 실행되어 빈 스키마가 생긴다.
  (집계 데이터를 채우는 것은 A의 collector/processor 몫이다.)
- 두 모드 모두 같은 계약(`CONTRACT.md` §5) 모양으로 응답하므로 **프론트 코드는 안 바뀐다.**

Windows PowerShell에서 환경변수를 앞에 붙이는 문법이 다르다:

```powershell
$env:USE_MOCK=0; docker compose --profile db up --build
```

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
