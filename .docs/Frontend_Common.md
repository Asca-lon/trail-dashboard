# 프론트엔드 공통 기능

# 개요

`Frontend.md`에서 페이지 책임에 따라 분리한 프론트엔드 구현 기록입니다.

# 구현 목적

여러 페이지가 함께 사용하는 내비게이션, 사이드바, 공통 데이터 매핑 및 유지보수 기록을 관리합니다.

# 구현 내용

- 공통 사이드바와 메뉴
- 페이지 간 링크 규칙
- 공통 Mock 데이터 매핑
- 인코딩 및 공통 UI 정리

# 코드 설명

세부 구현 원리와 실행 흐름은 아래 작업 기록에서 기능별로 설명합니다.

# API

페이지에서 사용하는 API 및 Mock 데이터 계약은 아래 작업 기록의 API 항목을 따릅니다.

# Database

프론트엔드 문서 분리로 인한 Database 변경 사항은 없습니다.

# 주의사항

- 기존 기록의 내용과 작성 시점은 보존했습니다.
- 최신 상태는 각 작업 기록의 변경 이력과 Timestamp를 함께 확인합니다.

# 변경 이력

## Change Log

2026-07-10

- 대형 프론트엔드 통합 문서에서 페이지별 문서로 분리

# 다음 작업

- 새 작업 기록은 해당 페이지 문서에만 추가

# 작업 기록

# 한글 깨짐 수정 작업 요약

## 완료한 내용

- `frontend/station-detail.html`의 깨진 한글 문구를 정상 한글로 복구했습니다.
- 손상된 HTML 속성 따옴표와 닫는 태그를 정상 구조로 복구했습니다.
- `frontend/station-detail.html`과 `frontend/sidebar.js`를 BOM 없는 UTF-8로 다시 저장했습니다.
- 화면 코드 기준 한글 깨짐 패턴 검색을 수행했습니다.

## 수정한 파일

- `frontend/station-detail.html`
- `frontend/sidebar.js`
- `.docs/Frontend.md`

## 구현 이유

역 상세 화면의 `<title>`, 접근성 라벨, 메뉴 텍스트, 카드 문구가 깨져 브라우저 표시와 HTML 구조 안정성에 문제가 생길 수 있었기 때문입니다.

## 변경 사항

- 문서 제목을 `역 상세 | 기상-철도 리스크 의사결정 지원 시스템`으로 복구했습니다.
- 메뉴, 내비게이션, 지표, 차트, 테이블, 과거 사례 문구를 정상 한글로 복구했습니다.
- `aria-label` 문구를 정상 한글로 복구해 접근성을 유지했습니다.

## 테스트 방법

```bash
rg -n "\?\?\?|湲|泥|由|섏|寃|젙|쒖|곸|꽭" ./frontend -g "*.html" -g "*.js" -g "*.css"
node --check frontend/sidebar.js
```

예상 결과:

- 깨짐 패턴 검색 결과가 없어야 합니다.
- `node --check` 실행 시 오류가 없어야 합니다.

## 새롭게 배운 개념

- UTF-8 인코딩
- BOM 없는 UTF-8 저장
- 한글 깨짐 패턴 검색

## 실무에서는

실무에서는 에디터, 터미널, Git 설정의 기본 인코딩을 UTF-8로 통일하고, 저장 후에는 브라우저 표시뿐 아니라 검색 명령으로 깨진 문자열이 남지 않았는지 확인합니다.

## 개선 가능한 부분

- `.editorconfig`로 `charset = utf-8` 명시
- HTML 정적 검사 도구 도입
- 저장 전후 인코딩 검증 스크립트 추가

## 다음 작업

- 브라우저에서 `station-detail.html` 실제 표시 확인
- `.editorconfig` 추가 여부 검토

## 복습 문제

1. UTF-8 BOM이 일부 도구에서 문제를 만들 수 있는 이유는 무엇일까요?
2. 한글 깨짐을 검색할 때 `???`, `湲`, `泥` 같은 패턴을 찾는 이유는 무엇일까요?
3. HTML 문구가 깨졌을 때 접근성에도 영향이 생기는 이유는 무엇일까요?

