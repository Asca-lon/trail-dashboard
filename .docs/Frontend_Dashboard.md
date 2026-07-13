# 메인 대시보드 프론트엔드

# 개요

`Frontend.md`에서 페이지 책임에 따라 분리한 프론트엔드 구현 기록입니다.

# 구현 목적

메인 대시보드의 화면 구성, 필터, 위험도 시각화, 우선 점검 이동 기능을 한 문서에서 관리합니다.

# 구현 내용

- 대시보드 레이아웃과 데이터 렌더링
- 요약 카드와 위험도 노선도
- 필터와 상세 페이지 이동
- 대시보드 데이터 정책

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

# 개요

기상-철도 리스크 의사결정 지원 시스템의 메인 대시보드 프론트엔드 구현 기록입니다.

# 구현 목적

Figma 디자인과 `frontend/MAIN_DASHBOARD_DESIGN_GUIDE.md`를 기준으로 메인 대시보드 상단 영역을 HTML/CSS로 구현합니다.

# 구현 내용

- Header
- Page Title Section
- Current Weather Alert Banner
- Filter Section
- Summary Cards
- Map / Heatmap Card
- Vulnerable Ranking Cards
- Priority Inspection Table
- SVG 아이콘 에셋 폴더 생성
- Mock 데이터 매핑 설계
- 현재 기상특보 배너 Mock 데이터 연결
- 노선 필터 Mock 데이터 연결
- Summary Cards Mock 데이터 연결
- Map / Heatmap Card Mock 데이터 연결
- Vulnerable Ranking Cards Mock 데이터 연결
- Priority Inspection Table Mock 데이터 연결
- 전체 대시보드 mock 데이터 연결 검수
- 메인 대시보드 오버레이 사이드바 구현
- 헤더 브랜드 텍스트 제거 및 `menu.svg` 메뉴 버튼 적용

# 코드 설명

`frontend/dashboard.html`은 HTML5 시맨틱 태그를 사용하여 페이지 구조를 정의합니다.

`frontend/style.css`는 디자인 가이드의 색상, 여백, 폰트, radius 값을 CSS 변수로 관리합니다.

`frontend/dashboard.js`는 `mock/alerts_active.json`을 불러와 최근 업데이트 시간과 현재 기상특보 배너를 동적으로 렌더링합니다.

또한 `mock/lines.json`을 불러와 노선 select 옵션을 동적으로 렌더링합니다.

Summary Cards는 `mock/alerts_active.json`, `mock/checklist.json`, `mock/vulnerability_segments.json`을 조합해 주요 위험 요약 값을 렌더링합니다.

Map / Heatmap Card는 `mock/heatmap.json`을 기준으로 역별 취약도와 구간 요약 정보를 렌더링합니다.

Vulnerable Ranking Cards는 `mock/vulnerability_segments.json`, `mock/vulnerability_stations.json`을 기준으로 취약 구간 TOP 5와 취약 역 TOP 5를 렌더링합니다.

Priority Inspection Table은 `mock/checklist.json`을 기준으로 우선 점검 대상 행을 렌더링합니다.

전체 대시보드는 현재 `mock/` 폴더의 임시 데이터로 주요 화면 영역을 렌더링합니다.

`frontend/assets/icons/`는 외부에서 받은 SVG 아이콘 파일을 모아두는 폴더입니다.

로고, 알림, 드롭다운 등 UI에서 반복 사용하는 아이콘은 이 폴더에 저장한 뒤 HTML에서 `img` 태그 또는 CSS 배경 이미지로 불러옵니다.

## 메인 사이드바 오버레이 구현 방식

### 왜 필요한가

메인 대시보드의 화면 매핑은 이미 완료되어 있으므로, 사이드바를 추가할 때 기존 콘텐츠의 위치와 너비가 변하면 안 됩니다.

따라서 사이드바는 레이아웃 흐름에 참여하지 않는 오버레이로 구현했습니다.

### 어떤 원리인가

`frontend/dashboard.html`의 헤더에는 `menu.svg`를 사용하는 메뉴 버튼만 남겼습니다.

메뉴 버튼은 `aria-controls="main-sidebar"`와 `aria-expanded`로 사이드바 상태를 스크린리더에 전달합니다.

사이드바 본문은 `<nav>` 요소로 구성하고, `frontend/style.css`에서 `position: fixed`와 `z-index`를 사용해 기존 대시보드 위에 표시합니다.

`frontend/sidebar.js`는 메뉴 버튼, 접기 버튼, `Escape` 키 입력을 감지해 사이드바 열림 상태를 제어합니다.

### 실행 흐름

1. 사용자가 헤더의 `menu.svg` 버튼을 누릅니다.
2. `sidebar.js`가 `hidden` 속성을 해제하고 `.sidebar--open` 클래스를 추가합니다.
3. 사이드바 패널이 왼쪽에서 200px 너비로 표시됩니다.
4. 기존 대시보드 콘텐츠는 오른쪽으로 밀리지 않고 그대로 유지됩니다.
5. 접기 버튼 또는 `Escape` 키를 누르면 사이드바가 닫힙니다.

### 장점

- 기존 대시보드 레이아웃을 변경하지 않습니다.
- 사이드바 구조와 데이터 렌더링 코드가 분리되어 유지보수하기 쉽습니다.
- `nav`, `button`, `aria-expanded`, `aria-current`를 사용해 접근성을 고려했습니다.
- Figma 기준의 `200px`, `176px`, `44px`, `#001B3F`, `#2563EB` 값을 CSS 토큰으로 관리합니다.

### 단점

- 현재 메뉴 항목은 실제 상세 페이지와 연결되지 않은 임시 링크입니다.
- 닫기 애니메이션은 `hidden` 속성 처리 때문에 즉시 닫히는 방식입니다.
- 모바일에서 사이드바가 화면 대부분을 덮을 수 있으므로 실제 사용성 검수가 필요합니다.

### 다른 구현 방법

| 방법 | 장점 | 단점 |
|---|---|---|
| 레이아웃 내부 고정 사이드바 | 항상 메뉴가 보여 탐색이 빠름 | 기존 대시보드가 오른쪽으로 밀림 |
| 오버레이 사이드바 | 기존 화면을 보존함 | 열림 상태에서 콘텐츠 일부를 덮음 |
| 반투명 백드롭 포함 Drawer | 닫기 동작이 명확함 | 이번 디자인 이미지와 다를 수 있음 |

### 실무에서는

실무에서는 사이드바 메뉴 항목을 정적 HTML에 직접 고정하기보다 라우팅 설정 또는 메뉴 설정 객체에서 관리하는 경우가 많습니다.

현재는 프로젝트가 Vanilla HTML/CSS/JS 구조이므로, 먼저 HTML 구조를 명확히 만들고 이후 상세 페이지가 생기면 링크만 교체하는 방식이 가장 부담이 적습니다.

## 현재 기상특보 배너 연결 방식

### 왜 필요한가

디자인 단계에서는 HTML에 직접 문구와 숫자를 적어도 충분하지만, 실제 대시보드는 데이터가 계속 바뀝니다.

현재 기상특보 배너를 mock 데이터와 연결하면 이후 백엔드 API로 전환할 때 화면 구조를 크게 바꾸지 않고 데이터 요청 URL만 교체할 수 있습니다.

### 어떤 원리인가

브라우저가 `dashboard.html`을 읽은 뒤 `dashboard.js`를 실행합니다.

`dashboard.js`는 `fetch("../mock/alerts_active.json")`로 JSON 데이터를 가져오고, 필요한 값을 계산한 뒤 `data-dashboard-*` 속성이 붙은 HTML 요소의 텍스트를 교체합니다.

### 실행 흐름

1. `dashboard.html`이 `dashboard.js`를 `defer` 방식으로 로드합니다.
2. `dashboard.js`가 `alerts_active.json`을 요청합니다.
3. `updated_at`을 화면용 날짜 형식으로 변환합니다.
4. 첫 번째 발효 특보를 기준으로 배지 문구를 만듭니다.
5. 발효 지역 수와 영향 가능 철도 구간 수를 계산합니다.
6. 데이터가 없거나 요청에 실패하면 기본 빈 상태 문구를 표시합니다.

### 장점

- 기존 HTML/CSS 디자인 구조를 거의 변경하지 않습니다.
- mock 데이터와 실제 API 전환이 쉽습니다.
- 데이터가 비어 있거나 실패할 때도 화면이 깨지지 않습니다.

### 단점

- 현재는 배너 한 영역만 연결되어 있어 다른 섹션은 아직 정적 데이터입니다.
- `fetch()`를 사용하므로 `file://` 직접 실행보다 로컬 서버 실행이 안정적입니다.
- 영향 가능 열차 수처럼 mock에 없는 데이터는 아직 계산하지 않습니다.

### 다른 구현 방법

| 방법 | 장점 | 단점 |
|---|---|---|
| HTML에 정적 데이터 유지 | 가장 단순함 | 데이터 변경에 취약함 |
| 서버에서 HTML 생성 | 초기 렌더링 흐름이 단순함 | 프론트엔드 상호작용이 늘어나면 복잡해짐 |
| React/Vue 컴포넌트 전환 | 확장성 좋음 | 현재 단계에서는 구조 변경 부담이 큼 |

### 실무에서는

실무에서는 API 응답을 그대로 DOM에 넣기보다 View Model로 변환합니다.

이번 구현도 `regionSummary`, `affectedSegmentCount`, `badgeText`처럼 화면 표시용 값으로 한 번 가공한 뒤 렌더링합니다.

## 노선 필터 연결 방식

### 왜 필요한가

노선 필터는 대시보드 전체 데이터의 기준이 되는 입력값입니다.

현재 mock에는 `경부선` 하나만 있지만, 노선이 늘어날 경우 HTML을 직접 수정하지 않아도 select 옵션이 자동으로 늘어나도록 구성했습니다.

### 어떤 원리인가

`dashboard.js`가 `fetch("../mock/lines.json")`로 노선 목록을 읽습니다.

그다음 `lines[].line` 값을 `<option>` 요소로 변환해 `#line-select` 내부를 교체합니다.

### 실행 흐름

1. `alerts_active.json`과 `lines.json`을 `Promise.all`로 함께 요청합니다.
2. `lines[]` 배열에서 노선명을 추출합니다.
3. 첫 번째 노선을 기본 선택값으로 지정합니다.
4. 노선 데이터가 비어 있거나 요청에 실패하면 `데이터 없음` 옵션을 표시하고 select를 비활성화합니다.

### 장점

- 노선 목록이 늘어나도 HTML 수정이 필요 없습니다.
- 기존 `label`과 `select` 접근성 구조를 유지합니다.
- 데이터 실패 시 사용자가 잘못된 필터를 선택하지 않도록 select를 비활성화합니다.

### 단점

- 현재는 노선 선택 변경 시 다른 영역을 다시 필터링하지 않습니다.
- mock에 노선별 상세 메타데이터가 적어 select 옵션 외에는 활용 범위가 제한적입니다.

### 다른 구현 방법

| 방법 | 장점 | 단점 |
|---|---|---|
| HTML option 직접 작성 | 가장 단순함 | 노선 변경 때마다 HTML 수정 필요 |
| JS로 mock option 생성 | 현재 구조에 적합함 | 선택 변경 이벤트를 별도로 구현해야 함 |
| API에서 필터 메타데이터 통합 제공 | 실서비스 확장에 적합함 | 백엔드 계약이 먼저 필요함 |

### 실무에서는

실무에서는 필터 옵션을 화면 데이터와 별도 API로 관리하는 경우가 많습니다.

예를 들어 `/filters` 또는 `/metadata/lines` 같은 API가 노선, 특보 종류, 열차 종류를 한 번에 내려주면 프론트엔드는 공통 필터 렌더링 로직으로 여러 select를 관리할 수 있습니다.

## Summary Cards 연결 방식

### 왜 필요한가

Summary Cards는 사용자가 대시보드에 들어왔을 때 위험 상황을 가장 먼저 요약해서 보는 영역입니다.

정적 숫자를 유지하면 mock 데이터와 화면이 서로 달라질 수 있으므로, 현재 mock 데이터에서 계산 가능한 값부터 동적으로 연결했습니다.

### 어떤 원리인가

각 카드에 `data-dashboard-summary-card` 속성을 부여하고, JavaScript가 카드별 값을 계산해 숫자, 단위, 보조 문구를 교체합니다.

### 실행 흐름

1. `alerts_active.json`, `checklist.json`, `vulnerability_segments.json`을 불러옵니다.
2. 영향 가능 구간은 `active[].affected[]` 중 `type === "segment"`인 항목 수로 계산합니다.
3. 평균 지연 시간은 `checklist.items[].avg_delay_incr` 평균으로 계산합니다.
4. 취약도 높음 구간은 `vulnerability_segments.segments[].avg_delay_incr >= 12`인 항목 수로 계산합니다.
5. 운행 지연 예상 열차는 현재 mock에 직접 필드가 없으므로 `-`로 표시합니다.

### 장점

- mock 데이터와 화면 숫자의 불일치를 줄입니다.
- API 전환 시 계산 기준만 유지하면 화면 구조를 재사용할 수 있습니다.
- mock에 없는 데이터는 억지로 추정하지 않고 `-`로 표시해 의미 왜곡을 피합니다.

### 단점

- `운행 지연 예상 열차`는 아직 실제 데이터를 표시하지 못합니다.
- 전일 대비 증감값은 현재 mock에 없어서 기준 설명으로 대체했습니다.
- 취약도 높음 기준값 `12분`은 임시 프론트엔드 상수입니다.

### 다른 구현 방법

| 방법 | 장점 | 단점 |
|---|---|---|
| 정적 숫자 유지 | 구현이 가장 단순함 | mock 데이터와 쉽게 불일치함 |
| 프론트엔드 계산 | 현재 mock으로 빠르게 구현 가능 | 기준 변경 시 프론트엔드 수정 필요 |
| 백엔드 요약 API 제공 | 실서비스에 가장 적합함 | API 계약과 백엔드 구현 필요 |

### 실무에서는

실무에서는 Summary Cards처럼 여러 데이터가 조합되는 영역은 백엔드에서 요약 API를 제공하는 경우가 많습니다.

예를 들어 `/dashboard/summary`가 영향 구간 수, 지연 예상 열차 수, 평균 지연 시간, 고위험 구간 수를 한 번에 내려주면 프론트엔드는 표시와 상태 처리에 집중할 수 있습니다.

## Map / Heatmap Card 연결 방식

### 왜 필요한가

지도/히트맵 카드는 노선의 어느 역과 구간이 위험한지 시각적으로 확인하는 영역입니다.

정적 HTML을 유지하면 mock 데이터의 역 목록이나 취약도 값이 바뀌어도 화면이 따라가지 못하므로, `heatmap.json` 기준으로 역 목록과 구간 요약을 다시 렌더링하도록 구성했습니다.

### 어떤 원리인가

`heatmap.nodes[]`는 역별 취약도 표시용으로 사용하고, `heatmap.edges[]`는 구간 요약 숫자 계산용으로 사용합니다.

취약도 등급 기준은 기존 문서 기준과 동일합니다.

| 취약도 값 | 화면 등급 |
|---:|---|
| 0.70 이상 | 높음 |
| 0.50 이상 0.70 미만 | 주의 |
| 0.50 미만 | 관심 |

### 실행 흐름

1. `mock/heatmap.json`을 불러옵니다.
2. `nodes[]`를 순회해 역명, 마커 색상, 위험도 라벨을 렌더링합니다.
3. `edges[]`를 순회해 `높음`, `주의`, `관심`, `데이터 없음` 구간 수를 계산합니다.
4. 계산한 구간 수를 우측 구간 요약 정보에 반영합니다.
5. 지도 기준 시간은 현재 `heatmap.json`에 시간 필드가 없으므로 `alerts_active.json.updated_at`을 함께 사용합니다.

### 장점

- 역 목록이 바뀌어도 HTML을 직접 수정하지 않아도 됩니다.
- 구간 요약 숫자가 mock 데이터와 일치합니다.
- 기존 지도 디자인과 반응형 레이아웃을 유지합니다.

### 단점

- 현재 지도는 실제 지리 좌표를 그리는 지도 엔진이 아니라 디자인된 노선형 UI입니다.
- `lat`, `lon` 값은 아직 화면 좌표 계산에 사용하지 않습니다.
- `heatmap.json`에 `updated_at`이 없어 기준 시간은 다른 mock의 시간을 사용합니다.

### 다른 구현 방법

| 방법 | 장점 | 단점 |
|---|---|---|
| 정적 노선 UI 유지 | 디자인 재현이 쉬움 | 데이터 변경에 취약함 |
| 현재 방식의 DOM 렌더링 | 구조 변경 없이 mock 연결 가능 | 실제 지도 좌표 표현에는 한계가 있음 |
| SVG 또는 Canvas 노선 렌더링 | 선과 역 위치 제어가 쉬움 | 구현 복잡도가 증가함 |
| 지도 라이브러리 사용 | 실제 좌표 기반 표현 가능 | 현재 대시보드 요구보다 무겁고 스타일 맞춤 비용이 큼 |

### 실무에서는

실무에서는 “노선형 위험도 지도”와 “실제 지도 기반 위험도 지도”를 구분해서 설계합니다.

운영자가 역 순서와 구간 위험도를 빠르게 보는 목적이면 현재처럼 노선형 UI가 적합하고, 지리적 위치와 주변 기상 데이터를 함께 봐야 한다면 지도 라이브러리나 GIS 연동을 검토합니다.

## Vulnerable Ranking Cards 연결 방식

### 왜 필요한가

취약 구간 TOP 5와 취약 역 TOP 5는 운영자가 가장 먼저 확인해야 할 우선순위를 보여주는 영역입니다.

정적 테이블을 유지하면 mock 데이터의 순위와 화면 순위가 달라질 수 있으므로, 취약도 기준에 따라 데이터를 정렬해 테이블 행을 다시 렌더링합니다.

### 어떤 원리인가

`vulnerability_segments.json`의 `segments[]`는 `avg_delay_incr` 기준 내림차순으로 정렬합니다.

`vulnerability_stations.json`의 `stations[]`는 `delay_rate` 기준 내림차순으로 정렬합니다.

각 행의 위험도 배지는 기존 `.risk-badge` 클래스를 재사용합니다.

### 실행 흐름

1. `mock/vulnerability_segments.json`과 `mock/vulnerability_stations.json`을 불러옵니다.
2. 취약 구간은 `avg_delay_incr` 값이 큰 순서로 정렬하고 상위 5개만 표시합니다.
3. 취약 역은 `delay_rate` 값이 큰 순서로 정렬하고 상위 5개만 표시합니다.
4. 위험도 라벨은 기존 등급 기준을 사용합니다.
5. 데이터가 비어 있으면 테이블에 안내 행을 표시합니다.

### 장점

- mock 데이터 기준으로 실제 TOP 5 순위가 표시됩니다.
- 기존 테이블 디자인과 접근성 구조를 유지합니다.
- 데이터가 5개보다 많거나 적어도 자동으로 대응할 수 있습니다.

### 단점

- 취약 역 테이블의 `지연 건수` 열은 mock에 실제 지연 건수 필드가 없어 `sample_n`을 표시합니다.
- 구간과 역의 위험도 기준이 서로 다릅니다.
- 정렬 기준이 프론트엔드에 있어 정책 변경 시 코드 수정이 필요합니다.

### 다른 구현 방법

| 방법 | 장점 | 단점 |
|---|---|---|
| HTML 정적 행 유지 | 구현이 단순함 | mock 데이터와 불일치함 |
| 프론트엔드 정렬 | 현재 mock으로 빠르게 구현 가능 | 정렬 정책이 프론트엔드에 남음 |
| 백엔드에서 정렬된 TOP 5 제공 | 실서비스에 적합함 | API 계약과 백엔드 구현 필요 |

### 실무에서는

실무에서는 TOP 5처럼 정책이 중요한 순위 데이터는 백엔드에서 정렬 기준과 함께 제공하는 편이 안전합니다.

프론트엔드는 순위 표시, 빈 상태, 로딩 상태에 집중하고, 정렬 기준 변경은 백엔드 또는 분석 레이어에서 관리하는 구조가 유지보수에 유리합니다.

## Priority Inspection Table 연결 방식

### 왜 필요한가

우선 점검 대상 테이블은 실제 운영자가 어떤 구간부터 확인해야 하는지 결정하는 영역입니다.

정적 행을 유지하면 checklist mock과 화면 내용이 달라질 수 있으므로, `mock/checklist.json`의 `items[]`를 기준으로 행을 다시 렌더링합니다.

### 어떤 원리인가

`checklist.items[]`를 `rank` 기준 오름차순으로 정렬한 뒤 테이블 행으로 변환합니다.

위험도는 `avg_delay_incr` 기준으로 계산하고, 기상특보 문구는 `reason`에서 추출합니다.

### 실행 흐름

1. `mock/checklist.json`을 불러옵니다.
2. `items[]`를 `rank` 기준으로 정렬합니다.
3. `avg_delay_incr` 값으로 위험도 배지를 계산합니다.
4. `reason`에서 `호우경보`, `폭염경보` 같은 특보 라벨을 추출합니다.
5. 위험도에 따라 대응 권고 문구를 표시합니다.
6. 데이터가 비어 있으면 안내 행을 표시합니다.

### 장점

- checklist mock과 화면의 우선순위가 일치합니다.
- 정적 테이블 행을 직접 수정하지 않아도 됩니다.
- 상세보기 버튼의 접근성 라벨을 대상별로 생성합니다.

### 단점

- `checklist.json`에 기상특보와 대응 권고 필드가 별도로 없어 일부 값은 프론트엔드에서 추론합니다.
- 상세보기 버튼은 아직 실제 상세 모달이나 페이지와 연결되지 않았습니다.
- 대응 권고 정책은 임시 문구입니다.

### 다른 구현 방법

| 방법 | 장점 | 단점 |
|---|---|---|
| HTML 정적 행 유지 | 구현이 단순함 | checklist 데이터와 불일치함 |
| 프론트엔드 추론 | 현재 mock으로 빠르게 구현 가능 | 정책 변경 시 프론트엔드 수정 필요 |
| checklist API에서 권고까지 제공 | 실서비스에 적합함 | API 필드 확장 필요 |

