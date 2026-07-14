# 역 상세 페이지 프론트엔드

# 개요

`Frontend.md`에서 페이지 책임에 따라 분리한 프론트엔드 구현 기록입니다.

# 구현 목적

역 상세 화면의 조회, 필터, 차트, 통계 및 Mock 데이터 연결 기록을 한 문서에서 관리합니다.

# 구현 내용

- 역 선택과 URL Query String
- 주요 지표와 차트
- 특보별 영향 통계
- 과거 사례와 데이터 매핑

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


# 역 상세 차트 Mock 연결 작업 요약

# 개요

역 상세 페이지의 정적 그래프 2개를 mock 데이터와 연결했습니다.

연결한 차트:

- 시간대별 평균 지연 시간
- 특보 발생 시 / 평상시 평균 지연 비교

# 구현 목적

기존 역 상세 그래프는 HTML에 고정된 `polyline`, tooltip, 막대 값으로 표시되고 있었습니다.

따라서 mock 데이터를 불러와도 그래프 값은 변하지 않았습니다.

이번 작업은 `station_details.json`에 차트용 mock 데이터를 추가하고, `station-detail.js`에서 해당 데이터를 DOM에 렌더링하도록 연결하기 위한 작업입니다.

# 구현 내용

- `mock/station_details.json`
  - `hourly_delay[]` 추가
  - `alert_delay_comparison[]` 추가

- `frontend/station-detail.html`
  - 선 그래프 polyline, point, tooltip에 렌더링용 `data-*` 속성 추가
  - 막대 그래프 plot 영역에 렌더링용 `data-*` 속성 추가

- `frontend/station-detail.js`
  - 선 그래프 좌표 계산 함수 추가
  - 평일/주말 polyline 렌더링 추가
  - tooltip과 강조 point 동적 갱신 추가
  - 특보별 평상시/특보 발생 시 평균 지연 막대 그래프 렌더링 추가
  - 선택한 역에 상세 차트 mock이 없을 때 빈 상태로 처리

# 코드 설명

## 왜 필요한가

역 상세 페이지의 요약 카드와 표는 mock 데이터와 연결되어 있었지만, 그래프는 정적 HTML 값으로 남아 있었습니다.

이 상태에서는 역을 변경하거나 mock 값을 수정해도 그래프가 바뀌지 않습니다.

## 어떤 원리인가

1. `station_details.json`에서 `hourly_delay[]`와 `alert_delay_comparison[]`를 읽습니다.
2. `hourly_delay[]`의 평일/주말 값을 SVG 좌표로 변환합니다.
3. 변환한 좌표를 `polyline points`에 반영합니다.
4. 마지막 평일 지점을 기준으로 tooltip과 point 위치를 갱신합니다.
5. `alert_delay_comparison[]`을 기준으로 평상시/특보 발생 시 막대 높이를 계산합니다.
6. 역 상세 화면 렌더링 시 차트도 함께 다시 렌더링합니다.

# API

API 변경 사항은 없습니다.

사용한 mock 데이터:

- `GET ../mock/station_details.json`

추가된 mock 필드:

```json
{
  "hourly_delay": [
    {
      "time": "00:00",
      "weekday_delay": 6.8,
      "holiday_delay": 5.4
    }
  ],
  "alert_delay_comparison": [
    {
      "alert_type": "호우",
      "normal_avg_delay": 8.2,
      "alert_avg_delay": 15.2
    }
  ]
}
```

# Database

DB 변경 사항은 없습니다.

# 테스트 방법

1. JavaScript 문법 검사

```bash
node --check frontend/station-detail.js
```

예상 결과:

- 오류 없이 종료됩니다.

2. 차트 mock 데이터 구조 검사

검증 결과:

```text
station: 대전
hourly points: 7
comparison groups: 4
bad chart data: 0
```

3. 대표 값 확인

검증 결과:

```text
last weekday: 5.9
rain compare: 8.2 15.2
```

4. HTTP 경로 검사

검증 결과:

```text
/frontend/station-detail.html?station_id=daejeon=200
/frontend/station-detail.js=200
/mock/station_details.json=200
/mock/vulnerability_stations.json=200
```

# 주의사항

현재 `station_details.json`은 대전역 상세 mock만 제공합니다.

