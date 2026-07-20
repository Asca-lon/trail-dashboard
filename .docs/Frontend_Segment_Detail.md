# 구간 상세 페이지 프론트엔드

# 개요

`Frontend.md`에서 페이지 책임에 따라 분리한 프론트엔드 구현 기록입니다.

# 구현 목적

구간 상세 화면의 조회, 분석 탭, 과거 사례, 차트 및 Mock 데이터 연결 기록을 한 문서에서 관리합니다.

# 구현 내용

- 구간 선택과 식별자 구조
- 특보별 분석
- 과거 사례와 비교 차트
- 위험도 기준 안내

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
5. 상세 컬럼은 후속 상세 보기 연결 전까지 빈 셀로 유지합니다.

## 장점

- 과거 사례 탭이 mock 데이터와 연결됩니다.
- mock에 없는 값을 임의로 만들지 않습니다.
- 데이터 없음 상태를 안전하게 처리합니다.
- 날짜 포맷을 화면 표시용으로 변환합니다.

## 단점

- 현재 mock에는 상세 기상 수치가 없습니다.
- 상세 비교 버튼은 아직 연결하지 않았습니다.

## 다른 구현 방법

- `cases[]`에 강수량, 중단률, 영향 열차, 사례 선정 기준 필드 추가
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

따라서 실제 사례 선정 기준이나 상세 비교 기능을 구현하려면 mock 필드를 확장해야 합니다.

# 변경 이력

2026-07-09

- 구간 상세 과거 사례 테이블 mock 연결
- 날짜 포맷팅 추가
- mock 미제공 값 fallback 표시 추가

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
- Fallback UI

## 실무에서는

실무에서는 과거 사례 선정 기준을 백엔드 또는 분석 모델에서 계산해 내려주고, 프론트엔드는 전달받은 결과와 산정 근거를 명확히 표시하는 역할을 맡는 것이 좋습니다.

## 개선 가능한 부분

- case id 추가
- 과거 사례 상세보기 연결
- 필터 form 동작 연결

## 다음 작업

- 대시보드 취약 구간 랭킹에서 구간 상세 화면으로 `segment_id` 전달

## 복습 문제

1. mock에 없는 과거 사례 컬럼을 `-`로 표시한 이유는 무엇인가요?
2. 날짜 데이터를 화면용 문자열로 변환할 때 주의할 점은 무엇인가요?
3. 과거 사례 선정 기준을 프론트엔드에서 임의 계산하지 않는 것이 좋은 이유는 무엇인가요?

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

실무에서는 과거 사례 비교 데이터를 프론트엔드에서 고정하지 않고 분석 API에서 받아 표시합니다. 사례 선정 기준도 화면에 설명하고, 실제 운영 판단에 쓰이는 경우에는 기준 변경 이력을 함께 관리하는 것이 좋습니다.

## 개선 가능한 부분

- 필터 조회 동작 구현
- 페이지네이션 실제 데이터 연결
- 과거 사례 선정 기준 상세 안내 구현
- 상세 비교 보기 페이지 연결

## 다음 작업

- 구간 상세 탭 전체 브라우저 시각 검수
- 구간 상세 mock/API 데이터 연결 설계
- RAG 심층 분석 화면 설계

## 복습 문제

1. 과거 사례 필터에서 `label`과 `select`를 연결해야 하는 이유는 무엇인가요?
2. 과거 사례 선정 기준을 화면에 표시할 때 함께 제공해야 하는 설명은 무엇일까요?
3. 표가 좁은 화면에서 깨지지 않게 만드는 방법에는 어떤 것들이 있을까요?

## 오늘 배운 내용

- 과거 사례 목록 UI
- 필터 폼 접근성
- 과거 사례 비교 카드
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
- 과거 사례 선정 기준 API 설계
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


# 구간 상세 위험도 산정 기준 아코디언 구현 작업 요약

# 개요

구간 상세 페이지의 `위험도 산정 기준 보기` 버튼을 클릭하면 위험도 기준 목록이 펼쳐지도록 구현했습니다.

# 구현 목적

사용자가 현재 위험도 배지가 어떤 기준으로 산정되는지 화면 안에서 바로 확인할 수 있도록 하기 위함입니다.

# 구현 내용

- `frontend/route-detail.html`의 위험도 산정 기준 버튼 3곳에 펼침 패널을 추가했습니다.
- 각 버튼에 `aria-expanded`, `aria-controls`, `data-route-risk-criteria-toggle`을 추가했습니다.
- 각 패널에 `높음`, `주의`, `관심`, `데이터 없음` 기준을 표시했습니다.
- `frontend/route-detail.js`에서 모든 기준 버튼의 클릭 이벤트를 등록했습니다.
- 위험도 계산 기준을 화면 문구와 맞추기 위해 예상 지연 15분/5분, 운행 중단률 5%/2% 기준으로 정리했습니다.
- `frontend/style.css`에 펼침 패널, 등급 점, 펼침 아이콘 회전 스타일을 추가했습니다.

# 코드 설명

## 왜 필요한가

위험도 결과만 보여주면 사용자는 `높음`, `주의`, `관심`이 어떤 의미인지 알기 어렵습니다.
따라서 기준을 버튼 아래에 즉시 펼쳐 보여주면 화면 이해도가 높아집니다.

## 어떤 원리인가

버튼 클릭 시 JS가 `aria-expanded` 값을 `true` 또는 `false`로 바꾸고, 연결된 패널의 `hidden` 속성을 토글합니다.
CSS는 `aria-expanded="true"` 상태를 기준으로 버튼 모서리와 화살표 회전을 표현합니다.

## 실행 흐름

