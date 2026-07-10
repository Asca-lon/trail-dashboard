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

# 역 상세 화면 작업 요약

## 완료한 내용

- `STATION_DETAIL_DESIGN_GUIDE.md` 기준의 역 상세 화면을 추가했습니다.
- 메인 대시보드와 동일한 오버레이 사이드바 구조를 재사용했습니다.
- 메뉴 버튼 클릭 시 사이드바가 화면 위에 표시되도록 `sidebar.js`를 연결했습니다.
- Global Header, Breadcrumb, Page Title, Station Information Header를 구현했습니다.
- 주요 지표 카드 4개를 구현했습니다.
- 시간대별 평균 지연 시간 라인 차트와 특보 발생 시/평상시 평균 지연 비교 차트를 구현했습니다.
- 특보별 영향 통계 테이블과 과거 주요 사례 카드를 구현했습니다.
- 필요한 Lucide 계열 SVG 아이콘 에셋을 `frontend/assets/icons/`에 추가했습니다.
- 사이드바 토글 버튼의 깨진 접근성 라벨을 정상 한글 문구로 수정했습니다.

## 수정한 파일

- `frontend/station-detail.html`
- `frontend/style.css`
- `frontend/sidebar.js`
- `frontend/assets/icons/bell.svg`
- `frontend/assets/icons/chevron-down.svg`
- `frontend/assets/icons/chevron-right.svg`
- `frontend/assets/icons/arrow-left.svg`
- `frontend/assets/icons/trending-up.svg`
- `frontend/assets/icons/percent.svg`
- `frontend/assets/icons/cloud-rain.svg`
- `frontend/assets/icons/wind.svg`
- `frontend/assets/icons/snowflake.svg`
- `frontend/assets/icons/sun.svg`
- `frontend/assets/icons/circle-info.svg`
- `.docs/Frontend.md`

## 구현 이유

역 상세 화면은 메인 대시보드에서 특정 역을 선택한 뒤 기상 영향과 운행 리스크를 더 자세히 확인하는 화면입니다.

메인 대시보드와 같은 디자인 토큰, 카드 스타일, 사이드바 방식을 유지해야 전체 서비스가 하나의 제품처럼 보입니다.

## 변경 사항

- 신규 페이지 `station-detail.html`을 추가했습니다.
- 사이드바 메뉴에서 `역 상세` 항목을 현재 페이지로 표시했습니다.
- 고정 사이드바가 아니라 메뉴 버튼을 눌렀을 때 나타나는 오버레이 사이드바를 유지했습니다.
- 역 정보 카드에 역명, 노선 배지, 주소, 역 변경 버튼, 현재 위험도 박스를 배치했습니다.
- 주요 지표 카드의 값, 단위, 전일 대비 증감값을 디자인 이미지와 동일한 구조로 배치했습니다.
- 차트는 별도 라이브러리 없이 HTML/SVG/CSS로 구현했습니다.
- 반응형에서는 카드와 차트가 한 줄에서 두 줄, 한 줄 세로 배치로 자연스럽게 전환되도록 했습니다.

## 테스트 방법

1. JavaScript 문법 검사

```bash
node --check frontend/sidebar.js
```

예상 결과: 오류 메시지가 없어야 합니다.

2. 로컬 서버 실행

```bash
python -m http.server 8765 --bind 127.0.0.1
```

브라우저에서 아래 주소로 접속합니다.

```text
http://127.0.0.1:8765/frontend/station-detail.html
```

3. 검증 기준

- 상단 메뉴 버튼을 누르면 사이드바가 기존 콘텐츠 위에 표시됩니다.
- 사이드바에서 `역 상세` 메뉴가 활성화되어 보입니다.
- 역 정보 카드에 `대전역`, `경부선`, `현재 위험도: 높음`이 표시됩니다.
- 주요 지표 카드 4개가 데스크톱에서 한 줄로 표시됩니다.
- 좁은 화면에서는 주요 지표, 차트, 하단 카드가 줄바꿈되어 겹치지 않습니다.
- `Escape` 키 또는 사이드바 접기 버튼으로 사이드바가 닫힙니다.

## 새롭게 배운 개념

- 상세 화면 레이아웃 분리
- 오버레이 사이드바 재사용
- 정적 SVG 차트 구현
- 반응형 카드 래핑
- 접근성 라벨 관리

## 실무에서는

실무에서는 역 상세 화면의 지표와 차트 데이터를 정적 HTML에 직접 넣기보다 `/stations/{stationId}/summary`, `/stations/{stationId}/charts`, `/stations/{stationId}/cases` 같은 API로 분리해 가져오는 편이 유지보수에 유리합니다.

차트는 요구사항이 커지면 Chart.js, ECharts, Recharts 같은 검증된 라이브러리를 도입하고, 지금처럼 디자인 검증 단계에서는 정적 구조로 빠르게 화면을 맞춘 뒤 데이터 연결 단계에서 컴포넌트화하는 방식도 많이 사용합니다.

## 개선 가능한 부분

- 역 변경 버튼 동작 설계
- 실제 역 상세 mock/API 데이터 연결
- 차트 데이터 동적 렌더링
- 브라우저 기반 시각 회귀 테스트 추가
- 사이드바 메뉴 링크 전체 페이지 연결

## 다음 작업

- 역 상세 화면 실제 브라우저 시각 검수
- 역 상세 mock 데이터 설계
- 역 변경 플로우 또는 검색 모달 설계

## 복습 문제

1. 오버레이 사이드바를 여러 페이지에서 재사용하려면 HTML과 JS를 어떻게 분리하는 것이 좋을까요?
2. 정적 SVG 차트와 차트 라이브러리의 장단점은 무엇일까요?
3. 상세 화면의 지표 데이터를 API로 분리할 때 어떤 단위의 엔드포인트가 적절할까요?

## 오늘 배운 내용

- 상세 페이지 시맨틱 구조
- Flexbox 기반 반응형 카드 레이아웃
- SVG 기반 정적 차트
- 사이드바 접근성 상태 문구

## Change Log

2026-07-09

- 역 상세 화면 `frontend/station-detail.html` 추가
- 역 상세 전용 CSS 스타일 추가
- 역 상세 화면용 SVG 아이콘 추가
- 사이드바 접근성 라벨 한글 깨짐 수정

## Timestamp

2026-07-09 11:11:38 (KST)

---

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

# 역 상세 헤더 오른쪽 영역 제거 작업 요약

## 완료한 내용

- 역 상세 화면의 `station-global-header__right` 영역을 제거했습니다.
- 데이터 기준, 알림 버튼, 사용자 정보와 관련된 HTML 마크업을 삭제했습니다.
- 해당 영역에만 사용되던 CSS 클래스들을 삭제했습니다.
- 모바일 미디어쿼리에 남아 있던 관련 스타일도 제거했습니다.

## 수정한 파일

- `frontend/station-detail.html`
- `frontend/style.css`
- `.docs/Frontend.md`

## 구현 이유

역 상세 화면 헤더에서는 메뉴 버튼만 유지하고, 오른쪽 사용자/데이터 기준 영역은 표시하지 않도록 하기 위해 제거했습니다.

## 변경 사항

- `station-global-header__right` 마크업 삭제
- `station-global-header__timestamp` 스타일 삭제
- `station-global-header__icon-button` 스타일 삭제
- `station-global-header__user`, `station-global-header__avatar`, `station-global-header__chevron` 스타일 삭제

## 테스트 방법

```bash
rg -n "station-global-header__right|station-global-header__timestamp|station-global-header__icon-button|station-global-header__user|station-global-header__avatar|station-global-header__chevron" frontend/station-detail.html frontend/style.css
```

예상 결과: 검색 결과가 없어야 합니다.

## Change Log

2026-07-09

- 역 상세 화면 헤더 오른쪽 영역 제거

## Timestamp

2026-07-09 11:40:00 (KST)

---

# 역 상세 Mock 데이터 연결 계획

## 개요

역 상세 화면 `frontend/station-detail.html`에 `mock/station_details.json`과 `mock/vulnerability_stations.json` 데이터를 연결합니다.

## 구현 목적

정적 HTML에 직접 작성된 역명, 위험도, 주요 지표 값을 mock 데이터 기준으로 렌더링하여 실제 API 전환이 쉬운 구조로 만듭니다.

## 구현 내용

이번 1차 범위는 역 상세 상단 영역입니다.

- 역 정보 카드
- 현재 위험도 박스
- 주요 지표 카드 4개

## 코드 설명

신규 `frontend/station-detail.js`를 생성해 역 상세 데이터만 독립적으로 관리합니다.

`station-detail.js`는 다음 mock 파일을 불러옵니다.

- `mock/station_details.json`
- `mock/vulnerability_stations.json`

## API

이번 작업에서는 실제 API를 직접 연결하지 않습니다.

향후 전환 예상 API:

- `GET /stations/{stationId}/detail`
- `GET /vulnerability/stations`

## Database

이번 작업에서는 Database 변경이 없습니다.

## 주의사항

- `station_details.json`에는 역 주소가 없으므로 기존 정적 주소를 유지합니다.
- `station_details.json`에는 현재 위험도 필드가 없으므로 `vulnerability_stations.json`의 `delay_rate` 기준으로 계산합니다.
- `station_details.json`에는 전일 대비 증감값이 없으므로 지표 카드의 비교 문구는 mock 기준 설명으로 대체합니다.

## Mock 데이터 매핑

| 화면 영역 | Mock 파일 | 주요 필드 | 렌더링 내용 | 비어 있을 때 처리 |
|---|---|---|---|---|
| 역명 | `mock/station_details.json` | `station` | `대전역` | `역 정보 없음` |
| 노선 배지 | `mock/vulnerability_stations.json` | `line` | `경부선` | `노선 정보 없음` |
| 주소 | 기존 HTML | 정적 문구 | `대전광역시 동구 중앙로 215` | 기존 문구 유지 |
| 현재 위험도 | `mock/vulnerability_stations.json` | `stations[].delay_rate` | 높음/주의/관심 | `정보 없음` |
| 위험도 설명 | `mock/vulnerability_stations.json` | `alert_type`, `alert_level` | `폭염 경보 기준` | `기준 정보 없음` |
| 평균 지연 시간 | `mock/vulnerability_stations.json` | `stations[].avg_delay` | `12.7분` | `-분` |
| 평균 지연 증가량 | `mock/vulnerability_stations.json` | `stations[].delta_delay` | `+8.9분` | `-분` |
| 지연률 | `mock/vulnerability_stations.json` | `stations[].delay_rate` | `44.0%` | `-%` |
| 운행 중단률 | `mock/vulnerability_stations.json` | `stations[].stop_rate` | `1.0%` | `-%` |

## 위험도 기준

| 기준 데이터 | 관심 | 주의 | 높음 |
|---|---:|---:|---:|
| `delay_rate` | 0.00 이상 0.25 미만 | 0.25 이상 0.40 미만 | 0.40 이상 |

## 다음 작업

- `frontend/station-detail.js` 생성
- `station-detail.html`에 렌더링 대상 `data-*` 속성 추가
- 역 정보와 주요 지표 카드 mock 연결
- JavaScript 문법 검사
- mock JSON 파싱 검사

## Change Log

2026-07-09

- 역 상세 mock 데이터 연결 매핑 추가

## Timestamp

2026-07-09 13:12:30 (KST)

---

# 구간 상세 전체 Mock 연결 검수 작업 요약

# 개요

구간 상세 화면의 전체 mock 연결 상태를 검수했습니다.

검수 범위는 구간 제목, breadcrumb, 상단 요약, 주요 지표 카드, 특보별 분석 테이블, 과거 사례 테이블, 대시보드에서 구간 상세로 이동하는 흐름입니다.

# 구현 목적

여러 단계로 나누어 연결한 구간 상세 mock 데이터가 같은 `segment_id` 기준으로 일관되게 표시되는지 확인하기 위함입니다.

# 구현 내용

이번 단계에서는 기능 코드를 새로 추가하지 않고 검수와 문서화를 진행했습니다.

검수한 파일:

- `frontend/route-detail.js`
- `frontend/dashboard.js`
- `mock/segments_details.json`
- `mock/vulnerability_segments.json`

# 코드 설명

## 왜 필요한가

구간 상세 화면은 여러 mock 파일을 함께 사용합니다.

`vulnerability_segments.json`은 요약 지표를 담당하고, `segments_details.json`은 특보별 통계와 과거 사례를 담당합니다.

두 mock의 `segment_id`가 맞지 않으면 화면 일부는 표시되고 일부는 다른 구간 데이터를 보여주는 문제가 생길 수 있습니다.

## 어떤 원리인가

1. JavaScript 문법 오류가 없는지 확인합니다.
2. `vulnerability_segments.json`의 모든 `segment_id`가 `segments_details.json`에도 존재하는지 확인합니다.
3. 대표 구간 3개의 화면 표시 기대값을 확인합니다.
4. 로컬 HTTP 서버에서 route detail 페이지와 mock 파일이 200으로 응답하는지 확인합니다.
5. 모든 상세 mock에 `by_alert[]`, `cases[]`가 존재하는지 확인합니다.

# API

API 변경 사항은 없습니다.

검수한 mock 데이터:

- `GET ../mock/vulnerability_segments.json`
- `GET ../mock/segments_details.json`

# Database

DB 변경 사항은 없습니다.

# 테스트 방법

1. JavaScript 문법 검사

```bash
node --check frontend/route-detail.js
node --check frontend/dashboard.js
```

예상 결과:

- 오류 없이 종료됩니다.

2. segment id 참조 무결성 검사

```bash
node -e "const fs=require('fs'); const details=JSON.parse(fs.readFileSync('mock/segments_details.json','utf8')); const vuln=JSON.parse(fs.readFileSync('mock/vulnerability_segments.json','utf8')); const detailIds=new Set(details.segments.map((item)=>item.segment_id)); const vulnIds=new Set(vuln.segments.map((item)=>item.segment_id)); const missingDetails=vuln.segments.filter((item)=>!detailIds.has(item.segment_id)); const missingSummary=details.segments.filter((item)=>!vulnIds.has(item.segment_id)); console.log('vulnerability segments:', vuln.segments.length); console.log('detail segments:', details.segments.length); console.log('missing details:', missingDetails.length); console.log('missing summaries:', missingSummary.length); if (missingDetails.length||missingSummary.length) process.exit(1);"
```

예상 결과:

```text
vulnerability segments: 6
detail segments: 6
missing details: 0
missing summaries: 0
```

3. 대표 구간 기대값 확인

```text
daejeon-gimcheon_gumi | 대전→김천(구미) 구간 | 높음 | 14.6분 | 8.0% | 37건 | 3 alerts | 3 cases
cheonan-daejeon | 천안→대전 구간 | 주의 | 11.3분 | 5.0% | 42건 | 3 alerts | 3 cases
miryang-busan | 밀양→부산 구간 | 관심 | 5.4분 | 0.0% | 7건 | 3 alerts | 3 cases
```

4. HTTP 경로 검사

```text
http://127.0.0.1:8765/frontend/route-detail.html?segment_id=daejeon-gimcheon_gumi
http://127.0.0.1:8765/frontend/route-detail.html?segment_id=cheonan-daejeon
http://127.0.0.1:8765/frontend/route-detail.html?segment_id=miryang-busan
```

검증 결과:

```text
route-detail.html?segment_id=daejeon-gimcheon_gumi = 200
route-detail.html?segment_id=cheonan-daejeon = 200
route-detail.html?segment_id=miryang-busan = 200
route-detail.js = 200
segments_details.json = 200
vulnerability_segments.json = 200
```

5. 상세 테이블 데이터 존재 검사

```bash
node -e "const fs=require('fs'); const details=JSON.parse(fs.readFileSync('mock/segments_details.json','utf8')); const bad=details.segments.filter((segment)=>!Array.isArray(segment.by_alert)||!segment.by_alert.length||!Array.isArray(segment.cases)||!segment.cases.length); console.log('segments with missing table data:', bad.length); if (bad.length) console.log(bad.map((item)=>item.segment_id).join(', ')); if (bad.length) process.exit(1);"
```

예상 결과:

```text
segments with missing table data: 0
```

# 주의사항

현재 차트 영역과 일부 사이드 카드에는 아직 정적 데이터가 남아 있습니다.

이번 검수는 지금까지 연결한 mock 데이터 범위의 일관성 검수입니다.

# 변경 이력

2026-07-09

- 구간 상세 전체 mock 연결 검수
- segment id 참조 무결성 확인
- 대표 구간 기대값 문서화

# 다음 작업

- 구간 상세 차트 영역 mock 연결 여부 결정
- route detail 사이드 카드의 정적 정보 mock 연결 여부 검토
- 전체 프로젝트 mock 데이터 매핑 체크리스트 작성

# 작업 요약

## 완료한 내용

- 구간 상세 JS 문법 검증
- segment id 참조 무결성 검증
- 대표 구간 기대값 확인
- HTTP 경로 검증
- 문서화

## 수정한 파일

- `.docs/Frontend.md`

## 구현 이유

여러 mock 파일이 연결된 상세 화면은 참조 무결성 검수가 중요합니다.

이번 검수로 구간 상세 화면의 주요 mock 연결이 같은 `segment_id` 기준으로 동작함을 확인했습니다.

## 변경 사항

- 기능 코드 변경 없음
- 검수 결과 문서 추가

## 새롭게 배운 개념

- Mock Integrity Check
- Cross-file Reference Validation
- Detail Page Regression Check

## 실무에서는

실무에서는 mock 또는 seed 데이터에도 schema 검증과 참조 무결성 검사를 자동화합니다.

프론트엔드에서는 최소한 상세 화면이 받는 id와 mock/API 응답 id가 일치하는지 테스트하는 것이 좋습니다.

## 개선 가능한 부분

- 검증 스크립트를 별도 파일로 분리
- Playwright 기반 화면 텍스트 검증 추가
- 차트 영역 mock 연결

## 다음 작업

- 구간 상세 차트 영역 mock 연결 여부 결정

## 복습 문제

1. `segment_id` 참조 무결성 검사가 필요한 이유는 무엇인가요?
2. 상세 화면에서 여러 mock 파일을 함께 사용할 때 주의할 점은 무엇인가요?
3. 현재 검수 방식에서 자동화할 수 있는 부분은 무엇인가요?

## 오늘 배운 내용

- Reference Integrity
- Mock Regression Check
- Cross-file Validation

## Change Log

2026-07-09

- 구간 상세 전체 mock 연결 검수
- 문서 업데이트

## Timestamp

2026-07-09 16:16:10 (KST)

---

# 구간 상세 요약 차트 Mock 연결 작업 요약

# 개요

구간 상세 화면의 요약 탭에 있는 차트 2개를 mock 데이터와 연결했습니다.

연결한 차트:

- 시간대별 평균 지연 시간 선 그래프
- 지연 증가량 추이 막대 그래프

# 구현 목적

기존 차트는 HTML에 고정된 정적 값으로 표시되고 있었습니다.

구간 상세 화면이 `segment_id`에 따라 바뀌도록 개선되었기 때문에, 차트도 선택된 구간의 mock 데이터를 기준으로 함께 변경되어야 합니다.

# 구현 내용

- `mock/segments_details.json`
  - 각 구간에 `hourly_delay[]` 추가
  - 각 구간에 `delay_increase_trend[]` 추가

- `frontend/route-detail.html`
  - 선 그래프 polyline, point, tooltip에 렌더링용 `data-*` 속성 추가
  - 막대 그래프 plot 영역에 렌더링용 `data-*` 속성 추가

- `frontend/route-detail.js`
  - 선 그래프 좌표 계산 함수 추가
  - 실제/예측 polyline 렌더링 추가
  - 최근 7일 지연 증가량 막대 생성 함수 추가
  - 상세 데이터 없음 상태에서 차트 fallback 처리 추가

# 코드 설명

## 왜 필요한가

상단 요약 카드와 테이블은 이미 mock 데이터와 연결되어 있었지만, 차트는 아직 고정된 숫자를 표시하고 있었습니다.