다른 역을 선택했을 때 대전역 차트가 그대로 남지 않도록, 상세 차트 mock이 없는 역은 빈 데이터로 처리했습니다.

# 변경 이력

2026-07-10

- 역 상세 시간대별 평균 지연 시간 그래프 mock 연결
- 역 상세 특보 발생 시 / 평상시 평균 지연 비교 그래프 mock 연결
- 대전역 차트용 mock 데이터 추가

# 작업 요약

## 완료한 내용

- 역 상세 차트 mock 데이터 추가
- 시간대별 평균 지연 시간 선 그래프 연결
- 특보 발생 시 / 평상시 평균 지연 비교 막대 그래프 연결
- 선택 역에 상세 mock이 없을 때 빈 차트 처리
- 문법 및 mock 구조 검증
- HTTP 경로 검증

## 수정한 파일

- `frontend/station-detail.html`
- `frontend/station-detail.js`
- `mock/station_details.json`
- `.docs/Frontend.md`

## 구현 이유

그래프 값이 변하지 않는 원인은 mock 데이터 부족과 매핑 로직 부재였습니다.

이번 작업으로 역 상세 그래프가 `station_details.json`의 데이터를 기준으로 렌더링됩니다.

## 변경 사항

- 정적 SVG polyline을 mock 기반 렌더링 대상으로 변경
- 정적 막대 그래프를 mock 배열 기반 DOM 렌더링으로 변경
- 상세 mock이 없는 역의 차트 fallback 처리 추가

## 새롭게 배운 개념

- SVG Polyline Mapping
- Bar Chart DOM Rendering
- Station Detail Chart Fallback

## 실무에서는

실무에서는 역별 상세 차트 데이터를 API에서 `station_id` 기준으로 조회하는 구조가 적절합니다.

목록용 요약 데이터와 상세 차트 데이터를 분리하면 초기 로딩은 가볍게 유지하고, 상세 화면에서는 필요한 데이터만 가져올 수 있습니다.

## 개선 가능한 부분

- 다른 역의 상세 차트 mock 데이터 추가
- `station_details.json`을 역별 `stations[]` 구조로 확장
- Playwright 기반 실제 렌더링 검증 자동화

## 다음 작업

- 역 상세 mock을 여러 역 상세 데이터 구조로 확장

## 복습 문제

1. 그래프 값이 변하지 않을 때 mock 데이터 문제와 매핑 문제를 어떻게 구분할 수 있나요?
2. SVG `polyline points`는 어떤 방식으로 동적으로 계산하나요?
3. 상세 mock이 없는 역을 선택했을 때 fallback 처리가 필요한 이유는 무엇인가요?

## 오늘 배운 내용

- SVG Polyline
- Data-driven Chart Rendering
- Fallback Rendering

## Change Log

2026-07-10

- 역 상세 차트 mock 연결
- 문서 업데이트

## Timestamp

2026-07-10 10:20:53 (KST)

---


# 역 상세 과거 주요 사례 상세보기 버튼 제거 작업 요약

## 완료한 내용

- 역 상세 화면의 `과거 주요 사례` 목록에서 기능이 연결되지 않은 `상세보기` 버튼을 제거했습니다.
- JS에서 과거 사례 항목을 동적으로 렌더링할 때도 `상세보기` 버튼을 생성하지 않도록 정리했습니다.
- 더 이상 사용하지 않는 `station-history-item__button` CSS 규칙과 포커스/반응형 참조를 제거했습니다.

## 수정한 파일

- `frontend/station-detail.html`
- `frontend/station-detail.js`
- `frontend/style.css`
- `.docs/Frontend.md`

## 구현 이유

해당 버튼은 클릭 가능한 UI처럼 보였지만 실제 모달, 상세 패널, 페이지 이동 기능이 없었습니다. 사용자가 동작을 기대하고 눌렀을 때 아무 반응이 없으면 혼란을 줄 수 있으므로 버튼을 제거했습니다.

## 변경 사항

- 정적 HTML 예시 목록의 `상세보기` 버튼 제거
- `createHistoryItem()`에서 버튼 생성 및 append 로직 제거
- 버튼 전용 CSS 제거

## 새롭게 배운 개념

