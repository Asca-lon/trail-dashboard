"""pytest 설정: backend/ 를 sys.path 에 넣어 `import api`, `import models` 가
어떤 실행 방식(pytest / python -m pytest)에서도 동작하게 한다."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
