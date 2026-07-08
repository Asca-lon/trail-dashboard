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

# 코드 설명

`frontend/dashboard.html`은 HTML5 시맨틱 태그를 사용하여 페이지 구조를 정의합니다.

`frontend/style.css`는 디자인 가이드의 색상, 여백, 폰트, radius 값을 CSS 변수로 관리합니다.

`frontend/assets/icons/`는 외부에서 받은 SVG 아이콘 파일을 모아두는 폴더입니다.

로고, 알림, 드롭다운 등 UI에서 반복 사용하는 아이콘은 이 폴더에 저장한 뒤 HTML에서 `img` 태그 또는 CSS 배경 이미지로 불러옵니다.

# API

이번 작업에서는 API를 직접 연결하지 않았습니다.

향후 연결 예정 API:

- `GET /lines`
- `GET /alerts/active`
- `GET /vulnerability/segments`
- `GET /vulnerability/stations`
- `GET /heatmap`
- `GET /checklist`

# Database

이번 작업에서는 Database 변경이 없습니다.

# 주의사항

- 기존 루트 `index.html`은 API / Mock 콘솔로 유지합니다.
- 신규 프론트엔드 산출물은 `frontend/` 폴더에서 관리합니다.
- 현재 구현 범위는 캡쳐본에 포함된 상단 4개 섹션입니다.
- 외부 아이콘을 사용할 때는 라이선스와 출처를 확인해야 합니다.
- 빈 폴더는 Git에 저장되지 않으므로 `frontend/assets/icons/.gitkeep` 파일로 폴더를 추적합니다.

# 변경 이력

## Change Log

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

# 다음 작업

- Summary Cards
- Map / Heatmap Card
- Vulnerable Ranking Cards
- Priority Inspection Table 구현
- Map / Heatmap 영역 구현
- Ranking TOP 5 카드 구현
- Priority Inspection Table 구현
- mock API 데이터 연결

# 작업 요약

## 완료한 내용

- `frontend/dashboard.html` 생성
- `frontend/style.css` 생성
- 대시보드 상단 4개 섹션 구현
- Summary Cards
- Map / Heatmap Card
- Vulnerable Ranking Cards
- Priority Inspection Table 영역 구현
- SVG 아이콘 보관 폴더 생성

## 수정한 파일

- `frontend/dashboard.html`
- `frontend/style.css`
- `frontend/assets/icons/.gitkeep`
- `.docs/Frontend.md`

## 구현 이유

기존 `index.html`을 보존하면서 실제 대시보드 화면을 독립적으로 개발하기 위해 `frontend/` 폴더에 신규 파일을 생성했습니다.

외부에서 받은 SVG 아이콘을 한 곳에서 관리하기 위해 `frontend/assets/icons/` 폴더를 생성했습니다.

## 변경 사항

- Figma 디자인 가이드 기반 색상 및 크기 적용
- 접근성을 위한 `label`과 `select` 연결
- 반응형 레이아웃 적용
- 아이콘 에셋 저장 위치 추가

## 새롭게 배운 개념

- HTML5 시맨틱 구조
- CSS 디자인 토큰
- 접근 가능한 폼 라벨
- Flexbox 반응형 레이아웃
- 정적 SVG 에셋 관리

## 실무에서는

실무에서는 디자인 토큰을 CSS 변수 또는 디자인 시스템으로 관리하고, API 연동 전에는 mock 데이터를 기준으로 UI 구조를 먼저 안정화합니다.

아이콘은 프로젝트 내부 에셋 폴더에 모아두고, 파일명은 `alert.svg`, `logo.svg`, `chevron-down.svg`처럼 역할이 드러나도록 관리합니다.

## 개선 가능한 부분

- 실제 폰트 파일 또는 CDN 연결
- API 데이터 기반 동적 렌더링
- 브라우저 시각 회귀 테스트
- SVG 아이콘 라이선스 출처 문서화

## 다음 작업

남은 작업은 실제 mock/API 데이터 연결과 전체 레이아웃 시각 검수입니다.

아이콘 파일을 추가한 뒤 Header 로고와 Alert Banner 아이콘에 실제 SVG를 연결합니다.

## 복습 문제

1. `label`의 `for` 속성과 `select`의 `id`를 연결하는 이유는 무엇인가요?
2. 색상을 CSS 변수로 관리하면 유지보수에 어떤 장점이 있나요?
3. Flexbox가 이번 필터 영역 구현에 적합한 이유는 무엇인가요?
4. 빈 폴더를 Git에 남기기 위해 `.gitkeep`을 사용하는 이유는 무엇인가요?

## 오늘 배운 내용

- 시맨틱 HTML
- CSS 변수
- Flexbox
- 접근성 라벨
- SVG 아이콘 에셋 관리
- `.gitkeep`

## Timestamp

2026-07-08 14:39:00 (KST)

