## 오늘 배운 내용

- UTF-8
- BOM
- 인코딩 깨짐
- 접근성 라벨 복구

## Change Log

2026-07-09

- 역 상세 화면 한글 깨짐 복구
- 수정 파일 BOM 없는 UTF-8 저장 확인

## Timestamp

2026-07-09 11:20:00 (KST)
---


# 사이드바 역 상세 링크 수정 작업 요약

## 완료한 내용

- 메인 대시보드 사이드바의 `역 상세` 메뉴 링크를 실제 역 상세 페이지로 연결했습니다.
- `href="#"`로 인해 주소가 `dashboard.html#`에 머무르던 문제를 수정했습니다.
- `dashboard.html`을 BOM 없는 UTF-8로 저장했습니다.

## 수정한 파일

- `frontend/dashboard.html`
- `.docs/Frontend.md`

## 구현 이유

사이드바의 `역 상세` 메뉴가 임시 링크 `#`를 사용하고 있어 사용자가 클릭해도 페이지 이동이 발생하지 않았습니다.

## 변경 사항

- `frontend/dashboard.html`의 역 상세 링크를 `./station-detail.html`로 변경했습니다.

## 테스트 방법

```bash
python -m http.server 8765 --bind 127.0.0.1
```

브라우저에서 아래 주소로 접속합니다.

```text
http://127.0.0.1:8765/frontend/dashboard.html
```

검증 기준:

- 메뉴 버튼을 눌러 사이드바를 엽니다.
- `역 상세` 메뉴를 클릭합니다.
- 주소가 `http://127.0.0.1:8765/frontend/station-detail.html`로 이동해야 합니다.

## Change Log

2026-07-09

- 메인 대시보드 사이드바의 역 상세 메뉴 링크 수정

## Timestamp

2026-07-09 11:30:00 (KST)
---


# 전체 Mock 데이터 매핑 검수 작업 요약

# 개요

현재 존재하는 mock 데이터를 추가하지 않고, 대시보드/역 상세/구간 상세 화면에서 mock 데이터 매핑이 정상적으로 연결되어 있는지 검수했습니다.

검수 범위:

- `frontend/dashboard.js`
- `frontend/station-detail.js`
- `frontend/route-detail.js`
- `mock/` 폴더의 전체 JSON 파일
- 대시보드에서 상세 화면으로 이동하는 `station_id`, `segment_id` 참조

# 구현 목적

현재 화면에 표시되는 데이터가 mock 파일과 올바르게 연결되어 있는지 확인하기 위함입니다.

이번 작업에서는 mock 데이터를 새로 추가하지 않고, 기존 데이터와 렌더링 로직의 연결 상태만 점검했습니다.

# 구현 내용

기능 코드 변경은 없습니다.

검수한 항목:

- 모든 mock JSON 파싱 가능 여부
- 주요 JS 파일 문법 오류 여부
- checklist의 `station_id`, `segment_id` 참조 무결성
- 구간 상세 요약 mock과 상세 mock의 `segment_id` 일치 여부
- 역 상세 mock과 역 요약 mock의 연결 여부
- HTTP 서버 기준 실제 fetch 경로 응답 여부

# 코드 설명

## 왜 필요한가

mock 데이터와 화면 매핑은 여러 파일을 거쳐 동작합니다.

대시보드는 여러 mock 파일을 동시에 사용하고, 상세 화면은 URL 파라미터로 전달된 id를 기준으로 mock 데이터를 찾습니다.

따라서 JSON 형식이 맞더라도 id 참조가 깨지면 화면에는 일부 데이터가 비거나 잘못된 상세 화면으로 이동할 수 있습니다.

## 어떤 원리인가

