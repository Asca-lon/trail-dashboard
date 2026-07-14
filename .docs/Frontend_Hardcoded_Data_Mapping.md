# 개요

프론트엔드 HTML에 디자인 확인 목적으로 직접 작성된 데이터와, 해당 영역에 실제로 연결되어야 하는 데이터 소스를 페이지별로 정리합니다.

현재 브라우저는 HTML을 먼저 표시하고 JavaScript의 비동기 데이터 요청 결과를 나중에 반영합니다. 이 때문에 새로고침 직후 하드코딩된 디자인 데이터가 잠시 노출된 뒤 연결 데이터로 바뀌는 현상이 발생합니다.

이 문서는 하드코딩 제거 작업의 범위와 데이터 연결 기준, 실제 적용 결과를 함께 관리합니다.

# 구현 목적

- 새로고침 직후 임의의 디자인 데이터가 노출되는 현상을 제거합니다.
- HTML은 화면 구조와 고정 문구만 담당하도록 정리합니다.
- 숫자, 역명, 구간명, 특보, 기준 시각, 표와 차트 데이터는 연결된 데이터만 표시합니다.
- 데이터 수신 전에는 로딩 상태, 데이터가 없으면 빈 상태, 요청 실패 시 오류 상태를 표시합니다.
- Mock 모드와 DB 모드가 동일한 응답 계약을 사용하도록 데이터 연결 지점을 문서화합니다.

# 구현 내용

## 공통 렌더링 원칙

| 구분 | HTML에 유지 | 데이터 연결 후 표시 |
|---|---|---|
| 화면 구조 | 제목, 카드, 표 머리글, 단위 설명, 탭, 버튼 | 해당 없음 |
| 실제 데이터 | 유지하지 않음 | 숫자, 지역, 역, 구간, 특보, 기준 시각, 목록, 차트 |
| 요청 중 | `불러오는 중` 또는 스켈레톤 | 응답 완료 후 교체 |
| 빈 응답 | 임의 값 사용 금지 | `데이터 없음` |
| 요청 실패 | 이전 디자인 값 사용 금지 | 오류 안내와 재시도 가능한 상태 |

고정된 위험도 산정 기준과 필터 선택지처럼 서비스 정책 또는 UI 조작에 필요한 문구는 디자인용 데이터가 아니므로 별도 정책 API가 생기기 전까지 유지할 수 있습니다.

## 구현 결과

- 세 페이지의 HTML에 직접 작성돼 있던 역명, 구간명, 특보, 기준 시각, 지표 숫자를 로딩 상태로 변경했습니다.
- JavaScript 렌더링 대상 표의 예시 행을 제거하고 빈 `tbody`만 유지했습니다.
- 선 차트의 예시 좌표와 강조점, 툴팁 값을 제거했습니다.
- 막대 차트와 비교 차트의 예시 막대를 제거하고 축과 범례만 유지했습니다.
- 구간 상세 페이지의 정적 특보 카드와 유사 사례 카드는 연결 데이터 대기 상태로 변경했습니다.
- DOM의 `data-*` 선택자는 그대로 유지하여 기존 JavaScript가 데이터 응답 후 값을 채울 수 있도록 했습니다.
- 아래 페이지별 매핑 표는 변경 전 위치와 데이터 연결 기준을 추적하기 위해 그대로 보존합니다.
- 구간 상세 페이지가 `alerts_active.json`을 추가로 요청하도록 연결했습니다.
- 선택 구간의 `from`, `to`와 `active[].affected`의 구간 또는 역 정보를 비교해 관련 특보만 표시합니다.
- 관련 특보가 없으면 `현재 발효 중인 특보가 없습니다.`를 표시합니다.

## 메인 대시보드

대상 파일: `frontend/dashboard.html`, `frontend/dashboard.js`