- Dead UI 제거
- 동적 렌더링 코드와 정적 fallback HTML 동시 정리
- 미사용 CSS 제거

## 실무에서는

실무에서는 기능이 아직 없는 버튼을 남기기보다 제거하거나 `disabled` 상태와 명확한 안내를 제공합니다. 현재 화면에서는 상세 기능 자체가 필요 없다고 판단했으므로 제거가 가장 단순하고 안전합니다.

## 개선 가능한 부분

- 추후 과거 사례 상세 분석이 필요해지면 상세 모달 또는 상세 패널로 별도 설계
- 과거 사례 항목 전체를 클릭 가능한 카드로 바꿀지 검토

## 다음 작업

- 구간 상세의 기능 없는 버튼/링크 정리
- 지도 카드 `전체 보기` 기능 여부 결정

## 프로젝트 진행률

■■■■■■■■□□ 80%

완료

- 역 상세 과거 주요 사례 `상세보기` 버튼 제거

진행 중

- 디자인만 있는 버튼/링크 정리

예정

- 구간 상세 과거 사례 필터/페이지네이션 점검

## 복습 문제

1. 기능이 없는 버튼을 화면에 남겨두면 어떤 UX 문제가 생길까요?
2. 정적 HTML과 JS 동적 렌더링을 함께 쓰는 화면에서 UI를 제거할 때 어디를 같이 확인해야 할까요?
3. 사용하지 않는 CSS를 제거하면 유지보수 측면에서 어떤 장점이 있을까요?

## 오늘 배운 내용

- Dead UI
- Dynamic Rendering Cleanup
- Unused CSS Cleanup

## README 반영 여부

기능 제거 범위가 화면 내부의 미동작 버튼 정리이므로 README 변경은 필요하지 않습니다.

## 추천 Commit Message

`refactor: 역 상세 과거 사례 상세보기 버튼 제거`

## Change Log

2026-07-10

- 역 상세 과거 주요 사례 상세보기 버튼 제거
- 관련 JS 생성 로직과 CSS 제거

## Timestamp

2026-07-10 10:58:06 (KST)

---


# 역 상세 페이지 경부선 고속 정차역 필터 개선

# 개요

역 상세 페이지의 역 변경 필터를 경부선 고속 정차역 전체로 확장하고 불필요한 주소, 목록 이동 버튼, 과거 주요 사례 영역을 제거했습니다.

# 구현 목적

- 대시보드 노선도와 역 상세 페이지가 동일한 정차역 체계를 사용하도록 합니다.
- 데이터 존재 여부와 무관하게 사용자가 모든 고속 정차역을 선택할 수 있도록 합니다.
- 현재 운영 범위에서 사용하지 않는 정보를 화면에서 제거합니다.

# 구현 내용

- 역 변경 필터에 서울, 광명, 천안아산, 오송, 대전, 김천(구미), 동대구, 경주, 울산, 부산을 순서대로 표시합니다.
- 각 역에 안정적인 `station_id`를 지정해 URL query parameter와 동기화합니다.
- mock에 취약도 데이터가 없는 역은 기존 빈 상태 렌더링을 사용합니다.
- 정차역 주소와 주소 렌더링 코드를 제거했습니다.
- 상단 `목록으로` 버튼을 제거했습니다.
- `과거 주요 사례` HTML과 JavaScript 렌더링 코드를 제거했습니다.

# 코드 설명

`GYEONGBU_HIGH_SPEED_STATIONS`를 역 선택의 기준 목록으로 사용합니다. 취약도 mock은 위험 지표 조회에만 사용하므로, mock에 없는 역도 필터에서 사라지지 않습니다. 역 ID와 이름 조회 함수는 기준 목록을 먼저 확인한 후 기존 데이터로 보완합니다.

장점은 화면 간 정차역 목록이 일관되고 결측 데이터가 탐색 기능을 제한하지 않는다는 점입니다. 단점은 정차역 목록이 프론트엔드에 중복 정의된다는 점이며, 실무 대안은 공통 노선 메타데이터 모듈이나 API를 사용하는 것입니다.

# API

새 API와 계약 변경은 없습니다. 선택 역은 `station_id` query parameter로 유지됩니다.

# Database

변경 사항이 없습니다.

# 주의사항