이 상태에서는 `route-detail.html?segment_id=miryang-busan`처럼 다른 구간으로 이동해도 차트가 같은 값으로 남는 문제가 생깁니다.

## 어떤 원리인가

1. URL의 `segment_id`로 선택 구간을 찾습니다.
2. 선택 구간의 `segments_details.json` 상세 데이터를 가져옵니다.
3. `hourly_delay[]`를 SVG 좌표로 변환합니다.
4. `actual` 데이터는 실선 polyline으로 표시합니다.
5. `forecast` 데이터는 실제 마지막 지점부터 이어지는 점선 polyline으로 표시합니다.
6. `delay_increase_trend[]`는 최근 7일 막대 그래프로 다시 생성합니다.

# API

API 변경 사항은 없습니다.

사용한 mock 데이터:

- `GET ../mock/segments_details.json`

추가된 mock 필드:

```json
{
  "hourly_delay": [
    { "time": "00:00", "delay_min": 6.4, "type": "actual" }
  ],
  "delay_increase_trend": [
    { "date": "2026-07-01", "delay_increase": 5.2 }
  ]
}
```

# Database

DB 변경 사항은 없습니다.

# 테스트 방법

1. JavaScript 문법 검사

```bash
node --check frontend/route-detail.js
```

예상 결과:

- 오류 없이 종료됩니다.

2. 모든 구간의 차트 mock 데이터 존재 검사

```bash
node -e "const fs=require('fs'); const data=JSON.parse(fs.readFileSync('mock/segments_details.json','utf8')); const bad=data.segments.filter((s)=>!Array.isArray(s.hourly_delay)||s.hourly_delay.length!==7||!Array.isArray(s.delay_increase_trend)||s.delay_increase_trend.length!==7); console.log('segments:', data.segments.length); console.log('bad chart data:', bad.length); if (bad.length) process.exit(1);"
```

검증 결과:

```text
segments: 6
bad chart data: 0
```

3. 대표 구간 차트 포인트 검사

```text
actual points: 4
forecast points: 3
trend bars: 7
```

4. HTTP 경로 검사

```text
/frontend/route-detail.html?segment_id=daejeon-gimcheon_gumi=200
/frontend/route-detail.js=200
/mock/segments_details.json=200
```

# 주의사항

이번 작업은 요약 탭의 차트 2개만 연결했습니다.

특보별 분석 탭의 가로 막대 차트와 과거 사례 비교 차트는 아직 정적 데이터가 남아 있습니다.

# 변경 이력

2026-07-09

- 구간 상세 요약 차트 mock 연결
- 구간별 시간대별 지연 데이터 추가
- 구간별 최근 7일 지연 증가량 데이터 추가

# 작업 요약

## 완료한 내용

- 요약 선 그래프 mock 데이터 연결
- 요약 막대 그래프 mock 데이터 연결
- 구간별 차트 데이터 구조 확장
- 문법 및 mock 구조 검증
- HTTP 경로 검증

## 수정한 파일

- `frontend/route-detail.html`
- `frontend/route-detail.js`
- `mock/segments_details.json`
- `.docs/Frontend.md`

## 구현 이유

구간 상세 화면은 선택된 `segment_id`에 따라 전체 내용이 바뀌어야 합니다.

차트까지 mock 데이터와 연결하면 화면의 데이터 일관성이 높아집니다.

## 변경 사항

- 정적 SVG/polyline 값을 JS 렌더링 대상으로 변경
- 최근 7일 막대 그래프를 mock 배열 기반으로 재생성
- 예측선이 실제선의 마지막 지점에서 이어지도록 처리

## 새롭게 배운 개념

- SVG polyline 동적 렌더링
- Mock 기반 시계열 데이터 매핑
- Chart Fallback 처리

## 실무에서는

실무에서는 차트 라이브러리를 사용하는 경우가 많지만, 단순한 대시보드 차트는 SVG와 DOM만으로도 충분히 구현할 수 있습니다.

중요한 점은 화면 구조보다 데이터 구조를 먼저 안정적으로 잡는 것입니다.

## 개선 가능한 부분

- 특보별 분석 가로 막대 차트 mock 연결
- 과거 사례 비교 미니 차트 mock 연결
- 차트 검증 스크립트 분리

## 다음 작업

- 특보별 분석 탭의 가로 막대 차트 mock 연결

## 복습 문제

1. SVG `polyline`의 `points` 값은 어떤 형식으로 만들어야 하나요?
2. 실제 데이터와 예측 데이터를 같은 선 그래프에 표시할 때 구분 기준은 무엇인가요?
3. 차트 데이터가 없을 때 fallback 처리가 필요한 이유는 무엇인가요?

## 오늘 배운 내용

- SVG Polyline
- Time Series Mock Data
- DOM-based Chart Rendering

## Change Log

2026-07-09

- 구간 상세 요약 차트 mock 연결
- 문서 업데이트

## Timestamp

2026-07-09 16:22:57 (KST)

---

# 구간 상세 제목 및 Breadcrumb Mock 연결 작업 요약

# 개요

구간 상세 화면의 breadcrumb, page title, 설명 문구, 브라우저 문서 제목에 현재 선택된 구간명을 반영하도록 개선했습니다.

예를 들어 `route-detail.html?segment_id=miryang-busan`으로 접속하면 `밀양→부산 구간`이 화면 제목에 표시됩니다.

# 구현 목적

구간 상세 화면은 여러 `segment_id`를 지원하게 되었기 때문에, 사용자가 현재 어떤 구간을 보고 있는지 제목 영역에서도 명확히 확인할 수 있어야 합니다.

# 구현 내용

- `frontend/route-detail.html`
  - breadcrumb current text에 `data-route-detail-breadcrumb` 추가
  - page title에 `data-route-detail-title` 추가
  - description에 `data-route-detail-description` 추가

- `frontend/route-detail.js`
  - `formatSegmentLabel()` 추가
  - `renderRoutePageMeta()` 추가
  - 선택된 segment의 `from`, `to` 기준으로 구간명 생성
  - breadcrumb, h1, 설명 문구, `document.title` 갱신
  - 데이터 없음 상태의 기본 제목 fallback 처리

# 코드 설명

## 왜 필요한가

상단 카드에는 출발역/도착역이 표시되지만, page title이 계속 `구간 상세`로만 남아 있으면 사용자가 여러 구간 링크를 오갈 때 맥락을 놓치기 쉽습니다.

선택 구간명을 제목에 반영하면 화면의 의미가 더 분명해집니다.

## 어떤 원리인가

1. URL의 `segment_id`로 선택 구간을 찾습니다.
2. 선택 구간의 `from`, `to` 값을 읽습니다.
3. `from→to 구간` 형태의 label을 만듭니다.
4. breadcrumb, h1, description, document title에 같은 label을 반영합니다.

## 장점

- 현재 보고 있는 구간이 명확해집니다.
- 브라우저 탭 제목도 선택 구간과 일치합니다.
- 여러 구간 상세 링크를 열었을 때 구분하기 쉽습니다.

## 단점

- 현재 title은 단순 label 중심입니다.
- 노선명까지 포함한 긴 제목은 아직 사용하지 않았습니다.

## 다른 구현 방법

- `경부선 / 밀양→부산 구간`처럼 노선명을 포함
- breadcrumb을 `대시보드 > 구간 상세 > 밀양→부산` 3단계로 확장
- document title에 시스템명까지 포함

# API

API 변경 사항은 없습니다.

사용한 mock 데이터:

- `GET ../mock/segments_details.json`
- `GET ../mock/vulnerability_segments.json`

# Database

DB 변경 사항은 없습니다.

# 테스트 방법

1. JavaScript 문법 검사

```bash
node --check frontend/route-detail.js
```

예상 결과:

- 오류 없이 종료됩니다.

2. 선택 구간 제목 기대값 확인

```bash
node -e "const fs=require('fs'); const details=JSON.parse(fs.readFileSync('mock/segments_details.json','utf8')); const item=details.segments.find((segment)=>segment.segment_id==='miryang-busan'); console.log(item.from+'→'+item.to+' 구간');"
```

예상 결과:

```text
밀양→부산 구간
```

3. 브라우저 확인

```text
http://127.0.0.1:8765/frontend/route-detail.html?segment_id=miryang-busan
```

검증 기준:

- breadcrumb current text가 `밀양→부산 구간`으로 표시됩니다.
- h1 제목이 `밀양→부산 구간`으로 표시됩니다.
- 설명 문구가 선택 구간명을 포함합니다.
- 브라우저 title이 선택 구간명을 포함합니다.

# 주의사항

현재 breadcrumb은 여전히 2단계 구조입니다.

추후 필요하면 `대시보드 > 구간 상세 > 밀양→부산 구간`처럼 3단계 구조로 확장할 수 있습니다.

# 변경 이력

2026-07-09

- 구간 상세 breadcrumb mock 연결
- 구간 상세 page title mock 연결
- document title 선택 구간 반영

# 다음 작업

- 구간 상세 화면 전체 mock 연결 검수
- route-detail의 다른 정적 영역 중 mock 연결 필요 여부 점검

# 작업 요약

## 완료한 내용

- breadcrumb 구간명 반영
- page title 구간명 반영
- 설명 문구 구간명 반영
- document title 구간명 반영
- 테스트 및 문서화

## 수정한 파일

- `frontend/route-detail.html`
- `frontend/route-detail.js`
- `.docs/Frontend.md`

## 구현 이유

구간 상세 화면이 여러 segment id를 지원하므로, 화면 제목도 선택 구간과 일치해야 합니다.

## 변경 사항

- 제목 영역 data 속성 추가
- `formatSegmentLabel()` 추가
- `renderRoutePageMeta()` 추가

## 새롭게 배운 개념

- Dynamic Page Meta
- Breadcrumb Data Binding
- Document Title Update

## 실무에서는

실무에서는 상세 화면의 title, breadcrumb, meta title을 현재 리소스 이름과 동기화합니다.

특히 여러 상세 페이지를 새 탭으로 열 수 있는 운영 도구에서는 브라우저 탭 제목이 매우 중요합니다.

## 개선 가능한 부분

- breadcrumb 3단계 구조로 확장
- title에 노선명 포함
- description에 현재 특보와 위험도 포함

## 다음 작업

- 구간 상세 화면 전체 mock 연결 검수

## 복습 문제

1. 상세 화면 title을 선택 리소스 이름과 동기화해야 하는 이유는 무엇인가요?
2. `document.title`을 동적으로 바꾸면 어떤 사용자 경험이 좋아지나요?
3. breadcrumb를 3단계로 확장하면 어떤 장점이 있나요?

## 오늘 배운 내용

- Dynamic Title
- Breadcrumb Binding
- Page Metadata

## Change Log

2026-07-09

- 구간 상세 제목 및 breadcrumb mock 연결
- 문서 업데이트

## Timestamp

2026-07-09 16:12:00 (KST)

---

# Segment Detail Mock ID별 구조 확장 작업 요약

# 개요

`mock/segments_details.json`을 단일 구간 객체에서 `segment_id`별 상세 데이터 배열 구조로 확장했습니다.

이제 구간 상세 화면은 URL의 `segment_id`에 맞는 상세 mock을 찾아 특보별 분석 테이블과 과거 사례 목록을 렌더링합니다.

# 구현 목적

기존 `segments_details.json`은 대전-김천(구미) 구간 하나만 표현하는 구조였습니다.

하지만 대시보드와 우선 점검 대상에서 여러 구간이 `route-detail.html?segment_id=...`로 이동하므로, 상세 mock도 여러 구간을 지원해야 합니다.

# 구현 내용

- `mock/segments_details.json`
  - 단일 객체 구조를 `segments[]` 배열 구조로 변경
  - 6개 구간의 `segment_id`, `from`, `to`, `by_alert[]`, `cases[]` 추가
  - `vulnerability_segments.json`의 모든 `segment_id`와 매칭되도록 확장

- `frontend/route-detail.js`
  - `getSegmentDetails()` 추가
  - `getSegmentDetailById()` 추가
  - `getSegmentDetailByEndpoints()` 추가
  - `getFirstSegmentDetail()` 추가
  - `getSelectedSegmentDetail()` 추가
  - 기존 단일 객체 mock도 fallback으로 처리
  - 선택한 segment id에 맞는 상세 데이터로 테이블/사례 렌더링

# 코드 설명

## 왜 필요한가

대시보드에서 `cheonan-daejeon`, `miryang-busan` 같은 다른 구간으로 이동해도 상세 화면이 항상 대전-김천(구미) 데이터만 보여주면 데이터 신뢰도가 떨어집니다.

따라서 상세 mock도 `segment_id`를 key로 여러 구간을 표현해야 합니다.

## 어떤 원리인가

1. URL에서 `segment_id`를 읽습니다.
2. `vulnerability_segments.json`에서 선택 구간의 요약 지표를 찾습니다.
3. `segments_details.json`의 `segments[]`에서 같은 `segment_id`의 상세 데이터를 찾습니다.
4. 찾은 상세 데이터의 `by_alert[]`와 `cases[]`를 구간 상세 테이블에 렌더링합니다.
5. id가 없거나 상세 데이터가 없는 경우 endpoint 또는 첫 번째 상세 데이터로 fallback합니다.

## 장점

- 모든 vulnerability segment가 상세 mock과 연결됩니다.
- 구간 상세 화면이 실제 multi-detail 구조에 가까워졌습니다.
- 기존 단일 객체 mock 구조도 fallback으로 지원합니다.
- API 전환 시 `segment_id` 기반 조회 구조로 자연스럽게 이동할 수 있습니다.

## 단점

- mock 파일이 길어졌습니다.
- 아직 실제 API처럼 pagination이나 case id는 없습니다.
- 일부 상세 수치는 예시 mock이므로 실제 통계와는 다를 수 있습니다.

## 다른 구현 방법

- `segments_details/{segment_id}.json`처럼 파일을 분리하는 방식
- 객체 map 구조로 `{ "daejeon-gimcheon_gumi": {...} }` 사용
- API endpoint `/segments/{segment_id}/details` 형태로 전환
- 상세 mock을 DB seed 파일로 관리

# API

API 변경 사항은 없습니다.

변경된 mock 구조:

```json
{
  "segments": [
    {
      "segment_id": "daejeon-gimcheon_gumi",
      "from": "대전",
      "to": "김천(구미)",
      "by_alert": [],
      "cases": []
    }
  ]
}
```

# Database

DB 변경 사항은 없습니다.

실제 DB에서는 다음 관계가 적합합니다.

- `segments.segment_id`
- `segment_alert_stats.segment_id`
- `segment_cases.segment_id`

# 테스트 방법

1. JavaScript 문법 검사

```bash
node --check frontend/route-detail.js
```

예상 결과:

- 오류 없이 종료됩니다.

2. 상세 mock 참조 무결성 검사

```bash
node -e "const fs=require('fs'); const details=JSON.parse(fs.readFileSync('mock/segments_details.json','utf8')); const vuln=JSON.parse(fs.readFileSync('mock/vulnerability_segments.json','utf8')); const detailIds=new Set(details.segments.map((item)=>item.segment_id)); const missing=vuln.segments.filter((item)=>!detailIds.has(item.segment_id)); console.log('detail count:', details.segments.length); console.log('missing detail refs:', missing.length); if (missing.length) process.exit(1);"
```

예상 결과:

```text
detail count: 6
missing detail refs: 0
```

3. 상세 mock 목록 확인

```bash
node -e "const fs=require('fs'); const details=JSON.parse(fs.readFileSync('mock/segments_details.json','utf8')); console.log(details.segments.map((item)=>item.segment_id+':'+item.from+'→'+item.to).join('\n'));"
```

예상 결과:

```text
daejeon-gimcheon_gumi:대전→김천(구미)
cheonan-daejeon:천안→대전
yeongdeungpo-suwon:영등포→수원
dongdaegu-miryang:동대구→밀양
gimcheon_gumi-dongdaegu:김천(구미)→동대구
miryang-busan:밀양→부산
```

4. 브라우저 확인

```text
http://127.0.0.1:8765/frontend/route-detail.html?segment_id=miryang-busan
```

검증 기준:

- 구간 상세 화면이 정상 로드됩니다.
- `miryang-busan` segment id가 유효하게 처리됩니다.
- 특보별 분석과 과거 사례가 해당 구간 상세 mock 기준으로 렌더링됩니다.

# 주의사항

기존 단일 객체 구조도 `route-detail.js`에서 fallback 처리하지만, 앞으로는 `segments[]` 배열 구조를 기준으로 mock을 관리합니다.

# 변경 이력

2026-07-09

- `segments_details.json`을 segment id별 배열 구조로 확장
- 전체 vulnerability segment와 상세 mock 참조 무결성 확보
- route detail 선택 상세 lookup 로직 추가

# 다음 작업

- 대시보드 우선 점검 대상이나 취약 구간에서 다른 segment id로 이동했을 때 표시값 최종 검수
- 구간 상세 breadcrumb에 현재 구간명 반영

# 작업 요약

## 완료한 내용

- segment id별 상세 mock 구조 확장
- 6개 구간 상세 데이터 추가
- route-detail lookup 로직 개선
- 테스트 및 문서화

## 수정한 파일

- `mock/segments_details.json`
- `frontend/route-detail.js`
- `.docs/Frontend.md`

## 구현 이유

구간 상세 화면이 여러 segment id를 받으려면 상세 mock도 id별 데이터를 가져야 합니다.

이번 변경으로 대시보드의 여러 구간 링크가 각각 다른 상세 데이터를 사용할 수 있게 되었습니다.

## 변경 사항

- `segments[]` 구조 도입
- `segment_id`별 상세 데이터 추가
- id 기반 상세 lookup 함수 추가
- 단일 객체 mock fallback 유지

## 새롭게 배운 개념

- ID-keyed Detail Data
- Reference Integrity
- Detail Lookup
- Backward-compatible Mock Parsing

## 실무에서는

실무에서는 상세 화면이 URL id를 받아 API endpoint에서 해당 id의 상세 데이터를 조회합니다.

프론트엔드는 id를 기준으로 조회하고, 표시명은 응답 데이터의 label/name을 사용합니다.

## 개선 가능한 부분

- `case_id` 추가
- `by_alert` 상세 필드 확장
- `segments_details.json` schema 검증 스크립트 추가
- 구간 상세 breadcrumb 동적 렌더링

## 다음 작업

- 구간 상세 breadcrumb와 page title에 현재 구간명 반영

## 복습 문제

1. 단일 상세 mock 구조가 여러 segment id를 처리하기 어려운 이유는 무엇인가요?
2. `segment_id` 참조 무결성 검사가 필요한 이유는 무엇인가요?
3. 기존 단일 객체 mock fallback을 유지하면 어떤 장점이 있나요?

## 오늘 배운 내용

- ID-keyed Detail Mock
- Reference Integrity
- Backward Compatibility

## Change Log

2026-07-09

- segment detail mock id별 구조 확장
- route detail 상세 lookup 로직 개선
- 문서 업데이트

## Timestamp

2026-07-09 16:09:30 (KST)

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

# 구간 상세 과거 사례 Mock 연결 작업 요약

# 개요

구간 상세 화면의 `과거 사례` 탭에 있는 유사 사례 테이블을 `mock/segments_details.json`의 `cases[]` 데이터와 연결했습니다.

# 구현 목적

구간 상세 화면에서 과거 유사 사례는 현재 위험도를 해석하는 근거가 됩니다.

정적 사례 목록을 mock 데이터 기반으로 전환해, 실제 API 전환 전에도 화면 데이터 흐름을 검증할 수 있게 했습니다.

# 구현 내용

- `frontend/route-detail.html`
  - 과거 사례 테이블 tbody에 `data-route-detail-history-body` 추가

- `frontend/route-detail.js`
  - `routeTableElements.historyBody` 추가
  - `formatCaseDate()` 추가
  - `createHistoryAlertCell()` 추가
  - `getSimilarityStars()` 추가
  - `createSimilarityCell()` 추가
  - `createHistoryRow()` 추가
  - `renderRouteHistoryTable()` 추가
  - 빈 상태 fallback 처리 추가

# 코드 설명

## 왜 필요한가