1. 페이지 로드 시 `[data-route-risk-criteria-toggle]` 버튼 목록을 찾습니다.
2. 각 버튼의 `aria-controls` 값으로 연결된 패널을 찾습니다.
3. 버튼 클릭 시 펼침 여부를 계산합니다.
4. 버튼의 `aria-expanded`와 패널의 `hidden` 상태를 갱신합니다.

# API

API 변경은 없습니다.

# Database

Database 변경은 없습니다.

# 주의사항

- 현재 기준은 프론트엔드 상수로 관리됩니다.
- 실무에서는 백엔드 분석 기준과 프론트엔드 표시 기준이 어긋나지 않도록 API 응답 또는 공용 설정으로 관리하는 것이 좋습니다.
- `주의` 기준의 `5~15분`, `2~5%`는 코드상 `15분 이상`, `5% 이상`이면 `높음`으로 우선 판정됩니다.

# 테스트

## 테스트 방법

```bash
node --check frontend/route-detail.js
```

```bash
node -e "const fs=require('fs'); const html=fs.readFileSync('frontend/route-detail.html','utf8'); const toggles=(html.match(/data-route-risk-criteria-toggle/g)||[]).length; const panels=(html.match(/data-route-risk-criteria-panel/g)||[]).length; const labels=['높음','주의','관심','데이터 없음']; console.log('toggles:',toggles); console.log('panels:',panels); console.log('labels:',labels.map((label)=>label+':' +(html.includes(label)?'ok':'missing')).join(', ')); if(toggles!==3||panels!==3||labels.some((label)=>!html.includes(label))) process.exit(1);"
```

## 예상 결과

- JS 문법 검사 오류가 없어야 합니다.
- 버튼 수는 `3`, 패널 수는 `3`이어야 합니다.
- `높음`, `주의`, `관심`, `데이터 없음` 라벨이 모두 `ok`로 표시되어야 합니다.

## 검증 결과

- `node --check frontend/route-detail.js`: 통과
- 정적 HTML 구조 검증: 통과

# 작업 요약

## 완료한 내용

- 구간 상세 페이지 위험도 산정 기준 펼침 기능 구현
- 위험도 기준 문구 추가
- 위험도 산정 기준 상수 정리
- 접근성 속성 연결
- 문서 업데이트

## 수정한 파일

- `frontend/route-detail.html`
- `frontend/route-detail.js`
- `frontend/style.css`
- `.docs/Frontend.md`

## 구현 이유

기준 안내를 별도 페이지나 문서로 숨기지 않고, 사용자가 위험도 정보를 보는 위치에서 바로 확인하도록 하기 위해 구현했습니다.

## 변경 사항

- 위험도 산정 기준 보기 버튼 클릭 시 패널이 펼쳐집니다.
- 펼친 상태에서는 화살표 아이콘이 회전합니다.
- 현재 위험도 계산이 예상 지연과 운행 중단률을 함께 고려합니다.

## 새롭게 배운 개념

- Accordion UI
- `aria-expanded`
- `aria-controls`
- `hidden` 속성 기반 상태 제어

## 실무에서는

실무에서는 위험도 기준을 프론트엔드에만 하드코딩하지 않고, 분석 정책 버전과 함께 API에서 내려주는 방식을 자주 사용합니다.
이렇게 하면 기준이 바뀌었을 때 화면, 백엔드, 문서가 서로 다르게 동작하는 문제를 줄일 수 있습니다.

## 개선 가능한 부분

- 위험도 기준을 공용 설정 JSON으로 분리
- 위험도 기준 변경 이력 표시
- 키보드 포커스 이동과 펼침 상태 테스트 자동화

## 다음 작업

- 역 상세 페이지의 위험도 산정 기준도 동일한 구조로 정리
- 위험도 기준을 백엔드 계약 문서와 맞춰 공통화

# 프로젝트 진행률

■■■■■■■■□□ 80%

완료

- 구간 상세 위험도 산정 기준 펼침 기능

진행 중

- 상세 화면 보조 UI 정리

예정

- 역 상세 위험도 기준 공통화
- 분석 기준 API화 검토

# 복습 문제

1. `aria-expanded`와 `hidden` 속성을 함께 사용하는 이유는 무엇일까요?
2. 위험도 산정 기준을 프론트엔드 상수로만 관리하면 어떤 문제가 생길 수 있을까요?
3. `15분 이상`과 `5~15분`처럼 경계값이 겹칠 때 우선순위를 정해야 하는 이유는 무엇일까요?

# 오늘 배운 내용

- Accordion UI
- 접근성 상태 속성
- 위험도 기준과 표시 기준 동기화

# README 반영 여부

이번 작업은 구간 상세 화면 내부의 보조 UI 동작 추가이므로 README 변경은 필요하지 않습니다.

# 추천 Commit Message

`feat: 구간 상세 위험도 산정 기준 아코디언 추가`

## Change Log

2026-07-10

- 구간 상세 페이지 위험도 산정 기준 펼침 패널 추가
- 예상 지연 및 운행 중단률 기준으로 위험도 산정 로직 정리
- 위험도 기준 버튼 접근성 속성 추가

## Timestamp

2026-07-10 11:07:33 (KST)

---


# 구간 상세 과거 사례 필터 기능 연결 작업 요약

## 완료한 내용

- 구간 상세 페이지의 `과거 사례` 탭에 있는 필터 `조회` 버튼을 실제 렌더링 로직과 연결했습니다.
- `특보 종류`, `특보 등급`, `기간` 조건에 따라 과거 사례 테이블을 다시 렌더링하도록 구현했습니다.
- 필터 결과를 기준으로 하단의 과거 사례 비교 미니 차트도 함께 갱신되도록 연결했습니다.

