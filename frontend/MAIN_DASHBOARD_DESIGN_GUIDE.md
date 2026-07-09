# Main Dashboard Design Guide

## 1. 기본 화면 규격

- 화면 기준: PC Web
- Frame size: 1440 × 1500px
- 좌우 margin: 64px
- Main content width: 1312px
- Page background: `#F8FAFC`
- Section gap: 24px
- Grid system: 8px

## 2. 전체 레이아웃 순서

1. Header
2. Page Title
3. Current Weather Alert Banner
4. Filter Section
5. Summary Cards
6. Map + Ranking Area
7. Priority Inspection Table
8. Footer / Data Standard Notice

## 3. 공통 스타일

### Card

- Background: `#FFFFFF`
- Border: `1px solid #E5E7EB`
- Border radius: 12px
- Shadow: `0 2px 8px rgba(0,0,0,0.04)`

### Text Colors

- Main text: `#111827`
- Secondary text: `#374151`
- Description text: `#6B7280`
- Disabled / caption: `#9CA3AF`
- Border: `#E5E7EB`
- Input border: `#D1D5DB`
- Primary blue: `#2563EB`
- Danger red: `#EF4444`
- Danger dark: `#DC2626`
- Warning orange: `#F59E0B`
- Safe green: `#22C55E`

### Typography

- Font family: Pretendard
- Page title: 28px / 700 / line-height 36px / `#111827`
- Card title: 16px / 700 / line-height 24px / `#111827`
- Summary card title: 14px / 600 / line-height 20px / `#374151`
- Main number: 30px / 700 / line-height 36px / `#111827`
- Normal text: 13px / 400 / line-height 20px / `#374151`
- Sub text: 12px / 400 / line-height 16px / `#6B7280`
- Badge text: 11px / 600 / line-height 16px

## 4. Header

- Size: 1440 × 72px
- Inner content: 1312 × 72px
- Padding left/right: 64px
- Background: `#FFFFFF`
- Bottom border: `1px solid #E5E7EB`

### Header contents

Left:
- Logo icon: 32 × 32px
- Service title: `기상-철도 리스크 의사결정 지원 시스템`
- Title style: 18px / 700 / `#111827`

Right:
- Data label: 13px / `#6B7280`
- User/admin area: 13px / `#374151`

## 5. Page Title Section

- Size: 1312 × 80px
- Layout: horizontal, space-between

Left:
- Title: `대시보드`
- Title style: 28px / 700 / `#111827`
- Description: `기상특보와 철도 운행 데이터를 기반으로 위험 구간을 확인합니다.`
- Description style: 14px / 400 / `#6B7280`
- Gap between title and description: 8px

Right:
- Label: `최근 업데이트`
- Label style: 12px / 400 / `#9CA3AF`
- Date/time: `2026.07.07 14:30`
- Date style: 14px / 500 / `#4B5563`

## 6. Current Weather Alert Banner

- Size: 1312 × 88px
- Background: `#FFF7F7`
- Border: `1px solid #FCA5A5`
- Border radius: 12px
- Padding: 24px
- Layout: horizontal
- Gap: 16px
- Align: center

### Elements

Icon container:
- Size: 40 × 40px
- Background: `#FEE2E2`
- Icon size: 24 × 24px
- Icon color: `#EF4444`

Title:
- Text: `현재 발효 중인 기상특보`
- Style: 16px / 700 / `#DC2626`

Badge:
- Text: `호우 경보`
- Height: 28px
- Padding left/right: 12px
- Background: `#FFFFFF`
- Border: `1px solid #FCA5A5`
- Radius: 14px
- Text style: 13px / 600 / `#DC2626`

Sub info:
- Text: `대전광역시 외 3개 지역 · 14:00 기준 · 영향 가능 철도 구간 7개`
- Region text: 14px / 500 / `#374151`
- Supporting text: 13px / 400 / `#6B7280`
- Highlight number `7개`: 13px / 600 / `#DC2626`

## 7. Filter Section

- Size: 1312 × 88px
- Background: `#FFFFFF`
- Border: `1px solid #E5E7EB`
- Radius: 12px
- Padding: 16px 24px
- Layout: horizontal
- Align: bottom
- Gap: 16px

### Filter group

Each filter group:
- Size: 220 × 56px
- Layout: vertical
- Gap: 4px

Label:
- Size: 12px / 500 / `#6B7280`

Select box:
- Size: 220 × 40px
- Background: `#FFFFFF`
- Border: `1px solid #D1D5DB`
- Radius: 8px
- Padding left/right: 12px
- Text: 14px / 400 / `#374151`
- Dropdown icon: 16 × 16px / `#6B7280`

Filters:
1. 노선: 경부선
2. 특보 종류: 호우
3. 특보 등급: 전체
4. 열차 종류: 전체