현재 구간의 지연 위험이 과거에도 반복되었는지 확인하려면 유사 사례 목록이 필요합니다.

mock의 `cases[]`를 연결하면 날짜, 특보 종류, 지연 시간을 화면에서 바로 확인할 수 있습니다.

## 어떤 원리인가

1. `segments_details.json`을 fetch합니다.
2. `segmentDetailData.cases[]`를 읽습니다.
3. 각 사례의 `date`, `alert_type`, `delay_min`을 테이블 row로 변환합니다.
4. mock에 없는 강수량, 중단률, 영향 열차는 `-`로 표시합니다.
5. 지연 시간이 클수록 유사도 별점이 높게 표시되도록 단순 기준을 적용합니다.

## 장점

- 과거 사례 탭이 mock 데이터와 연결됩니다.
- mock에 없는 값을 임의로 만들지 않습니다.
- 데이터 없음 상태를 안전하게 처리합니다.
- 날짜 포맷을 화면 표시용으로 변환합니다.

## 단점

- 현재 mock에는 상세 기상 수치가 없습니다.
- 유사도는 실제 알고리즘이 아니라 지연 시간 기준 단순 표시입니다.
- 상세 비교 버튼은 아직 연결하지 않았습니다.

## 다른 구현 방법

- `cases[]`에 강수량, 중단률, 영향 열차, 유사도 필드 추가
- 사례 상세 modal 추가
- 과거 사례 필터 select와 실제 필터링 연결
- 차트 영역까지 cases 기반으로 동적 렌더링

# API

API 변경 사항은 없습니다.

사용한 mock 데이터:

- `GET ../mock/segments_details.json`

# Database

DB 변경 사항은 없습니다.

실제 DB/API에서는 과거 사례에 다음 필드를 포함하는 것이 좋습니다.

- `case_id`
- `date`
- `alert_type`
- `alert_level`
- `rainfall_mm`
- `avg_delay`
- `delay_increase`
- `stop_rate`
- `affected_train_count`
- `similarity_score`

# 테스트 방법

1. JavaScript 문법 검사

```bash
node --check frontend/route-detail.js
```

예상 결과:

- 오류 없이 종료됩니다.

2. cases mock 값 확인

```bash
node -e "const fs=require('fs'); const data=JSON.parse(fs.readFileSync('mock/segments_details.json','utf8')); console.log(data.cases.map((item)=>[item.date,item.alert_type||'평상시',item.delay_min+'분'].join(' | ')).join('\n'));"
```

예상 결과:

```text
2026-06-28 | 호우 | 19분
2026-06-14 | 호우 | 12분
2026-06-03 | 평상시 | 6분
```

3. mock JSON 파싱 검사

```bash
node -e "const fs=require('fs'); JSON.parse(fs.readFileSync('mock/segments_details.json','utf8')); console.log('segments cases json OK');"
```

예상 결과:

```text
segments cases json OK
```

4. 브라우저 확인

```text
http://127.0.0.1:8765/frontend/route-detail.html?segment_id=daejeon-gimcheon_gumi
```

검증 기준:

- 과거 사례 탭의 테이블에 사례 3건이 표시됩니다.
- `2026.06.28 호우 19분` 사례가 표시됩니다.
- `2026.06.14 호우 12분` 사례가 표시됩니다.
- `2026.06.03 평상시 6분` 사례가 표시됩니다.
- mock에 없는 강수량, 중단률, 영향 열차는 `-`로 표시됩니다.

# 주의사항

현재 `cases[]` mock은 매우 간단한 구조입니다.

따라서 실제 유사도 계산이나 상세 비교 기능을 구현하려면 mock 필드를 확장해야 합니다.

# 변경 이력

2026-07-09

- 구간 상세 과거 사례 테이블 mock 연결
- 날짜 포맷팅 추가
- 유사도 별점 fallback 표시 추가

# 다음 작업

- 과거 사례 mock 필드 확장
- 과거 사례 필터 기능 연결
- 대시보드 취약 구간 랭킹에서 구간 상세 화면으로 이동 연결

# 작업 요약

## 완료한 내용

- 과거 사례 테이블 DOM 연결
- `cases[]` 기반 row 렌더링
- mock 미제공 컬럼 fallback 처리
- 테스트 및 문서화

## 수정한 파일

- `frontend/route-detail.html`
- `frontend/route-detail.js`
- `.docs/Frontend.md`

## 구현 이유

구간 상세 화면에서 과거 사례는 현재 위험 판단의 근거가 되므로, mock 데이터와 연결해 화면 신뢰도를 높였습니다.

## 변경 사항

- history table body data 속성 추가
- cases row 생성 함수 추가
- 날짜/특보/지연 시간 동적 표시

## 새롭게 배운 개념

- Historical Case Rendering
- Date Formatting
- Similarity Fallback

## 실무에서는

실무에서는 유사도 점수를 백엔드 또는 분석 모델에서 계산해 내려주고, 프론트엔드는 그 점수를 시각화하는 역할을 맡는 것이 좋습니다.

## 개선 가능한 부분

- case id 추가
- 유사도 점수 mock 추가
- 과거 사례 상세보기 연결
- 필터 form 동작 연결

## 다음 작업

- 대시보드 취약 구간 랭킹에서 구간 상세 화면으로 `segment_id` 전달

## 복습 문제

1. mock에 없는 과거 사례 컬럼을 `-`로 표시한 이유는 무엇인가요?
2. 날짜 데이터를 화면용 문자열로 변환할 때 주의할 점은 무엇인가요?
3. 유사도 점수는 프론트엔드에서 계산하는 것보다 백엔드에서 내려주는 것이 좋은 이유는 무엇인가요?

## 오늘 배운 내용

- Historical Case Mapping
- Date Formatting
- Fallback UI

## Change Log

2026-07-09

- 구간 상세 과거 사례 mock 연결
- 문서 업데이트

## Timestamp

2026-07-09 15:58:55 (KST)

---

# 구간 상세 특보별 분석 테이블 Mock 연결 작업 요약

# 개요

구간 상세 화면의 `특보별 영향 요약` 테이블과 `특보별 영향 비교` 테이블을 `mock/segments_details.json`의 `by_alert[]` 데이터와 연결했습니다.

# 구현 목적

구간 상세 화면의 특보별 분석 영역은 어떤 기상특보가 구간 지연에 큰 영향을 주는지 확인하는 핵심 영역입니다.

정적 표를 mock 데이터 기반으로 전환해, 이후 실제 API 응답으로 쉽게 바꿀 수 있도록 렌더링 구조를 만들었습니다.

# 구현 내용

- `frontend/route-detail.html`
  - 요약 탭의 특보별 영향 요약 tbody에 `data-route-detail-impact-summary-body` 추가
  - 특보별 분석 탭의 비교 표 tbody에 `data-route-detail-alert-analysis-body` 추가

- `frontend/route-detail.js`
  - `routeTableElements` 추가
  - `getAlertIconPath()` 추가
  - `getStatusBadgeClass()` 추가
  - `createSummaryAlertRow()` 추가
  - `createAlertAnalysisRow()` 추가
  - `renderRouteAlertTables()` 추가
  - 데이터 없음 fallback row 처리

# 코드 설명

## 왜 필요한가

mock의 `by_alert[]`에는 특보 종류, 특보 등급, 평균 지연 시간, 표본 수가 들어 있습니다.

이 데이터를 테이블에 연결하면 화면에 표시되는 특보별 영향 수치가 mock과 일치하게 됩니다.

## 어떤 원리인가

1. `segments_details.json`을 fetch합니다.
2. `segmentDetailData.by_alert[]` 배열을 읽습니다.
3. 요약 탭 테이블에는 특보 종류, 등급, 평균 지연, 표본 수를 렌더링합니다.
4. 특보별 분석 탭 테이블에도 같은 데이터를 더 넓은 컬럼 구조에 맞춰 렌더링합니다.
5. mock에 없는 지연 증가량, 운행 중단률, 최대 지연, 영향 열차는 `-`로 표시합니다.

## 장점

- 같은 `by_alert[]` 데이터를 두 테이블에서 재사용합니다.
- mock에 없는 필드를 임의로 만들지 않습니다.
- 특보 등급별 badge와 특보 종류별 icon을 동적으로 표시합니다.
- 데이터 없음 상태를 안전하게 처리합니다.

## 단점

- 현재 mock에는 일부 컬럼 데이터가 없습니다.
- 차트 영역은 아직 정적 상태입니다.
- 특보별 분석 탭의 모든 컬럼을 채우려면 mock 확장이 필요합니다.

## 다른 구현 방법

- `by_alert[]` mock에 `delay_increase`, `stop_rate`, `max_delay`, `affected_train_avg` 추가
- 요약 테이블과 분석 테이블을 하나의 View Model로 변환
- 특보별 차트까지 같은 데이터로 함께 렌더링

# API

API 변경 사항은 없습니다.

사용한 mock 데이터:

- `GET ../mock/segments_details.json`

# Database

DB 변경 사항은 없습니다.

실제 DB/API에서는 특보별 통계에 다음 필드를 포함하는 것이 좋습니다.

- `alert_type`
- `alert_level`
- `sample_n`
- `avg_delay`
- `delay_increase`
- `stop_rate`
- `max_delay`
- `affected_train_avg`

# 테스트 방법

1. JavaScript 문법 검사

```bash
node --check frontend/route-detail.js
```

예상 결과:

- 오류 없이 종료됩니다.

2. mock JSON 파싱 검사

```bash
node -e "const fs=require('fs'); JSON.parse(fs.readFileSync('mock/segments_details.json','utf8')); console.log('segments details json OK');"
```

예상 결과:

```text
segments details json OK
```

3. 특보별 테이블 기대값 확인

```bash
node -e "const fs=require('fs'); const data=JSON.parse(fs.readFileSync('mock/segments_details.json','utf8')); console.log(data.by_alert.map((item)=>[item.alert_type,item.alert_level,item.sample_n+'회',item.avg_delay.toFixed(1)+'분'].join(' | ')).join('\n'));"
```

예상 결과:

```text
호우 | 경보 | 37회 | 14.6분
호우 | 주의보 | 44회 | 9.1분
폭염 | 경보 | 25회 | 7.2분
```

4. 브라우저 확인

```text
http://127.0.0.1:8765/frontend/route-detail.html?segment_id=daejeon-gimcheon_gumi
```

검증 기준:

- 요약 탭의 특보별 영향 요약 테이블에 mock 데이터 3건이 표시됩니다.
- 특보별 분석 탭의 특보별 영향 비교 테이블에 mock 데이터 3건이 표시됩니다.
- `호우 경보`, `호우 주의보`, `폭염 경보`가 표시됩니다.
- mock에 없는 컬럼은 `-`로 표시됩니다.

# 주의사항

현재 `segments_details.by_alert[]`에는 평균 지연 시간과 표본 수만 있습니다.

따라서 지연 증가량, 운행 중단률, 최대 지연, 영향 열차는 이번 단계에서 계산하지 않고 `-`로 표시했습니다.

# 변경 이력

2026-07-09

- 구간 상세 특보별 영향 요약 테이블 mock 연결
- 구간 상세 특보별 영향 비교 테이블 mock 연결
- 특보별 테이블 빈 상태 처리 추가

# 다음 작업

- 구간 상세 과거 사례 목록을 `segments_details.cases[]`와 연결
- 특보별 차트 mock 연결
- `by_alert[]` mock 필드 확장

# 작업 요약

## 완료한 내용

- 특보별 분석 테이블 DOM 연결
- `by_alert[]` 기반 테이블 렌더링
- mock 미제공 컬럼 fallback 처리
- 테스트 및 문서화

## 수정한 파일

- `frontend/route-detail.html`
- `frontend/route-detail.js`
- `.docs/Frontend.md`

## 구현 이유

구간 상세 화면의 특보별 표가 mock 데이터와 일치해야 사용자가 데이터 흐름을 신뢰할 수 있습니다.

## 변경 사항

- table body data 속성 추가
- 특보별 row 생성 함수 추가
- 특보별 icon/badge 동적 처리

## 새롭게 배운 개념

- Table Rendering
- Shared Data Source
- Missing Field Fallback

## 실무에서는

실무에서는 표 컬럼과 API 필드를 먼저 계약하고, 프론트엔드는 누락 필드에 대한 fallback 정책을 명확히 둡니다.

## 개선 가능한 부분

- `by_alert[]`에 추가 통계 필드 확장
- 특보별 차트 동적 렌더링
- 테이블 row 클릭 상세 기능 추가

## 다음 작업

- 구간 상세 과거 사례 목록 mock 연결

## 복습 문제

1. mock에 없는 컬럼을 임의로 계산하지 않고 `-`로 표시한 이유는 무엇인가요?
2. 같은 `by_alert[]` 데이터를 두 테이블에서 재사용할 때 장점은 무엇인가요?
3. 특보별 차트까지 동적으로 만들려면 어떤 mock 필드가 추가로 필요할까요?

## 오늘 배운 내용

- Dynamic Table Rendering
- Missing Data Fallback
- Alert Statistics Mapping

## Change Log

2026-07-09

- 구간 상세 특보별 분석 테이블 mock 연결
- 문서 업데이트

## Timestamp

2026-07-09 15:55:45 (KST)

---

# 구간 상세 1차 Mock 매핑 작업 요약

# 개요

`frontend/route-detail.html`의 상단 구간 요약, 현재 위험도, 주요 지표 카드 4개를 mock 데이터와 연결했습니다.

이번 단계는 구간 상세 화면 전체가 아니라, 첫 화면에서 가장 먼저 보이는 핵심 요약 정보만 1차로 매핑했습니다.

# 구현 목적

구간 상세 화면의 정적 데이터를 mock 기반 렌더링 구조로 전환하기 위함입니다.

사용자는 구간 상세 화면에 진입했을 때 선택한 `segment_id` 기준으로 출발역, 도착역, 노선, 위험도, 지연/중단 지표를 확인할 수 있어야 합니다.

# 구현 내용

- `frontend/route-detail.html`
  - 구간 출발역/도착역에 `data-route-detail-from-station`, `data-route-detail-to-station` 추가
  - 노선, 기준 시간, 위험도, 특보 문구에 data 속성 추가
  - 주요 지표 카드 4개에 `data-route-detail-metric` 구조 추가

- `frontend/route-detail.js`
  - `segments_details.json` fetch 추가
  - `vulnerability_segments.json` fetch 추가
  - `segment_id` query 우선 해석
  - 선택 구간 기준 상단 요약 렌더링
  - 선택 구간 기준 주요 지표 카드 렌더링
  - 기존 탭 전환 기능 유지
  - fetch 실패 또는 데이터 없음 fallback 처리

# 코드 설명

## 왜 필요한가

구간 상세 화면이 정적 값으로 남아 있으면 대시보드의 구간 랭킹, checklist, 상세 화면이 서로 다른 정보를 보여줄 수 있습니다.

mock 데이터 기반으로 매핑하면 이후 API 전환 시 화면 구조를 유지한 채 데이터 출처만 바꾸기 쉬워집니다.

## 어떤 원리인가

1. `route-detail.html?segment_id=daejeon-gimcheon_gumi`에서 `segment_id`를 읽습니다.
2. `vulnerability_segments.json`에서 같은 `segment_id`의 구간을 찾습니다.
3. `segments_details.json`에서 기본 구간 상세 데이터를 함께 읽습니다.
4. 상단 구간명과 노선, 현재 위험도, 특보 문구를 렌더링합니다.
5. `avg_delay_incr`, `stop_rate`, `sample_n`을 주요 지표 카드에 표시합니다.

## 장점

- 구간 상세 첫 화면이 mock 데이터와 연결됩니다.
- `segment_id` 기반 진입을 지원합니다.
- 기존 탭 UI를 유지합니다.
- 데이터 없음 상태를 안전하게 처리합니다.

## 단점

- 특보별 분석 테이블과 과거 사례는 아직 연결하지 않았습니다.
- `segments_details.json`은 현재 대전-김천(구미) 구간 중심 데이터만 가지고 있습니다.
- 기준 시간, 거리, 기준 운행 시간은 아직 mock에 구조화되어 있지 않습니다.

## 다른 구현 방법

- 구간 상세 전용 mock을 segment id별 객체로 확장
- 대시보드에서 구간 상세로 직접 이동 링크 추가
- 구간 상세 화면에 select를 추가해 구간 변경 지원
- 모든 주요 지표를 하나의 View Model로 변환 후 렌더링

# API

API 변경 사항은 없습니다.

사용한 mock 데이터:

- `GET ../mock/segments_details.json`
- `GET ../mock/vulnerability_segments.json`

# Database

DB 변경 사항은 없습니다.

실제 DB에서는 `segments.segment_id`를 기준으로 구간 상세 지표와 과거 사례를 조회하는 구조가 적합합니다.

# 테스트 방법

1. JavaScript 문법 검사

```bash
node --check frontend/route-detail.js
```

예상 결과:

- 오류 없이 종료됩니다.

2. mock JSON 파싱 검사

```bash
node -e "const fs=require('fs'); JSON.parse(fs.readFileSync('mock/segments_details.json','utf8')); JSON.parse(fs.readFileSync('mock/vulnerability_segments.json','utf8')); console.log('route detail mock json OK');"
```

예상 결과:

```text
route detail mock json OK
```

3. 기대값 확인

```bash
node -e "const fs=require('fs'); const detail=JSON.parse(fs.readFileSync('mock/segments_details.json','utf8')); const data=JSON.parse(fs.readFileSync('mock/vulnerability_segments.json','utf8')); const seg=data.segments.find((item)=>item.segment_id==='daejeon-gimcheon_gumi'); const risk=seg.avg_delay_incr>=12?'높음':seg.avg_delay_incr>=7?'주의':'관심'; console.log([detail.from+'역→'+detail.to+'역', data.line, data.alert_type+' '+data.alert_level, risk, seg.avg_delay_incr.toFixed(1)+'분', (seg.stop_rate*100).toFixed(1)+'%', seg.sample_n+'건'].join(' | '));"
```

예상 결과:

```text
대전역→김천(구미)역 | 경부선 | 호우 경보 | 높음 | 14.6분 | 8.0% | 37건
```

4. 브라우저 확인

```text
http://127.0.0.1:8765/frontend/route-detail.html?segment_id=daejeon-gimcheon_gumi
```

검증 기준:

- 출발역은 `대전역`으로 표시됩니다.
- 도착역은 `김천(구미)역`으로 표시됩니다.
- 노선은 `경부선`으로 표시됩니다.
- 현재 위험도는 `높음`으로 표시됩니다.
- 특보는 `호우 경보`로 표시됩니다.
- 평균 예상 지연 시간은 `14.6분`으로 표시됩니다.
- 운행 중단률은 `8.0%`로 표시됩니다.
- 분석 표본 수는 `37건`으로 표시됩니다.

# 주의사항

이번 단계는 구간 상세 1차 매핑입니다.

특보별 분석 테이블과 과거 사례 목록은 다음 단계에서 `segments_details.by_alert[]`, `segments_details.cases[]`와 연결하는 것이 좋습니다.

# 변경 이력

2026-07-09

- 구간 상세 상단 요약 mock 연결
- 구간 상세 위험도 mock 연결
- 구간 상세 주요 지표 카드 mock 연결

# 다음 작업

- 특보별 분석 테이블을 `segments_details.by_alert[]`와 연결
- 과거 사례 목록을 `segments_details.cases[]`와 연결
- 대시보드 취약 구간 랭킹에서 구간 상세 화면으로 `segment_id` 전달

# 작업 요약

## 완료한 내용

- 구간 상세 HTML data 속성 추가
- route-detail mock fetch 구현
- segment id 기반 초기 구간 선택
- 주요 지표 카드 4개 렌더링
- 테스트 및 문서화

## 수정한 파일

- `frontend/route-detail.html`
- `frontend/route-detail.js`
- `.docs/Frontend.md`

## 구현 이유

구간 상세 화면도 역 상세 화면처럼 mock 데이터 기반으로 동작해야 전체 프로젝트의 데이터 흐름이 일관됩니다.

## 변경 사항