## 수정한 파일

- `frontend/route-detail.html`
- `frontend/route-detail.js`
- `.docs/Frontend.md`

## 구현 이유

기존 과거 사례 필터는 select와 조회 버튼만 있었고, 사용자가 조건을 바꿔도 테이블이나 차트가 변하지 않았습니다. 실제 mock 데이터의 `cases` 배열을 기준으로 필터링하고 기존 렌더 함수를 재사용해 화면이 갱신되도록 수정했습니다.

## 변경 사항

- 과거 사례 필터 폼에 `data-route-history-filter-form` 추가
- 특보 종류, 특보 등급, 기간 select에 JS 연결용 `data-*` 속성 추가
- 특보 종류 기본값을 `전체`로 변경
- `routeHistoryState`로 현재 선택 구간 상세 데이터를 보관
- submit 시 필터링된 `cases`로 테이블과 비교 차트 재렌더링

## 코드 설명

필터는 현재 선택된 구간의 상세 데이터에서 `cases`만 새 배열로 걸러냅니다. 그다음 기존 `renderRouteHistoryTable()`과 `renderRouteHistoryCharts()`를 다시 호출합니다.

과거 사례 mock에는 `alert_level` 필드가 없으므로 특보 등급은 `delay_min` 기준으로 추정합니다.

- `18분 이상`: 경보
- `10분 이상`: 주의보
- `10분 미만`: 관심

## API

API 변경 사항은 없습니다.

사용한 mock 데이터:

- `mock/segments_details.json`

## Database

DB 변경 사항은 없습니다.

## 주의사항

- 과거 사례 데이터에는 실제 특보 등급 필드가 없어 등급 필터는 지연 시간 기준 추정값입니다.
- 기간 필터는 현재 선택 구간의 과거 사례 중 가장 최신 날짜를 기준으로 계산합니다.
- 필터는 현재 화면의 과거 사례 탭 안에서만 동작합니다.

## 테스트 방법

```bash
node --check frontend/route-detail.js
```

예상 결과:

- JavaScript 문법 오류 없이 종료됩니다.

브라우저 확인:

- 구간 상세 페이지에서 `과거 사례` 탭으로 이동합니다.
- 특보 종류를 바꾸고 `조회`를 누르면 과거 사례 테이블이 갱신됩니다.
- 특보 등급을 바꾸고 `조회`를 누르면 지연 시간 기준에 맞는 사례만 표시됩니다.
- 기간을 바꾸고 `조회`를 누르면 기간 조건에 맞는 사례만 표시됩니다.

## 구현 목적

디자인만 존재하던 구간 상세 과거 사례 필터를 실제 mock 데이터 기반 필터 기능으로 전환하는 것이 목적입니다.

## 구현 내용

- 필터 폼 submit 이벤트 연결
- 현재 구간 상세 데이터 상태 저장
- 과거 사례 필터 조건 추출
- 과거 사례 배열 필터링
- 테이블 및 비교 차트 재렌더링

## 변경 이력

2026-07-10

- 구간 상세 과거 사례 필터 적용 기능 추가

## 작업 요약

## 완료한 내용

- 과거 사례 필터 `조회` 기능 연결
- 과거 사례 테이블 필터링
- 비교 미니 차트 필터링 결과 반영
- JS 문법 검사 완료

## 수정한 파일

- `frontend/route-detail.html`
- `frontend/route-detail.js`
- `.docs/Frontend.md`

## 구현 이유

기능 없는 필터 UI를 실제 데이터 제어 기능으로 연결해 사용자가 선택한 조건에 따른 결과를 확인할 수 있도록 했습니다.

## 변경 사항

- 필터 폼 기본 submit 차단
- 필터링된 구간 상세 데이터 객체 생성
- 기존 과거 사례 렌더 함수 재사용

## 새롭게 배운 개념

- Form Submit Handling
- State-based Filtering
- Derived Filter Criteria

## 실무에서는

실무에서는 과거 사례의 `alert_level`을 프론트엔드에서 추정하지 않고 API 응답에 명시적으로 포함하는 편이 좋습니다. 그래야 화면, API, 분석 기준이 서로 다르게 해석되는 문제를 줄일 수 있습니다.

## 개선 가능한 부분

- `cases[]`에 `alert_level` 필드 추가
- 필터 조건을 URL query parameter와 동기화
- 결과 없음 상태 문구를 필터 조건에 맞게 더 구체화

## 다음 작업

- 구간 상세 과거 사례 페이지네이션 기능 여부 결정
- 유사 과거 사례 상세 비교 링크 정리

## 프로젝트 진행률

■■■■■■■■□□ 80%

완료

- 구간 상세 과거 사례 필터 적용 기능

진행 중

- 디자인만 있는 버튼/링크 기능 연결

예정

- 과거 사례 페이지네이션 연결 또는 제거
- 상세 비교 보기 링크 연결 또는 제거

## 복습 문제

1. mock 데이터에 `alert_level`이 없을 때 프론트엔드에서 등급을 추정하면 어떤 위험이 있을까요?
2. 필터링된 데이터 객체를 새로 만들어 렌더 함수에 넘기는 방식의 장점은 무엇일까요?
3. 필터 조건을 URL에 저장하면 사용자 경험 측면에서 어떤 장점이 있을까요?

## 오늘 배운 내용

- Form Submit Handling
- Derived Criteria
- History Case Filtering

## README 반영 여부

이번 작업은 구간 상세 내부 동작 개선이므로 README에는 별도 항목을 추가하지 않았습니다.