| 하드코딩된 영역 | HTML에 작성된 예시 | 연결될 현재 데이터 | 주요 필드 또는 계산값 |
|---|---|---|---|
| 기상특보 배너 | `호우 경보`, `대전광역시` | `mock/alerts_active.json` | `alerts[].alert_type`, `alert_level`, `areas`, `issued_at` |
| 최근 업데이트 시각 | 정적인 업데이트 문구 | 각 응답의 갱신 시각 | `updated_at` 중 유효한 최신 시각 |
| 요약 카드 | 영향 구간 수, 지연 예상 열차, 평균 지연, 고위험 구간 수 예시 | `vulnerability_segments.json`, `vulnerability_stations.json`, `checklist.json`, `heatmap.json` | 배열 집계, `avg_delay_incr`, `sample_n`, 위험도 판정 결과 |
| 노선 위험도 지도 | `대전`, `김천(구미)`와 위험 상태 | `mock/heatmap.json` | `nodes[].station`, `risk_level` 및 응답 내 노선 정보 |
| 위험도별 요약 | 높음·주의·관심·정보 없음 개수 | `mock/heatmap.json` | `nodes[].risk_level`별 집계 |
| 구간 취약도 순위 | 반복된 `대전-김천(구미)` 예시 행 | `mock/vulnerability_segments.json` | `segments[].from`, `to`, `avg_delay_incr`, `stop_rate`, `sample_n` |
| 역 취약도 순위 | `대전`, `김천(구미)` 예시 행 | `mock/vulnerability_stations.json` | `stations[].station`, `avg_delay`, `delay_rate`, `stop_rate`, `sample_n` |
| 우선 점검 대상 | `호우경보`, `평균 지연 +18.4분` 반복 행 | `mock/checklist.json` | `items[].rank`, `target`, `reason`, `avg_delay_incr`, `sample_n` |
| 점검 대상 상세 패널 | 선택 전 디자인 설명 또는 예시 | `mock/checklist.json`과 역 목록 | 선택한 `items[]` 항목 및 `station_id` lookup |
| 필터 옵션 | 노선·특보·등급·열차 종류의 정적 예시 | `lines.json`과 취약도/특보 응답 | 응답에서 추출한 고유 필터 값 |

JavaScript 렌더링 진입점은 `renderAlertBanner`, `renderSummaryCards`, `renderHeatmap`, `renderRankings`, `renderInspectionTable`입니다.

## 역 상세 페이지

대상 파일: `frontend/station-detail.html`, `frontend/station-detail.js`

| 하드코딩된 영역 | HTML에 작성된 예시 | 연결될 현재 데이터 | 주요 필드 또는 계산값 |
|---|---|---|---|
| 역 기본 정보 | `대전역`, 노선 배지 | URL query와 `vulnerability_stations.json` | `station_id`, `station`, `line` |
| 현재 위험도 | `현재 위험도: 높음`, `호우 경보`와 기준 시각 | `vulnerability_stations.json` 및 `station_details.json` | `delay_rate`, `stop_rate`, `alert_type`, `alert_level`, 기준 시각 |
| 주요 지표 카드 | 평균 지연, 증가량, 지연률, 중단률 예시 | `mock/vulnerability_stations.json` | `avg_delay`, `delta_delay`, `delay_rate`, `stop_rate` |
| 시간대별 지연 차트 | 14시 `18.4분` 등 SVG 예시 | `mock/station_details.json` | `hourly[].hour`, 평일·휴일 지연 값 |
| 특보/평상시 비교 차트 | 호우·대설·강풍 막대 예시 | `mock/station_details.json` | 비교 배열의 특보 유형, 평상시 평균, 특보 시 평균 |
| 특보별 영향 통계 | 호우·강풍·대설·폭염 및 비율 예시 행 | `mock/station_details.json` | `by_alert[].alert_type`, `alert_level`, `avg_delay`, `sample_n` |
| 역 변경 선택지 | HTML 또는 코드의 역 예시 | `vulnerability_stations.json` 및 노선 메타데이터 | `stations[].station_id`, `station` |

JavaScript 렌더링 진입점은 `renderStationInfo`, `renderStationMetrics`, `renderStationCharts`, `renderAlertStatsTable`입니다.

## 구간 상세 페이지

대상 파일: `frontend/route-detail.html`, `frontend/route-detail.js`