- `route-detail.js` fetch/render 로직 추가
- `segment_id` query 해석 추가
- 상단 구간 정보와 주요 지표 카드 동적 렌더링

## 새롭게 배운 개념

- Segment Detail View
- Segment ID Query
- Mock-based Detail Rendering

## 실무에서는

실무에서는 상세 화면에 필요한 요약 데이터, 통계 테이블, 과거 사례를 하나의 endpoint 또는 조합 가능한 endpoint로 제공합니다.

프론트엔드는 API 응답을 바로 DOM에 넣기보다 화면용 View Model로 변환해 렌더링하는 편이 유지보수에 좋습니다.

## 개선 가능한 부분

- 거리/기준 시간 mock 추가
- 기준 시각 mock 추가
- 특보별 분석 테이블 연결
- 과거 사례 연결
- 구간 변경 UI 추가

## 다음 작업

- 구간 상세 특보별 분석 테이블 mock 연결

## 복습 문제

1. 상세 화면에서 `segment_id` query를 사용하는 이유는 무엇인가요?
2. `vulnerability_segments.json`과 `segments_details.json`을 함께 읽는 이유는 무엇인가요?
3. mock에 없는 거리/기준 시간은 어떻게 처리하는 것이 좋을까요?

## 오늘 배운 내용

- Segment Detail Mapping
- Query-based Detail Rendering
- Mock View Model

## Change Log

2026-07-09

- 구간 상세 1차 mock 매핑
- route-detail fetch/render 로직 추가
- 문서 업데이트

## Timestamp

2026-07-09 15:51:19 (KST)

---

# Segment ID Mock 구조화 작업 요약

# 개요

`mock/vulnerability_segments.json`의 각 구간에 `segment_id`를 추가했습니다.

또한 대시보드의 취약 구간 랭킹 row와 우선 점검 대상 row에 id를 DOM dataset으로 남겨, 이후 구간 상세 화면 연결에 사용할 수 있도록 준비했습니다.

# 구현 목적

구간 상세 화면을 만들려면 `대전→김천(구미) 구간` 같은 표시 문자열보다 안정적인 구간 식별자가 필요합니다.

이번 단계에서는 구간 상세 페이지를 바로 만들지 않고, 먼저 mock 데이터와 DOM 렌더링 흐름이 같은 `segment_id`를 공유하도록 정리했습니다.

# 구현 내용

- `mock/vulnerability_segments.json`
  - 각 구간에 `segment_id` 추가
  - 예: `daejeon-gimcheon_gumi`, `cheonan-daejeon`, `yeongdeungpo-suwon`

- `frontend/dashboard.js`
  - 취약 구간 랭킹 row에 `data-segment-id` 추가
  - 우선 점검 대상 row에 `data-target-type` 추가
  - 우선 점검 대상 row에 `data-target-id` 추가

# 코드 설명

## 왜 필요한가

구간명은 화면 표시용 문구입니다.

구간 상세 이동, API 조회, 데이터 join에는 `segment_id`처럼 변하지 않는 식별자가 필요합니다.

## 어떤 원리인가

1. `vulnerability_segments.segments[]`에 `segment_id`를 추가합니다.
2. `checklist.items[]`의 `segment_id`와 같은 값을 사용합니다.
3. 대시보드 취약 구간 랭킹을 렌더링할 때 row에 `data-segment-id`를 저장합니다.
4. 우선 점검 대상 row에는 `target_type`과 `target_id`를 dataset으로 저장합니다.
5. 이후 구간 상세 화면을 만들면 이 id를 query string 또는 route parameter로 전달할 수 있습니다.

## 장점

- checklist와 vulnerability segment mock이 같은 id 체계를 공유합니다.
- 구간 상세 화면을 만들 준비가 됩니다.
- 표시 문자열 파싱 없이 구간을 식별할 수 있습니다.
- DOM에도 id가 남아 있어 클릭 이벤트 확장이 쉬워집니다.

## 단점

- 아직 구간 상세 화면은 없습니다.
- 현재는 dataset으로 준비만 했기 때문에 사용자가 체감하는 화면 변화는 거의 없습니다.
- `segment_id` 네이밍 규칙을 프로젝트 전반에서 계속 지켜야 합니다.

## 다른 구현 방법

- 구간 상세 페이지를 먼저 만들고 동시에 링크 연결
- `segments.json` 메타데이터 파일을 별도로 생성
- API에서 구간별 `detail_url`을 직접 내려주는 방식
- route path를 `/segments/{segment_id}` 형태로 설계

# API

API 변경 사항은 없습니다.

변경된 mock 예시:

```json
{
  "segment_id": "daejeon-gimcheon_gumi",
  "from": "대전",
  "to": "김천(구미)"
}
```

# Database

DB 변경 사항은 없습니다.

실제 DB에서는 `segments` 테이블의 primary key 또는 unique key로 `segment_id`를 두고, checklist가 이를 참조하는 구조가 적합합니다.

# 테스트 방법

1. JavaScript 문법 검사

```bash
node --check frontend/dashboard.js
```

예상 결과:

- 오류 없이 종료됩니다.

2. segment id 참조 무결성 검사

```bash
node -e "const fs=require('fs'); const segments=JSON.parse(fs.readFileSync('mock/vulnerability_segments.json','utf8')).segments; const checklist=JSON.parse(fs.readFileSync('mock/checklist.json','utf8')).items; const segmentIds=new Set(segments.map((segment)=>segment.segment_id)); const missing=checklist.filter((item)=>item.target_type==='segment'&&!segmentIds.has(item.segment_id)); console.log('missing checklist segment refs:', missing.length); if (missing.length) process.exit(1);"
```

예상 결과:

```text
missing checklist segment refs: 0
```

3. mock JSON 파싱 검사

```bash
node -e "const fs=require('fs'); JSON.parse(fs.readFileSync('mock/vulnerability_segments.json','utf8')); JSON.parse(fs.readFileSync('mock/checklist.json','utf8')); console.log('segment mock json OK');"
```

예상 결과:

```text
segment mock json OK
```

4. 브라우저 확인

```text
http://127.0.0.1:8765/frontend/dashboard.html
```

검증 기준:

- 대시보드가 정상 로드됩니다.
- `mock/vulnerability_segments.json`이 HTTP 200으로 로드됩니다.
- 취약 구간 랭킹은 기존과 동일하게 표시됩니다.
- 우선 점검 대상 상세 패널도 기존과 동일하게 동작합니다.

# 주의사항

이번 작업은 구간 상세 연결을 위한 데이터 준비 단계입니다.

구간 상세 화면이 아직 없기 때문에 취약 구간 랭킹이나 구간 점검 대상은 링크로 만들지 않았습니다.

# 변경 이력

2026-07-09

- `vulnerability_segments.json`에 `segment_id` 추가
- 취약 구간 랭킹 row에 `data-segment-id` 추가
- 우선 점검 대상 row에 `data-target-type`, `data-target-id` 추가

# 다음 작업

- 구간 상세 화면 설계
- 구간 상세 mock 데이터 구조 설계
- 취약 구간 랭킹에서 구간 상세 화면으로 이동 연결

# 작업 요약

## 완료한 내용

- 구간 mock id 구조화
- checklist segment reference와 무결성 검증
- 대시보드 DOM dataset 준비
- 테스트 및 문서화

## 수정한 파일

- `mock/vulnerability_segments.json`
- `frontend/dashboard.js`
- `.docs/Frontend.md`

## 구현 이유

구간 상세 화면을 안정적으로 연결하려면 표시명 대신 `segment_id`가 필요합니다.

이번 작업으로 구간 데이터도 역 데이터처럼 id 기반 확장이 가능해졌습니다.

## 변경 사항

- `segment_id` 필드 추가
- `data-segment-id` 추가
- `data-target-type` 추가
- `data-target-id` 추가

## 새롭게 배운 개념

- Segment ID
- Reference Integrity
- Dataset-based UI Extension

## 실무에서는

실무에서는 구간, 역, 노선처럼 여러 데이터가 서로 참조하는 대상에 반드시 안정적인 id를 둡니다.

그리고 mock 단계에서도 id 참조가 맞는지 간단한 검증 스크립트를 두면 API 전환 때 버그를 크게 줄일 수 있습니다.

## 개선 가능한 부분

- 구간 상세 전용 mock 추가
- `segment_id` 네이밍 규칙 문서화
- 구간 상세 화면 생성
- checklist와 vulnerability segment join 로직 추가

## 다음 작업

- 구간 상세 화면의 기본 HTML 구조 설계

## 복습 문제

1. 구간명보다 `segment_id`를 사용하는 것이 안전한 이유는 무엇인가요?
2. checklist의 `segment_id`가 vulnerability segment mock에 존재하는지 검증해야 하는 이유는 무엇인가요?
3. DOM dataset은 어떤 상황에서 유용하게 사용할 수 있나요?

## 오늘 배운 내용

- Segment ID
- Reference Integrity
- DOM Dataset
- Mock Data Contract

## Change Log

2026-07-09

- segment id mock 구조화
- dashboard row dataset 추가
- 문서 업데이트

## Timestamp

2026-07-09 14:33:10 (KST)

---

# Station Lookup Mock 기반 통일 작업 요약

# 개요

`frontend/dashboard.js`에 남아 있던 `STATION_NAME_BY_ID` 하드코딩 상수를 제거하고, `mock/vulnerability_stations.json`의 `station_id`와 `station` 값을 기준으로 lookup하도록 정리했습니다.

# 구현 목적

역 id와 역명 매핑을 코드에 중복으로 관리하면 mock 데이터가 바뀔 때 JS 상수도 함께 수정해야 합니다.

이번 작업은 역 메타데이터의 기준을 `vulnerability_stations.json`으로 통일해 유지보수성을 높이기 위한 정리입니다.

# 구현 내용

- `frontend/dashboard.js`
  - `STATION_NAME_BY_ID` 제거
  - `getStationsFromData()` 추가
  - `getStationByName()` 추가
  - `getStationById()` 추가
  - 우선 점검 대상 역 링크 생성 시 mock stations 배열을 기준으로 station id와 역명 조회
  - 기존 문자열 fallback은 유지

# 코드 설명

## 왜 필요한가

`STATION_NAME_BY_ID`처럼 JS 안에 역 목록을 다시 적으면 `vulnerability_stations.json`과 데이터가 중복됩니다.

중복 데이터는 한쪽만 수정되는 순간 화면 링크가 깨질 수 있으므로, 한 곳의 mock 데이터를 기준으로 lookup하는 편이 안전합니다.

## 어떤 원리인가

1. `vulnerabilityStationsData.stations[]`를 가져옵니다.
2. `station_id`가 필요한 경우 `getStationById()`로 찾습니다.
3. 역명으로 id를 찾아야 하는 경우 `getStationByName()`을 사용합니다.
4. 우선 점검 대상의 `station_id`와 stations mock을 비교해 실제 역명을 찾습니다.
5. 찾은 역명의 `station_id`로 역 상세 URL을 생성합니다.

## 장점

- 역 id/역명 매핑을 한 곳에서 관리합니다.
- 새 역을 추가할 때 JS 상수를 수정하지 않아도 됩니다.
- mock 데이터가 실제 API 메타데이터 역할을 하게 됩니다.
- 이후 station id 기반 API 전환이 쉬워집니다.

## 단점

- 링크 생성 함수에 stations mock 데이터가 필요합니다.
- mock 데이터에 `station_id`가 빠지면 fallback으로 역명 query를 사용합니다.

## 다른 구현 방법

- 별도 `stations.json` 메타데이터 파일 생성
- API에서 station id와 label을 공통 코드 테이블로 제공
- 빌드 시 mock schema 검증 추가
- station id만 URL에 사용하고 역명 fallback 제거

# API

API 변경 사항은 없습니다.

사용한 mock 데이터:

- `GET ../mock/vulnerability_stations.json`
- `GET ../mock/checklist.json`

# Database

DB 변경 사항은 없습니다.

실제 서비스에서는 `stations` 테이블을 기준 테이블로 두고 다른 데이터가 `station_id`를 참조하는 구조가 적합합니다.

# 테스트 방법

1. JavaScript 문법 검사

```bash
node --check frontend/dashboard.js
```

예상 결과:

- 오류 없이 종료됩니다.

2. mock JSON 파싱 검사

```bash
node -e "const fs=require('fs'); JSON.parse(fs.readFileSync('mock/vulnerability_stations.json','utf8')); JSON.parse(fs.readFileSync('mock/checklist.json','utf8')); console.log('mock json OK');"
```

예상 결과:

```text
mock json OK
```

3. station id 기반 링크 확인

```bash
node -e "const fs=require('fs'); const stations=JSON.parse(fs.readFileSync('mock/vulnerability_stations.json','utf8')).stations; const checklist=JSON.parse(fs.readFileSync('mock/checklist.json','utf8')).items; const stationItem=checklist.find((item)=>item.target_type==='station'); const station=stations.find((item)=>item.station_id===stationItem.station_id); console.log([stationItem.target, station.station_id, station.station, './station-detail.html?'+new URLSearchParams({station_id:station.station_id}).toString()].join(' | '));"
```

예상 결과:

```text
대전역 | daejeon | 대전 | ./station-detail.html?station_id=daejeon
```

4. 브라우저 확인

```text
http://127.0.0.1:8765/frontend/dashboard.html
```

검증 기준:

- 대시보드가 정상 로드됩니다.
- 우선 점검 대상의 `대전역` 링크가 `station_id=daejeon`으로 이동합니다.
- 역 상세 화면도 정상 로드됩니다.

# 주의사항

현재 `station_id`는 `vulnerability_stations.json`에만 있습니다.

향후 다른 mock 파일에서도 역을 참조한다면 같은 id 체계를 사용해야 합니다.

# 변경 이력

2026-07-09

- `STATION_NAME_BY_ID` 제거
- stations mock 기반 lookup 함수 추가
- 우선 점검 대상 역 링크 lookup 통일

# 다음 작업

- `vulnerability_segments.json`에 `segment_id` 추가
- 구간 상세 화면 설계
- segment id 기반 구간 상세 링크 준비

# 작업 요약

## 완료한 내용

- 하드코딩 역명 매핑 제거
- stations mock 기반 id/name lookup 통일
- 대시보드 링크 동작 검증
- 문서화

## 수정한 파일

- `frontend/dashboard.js`
- `.docs/Frontend.md`

## 구현 이유

데이터 매핑 기준을 코드 상수가 아니라 mock 데이터로 통일하면 확장과 유지보수가 쉬워집니다.

## 변경 사항

- `getStationsFromData()` 추가
- `getStationByName()` 추가
- `getStationById()` 추가
- 우선 점검 대상 역 링크가 stations mock을 기준으로 생성되도록 변경

## 새롭게 배운 개념

- Single Source of Truth
- Metadata Lookup
- Mock-driven Mapping

## 실무에서는

실무에서는 station 목록을 공통 메타데이터 API로 제공하고, 여러 화면이 같은 `station_id`를 기준으로 데이터를 join합니다.

프론트엔드는 화면 표시명보다 id를 신뢰하고, label은 표시용으로만 사용합니다.

## 개선 가능한 부분

- 모든 station 참조 mock에 `station_id` 적용
- segment도 id 기반으로 구조화
- mock schema 검증 스크립트 추가

## 다음 작업

- `vulnerability_segments.json`에 `segment_id`를 추가하고 구간 상세 연결을 준비

## 복습 문제

1. Single Source of Truth가 유지보수에 도움이 되는 이유는 무엇인가요?
2. 역명 대신 station id를 기준으로 lookup하면 어떤 문제가 줄어드나요?
3. mock schema 검증이 필요한 이유는 무엇인가요?

## 오늘 배운 내용

- Single Source of Truth
- Metadata Lookup
- Mock-driven Mapping

## Change Log

2026-07-09

- dashboard station lookup을 mock 기반으로 통일
- 하드코딩 station map 제거
- 문서 업데이트

## Timestamp

2026-07-09 14:29:40 (KST)

---

# 역 상세 Station ID 전환 작업 요약

# 개요

`mock/vulnerability_stations.json`에 `station_id`를 추가하고, 대시보드에서 역 상세 화면으로 이동할 때 `station_id` query string을 우선 사용하도록 변경했습니다.

새 URL 형식:

```text
station-detail.html?station_id=daejeon
```

기존 URL 형식도 fallback으로 유지합니다.

```text
station-detail.html?station=대전
```

# 구현 목적

역명은 화면 표시용 데이터이고, `station_id`는 시스템에서 안정적으로 사용할 수 있는 식별자입니다.

역명이 바뀌거나 괄호, 공백, 동명이역 문제가 생겨도 링크와 데이터 매핑이 안전하게 유지되도록 id 기반으로 전환했습니다.

# 구현 내용

- `mock/vulnerability_stations.json`
  - 각 역에 `station_id` 추가
  - 예: `daejeon`, `dongdaegu`, `gimcheon_gumi`, `suwon`, `miryang`

- `frontend/dashboard.js`
  - `STATION_ID_QUERY_PARAM` 추가
  - `createStationDetailUrl()`이 `station_id`를 우선 사용하도록 변경
  - 취약 역 랭킹 링크가 `station_id` 기반 URL을 생성하도록 변경
  - 우선 점검 대상 역 링크도 `station_id` 기반으로 이동

- `frontend/station-detail.js`
  - `station_id` query를 우선 해석
  - 기존 `station` query는 fallback으로 유지
  - 역 선택 select의 value를 `station_id`로 변경
  - select 변경 시 URL을 `station_id` 기준으로 갱신

# 코드 설명

## 왜 필요한가

`?station=김천(구미)`처럼 역명을 URL에 직접 넣으면 인코딩과 명칭 변경에 영향을 받습니다.

반면 `?station_id=gimcheon_gumi`는 사람이 보기에는 덜 직관적이지만, 시스템 식별자로 더 안정적입니다.

## 어떤 원리인가

1. station mock에 `station_id`를 추가합니다.
2. 대시보드 링크 생성 시 역명이 아니라 `station_id`를 query string에 넣습니다.
3. 역 상세 화면은 `station_id`를 먼저 읽습니다.
4. `station_id`가 유효하면 해당 station 객체의 `station` 값을 찾아 화면에 렌더링합니다.
5. `station_id`가 없으면 기존 `station` query를 읽어 하위 호환성을 유지합니다.

## 장점

- URL이 안정적인 식별자를 사용합니다.
- 한글 역명 인코딩 부담이 줄어듭니다.
- 역명 변경에도 링크 구조가 덜 흔들립니다.
- 실제 API 설계 방식에 더 가까워집니다.

## 단점

- URL만 보고 역명을 바로 알기 어렵습니다.
- station id와 역명 매핑을 관리해야 합니다.
- 기존 `station` query와 새 `station_id` query를 함께 지원하는 동안 코드가 조금 복잡해집니다.

## 다른 구현 방법

- path parameter로 `/stations/daejeon` 형태 사용
- `station_id`만 지원하고 기존 `station` query 제거
- station metadata mock을 별도로 만들고 모든 화면에서 join
- API에서 상세 URL을 직접 내려주는 방식

# API

API 변경 사항은 없습니다.

변경된 mock 예시:

```json
{
  "station_id": "daejeon",
  "station": "대전"
}
```

지원하는 query string:

```text
station_id=daejeon
station=대전
```

# Database

DB 변경 사항은 없습니다.

실제 DB에서는 `stations` 테이블 또는 컬렉션의 primary key로 `station_id`를 사용하는 구조가 적합합니다.

# 테스트 방법

1. JavaScript 문법 검사

```bash
node --check frontend/dashboard.js
node --check frontend/station-detail.js
```

예상 결과:

- 오류 없이 종료됩니다.

2. station id 매핑 확인

```bash
node -e "const fs=require('fs'); const data=JSON.parse(fs.readFileSync('mock/vulnerability_stations.json','utf8')); const ids=data.stations.map((station)=>station.station_id+':'+station.station); console.log(ids.join('\n'));"
```

예상 결과:

```text
daejeon:대전
dongdaegu:동대구
gimcheon_gumi:김천(구미)
suwon:수원
miryang:밀양
```