1. `node --check`로 주요 JS 파일 문법을 검사합니다.
2. `mock/` 폴더의 JSON 파일을 모두 파싱합니다.
3. checklist의 대상 id가 실제 station/segment 목록에 존재하는지 확인합니다.
4. 구간 상세의 `segments_details.json`과 `vulnerability_segments.json`이 같은 `segment_id`를 공유하는지 확인합니다.
5. 역 상세의 `station_details.json`이 `vulnerability_stations.json`의 역과 연결되는지 확인합니다.
6. 로컬 HTTP 서버에서 실제 fetch 경로가 200으로 응답하는지 확인합니다.

# API

API 변경 사항은 없습니다.

검수한 mock 데이터:

- `GET ../mock/alerts_active.json`
- `GET ../mock/lines.json`
- `GET ../mock/checklist.json`
- `GET ../mock/heatmap.json`
- `GET ../mock/vulnerability_stations.json`
- `GET ../mock/vulnerability_segments.json`
- `GET ../mock/station_details.json`
- `GET ../mock/segments_details.json`

# Database

DB 변경 사항은 없습니다.

# 테스트 방법

1. JavaScript 문법 검사

```bash
node --check frontend/dashboard.js
node --check frontend/station-detail.js
node --check frontend/route-detail.js
```

예상 결과:

- 오류 없이 종료됩니다.

2. 전체 mock JSON 파싱 검사

검증 결과:

```text
alerts_active.json: ok
lines.json: ok
heatmap.json: ok
checklist.json: ok
vulnerability_segments.json: ok
vulnerability_stations.json: ok
segments_details.json: ok
station_details.json: ok
```

3. checklist 참조 무결성 검사

검증 결과:

```text
checklist items: 4
bad checklist refs: 0
```

4. 구간 상세 참조 무결성 검사

검증 결과:

```text
segment summaries: 6
segment details: 6
missing details: 0
missing summaries: 0
bad segment detail structures: 0
```

5. 역 상세 연결 검사

검증 결과:

```text
station summaries: 5
station detail station: 대전
station detail summary exists: true
station detail structure bad: 0
station detail coverage: daejeon:true, dongdaegu:false, gimcheon_gumi:false, suwon:false, miryang:false
```

6. HTTP 경로 검사

검증 결과:

```text
/frontend/dashboard.html=200
/frontend/dashboard.js=200
/frontend/station-detail.html?station_id=daejeon=200
/frontend/station-detail.js=200
/frontend/route-detail.html?segment_id=daejeon-gimcheon_gumi=200
/frontend/route-detail.js=200
/mock/alerts_active.json=200
/mock/lines.json=200
/mock/checklist.json=200
/mock/heatmap.json=200
/mock/vulnerability_stations.json=200
/mock/vulnerability_segments.json=200
/mock/station_details.json=200
/mock/segments_details.json=200
```

# 주의사항

전체적으로 mock 매핑은 정상입니다.

다만 역 상세 mock은 현재 `대전` 역 상세 데이터만 제공합니다.

따라서 `vulnerability_stations.json`에 있는 다른 역들은 요약 카드에는 표시되지만, 상세 차트/특보 통계/과거 사례 영역은 의도적으로 빈 상태 fallback으로 처리됩니다.

# 변경 이력

2026-07-10

- 전체 mock 데이터 매핑 검수
- JSON 파싱, JS 문법, 참조 무결성, HTTP 경로 확인
- 역 상세 상세 mock coverage 확인

# 작업 요약

## 완료한 내용

- 전체 mock JSON 파싱 검증
- 주요 JS 파일 문법 검증
- checklist id 참조 검증
- 구간 상세 `segment_id` 참조 검증
- 역 상세 `station_id`/역명 연결 검증
- 실제 HTTP fetch 경로 검증

## 수정한 파일

- `.docs/Frontend.md`

## 구현 이유

이번 요청은 새 mock 데이터를 추가하지 않고 현재 매핑 상태를 확인하는 작업이었습니다.

검수 결과를 문서화해 이후 포트폴리오와 유지보수 기록으로 남기기 위해 문서를 업데이트했습니다.

## 변경 사항

- 기능 코드 변경 없음
- mock 데이터 변경 없음
- 검수 결과 문서 추가

## 새롭게 배운 개념

