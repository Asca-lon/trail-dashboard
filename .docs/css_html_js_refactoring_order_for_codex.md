# CSS 통합 및 HTML·JavaScript 연계 수정 작업 순서

## 1. 목적
현재 CSS의 중복 스타일과 선택자를 통합하고, 필요 시 HTML class와 JavaScript 선택자 참조를 함께 수정한다.

유지해야 할 사항:
- 기존 디자인과 레이아웃
- 반응형 동작
- JavaScript 기능
- Mock 데이터 구조
- API 요청·응답 구조
- 백엔드 코드
- 기존 페이지 경로

핵심 순서:

> 중복 선언 제거 → 미디어쿼리 통합 → CSS 변수 정리 → 동일 선택자 묶기 → 공통 class 검토 → HTML 수정 → JavaScript 안전성 수정 → 중복 CSS 삭제 → 기능 검증

---

## 2. 작업 원칙
1. CSS 선택자를 바꾸기 전에 HTML과 JavaScript 사용 위치를 검색한다.
2. `querySelector`, `querySelectorAll`, `closest`, `matches`, `classList`에서 참조하는 class를 확인한다.
3. 상태 제어용 class는 임의로 삭제하거나 이름을 바꾸지 않는다.
4. 기존 BEM class는 유지하고, 필요한 경우 공통 스타일 class만 추가한다.
5. 각 단계가 끝날 때 화면과 JavaScript 동작을 확인한다.
6. CSS는 줄었지만 HTML class가 지나치게 늘면 적용하지 않는다.
7. 디자인이나 기능이 달라지면 해당 변경을 되돌린다.

---

## 3. 작업 전 분석

### 3.1 CSS 선택자 분류
- 레이아웃
- 카드
- 버튼
- 테이블
- 페이지 제목
- breadcrumb
- 상태 modifier
- 반응형
- hover 및 focus

### 3.2 HTML 검색
프로젝트 전체 HTML에서 다음 형태를 검색한다.

```html
class="..."
```

주요 대상:
```text
site-header
station-global-header
dashboard-main
station-detail-main
route-detail-main
station-breadcrumb
route-breadcrumb
station-page-title
route-page-title
summary-card
map-card
ranking-card
inspection-card
station-info-card
station-metric-card
station-chart-card
station-detail-card
route-info-card
route-content-card
route-chart-card
route-impact-card
route-alert-card
route-risk-criteria
```

### 3.3 JavaScript 검색
프로젝트 전체 JavaScript에서 다음을 검색한다.

```js
querySelector
querySelectorAll
getElementById
closest
matches
classList.add
classList.remove
classList.toggle
classList.contains
element.className
event.target.className
dataset
```

이름을 유지할 가능성이 큰 상태 class:
```text
sidebar--open
sidebar__navigation-link--active
route-map__item--high
route-map__item--warning
route-map__item--interest
route-map__item--none
station-risk-status--high
station-risk-status--warning
station-risk-status--interest
station-risk-status--none
route-risk-card--high
route-risk-card--warning
route-risk-card--interest
route-risk-card--none
inspection-table__row--selected
```

---

## 4. 1단계: 기능 영향 없는 정리

### 4.1 불필요한 빈 줄 제거
연속된 빈 줄은 한 줄만 남긴다.

### 4.2 동일 선택자의 중복 선언 통합
예:

```css
.sidebar__navigation-link {
  display: flex;
  align-items: center;
  width: var(--sidebar-menu-width);
  color: var(--sidebar-text);
  text-decoration: none;
}

.sidebar__navigation-link {
  height: 44px;
  gap: 12px;
  padding: 0 14px;
  border-radius: var(--radius-control);
  font-size: 14px;
  font-weight: 500;
  line-height: 20px;
}
```

다음처럼 합친다.

```css
.sidebar__navigation-link {
  display: flex;
  align-items: center;
  width: var(--sidebar-menu-width);
  height: 44px;
  gap: 12px;
  padding: 0 14px;
  color: var(--sidebar-text);
  border-radius: var(--radius-control);
  font-size: 14px;
  font-weight: 500;
  line-height: 20px;
  text-decoration: none;
}
```