## 추천 Commit Message

`feat: 구간 상세 과거 사례 필터 연결`

## Change Log

2026-07-10

- 구간 상세 과거 사례 필터 적용 기능 추가

## Timestamp

2026-07-10 11:45:12 (KST)

---


# 구간 상세 경부선 고속 전체 구간 필터 개선

# 개요

구간 상세 화면의 변경 모달에 경부선 고속 정차역 사이의 인접 구간 9개를 모두 표시하고 구간 거리 정보를 제거했습니다.

# 구현 목적

- 대시보드와 상세 화면이 동일한 고속 정차역 순서를 사용하도록 합니다.
- 데이터가 없는 구간도 탐색할 수 있고 데이터 부재를 명확히 확인하도록 합니다.
- 현재 사용하지 않는 구간 거리 정보를 화면에서 제거합니다.

# 구현 내용

- 서울-광명, 광명-천안아산, 천안아산-오송, 오송-대전, 대전-김천(구미), 김천(구미)-동대구, 동대구-경주, 경주-울산, 울산-부산 구간을 정의했습니다.
- 구간 변경 모달은 고정된 9개 인접 구간을 순서대로 렌더링합니다.
- 기존 mock과 같은 `segment_id`를 가진 구간에는 위험 지표를 결합합니다.
- 상세 데이터가 없는 구간은 다른 구간의 데이터를 대체 표시하지 않고 빈 상태를 사용합니다.
- 구간 정보 카드의 구간 거리 항목과 구분선을 제거했습니다.

# 코드 설명

`GYEONGBU_HIGH_SPEED_SEGMENTS`가 전체 인접 구간의 기준 데이터입니다. `getInitialSegment()`는 URL의 `segment_id`를 기준 데이터에서 먼저 찾고 mock 지표가 있으면 병합합니다. `getSelectedSegmentDetail()`은 명시적으로 선택한 구간의 상세 데이터가 없을 경우 빈 객체를 반환해 첫 번째 mock 상세가 잘못 노출되는 것을 방지합니다.

장점은 데이터 제공 여부와 무관하게 전체 노선을 탐색할 수 있다는 점입니다. 단점은 구간 목록이 프론트엔드 상수라는 점이며, 실무 대안은 노선 메타데이터 API에서 순서와 ID를 제공받는 것입니다.

# API

새 API는 추가하지 않았습니다. 기존 `segment_id` query parameter를 사용합니다.

# Database

변경 사항이 없습니다.

# 주의사항

- 상세 데이터가 없는 구간은 지표, 표, 차트가 정보 없음 상태로 표시됩니다.
- 구간 ID는 인접 역 ID를 하이픈으로 연결한 규칙을 사용합니다.
- `mock/` 폴더는 수정하지 않았습니다.

# 변경 이력

2026-07-10

- 경부선 고속 인접 구간 9개 적용
- 상세 데이터 없는 구간의 빈 상태 처리
- 구간 거리 제거

# 다음 작업

- 전체 화면 사이드바의 데이터 기준 안내 제거
- 전체 회귀 테스트

# 작업 요약

## 완료한 내용

- 전체 고속 구간 변경 필터
- 선택 구간 URL 이동
- 결측 상세 데이터 처리
- 구간 거리 UI 제거

## 수정한 파일

- `frontend/route-detail.html`
- `frontend/route-detail.js`
- `.docs/Frontend.md`

## 구현 이유

전체 고속 노선을 탐색하면서 실제 데이터가 없는 구간과 다른 구간의 데이터를 혼동하지 않도록 하기 위해 구현했습니다.

## 변경 사항

- 고속 인접 구간 기준 상수 추가
- 변경 옵션의 데이터 원천 교체
- 상세 데이터 fallback 정책 수정
- 구간 거리 마크업 제거

## 새롭게 배운 개념

- Adjacent Segment Modeling
- Reference Data Merge
- Safe Empty Fallback

## 실무에서는

노선 메타데이터 API에서 정차역 순서를 내려주고 인접한 역으로 구간을 구성하거나, 구간 엔터티를 별도로 관리해 안정적인 구간 ID를 제공합니다.

## 개선 가능한 부분

- 공통 노선 메타데이터 모듈 도입
- 구간별 상세 API 연결
- 선택 구간 브라우저 자동화 테스트 추가

## 다음 작업

- 공통 사이드바 요구사항 구현

## 프로젝트 진행률

■■■■■■■□□□ 70%

완료

- 대시보드 변경
- 역 상세 변경 및 모달 적용
- 구간 상세 변경

진행 중

- 공통 사이드바 변경 준비

예정

- 전체 회귀 테스트

## 복습 문제

1. 상세 데이터가 없을 때 첫 번째 상세 데이터를 fallback으로 사용하면 어떤 문제가 생길까요?
2. 정차역 순서를 바탕으로 인접 구간을 구성할 때 필요한 정보는 무엇일까요?
3. 기준 구간 데이터와 위험 지표 데이터를 병합하는 이유는 무엇일까요?

## 오늘 배운 내용

- Segment Reference Data
- Data Merge
- Empty Fallback

## README 반영 여부

기존 구간 상세 화면 내부 변경이므로 README에는 별도 항목을 추가하지 않았습니다.

## 추천 Commit Message

`feat: 구간 상세 고속 구간 필터 및 거리 정보 개선`

## Change Log

2026-07-10

- 구간 상세 전체 고속 구간 필터 적용 및 구간 거리 제거

## Timestamp

2026-07-10 15:14:11 (KST)

---


---

## Timestamp

2026-07-10 17:11:58 KST

---

# 개요