| 하드코딩된 영역 | HTML에 작성된 예시 | 연결될 현재 데이터 | 주요 필드 또는 계산값 |
|---|---|---|---|
| 출발·도착역과 구간 정보 | `대전역 - 김천(구미)역` | URL query, `segments_details.json`, `vulnerability_segments.json` | `segment_id`, `from`, `to`, `line` |
| 현재 위험도와 특보 | `호우 경보`, 지역과 기준 시각 | 두 구간 데이터 응답 | `alert_type`, `alert_level`, `avg_delay_incr`, `stop_rate`, 기준 시각 |
| 주요 지표 카드 | 평균 지연, 증가량, 중단률, 영향 열차 예시 | `vulnerability_segments.json`과 상세 응답 | `avg_delay_incr`, `stop_rate`, `sample_n` 및 상세 통계 |
| 시간대별 지연 차트 | 실제·예측 지연 SVG 예시 | `mock/segments_details.json` | 시간대별 실제 지연과 예측 지연 배열 |
| 최근 7일 추이 | 정적 막대와 수치 | `mock/segments_details.json` | 일자별 `delay_increase` 추이 |
| 특보 영향 요약 표 | 호우·대설·강풍 예시 행 | `mock/segments_details.json` | `by_alert[]`의 유형, 등급, 평균 지연, 증가량, 중단률, 표본 수 |
| 특보별 가로 차트 | `18.4`, `8.2%` 등의 예시 | `mock/segments_details.json` | `by_alert[].avg_delay`, `stop_rate` |
| 과거 사례 표 | 날짜, 강수량, 지연, 영향 열차 예시 | `mock/segments_details.json` | 과거 사례 배열의 시각, 기상, 지연, 중단률, 영향 열차 |
| 과거 사례 비교 차트 | `19.6`, `17.2`, `12.1` 등 예시 | `mock/segments_details.json` | 과거 사례 상위 항목과 현재 구간 값 |
| 유사 사례 카드 | 날짜, 유사도, 지표 예시 | `mock/segments_details.json` | 유사 사례 데이터 또는 과거 사례 계산 결과 |
| 구간 변경 선택지 | `대전역 - 김천(구미)역` | `vulnerability_segments.json` 및 노선 메타데이터 | `segments[].segment_id`, `from`, `to` |

JavaScript 렌더링 진입점은 `renderRouteSummary`, `renderRouteMetrics`, `renderRouteCharts`, `renderRouteAlertTables`, `renderRouteHistoryTable`, `renderRouteHistoryCharts`입니다.

# 코드 설명

## 실행 흐름

1. HTML은 데이터가 없는 구조 또는 로딩 상태로 렌더링됩니다.
2. 각 페이지의 초기화 함수가 필요한 JSON을 `Promise.all`로 요청합니다.
3. 응답 성공 시 페이지별 렌더링 함수가 DOM을 생성하거나 값을 갱신합니다.
4. 빈 응답이면 각 페이지의 `renderEmpty*` 함수가 빈 상태를 표시합니다.
5. 요청 실패 시 콘솔 기록과 사용자용 오류 상태를 표시하며 디자인 예시 값으로 되돌아가지 않습니다.

## 장점

- 사용자가 임의 데이터를 실제 데이터로 오해하지 않습니다.
- HTML과 데이터 소스의 역할이 분리됩니다.
- API 응답 변경 시 수정 지점을 렌더링 코드로 한정할 수 있습니다.
- Mock 모드와 DB 모드 전환 시 화면 초기 상태가 일관됩니다.

## 단점

- 네트워크가 느릴 때 빈 화면 또는 로딩 UI가 보일 수 있습니다.
- JavaScript가 비활성화되면 실제 데이터가 표시되지 않습니다.
- 로딩·빈 상태·오류 상태를 각각 설계하고 테스트해야 합니다.

## 다른 구현 방법

- 서버 사이드 렌더링으로 첫 HTML부터 실제 데이터를 포함할 수 있습니다.
- 모든 동적 영역에 스켈레톤 UI를 적용할 수 있습니다.
- HTML 템플릿 요소를 두고 JavaScript가 복제하여 행과 카드를 생성할 수 있습니다.

## 실무에서는

실무에서는 하드코딩된 실제처럼 보이는 값 대신 스켈레톤이나 명시적인 로딩 상태를 사용합니다. 또한 API 응답 스키마를 기준으로 UI 컴포넌트의 로딩, 성공, 빈 데이터, 실패 상태를 각각 정의하고 자동화 테스트로 새로고침 시 데이터 깜빡임을 검증합니다.

# API

현재 프론트엔드는 아래 Mock JSON 경로를 직접 사용합니다. FastAPI를 통한 대응 엔드포인트도 함께 표시합니다.

