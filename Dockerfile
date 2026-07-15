# trail-dashboard — 백엔드 API + 정적 프론트를 한 컨테이너로.
#
# serve.py 가 FastAPI(api.app) 위에 frontend/ 와 mock/ 를 마운트하므로
# 이미지 하나로 API·화면이 같은 포트(8000)에서 뜬다.
#
# 기본은 USE_MOCK=1 — A의 DB 없이도 docker compose up 한 번에 화면까지 동작한다.
# 실제 DB 조회로 바꾸려면 USE_MOCK=0 + DATABASE_URL 을 넘긴다(docker-compose 의 db 프로파일 참고).

FROM python:3.12-slim

# 파이썬 로그가 버퍼에 갇히지 않게(컨테이너 로그로 바로 보이게)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# 의존성 먼저 복사 → 레이어 캐시. 소스만 바뀌면 pip 재설치 안 함.
#   backend/requirements.txt   : API 서버(FastAPI)용
#   requirements-pipeline.txt  : 수집기·집계용(pandas·requests·sqlalchemy·openpyxl)
# 둘 다 설치해서 이 이미지 하나로 API 도 백필도 돌린다(컨테이너에서 실행하므로
# 팀원이 호스트에 파이썬·패키지를 따로 깔 필요가 없다).
COPY backend/requirements.txt ./backend/requirements.txt
COPY requirements-pipeline.txt ./requirements-pipeline.txt
RUN pip install --no-cache-dir -r backend/requirements.txt -r requirements-pipeline.txt

# 프로젝트 전체 복사. serve.py 가 ROOT 기준으로 frontend·mock·backend 를 참조하므로
# 루트 구조를 그대로 유지해야 한다(.dockerignore 로 불필요한 것만 제외).
COPY . .

# 기본 실행 모드. compose 나 docker run -e 로 덮어쓸 수 있다.
ENV USE_MOCK=1 \
    CORS_ORIGINS=*

EXPOSE 8000

# 헬스체크: /health 가 200 이면 정상.
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health').status==200 else 1)"

# serve.py = api.app + 정적 마운트. 0.0.0.0 이라야 컨테이너 밖에서 접속된다.
CMD ["uvicorn", "serve:app", "--host", "0.0.0.0", "--port", "8000"]