- Mock Mapping Audit
- Reference Integrity Check
- Coverage Check

## 실무에서는

실무에서는 mock 데이터도 API contract처럼 관리합니다.

특히 목록 화면과 상세 화면이 id로 연결되는 경우, mock 단계에서도 id 참조 검사를 자동화하면 화면 전환 오류를 빠르게 잡을 수 있습니다.

## 개선 가능한 부분

- 역 상세 mock을 여러 역 상세 데이터 구조로 확장
- mock schema 검증 스크립트 파일 분리
- Playwright 기반 실제 화면 텍스트 검증 추가

## 다음 작업

- 역 상세 mock coverage 확장 여부 결정

## 복습 문제

1. mock JSON 파싱 검사는 어떤 종류의 오류를 잡을 수 있나요?
2. `station_id`, `segment_id` 참조 무결성이 중요한 이유는 무엇인가요?
3. mock coverage와 데이터 매핑 정상 여부는 어떻게 구분할 수 있나요?

## 오늘 배운 내용

- Mock Mapping Audit
- Reference Integrity
- Mock Coverage

## Change Log

2026-07-10

- 전체 mock 데이터 매핑 검수
- 문서 업데이트

## Timestamp

2026-07-10 10:27:41 (KST)

---


# 구간 변경 버튼 기능 작업 요약

## 완료한 내용

- 구간 상세 화면의 `구간 변경` 버튼에 클릭 기능을 추가했습니다.
- 버튼 클릭 시 구간 변경 모달이 열리도록 구현했습니다.
- 모달에서 변경할 구간을 선택할 수 있는 `select`를 추가했습니다.
- `적용하기` 클릭 시 `segment_id` 쿼리 파라미터를 갱신해 선택한 구간 상세 화면으로 이동하도록 구현했습니다.
- `ESC` 키, 닫기 버튼, 취소 버튼, 모달 바깥 클릭으로 모달을 닫을 수 있게 했습니다.

## 수정한 파일

- `frontend/route-detail.html`
- `frontend/route-detail.js`
- `frontend/style.css`
- `.docs/Frontend.md`

## 구현 이유

기존 `구간 변경` 버튼은 UI만 존재했기 때문에 사용자가 다른 철도 구간으로 이동할 수 없었습니다. 모달 기반 선택 기능을 추가해 현재 구간 상세 화면 안에서 구간 변경 흐름을 시작할 수 있도록 했습니다.

## 변경 사항

- `data-route-change-open` 버튼 속성 추가
- `route-change-modal` 모달 마크업 추가
- `route-change-form` 폼과 `label/select` 접근성 연결 추가
- `route-detail.js`에 구간 목록 렌더링, 모달 열기/닫기, 선택 구간 이동 로직 추가
- `style.css`에 모달, 폼, 버튼 반응형 스타일 추가

## 테스트 방법

```bash
node --check frontend/route-detail.js
```

로컬 서버 실행 후 아래 주소에서 확인합니다.

```text
http://127.0.0.1:8765/frontend/route-detail.html
```

검증 기준:

- `구간 변경` 버튼을 누르면 모달이 열립니다.
- 모달의 `변경할 구간` label이 select와 연결되어 있습니다.
- `취소`, 닫기 버튼, ESC 키, 바깥 영역 클릭으로 모달이 닫힙니다.
- 구간을 선택하고 `적용하기`를 누르면 URL에 `segment_id`가 반영됩니다.
- 버튼과 모달은 모바일 화면에서도 겹치지 않아야 합니다.

## 새롭게 배운 개념

- 접근 가능한 dialog 구조
- query parameter 기반 화면 상태 변경
- 모달 닫기 인터랙션
- mock 데이터 기반 select option 렌더링

## 실무에서는

실무에서는 구간 변경 모달의 목록을 mock JSON이 아니라 `/segments` 같은 API에서 받아옵니다. 또한 선택한 구간을 URL에 반영하면 새로고침이나 공유 링크에서도 같은 구간을 유지할 수 있어 운영 도구에서 유용합니다.