3. 새 URL 확인

```text
http://127.0.0.1:8765/frontend/station-detail.html?station_id=daejeon
```

4. 기존 URL fallback 확인

```text
http://127.0.0.1:8765/frontend/station-detail.html?station=%EB%8C%80%EC%A0%84
```

검증 기준:

- 두 URL 모두 HTTP 200으로 열립니다.
- `station_id=daejeon`은 대전역으로 렌더링됩니다.
- 대시보드의 취약 역 링크는 `station_id` query를 사용합니다.
- 역 상세 select 변경 시 URL이 `station_id` 기준으로 갱신됩니다.

# 주의사항

현재 `dashboard.js`에는 `STATION_NAME_BY_ID` 상수가 남아 있습니다.

장기적으로는 `vulnerability_stations.json`의 `station_id`를 기준으로 모든 매핑을 처리하도록 정리하는 것이 좋습니다.

# 변경 이력

2026-07-09

- `vulnerability_stations.json`에 `station_id` 추가
- 대시보드 역 상세 링크를 `station_id` 기반으로 변경
- 역 상세 화면 query 해석을 `station_id` 우선으로 변경
- 기존 `station` query fallback 유지

# 다음 작업

- `STATION_NAME_BY_ID` 상수를 mock 기반 lookup으로 제거
- `vulnerability_segments.json`에 `segment_id` 추가
- 구간 상세 화면 설계

# 작업 요약

## 완료한 내용

- 역 mock에 station id 추가
- 대시보드에서 id 기반 상세 링크 생성
- 역 상세 화면에서 id 기반 초기 선택 처리
- 기존 역명 query fallback 유지
- 테스트 및 문서화

## 수정한 파일

- `mock/vulnerability_stations.json`
- `frontend/dashboard.js`
- `frontend/station-detail.js`
- `.docs/Frontend.md`

## 구현 이유

역명 기반 URL은 표시명 변경과 인코딩 문제에 취약합니다.

`station_id` 기반 URL은 실제 서비스에서 더 안정적인 데이터 계약을 만들 수 있습니다.

## 변경 사항

- `station_id` 필드 추가
- `station_id` query 추가
- 역 상세 select value를 id 기반으로 변경
- 기존 `station` query fallback 유지

## 새롭게 배운 개념

- Stable Identifier
- Query Compatibility
- ID-based Routing
- Backward Compatibility

## 실무에서는

실무에서는 사용자가 보는 이름과 내부 식별자를 분리합니다.

URL, API 요청, DB join에는 id를 사용하고, 화면에는 label/name을 표시하는 방식이 일반적입니다.

## 개선 가능한 부분

- station id lookup을 mock 데이터 기반으로 통일
- 구간 데이터에도 segment id 추가
- URL query를 모두 id 기반으로 정리
- 기존 station query 제거 시점 결정

## 다음 작업

- `STATION_NAME_BY_ID` 상수를 제거하고 `vulnerability_stations.json` 기반 lookup으로 통일

## 복습 문제

1. `station_id` 기반 URL이 역명 기반 URL보다 안정적인 이유는 무엇인가요?
2. 기존 `station` query fallback을 유지하는 이유는 무엇인가요?
3. 화면 표시명과 내부 식별자를 분리하면 어떤 유지보수 이점이 있나요?

## 오늘 배운 내용

- Station ID
- Backward Compatibility
- ID-based Query String
- Stable URL Contract

## Change Log

2026-07-09

- 역 상세 URL을 station id 기반으로 전환
- 기존 station query fallback 유지
- 문서 업데이트

## Timestamp

2026-07-09 14:05:30 (KST)

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

# 역 상세 URL Query String 연결 작업 요약

# 개요

역 상세 화면의 선택 역 상태를 URL query string과 연결했습니다.

이제 `station-detail.html?station=동대구`처럼 접속하면 해당 역이 초기 선택값으로 렌더링됩니다.

# 구현 목적

사용자가 선택한 역을 새로고침, 공유 링크, 브라우저 뒤로가기 흐름에서도 유지하기 위함입니다.

UI 내부 상태만 사용하면 페이지를 새로고침했을 때 항상 기본 역으로 돌아가지만, URL에 상태를 남기면 화면 상태를 더 안정적으로 복원할 수 있습니다.

# 구현 내용

- `frontend/station-detail.js`
  - `station` query parameter를 읽는 로직 추가
  - URL의 역명이 mock 역 목록에 존재하면 해당 역으로 초기 렌더링
  - 역 선택 select 변경 시 `history.pushState()`로 URL 갱신
  - 브라우저 뒤로가기/앞으로가기 시 `popstate` 이벤트로 화면 재렌더링
  - query string이 있는 경우 select를 처음부터 표시

# 코드 설명

## 왜 필요한가

사용자가 특정 역 상세 화면을 공유하거나 새로고침했을 때 같은 역이 유지되어야 합니다.

예를 들어 운영자가 `동대구역` 위험도를 보고 있다가 URL을 공유하면, 받는 사람도 같은 역 상태로 화면을 확인할 수 있어야 합니다.

## 어떤 원리인가

1. 페이지 초기화 시 `window.location.search`에서 `station` 값을 읽습니다.
2. 읽은 역명이 `vulnerability_stations.stations[]`에 존재하는지 확인합니다.
3. 존재하면 해당 역을 선택 역으로 사용합니다.
4. 존재하지 않으면 기본값인 `station_details.station` 또는 첫 번째 mock 역을 사용합니다.
5. 사용자가 select를 변경하면 `history.pushState()`로 URL의 `station` 값을 갱신합니다.
6. 브라우저 뒤로가기/앞으로가기를 누르면 `popstate` 이벤트에서 URL 값을 다시 읽어 화면을 갱신합니다.

## 장점

- 새로고침해도 선택 역이 유지됩니다.
- 특정 역 화면을 링크로 공유할 수 있습니다.
- 실제 라우팅 구조로 확장하기 쉽습니다.
- 브라우저 뒤로가기/앞으로가기 UX가 자연스러워집니다.

## 단점

- URL에 노출되는 역명과 mock 역명이 정확히 일치해야 합니다.
- 한글 query string은 브라우저에서 percent encoding 형태로 보일 수 있습니다.
- 지금은 station id가 아니라 역명을 key로 사용하므로, 동명이역이 생기면 id 기반 구조로 바꿔야 합니다.

## 다른 구현 방법

- `?stationId=daejeon`처럼 안정적인 id를 사용하는 방식
- path parameter로 `/stations/daejeon` 형태를 사용하는 방식
- `localStorage`에 마지막 선택 역을 저장하는 방식
- 서버 라우팅에서 선택 역을 처리하는 방식

# API

API 변경 사항은 없습니다.

사용한 mock 데이터:

- `GET ../mock/station_details.json`
- `GET ../mock/vulnerability_stations.json`

# Database

DB 변경 사항은 없습니다.

# 테스트 방법

1. JavaScript 문법 검사

```bash
node --check frontend/station-detail.js
```

예상 결과:

- 오류 없이 종료됩니다.

2. query string 기대값 확인

```bash
node -e "const fs=require('fs'); const data=JSON.parse(fs.readFileSync('mock/vulnerability_stations.json','utf8')); const params=new URLSearchParams('station=%EB%8F%99%EB%8C%80%EA%B5%AC'); const selected=params.get('station'); const station=data.stations.find((item)=>item.station===selected); const risk=station.delay_rate>=0.4?'높음':station.delay_rate>=0.25?'주의':'관심'; console.log([selected+'역', data.line, risk, station.avg_delay.toFixed(1)+'분', '+'+station.delta_delay.toFixed(1)+'분', (station.delay_rate*100).toFixed(1)+'%'].join(' | '));"
```

예상 결과:

```text
동대구역 | 경부선 | 주의 | 10.2분 | +6.5분 | 38.0%
```

3. 브라우저 확인

```text
http://127.0.0.1:8765/frontend/station-detail.html?station=%EB%8F%99%EB%8C%80%EA%B5%AC
```

검증 기준:

- 초기 화면이 `동대구역` 기준으로 렌더링됩니다.
- 위험도는 `주의`로 표시됩니다.
- 평균 지연 시간은 `10.2분`으로 표시됩니다.
- 역 선택 select가 표시됩니다.
- 다른 역을 선택하면 주소창의 `station` 값이 변경됩니다.
- 브라우저 뒤로가기를 누르면 이전 선택 역으로 돌아갑니다.

# 주의사항

현재 query key는 역명입니다.

실무에서는 역명이 바뀌거나 중복될 수 있으므로 `stationId` 같은 불변 식별자를 사용하는 것이 더 안전합니다.

# 변경 이력

2026-07-09

- 역 상세 선택 상태를 `station` query string과 연결
- select 변경 시 URL 갱신
- popstate 기반 뒤로가기/앞으로가기 처리 추가

# 다음 작업

- 역별 상세 mock 데이터 구조 설계
- query string을 `stationId` 기반으로 전환
- 대시보드 랭킹에서 역 상세 화면으로 이동할 때 station query 전달

# 작업 요약

## 완료한 내용

- URL query string 기반 초기 역 선택
- select 변경 시 URL 동기화
- 브라우저 뒤로가기/앞으로가기 대응
- 테스트 방법과 검증 기준 문서화

## 수정한 파일

- `frontend/station-detail.js`
- `.docs/Frontend.md`

## 구현 이유

상세 화면의 상태는 사용자가 공유하거나 새로고침해도 유지되어야 합니다.

URL query string은 이 요구를 가장 단순하고 명확하게 만족시키는 방법입니다.

## 변경 사항

- `station` query parameter 추가
- `getInitialSelectedStationName()` 추가
- `updateStationQueryString()` 추가
- `popstate` 이벤트 처리 추가

## 새롭게 배운 개념

- URLSearchParams
- History API
- pushState
- popstate

## 실무에서는

실무에서는 화면 상태를 URL에 남기는 기준을 정해둡니다.

검색어, 필터, 정렬, 페이지 번호, 선택한 리소스처럼 사용자가 공유하거나 복원해야 하는 상태는 URL에 남기는 편이 좋습니다.

## 개선 가능한 부분

- 역명을 station id로 변경
- 잘못된 query 값이 들어왔을 때 사용자 안내 메시지 추가
- 대시보드에서 상세 화면으로 이동할 때 station query 전달

## 다음 작업

- 대시보드 취약 역 랭킹에서 역 상세 화면으로 station query를 전달

## 복습 문제

1. UI 상태를 URL query string에 저장하면 어떤 장점이 있나요?
2. `pushState()`와 `popstate`는 각각 언제 사용하나요?
3. 역명보다 station id를 query key로 사용하는 것이 더 안전한 이유는 무엇인가요?

## 오늘 배운 내용

- URL Query String
- History API
- Browser Navigation State
- Shareable UI State

## Change Log

2026-07-09

- 역 상세 URL query string 연결
- select 변경 시 URL 동기화
- 뒤로가기/앞으로가기 렌더링 처리

## Timestamp

2026-07-09 13:41:07 (KST)

---

# 역 상세 역 변경 Mock 연결 작업 요약

# 개요

역 상세 화면의 `역 변경` 버튼을 `mock/vulnerability_stations.json`의 역 목록과 연결했습니다.

사용자가 역 변경 버튼을 누르면 역 선택 select가 열리고, 선택한 역 기준으로 상단 역명, 위험도, 주요 지표 카드가 다시 렌더링됩니다.

# 구현 목적

정적 상세 화면을 단일 역 화면에서 mock 데이터 기반의 역 선택 화면으로 확장하기 위함입니다.

이번 단계에서는 새로운 페이지 이동이나 API를 만들지 않고, 기존 역 상세 화면 내부에서 선택 상태만 변경합니다.

# 구현 내용

- `frontend/station-detail.html`
  - `역 변경` 버튼에 `data-station-select-toggle` 추가
  - 역 선택 select 영역 추가

- `frontend/station-detail.js`
  - `vulnerability_stations.stations[]`를 select option으로 변환
  - 선택한 역의 `avg_delay`, `delta_delay`, `delay_rate`, `stop_rate`를 주요 지표 카드에 반영
  - 선택한 역의 `delay_rate` 기준으로 위험도 계산
  - 대전역 외 다른 역은 상세 통계와 과거 사례 mock이 없으므로 빈 상태로 표시

- `frontend/style.css`
  - 역 선택 select 스타일 추가
  - 모바일에서 select가 카드 폭에 맞게 내려가도록 반응형 스타일 추가
  - select focus-visible 스타일 추가

# 코드 설명

## 왜 필요한가

역 상세 화면은 특정 역 하나만 보는 화면이 아니라, 사용자가 관심 역을 바꿔가며 비교할 수 있어야 합니다.

mock 단계에서는 모든 역의 상세 사례 데이터가 없기 때문에, 역별 공통 지표는 갱신하고 상세 사례는 데이터 없음 상태로 분리했습니다.

## 어떤 원리인가

1. 페이지 로드 시 `station_details.json`과 `vulnerability_stations.json`을 병렬로 불러옵니다.
2. `vulnerability_stations.stations[]`를 select option으로 렌더링합니다.
3. 사용자가 역을 선택하면 선택한 역 이름으로 mock 배열에서 지표를 찾습니다.
4. 찾은 지표를 상단 정보 카드와 주요 지표 카드에 다시 렌더링합니다.
5. `station_details.json`에 존재하지 않는 역의 상세 통계와 사례는 빈 상태 메시지로 표시합니다.

## 장점

- 기존 화면 구조를 유지합니다.
- API 없이 mock 데이터만으로 역 선택 흐름을 검증할 수 있습니다.
- mock에 없는 데이터를 억지로 만들어 표시하지 않아 데이터 신뢰도를 유지합니다.

## 단점

- 현재는 대전역만 상세 통계와 과거 사례가 있습니다.
- 다른 역을 선택하면 상단 지표만 갱신되고 하단 상세 영역은 비어 있습니다.
- 주소 데이터가 mock에 없기 때문에 대전역 외에는 `주소 정보 없음(mock 미제공)`으로 표시합니다.

## 다른 구현 방법

- 역 변경 시 URL query string을 변경하는 방식
- 역별 상세 mock 파일을 별도로 만드는 방식
- 모든 역의 상세 데이터를 하나의 API 응답으로 받는 방식
- 선택 UI를 select가 아니라 modal 또는 command palette로 구현하는 방식

# API

이번 작업에서는 API를 추가하지 않았습니다.

사용한 mock 데이터:

- `GET ../mock/station_details.json`
- `GET ../mock/vulnerability_stations.json`

# Database

DB 변경 사항은 없습니다.

# 테스트 방법

1. JS 문법 검사

```bash
node --check frontend/station-detail.js
```

예상 결과:

- 오류 없이 종료됩니다.

2. 선택 역 기대값 확인

```bash
node -e "const fs=require('fs'); const data=JSON.parse(fs.readFileSync('mock/vulnerability_stations.json','utf8')); const selected='동대구'; const station=data.stations.find((item)=>item.station===selected); const risk=station.delay_rate>=0.4?'높음':station.delay_rate>=0.25?'주의':'관심'; console.log([selected+'역', data.line, risk, station.avg_delay.toFixed(1)+'분', '+'+station.delta_delay.toFixed(1)+'분', (station.delay_rate*100).toFixed(1)+'%'].join(' | '));"
```

예상 결과:

```text
동대구역 | 경부선 | 주의 | 10.2분 | +6.5분 | 38.0%
```

3. 브라우저 확인

```text
http://127.0.0.1:8765/frontend/station-detail.html
```

검증 기준:

- `역 변경` 버튼을 누르면 역 선택 select가 나타납니다.
- `동대구역`을 선택하면 평균 지연 시간은 `10.2분`으로 변경됩니다.
- `동대구역`을 선택하면 위험도는 `주의`로 변경됩니다.
- `대전역` 외 역을 선택하면 특보별 영향 통계와 과거 주요 사례는 데이터 없음 상태로 표시됩니다.

# 주의사항

현재 mock 상세 데이터는 `대전` 역 기준입니다.

다른 역까지 상세 통계와 사례를 표시하려면 `station_details.json` 구조를 역별 배열 또는 station key 기반 객체로 확장해야 합니다.

# 변경 이력

2026-07-09

- 역 상세 화면 역 변경 select 연결
- 선택한 역 기준 주요 지표 카드 재렌더링
- mock 미제공 상세 데이터 빈 상태 처리

# 다음 작업

- 역별 상세 mock 데이터 구조 설계
- 역 선택 상태를 URL query string으로 유지
- 사례 상세보기 버튼 동작 설계

# 작업 요약

## 완료한 내용

- 역 변경 버튼과 mock 역 목록 연결
- 선택한 역의 위험도와 주요 지표 카드 갱신
- mock에 없는 상세 데이터의 빈 상태 처리
- 테스트 방법과 검증 기준 문서화

## 수정한 파일

- `frontend/station-detail.html`
- `frontend/station-detail.js`
- `frontend/style.css`
- `.docs/Frontend.md`

## 구현 이유

대시보드에서 특정 역을 상세히 확인하는 흐름은 이후 실제 API 전환 시 핵심 사용자 흐름이 됩니다.

따라서 mock 단계에서 먼저 선택 상태, 데이터 매핑, 빈 상태를 검증했습니다.

## 변경 사항

- 버튼 클릭 시 select 표시
- select 변경 시 화면 재렌더링
- 역별 상세 mock이 없는 경우 하단 영역 데이터 없음 처리

## 새롭게 배운 개념

- 선택 상태 기반 렌더링
- mock 데이터 범위와 UI 표시 범위 분리
- 빈 상태 UX

## 실무에서는

실무에서는 선택한 역을 URL query string 또는 route parameter로 관리합니다.

예를 들어 `/station-detail.html?station=동대구`처럼 상태를 URL에 남기면 새로고침, 공유, 뒤로가기 흐름을 더 안정적으로 만들 수 있습니다.

## 개선 가능한 부분

- 역별 주소 mock 추가
- 역별 상세 통계 mock 추가
- 선택 상태 URL 반영
- 선택 UI 접근성 문구 보강

## 다음 작업

- 역 선택 상태를 URL query string과 연결

## 복습 문제

1. 선택한 역의 상세 mock 데이터가 없을 때 빈 상태를 보여주는 이유는 무엇인가요?
2. select option을 mock 배열에서 동적으로 만드는 방식의 장점은 무엇인가요?
3. URL query string으로 선택 상태를 관리하면 어떤 장점이 있나요?

## 오늘 배운 내용

- Select 기반 상태 변경
- View 재렌더링
- Empty State
- Mock 데이터 한계 처리

## Change Log

2026-07-09

- 역 상세 화면 역 변경 mock 연결
- 선택 역 기준 주요 지표 재렌더링
- 문서 업데이트

## Timestamp

2026-07-09 13:38:17 (KST)

---

# 역 상세 특보별 영향 통계 Mock 연결 작업 요약

## 완료한 내용

- 특보별 영향 통계 테이블을 `mock/station_details.json`의 `by_alert[]` 데이터와 연결했습니다.
- `by_alert[].alert_type`, `by_alert[].alert_level`, `by_alert[].sample_n`, `by_alert[].avg_delay` 값을 테이블에 렌더링했습니다.
- mock에 없는 지연률과 운행 중단률은 `-`로 표시했습니다.
- 데이터가 비어 있을 때 안내 행을 표시하도록 처리했습니다.

## 수정한 파일

- `frontend/station-detail.html`
- `frontend/station-detail.js`
- `.docs/Frontend.md`

## 구현 이유

특보별 영향 통계는 특정 역이 어떤 기상특보에서 얼마나 영향을 받는지 보여주는 핵심 분석 영역입니다.

정적 테이블을 유지하면 mock 데이터와 화면 내용이 달라질 수 있으므로, mock 데이터 기준으로 행을 동적으로 렌더링했습니다.

## 변경 사항

- `station-detail.html`의 특보별 영향 통계 `<tbody>`에 `data-station-detail-alert-table-body` 속성을 추가했습니다.
- `station-detail.js`에 특보별 통계 행 생성 함수를 추가했습니다.
- 특보 종류에 따라 아이콘을 선택하는 `getAlertIconPath()` 함수를 추가했습니다.
- `by_alert[]`가 비어 있으면 `특보별 영향 통계 데이터가 없습니다.` 문구를 표시합니다.