- 데이터가 없는 역을 선택하면 위험 지표와 차트는 정보 없음 상태로 표시됩니다.
- `mock/` 폴더는 수정하지 않았습니다.

# 변경 이력

2026-07-10

- 역 변경 필터에 고속 정차역 10개 적용
- 정차역 주소 제거
- 목록으로 버튼 제거
- 과거 주요 사례 제거

# 다음 작업

- 구간 상세 페이지의 전체 인접 구간 필터 적용
- 구간 거리 제거

# 작업 요약

## 완료한 내용

- 전체 고속 정차역 선택 기능
- 역 선택 URL 동기화
- 요청된 역 상세 UI 제거

## 수정한 파일

- `frontend/station-detail.html`
- `frontend/station-detail.js`
- `.docs/Frontend.md`

## 구현 이유

데이터 제공 범위와 탐색 가능한 노선 범위를 분리해 전체 정차역을 일관되게 조회하도록 했습니다.

## 변경 사항

- 기준 정차역 상수 추가
- 선택 옵션 생성 기준 변경
- 주소 및 과거 사례 관련 렌더링 제거

## 새롭게 배운 개념

- 기준 데이터와 측정 데이터의 분리
- URL 기반 화면 상태 유지
- 결측 데이터의 빈 상태 처리

## 실무에서는

노선과 정차역 메타데이터를 공통 API에서 받아 대시보드와 상세 페이지가 동일한 원천을 사용하도록 구성합니다.

## 개선 가능한 부분

- 공통 노선 메타데이터 모듈 도입
- 역별 상세 API 연결
- 역 선택 브라우저 자동화 테스트 추가

## 다음 작업

- 구간 상세 페이지 요구사항 구현

## 프로젝트 진행률

■■■■■□□□□□ 50%

완료

- 대시보드 변경
- 역 상세 페이지 변경

진행 중

- 구간 상세 페이지 변경 준비

예정

- 공통 사이드바 변경
- 전체 회귀 테스트

## 복습 문제

1. 정차역 기준 데이터와 위험도 데이터를 분리하면 어떤 장점이 있을까요?
2. 선택한 역을 URL query parameter로 관리하는 이유는 무엇일까요?
3. 데이터가 없는 역도 필터에 표시해야 하는 이유는 무엇일까요?

## 오늘 배운 내용

- Reference Data
- URL State
- Empty State

## README 반영 여부

기존 역 상세 화면 내부 변경이므로 README에는 별도 항목을 추가하지 않았습니다.

## 추천 Commit Message

`feat: 역 상세 고속 정차역 필터 및 화면 구성 개선`

## Change Log

2026-07-10

- 역 상세 페이지 경부선 고속 정차역 필터 및 불필요 영역 제거

## Timestamp

2026-07-10 15:04:42 (KST)

---


# 역 상세 역 변경 모달 적용

# 개요

역 상세 화면의 `역 변경` 기능을 구간 상세 화면과 동일한 오버레이 모달 방식으로 변경했습니다.

# 구현 목적

- 역과 구간 상세 화면의 대상 변경 경험을 일관되게 제공합니다.
- 사용자가 `적용하기`를 누르기 전에는 현재 화면의 역이 변경되지 않도록 합니다.
- 키보드와 보조 기술에서도 모달을 명확히 인식하고 닫을 수 있도록 합니다.

# 구현 내용

- 역 변경 버튼 클릭 시 중앙 모달과 배경 오버레이를 표시합니다.
- 경부선 고속 정차역 10개를 선택 목록에 표시합니다.
- `적용하기` 제출 시에만 `station_id`와 상세 화면을 갱신합니다.
- 닫기 버튼, 취소 버튼, 오버레이 클릭, Escape 키로 모달을 닫습니다.
- 열릴 때 select로 포커스를 옮기고 닫힐 때 역 변경 버튼으로 복귀합니다.
- 현재 역을 모달의 초기 선택값으로 사용합니다.

# 코드 설명

모달은 구간 변경 화면의 `route-change-modal` 프레젠테이션 스타일을 재사용합니다. `openStationChangeModal()`과 `closeStationChangeModal()`이 표시 상태 및 포커스를 관리하고, form submit handler가 선택한 역을 URL과 화면에 반영합니다.