Buttons:
- Reset button: 88 × 40px, border `#D1D5DB`, text `#4B5563`
- Apply button: 96 × 40px, background `#2563EB`, text `#FFFFFF`

## 8. Summary Cards

- Whole section: 1312 × 120px
- Card count: 4
- Card size: 316 × 120px
- Gap: 16px

### Card common

- Background: `#FFFFFF`
- Border: `1px solid #E5E7EB`
- Radius: 12px
- Padding: 20px
- Layout: horizontal
- Gap: 20px
- Align: center

Icon container:
- Size: 56 × 56px
- Shape: circle
- Icon size: 28 × 28px
- Icon color: `#FFFFFF`

Text area:
- Layout: vertical

Title:
- 14px / 600 / `#374151`

Number:
- 30px / 700 / `#111827`

Unit:
- 14px / 500 / `#4B5563`

Comparison label:
- 12px / 400 / `#6B7280`

Increase value:
- 12px / 600 / `#EF4444`

### Card data

1. 영향 가능 구간
   - Value: 7 개
   - Comparison: 전일 대비 +2 ↑
   - Icon background: `#EF6461`

2. 운행 지연 예상 열차
   - Value: 23 편
   - Comparison: 전일 대비 +6 ↑
   - Icon background: `#F5A742`

3. 평균 지연 시간(예상)
   - Value: 18.4 분
   - Comparison: 전일 대비 +7.2분 ↑
   - Icon background: `#FBBF24`

4. 취약도 높은 구간
   - Value: 5 개
   - Comparison: 전일 대비 +1 ↑
   - Icon background: `#4CC76A`

## 9. Map + Ranking Area

- Whole width: 1312px
- Layout: horizontal
- Gap: 24px

Left:
- Map card: 840 × 520px

Right:
- Ranking area: 448 × 520px
- Contains two cards:
  - Vulnerable segment TOP 5: 448 × 252px
  - Vulnerable station TOP 5: 448 × 252px
- Gap between ranking cards: 16px

## 10. Map / Heatmap Card

- Size: 840 × 520px
- Background: `#FFFFFF`
- Border: `1px solid #E5E7EB`
- Radius: 12px

Header:
- Size: 840 × 64px
- Padding: 0 24px
- Layout: horizontal / space-between / center

Title:
- Text: `경부선 기상 취약도 현황`
- Style: 16px / 700 / `#111827`

Info icon:
- Size: 16 × 16px
- Color: `#9CA3AF`

Full view button:
- Size: 96 × 36px
- Border: `1px solid #D1D5DB`
- Radius: 8px
- Text: 13px / 500 / `#2563EB`

Map container:
- Size: 792 × 408px
- Margin: 24px
- Background: `#F1F5F9`
- Radius: 8px

Zoom control:
- Button size: 36 × 36px
- Background: `#FFFFFF`
- Border: `1px solid #D1D5DB`
- Icon: 16 × 16px / `#4B5563`

Station marker:
- Size: 12 × 12px
- Radius: 50%

Railway line:
- Stroke: 4px

Risk colors:
- High: `#EF4444`
- Warning: `#F59E0B`
- Normal/Interest: `#22C55E`

Legend:
- Size: 128 × 112px
- Position: left 16px, bottom 16px
- Background: `rgba(255,255,255,0.95)`
- Border: `1px solid #E5E7EB`
- Radius: 8px
- Padding: 16px

## 11. Vulnerable Segment TOP 5 Card

- Size: 448 × 252px
- Background: `#FFFFFF`
- Border: `1px solid #E5E7EB`
- Radius: 12px

Header:
- Size: 448 × 48px
- Padding: 0 20px
- Title: `취약 구간 TOP 5`
- Title style: 16px / 700 / `#111827`
- More text: `더보기 >`
- More style: 12px / 500 / `#6B7280`

Table header:
- Size: 448 × 36px
- Background: `#F8FAFC`
- Border top/bottom: `1px solid #E5E7EB`
- Text style: 11px / 600 / `#6B7280`

Row:
- Height: 33.6px
- Text style: 12px
- Total rows: 5

Column widths:
- 순위: 48px
- 구간: 112px
- 노선: 72px
- 취약도: 88px
- 예상 지연(분): 128px

Badge:
- Size: 56 × 24px
- Radius: 6px
- Text: 11px / 600

Badge colors:
- 높음: bg `#FEF2F2`, border `#FCA5A5`, text `#DC2626`
- 주의: bg `#FFFBEB`, border `#FCD34D`, text `#D97706`
- 관심: bg `#F0FDF4`, border `#86EFAC`, text `#16A34A`

## 12. Vulnerable Station TOP 5 Card