## 개선 가능한 부분

- 구간 검색 입력 추가
- 구간 변경 시 페이지 전체 reload 없이 DOM만 재렌더링
- 선택 구간 최근 사용 기록 저장
- 모달 focus trap 고도화

## 다음 작업

- 구간 변경 모달 브라우저 시각 검수
- 구간 검색 API 설계
- 선택 구간에 따른 모든 카드/차트 동적 갱신 검수

## 복습 문제

1. URL query parameter로 화면 상태를 관리하면 어떤 장점이 있나요?
2. 모달에서 ESC 키 닫기 기능이 필요한 이유는 무엇인가요?
3. `label`과 `select`를 연결하면 접근성 측면에서 어떤 이점이 있나요?

## 오늘 배운 내용

- Dialog UI
- Query Parameter
- Mock 데이터 select 렌더링
- 모달 닫기 이벤트 처리

## Change Log

2026-07-10

- 구간 변경 버튼 클릭 기능 추가
- 구간 변경 모달 및 선택 구간 이동 로직 추가

## Timestamp

2026-07-10 00:20:00 (KST)
---


# RAG 및 데이터 분석 메뉴 제거 작업 요약

## 완료한 내용

- 대시보드, 역 상세, 구간 상세 사이드바에서 `RAG 심층 설명` 메뉴를 제거했습니다.
- 세 페이지 사이드바에서 `데이터 분석·통계` 메뉴를 제거했습니다.
- 구간 상세 화면의 `RAG 심층 분석 보기` 버튼을 제거했습니다.
- 제거된 요소에서만 사용하던 CSS 규칙과 디자인 가이드 명세를 정리했습니다.

## 수정한 파일

- `frontend/dashboard.html`
- `frontend/station-detail.html`
- `frontend/route-detail.html`
- `frontend/style.css`
- `frontend/MAIN_DASHBOARD_DESIGN_GUIDE.md`
- `.docs/Frontend.md`

## 구현 목적

제공하지 않을 페이지의 진입점을 화면에 남겨두면 사용자가 동작하지 않는 `#` 링크를 선택하게 됩니다. 사이드바와 구간 상세의 관련 버튼을 제거해 현재 이용 가능한 기능만 노출하도록 정리했습니다.

## 구현 내용 및 실행 흐름

1. 각 HTML의 사이드바에서 두 메뉴 항목을 제거합니다.
2. 구간 상세 탭 헤더에서 RAG 분석 버튼을 제거합니다.
3. 사용처가 사라진 아이콘 modifier와 버튼 전용 CSS를 제거합니다.
4. 디자인 가이드의 메뉴 목록을 현재 구현과 일치시킵니다.

## 코드 설명

관련 요소를 숨기는 방식이 아니라 DOM에서 제거했습니다. 키보드 탐색과 스크린 리더에서도 더 이상 제공하지 않는 메뉴가 노출되지 않으며, 사용되지 않는 전용 스타일도 함께 정리됩니다.

장점:

- 동작하지 않는 링크가 사라집니다.
- 사이드바 정보 구조가 간결해집니다.
- 사용하지 않는 CSS가 줄어듭니다.

단점:

- 추후 기능을 다시 제공할 경우 메뉴 마크업과 스타일을 재구현해야 합니다.

다른 구현 방법:

기능 플래그로 메뉴를 조건부 렌더링할 수 있습니다. 현재 프로젝트는 정적 HTML 구조이고 기능 제거가 확정되어 있어 DOM과 스타일을 직접 제거하는 방식이 더 단순합니다.

## 테스트 방법

- 세 HTML에서 제거 대상 텍스트와 클래스가 검색되지 않는지 확인합니다.
- 구간 상세 탭 헤더가 RAG 버튼 없이 정상적으로 닫히는지 확인합니다.
- CSS 여는 중괄호와 닫는 중괄호 개수가 같은지 확인합니다.
- 기존 JavaScript 파일의 문법 검사를 실행합니다.

예상 결과:

- 모든 사이드바에는 대시보드, 역 상세, 구간 상세 메뉴만 표시됩니다.
- 구간 상세 화면에 `RAG 심층 분석 보기` 버튼이 표시되지 않습니다.
- 기존 사이드바 열기·닫기와 상세 탭 전환은 그대로 동작합니다.

## API

변경 없음.

## Database

변경 없음.

## 주의사항

아이콘 SVG 파일은 삭제하지 않았습니다. 다른 기능에서 재사용하거나 향후 기능을 복원할 가능성을 고려해 자산은 유지했습니다.

## 실무에서는

출시 환경별로 기능 제공 여부가 달라질 가능성이 있다면 권한 또는 feature flag 기반 메뉴 구성을 사용합니다. 기능 자체를 폐기하는 경우에는 이번 작업처럼 진입점과 사용되지 않는 스타일을 함께 제거합니다.

## 개선 가능한 부분

- 사이드바 메뉴 데이터를 공통 JavaScript 또는 템플릿으로 관리해 페이지별 마크업 중복 제거
- 사이드바 메뉴 항목을 검증하는 E2E 테스트 추가

## 다음 작업

- 로컬 브라우저에서 세 페이지의 사이드바와 구간 상세 탭 헤더 시각 검수

## 프로젝트 진행률

■■■■■■■■□□ 80%

완료:

- RAG 및 데이터 분석·통계 진입점 제거

진행 중:

- 전체 페이지 반응형 시각 검수

예정:

- 백엔드 API 연동 및 E2E 테스트

## 복습 문제

1. 사용하지 않는 메뉴를 CSS로 숨기는 것보다 DOM에서 제거하는 방식의 접근성 장점은 무엇인가요?
2. 사용처가 사라진 CSS를 함께 제거해야 하는 이유는 무엇인가요?
3. 환경별로 기능 노출 여부가 달라진다면 어떤 방식으로 메뉴를 관리하는 것이 적절할까요?

## 오늘 배운 내용

- 죽은 UI 진입점 제거
- 사용되지 않는 CSS 정리
- 정적 HTML 메뉴와 feature flag의 차이

## README 반영 여부

기존 미제공 기능의 진입점 제거이므로 README에 새로운 기능 설명은 추가하지 않습니다.

## 추천 커밋 메시지

`refactor: RAG 및 데이터 분석 메뉴 제거`

## Change Log

2026-07-10

- 모든 사이드바에서 RAG 심층 설명 메뉴 제거
- 모든 사이드바에서 데이터 분석·통계 메뉴 제거
- 구간 상세 RAG 심층 분석 버튼과 전용 CSS 제거

## Timestamp

2026-07-10 10:10:16 (KST)
---


# 공통 사이드바 데이터 기준 안내 제거

# 개요

대시보드, 역 상세, 구간 상세 화면의 공통 사이드바에서 `데이터 기준 안내` 링크를 제거했습니다.

# 구현 목적

- 현재 제공하지 않는 안내 기능을 내비게이션에서 노출하지 않습니다.
- 기능이 없는 `#` 링크로 인한 사용자 혼란을 방지합니다.
- 제거된 요소의 사용하지 않는 스타일도 함께 정리합니다.

# 구현 내용

- 세 화면의 `sidebar__standard-link` 마크업을 제거했습니다.
- 안내 링크 전용 아이콘 및 상호작용 CSS를 제거했습니다.
- 사이드바 하단 컨테이너와 닫기 버튼은 유지했습니다.

# 코드 설명

각 HTML에서 안내 링크만 제거하고 `sidebar__bottom`은 유지해 닫기 버튼이 기존처럼 사이드바 아래에 배치되도록 했습니다. CSS에서는 다른 내비게이션 링크와 함께 묶여 있던 선택자에서 안내 링크만 분리 제거했습니다.

장점은 기능 없는 링크와 불필요한 스타일이 사라진다는 점입니다. 단점은 추후 안내 기능을 다시 제공할 경우 UI와 목적지를 새로 연결해야 한다는 점입니다. 실무에서는 실제 도움말 문서나 운영 기준 페이지가 준비된 후 유효한 URL로 다시 제공합니다.