구간 상세 상단 정보와 주요 지표 카드를 역 상세 페이지의 정보 구조에 맞게 개편했습니다.

# 구현 목적

데이터 기준 시각과 위험도를 명확하게 표시하고 역·구간 상세 페이지의 사용자 경험을 통일합니다.

# 구현 내용

- 제목 영역에 `page-title__updated` 추가
- `alerts_active.json.updated_at`을 데이터 기준 시간과 위험 카드 기준 시간에 표시
- `route-risk-card`를 `route-info-card` 내부로 이동
- 높음·주의·관심·정보 없음의 카드 색상을 위험도 산정 기준 색상과 통일
- 특보 등급 기준 카드와 전용 CSS 삭제
- 구간 주요 지표 카드를 `station-metric-card` 구조와 스타일로 통일
- 1180px 이하에서 위험 카드를 정보 카드의 다음 행으로 배치

# 코드 설명

위험도 계산 결과를 modifier class로 변환해 카드의 배경·테두리·제목·배지·아이콘 색상을 함께 바꿉니다. 시간은 Mock 응답을 직접 포맷하며 하드코딩 문구를 제거했습니다. 공통 요약 카드 클래스를 재사용해 중복 CSS도 줄였습니다. 장점은 상태 인지가 빠르고 화면 간 일관성이 높다는 점입니다. 단점은 현재 시간 출처가 특보 Mock에 묶여 있다는 점입니다. 실무에서는 디자인 토큰과 공통 카드 컴포넌트로 관리합니다.

# API

요청 및 응답 계약 변경 없음

# Database

변경 없음

# 주의사항

- 시간 출처는 `alerts_active.json.updated_at`입니다.
- 위험도 임계값 계산 로직은 기존 값을 유지합니다.

# 변경 이력

2026-07-13 - 구간 상세 상단 정보 및 요약 카드 개편

# 다음 작업

실제 API의 구간 데이터 갱신 시각 연결

# 작업 요약

## 완료한 내용

- Mock 시간 연결
- 위험도별 카드 색상 적용
- 위험 카드 중첩 구조 변경
- 특보 등급 기준 삭제
- 역 상세 요약 카드 스타일 재사용

## 수정한 파일

- `frontend/route-detail.html`
- `frontend/route-detail.js`
- `frontend/style.css`
- `.docs/Frontend_Segment_Detail.md`

## 구현 이유

구간의 현재 상태와 데이터 기준 시점을 한 영역에서 빠르게 파악하도록 개선했습니다.

## 변경 사항

- 독립 위험 카드 → 정보 카드 내부 위험 상태
- 단일 빨간색 → 4단계 상태 색상
- 전용 구간 지표 CSS → 공통 역 지표 CSS

## 새롭게 배운 개념

- 상태 modifier class
- 공통 UI 클래스 재사용

## 실무에서는

위험 색상은 색만으로 전달하지 않고 텍스트 배지와 접근성 이름을 함께 제공합니다.

## 개선 가능한 부분

- 위험 색상 CSS 변수를 전역 디자인 토큰으로 승격
- DOM 기반 시각 회귀 테스트 추가

## 다음 작업

- 네 단계 위험 상태 시각 회귀 테스트

## 복습 문제

1. 위험도별 modifier class를 사용하는 장점은 무엇일까요?
2. 색상과 텍스트 배지를 함께 제공해야 하는 이유는 무엇일까요?
3. 공통 요약 카드 클래스를 재사용하면 어떤 유지보수 이점이 있을까요?

## 오늘 배운 내용

- 상태 기반 카드 테마
- UI 컴포넌트 일관성

## Change Log

2026-07-13 - 구간 상세 정보 카드와 위험 상태 UI 개편

## Timestamp

2026-07-13 10:55:51 (KST)

---

# 개요

구간 상세의 `route-alert-card__box`가 선택 구간의 위험도에 따라 다른 색상으로 표시되도록 개선했습니다.

# 구현 목적

현재 발효 특보 박스와 상단 위험 카드가 동일한 위험도 상태를 시각적으로 전달하도록 통일합니다.

# 구현 내용

- 높음, 주의, 관심, 정보 없음 modifier class 추가
- 선택 구간의 기존 `getRiskLevel()` 결과 재사용
- 세 탭의 현재 발효 특보 박스에 동일한 상태 적용
- 특보가 없는 경우 정보 없음 상태 적용
- 상태 변경 전에 기존 modifier를 제거해 클래스 중복 방지
- 배경, 테두리, 제목, 아이콘 색상 동시 변경

# 코드 설명

`renderActiveAlerts()`에서 일치하는 특보가 있으면 선택 구간의 평균 지연 증가량과 운행 중단률로 위험도를 계산합니다. 특보가 없으면 `none`을 사용합니다. CSS 사용자 정의 속성으로 각 상태의 강조색, 배경색, 테두리색, 아이콘 필터를 한 modifier에 모았습니다.

장점은 상단 위험 카드와 특보 카드의 상태가 일치한다는 점입니다. 단점은 여러 특보가 한 구간에 동시에 존재해도 구간 단위 색상 하나를 사용한다는 점입니다. 다른 구현으로 특보별 박스를 분리해 각각 색상을 계산할 수 있습니다. 실무에서는 위험도 토큰을 공통 디자인 시스템에서 관리합니다.

# API

변경 없음

# Database

변경 없음

# 주의사항

색상만으로 상태를 전달하지 않도록 기존 특보 제목과 위험도 텍스트를 유지합니다.

# 변경 이력

2026-07-13 - 현재 발효 특보 박스에 위험도별 색상 적용

# 다음 작업

위험 색상 토큰의 전역 CSS 변수화 검토