### 실무에서는

실무에서는 우선 점검 대상처럼 운영 판단에 영향을 주는 데이터는 API에서 위험도, 특보명, 주요 위험, 대응 권고를 명시적으로 내려주는 것이 좋습니다.

프론트엔드는 추론보다 표시와 사용자 동작 처리에 집중하는 편이 장애 대응과 감사 추적에 유리합니다.

## 전체 렌더링 검수

### 검수 목적

mock 데이터 연결 후 대시보드의 주요 데이터 렌더링 흐름이 깨지지 않는지 확인합니다.

이번 검수는 자동으로 확인 가능한 항목을 중심으로 진행했습니다.

### 검수 내용

| 검수 항목 | 결과 | 비고 |
|---|---|---|
| JavaScript 문법 검사 | 통과 | `node --check frontend/dashboard.js` |
| mock JSON 파싱 | 통과 | 전체 dashboard 사용 mock 확인 |
| 로컬 서버 접근 | 통과 | `dashboard.html`, `dashboard.js`, `style.css`, 주요 mock 파일 200 확인 |
| 렌더링 타깃 속성 확인 | 통과 | `data-dashboard-*` 속성 확인 |
| Chrome headless 스크린샷 | 제한 | 환경상 `ERR_CONNECTION_REFUSED` 페이지가 캡처되어 시각 판정에서 제외 |

### 확인된 데이터 연결

- 현재 기상특보 배너: `mock/alerts_active.json`
- 노선 필터: `mock/lines.json`
- Summary Cards: `mock/alerts_active.json`, `mock/checklist.json`, `mock/vulnerability_segments.json`
- 지도/히트맵: `mock/heatmap.json`
- 취약 구간 TOP 5: `mock/vulnerability_segments.json`
- 취약 역 TOP 5: `mock/vulnerability_stations.json`
- 우선 점검 대상: `mock/checklist.json`

### 브라우저 확인 방법

프로젝트 루트에서 로컬 서버를 실행합니다.

```bash
python -m http.server 8765 --bind 127.0.0.1
```

브라우저에서 아래 주소로 접속합니다.

```text
http://127.0.0.1:8765/frontend/dashboard.html
```

### 검수 시 주의사항

`file://`로 직접 열면 `fetch()`가 mock JSON을 읽지 못할 수 있습니다.

반드시 `http://127.0.0.1:8765/...` 형태로 접속해야 합니다.

# API

이번 작업에서는 실제 API를 직접 연결하지 않았습니다.

현재 프론트엔드는 `mock/` 폴더의 JSON 파일을 먼저 연결한 뒤, 이후 백엔드 API URL로 교체할 수 있도록 설계합니다.

향후 연결 예정 API:

- `GET /lines`
- `GET /alerts/active`
- `GET /vulnerability/segments`
- `GET /vulnerability/stations`
- `GET /heatmap`
- `GET /checklist`

## Mock 데이터 매핑

| 화면 영역 | Mock 파일 | 주요 필드 | 렌더링 내용 | 비어 있을 때 처리 |
|---|---|---|---|---|
| 노선 필터 | `mock/lines.json` | `lines[].line`, `lines[].stations` | 노선 select 옵션 | `전체` 또는 `데이터 없음` 옵션 표시 |
| 최근 업데이트 | `mock/alerts_active.json` | `updated_at` | 페이지 우측 최근 업데이트 시간 | `업데이트 정보 없음` 표시 |
| 현재 기상특보 배너 | `mock/alerts_active.json` | `active[].region_name`, `active[].alert_type`, `active[].alert_level`, `active[].affected` | 발효 중인 특보, 영향 지역, 영향 가능 대상 수 | 발효 중인 특보 없음 메시지 표시 |
| 요약 카드 - 영향 가능 구간 | `mock/alerts_active.json`, `mock/checklist.json` | `affected[type="segment"]`, `items[]` | 영향 가능 구간 수 | `0개` 표시 |
| 요약 카드 - 운행 지연 예상 열차 | 추후 API 또는 계산 데이터 필요 | 현재 mock에 직접 필드 없음 | 임시로 표시하지 않거나 기본값 사용 | `-` 표시 |
| 요약 카드 - 평균 지연 시간 | `mock/checklist.json` | `items[].avg_delay_incr` | 우선 점검 대상의 평균 지연 증가값 평균 | `-` 표시 |
| 요약 카드 - 취약도 높음 구간 | `mock/vulnerability_segments.json` | `segments[].avg_delay_incr` | 기준값 이상 구간 수 | `0개` 표시 |
| 지도/히트맵 | `mock/heatmap.json` | `nodes[].station`, `nodes[].vuln`, `edges[].from`, `edges[].to`, `edges[].vuln` | 역/구간별 취약도 상태 | 지도 영역에 데이터 없음 표시 |
| 취약 구간 TOP 5 | `mock/vulnerability_segments.json` | `segments[].from`, `segments[].to`, `segments[].avg_delay_incr`, `segments[].stop_rate` | 취약 구간 순위 테이블 | 빈 행 대신 안내 문구 표시 |
| 취약 역 TOP 5 | `mock/vulnerability_stations.json` | `stations[].station`, `stations[].avg_delay`, `stations[].delay_rate`, `stations[].delta_delay` | 취약 역 순위 테이블 | 빈 행 대신 안내 문구 표시 |
| 우선 점검 대상 | `mock/checklist.json` | `items[].rank`, `items[].target`, `items[].reason`, `items[].avg_delay_incr`, `items[].sample_n` | 우선 점검 대상 테이블 | 점검 대상 없음 표시 |
| 구간 상세보기 | `mock/segments_details.json` | `from`, `to`, `by_alert[]`, `cases[]` | 추후 상세 모달 또는 상세 페이지 | 상세 데이터 없음 표시 |
| 역 상세보기 | `mock/station_details.json` | `station`, `by_alert[]`, `cases[]` | 추후 상세 모달 또는 상세 페이지 | 상세 데이터 없음 표시 |

## 위험도 등급 기준

현재 mock 데이터에는 `높음`, `주의`, `관심` 같은 화면용 라벨이 직접 들어 있지 않은 항목이 있습니다.

따라서 프론트엔드에서는 취약도 수치 또는 지연 증가량을 기준으로 화면 라벨을 계산합니다.

| 기준 데이터 | 관심 | 주의 | 높음 |
|---|---:|---:|---:|
| `vuln` | 0.00 이상 0.50 미만 | 0.50 이상 0.70 미만 | 0.70 이상 |
| `avg_delay_incr` | 0분 이상 7분 미만 | 7분 이상 12분 미만 | 12분 이상 |
| `delay_rate` | 0.00 이상 0.25 미만 | 0.25 이상 0.40 미만 | 0.40 이상 |

이 기준은 임시 화면 렌더링 기준입니다. 실제 서비스에서는 백엔드에서 등급을 계산해 내려주거나, 별도 정책 문서로 기준값을 관리하는 방식이 더 안전합니다.

## 구현 흐름

1. `frontend/dashboard.html`에 `frontend/dashboard.js`를 연결합니다.
2. `dashboard.js`에서 mock JSON을 병렬로 불러옵니다.
3. mock 데이터를 화면 표시용 View Model로 변환합니다.
4. 기존 HTML/CSS 클래스 구조를 유지한 채 필요한 영역만 DOM 업데이트합니다.
5. 데이터가 비어 있거나 fetch 실패 시 기본 메시지를 표시합니다.

## 다른 구현 방법

| 방법 | 장점 | 단점 |
|---|---|---|
| HTML에 정적 데이터 유지 | 가장 단순함 | mock/API 전환이 어렵고 유지보수성이 낮음 |
| Vanilla JS로 mock 연결 | 현재 프로젝트 구조에 가장 적합하고 추가 설치가 필요 없음 | 상태 관리가 커지면 코드가 길어질 수 있음 |
| React/Vue 도입 | 컴포넌트화와 상태 관리에 유리 | 현재 범위에서는 라이브러리 설치와 구조 변경 부담이 큼 |
| 백엔드 API만 연결 | 실서비스 구조와 가까움 | 현재는 mock 기반 화면 검증이 먼저 필요함 |

# Database

이번 작업에서는 Database 변경이 없습니다.

# 주의사항

- 기존 루트 `index.html`은 API / Mock 콘솔로 유지합니다.
- 신규 프론트엔드 산출물은 `frontend/` 폴더에서 관리합니다.
- 현재 구현 범위는 캡쳐본에 포함된 상단 4개 섹션입니다.
- 외부 아이콘을 사용할 때는 라이선스와 출처를 확인해야 합니다.
- 빈 폴더는 Git에 저장되지 않으므로 `frontend/assets/icons/.gitkeep` 파일로 폴더를 추적합니다.
- `fetch()`로 mock JSON을 읽기 때문에 `file://`로 직접 열면 브라우저 보안 정책에 의해 `TypeError: Failed to fetch`가 발생할 수 있습니다.

## 디버깅 기록 - file:// fetch 오류

### 원인 분석

브라우저 콘솔에 `file:///C:/Users/User/trail-dashboard/frontend/dashboard.js`가 표시되면 HTML을 파일 시스템에서 직접 연 상태입니다.

이 상태에서는 브라우저가 `fetch("../mock/alerts_active.json")` 같은 로컬 파일 요청을 보안상 차단할 수 있습니다.

### 가능한 원인 우선순위

1. `dashboard.html`을 `file://` 경로로 직접 실행함
2. 로컬 서버를 켜지 않음
3. mock JSON 경로가 잘못됨
4. mock JSON 문법 오류

### 확인 방법

브라우저 주소창이 아래처럼 시작하면 문제가 발생할 수 있습니다.

```text
file:///C:/Users/User/trail-dashboard/frontend/dashboard.html
```

정상 실행은 아래처럼 `http://`로 시작해야 합니다.

```text
http://127.0.0.1:8765/frontend/dashboard.html
```

### 수정 방법

프로젝트 루트에서 로컬 정적 서버를 실행합니다.

```bash
python -m http.server 8765 --bind 127.0.0.1
```

그다음 브라우저에서 아래 주소로 접속합니다.

```text
http://127.0.0.1:8765/frontend/dashboard.html
```

### 검증

- 콘솔에 `TypeError: Failed to fetch`가 사라집니다.
- 최근 업데이트 시간이 mock 데이터 기준으로 표시됩니다.
- 현재 기상특보 배너가 `호우 경보`, `대전 외 1개 지역`, `1개`로 표시됩니다.
- 노선 필터에 `경부선`이 표시됩니다.

# 변경 이력

## Change Log

2026-07-09

- 메인 대시보드 헤더의 서비스명 텍스트 제거
- `brand__logo` 영역을 `menu.svg` 기반 메뉴 버튼으로 변경
- 메인 대시보드 왼쪽 오버레이 사이드바 추가
- 사이드바 메뉴 항목, 로고 영역, 데이터 기준 안내, 접기 버튼 구현
- 사이드바가 기존 대시보드 콘텐츠를 밀지 않도록 `position: fixed` 오버레이 구조 적용
- 사이드바 전용 `frontend/sidebar.js` 추가
- 메뉴 버튼, 접기 버튼, `Escape` 키 닫기 동작 구현
- 사이드바 디자인 토큰과 반응형 너비 처리 추가
- `node --check frontend/sidebar.js` 문법 검사 통과
- `node --check frontend/dashboard.js` 기존 대시보드 스크립트 문법 검사 통과

2026-07-08

- 메인 대시보드 상단 레이아웃 생성
- Header, Page Title, Alert Banner, Filter Section 구현
- 디자인 토큰 기반 CSS 분리
- 현재 기상특보 배너를 Figma 캡쳐본 기준의 한 줄형 컴팩트 레이아웃으로 조정
- 현재 기상특보 배너 아이콘을 triangle-alert.svg 기반 마스크 아이콘으로 변경
- 현재 기상특보 배너 아이콘을 img 기반 SVG 렌더링으로 변경
- 현재 기상특보 배너 아이콘의 원형 배경을 제거하고 SVG 자체 크기를 28px로 조정
- 요약 카드 UI를 Figma 캡쳐본과 디자인 가이드 기준으로 추가
- 요약 카드 전일 대비 증감 숫자를 추가
- 요약 카드 아이콘 배경을 붉은 원형 그라데이션으로 변경하고 SVG 아이콘을 추가
- 요약 카드별 아이콘 SVG와 배경색을 독립적으로 분리
- 취약 구간 TOP 5와 취약 역 TOP 5 랭킹 카드 구현
- 지도/히트맵 카드 구현
- 지도/히트맵 카드의 상세 정보 안내 박스 제거
- 구간 요약 정보 아이콘을 실제 이미지 렌더링 방식으로 변경
- 지도/히트맵 카드의 좁은 화면 겹침 문제를 반응형 세로 배치로 수정
- 우선 점검 대상 테이블 구현
- SVG 아이콘 관리를 위한 `frontend/assets/icons/` 폴더 생성
- 빈 아이콘 폴더 추적을 위한 `.gitkeep` 추가
- mock 데이터와 대시보드 화면 영역 매핑 설계 추가
- 위험도 등급 계산 기준 정의
- mock 데이터 연결 구현 흐름 정리
- `frontend/dashboard.js` 생성
- 현재 기상특보 배너와 최근 업데이트 시간을 `mock/alerts_active.json` 기준으로 렌더링
- 데이터 없음 및 fetch 실패 시 기본 문구 표시 처리
- `dashboard.html`에 `data-dashboard-*` 렌더링 대상 속성 추가
- 노선 필터를 `mock/lines.json` 기준으로 렌더링
- 노선 데이터 없음 및 fetch 실패 시 select 비활성화 처리
- Summary Cards를 mock 데이터 기반 계산값으로 렌더링
- mock에 없는 운행 지연 예상 열차 값은 `-`로 표시
- 지도/히트맵 카드를 `mock/heatmap.json` 기준으로 렌더링
- 역별 취약도 라벨과 구간 요약 숫자 계산 추가
- 노선 위험도 선을 mock 취약도 기준 그라데이션으로 표시
- 취약 구간 TOP 5를 `mock/vulnerability_segments.json` 기준으로 렌더링
- 취약 역 TOP 5를 `mock/vulnerability_stations.json` 기준으로 렌더링
- 랭킹 데이터가 비어 있을 때 안내 행 표시 처리
- 우선 점검 대상 테이블을 `mock/checklist.json` 기준으로 렌더링
- 점검 대상 위험도, 기상특보, 주요 위험, 대응 권고, 상세 버튼 생성
- 점검 대상 데이터가 비어 있을 때 안내 행 표시 처리
- 전체 대시보드 mock 데이터 연결 자동 검수 수행
- Chrome headless 시각 검수 제한 사항 문서화

# 다음 작업

- 실제 브라우저에서 육안 시각 검수
- 상세보기 버튼 동작 설계
- API 전환 준비

# 작업 요약

## 완료한 내용

- 메인 대시보드 오버레이 사이드바 구현
- 헤더의 서비스명 텍스트 제거
- `brand__logo`에 `menu.svg` 적용
- 메뉴 버튼 클릭 시 사이드바 열기/닫기 처리
- 접기 버튼과 `Escape` 키로 사이드바 닫기 처리
- 사이드바가 기존 콘텐츠를 밀지 않는 오버레이 구조 적용
- 사이드바 반응형 너비 처리
- 사이드바 구현 방식 문서화
- `frontend/dashboard.html` 생성
- `frontend/style.css` 생성
- 대시보드 상단 4개 섹션 구현
- Summary Cards
- Map / Heatmap Card
- Vulnerable Ranking Cards
- Priority Inspection Table 영역 구현
- SVG 아이콘 보관 폴더 생성
- mock 데이터와 화면 영역 매핑 설계
- 위험도 등급 산정 기준 정의
- 현재 기상특보 배너 mock 데이터 연결
- 최근 업데이트 시간 mock 데이터 연결
- fetch 실패 및 빈 데이터 기본 표시 처리
- 노선 필터 mock 데이터 연결
- Summary Cards mock 데이터 연결
- 지도/히트맵 mock 데이터 연결
- 취약 구간/취약 역 TOP 5 mock 데이터 연결
- 우선 점검 대상 mock 데이터 연결
- 전체 대시보드 mock 데이터 연결 검수

## 수정한 파일

- `frontend/dashboard.html`
- `frontend/style.css`
- `frontend/sidebar.js`
- `frontend/dashboard.js`
- `frontend/assets/icons/.gitkeep`
- `.docs/Frontend.md`

## 구현 이유

기존 `index.html`을 보존하면서 실제 대시보드 화면을 독립적으로 개발하기 위해 `frontend/` 폴더에 신규 파일을 생성했습니다.

외부에서 받은 SVG 아이콘을 한 곳에서 관리하기 위해 `frontend/assets/icons/` 폴더를 생성했습니다.

현재 기상특보 배너는 실시간성이 강한 영역이므로 가장 먼저 mock 데이터와 연결했습니다.

사이드바는 메인 대시보드의 기존 매핑 결과를 보존해야 하므로 콘텐츠를 밀지 않는 오버레이 방식으로 구현했습니다.

## 변경 사항

- Header의 브랜드 링크를 메뉴 버튼으로 변경
- Header에서 `기상-철도 리스크 의사결정 지원 시스템` 텍스트 제거
- `menu.svg`를 헤더 메뉴 아이콘으로 사용
- `nav.sidebar` 구조 추가
- 사이드바 로고 영역, 메뉴 리스트, 하단 데이터 기준 안내, 접기 버튼 추가
- 사이드바 색상과 크기를 CSS 변수로 관리
- `position: fixed`와 `z-index`로 기존 콘텐츠 위에 사이드바 표시
- `aria-controls`, `aria-expanded`, `aria-current`로 접근성 상태 제공
- `sidebar.js`에서 메뉴 버튼, 접기 버튼, `Escape` 키 이벤트 처리
- Figma 디자인 가이드 기반 색상 및 크기 적용
- 접근성을 위한 `label`과 `select` 연결
- 반응형 레이아웃 적용
- 아이콘 에셋 저장 위치 추가
- mock JSON 파일별 화면 사용 위치 정의
- 데이터가 없을 때의 기본 표시 정책 정의
- `mock/alerts_active.json`의 `updated_at`, `active[]`, `affected[]` 값을 화면에 반영
- `dashboard.html`에 `dashboard.js` 연결
- JavaScript가 DOM 요소를 안정적으로 찾을 수 있도록 `data-dashboard-*` 속성 추가
- `mock/lines.json`의 `lines[].line` 값을 노선 필터 option으로 렌더링
- 노선 데이터가 비어 있을 때 `데이터 없음` option과 disabled 상태 적용
- `mock/alerts_active.json` 기준 영향 가능 구간 수 계산
- `mock/checklist.json` 기준 평균 지연 시간 계산
- `mock/vulnerability_segments.json` 기준 취약도 높음 구간 수 계산
- mock에 없는 운행 지연 예상 열차는 `-`로 표시
- `mock/heatmap.json`의 `nodes[]` 기준 역별 위험도 렌더링
- `mock/heatmap.json`의 `edges[]` 기준 구간 요약 숫자 계산
- CSS 변수 `--route-risk-gradient`로 노선 위험도 선 색상 갱신
- `mock/vulnerability_segments.json`의 `segments[]`를 `avg_delay_incr` 기준으로 정렬
- `mock/vulnerability_stations.json`의 `stations[]`를 `delay_rate` 기준으로 정렬
- 랭킹 테이블 행을 mock 데이터 기반으로 교체
- `mock/checklist.json`의 `items[]`를 `rank` 기준으로 정렬
- 우선 점검 대상 테이블 행을 mock 데이터 기반으로 교체
- JavaScript 문법, mock JSON 파싱, HTTP 경로 접근 검증
- Chrome headless 스크린샷 검수 제한 사항 확인

## 테스트 방법

1. JavaScript 문법 검사

```bash
node --check frontend/dashboard.js
node --check frontend/sidebar.js
```

예상 결과: 오류 메시지가 없어야 합니다.

2. Mock JSON 파싱 검사

```bash
node -e "const fs=require('fs'); JSON.parse(fs.readFileSync('mock/alerts_active.json','utf8')); console.log('alerts_active.json OK')"
node -e "const fs=require('fs'); JSON.parse(fs.readFileSync('mock/lines.json','utf8')); console.log('lines.json OK')"
node -e "const fs=require('fs'); JSON.parse(fs.readFileSync('mock/checklist.json','utf8')); console.log('checklist.json OK')"
node -e "const fs=require('fs'); JSON.parse(fs.readFileSync('mock/vulnerability_segments.json','utf8')); console.log('vulnerability_segments.json OK')"
node -e "const fs=require('fs'); JSON.parse(fs.readFileSync('mock/vulnerability_stations.json','utf8')); console.log('vulnerability_stations.json OK')"
node -e "const fs=require('fs'); JSON.parse(fs.readFileSync('mock/heatmap.json','utf8')); console.log('heatmap.json OK')"
```

예상 결과:

- `alerts_active.json OK`
- `lines.json OK`
- `checklist.json OK`
- `vulnerability_segments.json OK`
- `vulnerability_stations.json OK`
- `heatmap.json OK`

3. 로컬 서버 경로 검사

```bash
python -m http.server 8765 --bind 127.0.0.1
```

브라우저에서 `http://127.0.0.1:8765/frontend/dashboard.html`을 열면 됩니다.

검증 기준:

- 최근 업데이트가 `mock/alerts_active.json`의 `updated_at` 기준으로 표시됩니다.
- 배지에는 첫 번째 특보인 `호우 경보`가 표시됩니다.
- 지역은 `대전 외 1개 지역`으로 표시됩니다.
- 영향 가능 철도 구간은 `1개`로 표시됩니다.
- 노선 필터에는 `경부선` option이 표시됩니다.
- Summary Cards의 영향 가능 구간은 `1개`로 표시됩니다.
- Summary Cards의 운행 지연 예상 열차는 `-편`으로 표시됩니다.
- Summary Cards의 평균 지연 시간은 `11.0분`으로 표시됩니다.
- Summary Cards의 취약도 높음 구간은 `1개`로 표시됩니다.
- 지도/히트맵 역 목록은 `서울`, `영등포`, `수원`, `천안`, `대전`, `김천(구미)`, `동대구`, `밀양`, `부산`으로 표시됩니다.
- 구간 요약은 `높음 1개`, `주의 5개`, `관심 2개`, `데이터 없음 0개`로 표시됩니다.
- 취약 구간 TOP 5는 `대전-김천(구미)`, `천안-대전`, `영등포-수원`, `동대구-밀양`, `김천(구미)-동대구` 순서로 표시됩니다.
- 취약 역 TOP 5는 `대전`, `동대구`, `김천(구미)`, `수원`, `밀양` 순서로 표시됩니다.
- 우선 점검 대상은 `대전→김천(구미) 구간`, `천안→대전 구간`, `대전역`, `영등포→수원 구간` 순서로 표시됩니다.
- 헤더에는 서비스명 텍스트 대신 `menu.svg` 아이콘 버튼만 표시됩니다.
- 메뉴 버튼을 누르면 왼쪽에서 200px 너비의 사이드바가 기존 콘텐츠 위에 표시됩니다.
- 사이드바가 열려도 대시보드 콘텐츠는 오른쪽으로 밀리지 않습니다.
- 사이드바의 접기 버튼 또는 `Escape` 키를 누르면 사이드바가 닫힙니다.
- 좁은 화면에서는 사이드바가 화면 폭을 넘지 않고 최대 `88vw` 안에서 표시됩니다.

실패 시 확인 사항:

- `file://`로 직접 열지 않았는지 확인합니다.
- 브라우저 개발자 도구 Console에 fetch 오류가 있는지 확인합니다.
- `mock/alerts_active.json` 경로와 JSON 문법을 확인합니다.
- `mock/lines.json` 경로와 JSON 문법을 확인합니다.
- `mock/checklist.json` 경로와 JSON 문법을 확인합니다.
- `mock/vulnerability_segments.json` 경로와 JSON 문법을 확인합니다.
- `mock/vulnerability_stations.json` 경로와 JSON 문법을 확인합니다.
- `mock/heatmap.json` 경로와 JSON 문법을 확인합니다.
- 주소창이 `file://`로 시작한다면 로컬 서버 주소로 다시 접속합니다.
- `frontend/sidebar.js`가 `dashboard.html`에 연결되어 있는지 확인합니다.
- 메뉴 버튼에 `data-sidebar-toggle` 속성이 있는지 확인합니다.
- 사이드바 요소에 `data-sidebar`와 `id="main-sidebar"`가 있는지 확인합니다.

## 새롭게 배운 개념

- HTML5 시맨틱 구조
- CSS 디자인 토큰
- 접근 가능한 폼 라벨
- Flexbox 반응형 레이아웃
- 정적 SVG 에셋 관리
- Mock 데이터 매핑
- View Model
- Fetch API
- DOM 렌더링
- Promise.all

## 실무에서는

실무에서는 디자인 토큰을 CSS 변수 또는 디자인 시스템으로 관리하고, API 연동 전에는 mock 데이터를 기준으로 UI 구조를 먼저 안정화합니다.

아이콘은 프로젝트 내부 에셋 폴더에 모아두고, 파일명은 `alert.svg`, `logo.svg`, `chevron-down.svg`처럼 역할이 드러나도록 관리합니다.

실무에서는 API 응답을 화면에 바로 넣기보다 View Model로 한 번 변환합니다. 이렇게 하면 API 필드명이 바뀌거나 데이터 구조가 변경되어도 화면 코드를 전부 수정하지 않아도 됩니다.

실무에서는 fetch 실패, 빈 배열, null 값을 항상 정상 상태 중 하나로 보고 UI가 무너지지 않도록 빈 상태를 설계합니다.

여러 mock 또는 API가 동시에 필요할 때는 `Promise.all`로 병렬 요청을 처리해 초기 렌더링 시간을 줄입니다.

## 개선 가능한 부분

- 실제 폰트 파일 또는 CDN 연결
- API 데이터 기반 동적 렌더링
- 브라우저 시각 회귀 테스트
- SVG 아이콘 라이선스 출처 문서화
- 위험도 등급 기준을 백엔드 또는 별도 정책 파일로 이동
- 날짜 포맷 유틸 함수를 공통 모듈로 분리
- 여러 mock 파일을 병렬로 불러오는 데이터 로더 구성
- Summary 전용 mock 또는 API 계약 추가
- 실제 좌표 기반 지도 또는 SVG 노선 렌더링 검토
- 랭킹 정렬 기준을 백엔드 또는 정책 파일로 이동
- checklist mock에 기상특보명과 대응 권고 필드를 명시적으로 추가
- Playwright 같은 브라우저 자동화 도구를 도입해 콘솔 오류와 시각 회귀 테스트 자동화

## 다음 작업

- 실제 브라우저에서 사이드바 열림/닫힘 시각 검수
- 사이드바 메뉴 항목별 상세 페이지 또는 라우팅 설계
- 상세보기 버튼 동작 설계
- 실제 API 전환 계획 수립

## 복습 문제

1. 오버레이 사이드바에 `position: fixed`를 사용하면 기존 레이아웃에 어떤 영향을 주나요?
2. `aria-expanded`는 메뉴 버튼 접근성에서 어떤 역할을 하나요?
3. 사이드바 메뉴를 `<nav>` 요소로 감싸는 이유는 무엇인가요?
4. `label`의 `for` 속성과 `select`의 `id`를 연결하는 이유는 무엇인가요?
5. 색상을 CSS 변수로 관리하면 유지보수에 어떤 장점이 있나요?
6. Flexbox가 이번 필터 영역 구현에 적합한 이유는 무엇인가요?
7. 빈 폴더를 Git에 남기기 위해 `.gitkeep`을 사용하는 이유는 무엇인가요?
8. API 응답 데이터를 View Model로 변환하면 어떤 장점이 있나요?
9. `fetch()`를 사용할 때 `file://` 실행보다 로컬 서버 실행이 안정적인 이유는 무엇인가요?
10. `Promise.all`로 여러 데이터를 동시에 요청하면 어떤 장점과 주의점이 있나요?
11. mock에 없는 데이터를 화면에 표시해야 할 때 `-`로 표시하는 방식의 장단점은 무엇인가요?
12. 노선형 위험도 지도와 실제 지도 기반 위험도 지도의 차이는 무엇인가요?
13. TOP 5 랭킹의 정렬 기준을 프론트엔드에 둘 때와 백엔드에 둘 때의 차이는 무엇인가요?
14. 운영 판단에 영향을 주는 대응 권고를 프론트엔드에서 추론하면 어떤 위험이 있나요?
15. 브라우저 자동화 도구로 시각 검수를 자동화하면 어떤 장점이 있나요?

## 오늘 배운 내용

- 시맨틱 HTML
- CSS 변수
- Flexbox
- 접근성 라벨
- SVG 아이콘 에셋 관리
- `.gitkeep`
- Mock 데이터 매핑
- View Model
- Fetch API
- DOM 렌더링
- 빈 상태 처리
- Promise.all
- 브라우저 로컬 파일 보안 정책
- file://와 http:// 실행 차이
- Summary 데이터 계산
- Heatmap 데이터 렌더링
- 취약도 등급 계산
- Ranking 데이터 정렬
- Checklist 데이터 렌더링
- 렌더링 검수
- Headless 브라우저 검수 한계
- 오버레이 사이드바
- aria-expanded
- aria-current
- Escape 키 닫기 인터랙션

## Timestamp

2026-07-09 09:33:57 (KST)


















---


# 우선 점검 대상 구간 상세 이동 작업 요약

# 개요

대시보드의 `우선 점검 대상` 테이블에서 구간 대상도 구간 상세 화면으로 이동할 수 있게 연결했습니다.

기존에는 역 대상만 역 상세 화면으로 연결되었고, 이번 작업으로 `segment` 타입 대상도 `route-detail.html?segment_id=...` 형식으로 이동합니다.

# 구현 목적

우선 점검 대상에는 역 대상과 구간 대상이 함께 포함됩니다.

역 대상은 역 상세 화면으로, 구간 대상은 구간 상세 화면으로 이동해야 운영자가 대상 유형에 맞는 상세 정보를 확인할 수 있습니다.

# 구현 내용

- `frontend/dashboard.js`
  - `createRouteDetailLink()` 추가
  - 우선 점검 대상의 `target_type === "segment"` 항목을 구간 상세 링크로 렌더링
  - 상세 패널의 `대상` 값도 구간 대상이면 구간 상세 링크로 렌더링
  - 기존 역 대상 링크 동작 유지

# 코드 설명

## 왜 필요한가

`checklist.json`의 우선 점검 대상은 `target_type`으로 역과 구간을 구분합니다.

이 타입을 기준으로 상세 이동 경로를 나누면 사용자가 올바른 상세 화면으로 이동할 수 있습니다.

## 어떤 원리인가

1. item의 `target_type`을 확인합니다.
2. `station`이면 `station-detail.html?station_id=...` 링크를 만듭니다.
3. `segment`이면 `route-detail.html?segment_id=...` 링크를 만듭니다.
4. 테이블 target 셀과 상세 패널 target 값에 같은 링크 생성 함수를 사용합니다.

## 장점

- 우선 점검 대상의 모든 주요 target type이 상세 화면으로 연결됩니다.
- 역/구간 링크 로직이 명확히 분리됩니다.
- 기존 `inspection-link` 스타일을 재사용합니다.
- 표와 상세 패널의 이동 경로가 일관됩니다.

## 단점

- 구간 상세 mock은 아직 모든 segment id별 상세 데이터를 충분히 갖고 있지 않습니다.
- `route-detail.html`은 segment id를 받지만, 상세 mock 구조는 아직 단일 구간 중심입니다.

## 다른 구현 방법

- API에서 `detail_url`을 직접 내려주는 방식
- target type별 route map 객체를 만드는 방식
- row 전체 클릭으로 이동하게 만드는 방식
- 상세 패널에 별도 “상세 화면으로 이동” 버튼을 두는 방식

# API

API 변경 사항은 없습니다.

사용한 mock 데이터:

- `GET ../mock/checklist.json`

# Database

DB 변경 사항은 없습니다.

실제 DB에서는 checklist target이 다음 중 하나를 참조하는 구조가 적합합니다.

- `station_id`
- `segment_id`

# 테스트 방법

1. JavaScript 문법 검사

```bash
node --check frontend/dashboard.js
```

예상 결과:

- 오류 없이 종료됩니다.

2. checklist target별 URL 확인

```bash
node -e "const fs=require('fs'); const checklist=JSON.parse(fs.readFileSync('mock/checklist.json','utf8')).items; console.log(checklist.map((item)=>{ const href=item.target_type==='segment' ? './route-detail.html?'+new URLSearchParams({segment_id:item.segment_id}).toString() : item.target_type==='station' ? './station-detail.html?'+new URLSearchParams({station_id:item.station_id}).toString() : '-'; return item.target+' => '+href; }).join('\n'));"
```

예상 결과:

```text
대전→김천(구미) 구간 => ./route-detail.html?segment_id=daejeon-gimcheon_gumi
천안→대전 구간 => ./route-detail.html?segment_id=cheonan-daejeon
대전역 => ./station-detail.html?station_id=daejeon
영등포→수원 구간 => ./route-detail.html?segment_id=yeongdeungpo-suwon
```

3. 브라우저 확인

```text
http://127.0.0.1:8765/frontend/dashboard.html
```

검증 기준:

- 우선 점검 대상의 구간 대상이 링크로 표시됩니다.
- `대전→김천(구미) 구간`을 클릭하면 구간 상세 화면으로 이동합니다.
- `대전역`은 기존처럼 역 상세 화면으로 이동합니다.
- 상세 패널의 `대상` 값도 동일하게 상세 화면 링크로 표시됩니다.

# 주의사항

현재 구간 상세 mock은 모든 구간별 상세 데이터를 완전히 제공하지 않습니다.

따라서 다음 단계에서 `segments_details.json`을 segment id별 구조로 확장하는 것이 좋습니다.

# 변경 이력

2026-07-09

- 우선 점검 대상 구간 target 상세 링크 추가
- 상세 패널 target 링크 구간 타입 지원
- 기존 역 target 상세 링크 유지

# 다음 작업

- `segments_details.json`을 segment id별 구조로 확장
- 구간 상세 화면에서 여러 segment id별 상세 데이터 표시

# 작업 요약

## 완료한 내용

- 우선 점검 대상 구간 링크 연결
- 표와 상세 패널 target 링크 통일
- station/segment target type별 라우팅 분기
- 테스트 및 문서화

## 수정한 파일

- `frontend/dashboard.js`
- `.docs/Frontend.md`

## 구현 이유

우선 점검 대상의 구간 항목도 상세 분석으로 이어져야 실제 운영 흐름이 완성됩니다.

## 변경 사항

- `createRouteDetailLink()` 추가
- segment target의 링크 렌더링 추가
- 상세 패널 대상 값 segment 링크 처리

## 새롭게 배운 개념

- Target Type Routing
- Shared Link Renderer
- Segment Detail Navigation

## 실무에서는

실무에서는 target type별로 이동 URL을 프론트에서 직접 조립하기보다, route helper 또는 API의 `detail_url` 정책을 만들어 일관되게 관리합니다.

## 개선 가능한 부분

- segment id별 상세 mock 확장
- route helper 객체화
- 상세 패널에 명시적인 이동 버튼 추가

## 다음 작업

- `segments_details.json`을 segment id별 구조로 확장

## 복습 문제

1. `target_type`에 따라 상세 화면을 다르게 연결해야 하는 이유는 무엇인가요?
2. 표와 상세 패널이 같은 링크 생성 함수를 쓰면 어떤 장점이 있나요?
3. 구간 상세 mock을 segment id별로 확장해야 하는 이유는 무엇인가요?

## 오늘 배운 내용

- Target Type Routing
- Segment Detail Link
- Shared Renderer

## Change Log

2026-07-09

- 우선 점검 대상 구간 상세 이동 연결
- 문서 업데이트

## Timestamp

2026-07-09 16:04:33 (KST)

---


# 대시보드 취약 구간 상세 이동 작업 요약

# 개요

대시보드의 `취약 구간 TOP 5` 랭킹에서 구간명을 클릭하면 구간 상세 화면으로 이동하도록 연결했습니다.

이동 시 `segment_id` query string을 전달합니다.

예시:

```text
route-detail.html?segment_id=daejeon-gimcheon_gumi
```

# 구현 목적

대시보드에서 위험도가 높은 구간을 발견한 뒤, 사용자가 바로 해당 구간의 상세 지표와 특보별 분석, 과거 사례를 확인할 수 있게 하기 위함입니다.

# 구현 내용

- `frontend/dashboard.js`
  - `ROUTE_DETAIL_URL` 추가
  - `SEGMENT_ID_QUERY_PARAM` 추가
  - `createSegmentDetailUrl()` 추가
  - `createSegmentLinkCell()` 추가
  - 취약 구간 랭킹의 구간명 셀을 링크로 변경

- `frontend/dashboard.html`
  - 사이드바의 구간 상세 링크를 기본 `segment_id` 포함 URL로 변경

# 코드 설명

## 왜 필요한가

대시보드는 전체 위험 현황을 보여주는 화면이고, 구간 상세는 특정 구간을 깊게 분석하는 화면입니다.

두 화면이 연결되어야 사용자가 대시보드에서 발견한 위험 구간을 바로 분석할 수 있습니다.

## 어떤 원리인가

1. `vulnerability_segments.json`의 `segment_id`를 사용합니다.
2. 취약 구간 랭킹 row를 만들 때 구간명 셀을 `a` 태그로 생성합니다.
3. 링크는 `route-detail.html?segment_id=...` 형식으로 생성합니다.
4. 구간 상세 화면은 `segment_id` query를 읽어 해당 구간 mock 데이터를 렌더링합니다.

## 장점

- 대시보드와 구간 상세 화면의 사용자 흐름이 연결됩니다.
- 표시 문자열이 아니라 `segment_id`로 이동합니다.
- 링크이기 때문에 새 탭 열기, 주소 복사, 키보드 접근성이 자연스럽습니다.

## 단점

- 아직 우선 점검 대상의 구간 대상은 링크로 연결하지 않았습니다.
- 구간 상세 화면은 현재 첫 번째 mock 구간 중심으로 상세 데이터가 구성되어 있습니다.

## 다른 구현 방법

- 랭킹 row 전체를 클릭 가능하게 만들기
- `segment-detail.html`처럼 별도 파일명을 사용하는 방식
- 프론트엔드 라우터를 도입해 `/segments/{segment_id}` 형태로 이동
- API가 상세 URL을 직접 내려주는 방식

# API

API 변경 사항은 없습니다.

사용한 mock 데이터:

- `GET ../mock/vulnerability_segments.json`

# Database

DB 변경 사항은 없습니다.

실제 DB에서는 `segment_id`를 구간 상세 조회 key로 사용하는 것이 적합합니다.

# 테스트 방법

1. JavaScript 문법 검사

```bash
node --check frontend/dashboard.js
```

예상 결과:

- 오류 없이 종료됩니다.

2. URL 생성 확인

```bash
node -e "const params=new URLSearchParams({segment_id:'daejeon-gimcheon_gumi'}); console.log('./route-detail.html?'+params.toString());"
```

예상 결과:

```text
./route-detail.html?segment_id=daejeon-gimcheon_gumi
```

3. 취약 구간 랭킹 링크 기대값 확인

```bash
node -e "const fs=require('fs'); const data=JSON.parse(fs.readFileSync('mock/vulnerability_segments.json','utf8')); console.log(data.segments.slice().sort((a,b)=>b.avg_delay_incr-a.avg_delay_incr).slice(0,3).map((segment)=>segment.from+'-'+segment.to+' => ./route-detail.html?'+new URLSearchParams({segment_id:segment.segment_id}).toString()).join('\n'));"
```

예상 결과:

```text
대전-김천(구미) => ./route-detail.html?segment_id=daejeon-gimcheon_gumi
천안-대전 => ./route-detail.html?segment_id=cheonan-daejeon
영등포-수원 => ./route-detail.html?segment_id=yeongdeungpo-suwon
```

4. 브라우저 확인

```text
http://127.0.0.1:8765/frontend/dashboard.html
```

검증 기준:

- 취약 구간 TOP 5의 구간명이 링크처럼 동작합니다.
- `대전-김천(구미)`를 클릭하면 구간 상세 화면으로 이동합니다.
- 이동 URL은 `segment_id=daejeon-gimcheon_gumi`를 포함합니다.
- 구간 상세 화면은 해당 구간 기준으로 렌더링됩니다.

# 주의사항

현재 구간 상세 mock은 `daejeon-gimcheon_gumi` 중심입니다.

다른 구간까지 완전한 상세 데이터를 보여주려면 `segments_details.json`을 segment id별 구조로 확장해야 합니다.

# 변경 이력

2026-07-09

- 취약 구간 랭킹 구간명 링크 추가
- 구간 상세 URL에 `segment_id` 전달
- 사이드바 구간 상세 링크 기본 id 포함

# 다음 작업

- 우선 점검 대상의 구간 대상도 구간 상세 화면으로 연결
- `segments_details.json`을 segment id별 구조로 확장

# 작업 요약

## 완료한 내용

- 취약 구간 TOP 5 상세 이동 구현
- segment id 기반 URL 생성
- 사이드바 구간 상세 링크 보강
- 테스트 및 문서화

## 수정한 파일

- `frontend/dashboard.html`
- `frontend/dashboard.js`
- `.docs/Frontend.md`

## 구현 이유

대시보드에서 특정 구간의 위험을 확인한 뒤 바로 상세 분석 화면으로 이동할 수 있어야 사용자 흐름이 완성됩니다.

## 변경 사항

- `ROUTE_DETAIL_URL` 추가
- `SEGMENT_ID_QUERY_PARAM` 추가
- `createSegmentDetailUrl()` 추가
- `createSegmentLinkCell()` 추가

## 새롭게 배운 개념

- Segment Detail Navigation
- Query-based Routing
- Dashboard to Detail Flow

## 실무에서는

실무에서는 목록 화면의 각 row가 상세 화면으로 이동할 때 내부 id를 사용합니다.

표시명은 바뀔 수 있지만 id는 유지되기 때문에 링크 안정성이 높아집니다.

## 개선 가능한 부분

- 우선 점검 대상 구간 링크 연결
- 구간 상세 mock을 segment id별로 확장
- 구간 상세 breadcrumb에 선택 구간 표시

## 다음 작업

- 우선 점검 대상의 구간 대상도 구간 상세 화면으로 연결

## 복습 문제

1. 구간명 대신 `segment_id`로 상세 화면에 이동하는 이유는 무엇인가요?
2. 링크를 버튼 대신 사용한 이유는 무엇인가요?
3. 다른 구간 상세를 완전히 지원하려면 mock 구조를 어떻게 바꿔야 할까요?

## 오늘 배운 내용

- Segment Detail Link
- Query-based Routing
- Dashboard Flow

## Change Log

2026-07-09

- 대시보드 취약 구간 상세 이동 연결
- 문서 업데이트

## Timestamp

2026-07-09 16:01:50 (KST)

---


# Checklist Mock 대상 타입 구조화 작업 요약

# 개요

`mock/checklist.json`의 우선 점검 대상 항목에 `target_type`, `station_id`, `segment_id`를 추가했습니다.

기존에는 `대전역`이라는 문자열을 보고 역 대상인지 추론했지만, 이제는 구조화된 필드를 우선 사용해 역 상세 링크를 생성합니다.

# 구현 목적

문자열 파싱에 의존하면 데이터 형식이 조금만 바뀌어도 링크 연결이 깨질 수 있습니다.

실무에서는 화면에 보이는 이름과 시스템이 사용하는 식별자를 분리하므로, mock 단계에서도 이 구조를 먼저 반영했습니다.

# 구현 내용

- `mock/checklist.json`
  - 구간 대상에 `target_type: "segment"` 추가
  - 구간 대상에 `segment_id` 추가
  - 역 대상에 `target_type: "station"` 추가
  - 역 대상에 `station_id` 추가