장점은 기존 디자인과 반응형 스타일을 중복 없이 활용한다는 점입니다. 단점은 공통 모달 클래스 이름이 구간 중심으로 작성되어 있다는 점이며, 실무에서는 공통 `entity-change-modal` 컴포넌트로 분리할 수 있습니다.

# API

변경 사항이 없습니다. 기존 `station_id` query parameter를 사용합니다.

# Database

변경 사항이 없습니다.

# 주의사항

- 선택값 변경만으로는 상세 화면이 바뀌지 않으며 `적용하기`가 필요합니다.
- 취소하거나 닫으면 기존 역을 유지합니다.
- `mock/` 폴더는 수정하지 않았습니다.

# 변경 이력

2026-07-10

- 역 변경 인라인 선택기를 모달 방식으로 변경
- 닫기 및 포커스 동작 추가
- 버튼과 dialog의 접근성 연결 추가

# 다음 작업

- 구간 상세 전체 고속 구간 필터 적용
- 구간 거리 제거

# 작업 요약

## 완료한 내용

- 역 변경 모달 UI
- 적용·취소·닫기 상호작용
- 전체 정차역 선택 목록
- 접근성 속성과 포커스 복귀

## 수정한 파일

- `frontend/station-detail.html`
- `frontend/station-detail.js`
- `.docs/Frontend.md`

## 구현 이유

구간 상세 화면과 동일한 변경 패턴을 제공하고 사용자가 선택을 확정한 시점에만 화면을 갱신하기 위해 구현했습니다.

## 변경 사항

- 인라인 선택 UI 제거
- 역 변경 dialog 추가
- modal open, close, submit 이벤트 연결
- `aria-controls`, `aria-expanded`, `aria-modal` 적용

## 새롭게 배운 개념

- Modal Dialog
- Deferred Apply Pattern
- Focus Restoration

## 실무에서는

여러 화면에서 같은 모달 패턴을 사용할 경우 공통 컴포넌트로 추출하고 포커스 트랩까지 포함해 접근성 동작을 표준화합니다.

## 개선 가능한 부분

- 공통 대상 변경 모달 컴포넌트 분리
- 모달 내부 포커스 트랩 추가
- 브라우저 기반 키보드 접근성 테스트 추가

## 다음 작업

- 구간 상세 페이지 요구사항 구현

## 프로젝트 진행률

■■■■■■□□□□ 60%

완료

- 대시보드 변경
- 역 상세 구성 변경
- 역 변경 모달 적용

진행 중

- 구간 상세 변경 준비

예정

- 공통 사이드바 변경
- 전체 회귀 테스트

## 복습 문제

1. select의 change 이벤트가 아니라 form submit에서 역을 적용하는 이유는 무엇일까요?
2. 모달을 닫은 뒤 실행 버튼으로 포커스를 돌려보내야 하는 이유는 무엇일까요?
3. `aria-modal`과 `aria-controls`는 보조 기술에 어떤 정보를 제공할까요?

## 오늘 배운 내용

- Modal Dialog
- Form Submission
- Accessible Focus Management

## README 반영 여부

역 상세 내부 상호작용 변경이므로 README에는 별도 항목을 추가하지 않았습니다.

## 추천 Commit Message

`feat: 역 상세 역 변경 모달 적용`

## Change Log

2026-07-10

- 역 상세 화면에 구간 변경과 동일한 모달 패턴 적용

## Timestamp

2026-07-10 15:10:45 (KST)

---


---

## Timestamp

2026-07-10 17:11:58 KST

---

# 개요

역 상세 페이지 제목에 최근 업데이트 시간을 추가했습니다.

# 구현 목적

사용자가 현재 표시된 역 위험 정보의 데이터 기준 시점을 바로 확인할 수 있도록 합니다.

# 구현 내용

- `page-title__updated` UI 추가
- `mock/alerts_active.json` 병렬 요청 추가
- `updated_at`을 Asia/Seoul 기준 날짜·시간으로 표시
- 값이 없거나 유효하지 않으면 `업데이트 정보 없음` 표시

# 코드 설명