# API

변경 사항이 없습니다.

# Database

변경 사항이 없습니다.

# 주의사항

- 사이드바 닫기 버튼은 제거하지 않았습니다.
- `mock/` 폴더는 수정하지 않았습니다.

# 변경 이력

2026-07-10

- 전체 화면 사이드바의 데이터 기준 안내 제거
- 안내 링크 전용 CSS 제거

# 다음 작업

- 전체 변경사항 회귀 테스트
- README 최종 반영 여부 검토

# 작업 요약

## 완료한 내용

- 대시보드 사이드바 안내 제거
- 역 상세 사이드바 안내 제거
- 구간 상세 사이드바 안내 제거
- 사용하지 않는 스타일 정리

## 수정한 파일

- `frontend/dashboard.html`
- `frontend/station-detail.html`
- `frontend/route-detail.html`
- `frontend/style.css`
- `.docs/Frontend.md`

## 구현 이유

연결된 기능이 없는 링크를 제거해 사이드바의 정보 구조를 단순화하고 잘못된 탐색을 방지했습니다.

## 변경 사항

- 안내 링크 HTML 삭제
- 안내 아이콘 및 hover, focus 스타일 삭제
- 하단 닫기 동작 유지

## 새롭게 배운 개념

- Dead UI Removal
- Orphan CSS Cleanup
- Navigation Integrity

## 실무에서는

내비게이션 항목은 실제 접근 가능한 목적지가 준비된 경우에만 노출하고, 권한이나 배포 상태에 따라 기능 플래그로 제어하기도 합니다.

## 개선 가능한 부분

- 사이드바 HTML을 공통 컴포넌트로 통합
- 화면별 중복 마크업 제거
- 사이드바 브라우저 자동화 테스트 추가

## 다음 작업

- 전체 요구사항 통합 검증

## 프로젝트 진행률

■■■■■■■■□□ 80%

완료

- 대시보드 변경
- 역 상세 변경
- 구간 상세 변경
- 사이드바 변경

진행 중

- 전체 회귀 테스트 준비

예정

- 최종 문서 및 작업 요약 정리

## 복습 문제

1. 목적지가 없는 `href="#"` 링크가 사용자 경험에 어떤 문제를 만들 수 있을까요?
2. HTML 요소를 제거할 때 관련 CSS도 함께 확인해야 하는 이유는 무엇일까요?
3. 공통 사이드바 마크업을 컴포넌트화하면 어떤 장점이 있을까요?

## 오늘 배운 내용

- Dead UI
- CSS Cleanup
- Navigation Design

## README 반영 여부

사이드바 항목 제거는 프로젝트 실행 방법이나 구조 변경이 아니므로 README에는 별도 항목을 추가하지 않았습니다.

## 추천 Commit Message

`chore: 사이드바 데이터 기준 안내 제거`

## Change Log

2026-07-10

- 전체 화면 사이드바 데이터 기준 안내 및 전용 스타일 제거

## Timestamp

2026-07-10 15:16:47 (KST)

---


---

## Timestamp

2026-07-10 17:11:58 KST

---

# 개요

대시보드, 역 상세, 구간 상세 페이지의 사이트 헤더 크기를 `station-global-header__inner` 기준으로 통일했습니다.

# 구현 목적

페이지를 이동할 때 헤더 높이와 메뉴 아이콘 크기가 달라 발생하는 시각적 흔들림을 제거하고 공통 레이아웃의 일관성을 높입니다.

# 구현 내용

- 대시보드 헤더와 내부 영역 높이를 72px에서 64px로 변경
- 전체 페이지 메뉴 버튼을 40×40px로 통일
- 전체 페이지 메뉴 아이콘을 20×20px로 통일
- 1024px 이하에서 헤더 내부 너비를 `calc(100% - 40px)`로 통일
- 640px 이하에서 상하 12px 패딩을 적용해 최종 헤더 높이 64px 유지

# 코드 설명