이 단계에서는 HTML과 JavaScript를 수정하지 않는다.

---

## 5. 2단계: 동일 breakpoint 미디어쿼리 통합

대상:
```css
@media (max-width: 1180px)
@media (max-width: 1024px)
@media (max-width: 640px)
```

작업:
1. 동일 breakpoint를 모두 찾는다.
2. 같은 breakpoint 규칙을 한곳으로 모은다.
3. 동일 선택자 충돌 여부를 확인한다.
4. 뒤쪽 선언이 덮어쓰던 최종값을 유지한다.
5. 통합 전후 반응형 화면을 비교한다.

---

## 6. 3단계: 공통 CSS 변수 추가

### 6.1 포커스 변수

```css
:root {
  --focus-outline: 3px solid rgba(37, 99, 235, 0.24);
  --focus-outline-strong: 3px solid rgba(37, 99, 235, 0.36);
  --focus-offset: 2px;
}
```

```css
.button:focus-visible,
.brand:focus-visible,
.filter-group__select:focus-visible,
.ranking-card__more:focus-visible,
.ranking-table__link:focus-visible,
.inspection-link:focus-visible,
.inspection-table__button:focus-visible,
.station-info-card__change:focus-visible,
.station-page-title__back:focus-visible,
.station-info-card__select:focus-visible,
.route-info-card__change-button:focus-visible {
  outline: var(--focus-outline);
  outline-offset: var(--focus-offset);
}
```

sidebar는 더 진한 변수를 사용한다.

```css
.sidebar__navigation-link:focus-visible,
.sidebar__collapse-button:focus-visible {
  outline: var(--focus-outline-strong);
  outline-offset: var(--focus-offset);
}
```

### 6.2 위험 상태 색상 변수

```css
:root {
  --risk-high: #DC2626;
  --risk-warning: #D97706;
  --risk-interest: #16A34A;
  --risk-none: #64748B;

  --risk-high-bg: #FEF2F2;
  --risk-warning-bg: #FFFBEB;
  --risk-interest-bg: #F0FDF4;
  --risk-none-bg: #F8FAFC;

  --risk-high-border: #FCA5A5;
  --risk-warning-border: #FCD34D;
  --risk-interest-border: #86EFAC;
  --risk-none-border: #E2E8F0;
}
```

상태 class 이름은 그대로 두고 색상값만 변수로 교체한다.

---

## 7. 4단계: 공통 페이지 컨테이너 통합

```css
.dashboard-main,
.station-detail-main,
.route-detail-main {
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: min(
    var(--content-width),
    calc(100% - (var(--page-margin) * 2))
  );
  margin: 0 auto;
}

.dashboard-main {
  padding: 24px 0 48px;
}

.station-detail-main,
.route-detail-main {
  padding: 24px 0 40px;
}
```

HTML과 JavaScript는 기존 class를 유지하므로 수정하지 않는다.

---

## 8. 5단계: 헤더 스타일 통합

```css
.site-header,
.station-global-header {
  height: 64px;
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
}

.site-header__inner,
.station-global-header__inner {
  display: flex;
  align-items: center;
  width: min(
    var(--content-width),
    calc(100% - (var(--page-margin) * 2))
  );
  height: 64px;
  margin: 0 auto;
}

.station-global-header__inner {
  justify-content: space-between;
}
```

우선 CSS 선택자 묶기를 사용하고 HTML에 새 class는 추가하지 않는다.

---

## 9. 6단계: breadcrumb 통합

```css
.station-breadcrumb,
.route-breadcrumb {
  display: flex;
  align-items: center;
  min-height: 24px;
  gap: 8px;
}

.station-breadcrumb__link,
.route-breadcrumb__link {
  color: var(--color-description-text);
  font-size: 12px;
  font-weight: 400;
  line-height: 18px;
  text-decoration: none;
}

.station-breadcrumb__separator,
.route-breadcrumb__separator {
  width: 12px;
  height: 12px;
}

.station-breadcrumb__current,
.route-breadcrumb__current {
  color: var(--color-primary-blue);
  font-size: 12px;
  font-weight: 600;
  line-height: 18px;
}
```