기존 대시보드와 동일한 페이지 제목 스타일을 재사용하고, `Intl.DateTimeFormat`으로 시간을 변환합니다. 장점은 별도 라이브러리 없이 일관된 형식을 제공한다는 점입니다. 단점은 특보 갱신 시각을 역 데이터 갱신 시각으로 함께 사용한다는 점입니다. 실무에서는 각 API 응답에 자체 `updated_at`을 제공하는 것이 더 정확합니다.

# API

API 변경은 없으며 기존 Mock 파일을 추가로 읽습니다.

# Database

변경 없음

# 주의사항

현재 표시 시간의 출처는 `alerts_active.json.updated_at`입니다.

# 변경 이력

2026-07-13 - 역 상세 최근 업데이트 추가

# 다음 작업

역 상세 전용 API에 `updated_at` 추가 검토

# 작업 요약

## 완료한 내용

- 최근 업데이트 UI와 KST 변환
- 오류 시 대체 문구 처리

## 수정한 파일

- `frontend/station-detail.html`
- `frontend/station-detail.js`
- `.docs/Frontend_Station_Detail.md`

## 구현 이유

데이터의 최신성을 화면에서 확인할 수 있게 했습니다.

## 변경 사항

- 역 상세 초기 요청 2개 → 3개

## 새롭게 배운 개념

- ISO 8601 시간의 KST 표시

## 실무에서는

화면 전체 갱신 시각과 개별 데이터셋 갱신 시각을 구분해 제공합니다.

## 개선 가능한 부분

- 공통 날짜 포맷 함수 모듈화

## 다음 작업

- 실제 API 갱신 시각 연결

## 복습 문제

1. `updated_at`에 ISO 8601 형식을 사용하는 장점은 무엇일까요?
2. 잘못된 날짜를 검사해야 하는 이유는 무엇일까요?
3. 각 API가 자체 갱신 시각을 제공해야 하는 이유는 무엇일까요?

## 오늘 배운 내용

- 데이터 최신성 표시

## Change Log

2026-07-13 - 역 상세 page-title 업데이트 시간 추가

## Timestamp

2026-07-13 10:55:51 (KST)

---

# 개요

역 상세 페이지의 `station-risk-status`가 현재 위험도에 따라 위험도 산정 기준과 동일한 색상으로 표시되도록 개선했습니다.

# 구현 목적

기존 역 상세 위험도 카드는 실제 위험도와 관계없이 빨간색 계열로 표시되어 사용자가 상태를 오해할 수 있었습니다. 구간 상세의 `route-risk-card`와 동일한 색상 의미를 사용해 화면 간 일관성과 위험도 식별성을 높입니다.

# 구현 내용

- 높음(`high`): 빨간색
- 주의(`warning`): 주황색
- 관심(`interest`): 초록색
- 정보 없음(`none`): 회색
- 카드 배경, 테두리, 제목, 경고 아이콘에 상태 색상 적용
- 역 변경 시 기존 상태 클래스를 제거한 후 현재 위험도 클래스 적용
- 초기 로딩과 데이터 없음 상태에 `none` 클래스 적용

# 코드 설명

## 왜 필요한가

색상은 위험도를 빠르게 구분하기 위한 시각적 정보입니다. 라벨과 색상이 일치해야 사용자가 현재 상태를 정확하게 판단할 수 있습니다.

## 어떤 원리인가

기존 `getRiskLevelByDelayRate()`가 반환하는 `high`, `warning`, `interest`, `none` 값을 CSS modifier 클래스 이름에 연결합니다. CSS Custom Property로 강조색, 배경색, 테두리색을 상태별로 교체합니다.

## 실행 흐름

1. 역의 지연률로 위험도 수준을 계산합니다.
2. `setStationRiskStatusLevel()`이 기존 modifier 클래스를 모두 제거합니다.
3. 계산된 위험도에 맞는 modifier 클래스를 추가합니다.
4. CSS 변수가 카드와 아이콘의 색상을 갱신합니다.
5. 데이터를 불러오지 못하면 `none` 상태로 복원합니다.

## 장점

- 구간 상세와 같은 위험도 색상 체계를 사용합니다.
- 상태 전환 시 이전 역의 색상이 남지 않습니다.
- CSS 변수 기반이라 색상 정책을 수정하기 쉽습니다.

## 단점

- 구간 카드와 역 카드에 동일한 색상 값이 각각 선언되어 있습니다.
- SVG 아이콘 색상은 CSS `filter` 값에 의존합니다.