| 데이터 | 현재 프론트엔드 소스 | 대응 API |
|---|---|---|
| 활성 특보 | `mock/alerts_active.json` | `GET /alerts/active` |
| 노선 목록 | `mock/lines.json` | `GET /lines` |
| 구간 취약도 | `mock/vulnerability_segments.json` | `GET /vulnerability/segments` |
| 역 취약도 | `mock/vulnerability_stations.json` | `GET /vulnerability/stations` |
| 히트맵 | `mock/heatmap.json` | `GET /heatmap` |
| 점검 목록 | `mock/checklist.json` | `GET /checklist` |
| 역 상세 | `mock/station_details.json` | `GET /station/{code}` |
| 구간 상세 | `mock/segments_details.json` | `GET /segment/{from}/{to}` |

# Database

이번 문서 작업에는 Database 스키마 변경이 없습니다.

DB 모드에서는 API가 집계 테이블과 역 메타데이터를 조회해 Mock과 같은 응답 계약으로 반환해야 합니다. 따라서 프론트엔드는 DB 구조가 아니라 API 필드만 기준으로 렌더링해야 합니다.

# 주의사항

- `높음`, `주의`, `관심`의 임계값은 디자인 데이터가 아니라 현재 프론트엔드 정책 상수입니다. 정책 API 도입 여부를 별도로 결정해야 합니다.
- 역·구간 목록 일부가 JavaScript 상수에도 존재하므로 HTML 제거 작업 시 함께 실제 데이터인지 fallback 메타데이터인지 구분해야 합니다.
- 표의 머리글, 지표 단위, 접근성 설명은 데이터가 아니므로 삭제 대상에서 제외합니다.
- 빈 데이터에 `0`을 임의로 표시하면 실제 측정값 0과 구분할 수 없으므로 `-` 또는 `데이터 없음`을 사용합니다.
- 새로고침 깜빡임 제거 작업은 세 페이지의 초기 HTML과 오류 처리까지 함께 검증해야 합니다.

# 변경 이력

## Change Log

### 2026-07-10

- 메인 대시보드의 하드코딩 영역과 연결 데이터 매핑 작성
- 역 상세 페이지의 하드코딩 영역과 연결 데이터 매핑 작성
- 구간 상세 페이지의 하드코딩 영역과 연결 데이터 매핑 작성
- 현재 Mock 소스와 대응 API 엔드포인트 정리
- 메인 대시보드의 초기 디자인 데이터와 예시 목록 제거
- 역 상세 페이지의 초기 지표, 차트 좌표, 통계 행 제거
- 구간 상세 페이지의 초기 지표, 차트, 통계, 과거 사례 제거
- 데이터 수신 전 표시를 `불러오는 중` 상태로 변경
- 구간 상세 페이지에 활성 특보 데이터 요청 추가
- 선택 구간의 출발역·도착역 기준 활성 특보 필터링 추가
- 활성 특보 시작 시각 표시와 빈 상태 처리 추가

# 다음 작업

- 실제 브라우저에서 네트워크 속도를 낮춘 후 새로고침 깜빡임 확인
- 활성 특보 데이터에 종료 예상 시각이 추가되면 보조 카드에 연결
- 기존 백엔드 구간 상세 Mock 계약 테스트 실패 수정

# 작업 요약

## 완료한 내용

- 세 페이지에 하드코딩된 동적 데이터 영역을 분류했습니다.
- 각 영역에 연결될 Mock JSON, API, 주요 필드를 매핑했습니다.
- 세 페이지의 HTML에서 디자인용 초기 데이터를 제거했습니다.
- 데이터 요청 전에는 임의 값 대신 로딩 상태가 표시되도록 변경했습니다.
- 정적 검사, HTML 파싱, JavaScript 구문 검사를 완료했습니다.
- 구간 상세의 세 보조 특보 카드에 선택 구간 관련 활성 특보를 연결했습니다.

## 수정한 파일

- `frontend/dashboard.html`
- `frontend/station-detail.html`
- `frontend/route-detail.html`
- `.docs/Frontend_Hardcoded_Data_Mapping.md`
- `README.md`

## 구현 이유

비동기 응답 전에 임의 데이터가 노출되는 현상을 제거하고, 화면 영역과 데이터 소스의 대응 관계를 계속 추적하기 위해 변경했습니다.

