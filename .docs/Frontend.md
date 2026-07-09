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

