- `frontend/dashboard.js`
  - `STATION_NAME_BY_ID` 추가
  - `getStationNameFromInspectionItem()` 추가
  - 우선 점검 대상 링크 판별 시 `target_type`, `station_id`를 우선 사용
  - 기존 문자열 판별은 fallback으로 유지

# 코드 설명

## 왜 필요한가

`target: "대전역"`처럼 화면 표시용 문자열만 있으면 프론트엔드는 이 값이 역인지 구간인지 추론해야 합니다.

이 방식은 빠르게 구현할 수 있지만, 유지보수성이 낮습니다.

`target_type`과 id를 분리하면 프론트엔드는 명확한 계약에 따라 링크와 화면 표시를 결정할 수 있습니다.

## 어떤 원리인가

1. checklist item에 `target_type`을 추가합니다.
2. `target_type`이 `station`이면 `station_id`를 읽습니다.
3. `station_id`를 `STATION_NAME_BY_ID`로 역명에 매핑합니다.
4. 역명이 mock 역 목록에 있으면 역 상세 링크를 생성합니다.
5. `target_type`이 없거나 station id를 찾지 못하면 기존 문자열 판별 로직을 fallback으로 사용합니다.

## 장점

- 문자열 형식 변화에 덜 취약합니다.
- 역 대상과 구간 대상을 명확히 구분할 수 있습니다.
- 이후 구간 상세 화면을 붙일 때 `segment_id`를 바로 활용할 수 있습니다.
- mock 데이터가 실제 API 계약에 가까워집니다.

## 단점

- mock 데이터 필드가 늘어납니다.
- `station_id`와 실제 역명 매핑을 별도로 관리해야 합니다.
- 현재는 `STATION_NAME_BY_ID`가 프론트엔드 코드에 있어, 장기적으로는 mock/API에서 역 메타데이터로 내려주는 편이 좋습니다.

## 다른 구현 방법

- checklist item에 `detail_url`을 직접 넣는 방식
- station mock에 `id` 필드를 추가하고 id 기준으로 join하는 방식
- 모든 대상 정보를 `targets.json` 같은 별도 mock으로 분리하는 방식
- 프론트엔드 라우터를 도입해 id 기반 route로 이동하는 방식

# API

API 변경 사항은 없습니다.

변경된 mock 필드:

```json
{
  "target_type": "station",
  "station_id": "daejeon"
}
```

```json
{
  "target_type": "segment",
  "segment_id": "daejeon-gimcheon_gumi"
}
```

# Database

DB 변경 사항은 없습니다.

다만 실제 DB를 설계한다면 우선 점검 대상 테이블에 다음 필드가 필요합니다.

- `target_type`
- `target_id`
- `station_id`
- `segment_id`

# 테스트 방법

1. JavaScript 문법 검사

```bash
node --check frontend/dashboard.js
```

예상 결과:

- 오류 없이 종료됩니다.

2. checklist JSON 파싱 검사

```bash
node -e "const fs=require('fs'); JSON.parse(fs.readFileSync('mock/checklist.json','utf8')); console.log('checklist json OK');"
```

예상 결과:

```text
checklist json OK
```

3. 구조화 필드 기반 링크 확인

```bash
node -e "const fs=require('fs'); const checklist=JSON.parse(fs.readFileSync('mock/checklist.json','utf8')); const nameById={daejeon:'대전',dongdaegu:'동대구',gimcheon_gumi:'김천(구미)',suwon:'수원',miryang:'밀양'}; const result=checklist.items.map((item)=>{ const station=item.target_type==='station' ? nameById[item.station_id] : null; const href=station ? './station-detail.html?'+new URLSearchParams({station}).toString() : '-'; return [item.rank,item.target_type,item.station_id||item.segment_id,item.target,href].join(' | '); }); console.log(result.join('\n'));"
```

예상 결과:

```text
1 | segment | daejeon-gimcheon_gumi | 대전→김천(구미) 구간 | -
2 | segment | cheonan-daejeon | 천안→대전 구간 | -
3 | station | daejeon | 대전역 | ./station-detail.html?station=%EB%8C%80%EC%A0%84
4 | segment | yeongdeungpo-suwon | 영등포→수원 구간 | -
```

4. 브라우저 확인

```text
http://127.0.0.1:8765/frontend/dashboard.html
```

검증 기준:

- 대시보드가 정상 로드됩니다.
- 우선 점검 대상의 `대전역`은 역 상세 링크로 표시됩니다.
- 구간 대상은 일반 텍스트로 유지됩니다.
- checklist mock은 HTTP 200으로 로드됩니다.

# 주의사항

현재 `station_id`와 역명 매핑은 `dashboard.js`의 `STATION_NAME_BY_ID`에 있습니다.

장기적으로는 `vulnerability_stations.json`에도 `station_id`를 추가해 mock끼리 같은 id로 join하는 구조가 더 좋습니다.

# 변경 이력

2026-07-09

- checklist mock에 `target_type`, `station_id`, `segment_id` 추가
- dashboard 링크 판별 로직을 구조화 필드 우선 방식으로 변경
- 문자열 기반 판별은 fallback으로 유지

# 다음 작업

- `vulnerability_stations.json`에 `station_id` 추가
- `vulnerability_segments.json`에 `segment_id` 추가
- 구간 상세 화면 설계

# 작업 요약

## 완료한 내용

- checklist mock 구조화
- station id 기반 역 상세 링크 생성
- segment id 기반 확장 준비
- 테스트 및 문서화

## 수정한 파일

- `mock/checklist.json`
- `frontend/dashboard.js`
- `.docs/Frontend.md`

## 구현 이유

문자열 기반 판별은 빠르지만 확장에 약합니다.

이번 변경으로 mock 데이터가 실제 서비스 API 구조에 더 가까워졌고, 이후 구간 상세 화면 연결도 쉬워졌습니다.

## 변경 사항

- `target_type` 추가
- `station_id` 추가
- `segment_id` 추가
- 구조화 필드 기반 링크 판별 함수 추가

## 새롭게 배운 개념

- Structured Mock Data
- Stable Identifier
- Fallback Logic
- Data Contract

## 실무에서는

실무에서는 화면 표시명과 시스템 식별자를 분리합니다.

사용자에게는 `대전역`을 보여주지만, 내부 링크와 API 요청에는 `station_id`처럼 변하지 않는 값을 사용합니다.

## 개선 가능한 부분

- 모든 station mock에 id 추가
- 모든 segment mock에 id 추가
- `STATION_NAME_BY_ID`를 mock 데이터로 분리
- URL query를 station name이 아니라 station id 기반으로 전환

## 다음 작업

- `vulnerability_stations.json`에 `station_id`를 추가하고 역 상세 URL을 id 기반으로 전환

## 복습 문제

1. 화면 표시명과 시스템 식별자를 분리해야 하는 이유는 무엇인가요?
2. fallback 로직을 남겨두면 어떤 장점이 있나요?
3. `station_id` 기반 URL이 역명 기반 URL보다 안전한 이유는 무엇인가요?

## 오늘 배운 내용

- Target Type
- Station ID
- Segment ID
- Mock Data Contract

## Change Log

2026-07-09

- checklist mock 대상 타입 구조화
- station id 기반 링크 판별 추가
- 문서 업데이트

## Timestamp

2026-07-09 14:00:31 (KST)

---


# 우선 점검 대상 역 상세 링크 작업 요약

# 개요

우선 점검 대상 중 `대전역`처럼 역 단위 대상인 항목을 역 상세 화면으로 이동할 수 있게 연결했습니다.

구간 대상은 아직 구간 상세 화면이 없으므로 링크로 만들지 않고, 역 대상만 `station-detail.html?station=대전` 형태로 연결했습니다.

# 구현 목적

우선 점검 대상에서 역 단위 위험 항목을 발견했을 때, 사용자가 바로 역 상세 화면으로 이동해 더 자세한 지표를 확인할 수 있게 하기 위함입니다.

이전 단계에서 역 상세 화면이 `station` query string을 지원하므로, 이번 단계에서는 우선 점검 대상과 역 상세 화면의 진입점을 연결했습니다.

# 구현 내용

- `frontend/dashboard.js`
  - `getStationNamesFromData()` 추가
  - `getStationNameFromInspectionTarget()` 추가
  - `createStationDetailLink()` 추가
  - `createInspectionTargetCell()` 추가
  - 우선 점검 대상 렌더링 시 `vulnerability_stations.json`의 역 목록을 함께 사용
  - `대전역`처럼 mock 역 목록에 존재하는 역 대상만 링크로 렌더링
  - 상세 패널의 `대상` 값도 역 대상이면 링크로 표시

- `frontend/style.css`
  - `.inspection-link` 스타일 추가
  - hover/focus-visible 상태 추가

# 코드 설명

## 왜 필요한가

우선 점검 대상은 운영자가 조치해야 할 항목을 보여주는 영역입니다.

그중 역 단위 대상은 이미 역 상세 화면이 있으므로, 바로 이동할 수 있어야 분석 흐름이 끊기지 않습니다.

## 어떤 원리인가

1. `vulnerability_stations.json`에서 사용 가능한 역 목록을 가져옵니다.
2. 우선 점검 대상의 `target`이 `역`으로 끝나는지 확인합니다.
3. `역` 접미사를 제거한 이름이 mock 역 목록에 있는지 확인합니다.
4. 존재하면 `station-detail.html?station=역명` 링크를 생성합니다.
5. 존재하지 않거나 구간 대상이면 일반 텍스트로 표시합니다.

## 장점

- 역 대상만 안전하게 상세 화면으로 연결합니다.
- 구간 대상을 잘못 역 상세 화면으로 보내지 않습니다.
- 한글 역명은 `URLSearchParams`를 통해 안전하게 인코딩됩니다.
- 표와 상세 패널 모두 같은 링크 생성 함수를 재사용합니다.

## 단점

- 현재는 target 문자열이 `대전역`처럼 일정한 형식이어야 합니다.
- 역명 기반 매칭이라 동명이역이 생기면 한계가 있습니다.
- 구간 상세 화면은 아직 연결하지 않았습니다.

## 다른 구현 방법

- checklist mock에 `target_type`, `station_id`, `segment_id`를 명시하는 방식
- API 응답에서 상세 URL을 직접 내려주는 방식
- target 문자열 파싱 대신 View Model 변환 단계에서 링크 가능 여부를 계산하는 방식
- 구간 상세 화면을 먼저 만들고 구간 대상도 링크로 연결하는 방식

# API

API 변경 사항은 없습니다.

사용한 mock 데이터:

- `GET ../mock/checklist.json`
- `GET ../mock/vulnerability_stations.json`

# Database

DB 변경 사항은 없습니다.

# 테스트 방법

1. JavaScript 문법 검사

```bash
node --check frontend/dashboard.js
```

예상 결과:

- 오류 없이 종료됩니다.

2. 우선 점검 대상 링크 생성 확인

```bash
node -e "const fs=require('fs'); const checklist=JSON.parse(fs.readFileSync('mock/checklist.json','utf8')); const stations=JSON.parse(fs.readFileSync('mock/vulnerability_stations.json','utf8')).stations.map((item)=>item.station); const links=checklist.items.map((item)=>{ const station=item.target.endsWith('역') ? item.target.slice(0,-1) : null; const href=station&&stations.includes(station) ? './station-detail.html?'+new URLSearchParams({station}).toString() : '-'; return item.target+' => '+href; }); console.log(links.join('\n'));"
```

예상 결과:

```text
대전→김천(구미) 구간 => -
천안→대전 구간 => -
대전역 => ./station-detail.html?station=%EB%8C%80%EC%A0%84
영등포→수원 구간 => -
```

3. 브라우저 확인

```text
http://127.0.0.1:8765/frontend/dashboard.html
```

검증 기준:

- 우선 점검 대상의 `대전역`은 링크로 표시됩니다.
- `대전역` 링크를 클릭하면 역 상세 화면으로 이동합니다.
- 이동 URL은 `station=%EB%8C%80%EC%A0%84` 값을 포함합니다.
- 구간 대상은 링크가 아니라 일반 텍스트로 유지됩니다.

# 주의사항

현재는 문자열 기반으로 역 대상을 판별합니다.

실무에서는 `target_type: "station"`과 `station_id`를 mock/API에 포함하는 편이 더 안전합니다.

# 변경 이력

2026-07-09

- 우선 점검 대상 역 항목 상세 링크 추가
- 상세 패널 대상 값 링크 처리
- 구간 대상은 일반 텍스트 유지

# 다음 작업

- checklist mock에 `target_type`, `station_id`, `segment_id` 추가 설계
- 구간 상세 화면 설계
- 구간 대상 상세 링크 연결

# 작업 요약

## 완료한 내용

- 우선 점검 대상 중 역 대상만 역 상세 화면으로 연결
- 상세 패널 대상 값 링크 처리
- 구간 대상 오연결 방지
- 테스트 및 문서화

## 수정한 파일

- `frontend/dashboard.js`
- `frontend/style.css`
- `.docs/Frontend.md`

## 구현 이유

대시보드에서 점검 대상과 상세 화면이 연결되면 운영자가 더 빠르게 원인과 지표를 확인할 수 있습니다.

단, 아직 구간 상세 화면은 없으므로 역 대상만 연결해 기능 범위를 명확히 제한했습니다.

## 변경 사항

- 역 대상 판별 함수 추가
- 우선 점검 대상 target 셀 링크 처리
- 상세 패널 target 값 링크 처리
- inspection link 스타일 추가

## 새롭게 배운 개념

- 조건부 링크 렌더링
- 문자열 기반 target 판별
- Mock 데이터 간 매칭

## 실무에서는

실무에서는 문자열을 파싱해서 대상 타입을 추론하지 않습니다.

API 응답에 `target_type`, `target_id`, `detail_url` 같은 필드를 포함해 프론트엔드가 안전하게 라우팅할 수 있게 만듭니다.

## 개선 가능한 부분

- checklist mock 구조 개선
- station id 기반 URL 전환
- 구간 상세 화면 추가
- 구간 대상 링크 연결

## 다음 작업

- checklist mock에 대상 타입과 id를 추가하는 구조 설계

## 복습 문제

1. 문자열 파싱으로 대상 타입을 판단하는 방식의 한계는 무엇인가요?
2. 역 대상만 링크로 만들고 구간 대상은 일반 텍스트로 둔 이유는 무엇인가요?
3. `target_type`과 `target_id`를 mock/API에 추가하면 어떤 장점이 있나요?

## 오늘 배운 내용

- Conditional Link Rendering
- Mock Cross-reference
- Target Type Detection

## Change Log

2026-07-09

- 우선 점검 대상 역 상세 링크 추가
- 상세 패널 대상 링크 처리
- 문서 업데이트

## Timestamp

2026-07-09 13:54:38 (KST)

---


# 우선 점검 대상 기본 선택 작업 요약

# 개요

대시보드의 `우선 점검 대상` 상세 패널이 첫 번째 항목을 기본으로 표시하도록 개선했습니다.

이제 사용자가 `상세보기` 버튼을 누르기 전에도 1순위 점검 대상의 상세 근거를 바로 확인할 수 있습니다.

# 구현 목적

우선 점검 대상은 순위가 있는 데이터입니다.

가장 중요한 1순위 항목은 사용자가 별도 조작을 하지 않아도 바로 보여주는 편이 운영 화면에서 더 자연스럽습니다.

# 구현 내용

- `frontend/dashboard.js`
  - `setSelectedInspectionRow()` 추가
  - 테이블 렌더링 후 첫 번째 item을 상세 패널에 자동 렌더링
  - 첫 번째 row에 선택 상태 적용
  - 상세보기 버튼 클릭 시 선택 row 갱신

- `frontend/style.css`
  - `.inspection-table__row--selected` 스타일 추가
  - 선택된 row의 텍스트 강조 처리

# 코드 설명

## 왜 필요한가

기존 상세 패널은 안내 문구만 표시되었고, 사용자가 버튼을 눌러야 의미 있는 데이터가 나타났습니다.

운영 대시보드에서는 가장 중요한 항목을 즉시 보여주는 것이 더 효율적입니다.

## 어떤 원리인가

1. `checklist.items[]`를 rank 기준으로 정렬합니다.
2. 정렬된 첫 번째 item으로 테이블 첫 번째 row를 만듭니다.
3. 테이블 렌더링이 끝나면 `renderInspectionDetail(items[0])`을 호출합니다.
4. `setSelectedInspectionRow(rows[0])`로 첫 번째 행에 선택 상태를 부여합니다.
5. 다른 행의 상세보기 버튼을 누르면 선택 상태가 해당 행으로 이동합니다.

## 장점

- 사용자가 바로 1순위 점검 근거를 확인할 수 있습니다.
- 상세 패널이 빈 안내 상태로 남지 않습니다.
- 현재 선택된 행이 시각적으로 구분됩니다.

## 단점

- 기본 선택 기준이 항상 `rank` 1순위로 고정됩니다.
- 사용자가 마지막으로 선택한 항목을 기억하지는 않습니다.
- 행 선택 상태는 현재 세션의 화면 렌더링에만 유지됩니다.

## 다른 구현 방법

- 마지막 선택 항목을 `localStorage`에 저장하는 방식
- URL query string으로 선택한 점검 항목을 관리하는 방식
- 위험도가 가장 높은 항목을 기본 선택하는 방식
- 사용자가 직접 선택하기 전까지 상세 패널을 접어두는 방식

# API

API 변경 사항은 없습니다.

사용한 mock 데이터:

- `GET ../mock/checklist.json`

# Database

DB 변경 사항은 없습니다.

# 테스트 방법

1. JavaScript 문법 검사

```bash
node --check frontend/dashboard.js
```

예상 결과:

- 오류 없이 종료됩니다.

2. 첫 번째 항목 기대값 확인

```bash
node -e "const fs=require('fs'); const data=JSON.parse(fs.readFileSync('mock/checklist.json','utf8')); const item=data.items.slice().sort((a,b)=>a.rank-b.rank)[0]; const risk=item.avg_delay_incr>=12?'높음':item.avg_delay_incr>=7?'주의':'관심'; console.log([item.target+' 상세', risk, item.reason, '+'+item.avg_delay_incr.toFixed(1)+'분', item.sample_n+'건'].join(' | '));"
```

예상 결과:

```text
대전→김천(구미) 구간 상세 | 높음 | 호우 경보 시 평균 +14.6분 | +14.6분 | 37건
```

3. 브라우저 확인

```text
http://127.0.0.1:8765/frontend/dashboard.html
```

검증 기준:

- 페이지 로드 직후 상세 패널 제목이 `대전→김천(구미) 구간 상세`로 표시됩니다.
- 첫 번째 우선 점검 대상 행이 선택 상태로 강조됩니다.
- 다른 행의 `상세보기`를 클릭하면 상세 패널과 선택 행이 함께 변경됩니다.

# 주의사항

현재 기본 선택 기준은 `rank` 정렬 결과의 첫 번째 항목입니다.

향후 사용자의 마지막 선택을 유지하려면 URL query string 또는 localStorage를 추가로 설계해야 합니다.

# 변경 이력

2026-07-09

- 우선 점검 대상 첫 번째 항목 기본 상세 표시
- 선택 행 강조 스타일 추가
- 상세보기 클릭 시 선택 상태 갱신

# 다음 작업

- 우선 점검 대상 중 역 대상은 역 상세 화면 링크로 연결
- 구간 대상 상세 화면 설계
- 조치 체크리스트 mock 확장

# 작업 요약

## 완료한 내용

- 첫 번째 우선 점검 대상 기본 선택
- 선택 행 시각 강조
- 상세보기 클릭 시 선택 상태 갱신
- 테스트 및 문서화

## 수정한 파일

- `frontend/dashboard.js`
- `frontend/style.css`
- `.docs/Frontend.md`

## 구현 이유

대시보드에서는 사용자가 가장 먼저 봐야 할 정보를 자동으로 노출하는 것이 중요합니다.

1순위 점검 대상 상세를 기본 표시하면 의사결정 속도를 높일 수 있습니다.

## 변경 사항

- `setSelectedInspectionRow()` 추가
- 첫 번째 item 자동 상세 렌더링
- 선택 row 클래스 추가

## 새롭게 배운 개념

- Default Selection
- Selected Row State
- UI State Synchronization

## 실무에서는

실무 운영 도구에서는 첫 번째 항목 기본 선택 패턴을 자주 사용합니다.

특히 알림, 점검 대상, 장애 목록처럼 우선순위가 있는 데이터는 가장 중요한 항목을 자동으로 열어두는 방식이 효율적입니다.

## 개선 가능한 부분

- 마지막 선택 항목 기억
- URL query string으로 선택 점검 항목 공유
- 선택 행에 키보드 탐색 지원 추가

## 다음 작업

- 우선 점검 대상 중 `대전역` 같은 역 대상은 역 상세 화면으로 이동할 수 있게 연결

## 복습 문제

1. 기본 선택 상태를 제공하면 사용자 경험이 어떻게 좋아지나요?
2. 선택된 행을 class로 관리하는 방식의 장점은 무엇인가요?
3. 마지막 선택 항목을 유지하려면 어떤 저장 방식을 사용할 수 있나요?

## 오늘 배운 내용

- Default Selected Item
- Selected State Styling
- Table Row State

## Change Log

2026-07-09

- 우선 점검 대상 기본 선택 상태 추가
- 선택 행 강조 스타일 추가
- 문서 업데이트

## Timestamp

2026-07-09 13:50:18 (KST)

---


# 우선 점검 대상 상세보기 작업 요약

# 개요

대시보드의 `우선 점검 대상` 테이블에서 `상세보기` 버튼을 클릭하면 선택한 항목의 상세 요약 패널이 표시되도록 구현했습니다.

별도 페이지를 만들지 않고, 현재 대시보드 화면 안에서 선택 항목의 위험 사유와 대응 권고를 확인할 수 있게 했습니다.

# 구현 목적

표에는 핵심 정보만 표시되기 때문에 사용자가 왜 이 대상이 우선 점검 대상인지 빠르게 확인하기 어렵습니다.

상세 패널을 추가하면 테이블의 밀도는 유지하면서도 클릭 시 필요한 근거 정보를 더 자세히 보여줄 수 있습니다.

# 구현 내용