## 테스트 방법

1. JavaScript 문법 검사

```bash
node --check frontend/station-detail.js
```

예상 결과: 오류 메시지가 없어야 합니다.

2. Mock 데이터 확인

```bash
node -e "const fs=require('fs'); const d=JSON.parse(fs.readFileSync('mock/station_details.json','utf8')); console.log(JSON.stringify(d.by_alert.map(a=>a.alert_type+' '+a.alert_level+':'+a.sample_n+':'+a.avg_delay)))"
```

예상 결과:

- `호우 경보:34:15.2`
- `폭염 경보:61:12.7`
- `호우 주의보:52:8.4`
- `폭염 주의보:70:6.1`

3. 로컬 서버 경로 검사

```bash
python -m http.server 8765 --bind 127.0.0.1
```

브라우저에서 아래 주소로 접속합니다.

```text
http://127.0.0.1:8765/frontend/station-detail.html
```

검증 기준:

- 특보별 영향 통계 테이블에 4개 행이 표시됩니다.
- 발생 횟수 열에는 `sample_n` 값이 `회` 단위로 표시됩니다.
- 평균 지연 열에는 `avg_delay` 값이 표시됩니다.
- 지연률과 운행 중단률은 mock에 없으므로 `-`로 표시됩니다.

## 새롭게 배운 개념

- 테이블 행 동적 렌더링
- mock에 없는 데이터의 명시적 빈 값 처리
- 특보 종류별 아이콘 매핑

## 실무에서는

실무에서는 테이블에 필요한 모든 값이 API 계약에 명시되어야 합니다.

이번처럼 `지연률`, `운행 중단률`이 mock에 없을 때 프론트엔드에서 임의 계산하거나 추정하면 의미가 왜곡될 수 있으므로, 실서비스에서는 백엔드 또는 분석 레이어에서 정확한 값을 내려주는 것이 좋습니다.

## 개선 가능한 부분

- `by_alert[]`에 `delay_rate`, `stop_rate` 필드 추가
- 특보별 발생 횟수와 표본 수를 구분하는 필드 추가
- 테이블 정렬 기준 명시

## 다음 작업

- 과거 주요 사례를 `station_details.cases[]`와 연결

## 복습 문제

1. mock에 없는 값을 `-`로 표시하는 방식이 사용자에게 주는 장점은 무엇인가요?
2. 표본 수 `sample_n`과 실제 발생 횟수는 어떻게 다를 수 있나요?
3. 테이블 행을 동적으로 렌더링할 때 빈 데이터 상태를 처리해야 하는 이유는 무엇인가요?

## 오늘 배운 내용

- Dynamic Table Rendering
- Empty State
- Mock Field Gap

## Change Log

2026-07-09

- 역 상세 특보별 영향 통계 테이블 mock 데이터 연결

## Timestamp

2026-07-09 13:18:49 (KST)

---

# 역 상세 과거 주요 사례 Mock 연결 작업 요약

## 완료한 내용

- 과거 주요 사례 목록을 `mock/station_details.json`의 `cases[]` 데이터와 연결했습니다.
- `cases[].date`, `cases[].alert_type`, `cases[].delay_min` 값을 리스트에 렌더링했습니다.
- `alert_type`이 `null`인 사례는 `평상시`로 표시했습니다.
- 데이터가 비어 있을 때 안내 항목을 표시하도록 처리했습니다.

## 수정한 파일

- `frontend/station-detail.html`
- `frontend/station-detail.js`
- `.docs/Frontend.md`

## 구현 이유

과거 주요 사례는 특정 역에서 실제로 지연이 발생했던 이력을 보여주는 영역입니다.

정적 사례 문구에는 mock에 없는 강수량, 운행 중단률 등이 포함되어 있었기 때문에, mock에 실제로 존재하는 날짜, 특보 종류, 지연 시간 중심으로 의미를 명확히 바꿨습니다.

## 변경 사항

- `station-detail.html`의 과거 주요 사례 `<ul>`에 `data-station-detail-history-list` 속성을 추가했습니다.
- `station-detail.js`에 과거 사례 항목 생성 함수를 추가했습니다.
- 날짜를 `YYYY.MM.DD` 형식으로 표시하도록 변환했습니다.
- 지연 시간은 `기록된 지연 N분` 형식으로 표시합니다.
- 상세보기 버튼에 사례별 접근성 라벨을 추가했습니다.

## 테스트 방법

1. JavaScript 문법 검사

```bash
node --check frontend/station-detail.js
```

예상 결과: 오류 메시지가 없어야 합니다.

2. Mock 데이터 확인

```bash
node -e "const fs=require('fs'); const d=JSON.parse(fs.readFileSync('mock/station_details.json','utf8')); console.log(JSON.stringify(d.cases.map(c=>(c.date+':'+(c.alert_type||'평상시')+':'+c.delay_min))))"
```

예상 결과:

- `2026-06-28:호우:22`
- `2026-06-22:폭염:15`
- `2026-06-15:호우:11`
- `2026-06-09:평상시:7`

3. 로컬 서버 경로 검사

```bash
python -m http.server 8765 --bind 127.0.0.1
```

브라우저에서 아래 주소로 접속합니다.

```text
http://127.0.0.1:8765/frontend/station-detail.html
```

검증 기준:

- 과거 주요 사례 목록에 4개 항목이 표시됩니다.
- 첫 번째 항목은 `2026.06.28 호우`와 `기록된 지연 22분`을 표시합니다.
- 네 번째 항목은 특보가 없으므로 `평상시`로 표시합니다.

## 새롭게 배운 개념

- 동적 리스트 렌더링
- null 데이터 표시 정책
- 날짜 포맷 변환

## 실무에서는

실무에서는 과거 사례 데이터에 기상 수치, 운행 중단률, 상세 링크 ID가 함께 내려오는 것이 좋습니다.

현재 mock은 최소 필드만 가지고 있으므로, 프론트엔드는 존재하지 않는 정보를 꾸며내지 않고 명확히 표시 가능한 값만 렌더링했습니다.

## 개선 가능한 부분

- `cases[]`에 상세 ID 추가
- `cases[]`에 강수량, 풍속, 중단률 같은 원인 지표 추가
- 상세보기 버튼 클릭 시 상세 모달 연결

## 다음 작업

- 역 상세 화면 전체 mock 연결 검수
- 상세보기 버튼 동작 설계

## 복습 문제

1. `null` 값을 화면에 표시할 때 `평상시`처럼 의미 있는 라벨로 바꾸는 이유는 무엇인가요?
2. mock에 없는 강수량 정보를 화면에서 제거한 이유는 무엇인가요?
3. 리스트 렌더링에서 빈 배열 처리가 필요한 이유는 무엇인가요?

## 오늘 배운 내용

- Dynamic List Rendering
- Null Handling
- Date Formatting

## Change Log

2026-07-09

- 역 상세 과거 주요 사례 mock 데이터 연결

## Timestamp

2026-07-09 13:21:29 (KST)

---

# 역 상세 전체 Mock 연결 검수 작업 요약

## 완료한 내용

- 역 상세 화면의 mock 데이터 연결 상태를 전체 검수했습니다.
- `station-detail.js`와 `sidebar.js` 문법 검사를 수행했습니다.
- `station_details.json`, `vulnerability_stations.json` 파싱을 확인했습니다.
- 로컬 서버 기준으로 HTML, JS, CSS, mock JSON 접근 상태를 확인했습니다.
- 현재 mock 기준 화면 표시 예상값을 정리했습니다.

## 수정한 파일

- `.docs/Frontend.md`

## 구현 이유

역 상세 화면은 여러 mock 데이터를 조합해 렌더링합니다.

기능을 추가한 뒤에는 코드가 동작하는지만 보는 것이 아니라, 어떤 값이 화면에 표시되어야 하는지 기준을 문서로 남겨야 이후 API 전환이나 리팩토링 때 회귀를 빠르게 확인할 수 있습니다.

## 변경 사항

- 역 상세 전체 mock 연결 검수 기록을 추가했습니다.
- 로컬 서버 경로 검증 결과를 문서화했습니다.
- 화면 표시 예상값을 문서화했습니다.

## 테스트 방법

1. JavaScript 문법 검사

```bash
node --check frontend/station-detail.js
node --check frontend/sidebar.js
```

예상 결과: 오류 메시지가 없어야 합니다.

2. Mock 데이터 파싱 검사

```bash
node -e "const fs=require('fs'); JSON.parse(fs.readFileSync('mock/station_details.json','utf8')); JSON.parse(fs.readFileSync('mock/vulnerability_stations.json','utf8')); console.log('station detail mock json OK')"
```

예상 결과:

- `station detail mock json OK`

3. 로컬 서버 경로 검사

```bash
python -m http.server 8765 --bind 127.0.0.1
```

검증 대상:

- `/frontend/station-detail.html`
- `/frontend/station-detail.js`
- `/frontend/sidebar.js`
- `/frontend/style.css`
- `/mock/station_details.json`
- `/mock/vulnerability_stations.json`

모두 `200`으로 응답해야 합니다.

## 검증 기준

역 상세 상단:

- 역명: `대전역`
- 노선: `경부선`
- 현재 위험도: `높음`
- 기준 문구: `폭염 경보 기준`

주요 지표:

- 평균 지연 시간: `12.7분`
- 평균 지연 증가량: `+8.9분`
- 지연률: `44.0%`
- 운행 중단률: `1.0%`

특보별 영향 통계:

- `호우 경보` / `34회` / `15.2분`
- `폭염 경보` / `61회` / `12.7분`
- `호우 주의보` / `52회` / `8.4분`
- `폭염 주의보` / `70회` / `6.1분`

과거 주요 사례:

- `2026-06-28` / `호우` / `22분`
- `2026-06-22` / `폭염` / `15분`
- `2026-06-15` / `호우` / `11분`
- `2026-06-09` / `평상시` / `7분`

## 새롭게 배운 개념

- 연결 검수 기준 문서화
- 회귀 검증 기준값
- mock 기반 화면 검수

## 실무에서는

실무에서는 화면에 표시되어야 하는 기대값을 테스트 코드나 스냅샷으로 관리합니다.

현재 프로젝트는 Vanilla HTML/CSS/JS 구조이므로 우선 문서에 기대값을 명확히 남기고, 이후 Playwright 같은 브라우저 자동화 도구를 도입하면 이 기준을 테스트로 옮길 수 있습니다.

## 개선 가능한 부분

- 브라우저 자동화 테스트 도입
- 역 상세 화면 기대값 테스트 스크립트 추가
- mock 데이터 스키마 검증 추가

## 다음 작업

- 상세보기 버튼 동작 설계
- 역 변경 버튼 동작 설계
- 실제 API 전환 계획 수립

## 복습 문제

1. 화면 검수에서 “기대값”을 문서로 남기는 이유는 무엇인가요?
2. mock 데이터 기반 검수와 실제 API 기반 검수의 차이는 무엇인가요?
3. 브라우저 자동화 테스트를 도입하면 어떤 반복 작업을 줄일 수 있나요?

## 오늘 배운 내용

- Rendering Verification
- Regression Criteria
- Mock Validation

## Change Log

2026-07-09

- 역 상세 화면 전체 mock 연결 검수
- 표시 예상값 문서화

## Timestamp

2026-07-09 13:26:33 (KST)

---

# 역 상세 주요 지표 Mock 연결 작업 요약

## 완료한 내용

- `frontend/station-detail.js`를 생성했습니다.
- `mock/station_details.json`과 `mock/vulnerability_stations.json`을 불러오도록 연결했습니다.
- 역명, 노선 배지, 현재 위험도, 주요 지표 카드 4개를 mock 데이터 기준으로 렌더링했습니다.
- 데이터가 없거나 fetch에 실패할 때 기본 빈 상태를 표시하도록 처리했습니다.

## 수정한 파일

- `frontend/station-detail.html`
- `frontend/station-detail.js`
- `.docs/Frontend.md`

## 구현 이유

역 상세 화면의 상단 정보와 주요 지표는 사용자가 가장 먼저 확인하는 핵심 정보입니다.

정적 숫자를 유지하면 mock/API 데이터와 화면이 달라질 수 있으므로, 실제 데이터 연결에 앞서 mock 기반 렌더링 구조를 만들었습니다.

## 변경 사항

- `station-detail.html`에 `data-station-detail-*` 렌더링 대상 속성을 추가했습니다.
- `station-detail.html`에 `station-detail.js`를 연결했습니다.
- `station-detail.js`에서 역 상세 mock과 취약 역 mock을 병렬로 불러옵니다.
- `delay_rate` 기준으로 현재 위험도를 계산합니다.
- 주요 지표 카드의 값과 보조 문구를 mock 기준으로 갱신합니다.

## 테스트 방법

1. JavaScript 문법 검사

```bash
node --check frontend/station-detail.js
node --check frontend/sidebar.js
```

예상 결과: 오류 메시지가 없어야 합니다.

2. Mock JSON 파싱 검사

```bash
node -e "const fs=require('fs'); JSON.parse(fs.readFileSync('mock/station_details.json','utf8')); JSON.parse(fs.readFileSync('mock/vulnerability_stations.json','utf8')); console.log('station detail mock json OK')"
```

예상 결과:

- `station detail mock json OK`

3. 로컬 서버 경로 검사

```bash
python -m http.server 8765 --bind 127.0.0.1
```

브라우저에서 아래 주소로 접속합니다.

```text
http://127.0.0.1:8765/frontend/station-detail.html
```

검증 기준:

- 역명은 `대전역`으로 표시됩니다.
- 노선은 `경부선`으로 표시됩니다.
- 현재 위험도는 `높음`으로 표시됩니다.
- 기준 문구는 `폭염 경보 기준`으로 표시됩니다.
- 평균 지연 시간은 `12.7분`으로 표시됩니다.
- 평균 지연 증가량은 `+8.9분`으로 표시됩니다.
- 지연률은 `44.0%`로 표시됩니다.
- 운행 중단률은 `1.0%`로 표시됩니다.

## 새롭게 배운 개념

- 상세 화면 View Model
- 비율 데이터를 퍼센트로 변환하는 방식
- mock에 없는 필드를 정적 UI로 유지하는 방식

## 실무에서는

실무에서는 역 상세 화면의 상단 요약 데이터를 `/stations/{stationId}/summary` 같은 단일 API로 내려주는 편이 좋습니다.

프론트엔드는 API 응답을 그대로 DOM에 넣기보다 화면 표시용 View Model로 변환하고, mock에 없는 주소나 기준 시간 같은 값은 API 계약에 포함할지 별도 정책으로 남길지 결정합니다.

## 개선 가능한 부분

- 역 주소를 mock 또는 API에 추가
- 기준 시간을 mock 또는 API에 추가
- 특보별 영향 통계 테이블 연결
- 과거 주요 사례 연결
- 역 변경 버튼 동작 설계

## 다음 작업

- 특보별 영향 통계 테이블을 `station_details.by_alert[]`와 연결
- 과거 주요 사례를 `station_details.cases[]`와 연결

## 복습 문제

1. `delay_rate`처럼 0~1 사이 비율 데이터를 화면에서 퍼센트로 표시할 때 주의할 점은 무엇인가요?
2. mock에 없는 주소 필드를 기존 정적 문구로 유지하는 방식의 장단점은 무엇인가요?
3. 상세 화면 데이터를 View Model로 변환하면 어떤 유지보수 이점이 있나요?

## 오늘 배운 내용

- Station Detail Mock 연결
- View Model
- 빈 상태 처리
- 비율 데이터 포맷팅

## Change Log

2026-07-09

- 역 상세 상단 정보와 주요 지표 카드 mock 데이터 연결
- `frontend/station-detail.js` 추가

## Timestamp

2026-07-09 13:12:30 (KST)

---

# 구간 상세 화면 작업 요약

## 완료한 내용

- `ROUTE_DETAIL_DESIGN_GUIDE.md` 기준의 구간 상세 화면을 추가했습니다.
- 기존 메인 대시보드/역 상세 화면과 동일한 오버레이 사이드바 구조를 재사용했습니다.
- 메인 대시보드와 역 상세 화면의 `구간 상세` 사이드바 링크를 `route-detail.html`로 연결했습니다.
- 구간 요약 카드, 현재 위험도 카드, 탭 영역, 주요 지표 카드, 차트, 특보별 영향 요약 테이블, 현재 발효 특보 카드, 위험도 산정 기준 버튼을 구현했습니다.
- 구간 상세 화면 전용 CSS를 `frontend/style.css`에 추가했습니다.

## 수정한 파일

- `frontend/route-detail.html`
- `frontend/style.css`
- `frontend/dashboard.html`
- `frontend/station-detail.html`
- `.docs/Frontend.md`

## 구현 이유

메인 대시보드에서 특정 구간을 선택했을 때, 해당 구간의 기상 위험도와 철도 운행 영향을 상세하게 확인할 수 있는 화면이 필요하기 때문입니다.

## 변경 사항

- 구간 상세 신규 HTML 페이지 추가
- 사이드바에서 `구간 상세` 메뉴 활성화 처리
- 메인/역 상세 페이지의 구간 상세 링크 연결
- 구간 정보 카드와 위험도 카드 구현
- 요약 탭, RAG 심층 분석 버튼 구현
- 평균 예상 지연 시간, 지연 증가량, 운행 중단률, 예상 영향 열차 카드 구현
- 시간대별 평균 지연 시간 라인 차트 구현
- 최근 7일 지연 증가량 막대 차트 구현
- 특보별 영향 요약 테이블 구현
- 현재 발효 특보 및 위험도 산정 기준 사이드 카드 구현

## 테스트 방법

```bash
node --check frontend/sidebar.js
```

로컬 서버 실행 후 아래 주소에서 확인합니다.

```text
http://127.0.0.1:8765/frontend/route-detail.html
```

검증 기준:

- 메뉴 버튼을 누르면 기존과 동일하게 오버레이 사이드바가 열립니다.
- 사이드바에서 `구간 상세` 메뉴가 활성화되어 보입니다.
- 메인 대시보드와 역 상세 화면의 `구간 상세` 메뉴를 클릭하면 `route-detail.html`로 이동합니다.
- 좁은 화면에서 요약 카드, 차트, 사이드 정보가 세로로 배치되어 겹치지 않습니다.

## 새롭게 배운 개념

- 상세 페이지 간 사이드바 재사용
- 구간 정보 시각화
- Flexbox 기반 2열 분석 레이아웃
- 정적 라인/막대 차트 구성

## 실무에서는

실무에서는 구간 상세 화면의 지표와 차트 데이터를 정적 HTML에 직접 넣기보다 구간 ID를 기준으로 API에서 받아 렌더링합니다. 예를 들어 `/routes/{routeId}/summary`, `/routes/{routeId}/metrics`, `/routes/{routeId}/weather-alerts`처럼 책임별로 데이터를 나누면 유지보수와 테스트가 쉬워집니다.

## 개선 가능한 부분

- 구간 상세 mock 데이터 연결
- RAG 심층 분석 버튼 실제 페이지 연결
- 탭 전환 인터랙션 구현
- 차트 데이터 동적 렌더링
- 브라우저 시각 회귀 테스트 추가

## 다음 작업

- 구간 상세 화면 실제 브라우저 시각 검수
- 구간 상세 mock/API 데이터 설계
- 특보별 분석/과거 사례 탭 화면 구현

## 복습 문제

1. 메인/역/구간 상세 페이지에서 같은 사이드바 구조를 반복 작성할 때 생길 수 있는 유지보수 문제는 무엇일까요?
2. 구간 상세 화면의 차트 데이터를 API로 연결하려면 어떤 데이터 구조가 필요할까요?
3. 탭 UI에서 `role="tablist"`, `role="tab"` 같은 접근성 속성이 필요한 이유는 무엇일까요?

## 오늘 배운 내용