HTML과 JavaScript 수정은 필요 없다.

---

## 10. 7단계: 페이지 제목 통합

```css
.station-page-title,
.route-page-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 64px;
  gap: 24px;
}

.station-page-title__text,
.route-page-title__text {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.station-page-title__heading,
.route-page-title__heading {
  margin: 0;
  color: var(--color-main-text);
  font-size: 28px;
  font-weight: 700;
  line-height: 36px;
}

.station-page-title__description,
.route-page-title__description {
  margin: 0;
  color: var(--color-description-text);
  font-size: 14px;
  font-weight: 400;
  line-height: 20px;
}
```

HTML과 JavaScript 수정은 필요 없다.

---

## 11. 8단계: 테이블 공통 스타일 통합

```css
.ranking-table,
.inspection-table,
.station-alert-table,
.route-alert-analysis-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
}

.ranking-card__table-wrap,
.inspection-card__table-wrap,
.station-alert-table-wrap,
.route-alert-analysis-table-wrap {
  width: 100%;
  overflow-x: auto;
}
```

다음은 공통화하지 않는다.
- 열 너비
- 행 높이
- padding
- font-size
- thead 높이
- 선택 행 색상
- column별 정렬

---

## 12. 9단계: 카드 공통화 방식 결정

공통 스타일:
```css
background: var(--color-surface);
border: 1px solid var(--color-border);
border-radius: var(--radius-card);
box-shadow: var(--shadow-card);
```

### 방식 A: 선택자 묶기
HTML 수정이 필요 없다.

```css
.filter-panel,
.summary-card,
.map-card,
.ranking-card,
.inspection-card,
.station-info-card,
.station-metric-card,
.station-chart-card,
.station-detail-card,
.route-info-card,
.route-content-card,
.route-chart-card,
.route-impact-card,
.route-alert-card,
.route-risk-criteria {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-card);
  box-shadow: var(--shadow-card);
}
```

### 방식 B: `.card` 공통 class 추가

```css
.card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-card);
  box-shadow: var(--shadow-card);
}
```

HTML:

```html
<section class="summary-card card">
<section class="station-info-card card">
<section class="route-content-card card">
```

권장:
- HTML 파일이 적고 수정이 안전하면 방식 B
- HTML 파일이 많거나 JavaScript 의존성이 크면 방식 A
- 기존 고유 BEM class는 삭제하지 않는다.

---

## 13. 10단계: 카드 제목 공통화

선택자 묶기:

```css
.map-card__title,
.ranking-card__title,
.inspection-card__title,
.station-chart-card__title,
.station-detail-card__title {
  margin: 0;
  color: var(--color-main-text);
  font-size: 16px;
  font-weight: 700;
  line-height: 24px;
}
```

또는 공통 class:

```css
.card-title {
  margin: 0;
  color: var(--color-main-text);
  font-size: 16px;
  font-weight: 700;
  line-height: 24px;
}
```

```html
<h2 class="map-card__title card-title">
```

현재 페이지 수가 적다면 선택자 묶기를 우선한다.

---

## 14. 11단계: 버튼 공통화 검토

```css
.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-control);
  cursor: pointer;
  font: inherit;
  font-weight: 500;
}

.button--outline {
  color: var(--color-secondary-text);
  background: var(--color-surface);
  border: 1px solid var(--color-input-border);
}

.button--primary {
  color: var(--color-surface);
  background: var(--color-primary-blue);
  border: 1px solid var(--color-primary-blue);
}

.button--sm {
  height: 32px;
  font-size: 12px;
}

.button--md {
  height: 40px;
  font-size: 13px;
}
```

HTML:

```html
<button class="station-info-card__change button button--outline button--sm">
```