## 다른 구현 방법

공통 `risk-status` 컴포넌트와 전역 위험도 색상 토큰을 만들 수 있습니다. 다만 이번 작업에서는 기존 프로젝트 구조를 유지하고 하나의 기능만 변경하기 위해 역 상세 전용 modifier를 추가했습니다.

## 실무에서는

디자인 토큰에 위험도별 강조색, 배경색, 테두리색을 정의하고 여러 컴포넌트가 같은 토큰을 참조하도록 구성합니다. 아이콘은 `currentColor`를 지원하는 인라인 SVG 또는 SVG 컴포넌트를 사용하면 `filter`보다 유지보수가 쉽습니다.

# API

변경 없음. 기존 Mock 데이터의 `delay_rate`를 그대로 사용합니다.

# Database

변경 없음. 스키마와 ERD 변경이 필요하지 않습니다.

# 주의사항

- 위험도 기준은 지연률 40% 이상 높음, 25% 이상 주의, 그 미만 관심입니다.
- 지연률이 유효한 숫자가 아니면 정보 없음으로 표시합니다.
- 색상만으로 상태를 전달하지 않도록 기존 위험도 텍스트와 `aria-label`을 유지합니다.

# 변경 이력

2026-07-13 - 역 상세 위험도 카드의 상태별 색상 적용

# 다음 작업

- 공통 위험도 색상 토큰 분리 검토
- 실제 브라우저 기반 시각 회귀 테스트 추가

# 작업 요약

## 완료한 내용

- 역 상세 위험도 카드의 네 가지 상태 색상 구현
- 역 변경 및 데이터 없음 상태의 클래스 초기화 구현
- JavaScript 문법과 상태 클래스 연결 검증

## 수정한 파일

- `frontend/station-detail.html`
- `frontend/station-detail.js`
- `frontend/style.css`
- `.docs/Frontend_Station_Detail.md`

## 구현 이유

실제 위험도와 카드 색상을 일치시키고 구간 상세와 일관된 사용자 경험을 제공하기 위해 수정했습니다.

## 변경 사항

- `station-risk-status--{level}` modifier 클래스 추가
- 위험도 클래스 전환 함수 추가
- 초기 및 오류 상태를 회색으로 변경

## 새롭게 배운 개념

- CSS Custom Property를 이용한 상태별 테마
- modifier 클래스 기반 UI 상태 관리

## 실무에서는

위험도 정책을 공통 디자인 토큰과 도메인 상수로 관리하고 시각 회귀 테스트로 색상 변경을 검증합니다.

## 개선 가능한 부분

- 구간·역 상세의 위험도 색상 토큰 공통화
- SVG 아이콘을 `currentColor` 방식으로 전환
- 브라우저 자동화 테스트 추가

## 다음 작업

- 구간·역 상세 공통 위험도 UI 정책 정리

## 프로젝트 진행률

■■■■■■■■■■ 100%

완료

- 문제 분석 및 설계
- 위험도별 색상 구현
- 빈 데이터 복원 처리
- 정적 테스트
- 문서화

진행 중

- 없음

예정

- 공통 위험도 디자인 토큰 검토

## 복습 문제

1. 상태 클래스를 추가하기 전에 기존 modifier 클래스를 모두 제거해야 하는 이유는 무엇일까요?
2. CSS Custom Property를 사용하면 상태별 스타일 관리에 어떤 장점이 있을까요?
3. 색상과 함께 위험도 텍스트를 유지해야 하는 접근성상의 이유는 무엇일까요?

## 오늘 배운 내용

- CSS Custom Property 기반 상태 테마
- UI modifier 클래스
- 빈 데이터 UI 상태 복원

## README 반영 여부

실행 방법이나 프로젝트 기능 범주가 바뀌지 않은 역 상세 내부 표현 개선이므로 README는 수정하지 않았습니다.

## 추천 Commit Message

`fix: 역 상세 위험도 카드 색상 기준 통일`

## Change Log

2026-07-13

- 역 상세 위험도 카드에 높음·주의·관심·정보 없음 색상 적용
- 초기 로딩과 데이터 없음 상태를 회색으로 통일

## Timestamp

2026-07-13 16:02:26 (KST)