- 구간 상세 화면 레이아웃
- Flexbox 기반 콘텐츠/사이드 영역 구성
- 정적 SVG 라인 차트
- CSS 막대 차트
- 탭 접근성 구조

## Change Log

2026-07-09

- 구간 상세 화면 추가
- 메인/역 상세 사이드바의 구간 상세 링크 연결
- 구간 상세 전용 CSS 추가

## Timestamp

2026-07-09 12:00:00 (KST)
---

# 구간 상세 특보별 분석 탭 작업 요약

## 완료한 내용

- 구간 상세 화면의 `특보별 분석` 탭 화면을 추가했습니다.
- 기존 `요약` 탭과 새 `특보별 분석` 탭이 전환되도록 `frontend/route-detail.js`를 추가했습니다.
- 특보별 영향 비교 테이블을 구현했습니다.
- 특보별 평균 지연 시간 가로 막대 차트를 구현했습니다.
- 특보별 운행 중단률 가로 막대 차트를 구현했습니다.
- 우측 보조 영역에 현재 발효 특보, 위험도 산정 기준, 특보 등급 기준 카드를 배치했습니다.

## 수정한 파일

- `frontend/route-detail.html`
- `frontend/route-detail.js`
- `frontend/style.css`
- `.docs/Frontend.md`

## 구현 이유

구간 상세 화면에서 `특보별 분석` 탭을 클릭했을 때, 특보 종류와 등급별로 운행 영향 차이를 비교할 수 있는 별도 분석 화면이 필요하기 때문입니다.

## 변경 사항

- `data-route-tab`과 `data-route-panel` 기반 탭 전환 구조 추가
- `요약` 패널과 `특보별 분석` 패널 분리
- `role="tablist"`, `role="tab"`, `role="tabpanel"`, `aria-selected`, `aria-controls` 속성 보강
- 특보별 영향 비교 테이블 추가
- 평균 지연 시간/운행 중단률 가로 막대 차트 추가
- 특보 등급 기준 카드 추가

## 테스트 방법

```bash
node --check frontend/route-detail.js
```

로컬 서버 실행 후 아래 주소에서 확인합니다.

```text
http://127.0.0.1:8765/frontend/route-detail.html
```

검증 기준:

- `특보별 분석` 탭을 클릭하면 특보별 영향 비교 표가 표시됩니다.
- `요약` 탭을 다시 클릭하면 기존 요약 화면으로 돌아옵니다.
- 우측에는 현재 발효 특보, 위험도 산정 기준, 특보 등급 기준이 표시됩니다.
- 좁은 화면에서는 표와 차트가 가로 스크롤 또는 세로 배치로 깨지지 않아야 합니다.

## 새롭게 배운 개념

- 탭 패널 상태 관리
- `hidden` 속성을 이용한 패널 전환
- ARIA 탭 접근성 구조
- 가로 막대 차트 UI

## 실무에서는

실무에서는 탭 상태를 URL 쿼리나 해시와 연결해 새로고침 후에도 같은 탭을 유지하도록 구현하는 경우가 많습니다. 또한 특보별 분석 데이터는 정적 HTML이 아니라 API 응답을 받아 테이블과 차트를 같은 데이터 소스에서 렌더링하는 방식이 유지보수에 유리합니다.

## 개선 가능한 부분

- `과거 사례` 탭 화면 구현
- 탭 상태 URL 동기화
- 특보별 분석 mock/API 데이터 연결
- 차트 컴포넌트 공통화

## 다음 작업

- 구간 상세 `과거 사례` 탭 디자인 구현
- 특보별 분석 데이터 구조 설계
- 브라우저 시각 검수

## 복습 문제

1. 탭 UI에서 `aria-selected`와 `aria-controls`는 각각 어떤 역할을 하나요?
2. `hidden` 속성으로 패널을 숨기는 방식의 장점은 무엇인가요?
3. 하나의 데이터로 표와 차트를 동시에 렌더링하면 어떤 유지보수 장점이 있을까요?

## 오늘 배운 내용

- ARIA 탭 구조
- hidden 기반 화면 전환
- 특보별 영향 비교 테이블
- CSS 가로 막대 차트

## Change Log

2026-07-09

- 구간 상세 특보별 분석 탭 화면 추가
- 구간 상세 탭 전환 스크립트 추가

## Timestamp

2026-07-09 12:20:00 (KST)
---

# 구간 상세 과거 사례 탭 작업 요약

## 완료한 내용

- 구간 상세 화면의 `과거 사례` 탭 화면을 추가했습니다.
- 특보 종류, 특보 등급, 기간 필터를 구현했습니다.
- 유사 사례 목록 테이블을 구현했습니다.
- 페이지네이션 UI를 구현했습니다.
- 과거 사례 비교 카드 4개를 구현했습니다.
- 우측 보조 영역에 현재 발효 특보, 위험도 산정 기준, 현재 사례와 유사한 과거 사례 카드를 배치했습니다.

## 수정한 파일

- `frontend/route-detail.html`
- `frontend/style.css`
- `.docs/Frontend.md`

## 구현 이유

구간 상세 화면에서 과거 유사 사례를 기준으로 현재 위험 상황을 비교하고, 운영자가 과거 지연 및 운행 중단 사례를 빠르게 확인할 수 있도록 하기 위해 구현했습니다.

## 변경 사항

- `data-route-panel="history"` 패널 추가
- 필터 form과 label/select 연결 추가
- 유사 사례 목록 테이블 추가
- 평균 지연 시간, 지연 증가량, 운행 중단률, 누적 강수량 비교 차트 추가
- 현재 사례와 가장 유사한 과거 사례 요약 카드 추가
- 과거 사례 탭 전용 반응형 CSS 추가

## 테스트 방법

```bash
node --check frontend/route-detail.js
```

로컬 서버 실행 후 아래 주소에서 확인합니다.

```text
http://127.0.0.1:8765/frontend/route-detail.html
```

검증 기준:

- `과거 사례` 탭을 클릭하면 과거 사례 화면이 표시됩니다.
- `요약`, `특보별 분석`, `과거 사례` 탭이 서로 전환됩니다.
- 필터의 label과 select가 연결되어 있습니다.
- 좁은 화면에서 표와 차트가 깨지지 않고 스크롤 또는 세로 배치됩니다.

## 새롭게 배운 개념

- 탭 패널 확장
- 필터 폼 접근성
- 과거 사례 비교 UI
- 미니 막대 차트

## 실무에서는

실무에서는 유사도 점수와 과거 사례 비교 데이터를 프론트엔드에서 고정하지 않고 분석 API에서 받아 표시합니다. 유사도 산정 기준도 화면에 설명하고, 실제 운영 판단에 쓰이는 경우에는 기준 변경 이력을 함께 관리하는 것이 좋습니다.

## 개선 가능한 부분

- 필터 조회 동작 구현
- 페이지네이션 실제 데이터 연결
- 유사도 산정 기준 상세 모달 구현
- 상세 비교 보기 페이지 연결

## 다음 작업

- 구간 상세 탭 전체 브라우저 시각 검수
- 구간 상세 mock/API 데이터 연결 설계
- RAG 심층 분석 화면 설계

## 복습 문제

1. 과거 사례 필터에서 `label`과 `select`를 연결해야 하는 이유는 무엇인가요?
2. 유사도 점수를 화면에 표시할 때 함께 제공해야 하는 설명은 무엇일까요?
3. 표가 좁은 화면에서 깨지지 않게 만드는 방법에는 어떤 것들이 있을까요?

## 오늘 배운 내용

- 과거 사례 목록 UI
- 필터 폼 접근성
- 유사도 기반 비교 카드
- 반응형 테이블 처리

## Change Log

2026-07-09

- 구간 상세 과거 사례 탭 화면 추가
- 과거 사례 필터, 목록, 비교 차트, 유사 사례 카드 구현

## Timestamp

2026-07-09 12:40:00 (KST)

---

# 구간 상세 특보별 분석 차트 Mock 연결 작업 요약

# 개요

구간 상세 화면의 `특보별 분석` 탭에 있는 가로 막대 차트 2개를 mock 데이터와 연결했습니다.

연결한 차트:

- 특보별 평균 지연 시간
- 특보별 운행 중단률

# 구현 목적

특보별 분석 탭의 차트는 기존에 HTML 정적 값으로 표시되고 있었습니다.

구간 상세 화면이 `segment_id`에 따라 다른 구간 데이터를 보여주도록 바뀌었기 때문에, 특보별 차트도 선택된 구간의 `by_alert[]` 데이터를 기준으로 렌더링되어야 합니다.

# 구현 내용

- `frontend/route-detail.html`
  - 평균 지연 시간 가로 막대 차트에 `data-route-detail-alert-delay-chart` 추가
  - 운행 중단률 가로 막대 차트에 `data-route-detail-alert-stop-chart` 추가

- `frontend/route-detail.js`
  - `renderRouteAlertCharts()` 추가
  - `createHorizontalChartRow()` 추가
  - `renderHorizontalChart()` 추가
  - `by_alert[].avg_delay`로 평균 지연 차트 렌더링
  - `by_alert[].stop_rate`로 운행 중단률 차트 렌더링
  - 표의 지연 증가량, 운행 중단률 칸도 같은 mock 필드 재사용

- `mock/segments_details.json`
  - 각 `by_alert` 항목에 `delay_increase` 추가
  - 각 `by_alert` 항목에 `stop_rate` 추가

# 코드 설명

## 왜 필요한가

특보별 분석 탭은 구간별로 특보가 운행에 미치는 영향을 비교하는 화면입니다.

차트가 정적 값으로 남아 있으면 `천안→대전`, `밀양→부산`처럼 다른 구간을 선택해도 동일한 막대 그래프가 보이게 됩니다.

## 어떤 원리인가

1. URL의 `segment_id`로 현재 구간 상세 데이터를 찾습니다.
2. 선택 구간의 `by_alert[]` 배열을 읽습니다.
3. 평균 지연 시간 차트는 `avg_delay`를 기준으로 막대 너비를 계산합니다.
4. 운행 중단률 차트는 `stop_rate * 100` 값을 기준으로 막대 너비를 계산합니다.
5. 기존 axis 요소는 유지하고, row만 mock 데이터 기준으로 다시 생성합니다.

# API

API 변경 사항은 없습니다.

사용한 mock 데이터:

- `GET ../mock/segments_details.json`

확장된 mock 필드:

```json
{
  "by_alert": [
    {
      "alert_type": "호우",
      "alert_level": "경보",
      "avg_delay": 14.6,
      "delay_increase": 9.8,
      "stop_rate": 0.08,
      "sample_n": 37
    }
  ]
}
```

# Database

DB 변경 사항은 없습니다.

# 테스트 방법

1. JavaScript 문법 검사

```bash
node --check frontend/route-detail.js
```

예상 결과:

- 오류 없이 종료됩니다.

2. 특보별 차트 mock 데이터 존재 검사

```bash
node -e "const fs=require('fs'); const data=JSON.parse(fs.readFileSync('mock/segments_details.json','utf8')); const bad=data.segments.filter((s)=>!Array.isArray(s.by_alert)||s.by_alert.some((a)=>!Number.isFinite(a.avg_delay)||!Number.isFinite(a.delay_increase)||!Number.isFinite(a.stop_rate))); console.log('segments:', data.segments.length); console.log('bad alert chart data:', bad.length); if (bad.length) process.exit(1);"
```

검증 결과:

```text
segments: 6
bad alert chart data: 0
```

3. 대표 구간 값 확인

```text
daejeon-gimcheon_gumi 호우 경보 14.6 9.8 8.0%
cheonan-daejeon 호우 경보 11.3 7.1 5.0%
miryang-busan 호우 경보 5.4 2.9 0.0%
```

4. HTTP 경로 검사

```text
/frontend/route-detail.html?segment_id=daejeon-gimcheon_gumi=200
/frontend/route-detail.js=200
/mock/segments_details.json=200
```

# 주의사항

이번 작업은 특보별 분석 탭의 가로 막대 차트만 연결했습니다.

과거 사례 탭의 미니 비교 차트는 아직 정적 데이터가 남아 있습니다.

# 변경 이력

2026-07-09

- 특보별 평균 지연 시간 차트 mock 연결
- 특보별 운행 중단률 차트 mock 연결
- `by_alert` mock 필드 확장

# 작업 요약

## 완료한 내용

- 특보별 분석 가로 막대 차트 mock 데이터 연결
- `by_alert[].delay_increase`, `by_alert[].stop_rate` 추가
- 특보별 분석 표 일부 칸 mock 데이터 재사용
- 문법 및 mock 구조 검증
- HTTP 경로 검증

## 수정한 파일

- `frontend/route-detail.html`
- `frontend/route-detail.js`
- `mock/segments_details.json`
- `.docs/Frontend.md`

## 구현 이유

특보별 차트는 구간 상세 화면의 핵심 분석 요소입니다.

구간별 mock 데이터와 연결하면 선택 구간에 따라 차트, 표, 요약 지표가 같은 데이터 기준으로 표시됩니다.

## 변경 사항

- 정적 가로 막대 차트를 DOM 기반 렌더링으로 변경
- 평균 지연과 운행 중단률을 `by_alert[]`에서 계산
- 데이터 없음 상태 fallback 메시지 추가

## 새롭게 배운 개념

- Horizontal Bar Chart
- Data-driven DOM Rendering
- Shared Mock Field Reuse

## 실무에서는

실무에서는 같은 지표를 표와 차트에서 함께 사용할 때 데이터 소스를 하나로 맞춥니다.

프론트엔드에서 표시 형식만 다르게 만들고, 실제 값은 같은 API 응답 필드를 재사용하는 방식이 유지보수에 유리합니다.

## 개선 가능한 부분

- 차트 axis 값을 데이터 최대값에 따라 동적으로 계산
- 과거 사례 비교 미니 차트 mock 연결
- 시각 회귀 테스트 추가

## 다음 작업

- 과거 사례 탭의 미니 비교 차트 mock 연결

## 복습 문제

1. 표와 차트가 같은 mock 필드를 재사용하면 어떤 장점이 있나요?
2. `stop_rate`를 화면에 표시할 때 왜 `* 100` 변환이 필요한가요?
3. 가로 막대 차트에서 axis를 유지하고 row만 다시 생성한 이유는 무엇인가요?

## 오늘 배운 내용

- Horizontal Chart Rendering
- Shared Data Source
- Rate Formatting

## Change Log

2026-07-09

- 구간 상세 특보별 분석 차트 mock 연결
- 문서 업데이트

## Timestamp

2026-07-09 17:49:07 (KST)

---

# 구간 상세 과거 사례 미니 비교 차트 Mock 연결 작업 요약

# 개요

구간 상세 화면의 `과거 사례` 탭에 있는 미니 비교 차트 4개를 mock 데이터와 연결했습니다.

연결한 차트:

- 평균 지연 시간 비교
- 지연 증가량 비교
- 운행 중단률 비교
- 누적 강수량 비교

# 구현 목적

과거 사례 탭의 미니 차트는 기존에 HTML 정적 값으로 표시되고 있었습니다.

구간 상세 화면이 `segment_id` 기준으로 여러 구간을 지원하므로, 과거 사례 비교 차트도 선택된 구간의 `cases[]` 데이터를 기준으로 바뀌어야 합니다.

# 구현 내용

- `frontend/route-detail.html`
  - 미니 비교 차트 4개에 `data-route-detail-history-chart` 속성 추가

- `frontend/route-detail.js`
  - `renderRouteHistoryCharts()` 추가
  - `renderMiniChart()` 추가
  - `createMiniBar()` 추가
  - 과거 사례 상위 3건과 현재 예측값을 비교하도록 렌더링
  - 과거 사례 표의 강수량, 지연 증가량, 운행 중단률, 영향 열차 칸을 mock 필드와 연결

- `mock/segments_details.json`
  - 구간별 `current_rain_mm` 추가
  - `cases[]` 항목에 `rain_mm`, `delay_increase`, `stop_rate`, `affected_trains` 추가

# 코드 설명

## 왜 필요한가

과거 사례 비교 차트는 현재 상황과 유사한 과거 사례를 빠르게 비교하는 영역입니다.

차트가 정적 값이면 다른 구간 상세로 이동해도 과거 사례 비교가 바뀌지 않아 분석 화면의 신뢰도가 떨어집니다.

## 어떤 원리인가

1. 선택된 구간의 `cases[]`에서 상위 3건을 가져옵니다.
2. 현재 예측값은 선택 구간의 요약 지표와 `current_rain_mm`을 사용합니다.
3. 각 차트별 최대값을 기준으로 막대 높이를 계산합니다.
4. 과거 사례 3개와 현재 예측 1개를 같은 차트에 표시합니다.
5. 과거 사례 표도 같은 `cases[]` 필드를 사용해 갱신합니다.

# API

API 변경 사항은 없습니다.

사용한 mock 데이터:

- `GET ../mock/segments_details.json`
- `GET ../mock/vulnerability_segments.json`

확장된 mock 필드:

```json
{
  "current_rain_mm": 126.4,
  "cases": [
    {
      "date": "2026-06-28",
      "alert_type": "호우",
      "rain_mm": 162.3,
      "delay_min": 19,
      "delay_increase": 13.4,
      "stop_rate": 0.089,
      "affected_trains": 36
    }
  ]
}
```

# Database

DB 변경 사항은 없습니다.

# 테스트 방법

1. JavaScript 문법 검사

```bash
node --check frontend/route-detail.js
```

예상 결과:

- 오류 없이 종료됩니다.

2. 과거 사례 비교 차트 mock 데이터 존재 검사

```bash
node -e "const fs=require('fs'); const data=JSON.parse(fs.readFileSync('mock/segments_details.json','utf8')); const bad=data.segments.filter((s)=>!Number.isFinite(s.current_rain_mm)||!Array.isArray(s.cases)||s.cases.some((c)=>!Number.isFinite(c.rain_mm)||!Number.isFinite(c.delay_min)||!Number.isFinite(c.delay_increase)||!Number.isFinite(c.stop_rate)||!Number.isFinite(c.affected_trains))); console.log('segments:', data.segments.length); console.log('bad history chart data:', bad.length); if (bad.length) process.exit(1);"
```

검증 결과:

```text
segments: 6
bad history chart data: 0
```

3. 대표 구간 값 확인

```text
daejeon-gimcheon_gumi currentRain 126.4 case 2026-06-28 162.3 19 13.4 8.9% 36
cheonan-daejeon currentRain 104.8 case 2026-06-26 137.5 15 9.2 6.1% 31
miryang-busan currentRain 52.7 case 2026-06-16 74.3 7 3.8 0.0% 9
```

4. HTTP 경로 검사

```text
/frontend/route-detail.html?segment_id=daejeon-gimcheon_gumi=200
/frontend/route-detail.js=200
/mock/segments_details.json=200
```

# 주의사항

현재 예측의 지연 증가량은 기존 구간 요약 지표인 `avg_delay_incr`를 재사용합니다.

실제 API 설계 단계에서는 평균 지연 시간과 지연 증가량을 별도 필드로 분리하는 것이 더 명확합니다.

# 변경 이력

2026-07-09

- 과거 사례 미니 비교 차트 mock 연결
- 과거 사례 표 상세 필드 mock 연결
- 구간별 현재 누적 강수량 mock 추가

# 작업 요약

## 완료한 내용

- 과거 사례 미니 차트 4개 mock 데이터 연결
- 과거 사례 표의 비어 있던 지표 칸 연결
- 구간별 `current_rain_mm` 추가
- `cases[]` 상세 필드 확장
- 문법 및 mock 구조 검증
- HTTP 경로 검증

## 수정한 파일

- `frontend/route-detail.html`
- `frontend/route-detail.js`
- `mock/segments_details.json`
- `.docs/Frontend.md`

## 구현 이유

과거 사례 탭의 표와 차트가 같은 데이터를 사용해야 상세 화면의 일관성이 높아집니다.

사용자는 현재 예측값과 과거 사례를 같은 기준으로 비교할 수 있습니다.

## 변경 사항

- 정적 미니 막대 차트를 DOM 기반 렌더링으로 변경
- 과거 사례 상위 3건과 현재 예측값 비교
- 과거 사례 표에 누적 강수량, 운행 중단률, 영향 열차 수 표시