# 작업 요약

## 완료한 내용

- 네 단계 특보 박스 색상 구현
- 세 탭 동시 적용
- 빈 특보 정보 없음 처리

## 수정한 파일

- `frontend/route-detail.js`
- `frontend/style.css`
- `.docs/Frontend_Segment_Detail.md`

## 구현 이유

특보 박스에서도 선택 구간의 위험도를 즉시 식별할 수 있도록 했습니다.

## 변경 사항

- 고정 빨간색 박스 → 상태 기반 4색 박스

## 새롭게 배운 개념

- CSS 사용자 정의 속성을 이용한 상태 테마

## 실무에서는

색각 이상 사용자를 위해 색상과 함께 텍스트, 아이콘, 접근성 이름을 제공합니다.

## 개선 가능한 부분

- 위험 카드와 특보 박스의 색상 토큰 완전 공통화

## 다음 작업

- 네 단계 시각 회귀 테스트 추가

## 복습 문제

1. 새 상태를 적용하기 전에 기존 modifier를 제거해야 하는 이유는 무엇일까요?
2. 특보가 없을 때 `none` 색상을 사용하는 이유는 무엇일까요?
3. CSS 사용자 정의 속성으로 상태 색상을 관리하면 어떤 장점이 있을까요?

## 오늘 배운 내용

- 상태 기반 특보 카드 테마

## README 반영 여부

내부 UI 표현 변경이며 실행 방법 변화가 없어 README 수정은 필요하지 않습니다.

## 추천 Commit Message

`style: 구간 특보 카드 위험도별 색상 적용`

## Change Log

2026-07-13 - route-alert-card__box 위험도별 색상 추가

## Timestamp

2026-07-13 11:11:58 (KST)

---

# 개요

구간 상세 요약 카드를 평균 지연 시간, 평균 지연 증가량, 운행 지연률, 운행 중단률 순서로 변경했습니다.

# 구현 목적

역 상세 페이지와 같은 지연·중단 중심 지표 구성을 제공하면서 분석 표본 수 대신 운행 상태를 직접 보여줍니다.

# 구현 내용

- 분석 표본 수 카드 제거
- 운행 지연률 카드 추가
- 평균 지연 시간을 현재 특보의 `by_alert[].avg_delay`와 연결
- 평균 지연 증가량을 현재 특보의 `by_alert[].delay_increase`와 연결
- 운행 중단률을 `by_alert[].stop_rate`와 연결하고 없으면 기존 구간 `stop_rate` 사용
- 운행 지연률은 필드가 없으므로 `- %`, `데이터 미제공` 표시
- Mock, API, 백엔드 모델은 수정하지 않음

# 코드 설명

현재 특보 종류와 등급이 일치하는 `by_alert` 항목을 찾아 요약 카드 값을 구성합니다. 일치 항목이 없으면 첫 번째 특보 통계를 사용합니다. 운행 지연률은 계산에 필요한 지연 건수와 전체 운행 건수가 없어 임의 계산하지 않습니다.

장점은 기존 데이터의 의미를 정확히 유지한다는 점입니다. 단점은 운행 지연률 값이 아직 표시되지 않는다는 점입니다. 다른 구현 방법은 프런트엔드 하드코딩이나 추정이지만 데이터 신뢰성을 훼손하므로 사용하지 않았습니다. 실무에서는 API가 `delay_rate`를 명시적으로 제공해야 합니다.

# API

변경 없음

# Database

변경 없음

# 주의사항

운행 지연률은 구간 응답에 `delay_rate`가 추가되기 전까지 `-`로 표시됩니다.

# 변경 이력

2026-07-13 - 구간 상세 요약 카드 지표 구성 변경

# 다음 작업

데이터 계약이 허용될 때 구간 `delay_rate` 제공 검토

# 작업 요약

## 완료한 내용

- 요약 카드 순서와 명칭 변경
- 현재 특보 통계 연결
- 데이터 미제공 상태 처리

## 수정한 파일

- `frontend/route-detail.html`
- `frontend/route-detail.js`
- `frontend/style.css`
- `.docs/Frontend_Segment_Detail.md`

## 구현 이유

사용자가 구간의 지연과 중단 비율을 한눈에 비교할 수 있도록 구성했습니다.

## 변경 사항

- 분석 표본 수 → 운행 지연률
- 평균 예상 지연 시간 → 평균 지연 시간
- 지연 증가량 → 평균 지연 증가량

## 새롭게 배운 개념

- 데이터 미제공 상태의 명시적 표현
- 특보 조건 기반 상세 통계 선택

## 실무에서는

비율 데이터는 분자와 분모 또는 서버 집계값을 명확히 제공하고 프런트엔드에서 임의 추정하지 않습니다.

## 개선 가능한 부분

- 향후 `delay_rate` 필드 연결
- 공통 지표 데이터 매퍼 분리

## 다음 작업

- 실제 API 계약 확정 후 운행 지연률 연결

## 복습 문제

1. `sample_n`만으로 운행 지연률을 계산할 수 없는 이유는 무엇일까요?
2. 특보 종류와 등급을 모두 비교해야 하는 이유는 무엇일까요?
3. 데이터가 없을 때 0 대신 `-`를 표시해야 하는 이유는 무엇일까요?

## 오늘 배운 내용

- 지표 데이터 매핑
- 결측 데이터 표현

## README 반영 여부

실행 방법 변경이 아닌 화면 지표 변경이므로 README 수정은 필요하지 않습니다.

## 추천 Commit Message

`refactor: 구간 상세 요약 카드 지표 구성 변경`

## Change Log

