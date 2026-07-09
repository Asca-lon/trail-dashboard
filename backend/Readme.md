##테스트 도구를 실행하기 위한 방법
```
python3 -m venv .venv

source .venv/bin/activate

cd /backend

pytest
#16 passed 시 정상

uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```