## 변경 사항

- 카드 값은 `-`, 설명은 `불러오는 중`으로 초기화했습니다.
- 데이터 기반 목록과 표의 정적 자식 요소를 제거했습니다.
- 차트 축과 범례는 유지하고 데이터 좌표와 막대만 제거했습니다.
- 데이터베이스와 API 코드는 변경하지 않았습니다.

## 새롭게 배운 개념

- Flash of Static Content: 비동기 데이터 반영 전에 HTML의 정적 내용이 잠시 노출되는 현상
- Loading State: 데이터 요청이 진행 중임을 나타내는 UI 상태
- Empty State: 정상 응답이지만 표시할 데이터가 없는 상태
- API Contract: 프론트엔드와 백엔드가 합의한 응답 구조

## 실무에서는

구현 전에 데이터 매핑 표를 작성하고 각 UI 영역을 로딩, 성공, 빈 데이터, 실패의 네 가지 상태로 나누면 개발과 테스트의 누락을 줄일 수 있습니다.

## 개선 가능한 부분

- 프론트엔드의 Mock 직접 호출을 API 호출로 통일
- 정책 상수를 API 또는 공통 설정으로 관리
- 새로고침 초기 상태를 검증하는 브라우저 자동화 테스트 추가
- 역명 문자열이 아닌 지역코드 기반 특보 매칭으로 확장
- `segments_details.json`의 API 응답 계약과 테스트 등록 불일치 수정

## 다음 작업

브라우저 개발자 도구에서 네트워크 속도를 낮춘 뒤 세 페이지를 새로고침하여 로딩 상태와 실제 데이터 전환을 육안 검증합니다.

## 테스트 결과

- 디자인 예시 문자열 정적 검색: 통과, 검색 결과 없음
- `dashboard.js`, `station-detail.js`, `route-detail.js`의 `node --check`: 통과
- Python `html.parser`를 사용한 세 HTML 파일 파싱: 통과
- 대전→김천(구미) 구간 활성 특보 매칭: 통과, 호우 경보 1건
- 밀양→부산 구간 활성 특보 빈 상태: 통과, 0건
- `python -m pytest backend/tests -q`: `15 passed, 1 skipped, 2 failed`

백엔드 실패는 이번 HTML 변경과 무관한 기존 문제입니다.

1. `segments_details.json`이 `MOCK_MODEL_MAP`에 등록되지 않았습니다.
2. `GET /segment/{from}/{to}`가 복수 구간을 담은 최상위 객체를 `SegmentDetail`로 검증하여 `by_alert`, `cases` 필드 누락 오류가 발생합니다.

실패 시 확인 사항:

- 프론트엔드는 파일 서버 또는 FastAPI 정적 경로를 통해 열어야 `fetch()`가 Mock JSON을 읽을 수 있습니다.
- 브라우저 콘솔에서 JSON 경로의 404와 JavaScript 오류를 확인합니다.
- 백엔드 전체 테스트를 통과시키려면 별도 작업으로 구간 상세 API 응답 선택 로직과 Mock 모델 등록을 수정해야 합니다.

## 복습 문제

1. HTML에 실제처럼 보이는 예시 데이터를 두면 비동기 요청 환경에서 어떤 문제가 발생할까요?
2. 데이터 값 `0`과 데이터 없음 상태를 구분해야 하는 이유는 무엇일까요?
3. Mock 모드와 DB 모드가 같은 API 응답 계약을 사용하면 어떤 장점이 있을까요?

## 오늘 배운 내용

- Flash of Static Content
- 로딩·빈 데이터·오류 상태 분리
- UI와 데이터 소스 매핑
- API 응답 계약

## 프로젝트 진행률

`■■■■■■■■■■ 100%`

완료:

- 문제 분석
- 영향 페이지 확인
- 하드코딩 데이터 매핑 문서 작성
- 세 페이지 초기 디자인 데이터 제거
- 정적 HTML 및 JavaScript 검증
- 테스트 결과 문서화
- 구간 상세 활성 특보 연결 및 구간 필터링

예정:

- 브라우저 수동 확인
- 별도 백엔드 Mock 계약 오류 수정

Timestamp

2026-07-10 17:33:27 (KST)