크기와 동작이 다른 버튼은 억지로 통합하지 않는다.

---

## 15. 12단계: 아이콘 wrapper 통합

```css
.alert-banner__icon,
.summary-card__icon,
.station-info-card__icon,
.station-metric-card__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 auto;
}
```

각 아이콘의 크기, 색상, 배경은 개별 선택자에 남긴다.

---

## 16. 13단계: 상태 class 유지

다음 modifier는 JavaScript가 동적으로 추가할 수 있으므로 이름을 유지한다.

```text
--high
--warning
--interest
--none
--active
--selected
--open
```

예:
```css
.station-risk-status--high
.route-risk-card--high
.route-map__item--high
.risk-badge--high
```

색상값만 공통 변수로 바꾸고 class 이름은 통합하지 않는다.

---

## 17. 14단계: JavaScript 수정 기준

### 17.1 className 전체 비교 제거

변경 전:

```js
if (element.className === "summary-card") {
```

변경 후:

```js
if (element.classList.contains("summary-card")) {
```

### 17.2 className 전체 덮어쓰기 방지

변경 전:

```js
element.className = "route-risk-card route-risk-card--high";
```

변경 후:

```js
element.classList.remove(
  "route-risk-card--high",
  "route-risk-card--warning",
  "route-risk-card--interest",
  "route-risk-card--none"
);

element.classList.add("route-risk-card--high");
```

공통 `.card` class가 추가되더라도 제거되지 않도록 한다.

### 17.3 querySelector는 기존 고유 class 유지

유지:

```js
document.querySelector(".summary-card")
```

피할 것:

```js
document.querySelector(".card")
```

`.card`는 여러 요소에 적용될 수 있으므로 JavaScript 요소 식별용으로 사용하지 않는다.

---

## 18. 15단계: HTML 수정 기준

공통 class 방식을 선택한 경우에만 수정한다.

카드:

```html
<section class="summary-card card">
```

제목:

```html
<h2 class="summary-card__title card-title">
```

버튼:

```html
<button
  class="station-info-card__change button button--outline button--sm"
>
```

기존 BEM class는 삭제하지 않는다.

---

## 19. 16단계: 공통화 후 중복 CSS 삭제

공통 `.card`가 적용된 경우 기존 개별 선택자에서 다음 속성을 삭제한다.

```css
background
border
border-radius
box-shadow
```

단, HTML에 `.card`가 실제로 추가된 것을 확인한 뒤 삭제한다.

---

## 20. 17단계: CSS 정렬 순서

```text
1. CSS 변수
2. Reset 및 전역 스타일
3. 접근성 유틸리티
4. 공통 레이아웃
5. 공통 컴포넌트
6. Header
7. Sidebar
8. Dashboard
9. Map 및 Ranking
10. Inspection
11. Station detail
12. Route detail
13. 상태 modifier
14. 반응형 미디어쿼리
```

상태 modifier는 기본 선택자보다 뒤에 둔다.

---

## 21. 18단계: 기능 검증

### 화면
- 메인 대시보드
- Sidebar
- 필터
- 요약 카드
- 지도
- Ranking
- Inspection
- 역 상세
- 구간 상세

### 반응형
```text
1440px
1180px
1024px
768px
640px
375px
```

### 상태
- 위험
- 주의
- 관심
- 해당 없음
- active
- selected
- sidebar open

### 상호작용
- 버튼 클릭
- 링크 이동
- select 변경
- tooltip
- sidebar
- modal
- 테이블 행 선택
- 역 변경
- 구간 변경

### 접근성
- Tab 키 이동
- focus-visible
- 버튼 focus
- 링크 focus
- select focus

---

## 22. Codex 최종 실행 순서