- `frontend/dashboard.html`
  - 우선 점검 대상 테이블 아래에 `inspection-detail-panel` 추가
  - 기본 안내 문구 추가

- `frontend/dashboard.js`
  - `data-dashboard-inspection-detail` 요소 연결
  - `renderInspectionDetail()` 추가
  - `상세보기` 버튼 클릭 이벤트 추가
  - 선택 항목의 대상, 위험도, 기상특보, 주요 위험, 평균 지연 증가, 분석 표본, 대응 권고 표시
  - 데이터 없음 상태에서도 상세 패널 안내 문구 표시

- `frontend/style.css`
  - 상세 패널 레이아웃 추가
  - 상세 항목 `dl/dt/dd` 스타일 추가
  - 모바일에서 상세 항목이 1열로 내려가도록 반응형 처리

# 코드 설명

## 왜 필요한가

운영자는 우선 점검 대상 목록을 보고 바로 조치 판단을 해야 합니다.

테이블만 있으면 각 행의 근거가 압축되어 있어, 상세보기 클릭 시 점검 근거와 권고 조치를 한 번 더 풀어서 보여주는 흐름이 필요합니다.

## 어떤 원리인가

1. `checklist.json`의 각 항목으로 테이블 행을 렌더링합니다.
2. 행마다 `상세보기` 버튼을 생성합니다.
3. 버튼에 해당 item을 닫아둔 click 이벤트를 연결합니다.
4. 클릭 시 `renderInspectionDetail(item)`을 호출합니다.
5. 상세 패널을 `replaceChildren()`으로 갱신합니다.

## 장점

- 새 페이지 없이 현재 화면 안에서 빠르게 상세 내용을 확인할 수 있습니다.
- mock 데이터 구조를 크게 바꾸지 않고 구현할 수 있습니다.
- 테이블은 간결하게 유지하고 상세 정보는 필요할 때만 보여줄 수 있습니다.

## 단점

- 현재 mock에는 상세 설명 전용 필드가 없습니다.
- 상세 패널은 기존 표 데이터를 재구성해서 보여줍니다.
- 여러 항목을 동시에 비교하는 상세 보기에는 적합하지 않습니다.

## 다른 구현 방법

- 상세보기 클릭 시 modal을 여는 방식
- 행 아래에 expandable row를 추가하는 방식
- 별도 상세 페이지로 이동하는 방식
- 우측 drawer 패널을 여는 방식

# API

API 변경 사항은 없습니다.

사용한 mock 데이터:

- `GET ../mock/checklist.json`

# Database

DB 변경 사항은 없습니다.

# 테스트 방법

1. JavaScript 문법 검사

```bash
node --check frontend/dashboard.js
```

예상 결과:

- 오류 없이 종료됩니다.

2. mock 상세값 계산 확인

```bash
node -e "const fs=require('fs'); const data=JSON.parse(fs.readFileSync('mock/checklist.json','utf8')); const item=data.items[2]; const risk=item.avg_delay_incr>=12?'높음':item.avg_delay_incr>=7?'주의':'관심'; console.log([item.target, risk, item.reason, '+'+item.avg_delay_incr.toFixed(1)+'분', item.sample_n+'건'].join(' | '));"
```

예상 결과:

```text
대전역 | 주의 | 폭염 경보 시 지연율 44% | +8.9분 | 61건
```

3. 브라우저 확인

```text
http://127.0.0.1:8765/frontend/dashboard.html
```

검증 기준:

- 우선 점검 대상 테이블 아래에 기본 상세 안내 패널이 표시됩니다.
- `대전역` 행의 상세보기를 누르면 상세 패널 제목이 `대전역 상세`로 바뀝니다.
- 상세 패널에 위험도, 기상특보, 주요 위험, 평균 지연 증가, 분석 표본, 대응 권고가 표시됩니다.

# 주의사항

현재 `checklist.json`에는 상세 설명 전용 필드가 없습니다.

더 풍부한 상세 화면을 만들려면 `description`, `action_items`, `last_checked_at`, `owner_team` 같은 필드를 mock 또는 API에 추가하는 것이 좋습니다.

# 변경 이력

2026-07-09

- 우선 점검 대상 상세 패널 추가
- 상세보기 버튼 클릭 이벤트 연결
- 선택 항목 상세 정보 렌더링

# 다음 작업

- 상세 패널에 조치 체크리스트 추가
- `대전역` 같은 역 대상은 역 상세 화면 링크와 함께 제공
- 구간 대상은 구간 상세 화면 설계 후 연결

# 작업 요약

## 완료한 내용

- 우선 점검 대상 상세보기 버튼 동작 구현
- 선택 항목 상세 패널 렌더링
- 빈 상태 안내 처리
- 테스트 및 문서화

## 수정한 파일

- `frontend/dashboard.html`
- `frontend/dashboard.js`
- `frontend/style.css`
- `.docs/Frontend.md`

## 구현 이유

우선 점검 대상은 운영 의사결정과 직접 연결되는 영역입니다.

상세보기 버튼이 실제 정보를 보여주면 사용자가 점검 우선순위와 대응 이유를 더 쉽게 이해할 수 있습니다.

## 변경 사항

- 상세 패널 DOM 추가
- 상세 패널 렌더링 함수 추가
- 상세보기 클릭 이벤트 추가
- 상세 패널 스타일 추가

## 새롭게 배운 개념

- Inline Detail Panel
- Event Handler Closure
- `dl/dt/dd`를 활용한 상세 정보 표현
- `aria-live`를 활용한 동적 영역 안내

## 실무에서는

실무에서는 상세 패널에 단순 요약뿐 아니라 조치 이력, 담당 부서, 마지막 점검 시간, 근거 데이터 링크를 함께 제공합니다.

또한 위험도 높은 항목은 버튼 클릭 없이도 첫 번째 항목을 기본 선택 상태로 보여주는 방식을 자주 사용합니다.

## 개선 가능한 부분

- 첫 번째 우선 점검 대상을 기본 선택으로 표시
- 조치 체크리스트 mock 추가
- 담당자/부서 정보 추가
- 상세 패널 닫기 또는 고정 기능 추가

## 다음 작업

- 첫 번째 우선 점검 대상을 기본 선택 상태로 표시

## 복습 문제

1. 상세 패널을 별도 페이지 대신 현재 화면에 표시하는 장점은 무엇인가요?
2. 버튼 클릭 이벤트에서 item 데이터를 사용할 수 있는 이유는 무엇인가요?
3. 상세 정보 표현에 `dl/dt/dd` 구조를 사용할 때의 장점은 무엇인가요?

## 오늘 배운 내용

- Inline Detail Pattern
- Event-driven Rendering
- Definition List
- Dynamic Detail Panel

## Change Log

2026-07-09

- 우선 점검 대상 상세보기 패널 추가
- 상세보기 클릭 이벤트 연결
- 상세 패널 스타일 및 문서 업데이트

## Timestamp

2026-07-09 13:47:09 (KST)

---


# 대시보드 취약 역 상세 이동 작업 요약

# 개요

대시보드의 `취약 역 TOP 5` 랭킹에서 역명을 클릭하면 역 상세 화면으로 이동하도록 연결했습니다.

이동 시 선택한 역명을 `station` query string으로 전달합니다.

예시:

```text
./station-detail.html?station=%EA%B9%80%EC%B2%9C%28%EA%B5%AC%EB%AF%B8%29
```

# 구현 목적

대시보드에서 위험한 역을 발견한 뒤, 사용자가 바로 해당 역의 상세 지표를 확인할 수 있는 흐름을 만들기 위함입니다.

이전 단계에서 역 상세 화면이 `station` query string을 읽도록 구현했기 때문에, 이번 단계에서는 대시보드에서 그 값을 전달하는 진입점을 연결했습니다.

# 구현 내용

- `frontend/dashboard.js`
  - `STATION_DETAIL_URL` 상수 추가
  - `STATION_QUERY_PARAM` 상수 추가
  - `createStationDetailUrl()` 추가
  - `createStationLinkCell()` 추가
  - 취약 역 랭킹의 역명 셀을 텍스트에서 링크로 변경

- `frontend/style.css`
  - `.ranking-table__link` 스타일 추가
  - hover 상태 추가
  - focus-visible 상태 추가

# 코드 설명

## 왜 필요한가

대시보드는 전체 위험 상황을 파악하는 화면이고, 역 상세 화면은 특정 역을 분석하는 화면입니다.

두 화면이 연결되지 않으면 사용자가 랭킹에서 역을 확인한 뒤 다시 직접 역 상세 화면에서 선택해야 합니다.

## 어떤 원리인가

1. `vulnerability_stations.json`의 역 목록으로 취약 역 랭킹을 렌더링합니다.
2. 각 역명 셀을 `a` 태그로 생성합니다.
3. 링크 URL은 `URLSearchParams`로 안전하게 만듭니다.
4. 사용자가 역명을 클릭하면 `station-detail.html?station=역명`으로 이동합니다.
5. 역 상세 화면은 query string의 `station` 값을 읽어 해당 역 기준으로 렌더링합니다.

## 장점

- 대시보드와 상세 화면의 사용자 흐름이 연결됩니다.
- 한글과 괄호가 포함된 역명도 `URLSearchParams`로 안전하게 인코딩됩니다.
- 링크이기 때문에 새 탭 열기, 복사, 접근성 측면에서 버튼보다 자연스럽습니다.

## 단점

- 현재는 역명을 query key로 사용합니다.
- 역명이 바뀌거나 중복되면 station id 기반으로 변경해야 합니다.
- 구간 상세 화면은 아직 없기 때문에 취약 구간 TOP 5는 연결하지 않았습니다.

## 다른 구현 방법

- 역명 대신 station id를 전달하는 방식
- 랭킹 행 전체를 클릭 가능하게 만드는 방식
- 상세 화면을 페이지 이동이 아니라 modal로 여는 방식
- 프론트엔드 라우터를 도입해 `/stations/:stationId` 형태로 관리하는 방식

# API

API 변경 사항은 없습니다.

사용한 mock 데이터:

- `GET ../mock/vulnerability_stations.json`

# Database

DB 변경 사항은 없습니다.

# 테스트 방법

1. JavaScript 문법 검사

```bash
node --check frontend/dashboard.js
node --check frontend/station-detail.js
```

예상 결과:

- 오류 없이 종료됩니다.

2. URL 생성 검증

```bash
node -e "const params=new URLSearchParams({station:'김천(구미)'}); console.log('./station-detail.html?'+params.toString());"
```

예상 결과:

```text
./station-detail.html?station=%EA%B9%80%EC%B2%9C%28%EA%B5%AC%EB%AF%B8%29
```

3. 브라우저 확인

```text
http://127.0.0.1:8765/frontend/dashboard.html
```

검증 기준:

- 취약 역 TOP 5의 역명이 링크처럼 동작합니다.
- `김천(구미)`를 클릭하면 역 상세 화면으로 이동합니다.
- 이동 URL에 `station=%EA%B9%80%EC%B2%9C%28%EA%B5%AC%EB%AF%B8%29`가 포함됩니다.
- 역 상세 화면은 김천(구미)역 기준 주요 지표를 표시합니다.

# 주의사항

현재 취약 역 랭킹만 상세 화면과 연결했습니다.

취약 구간 랭킹은 아직 구간 상세 화면이 없으므로 링크를 추가하지 않았습니다.

# 변경 이력

2026-07-09

- 대시보드 취약 역 랭킹 역명 링크 추가
- 역 상세 화면으로 `station` query 전달
- 랭킹 링크 스타일 추가

# 다음 작업

- 대시보드 우선 점검 대상의 상세보기 버튼 연결 설계
- 취약 구간 상세 화면 설계
- station id 기반 mock 구조 설계

# 작업 요약

## 완료한 내용

- 취약 역 TOP 5 역명 클릭 이동 구현
- `URLSearchParams` 기반 query string 생성
- 링크 hover/focus 스타일 추가
- 테스트 및 문서화

## 수정한 파일

- `frontend/dashboard.js`
- `frontend/style.css`
- `.docs/Frontend.md`

## 구현 이유

사용자는 대시보드에서 위험한 역을 확인한 직후 상세 지표를 보고 싶어 합니다.

따라서 랭킹과 상세 화면을 연결하면 분석 흐름이 끊기지 않습니다.

## 변경 사항

- 취약 역명 텍스트를 링크로 변경
- 선택 역을 `station` query string으로 전달
- 링크 접근성 문구 추가

## 새롭게 배운 개념

- URLSearchParams
- 페이지 간 상태 전달
- 링크 기반 내비게이션
- 접근 가능한 링크 라벨

## 실무에서는

실무에서는 역명보다 `stationId`를 링크에 전달하는 편이 안전합니다.

예를 들어 `station-detail.html?stationId=daejeon`처럼 불변 id를 사용하면 역명이 바뀌어도 링크가 깨지지 않습니다.

## 개선 가능한 부분

- mock에 station id 추가
- 취약 구간 상세 페이지 추가
- 우선 점검 대상 상세보기 버튼 연결
- 랭킹 행 전체 클릭 영역 검토

## 다음 작업

- 우선 점검 대상 `상세보기` 버튼 동작 설계

## 복습 문제

1. 한글 역명을 URL에 넣을 때 `URLSearchParams`를 사용하는 이유는 무엇인가요?
2. 버튼보다 링크가 더 적절한 경우는 언제인가요?
3. 역명 대신 station id를 사용하는 것이 실무에서 더 안전한 이유는 무엇인가요?

## 오늘 배운 내용

- URL Encoding
- Link Navigation
- Dashboard to Detail Flow
- Accessible Link Label

## Change Log

2026-07-09

- 대시보드 취약 역 랭킹 상세 이동 연결
- `station` query string 전달
- 랭킹 링크 스타일 추가

## Timestamp

2026-07-09 13:43:58 (KST)

---


# 대시보드 전체 보기 링크 연결 작업 요약

## 완료한 내용

- 대시보드의 `취약 구간 TOP 5` 카드에 있는 `전체 보기` 링크를 구간 상세 화면으로 연결했습니다.
- 대시보드의 `취약 역 TOP 5` 카드에 있는 `전체 보기` 링크를 역 상세 화면으로 연결했습니다.

## 수정한 파일

- `frontend/dashboard.html`
- `.docs/Frontend.md`

## 구현 이유

기존 `전체 보기` 링크는 `href="#"`로 되어 있어 클릭해도 실제 페이지 이동이 발생하지 않았습니다. 사용자가 취약 구간과 취약 역 목록에서 자연스럽게 상세 분석 화면으로 이동할 수 있도록 실제 상세 페이지 경로를 연결했습니다.

## 변경 사항

- 취약 구간 전체 보기: `./route-detail.html?segment_id=daejeon-gimcheon_gumi`
- 취약 역 전체 보기: `./station-detail.html`

## 새롭게 배운 개념

- `href="#"`는 임시 링크로 사용할 수 있지만, 실제 기능이 없으면 사용자 경험과 접근성 측면에서 혼란을 줄 수 있습니다.
- 구간 상세 화면은 `segment_id` query parameter를 기준으로 상세 데이터를 선택합니다.

## 실무에서는

실무에서는 `전체 보기`가 단일 상세 페이지가 아니라 목록 페이지로 이동하는 경우가 많습니다. 현재 프로젝트에는 별도 전체 목록 페이지가 없으므로, 기존에 구현된 상세 화면 중 대표 구간과 역 상세 화면으로 연결하는 방식이 가장 작은 변경입니다.

## 개선 가능한 부분

- 취약 구간 전체 목록 페이지 추가
- 취약 역 전체 목록 페이지 추가
- 현재 TOP 5 데이터의 1순위 항목을 기준으로 동적 링크 생성

## 다음 작업

- 대시보드 필터 `적용하기` 기능 연결
- 지도 카드 `전체 보기` 기능 설계
- 전체 목록 페이지가 필요한지 결정

## 프로젝트 진행률

■■■■■■■■□□ 80%

완료

- 취약 구간 전체 보기 링크 연결
- 취약 역 전체 보기 링크 연결

진행 중

- 디자인만 있는 버튼/링크 기능 연결

예정

- 대시보드 필터 동작 구현
- 구간/역 전체 목록 화면 설계

## 복습 문제

1. `href="#"`를 실제 서비스 화면에 그대로 두면 어떤 문제가 생길 수 있을까요?
2. query parameter를 사용해 상세 화면의 데이터를 선택하는 방식의 장점은 무엇일까요?
3. `전체 보기`가 상세 화면이 아니라 목록 화면으로 가야 하는 경우에는 어떤 라우팅 구조가 더 적절할까요?

## 오늘 배운 내용

- 임시 링크 제거
- HTML 앵커 이동 경로
- Query Parameter 기반 상세 화면 이동

## README 반영 여부

이번 작업은 기존 화면 간 이동 링크를 연결한 작은 변경이므로 README에 별도 기능 설명을 추가하지 않았습니다.

## 추천 Commit Message

`fix: 대시보드 전체 보기 링크 연결`

## Change Log

2026-07-10

- 대시보드 취약 구간 전체 보기 링크를 구간 상세 화면으로 연결
- 대시보드 취약 역 전체 보기 링크를 역 상세 화면으로 연결

## Timestamp

2026-07-10 10:35:56 (KST)
---


# 대시보드 필터 기능 연결 작업 요약

## 완료한 내용

- 대시보드 필터 폼의 `적용하기` 버튼이 실제 화면 데이터를 다시 렌더링하도록 연결했습니다.
- `노선`, `특보 종류`, `특보 등급` 조건을 대시보드 데이터에 반영했습니다.
- `초기화` 버튼을 누르면 필터링 전 전체 mock 데이터 화면으로 돌아가도록 처리했습니다.

## 수정한 파일

- `frontend/dashboard.html`
- `frontend/dashboard.js`
- `.docs/Frontend.md`

## 구현 이유

기존 필터 영역은 select와 버튼 UI만 있었고, `적용하기`를 눌러도 데이터가 바뀌지 않았습니다. 사용자가 선택한 조건에 따라 알림 배너, 요약 카드, 취약 랭킹, 점검 테이블이 달라지도록 연결했습니다.

## 변경 사항

- 필터 폼에 `data-dashboard-filter-form` 추가
- 특보 종류 select에 `전체` 기본 옵션 추가
- 특보 종류, 특보 등급, 열차 종류 select에 JS 연결용 `data-*` 속성 추가
- 원본 mock 데이터를 `dashboardState`에 보관
- submit 시 필터링된 데이터로 재렌더링
- reset 시 원본 데이터로 재렌더링

## 코드 설명

필터는 원본 데이터를 직접 수정하지 않습니다. `getFilteredDashboardData()`에서 원본 mock 데이터를 기준으로 필터 조건에 맞는 새 데이터 객체를 만든 뒤 기존 렌더 함수에 전달합니다.

이 방식의 장점은 초기화가 쉽고, 같은 원본 데이터를 여러 조건으로 반복 필터링해도 데이터가 손상되지 않는다는 점입니다.

## API

API 변경 사항은 없습니다.

현재는 기존 mock 파일을 사용합니다.

- `mock/alerts_active.json`
- `mock/checklist.json`
- `mock/vulnerability_segments.json`
- `mock/vulnerability_stations.json`
- `mock/heatmap.json`

## Database

DB 변경 사항은 없습니다.

## 주의사항

- `열차 종류`는 현재 mock 데이터에 대응 필드가 없어 실제 필터 조건에는 반영하지 않았습니다.
- 히트맵 mock에는 특보 종류/등급 필드가 없어 `노선` 조건만 반영합니다.
- 전체 목록 페이지가 아직 없으므로 필터 결과는 현재 대시보드에 보이는 영역 중심으로 반영됩니다.

## 테스트 방법

```bash
node --check frontend/dashboard.js
```

예상 결과:

- JavaScript 문법 오류 없이 종료됩니다.

브라우저 확인:

- 대시보드에서 특보 종류를 변경하고 `적용하기`를 누르면 알림 배너, 요약 카드, 랭킹, 점검 테이블이 조건에 맞게 갱신됩니다.
- `초기화`를 누르면 필터링 전 전체 데이터가 다시 표시됩니다.

## 구현 목적

디자인만 존재하던 필터 영역을 실제 mock 데이터 기반 화면 제어 기능으로 전환하는 것이 목적입니다.

## 구현 내용

- 필터 폼 이벤트 제어
- 원본 데이터 상태 저장
- 필터 조건 추출
- 영역별 데이터 필터링
- 기존 렌더 함수 재사용

## 변경 이력

2026-07-10

- 대시보드 필터 적용 기능 추가
- 대시보드 필터 초기화 기능 추가

## 작업 요약

## 완료한 내용

- 필터 `적용하기` 기능 연결
- 필터 `초기화` 기능 연결
- mock 기반 필터링 로직 추가
- JS 문법 검사 완료

## 수정한 파일

- `frontend/dashboard.html`
- `frontend/dashboard.js`
- `.docs/Frontend.md`

## 구현 이유

사용자가 필터를 조작해도 화면이 변하지 않는 문제를 해결하기 위해 이벤트와 렌더링 로직을 연결했습니다.

## 변경 사항

- `submit` 기본 동작 차단
- 필터 조건 기반 데이터 객체 생성
- 기존 렌더 함수 재호출

## 새롭게 배운 개념

- Form Submit Handling
- Reset Event Handling
- Immutable Filtering

## 실무에서는

실무에서는 필터 조건을 URL query parameter에도 반영하는 경우가 많습니다. 그러면 사용자가 필터링된 화면을 공유하거나 새로고침해도 같은 조건을 유지할 수 있습니다.

## 개선 가능한 부분

- 열차 종류 필터를 위한 mock/API 필드 추가
- 필터 조건을 URL query parameter와 동기화
- 필터 결과 없음 상태 문구 개선

## 다음 작업

- 지도 카드 `전체 보기` 버튼 기능 연결
- 구간 상세 과거 사례 필터 기능 연결

## 프로젝트 진행률

■■■■■■■■□□ 80%

완료

- 대시보드 필터 적용 기능
- 대시보드 필터 초기화 기능

진행 중

- 디자인만 있는 버튼/링크 기능 연결

예정

- 열차 종류 필터 데이터 구조 설계
- 전체 보기 목록 화면 설계

## 복습 문제