## 새롭게 배운 개념

- Mini Bar Chart Rendering
- Historical Case Comparison
- Current vs Historical Metrics

## 실무에서는

실무에서는 과거 사례 비교용 데이터와 현재 예측 데이터를 API에서 명확히 분리해 내려주는 편이 좋습니다.

프론트엔드는 같은 차트 컴포넌트에 데이터만 바꿔 넣는 구조로 만들면 유지보수가 쉬워집니다.

## 개선 가능한 부분

- 평균 지연 시간과 지연 증가량 필드 분리
- 유사도 기준 API 설계
- 과거 사례 상세 비교 페이지 연결

## 다음 작업

- 구간 상세 화면 전체 mock 연결 최종 검수

## 복습 문제

1. 과거 사례 표와 차트가 같은 `cases[]` 데이터를 사용하면 어떤 장점이 있나요?
2. 현재 예측값과 과거 사례값을 한 차트에서 비교할 때 주의할 점은 무엇인가요?
3. 실제 API에서는 왜 평균 지연 시간과 지연 증가량을 별도 필드로 분리하는 것이 좋을까요?

## 오늘 배운 내용

- Historical Comparison Chart
- Shared Case Data
- Current Forecast Comparison

## Change Log

2026-07-09

- 구간 상세 과거 사례 미니 비교 차트 mock 연결
- 문서 업데이트

## Timestamp

2026-07-09 17:53:12 (KST)

---

# 구간 상세 화면 전체 Mock 연결 최종 검수 작업 요약

# 개요

구간 상세 화면의 전체 mock 데이터 연결 상태를 최종 검수했습니다.

검수 범위:

- 구간 선택 기준 `segment_id`
- 상단 제목, breadcrumb, 요약 카드
- 주요 지표 카드
- 요약 탭 선 그래프와 막대 그래프
- 특보별 분석 표와 가로 막대 차트
- 과거 사례 표와 미니 비교 차트
- 대시보드에서 구간 상세로 이동하는 HTTP 경로

# 구현 목적

여러 단계로 나누어 연결한 구간 상세 mock 데이터가 화면 전체에서 같은 기준으로 동작하는지 확인하기 위함입니다.

특히 `vulnerability_segments.json`과 `segments_details.json`이 같은 `segment_id`를 공유하므로, 두 mock 파일의 참조 무결성이 중요합니다.

# 구현 내용

이번 단계에서는 기능 코드를 새로 추가하지 않고 검수와 문서화를 진행했습니다.

검수한 파일:

- `frontend/route-detail.html`
- `frontend/route-detail.js`
- `frontend/dashboard.js`
- `mock/segments_details.json`
- `mock/vulnerability_segments.json`

# 코드 설명

## 왜 필요한가

구간 상세 화면은 여러 종류의 데이터를 함께 표시합니다.

요약 지표는 `vulnerability_segments.json`에서 가져오고, 차트와 상세 표는 `segments_details.json`에서 가져옵니다.

두 데이터의 `segment_id`가 맞지 않거나 특정 필드가 빠지면 화면 일부가 비거나 다른 구간의 데이터를 표시할 수 있습니다.

## 어떤 원리인가

1. JavaScript 문법 오류를 확인합니다.
2. 두 mock 파일의 `segment_id`가 서로 일치하는지 확인합니다.
3. 상세 mock에 필요한 차트/표 필드가 모두 존재하는지 확인합니다.
4. HTML에 렌더링 대상 `data-*` 선택자가 존재하는지 확인합니다.
5. 대표 구간 3개의 계산값을 확인합니다.
6. 로컬 HTTP 서버에서 실제 접근 경로가 200으로 응답하는지 확인합니다.

# API

API 변경 사항은 없습니다.

검수한 mock 데이터:

- `GET ../mock/vulnerability_segments.json`
- `GET ../mock/segments_details.json`

# Database

DB 변경 사항은 없습니다.

# 테스트 방법

1. JavaScript 문법 검사

```bash
node --check frontend/route-detail.js
node --check frontend/dashboard.js
```

예상 결과:

- 오류 없이 종료됩니다.

2. `segment_id` 참조 무결성 및 상세 구조 검사

검증 결과:

```text
vulnerability segments: 6
detail segments: 6
missing details: 0
missing summaries: 0
bad detail structures: 0
```

3. 상세 지표 필드 검사

검증 결과:

```text
bad metric fields: 0
```

4. 대표 구간 값 확인

검증 결과:

```text
daejeon-gimcheon_gumi | 대전→김천(구미) | 14.6분 | 8.0% | 7 hourly | 7 trend | 3 alerts | 3 cases | 126.4mm
cheonan-daejeon | 천안→대전 | 11.3분 | 5.0% | 7 hourly | 7 trend | 3 alerts | 3 cases | 104.8mm
miryang-busan | 밀양→부산 | 5.4분 | 0.0% | 7 hourly | 7 trend | 3 alerts | 3 cases | 52.7mm
```

5. HTTP 경로 검사

검증 결과:

```text
/frontend/route-detail.html?segment_id=daejeon-gimcheon_gumi=200
/frontend/route-detail.html?segment_id=cheonan-daejeon=200
/frontend/route-detail.html?segment_id=miryang-busan=200
/frontend/route-detail.js=200
/mock/segments_details.json=200
/mock/vulnerability_segments.json=200
```

# 주의사항

이번 검수는 정적 분석과 HTTP 응답 확인 중심입니다.

브라우저에서 실제 렌더링된 텍스트와 차트 픽셀을 확인하는 Playwright 기반 시각 검수는 아직 별도 자동화하지 않았습니다.

# 변경 이력

2026-07-09

- 구간 상세 화면 전체 mock 연결 최종 검수
- `segment_id` 참조 무결성 확인
- 차트/테이블 필드 완성도 확인
- 대표 구간 계산값 문서화

# 작업 요약

## 완료한 내용

- 구간 상세 JS 문법 검증
- dashboard JS 문법 검증
- 두 mock 파일 간 `segment_id` 참조 무결성 검증
- 상세 mock 필드 완성도 검증
- HTML 렌더링 선택자 존재 확인
- 대표 구간 3개 계산값 확인
- HTTP 경로 검증
- 문서화

## 수정한 파일

- `.docs/Frontend.md`

## 구현 이유

구간 상세 화면의 mock 연결 작업이 여러 단계로 진행되었기 때문에, 최종적으로 전체 데이터 흐름을 한 번에 검증해야 합니다.

이 검수를 통해 현재 구간 상세 화면은 선택된 `segment_id` 기준으로 요약, 차트, 표가 같은 구간 데이터를 표시할 수 있음을 확인했습니다.

## 변경 사항

- 기능 코드 변경 없음
- 최종 검수 결과 문서 추가

## 새롭게 배운 개념

- End-to-end Mock Validation
- Cross-file Reference Integrity
- Static Rendering Selector Check

## 실무에서는

실무에서는 이런 검수를 CI에 포함해 mock 데이터나 API contract가 깨졌을 때 바로 확인할 수 있게 만듭니다.

특히 상세 화면은 URL 파라미터, 목록 화면 링크, 상세 API 응답이 모두 같은 id 체계를 사용해야 안정적으로 동작합니다.

## 개선 가능한 부분

- Playwright로 실제 화면 텍스트 검증 자동화
- 차트 DOM 렌더링 결과 검증 자동화
- mock schema 검증 스크립트 분리
- RAG 심층 분석 화면 mock 연결

## 다음 작업

- 구간 상세 mock 연결 변경사항 커밋 준비

## 복습 문제

1. `segment_id` 참조 무결성 검사가 상세 화면에서 중요한 이유는 무엇인가요?
2. HTTP 응답 검증과 실제 화면 렌더링 검증은 어떤 차이가 있나요?
3. mock schema 검증을 CI에 넣으면 어떤 장점이 있나요?

## 오늘 배운 내용

- Mock Validation
- Reference Integrity
- HTTP Path Verification

## Change Log

2026-07-09

- 구간 상세 화면 전체 mock 연결 최종 검수
- 문서 업데이트

## Timestamp

2026-07-09 17:55:23 (KST)

---

# 구간 상세 구간 변경 버튼 작업 요약

## 완료한 내용

- 구간 상세 화면의 구간 정보 카드에 `구간 변경` 버튼을 추가했습니다.
- 버튼에는 화살표 아이콘을 넣지 않고 텍스트만 중앙 정렬했습니다.
- 버튼 전용 클래스 `route-info-card__change-button`을 추가했습니다.
- 모바일 화면에서 버튼이 카드 폭에 맞게 확장되도록 반응형 스타일을 추가했습니다.

## 수정한 파일

- `frontend/route-detail.html`
- `frontend/style.css`
- `.docs/Frontend.md`

## 구현 이유

현재 구간을 다른 구간으로 바꾸는 사용자 흐름의 진입점을 구간 정보 카드 안에 배치하기 위해 버튼을 추가했습니다.

## 변경 사항

- 노선 시각화와 구간 메타데이터 사이에 `구간 변경` 버튼 추가
- 버튼 크기 `104px × 40px`, border `#D1D5DB`, radius `6px`, 텍스트 중앙 정렬 적용
- 접근성을 위해 `aria-label="조회할 구간 변경"` 추가

## 테스트 방법

```bash
node --check frontend/route-detail.js
```

검증 기준:

- 구간 정보 카드 안에 `구간 변경` 버튼이 표시됩니다.
- 버튼 내부에 아이콘이 없어야 합니다.
- 버튼 텍스트가 가운데 정렬되어야 합니다.
- 모바일 화면에서는 버튼이 카드 폭에 맞게 표시되어야 합니다.

## 새롭게 배운 개념

- 버튼 접근성 라벨
- Flexbox 중앙 정렬
- 카드 내부 액션 버튼 배치

## 실무에서는

실무에서는 이 버튼을 클릭했을 때 구간 검색 모달이나 구간 선택 드롭다운을 열도록 연결합니다. 현재는 UI 진입점만 만들고, 실제 구간 변경 로직은 이후 데이터/API 연결 단계에서 붙이는 방식이 안전합니다.

## 개선 가능한 부분

- 구간 변경 모달 구현
- 구간 검색 API 연결
- 선택한 구간에 따른 상세 데이터 갱신

## 다음 작업

- 구간 변경 버튼 클릭 동작 설계
- 구간 목록 mock/API 데이터 구조 설계

## 복습 문제

1. 버튼 안에 아이콘 없이 텍스트만 둘 때 접근성에서 확인해야 할 점은 무엇인가요?
2. `justify-content: center`와 `align-items: center`는 각각 어떤 방향의 정렬을 담당하나요?
3. 구간 변경 기능을 실제 데이터와 연결하려면 어떤 API가 필요할까요?

## 오늘 배운 내용

- 카드 내부 버튼 배치
- 버튼 중앙 정렬
- 반응형 버튼 폭 처리

## Change Log

2026-07-10

- 구간 상세 화면 구간 변경 버튼 추가

## Timestamp

2026-07-10 00:00:00 (KST)
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

# 구간 상세 상단 요약 영역 폭 보정 작업 요약

## 완료한 내용

- 구간 상세 화면의 `현재 위험도` 카드가 콘텐츠 최대 폭 `1312px` 밖으로 밀려나지 않도록 상단 요약 레이아웃을 보정했습니다.
- 최대 폭에서 구간 정보 `944px`, 간격 `16px`, 위험도 카드 `352px`로 배치되도록 구성했습니다.
- `1180px` 이하에서는 구간 정보와 위험도 카드를 세로로 배치하도록 반응형 규칙을 복구했습니다.

## 수정한 파일

- `frontend/style.css`
- `.docs/Frontend.md`

## 구현 이유

구간 변경 버튼 추가 후 왼쪽 정보 카드의 내부 최소 너비가 증가하면서 오른쪽 위험도 카드가 콘텐츠 영역 밖으로 밀릴 수 있었습니다. 부모 레이아웃의 열 크기를 명시하고 내부 flex 요소에 축소 가능한 최소 너비를 적용해 최대 콘텐츠 폭을 지키도록 수정했습니다.

## 변경 사항

- `.route-summary-grid`를 최대 `1312px`의 2열 Grid로 변경
- `.route-info-card`, 메타 정보 영역에 `min-width: 0` 적용
- 메타 값이 좁은 화면에서 레이아웃을 밀지 않도록 말줄임 처리
- `1180px` 및 `768px` 반응형 규칙 복구

## 테스트 방법

- `git diff --check`로 공백 오류를 검사합니다.
- CSS 여는 중괄호와 닫는 중괄호 개수가 같은지 확인합니다.
- 브라우저에서 화면 폭을 변경하며 위험도 카드가 본문 오른쪽 경계를 벗어나지 않는지 확인합니다.

예상 결과:

- 넓은 화면에서 상단 요약 영역 전체가 `1312px` 안에 표시됩니다.
- `1180px` 이하에서 위험도 카드가 구간 정보 카드 아래로 이동합니다.
- 모바일에서 노선 시각화와 구간 변경 버튼이 카드 폭을 넘지 않습니다.

## 구현 이유 및 원리

CSS Grid의 열 합계를 콘텐츠 토큰과 동일하게 맞추고, 내부 flex 항목의 기본 최소 크기를 해제했습니다. 이 방식은 텍스트 길이가 달라져도 오른쪽 고정 카드가 부모 영역 밖으로 밀리는 현상을 방지합니다.

## 장점

- 디자인 가이드의 최대 콘텐츠 폭을 유지합니다.
- 데이터 문자열이 길어져도 레이아웃 이탈 가능성이 줄어듭니다.
- 기존 모바일 전환 구조를 유지합니다.

## 단점

- 좁은 데스크톱 폭에서는 긴 메타 값이 말줄임 처리될 수 있습니다.

## 다른 구현 방법

전체 영역을 flex로 유지하고 왼쪽 카드에 `calc(100% - 368px)`를 적용할 수도 있습니다. 현재 구현은 열 관계가 명시적인 Grid가 상단 2열 구조를 표현하기에 더 적합합니다.

## 새롭게 배운 개념

- Grid 열 크기와 콘텐츠 최대 폭의 관계
- flex item의 기본 최소 너비와 `min-width: 0`
- 반응형 breakpoint에서 레이아웃 방향 전환

## 실무에서는

실무에서는 긴 API 데이터와 번역 문자열을 포함한 상태로 여러 viewport를 시각 회귀 테스트합니다. 고정 폭 카드와 유동 폭 카드가 함께 있을 때는 부모의 최대 폭뿐 아니라 자식의 최소 콘텐츠 크기도 함께 제어합니다.

## 개선 가능한 부분

- Playwright 기반 데스크톱·태블릿·모바일 스크린샷 회귀 테스트 추가
- 메타 값 전체 내용을 확인할 수 있는 접근 가능한 tooltip 검토

## 다음 작업

- 로컬 브라우저에서 `1312px`, `1180px`, `768px` 전후 화면 시각 검수

## 프로젝트 진행률

■■■■■■■■□□ 80%

완료:

- 메인 대시보드
- 역 상세 화면
- 구간 상세 화면과 탭
- 구간 변경 기능
- 상단 요약 영역 폭 보정

진행 중:

- 상세 화면 반응형 시각 검수

예정:

- 백엔드 API 연동 및 데이터 상태 검증

## 복습 문제

1. flex item에 `min-width: 0`이 필요한 상황은 언제인가요?
2. `944px + 16px + 352px` 구조가 `1312px` 경계를 지키는 이유는 무엇인가요?
3. 고정 열과 유동 열이 섞인 레이아웃에서 Grid가 유용한 이유는 무엇인가요?

## 오늘 배운 내용

- CSS Grid 열 제약
- Flexbox 최소 콘텐츠 크기
- 반응형 레이아웃 경계 관리

## README 반영 여부

이번 작업은 기존 화면의 레이아웃 오류 수정이므로 README에 별도 기능 설명을 추가하지 않습니다.

## 추천 커밋 메시지

`fix: 구간 상세 현재 위험도 카드의 콘텐츠 폭 이탈 수정`

## Change Log

2026-07-10

- 구간 상세 상단 요약 영역을 최대 `1312px`로 제한
- 현재 위험도 카드의 레이아웃 이탈 수정
- 태블릿 및 모바일 반응형 규칙 복구

## Timestamp

2026-07-10 09:54:57 (KST)
---

# 구간 상세 페이지 구간 변경 버튼 적용 범위 점검

## 작업 요약

### 완료한 내용

- 모든 구간 상세 진입 경로에서 `구간 변경` 버튼이 표시되는지 확인했습니다.
- `요약`, `특보별 분석`, `과거 사례` 탭 모두 공통 상단 요약 영역을 사용하는지 확인했습니다.
- 구간별 `segment_id`가 동일한 `route-detail.html` 템플릿으로 연결되는지 확인했습니다.

### 수정한 파일

- `.docs/Frontend.md`

### 구현 이유

구간 상세 화면은 구간마다 별도 HTML을 생성하지 않고 URL의 `segment_id`에 따라 데이터를 바꾸는 단일 템플릿 구조입니다. 따라서 버튼을 각 탭이나 구간마다 중복 추가하면 접근성 식별자와 이벤트가 중복될 수 있어 공통 상단에 한 번만 유지하는 것이 적절합니다.

### 변경 사항

- 애플리케이션 코드는 변경하지 않았습니다.
- 버튼 적용 범위와 공통 템플릿 구조의 검증 결과를 문서화했습니다.

### 테스트 및 검증

- `route-detail.html`에서 `data-route-change-open` 버튼이 탭 패널 바깥에 존재함을 확인했습니다.
- `dashboard.js`가 모든 구간 링크를 `route-detail.html?segment_id=...`로 생성함을 확인했습니다.
- `route-detail.js`가 URL의 `segment_id`를 읽고 동일한 버튼과 모달을 초기화함을 확인했습니다.
- `node --check frontend/route-detail.js` 문법 검사를 통과했습니다.

### 새롭게 배운 개념

- Query Parameter 기반 단일 상세 페이지
- 공통 레이아웃과 탭 패널의 DOM 범위
- 공통 버튼 중복 방지

### 실무에서는

동일한 상세 레이아웃에서 식별자만 바뀌는 경우 페이지를 복제하지 않고 라우트 파라미터 또는 쿼리 파라미터 기반 템플릿을 사용합니다. 공통 액션은 탭 패널 밖에 배치해 모든 상태에서 일관되게 제공합니다.

### 개선 가능한 부분

- 각 `segment_id`별 E2E 테스트 추가
- 세 탭에서 버튼 노출과 모달 열림을 확인하는 Playwright 테스트 추가

### 다음 작업

- 백엔드 구간 목록 API 연결 후 모든 실제 구간이 선택 목록에 표시되는지 검증

### 프로젝트 진행률

■■■■■■■■□□ 80%

완료:

- 모든 구간 상세 화면의 구간 변경 버튼 적용 범위 확인

진행 중:

- 상세 화면 반응형 시각 검수

예정:

- 백엔드 API 연동 및 E2E 테스트

### 복습 문제

1. 구간별 HTML을 복제하는 대신 `segment_id`를 사용하는 장점은 무엇인가요?
2. 공통 버튼을 탭 패널 밖에 배치해야 하는 이유는 무엇인가요?
3. 동일한 `data-route-change-open` 버튼을 여러 개 추가하면 현재 JavaScript 구조에서 어떤 문제가 생길 수 있나요?

### 오늘 배운 내용

- 단일 상세 페이지 템플릿
- Query Parameter 라우팅
- 공통 UI 이벤트 연결

### README 반영 여부

기존 기능의 적용 범위 점검이므로 README 변경은 필요하지 않습니다.

### 추천 커밋 메시지

문서 변경을 포함해 커밋할 경우: `docs: 구간 변경 버튼 적용 범위 점검 결과 기록`

## Change Log

2026-07-10

- 모든 구간 상세 화면의 구간 변경 버튼 적용 여부 확인
- 공통 템플릿 및 탭 구조 검증 결과 기록

## Timestamp

2026-07-10 10:03:47 (KST)
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