1. CSS, HTML, JavaScript 전체에서 class 사용 위치를 검색한다.
2. JavaScript가 동적으로 변경하는 상태 class 목록을 작성한다.
3. 불필요한 빈 줄을 제거한다.
4. 동일 선택자의 중복 선언을 합친다.
5. 동일 breakpoint 미디어쿼리를 통합한다.
6. 반복 포커스와 상태 색상을 CSS 변수로 만든다.
7. 공통 페이지 컨테이너 선택자를 묶는다.
8. 공통 헤더 선택자를 묶는다.
9. station 및 route breadcrumb를 묶는다.
10. station 및 route 페이지 제목을 묶는다.
11. 공통 테이블 및 wrapper를 묶는다.
12. 카드 통합 방식을 결정한다.
13. 필요하면 `.card`를 HTML에 추가한다.
14. 필요하면 `.card-title`을 추가한다.
15. 필요하면 `.button` modifier 구조를 적용한다.
16. JavaScript의 `className` 전체 비교를 확인한다.
17. 전체 비교는 `classList.contains()`로 변경한다.
18. 상태 class 전체 덮어쓰기는 `classList` 방식으로 변경한다.
19. 공통화된 속성을 개별 CSS에서 삭제한다.
20. CSS 선언 순서를 정리한다.
21. 데스크톱 화면을 검증한다.
22. 1180px, 1024px, 640px 반응형 화면을 검증한다.
23. JavaScript 상호작용을 검증한다.
24. 수정 전후 CSS 줄 수와 변경 파일을 비교한다.
25. 디자인이나 기능이 변경된 통합은 되돌린다.

---

## 23. 작업 완료 보고 형식

### 수정한 CSS 항목
- 중복 선택자 통합:
- 미디어쿼리 통합:
- CSS 변수 추가:
- 공통 레이아웃 통합:
- 카드 스타일 통합:
- 테이블 스타일 통합:
- 포커스 스타일 통합:

### 수정한 HTML 파일
- 파일명:
- 추가한 공통 class:
- 기존 class 유지 여부:

### 수정한 JavaScript 파일
- 파일명:
- 수정한 선택자:
- className 비교 변경:
- classList 처리 변경:
- 기능 영향:

### 유지한 class
- JavaScript 상태 제어 class:
- 페이지별 고유 class:
- 요소 식별용 class:

### 수정 전후 비교
- 수정 전 CSS 줄 수:
- 수정 후 CSS 줄 수:
- 줄어든 CSS 줄 수:
- 새로 추가된 공통 class:
- 제거된 중복 속성:

### 기능 검증
- 데스크톱:
- 1180px:
- 1024px:
- 640px:
- Sidebar:
- Filter:
- Tooltip:
- Table:
- Station detail:
- Route detail:
- Focus-visible:
- 콘솔 오류:

### 보호 영역 확인
- Mock 데이터 변경 없음
- API 변경 없음
- 백엔드 변경 없음
- 기존 페이지 경로 변경 없음
- 기존 상태 class 이름 변경 없음
- 기존 디자인 변경 없음

---

## 24. Codex 실행 지시문

현재 CSS 파일과 연결된 모든 HTML 및 JavaScript 파일을 분석한 뒤 위 순서대로 CSS를 통합하라.

먼저 CSS class가 HTML과 JavaScript에서 어떻게 사용되는지 프로젝트 전체 검색을 수행하라.

JavaScript에서 상태 변경이나 요소 선택에 사용하는 class는 임의로 삭제하거나 이름을 변경하지 마라.

공통 `.card`, `.card-title`, `.button` class를 추가할 경우 기존 BEM class는 삭제하지 말고 함께 유지하라.

JavaScript가 `className` 전체 문자열을 비교하거나 덮어쓰는 경우 공통 class가 사라지지 않도록 `classList.contains`, `classList.add`, `classList.remove`, `classList.toggle` 방식으로 수정하라.

CSS 줄 수를 줄이기 위해 디자인이나 기능을 변경하지 마라.

동일한 CSS 속성이 아닌 선택자를 억지로 통합하지 마라.

수정 전후의 CSS 줄 수, HTML 변경 파일, JavaScript 변경 파일, 기능 검증 결과를 지정된 형식으로 보고하라.