2026-07-13 - 구간 요약 카드에 운행 지연률 추가 및 분석 표본 수 제거

## Timestamp

2026-07-13 11:36:01 (KST)

---

# 구간 상세 과거 사례 유사도 별점 제거 작업 요약

# 개요

구간 상세 `과거 사례` 탭에서 더 이상 사용하지 않는 유사도 별점 표시 코드를 제거했습니다.

# 구현 목적

HTML과 CSS에서 제거된 유사도 별점 UI가 JavaScript에 남아 있으면 화면 구조와 렌더링 로직이 서로 어긋날 수 있습니다. 사용하지 않는 함수를 삭제해 유지보수 비용을 줄이고, 과거 사례 테이블의 컬럼 수를 실제 화면 요구사항과 맞췄습니다.

# 구현 내용

- 과거 사례 테이블의 `유사도` 컬럼 헤더 삭제
- `getSimilarityStars()` 삭제
- `createSimilarityCell()` 삭제
- `createHistoryRow()`의 유사도 셀 생성 호출 삭제
- `.route-history-stars` 미사용 스타일 삭제
- `.route-history-table__chevron` 미사용 스타일 삭제
- 유사도 기준 안내 문구를 현재 화면에 맞게 정리

# 코드 설명

## 왜 필요한가

사용하지 않는 UI 로직이 남아 있으면 이후 기능을 수정할 때 실제 화면에 없는 요소를 기준으로 코드를 오해할 수 있습니다.

## 어떤 원리인가

과거 사례 row는 `createHistoryRow()`에서 테이블 헤더 순서에 맞춰 `td`를 생성합니다. 유사도 헤더를 제거했기 때문에 JavaScript에서도 동일한 위치의 유사도 셀 생성을 제거해 헤더와 데이터 셀 개수를 맞췄습니다.

## 실행 흐름

1. `segmentDetailData.cases[]`를 읽습니다.
2. 각 사례를 `createHistoryRow()`로 변환합니다.
3. 발생 일시, 특보, 강수량, 지연, 중단률, 영향 열차, 상세 셀만 렌더링합니다.
4. 유사도 별점 셀은 더 이상 생성하지 않습니다.

## 장점

- 화면에 없는 기능 코드가 제거됩니다.
- 테이블 헤더와 row 셀 구조가 일치합니다.
- CSS에 남은 미사용 클래스가 줄어듭니다.

## 단점

- 유사도 점수를 다시 표시하려면 별도 설계와 데이터 계약이 필요합니다.

## 다른 구현 방법

- 유사도 컬럼을 유지하고 백엔드의 `similarity_score` 필드를 연결할 수 있습니다.
- 별점 대신 숫자 점수, 등급 배지, 설명형 텍스트로 표시할 수 있습니다.

## 실무에서는

실무에서는 화면에서 제거된 기능을 코드에서도 함께 제거하고, 다시 필요한 경우 새 요구사항과 API 계약을 기준으로 재도입합니다. 특히 테이블은 헤더와 데이터 셀 개수가 어긋나면 접근성과 유지보수성이 함께 나빠질 수 있어 함께 검증합니다.

# API

변경 없음

# Database

변경 없음

# 주의사항

`유사 사례 목록`이라는 화면 개념은 유지했습니다. 삭제한 것은 유사도 점수를 별점으로 표시하던 컬럼과 관련 렌더링 코드입니다.

# 변경 이력

2026-07-13 - 과거 사례 유사도 별점 컬럼 및 미사용 JS/CSS 제거

# 다음 작업

- 과거 사례 상세 컬럼에 실제 상세 보기 동작 연결 검토
- 필요 시 과거 사례 선정 기준 안내 UI 재설계

# 작업 요약

## 완료한 내용

- `getSimilarityStars()` 삭제
- `createSimilarityCell()` 삭제
- 과거 사례 테이블의 유사도 컬럼 삭제
- 관련 미사용 CSS 삭제
- 문서의 오래된 유사도 별점 설명 정리

## 수정한 파일

- `frontend/route-detail.html`
- `frontend/route-detail.js`
- `frontend/style.css`
- `.docs/Frontend_Segment_Detail.md`

## 구현 이유

화면에서 사라진 기능이 JavaScript와 CSS에 남아 있으면 불필요한 유지보수 포인트가 생기기 때문입니다.

## 변경 사항

- 과거 사례 row가 8개 컬럼 구조로 렌더링됩니다.
- 유사도 별점 텍스트와 스타일이 더 이상 생성되지 않습니다.
- 유사도 기준 안내 문구가 제거되었습니다.

## 새롭게 배운 개념

- Dead Code 제거
- 테이블 헤더와 데이터 셀 정합성
- 접근성 문구 정리

## 실무에서는

기능을 제거할 때는 HTML, CSS, JavaScript, 문서를 함께 확인합니다. 화면에서 보이지 않는 `aria-label` 같은 접근성 텍스트도 사용자 경험의 일부이므로 함께 정리해야 합니다.

## 개선 가능한 부분

- 상세 컬럼에 버튼 또는 링크 연결
- 과거 사례 선정 기준을 별도 도움말로 설계
- 정적 분석 또는 테스트 스크립트 추가

## 다음 작업

- 과거 사례 상세 보기 기능 설계

## 복습 문제

1. HTML 테이블에서 헤더 개수와 row 셀 개수가 맞아야 하는 이유는 무엇인가요?
2. 화면에서 보이지 않는 `aria-label`도 함께 수정해야 하는 이유는 무엇인가요?
3. 삭제된 유사도 기능을 다시 도입하려면 먼저 어떤 데이터 계약이 필요할까요?

## 오늘 배운 내용