Same component as Vulnerable Segment TOP 5.

- Size: 448 × 252px
- Header title: `취약 역 TOP 5`

Column widths:
- 순위: 48px
- 역명: 112px
- 노선: 72px
- 취약도: 88px
- 분석 지표: 128px

Use the same typography, border, badge, and row styles as the segment card.

## 13. Priority Inspection Table

- Size: 1312 × 320px
- Background: `#FFFFFF`
- Border: `1px solid #E5E7EB`
- Radius: 12px

Header:
- Size: 1312 × 64px
- Padding: 0 24px
- Layout: horizontal / space-between / center
- Title: `우선 점검 대상`
- Title style: 16px / 700 / `#111827`
- More text: 12px / 500 / `#6B7280`

Table header:
- Size: 1312 × 48px
- Padding: 0 24px
- Background: `#F8FAFC`
- Text: 13px / 600 / `#6B7280`

Data row:
- Size: 1312 × 52px
- Padding: 0 24px
- Text: 13px / 400 / `#374151`
- Important text: 13px / 600 / `#111827`
- Row count: 4

Column widths:
- 위험도: 120px
- 대상 구간: 240px
- 기상특보: 200px
- 주요 위험: 280px
- 대응 권고: 264px
- 상세: 160px

Risk badge:
- Size: 56 × 28px
- Radius: 6px

Detail button:
- Size: 88 × 32px
- Background: `#FFFFFF`
- Border: `1px solid #D1D5DB`
- Radius: 6px
- Text: 12px / 500 / `#374151`

## 14. Footer / Data Standard Notice

- Size: 1312 × 48px
- Text style: 12px / 400 / `#9CA3AF`
- Example text:
  - `철도 운행 실적 최근 3개월 기준 · 기상특보 정보 업데이트 14:30`

## 15. Implementation Notes for Codex

- Build the page as a single desktop dashboard first.
- Use reusable components:
  - Header
  - PageTitle
  - AlertBanner
  - FilterSection
  - SummaryCard
  - MapCard
  - RankingTableCard
  - RiskBadge
  - PriorityInspectionTable
  - Button
  - SelectBox
- Keep all dimensions close to the values defined in this guide.
- Use CSS variables or design tokens for colors, spacing, typography, and radius.
- The UI should look like a clean Korean admin dashboard.
- Do not add a sidebar to the main dashboard.
- Main content must be centered with 64px left/right margins.
- Use table layout for TOP 5 cards, not simple list layout.

## 16. Sidebar / Left Navigation

메인 대시보드의 왼쪽 고정 내비게이션 영역이다.

### Sidebar Container

- Width: `200px`
- Height: `100vh`
- Background: `#001B3F`
- Padding: `20px 12px`
- Position: `fixed left`
- Text color default: `#E5E7EB`

### Logo Area

- Size: `176 × 48px`
- Layout: horizontal
- Gap: `10px`
- Margin bottom: `28px`

Logo icon:
- Size: `32 × 32px`
- Color: `#FFFFFF`

Title:
- Text: `기상-철도 리스크`
- Font: `16px / 700`
- Color: `#FFFFFF`

Subtitle:
- Text: `의사결정 지원 시스템`
- Font: `11px / 400`
- Color: `#CBD5E1`

### Navigation List

- Width: `176px`
- Layout: vertical
- Gap: `8px`

### Navigation Item

Default:
- Size: `176 × 44px`
- Border radius: `8px`
- Padding: `0 14px`
- Layout: horizontal
- Gap: `12px`
- Icon size: `18 × 18px`
- Icon color: `#E5E7EB`
- Text: `14px / 500`
- Text color: `#E5E7EB`

Active:
- Background: `#2563EB`
- Icon color: `#FFFFFF`
- Text color: `#FFFFFF`
- Font weight: `600`

Hover:
- Background: `rgba(255,255,255,0.08)`

### Menu Items

1. `대시보드`
   - Icon: `Home`
   - Active on main dashboard

2. `역 상세`
   - Icon: `TrainFront`

3. `구간 상세`
   - Icon: `GitBranch` or `Route`

4. `RAG 심층 설명`
   - Icon: `CircleHelp` or `Sparkles`

5. `데이터 분석·통계`
   - Icon: `BarChart3`

### Bottom Area

- Position: bottom
- Width: `176px`

Divider:
- Height: `1px`
- Color: `rgba(255,255,255,0.12)`
- Margin bottom: `16px`

Data standard item:
- Size: `176 × 40px`
- Icon: `CircleHelp`
- Icon size: `16 × 16px`
- Text: `데이터 기준 안내`
- Text style: `13px / 500 / #E5E7EB`

Collapse icon:
- Size: `16 × 16px`
- Color: `#CBD5E1`