1. 원본 데이터를 직접 수정하지 않고 필터링된 새 객체를 만드는 이유는 무엇일까요?
2. `submit` 이벤트에서 `preventDefault()`가 필요한 이유는 무엇일까요?
3. 필터 조건을 URL query parameter에 저장하면 어떤 장점이 있을까요?

## 오늘 배운 내용

- Form Submit Handling
- Reset Event
- Data Filtering

## README 반영 여부

이번 작업은 대시보드 내부 동작 개선이므로 README에는 별도 항목을 추가하지 않았습니다.

## 추천 Commit Message

`feat: 대시보드 필터 적용 기능 연결`

## Change Log

2026-07-10

- 대시보드 필터 적용 및 초기화 기능 추가

## Timestamp

2026-07-10 10:40:43 (KST)
---


# 대시보드 역별 취약도 화살표 상세 이동 구현 작업 요약

# 개요

대시보드의 `경부선 기상 취약도 현황` 노선 지도에서 각 역 오른쪽 화살표를 누르면 역 상세 화면으로 이동하도록 구현했습니다.

# 구현 목적

사용자가 지도에서 관심, 주의, 높음 상태를 확인한 뒤 해당 역의 상세 화면으로 자연스럽게 이동할 수 있도록 하기 위함입니다.

# 구현 내용

- `frontend/dashboard.html`에서 노선 지도 카드의 `전체 보기` 버튼을 제거했습니다.
- `frontend/dashboard.js`의 `createRouteMapItem()`에서 화살표를 `span`이 아닌 `a` 링크로 생성하도록 변경했습니다.
- mock 취약 역 데이터에 존재하는 역은 `station_id`로 이동합니다.
- mock 취약 역 데이터에 없는 역은 새 mock 값을 추가하지 않고 `station=역명`으로 이동합니다.
- `frontend/station-detail.js`에서 URL의 `station` 파라미터가 mock 목록에 없어도 해당 역명을 유지하도록 수정했습니다.
- `frontend/style.css`에서 화살표 링크의 hover/focus 스타일을 추가했습니다.

# 코드 설명

## 왜 필요한가

기존 화살표는 클릭 가능한 것처럼 보이지만 실제 이동 기능이 없었습니다.
사용자 입장에서는 역별 위험도를 본 뒤 자연스럽게 해당 역 상세로 들어가는 흐름이 필요합니다.

## 어떤 원리인가

대시보드에서 역 이름을 기준으로 `vulnerability_stations.json`의 `station_id`를 찾습니다.
찾으면 `station-detail.html?station_id=...`로 이동하고, 찾지 못하면 `station-detail.html?station=역명`으로 이동합니다.
역 상세 화면은 `station` 파라미터를 그대로 받아 제목과 기본 정보를 해당 역명 기준으로 표시합니다.

## 실행 흐름

1. `mock/heatmap.json`의 `nodes[]`를 기준으로 역 목록을 렌더링합니다.
2. 각 역 이름을 `mock/vulnerability_stations.json`에서 찾습니다.
3. mock 지표가 있는 역은 `station_id` 링크를 생성합니다.
4. mock 지표가 없는 역은 `station` 이름 링크를 생성합니다.
5. 역 상세 화면은 mock 상세 데이터가 없으면 지표와 표를 빈 상태로 보여줍니다.

# API

API 변경은 없습니다.

# Database

Database 변경은 없습니다.

# 주의사항

- 이번 작업에서는 mock 데이터가 없는 역의 값을 새로 추가하지 않았습니다.
- mock 데이터가 없는 역은 상세 화면으로 이동하지만 지표, 특보별 통계, 과거 사례는 빈 상태로 표시됩니다.
- 실무에서는 역 기본 정보와 위험도 지표를 분리해, 지표가 없어도 역명/노선/위치 같은 기본 정보는 API에서 제공하는 편이 좋습니다.

# 테스트

## 테스트 방법

```bash
node --check frontend/dashboard.js
node --check frontend/station-detail.js
```

```bash
node -e "const fs=require('fs'); const heatmap=JSON.parse(fs.readFileSync('mock/heatmap.json','utf8')); const vuln=JSON.parse(fs.readFileSync('mock/vulnerability_stations.json','utf8')); const ids=new Map(vuln.stations.map(s=>[s.station,s.station_id])); const urls=heatmap.nodes.map(n=>ids.has(n.station)?'./station-detail.html?station_id='+ids.get(n.station):'./station-detail.html?station='+encodeURIComponent(n.station)); console.log(urls.join('\n')); if(!urls.some(u=>u.includes('station='))) process.exit(1);"
```

## 예상 결과

- JS 문법 오류가 없어야 합니다.
- mock 데이터가 있는 역은 `station_id` URL이 생성되어야 합니다.
- mock 데이터가 없는 역은 `station` URL이 생성되어야 합니다.

## 검증 결과

- `node --check frontend/dashboard.js`: 통과
- `node --check frontend/station-detail.js`: 통과
- 노선 지도 역 상세 URL 생성 검증: 통과

# 작업 요약

## 완료한 내용

- 노선 지도 역별 화살표 링크 구현
- mock 없는 역명 기반 상세 이동 지원
- 노선 지도 카드의 전체 보기 버튼 제거
- 접근 가능한 링크 라벨과 포커스 스타일 추가
- 문서 업데이트

## 수정한 파일

- `frontend/dashboard.html`
- `frontend/dashboard.js`
- `frontend/station-detail.js`
- `frontend/style.css`
- `.docs/Frontend.md`

## 구현 이유

화면에서 역별 위험도를 확인한 사용자가 추가 정보를 보기 위해 바로 역 상세 화면으로 이동할 수 있어야 하기 때문입니다.

## 변경 사항

- 정적 버튼 형태의 `전체 보기` 제거
- 역별 화살표를 상세 페이지 링크로 변경
- mock 데이터가 없는 역도 URL의 역명을 유지하도록 역 상세 초기 선택 로직 변경

## 새롭게 배운 개념

- URL query parameter 기반 화면 상태 전달
- mock 데이터가 없는 대상의 fallback 렌더링
- 링크 접근성 라벨

## 실무에서는

실무에서는 역 ID를 모든 역에 대해 안정적으로 관리하고, 상세 지표 유무와 관계없이 역 기본 정보 API를 제공합니다.
또한 데이터 없음 상태는 단순 빈칸보다 `분석 가능한 데이터가 부족함`처럼 의사결정에 도움이 되는 문구로 명확히 표시합니다.

## 개선 가능한 부분

- 모든 heatmap 역에 고유 station id 부여
- 역 상세 화면의 데이터 없음 안내 문구 강화
- 지도 화살표 클릭 이벤트에 E2E 테스트 추가

## 다음 작업

- 역 상세 화면의 데이터 없음 상태 문구를 더 명확하게 개선
- 노선 지도 역 전체 클릭 영역 확장 검토

# 프로젝트 진행률

■■■■■■■■□□ 82%

완료

- 대시보드 역별 상세 이동
- 전체 보기 버튼 제거

진행 중

- 상세 화면 간 이동 흐름 정리

예정

- mock 없는 역의 데이터 없음 UX 개선
- 역 ID 체계 공통화

# 복습 문제

1. mock 데이터가 없는 역도 `station=역명`으로 이동하게 만든 이유는 무엇일까요?
2. `station_id`와 `station` 쿼리를 함께 지원하면 어떤 장단점이 있을까요?
3. 클릭 가능한 화살표에 `aria-label`을 넣는 이유는 무엇일까요?

# 오늘 배운 내용

- Query Parameter Routing
- Fallback Detail Rendering
- Accessible Link Label

# README 반영 여부

이번 작업은 대시보드 내부 이동 UX 개선이므로 README 변경은 필요하지 않습니다.

# 추천 Commit Message

`feat: 대시보드 역별 상세 이동 링크 추가`

## Change Log

2026-07-10

- 대시보드 노선 지도 역별 화살표를 역 상세 링크로 변경
- mock 데이터가 없는 역명 기반 상세 이동 지원
- 노선 지도 카드 전체 보기 버튼 제거

## Timestamp

2026-07-10 11:14:32 (KST)
---


# 대시보드 경부선 고속 노선도 및 특보 지역 표시 개선

# 개요

대시보드의 발효 기상특보 지역을 축약하지 않고 모두 표시하고, 경부선 고속 정차역과 역간 구간의 데이터 유무 및 위험도를 노선도에 반영했습니다.

# 구현 목적

- 사용자가 발효 특보 대상 지역을 누락 없이 확인할 수 있도록 합니다.
- API가 일부 역만 반환해도 경부선 고속 노선 구조 전체를 유지합니다.
- 역 위험도와 역간 구간 위험도를 서로 독립적으로 표현합니다.
- 각 정차역에서 해당 역 상세 화면으로 이동할 수 있도록 합니다.

# 구현 내용

- 고속 정차역 10개를 `서울 → 광명 → 천안아산 → 오송 → 대전 → 김천(구미) → 동대구 → 경주 → 울산 → 부산` 순서로 정의했습니다.
- `heatmap.nodes[]`의 역명과 정확히 일치하는 데이터만 역 위험도에 연결했습니다.
- 인접한 고속 정차역 쌍과 정확히 일치하는 `heatmap.edges[]`만 구간 위험도에 연결했습니다.
- 데이터가 없는 역과 구간은 범례의 데이터 없음 색상인 회색으로 표시합니다.
- 역 오른쪽 이동 아이콘은 역별 query parameter가 포함된 역 상세 URL을 사용합니다.
- 발효 특보 지역은 중복 제거 후 쉼표로 구분해 모두 표시합니다.

# 코드 설명

`buildHighSpeedRoute()`가 고정된 고속 정차역 목록과 히트맵 데이터를 결합합니다. 데이터가 없는 항목은 `null` 취약도를 가지며 `getRiskLevelByVulnerability()`에서 `none`으로 분류됩니다. 각 역간 연결선은 별도 DOM 요소로 렌더링되므로 역의 위험도와 구간의 위험도가 서로 영향을 주지 않습니다.

장점은 불완전한 응답에서도 전체 노선 구조가 유지되고 데이터 없음이 명확하다는 점입니다. 단점은 현재 고속 정차역 목록이 프론트엔드 상수이므로 운영 환경에서 노선 변경 시 배포가 필요하다는 점입니다. 다른 방법으로는 노선 메타데이터 API에서 전체 정차역과 순서를 제공받는 방식이 있습니다.

# API

새 API는 추가하지 않았습니다. 기존 히트맵 응답의 `nodes[]`, `edges[]`와 발효 특보 응답의 `active[].region_name`을 사용합니다.

# Database

변경 사항이 없습니다.

# 주의사항

- `mock/` 폴더는 수정하지 않았습니다.
- 일반 경부선 역명과 고속 정차역 명칭이 다르면 자동으로 유사 매칭하지 않습니다. 잘못된 데이터 연결을 방지하기 위한 정책입니다.
- 실무에서는 노선 순서와 역 식별자를 별도 메타데이터 API로 관리하는 것이 적절합니다.

# 변경 이력

2026-07-10

- 기상특보 지역 전체 표시
- 경부선 고속 정차역 10개 고정 표시
- 역 및 인접 구간 위험도 독립 색상 적용
- 정차역별 상세 화면 링크 적용

# 다음 작업

- 역 상세 페이지의 전체 고속 정차역 변경 필터 적용
- 역 주소, 목록으로 버튼, 과거 주요 사례 제거

# 작업 요약

## 완료한 내용

- 특보 지역 전체 표시
- 고속 정차역 전체 노선도 표시
- 역·구간 데이터 없음 처리
- 정차역별 상세 링크 지정

## 수정한 파일

- `frontend/dashboard.js`
- `frontend/style.css`
- `.docs/Frontend.md`

## 구현 이유

일부 데이터만 존재하는 상황에서도 전체 노선과 데이터 공백을 함께 보여주어 운영자가 위험도와 미수집 구간을 구분할 수 있도록 했습니다.

## 변경 사항

- 축약 지역명 생성 로직을 전체 지역명 결합 방식으로 변경
- 고속 정차역과 히트맵 데이터를 결합하는 함수 추가
- 구간별 연결선 요소와 위험도 스타일 추가
- 모바일 연결선 위치 보정

## 새롭게 배운 개념

- 기준 노선과 관측 데이터의 병합
- 결측 데이터의 명시적 표현
- 역과 구간의 독립적인 상태 렌더링

## 실무에서는

역 이름보다 변경 가능성이 낮은 역 코드를 조인 키로 사용하고, 노선 메타데이터와 위험도 데이터를 별도 API로 제공하는 편이 안전합니다.

## 개선 가능한 부분

- 노선 메타데이터 API 도입
- 역 코드 기반 데이터 결합
- DOM 렌더링 자동화 테스트 추가

## 다음 작업

- 역 상세 페이지 요구사항 구현

## 프로젝트 진행률

■■■□□□□□□□ 30%

완료

- 요구사항 및 구조 분석
- 대시보드 변경

진행 중

- 역 상세 페이지 변경 준비

예정

- 구간 상세 페이지 변경
- 공통 사이드바 변경
- 전체 회귀 테스트

## 복습 문제

1. API 응답에 존재하는 역만 렌더링하면 노선도에서 어떤 문제가 발생할 수 있을까요?
2. 역 위험도와 구간 위험도를 별도 요소로 렌더링하는 이유는 무엇일까요?
3. 역 이름 대신 역 코드를 데이터 결합 키로 사용하면 어떤 장점이 있을까요?

## 오늘 배운 내용

- Reference Data
- Missing Data State
- Independent Segment Rendering

## README 반영 여부

이번 변경은 기존 대시보드 표시 방식 개선이므로 README에는 별도 항목을 추가하지 않았습니다.

## 추천 Commit Message

`feat: 경부선 고속 노선도와 특보 지역 표시 개선`

## Change Log

2026-07-10

- 대시보드 경부선 고속 노선도 및 특보 지역 표시 개선

## Timestamp

2026-07-10 14:55:33 (KST)

---


# 대시보드 다중 기상특보 배너 개선

# 개요

대시보드의 특보 종류와 등급이 전체인 경우 현재 발효 중인 모든 특보를 종류와 등급별로 구분하여 표시합니다.

# 구현 목적

- 첫 번째 특보만 대표로 노출되던 정보 누락을 해소합니다.
- 동일 특보가 여러 지역에 발효됐을 때 배너가 지나치게 길어지지 않도록 요약합니다.
- 마우스, 키보드, 터치 환경에서 숨은 지역을 확인할 수 있도록 합니다.

# 구현 내용

- `alert_type + alert_level` 조합을 동일 특보 그룹의 기준으로 사용합니다.
- 각 그룹에 특보명, 대표 지역, 영향 가능 구간 수, 기준 시간을 표시합니다.
- 지역이 여러 개인 경우 첫 지역 뒤에 `외 N개 지역`을 표시합니다.
- `외 N개 지역`에 마우스를 올리거나 키보드 포커스를 이동하면 나머지 지역 목록을 표시합니다.
- 마우스가 영역을 벗어나거나 포커스가 빠지면 목록을 숨깁니다.
- 터치 환경에서는 버튼을 눌러 목록을 열고 닫을 수 있으며 `Escape` 키도 지원합니다.
- 발효 특보가 없을 때 기존 빈 상태 문구를 유지합니다.

# 코드 설명

`groupActiveAlerts()`는 발효 특보 배열을 종류와 등급 조합으로 그룹화하고 지역 중복을 제거합니다. `createAlertGroupItem()`은 그룹별 DOM을 생성하며, `createHiddenRegionList()`는 대표 지역 외의 지역을 툴팁 목록으로 구성합니다.

이 방식은 현재 Mock 응답 구조를 변경하지 않고 여러 특보를 표현할 수 있다는 장점이 있습니다. 반면 동일 영향 구간을 식별할 안정적인 `segment_id`가 없으므로 여러 지역에 중복된 동일 구간은 현재 중복 합산될 수 있습니다. 다른 구현 방법으로 백엔드에서 특보 그룹과 고유 영향 구간 수를 계산한 View Model을 제공할 수 있으며, 실무에서는 이 방식이 중복 판정 정책을 일관되게 관리하기에 더 적합합니다.

# API

API 계약 변경은 없습니다. 기존 `GET /alerts/active?line=경부선` 응답의 다음 필드를 사용합니다.

- `active[].alert_type`
- `active[].alert_level`
- `active[].region_name`
- `active[].affected[].type`
- `updated_at`

# Database

변경 사항이 없습니다.

# 주의사항

- `mock/` 폴더와 Mock 데이터는 수정하지 않았습니다.
- 영향 가능 구간 수는 각 특보의 `affected` 중 `type === "segment"`인 항목을 합산합니다.
- 같은 실제 구간이 여러 특보 지역에 중복 포함되어도 현재 응답만으로는 고유 구간 여부를 확정할 수 없습니다.

# 변경 이력

2026-07-10

- 발효 특보 종류·등급별 그룹 렌더링 추가
- 다중 지역 요약 및 숨은 지역 툴팁 추가
- 마우스·키보드·터치 접근성 동작 추가

# 다음 작업

- 모든 대시보드 API의 공통 필터 규격 확정
- 필터 옵션 동적 데이터 전환

# 작업 요약

## 완료한 내용

- 모든 발효 특보 그룹 표시
- 동일 특보의 다중 지역 요약
- 숨은 지역 목록 표시 및 자동 닫기
- 특보 없음 상태 유지

## 수정한 파일

- `frontend/dashboard.html`
- `frontend/dashboard.js`
- `frontend/style.css`
- `.docs/Frontend.md`

## 구현 이유

동시에 발효된 특보와 영향 지역을 누락 없이 전달하면서 제한된 배너 공간을 효율적으로 사용하기 위해 구현했습니다.

## 변경 사항

- 단일 특보 마크업을 그룹 목록 컨테이너로 변경
- 특보 그룹화 및 동적 DOM 생성 함수 추가
- 지역 툴팁 스타일과 상호작용 추가

## 새롭게 배운 개념

- Composite Grouping Key
- Progressive Disclosure
- Accessible Tooltip Interaction

## 실무에서는

운영 정책에 영향을 주는 고유 영향 구간 집계는 프론트엔드가 아닌 백엔드에서 안정적인 구간 ID를 기준으로 계산하고, 프론트엔드는 반환된 그룹 데이터를 표시하는 데 집중하는 편이 좋습니다.

## 개선 가능한 부분

- `segment_id`를 이용한 영향 구간 중복 제거
- 브라우저 자동화 기반 hover·focus·touch 회귀 테스트
- 특보 그룹별 상세 화면 연결

## 다음 작업

- 공통 필터 규격 설계 및 확정

## 프로젝트 진행률

■■■■■■■■□□ 80%

완료

- 다중 기상특보 배너 개선

진행 중

- 대시보드 데이터·기능 보완

예정

- 공통 필터 규격 확정
- 동적 필터 데이터 적용
- 실 API 및 오류 처리 전환

## 복습 문제

1. 특보 종류와 등급을 함께 그룹 키로 사용해야 하는 이유는 무엇일까요?
2. 숨은 지역 목록을 CSS hover만으로 구현하면 터치와 키보드 환경에서 어떤 문제가 생길까요?
3. 영향 구간 중복 제거에 안정적인 `segment_id`가 필요한 이유는 무엇일까요?

## 오늘 배운 내용

- 데이터 그룹화
- 점진적 정보 공개
- 접근 가능한 툴팁

## README 반영 여부

기존 대시보드 내부 표시 방식의 변경이므로 README에는 별도 항목을 추가하지 않았습니다.

## 추천 Commit Message

`feat: 대시보드 다중 기상특보 배너 개선`

## Change Log

2026-07-10

- 대시보드에 특보별 지역 요약 및 지역 목록 툴팁 추가

## Timestamp

2026-07-10 16:04:44 (KST)

---


# 대시보드 프론트엔드 공통 필터 규격

# 개요

대시보드의 노선, 특보 종류, 특보 등급, 열차 종류 필터가 동일한 상태 모델과 API 쿼리 규칙을 사용하도록 프론트엔드 공통 규격을 적용했습니다.

# 구현 목적

- 화면마다 달랐던 전체 값 표현을 `all`로 통일합니다.
- Mock 필터링과 향후 실제 API 요청이 같은 필터 객체를 사용하도록 합니다.
- 필터 이름과 API 쿼리 파라미터의 변환을 한 곳에서 관리합니다.

# 구현 내용

- 공통 필터 필드를 `line`, `alertType`, `alertLevel`, `trainType`으로 정의했습니다.
- API 전달값은 `line`, `alert_type`, `alert_level`, `train_type`으로 매핑합니다.
- 전체 조건은 빈 문자열이나 `전체`가 아닌 `all`로 정규화합니다.
- 필터 기본값은 경부선과 모든 조건의 `all`입니다.
- `createDashboardFilterQuery()`가 향후 실제 API에 사용할 공통 쿼리 문자열을 생성합니다.
- 현재 Mock 필터링 함수도 동일한 `all` 판정 함수를 사용합니다.

# 코드 설명

`DEFAULT_DASHBOARD_FILTERS`는 대시보드의 기본 필터 상태를 정의하고, `FILTER_QUERY_PARAM_NAMES`는 화면의 camelCase 필드명을 API의 snake_case 파라미터로 변환합니다. `normalizeDashboardFilters()`는 비어 있거나 기존 한글 `전체` 값이 들어와도 안전하게 `all`로 통일합니다.

장점은 실제 API 전환 시 필터 변환 코드를 다시 만들 필요가 없고 전체 조건 판정이 일관된다는 점입니다. 단점은 현재 Mock 데이터에 열차 종류 필드가 없어 `trainType`이 실제 데이터 결과에는 영향을 주지 않는다는 점입니다. 실무에서는 백엔드도 같은 허용값과 기본값을 검증해야 하지만 이번 작업 범위에서는 프론트엔드 규격만 적용했습니다.

# API

프론트엔드가 생성하는 공통 쿼리 형식은 다음과 같습니다.

```text
line=경부선&alert_type=all&alert_level=all&train_type=all
```

이번 단계에서는 실제 API를 호출하지 않으며 생성된 쿼리를 대시보드 상태에 보관합니다.

# Database