- Dead Code
- Accessibility Label
- Table Column Consistency

## README 반영 여부

실행 방법이나 프로젝트 사용법 변경이 아니므로 README 수정은 필요하지 않습니다.

## 추천 Commit Message

`refactor: 구간 상세 과거 사례 유사도 별점 제거`

## Change Log

2026-07-13

- 과거 사례 유사도 별점 컬럼 제거
- 미사용 유사도 JS 함수 제거
- 미사용 CSS 클래스 제거
- 구간 상세 문서 업데이트

## Timestamp

2026-07-13 13:08:01 (KST)

---

# 구간 상세 위험도 산정 기준 안내 변경

# 개요

구간 상세 페이지의 위험도 산정 기준 안내를 실제 구간 위험도 판정 기준과 일치하도록 변경했습니다.

# 구현 목적

사용자가 화면에 표시된 기준만으로 높음, 주의, 관심 및 데이터 없음 상태를 정확히 이해할 수 있도록 합니다.

# 구현 내용

- 요약, 특보 분석, 과거 사례 탭의 기준 안내 문구를 동일하게 변경했습니다.
- 사용자 요청 문구를 표현 변경 없이 그대로 적용했습니다.
- 백엔드 산정 로직은 이미 5분·2분 기준이므로 수정하지 않았습니다.

# 코드 설명

`frontend/route-detail.html`에 존재하는 세 개의 위험도 기준 패널은 탭마다 독립적으로 표시됩니다. 따라서 모든 패널의 문구를 함께 변경해 탭 전환 후에도 동일한 기준을 안내하도록 했습니다.

장점은 화면과 서버 판정의 기준이 일치한다는 점입니다. 단점은 같은 문구가 HTML 세 곳에 중복되어 향후 변경 시 모두 수정해야 한다는 점입니다. 다른 방법으로 JavaScript 템플릿이나 서버 응답으로 기준 목록을 한 번만 정의할 수 있습니다. 실무에서는 정책 API 또는 공통 UI 컴포넌트를 사용해 단일 기준을 여러 화면에 제공합니다.

# API

변경 없음

# Database

변경 없음

# 주의사항

- 주의 문구의 `2~5분`은 실제 로직에서 2분 이상 5분 미만을 의미합니다.
- 표본이 10건 미만이거나 평균 지연 증가량이 없으면 데이터 없음 상태입니다.

# 변경 이력

2026-07-20 - 구간 상세 위험도 산정 기준 안내 문구 변경

# 다음 작업

- 위험도 기준 패널을 공통 템플릿으로 관리하는 방안 검토

# 작업 요약

## 완료한 내용

- 위험도 기준 패널 3곳의 문구 변경
- 요청 문구 반복 횟수 검증
- 실제 구간 위험도 경계값 검증

## 수정한 파일

- `frontend/route-detail.html`
- `.docs/Frontend_Segment_Detail.md`

## 구현 이유

기존 안내가 실제 백엔드 판정 기준과 달라 사용자에게 잘못된 정보를 제공할 수 있었기 때문입니다.

## 변경 사항

- 높음: 기상 특보 시 평균 지연 5분 이상 증가
- 주의: 기상 특보 시 평균 지연 2~5분 증가
- 관심: 기상 특보 시 지연 증가 2분 미만
- 데이터 없음: 분석 가능한 데이터가 부족함

## 새롭게 배운 개념

- 경계값 기반 분류
- 화면 문구와 도메인 정책의 정합성

## 실무에서는

업무 기준 문구와 계산 로직은 하나의 정책 원천에서 관리하고, 경계값 테스트로 두 표현의 일치 여부를 지속적으로 확인합니다.

## 개선 가능한 부분

- 중복된 패널 마크업을 공통 컴포넌트로 전환
- 백엔드 정책 정보를 제공하는 API 검토
- 자동화된 UI 문구 테스트 추가

## 다음 작업

- 위험도 기준의 단일 관리 구조 설계

## 테스트 방법

- 네 가지 문구가 HTML에 각각 3회 존재하는지 확인했습니다.
- `classify_segment_risk()`에 5, 4.999, 2, 1.999 및 데이터 없음 값을 입력해 경계값을 검증했습니다.

## 예상 결과

- 세 탭에서 동일한 네 가지 기준이 표시됩니다.
- 5분은 높음, 2분은 주의, 2분 미만은 관심으로 판정됩니다.
- 값이 없거나 표본이 10건 미만이면 데이터 없음으로 판정됩니다.

## 실패 시 확인 사항

- 세 개의 `route-risk-criteria-panel` 중 누락된 패널이 없는지 확인합니다.
- `backend/risk_rules.py`의 `classify_segment_risk()` 경계값을 확인합니다.

## 복습 문제

1. 화면 안내와 실제 산정 로직의 경계값이 같아야 하는 이유는 무엇인가요?
2. `2~5분`의 상한값 5분이 주의가 아닌 높음으로 분류되는 이유는 무엇인가요?
3. 동일한 기준 문구를 여러 곳에 복사하면 어떤 유지보수 문제가 생길 수 있나요?

## 오늘 배운 내용

- Boundary Value Testing
- Single Source of Truth
- Domain Policy

## README 반영 여부

실행 방법이나 설치 절차 변경이 아니므로 README 수정은 필요하지 않습니다.

## 추천 Commit Message

`fix: 구간 상세 위험도 산정 기준 문구 변경`

## Change Log

2026-07-20

- 위험도 기준 안내 문구 변경
- 화면 문구와 백엔드 산정 기준 정합성 검증
- 구간 상세 문서 업데이트

## Timestamp

2026-07-20 09:51:36 (KST)