대시보드의 기존 `site-header` 클래스는 유지하면서 크기 규칙만 상세 페이지의 `station-global-header`와 맞췄습니다. 기존 클래스명을 유지했기 때문에 HTML 구조나 사이드바 JavaScript를 변경하지 않고 레이아웃만 통일할 수 있습니다.

장점은 변경 범위가 CSS에 한정되어 기존 동작에 미치는 영향이 작다는 점입니다. 단점은 이름이 다른 두 헤더 클래스에 유사한 규칙이 남는다는 점입니다. 다른 구현 방법으로 공통 `global-header` 클래스를 HTML에 추가할 수 있지만 여러 페이지 마크업 변경이 필요합니다. 실무에서는 공통 컴포넌트 또는 공통 유틸리티 클래스로 헤더 규격을 한 곳에서 관리합니다.

# API

API 변경은 없습니다.

# Database

Database 변경은 없습니다.

# 주의사항

- 루트 `index.html`은 애플리케이션 사이트 헤더가 아닌 독립 API/Mock 콘솔이므로 대상에서 제외했습니다.
- 대시보드·역 상세·구간 상세의 사이드바 열기 동작은 변경하지 않았습니다.

# 변경 이력

2026-07-13

- 전체 애플리케이션 페이지 헤더를 64px 기준으로 통일
- 메뉴 버튼과 아이콘 크기 및 반응형 내부 너비 통일

# 다음 작업

- 공통 헤더 마크업 컴포넌트화 검토

# 작업 요약

## 완료한 내용

- 데스크톱과 모바일 헤더 크기 통일
- 페이지별 메뉴 버튼 및 아이콘 크기 통일
- 반응형 헤더 내부 너비 통일

## 수정한 파일

- `frontend/style.css`
- `.docs/Frontend_Common.md`

## 구현 이유

페이지 전환 시 동일한 전역 내비게이션이 같은 크기와 위치로 표시되도록 하기 위해 변경했습니다.

## 변경 사항

- 대시보드 헤더: 72px → 64px
- 대시보드 메뉴 아이콘: 32px → 20px
- 모바일 메뉴 버튼: 36px → 40px
- 모바일 메뉴 아이콘: 28px → 20px

## 새롭게 배운 개념

- 공통 헤더 규격
- 반응형 계산 높이
- 시각적 레이아웃 안정성

## 실무에서는

헤더처럼 모든 페이지가 공유하는 UI는 디자인 토큰과 공통 컴포넌트로 관리해 페이지별 CSS 차이가 발생하지 않도록 합니다.

## 개선 가능한 부분

- 헤더 높이와 아이콘 크기를 CSS 사용자 정의 속성으로 관리
- 공통 헤더 HTML 컴포넌트화
- 화면 전환 시 시각 회귀 테스트 추가

## 다음 작업

- 브라우저에서 1024px 및 640px 경계 시각 검수

## 프로젝트 진행률

■■■■■■■■■■ 100%

완료

- 전체 페이지 헤더 규격 통일
- 반응형 규칙 통일
- 문서화

진행 중

- 없음

예정

- 공통 컴포넌트화 검토

## 복습 문제

1. 전역 헤더의 높이가 페이지마다 다르면 어떤 사용자 경험 문제가 발생할까요?
2. 모바일에서 40px 버튼과 상하 12px 패딩을 사용하면 헤더 높이는 얼마일까요?
3. 기존 HTML 클래스를 유지하고 CSS만 변경한 장점은 무엇일까요?

## 오늘 배운 내용

- 전역 헤더 크기 통일
- 반응형 헤더 레이아웃
- CSS 변경 범위 최소화

## README 반영 여부

프로젝트 실행 방법이나 기능 변경이 아닌 공통 UI 크기 조정이므로 README 수정은 필요하지 않습니다.

## 추천 Commit Message

`style: 전체 페이지 사이트 헤더 크기 통일`

## Change Log

2026-07-13

- 사이트 헤더를 64px, 메뉴 버튼을 40px, 메뉴 아이콘을 20px로 통일

## Timestamp

2026-07-13 10:43:41 (KST)