변경 사항이 없습니다.

# 주의사항

- `backend/`, `mock/`, DB 파일은 수정하지 않았습니다.
- 열차 종류는 현재 데이터에 필드가 없어 필터 결과에 적용되지 않습니다.
- 히트맵은 현재 Mock에 특보 종류와 등급 필드가 없어 노선 조건만 적용됩니다.

# 변경 이력

2026-07-10

- 전체 필터 값 `all` 통일
- 공통 필터 정규화 함수 추가
- API 쿼리 파라미터 생성 규격 추가

# 다음 작업

- 특보 종류, 특보 등급, 열차 종류 선택지의 동적 데이터 전환

# 작업 요약

## 완료한 내용

- 공통 필터 상태 모델
- 전체 값 정규화
- 공통 API 쿼리 생성
- 기존 Mock 메모리 필터와 공통 규격 연결

## 수정한 파일

- `frontend/dashboard.html`
- `frontend/dashboard.js`
- `.docs/Frontend.md`

## 구현 이유

필터별로 달랐던 전체 값과 이름 변환을 통일해 실제 API 전환 시 유지보수 비용을 줄이기 위해 구현했습니다.

## 변경 사항

- HTML의 전체 옵션 값을 `all`로 변경
- 공통 기본값과 쿼리명 매핑 추가
- 필터 정규화 및 전체 판정 함수 추가

## 새롭게 배운 개념

- Filter Normalization
- Query Parameter Mapping
- Single Source of Truth

## 실무에서는

프론트엔드와 백엔드가 공통 OpenAPI 계약을 사용하고, 생성된 API 클라이언트나 공유 스키마로 허용값과 기본값을 동기화하는 방식이 안전합니다.

## 개선 가능한 부분

- 백엔드 공통 필터 검증 연동
- URL에 현재 필터 상태 저장
- 열차 종류별 실제 집계 데이터 연결

## 다음 작업

- 필터 선택지 동적 생성

## 프로젝트 진행률

■■■■■■■■□□ 80%

완료

- 다중 기상특보 배너
- 프론트엔드 공통 필터 규격

진행 중

- 필터 데이터 동적화 준비

예정

- 노선도 기준 및 카드 지표 정의
- 실제 API 전환과 오류 처리

## 복습 문제

1. 화면의 `전체` 값을 내부적으로 `all`로 통일하면 어떤 장점이 있을까요?
2. 화면 필드명과 API 쿼리 필드명을 별도 매핑으로 관리하는 이유는 무엇일까요?
3. 현재 열차 종류 필터가 데이터 결과에 영향을 줄 수 없는 이유는 무엇일까요?

## 오늘 배운 내용

- 필터 정규화
- 쿼리 파라미터
- 기본 상태 모델

## README 반영 여부

대시보드 내부 필터 규격 변경이므로 README에는 별도 항목을 추가하지 않았습니다.

## 추천 Commit Message

`refactor: 대시보드 공통 필터 규격 통일`

## Change Log

2026-07-10

- 대시보드 프론트엔드 필터 값 및 API 쿼리 규격 통일

## Timestamp

2026-07-10 16:09:50 (KST)

---


# 대시보드 필터 선택지 동적 생성

# 개요

대시보드의 특보 종류와 특보 등급 선택지를 HTML 고정값이 아니라 현재 로드된 데이터에서 생성하도록 변경했습니다.

# 구현 목적

- 데이터에 존재하는 필터 값만 사용자에게 제공합니다.
- 새로운 특보 종류나 등급이 추가될 때 HTML을 직접 수정하지 않도록 합니다.
- 데이터가 제공되지 않는 열차 종류 필터가 실제로 동작하는 것처럼 보이지 않도록 합니다.

# 구현 내용

- 특보 종류는 로드된 데이터의 `alert_type`, `alert_types` 값을 재귀적으로 수집합니다.
- 특보 등급은 `alert_level`, `alert_levels` 값을 수집합니다.
- 중복값과 빈 문자열을 제거하고 option 요소를 동적으로 생성합니다.
- 특보 등급은 주의보, 경보 순서를 우선합니다.
- 열차 종류는 `train_type`, `train_types`가 제공될 때 자동으로 활성화합니다.
- 현재 Mock에는 열차 종류 데이터가 없으므로 `전체`만 표시하고 선택 상자를 비활성화합니다.
- 데이터 로딩에 실패하면 동적 필터도 전체만 남기고 비활성화합니다.

# 코드 설명

`collectNestedFilterValues()`는 배열과 객체를 순회하며 지정된 단일·목록 필드의 값을 수집합니다. `renderDynamicFilterSelect()`는 중복 제거, 정렬, 전체 옵션 추가, 데이터 부재 시 비활성화를 공통으로 처리합니다.

장점은 현재 응답 구조뿐 아니라 이후 API가 `train_types` 같은 메타데이터를 포함할 때도 같은 렌더링 함수를 재사용할 수 있다는 점입니다. 단점은 전용 필터 메타데이터 API가 없으므로 여러 화면 데이터 응답을 모두 받은 후에야 선택지를 확정할 수 있다는 점입니다. 실무에서는 `/filters` 또는 `/metadata` API에서 허용값과 표시 순서를 제공하는 방식이 더 안정적입니다.

# API

새 API를 호출하지 않습니다. 현재 대시보드가 이미 불러오는 응답의 필터 관련 필드만 사용합니다.

# Database

변경 사항이 없습니다.

# 주의사항

- `backend/`와 `mock/`은 수정하지 않았습니다.
- 체크리스트의 `reason` 문자열에서는 필터 값을 추론하지 않습니다.
- 열차 종류 데이터가 없는 동안 열차 종류 선택 상자는 비활성화됩니다.

# 변경 이력

2026-07-10

- 특보 종류와 등급 option 동적 생성
- 열차 종류 데이터 탐색 및 데이터 없음 상태 추가
- 고정 필터 option 제거

# 다음 작업

- 고속철도 역 목록과 일반 경부선 역 목록 중 화면 기준 확정

# 작업 요약

## 완료한 내용

- 특보 종류 동적 필터
- 특보 등급 동적 필터
- 열차 종류 데이터 없음 처리
- 필터 값 중복 제거와 정렬

## 수정한 파일

- `frontend/dashboard.html`
- `frontend/dashboard.js`
- `.docs/Frontend.md`

## 구현 이유

고정된 선택지와 실제 데이터의 불일치를 제거하고 데이터가 제공될 때 자동으로 필터가 확장되도록 하기 위해 구현했습니다.

## 변경 사항

- HTML 고정 option 제거
- 공통 동적 select 렌더러 추가
- 중첩 데이터 필터값 수집 함수 추가
- 데이터 없는 필터 비활성화

## 새롭게 배운 개념

- Dynamic Filter Metadata
- Recursive Value Collection
- Disabled State

## 실무에서는

필터 허용값, 표시명, 정렬 순서, 지원 여부를 전용 메타데이터 API에서 제공하고 프론트엔드는 해당 계약에 따라 선택지를 렌더링합니다.

## 개선 가능한 부분

- 전용 필터 메타데이터 API 연결
- 필터별 독립 로딩·오류 상태
- 선택 가능한 필터 조합 검증

## 다음 작업

- 대시보드 노선도 기준 데이터 확정

## 프로젝트 진행률

■■■■■■■■□□ 80%

완료

- 공통 필터 규격
- 특보 종류·등급 동적 생성
- 열차 종류 데이터 없음 처리

진행 중

- 노선도 기준 검토 준비

예정

- 카드 지표와 위험도 기준 확정
- 실제 API 및 오류 처리

## 복습 문제

1. 필터 선택지를 화면 데이터에서 동적으로 생성할 때의 장단점은 무엇일까요?
2. 현재 열차 종류 필터를 비활성화한 이유는 무엇일까요?
3. 전용 필터 메타데이터 API가 있으면 어떤 문제가 해결될까요?

## 오늘 배운 내용

- 동적 필터
- 재귀 데이터 탐색
- 비활성화 상태

## README 반영 여부

대시보드 내부 필터 생성 방식 변경이므로 README에는 별도 항목을 추가하지 않았습니다.

## 추천 Commit Message

`feat: 대시보드 필터 선택지 동적 생성`

## Change Log

2026-07-10

- 대시보드 특보 필터 동적 생성 및 열차 필터 데이터 없음 처리

## Timestamp

2026-07-10 16:16:17 (KST)

---


# 대시보드 경부선 고속철도 노선도 기준 확정

# 개요

대시보드 노선도의 화면 기준을 일반 경부선 역 목록이 아닌 경부선 고속철도 정차역 10개와 인접 구간 9개로 확정했습니다.

# 구현 목적

- 대시보드, 역 상세, 구간 상세 화면의 탐색 기준을 일치시킵니다.
- 일반 경부선 역과 고속철도 역을 임의로 대응시켜 잘못된 위험 데이터를 표시하지 않습니다.
- 데이터가 없는 고속철도 역도 안정적인 ID로 상세 화면에 이동하도록 합니다.

# 구현 내용

- 기준 역을 서울, 광명, 천안아산, 오송, 대전, 김천(구미), 동대구, 경주, 울산, 부산으로 확정했습니다.
- 각 기준 역에 `stationId`와 표시명을 함께 정의했습니다.
- 노선도 제목과 접근성 설명에 `고속철도` 범위를 명시했습니다.
- Mock 역명과 기준 역명이 정확히 일치할 때만 취약도를 결합합니다.
- 일치하는 구간만 위험도를 표시하고 나머지는 데이터 없음으로 분류합니다.
- 취약도 데이터가 없는 역도 기준 `stationId`를 사용해 역 상세로 이동합니다.

# 코드 설명

`GYEONGBU_HIGH_SPEED_STATIONS`는 문자열 배열 대신 역 ID와 표시명을 가진 읽기 전용 기준 데이터 배열입니다. `buildHighSpeedRoute()`는 이 순서를 유지하면서 Mock의 node와 edge를 정확한 역명 기준으로 결합합니다.

장점은 세 화면의 기준이 일관되고 다른 역의 데이터를 잘못 대체하지 않는다는 점입니다. 단점은 현재 일반 경부선 Mock과 정확히 일치하지 않는 광명, 천안아산, 오송, 경주, 울산 및 여러 인접 구간이 데이터 없음으로 표시된다는 점입니다. 다른 방법으로 일반 경부선 목록을 사용할 수 있지만 역·구간 상세 화면과 탐색 기준이 달라지므로 적용하지 않았습니다. 실무에서는 노선 메타데이터 API가 역 ID, 정차 순서, 노선 유형을 제공하도록 구성합니다.

# API

변경 사항이 없습니다. 현재 `heatmap` 데이터의 역명과 구간 시작·종료역을 프론트엔드 기준 데이터와 정확히 비교합니다.

# Database

변경 사항이 없습니다.

# 주의사항

- `backend/`와 `mock/`은 수정하지 않았습니다.
- 천안과 천안아산처럼 명칭과 실제 역이 다른 경우 데이터를 대체 사용하지 않습니다.
- 구간 요약은 고속철도 인접 구간 9개를 기준으로 계산합니다.
- TOP 5와 요약 카드의 데이터 범위는 이후 지표 정의 작업에서 별도로 확정합니다.

# 변경 이력

2026-07-10

- 경부선 고속철도 정차역 10개 기준 확정
- 기준 역별 안정적인 station ID 추가
- 노선도 제목 및 접근성 설명 변경

# 다음 작업

- 대시보드 카드별 지표 정의 확정

# 작업 요약

## 완료한 내용

- 고속철도 노선도 기준 데이터
- 정확한 역·구간 데이터 결합
- 데이터 없는 역의 상세 링크 ID
- 화면 범위 명시

## 수정한 파일

- `frontend/dashboard.html`
- `frontend/dashboard.js`
- `.docs/Frontend.md`

## 구현 이유

대시보드와 상세 화면이 동일한 철도 단위를 사용하고 서로 다른 역의 위험 데이터를 혼동하지 않도록 하기 위해 구현했습니다.

## 변경 사항

- 역 문자열 배열을 ID 기반 기준 데이터로 변경
- 고속철도 인접 구간 생성 로직 적용
- 제목과 aria-label에 고속철도 범위 추가

## 새롭게 배운 개념

- Reference Data
- Exact-match Data Join
- Stable Entity Identifier

## 실무에서는

역과 구간을 이름으로 결합하기보다 철도 운영 시스템의 고유 코드를 사용하고, 별도의 노선 메타데이터에서 표시명과 정차 순서를 관리합니다.

## 개선 가능한 부분

- 고속철도 전용 취약도 데이터 연결
- 공통 노선 메타데이터 모듈 분리
- 노선도와 순위표 데이터 범위 통일

## 다음 작업

- 카드별 지표 정의 및 표시 기준 확정

## 프로젝트 진행률

■■■■■■■■□□ 80%

완료

- 공통 필터 및 동적 선택지
- 경부선 고속철도 노선도 기준

진행 중

- 카드 지표 검토 준비

예정

- 위험도 기준과 부족 데이터 처리
- 실제 API 및 오류 처리

## 복습 문제

1. 천안 데이터를 천안아산에 대신 표시하면 안 되는 이유는 무엇일까요?
2. 역 이름과 별도로 안정적인 역 ID를 관리해야 하는 이유는 무엇일까요?
3. 데이터가 없는 상태를 명시적으로 표시하는 것이 잘못된 대체 데이터보다 안전한 이유는 무엇일까요?

## 오늘 배운 내용

- 기준 데이터
- 정확 일치 결합
- 안정적인 식별자

## README 반영 여부

대시보드 노선도 내부 기준 확정이므로 README에는 별도 항목을 추가하지 않았습니다.

## 추천 Commit Message

`refactor: 대시보드 고속철도 노선도 기준 확정`

## Change Log

2026-07-10

- 대시보드 노선도를 경부선 고속철도 10개 역 기준으로 통일

## Timestamp

2026-07-10 16:23:30 (KST)

---


# 대시보드 요약 카드 지표 정의 확정

# 개요

대시보드 요약 카드 4개의 계산 범위와 데이터 원천을 경부선 고속철도 기준으로 통일했습니다.

# 구현 목적

- 서로 다른 성격의 역·구간 데이터를 섞지 않습니다.
- 동일 영향 구간의 중복 집계를 방지합니다.
- 평균 신규 지연 계산에 분석 표본 수를 반영합니다.
- 계산할 수 없는 지표와 전일 비교값을 임의로 추정하지 않습니다.

# 구현 내용

- 영향 가능 구간은 현재 발효 특보의 영향 대상 중 고속철도 인접 구간에 해당하는 고유 구간 수입니다.
- 정방향과 역방향의 같은 구간은 하나로 계산합니다.
- 운행 지연 예상 열차는 제공 데이터가 없어 `-편`, `집계 데이터 없음`으로 표시합니다.
- 평균 지연 카드명을 `평균 신규 지연(예상)`으로 변경했습니다.
- 평균 신규 지연은 고속철도 취약 구간의 `avg_delay_incr`를 `sample_n`으로 가중평균합니다.
- 취약도 높음 구간은 고속철도 인접 구간 중 히트맵 판정이 `높음`인 구간 수입니다.
- 전일 데이터가 없는 카드에는 `전일 비교 데이터 없음`을 표시합니다.

# 코드 설명

`isHighSpeedSegment()`는 두 역이 기준 정차역 목록에서 서로 인접한지 확인합니다. `getSegmentKey()`는 역 순서와 관계없이 같은 구간에 동일한 키를 부여합니다. `getWeightedAverageHighSpeedDelay()`는 각 구간의 평균 신규 지연에 표본 수를 곱한 뒤 전체 표본 수로 나눕니다.

장점은 네 카드의 범위가 고속철도 구간으로 통일되고 표본 크기가 다른 구간을 공정하게 반영한다는 점입니다. 단점은 일반 경부선 Mock 중 고속철도 기준과 일치하지 않는 데이터가 제외되고 예상 지연 열차 및 전일 비교 데이터는 아직 표시할 수 없다는 점입니다. 실무에서는 요약 전용 API가 현재값, 이전값, 차이, 산출 기준 시각을 함께 제공하는 방식이 적합합니다.

# API

새 API를 호출하지 않습니다. 현재 프론트엔드가 읽는 다음 필드를 사용합니다.

- `alerts.active[].affected[].type/from/to`
- `vulnerability_segments.segments[].avg_delay_incr/sample_n/from/to`
- `heatmap.edges[].vuln/from/to`

# Database

변경 사항이 없습니다.

# 주의사항

- `backend/`와 `mock/`은 수정하지 않았습니다.
- 예상 지연 열차 수는 데이터가 제공되기 전까지 추정하지 않습니다.
- 높음 판정 임계값은 다음 위험도 기준 확정 작업에서 최종 검토합니다.

# 변경 이력

2026-07-10

- 고속철도 기준 영향 구간 중복 제거
- 평균 신규 지연 표본 가중평균 적용
- 고위험 구간 히트맵 기준 적용
- 전일 비교 데이터 없음 표시

# 다음 작업

- 취약도 높음·주의·관심 판정 기준 확정

# 작업 요약

## 완료한 내용

- 카드별 데이터 원천 확정
- 고속철도 공통 계산 범위
- 가중평균과 구간 중복 제거
- 데이터 부재 상태 문구

## 수정한 파일

- `frontend/dashboard.html`
- `frontend/dashboard.js`
- `.docs/Frontend.md`

## 구현 이유

요약 카드가 사용자의 운영 판단에 사용될 수 있도록 각 값의 의미와 계산 기준을 명확하게 만들기 위해 구현했습니다.

## 변경 사항

- 평균 지연 카드 제목 변경
- 체크리스트 단순 평균 제거
- 구간 데이터 표본 가중평균 적용
- 고위험 구간 데이터 원천 변경

## 새롭게 배운 개념

- Weighted Average
- Canonical Segment Key
- Metric Definition

## 실무에서는

대시보드 지표의 산식과 데이터 기준 시각을 서버에서 버전 관리하고 프론트엔드는 계산보다 표시와 상태 처리에 집중합니다.

## 개선 가능한 부분

- 요약 전용 API 연결
- 전일 비교 데이터 소비
- 열차별 지연 예상 데이터 연결

## 다음 작업

- 위험도 판정 기준 공통화

## 프로젝트 진행률

■■■■■■■■□□ 80%

완료

- 대시보드 공통 필터
- 고속철도 노선도 기준
- 카드별 지표 정의

진행 중

- 위험도 기준 검토 준비

예정

- 부족 지표 및 표본 부족 표시
- 실제 API 및 오류 처리

## 복습 문제

1. 평균 신규 지연을 단순 평균하지 않고 표본 가중평균해야 하는 이유는 무엇일까요?
2. 역방향 구간을 같은 구간으로 처리하기 위해 정규화된 키가 필요한 이유는 무엇일까요?
3. 예상 지연 열차 수를 기존 데이터로 임의 추정하면 어떤 문제가 생길까요?

## 오늘 배운 내용

- 표본 가중평균
- 구간 정규화
- 지표 산식 정의

## README 반영 여부

대시보드 내부 지표 계산 방식 변경이므로 README에는 별도 항목을 추가하지 않았습니다.

## 추천 Commit Message

`refactor: 대시보드 요약 카드 지표 정의 통일`

## Change Log

2026-07-10

- 대시보드 요약 카드를 고속철도 기준 지표로 변경

## Timestamp

2026-07-10 16:30:20 (KST)

---


# 대시보드 위험도 판정 기준 공통화

# 개요

기존 프론트엔드 문서에 명시된 취약도 점수, 신규 지연 시간, 역 지연율의 위험도 임계값을 대시보드 공통 설정으로 통합했습니다.

# 구현 목적

- 동일한 지표가 화면 영역마다 다른 등급으로 표시되지 않도록 합니다.
- 단위가 다른 취약도 점수, 지연 시간, 지연율을 각각 올바른 기준으로 판정합니다.
- 코드에 흩어진 Magic Number를 제거하고 정책 변경 지점을 한 곳으로 모읍니다.

# 구현 내용

- 취약도 점수는 높음 0.70 이상, 주의 0.50 이상, 그 미만 관심으로 판정합니다.
- 신규 지연은 높음 12분 이상, 주의 7분 이상, 그 미만 관심으로 판정합니다.
- 역 지연율은 높음 0.40 이상, 주의 0.25 이상, 그 미만 관심으로 판정합니다.
- 숫자가 아니거나 값이 없으면 데이터 없음으로 판정합니다.
- 노선도, 구간 요약, 고위험 카드에는 취약도 점수 기준을 사용합니다.
- 취약 구간 순위와 우선 점검 대상에는 신규 지연 기준을 사용합니다.
- 취약 역 순위에는 역 지연율 기준을 사용합니다.

# 코드 설명

`RISK_THRESHOLDS`는 지표별 높음과 주의 임계값을 읽기 전용 객체로 관리합니다. `getRiskLevel(value, thresholds)`는 숫자 유효성을 확인한 뒤 전달받은 기준에 따라 `high`, `warning`, `interest`, `none`을 반환합니다.

장점은 판정 로직이 하나로 통합되고 지표별 기준이 명시적으로 드러난다는 점입니다. 단점은 현재 값들이 프론트엔드 표시 정책이므로 공식 분석 기준이 변경되면 설정을 함께 갱신해야 한다는 점입니다. 다른 구현 방법으로 API가 계산된 위험도 코드와 기준 버전을 직접 제공할 수 있으며, 실무에서는 운영 정책의 일관성을 위해 이 방식이 더 적합합니다.

# API

변경 사항이 없습니다. 기존 응답의 `vuln`, `avg_delay_incr`, `delay_rate` 값을 사용합니다.

# Database

변경 사항이 없습니다.

# 주의사항

- 이번 임계값은 기존 `.docs/Frontend.md`에 기록된 프론트엔드 정책을 그대로 사용했습니다.
- `CONTRACT.md`는 지표의 단위와 의미만 정의하며 위험도 임계값은 정의하지 않습니다.
- `backend/`와 `mock/`은 수정하지 않았습니다.

# 변경 이력

2026-07-10

- 위험도 임계값 객체 중앙화
- 지표별 공통 위험도 판정 함수 적용
- 취약 역 순위에 지연율 전용 기준 적용

# 다음 작업

- 지연 건수, 전일 대비, 예상 지연 열차 수 데이터 처리

# 작업 요약

## 완료한 내용

- 취약도 점수 판정 기준
- 신규 지연 판정 기준
- 역 지연율 판정 기준
- 대시보드 전체 위험 배지 공통 함수

## 수정한 파일

- `frontend/dashboard.js`
- `.docs/Frontend.md`

## 구현 이유

서로 다른 단위의 지표를 구분하면서 동일한 위험도 라벨과 색상을 일관되게 제공하기 위해 구현했습니다.

## 변경 사항

- 위험도 관련 Magic Number 제거
- 세 지표별 임계값 설정 추가
- 노선도·카드·순위·점검표 판정 함수 교체

## 새롭게 배운 개념

- Threshold Policy
- Metric-specific Classification
- Configuration Centralization

## 실무에서는

위험도 기준을 분석 또는 정책 서버에서 버전과 함께 관리하고 API 응답에 계산된 등급과 기준 버전을 포함해 화면과 보고서가 같은 정책을 사용하도록 합니다.

## 개선 가능한 부분

- 공식 운영 기준과 임계값 검증
- 기준 버전 표시
- 상세 화면과 공통 설정 모듈 공유

## 다음 작업

- 부족한 요약 및 비교 데이터의 프론트엔드 처리 설계

## 프로젝트 진행률

■■■■■■■■□□ 80%

완료

- 카드 지표 정의
- 위험도 판정 기준 공통화

진행 중

- 부족 데이터 처리 준비

예정

- 표본 부족 및 전체 보기 동작
- 실제 API와 오류 처리

## 복습 문제

1. 취약도 점수와 역 지연율에 서로 다른 임계값을 사용해야 하는 이유는 무엇일까요?
2. 임계값을 하나의 설정 객체로 관리하면 어떤 장점이 있을까요?
3. 위험도 기준에 버전 정보가 필요한 이유는 무엇일까요?

## 오늘 배운 내용

- 임계값 정책
- 지표별 위험도 분류
- 설정 중앙화

## README 반영 여부

기존 대시보드 내부 판정 기준 정리이므로 README에는 별도 항목을 추가하지 않았습니다.

## 추천 Commit Message

`refactor: 대시보드 위험도 판정 기준 공통화`

## Change Log

2026-07-10

- 대시보드 위험도 판정 기준을 지표별 공통 설정으로 통합

## Timestamp

2026-07-10 16:37:43 (KST)

---


# 대시보드 부족 집계 데이터 처리

# 개요

현재 프론트엔드 데이터로 계산 가능한 역 지연 건수를 올바르게 표시하고, 전일 비교와 예상 지연 열차 수는 실제 선택적 필드가 제공될 때만 표시하도록 준비했습니다.

# 구현 목적

- 취약 역 테이블에 표본 수가 지연 건수로 잘못 표시되는 문제를 수정합니다.
- 데이터가 없는 예상 지연 열차 수와 전일 비교값을 임의로 생성하지 않습니다.
- 향후 실제 API가 선택적 집계 필드를 제공하면 화면이 바로 사용할 수 있도록 합니다.

# 구현 내용

- 역 데이터에 `delay_count`가 있으면 정확한 지연 건수로 우선 표시합니다.
- `delay_count`가 없으면 `sample_n × delay_rate`를 반올림해 `약 N건`으로 표시합니다.
- 테이블 열 제목을 `지연 건수(추정)`으로 변경했습니다.
- `expected_delayed_train_count`가 있으면 예상 지연 열차 수로 표시합니다.
- 열차 배열만 있으면 `run_date + train_no`로 중복 제거해 편수를 계산합니다.
- 전일값이 있으면 현재값과의 차이를 계산해 증가, 감소, 동일 상태를 표시합니다.
- 전일값이 없으면 `전일 비교 데이터 없음`을 유지합니다.

# 코드 설명

`getSummaryContainers()`는 각 응답의 `dashboard_summary`, `summary`, 최상위 객체를 선택적 집계 데이터 후보로 사용합니다. `formatDayOverDayComparison()`은 현재값과 이전값이 모두 숫자인 경우에만 차이를 계산합니다. `getExpectedDelayedTrainCount()`는 직접 집계값을 우선하고 열차 목록이 제공될 때만 고유 편수를 계산합니다.

장점은 없는 데이터를 추정하지 않으면서 향후 응답 확장을 수용할 수 있다는 점입니다. 역 지연 건수는 문서에 정의된 `delay_rate = 지연 건수 / 표본 수` 관계를 활용할 수 있습니다. 단점은 반올림된 지연율을 이용한 값이므로 실제 원본 건수와 차이가 날 수 있고, 선택적 요약 필드는 백엔드 계약이 확정되기 전까지 동작을 준비한 상태라는 점입니다. 실무에서는 서버가 정확한 `delay_count`와 요약 지표를 직접 제공해야 합니다.

# API

새 API를 호출하지 않습니다. 향후 다음 선택적 필드를 소비할 수 있습니다.

- `delay_count`
- `expected_delayed_train_count`
- `expected_delayed_trains[].run_date/train_no`
- `dashboard_summary` 또는 `summary`의 지표별 `previous`

# Database

변경 사항이 없습니다.

# 주의사항

- `backend/`와 `mock/`은 수정하지 않았습니다.
- 현재 예상 지연 열차 수와 전일 비교값은 데이터가 없어 기존 빈 상태로 표시됩니다.
- `약 N건`은 실제 지연 건수가 아닌 반올림된 추정값입니다.

# 변경 이력

2026-07-10

- 취약 역 지연 건수 오표시 수정
- 전일 비교 표시 함수 추가
- 예상 지연 열차 선택적 데이터 처리 추가

# 다음 작업

- 표본 부족 표시

# 작업 요약

## 완료한 내용

- 역 지연 건수 추정 표시
- 정확한 지연 건수 우선 처리
- 전일 비교 표시 규칙
- 예상 지연 열차 선택적 처리

## 수정한 파일

- `frontend/dashboard.html`
- `frontend/dashboard.js`
- `.docs/Frontend.md`

## 구현 이유

잘못 표시된 지표를 수정하고 데이터가 실제로 제공될 때만 운영 판단용 숫자를 표시하기 위해 구현했습니다.

## 변경 사항

- 표본 수 대신 지연 건수 계산값 표시
- 추정값 문구 추가
- 선택적 요약 데이터 탐색 및 비교 함수 추가

## 새롭게 배운 개념

- Derived Metric
- Optional Data Contract
- Day-over-Day Comparison

## 실무에서는

지연 건수와 전일 비교는 원본 정수 집계와 동일한 기준 시각을 서버에서 제공하고 프론트엔드는 계산된 결과와 데이터 상태만 표시합니다.

## 개선 가능한 부분

- 정확한 `delay_count` 연결
- 요약 API 계약 확정
- 기준일과 집계 시각 표시

## 다음 작업

- 표본 수 10건 미만 근거 부족 표시

## 프로젝트 진행률

■■■■■■■■□□ 80%

완료

- 지연 건수 표시 수정
- 선택적 전일 비교와 예상 열차 처리

진행 중

- 표본 부족 처리 준비

예정

- 전체 보기 및 실제 API 전환
- 오류·재시도 처리

## 복습 문제

1. 표본 수를 지연 건수로 직접 표시하면 안 되는 이유는 무엇일까요?
2. 반올림된 지연율로 계산한 값에 `약`을 표시해야 하는 이유는 무엇일까요?
3. 열차 편수를 셀 때 운행일과 열차 번호를 함께 사용해야 하는 이유는 무엇일까요?

## 오늘 배운 내용

- 파생 지표
- 선택적 응답 필드
- 전일 비교

## README 반영 여부

대시보드 내부 데이터 표시 개선이므로 README에는 별도 항목을 추가하지 않았습니다.

## 추천 Commit Message

`fix: 대시보드 부족 집계 데이터 처리`

## Change Log

2026-07-10

- 역 지연 건수 추정 표시 및 선택적 요약 데이터 처리 추가

## Timestamp

2026-07-10 16:42:56 (KST)

---


# 대시보드 기상 취약도 안내 아이콘 제거

# 개요

별도 안내 기능을 구현하지 않기로 결정한 대시보드 기상 취약도 카드의 `i` 아이콘을 제거했습니다.

# 구현 목적

동작하지 않는 안내 요소를 화면에서 제거해 사용자가 클릭 가능한 기능으로 오해하지 않도록 합니다.

# 구현 내용

- 기상 취약도 카드 제목 옆의 `map-card__info` 마크업을 제거했습니다.
- 해당 아이콘에서만 사용하던 CSS를 제거했습니다.
- 카드 제목과 노선도 데이터 렌더링은 그대로 유지했습니다.

# 코드 설명

기능이 연결되지 않은 장식 요소와 전용 스타일만 제거했습니다. 장점은 화면 의미가 명확해지고 사용하지 않는 CSS가 남지 않는다는 점입니다. 단점은 추후 안내 기능이 필요해지면 실제 팝오버 또는 도움말과 함께 UI를 다시 설계해야 한다는 점입니다. 실무에서는 상호작용을 암시하는 아이콘은 실제 동작과 접근 가능한 설명이 준비된 경우에만 제공합니다.

# API

변경 사항이 없습니다.

# Database

변경 사항이 없습니다.

# 주의사항

- 노선도 제목과 접근성 라벨은 유지했습니다.
- `backend/`와 `mock/`은 수정하지 않았습니다.
- 표본 부족 표시와 전체 보기 작업은 사용자 요청으로 보류했습니다.

# 변경 이력

2026-07-10

- 기상 취약도 카드 안내 `i` 아이콘 및 전용 CSS 제거

# 다음 작업

- Mock 호출을 실제 API 호출로 전환

# 작업 요약

## 완료한 내용

- 기능 없는 안내 아이콘 제거
- 사용하지 않는 전용 스타일 제거

## 수정한 파일

- `frontend/dashboard.html`
- `frontend/style.css`
- `.docs/Frontend.md`
- `.docs/Dashboard_Change_Spec.md`

## 구현 이유

동작하지 않는 UI가 사용자에게 잘못된 기능 기대를 만들지 않도록 제거했습니다.

## 변경 사항

- 안내 아이콘 DOM 삭제
- `map-card__info` CSS 삭제

## 새롭게 배운 개념

- Dead UI Removal
- Orphan CSS Cleanup

## 실무에서는

도움말 아이콘을 제공할 때는 키보드 접근, 화면 낭독기 설명, 모바일 동작까지 포함한 팝오버를 함께 구현합니다.

## 개선 가능한 부분

- 추후 실제 도움말 요구사항 발생 시 접근 가능한 팝오버 설계

## 다음 작업

- 실제 API 전환 설계

## 프로젝트 진행률

■■■■■■■■□□ 80%

완료

- 기상 취약도 안내 아이콘 제거

진행 중

- 실제 API 전환 준비

예정

- 로딩·부분 오류·재시도 처리

## 복습 문제

1. 동작하지 않는 아이콘을 화면에 남겨두면 어떤 사용자 경험 문제가 생길까요?
2. HTML 요소를 제거할 때 전용 CSS도 함께 제거해야 하는 이유는 무엇일까요?
3. 실제 도움말 팝오버에는 어떤 접근성 동작이 필요할까요?

## 오늘 배운 내용

- 기능 없는 UI 제거
- CSS 정리

## README 반영 여부

대시보드 내부 장식 요소 제거이므로 README에는 별도 항목을 추가하지 않았습니다.

## 추천 Commit Message

`chore: 대시보드 기상 취약도 안내 아이콘 제거`

## Change Log

2026-07-10

- 대시보드 기상 취약도 카드의 기능 없는 안내 아이콘 제거

## Timestamp

2026-07-10 16:52:44 (KST)

---

## Timestamp

2026-07-10 17:11:58 KST

---

# 개요

우선 점검 대상 테이블에서 중복 정보인 `대응 권고` 열을 제거하고, 남은 열의 너비를 정보량에 맞게 조정했습니다.

# 구현 목적

주요 위험 설명에 더 넓은 공간을 제공하고, 사용자가 위험도·대상·기상특보·주요 위험·상세 동작에 집중할 수 있도록 테이블의 정보 밀도를 개선합니다.

# 구현 내용

- 테이블 헤더와 데이터 행에서 `대응 권고` 열 제거
- 상세 패널에서 `대응 권고` 항목 제거
- 더 이상 사용하지 않는 `getInspectionRecommendation()` 함수 제거
- 빈 상태 행의 열 병합 수를 6에서 5로 변경
- 열 너비를 위험도 12%, 대상 구간 25%, 기상특보 16%, 주요 위험 35%, 상세 12%로 조정
- 테이블 최소 너비를 1040px에서 800px로 조정

# 코드 설명

`table-layout: fixed`를 유지하면서 각 열에 백분율 너비를 적용했습니다. 전체 비율의 합을 100%로 맞춰 카드 너비가 변해도 열 간 상대적인 공간 배분이 유지됩니다. 가장 긴 텍스트가 들어가는 주요 위험 열에 35%를 배정하고, 배지와 버튼처럼 너비가 일정한 열은 각각 12%로 제한했습니다.

장점은 고정 픽셀 방식보다 카드 너비 변화에 유연하고 불필요한 가로 스크롤이 줄어든다는 점입니다. 단점은 800px보다 좁은 화면에서는 가독성을 지키기 위해 기존처럼 가로 스크롤이 발생한다는 점입니다. 다른 구현 방법으로는 `<colgroup>`을 사용할 수 있으며, 열 정의를 HTML에 명시해야 하는 복잡성이 있어 현재 CSS 구조를 유지했습니다. 실무에서는 실제 데이터의 최대·평균 길이와 지원 화면 너비를 기준으로 열 비율을 정하고 시각 회귀 테스트로 검증합니다.

# API

API 요청 및 응답 형식 변경은 없습니다.

# Database

Database 변경은 없습니다.

# 주의사항

- 우선 점검 대상의 위험도 계산, 대상 상세 링크, 상세보기 선택 동작은 기존과 동일합니다.
- 백엔드 계약 테스트의 기존 실패 2건은 이번 프런트엔드 변경 범위에 포함하지 않았습니다.

# 변경 이력

2026-07-13

- 우선 점검 대상 대응 권고 열 및 상세 항목 제거
- 우선 점검 대상 테이블을 5열 비율 구조로 변경

# 다음 작업

- 실제 브라우저에서 800px 경계와 모바일 가로 스크롤 시각 검수

# 작업 요약

## 완료한 내용

- 대응 권고 표시 및 미사용 생성 함수 제거
- 5열 기준 레이아웃과 빈 상태 접근 구조 정리
- JavaScript 문법 및 잔여 참조 검사

## 수정한 파일

- `frontend/dashboard.html`
- `frontend/dashboard.js`
- `frontend/style.css`
- `.docs/Frontend_Dashboard.md`

## 구현 이유

중복된 권고 문구를 제거하고 주요 위험 정보의 가독성을 높이기 위해 변경했습니다.

## 변경 사항

- 테이블 열 수: 6개 → 5개
- 테이블 최소 너비: 1040px → 800px
- 주요 위험 열 너비: 전체의 35%

## 새롭게 배운 개념

- 고정 테이블 레이아웃에서 백분율 기반 열 배분
- 열 삭제 시 헤더·본문·빈 상태 `colspan`을 함께 동기화하는 방법

## 실무에서는

운영 테이블의 열을 제거할 때는 정상 데이터뿐 아니라 로딩·빈 상태·오류 상태의 열 수와 접근성 속성까지 함께 점검합니다.

## 개선 가능한 부분

- Playwright 등의 시각 회귀 테스트 추가
- 긴 주요 위험 문구에 대한 줄바꿈 정책 검토

## 다음 작업

- 브라우저 시각 검수 후 필요하면 화면 너비별 비율 미세 조정

## 프로젝트 진행률

■■■■■■■■■■ 100%

완료

- 대응 권고 제거
- 5열 비율 조정
- 정적 검사 및 문서화

진행 중

- 없음

예정

- 브라우저 시각 회귀 테스트 자동화

## 복습 문제

1. 테이블 열을 제거할 때 빈 상태 행의 `colspan`도 변경해야 하는 이유는 무엇일까요?
2. `table-layout: fixed`에서 백분율 너비를 사용하면 어떤 장점이 있을까요?
3. 주요 위험 열에 가장 큰 비율을 배정한 이유는 무엇일까요?

## 오늘 배운 내용

- 백분율 기반 테이블 열 배분
- 미사용 UI 로직 정리
- 빈 상태 테이블 구조 동기화

## README 반영 여부

대시보드 내부 표시 구조 변경이며 새로운 기능이나 실행 방법 변화가 없어 README 수정은 필요하지 않습니다.

## 추천 Commit Message

`refactor: 우선 점검 대상 대응 권고 제거 및 열 비율 조정`

## Change Log

2026-07-13

- 우선 점검 대상 대응 권고 제거
- 위험도 12%, 대상 구간 25%, 기상특보 16%, 주요 위험 35%, 상세 12% 적용

## Timestamp

2026-07-13 10:34:30 (KST)

---

# 개요

모든 실행 페이지에서 사용자에게 노출되는 `취약`, `취약도` 용어를 각각 `위험`, `위험도`로 통일했습니다.

# 구현 목적

동일한 위험 지표를 화면마다 다르게 표현하지 않도록 용어를 통일해 사용자의 이해와 화면 일관성을 높입니다.

# 구현 내용

- 대시보드 요약 카드, 노선 현황, 구간·역 순위의 표시 문구 변경
- 빈 데이터 안내와 `aria-label`, 스크린 리더 전용 설명 변경
- API/Mock 안내 페이지의 제목, 범례, 데이터 설명 변경
- FastAPI OpenAPI 문서 제목 변경
- 메인 대시보드 디자인 가이드의 표시 용어 변경
- 내부 API 경로, DB 테이블, Mock 파일명, 응답 필드는 호환성을 위해 유지

# 코드 설명

정적 문구는 HTML에서, 필터나 데이터 상태에 따라 달라지는 문구는 JavaScript에서 변경했습니다. 접근성 트리에서도 같은 용어가 사용되도록 `aria-label`, 표 `caption`, 스크린 리더 전용 제목을 함께 수정했습니다.

장점은 시각 사용자와 보조 기술 사용자 모두 동일한 용어를 경험한다는 점입니다. 단점은 내부 식별자에는 기존 `vulnerability` 용어가 남아 화면 용어와 코드 용어가 다르다는 점입니다. 다른 방법은 API와 DB까지 전면 변경하는 것이지만 Breaking Change가 발생합니다. 실무에서는 표시 용어와 기술 식별자를 분리하고, 외부 계약 변경은 별도 버전 마이그레이션으로 진행합니다.

# API

- `/vulnerability/segments`, `/vulnerability/stations` 경로는 변경하지 않았습니다.
- FastAPI 문서 제목만 `경부선 기상 위험구간 API`로 변경했습니다.
- 요청 및 응답 스키마 변경은 없습니다.

# Database

`station_vulnerability`, `segment_vulnerability` 테이블명과 스키마는 변경하지 않았습니다.

# 주의사항

- 코드의 `vulnerability`, `vuln` 식별자는 외부 계약과 연결되므로 그대로 유지합니다.
- 일반적인 약점을 뜻하는 문서 표현인 `변경에 취약하다`는 위험 지표 용어가 아니므로 일괄 치환하지 않습니다.

# 변경 이력

2026-07-13

- 사용자 노출 용어를 취약/취약도에서 위험/위험도로 통일

# 다음 작업

- 향후 외부 API 버전 변경 시 기술 식별자 개편 여부 검토

# 작업 요약

## 완료한 내용

- 모든 실행 페이지의 사용자 노출 문구 변경
- 동적 빈 상태와 접근성 문구 변경
- API 문서 제목 및 디자인 가이드 동기화
- JavaScript와 Python 문법 검사

## 수정한 파일

- `frontend/dashboard.html`
- `frontend/dashboard.js`
- `frontend/MAIN_DASHBOARD_DESIGN_GUIDE.md`
- `index.html`
- `backend/api.py`
- `.docs/Frontend_Dashboard.md`

## 구현 이유

사용자가 위험 수준을 해석할 때 하나의 일관된 용어를 사용하도록 하기 위해 변경했습니다.

## 변경 사항

- `취약도` → `위험도`
- `취약 구간` → `위험 구간`
- `취약 역` → `위험 역`
- 내부 기술 계약은 변경하지 않음

## 새롭게 배운 개념

- 표시 용어와 기술 식별자의 분리
- 접근성 문구를 포함한 UI 용어 일관성

## 실무에서는

서비스 용어 변경 시 화면 텍스트뿐 아니라 빈 상태, 오류 메시지, 접근성 이름, 브라우저 제목, API 문서까지 함께 검색합니다.

## 개선 가능한 부분

- UI 문구를 다국어 리소스 또는 상수로 중앙화
- 용어 사전을 기반으로 한 자동 검증 추가

## 다음 작업

- 브라우저에서 대시보드와 API 안내 페이지의 최종 문구 검수

## 프로젝트 진행률

■■■■■■■■■■ 100%

완료

- 실행 페이지 용어 통일
- 접근성 문구 통일
- 문서화와 정적 검사

진행 중

- 없음

예정

- UI 문구 중앙화 검토

## 복습 문제

1. 화면 용어 변경 시 `aria-label`도 함께 변경해야 하는 이유는 무엇일까요?
2. API 경로의 `vulnerability`를 유지한 이유는 무엇일까요?
3. 사용자 표시 용어와 내부 기술 식별자를 분리하면 어떤 장점이 있을까요?

## 오늘 배운 내용

- UI 용어 일관성
- 접근 가능한 이름
- Breaking Change 회피

## README 반영 여부

실행 방법이나 기능 추가가 아닌 표시 용어 변경이므로 README 수정은 필요하지 않습니다.

## 추천 Commit Message

`refactor: 전체 페이지 취약도 용어를 위험도로 통일`

## Change Log

2026-07-13

- 모든 실행 페이지의 취약/취약도 노출 문구를 위험/위험도로 변경

## Timestamp

2026-07-13 10:45:00 (KST)
