# STATION DETAIL DESIGN GUIDE

## 1. 문서 개요

본 문서는 기상-철도 리스크 의사결정 지원 시스템의 `역 상세 화면(Station Detail Page)` UI/UX 디자인 및 프론트엔드 구현 규격을 정의한다.

역 상세 화면은 사용자가 특정 철도역을 선택했을 때 해당 역의 기상 영향과 철도 운행 현황을 종합적으로 확인할 수 있도록 구성한다.

본 화면은 메인 대시보드의 디자인 시스템을 그대로 사용하며 전체적인 색상, 카드 스타일, 버튼, Badge, Typography 등을 통일한다.

### 주요 정보 흐름

1. Global Header
2. Breadcrumb
3. Page Title Section
4. Station Information Header
5. Key Metric Cards
6. Analysis Charts
7. Weather Alert Statistics
8. Historical Major Cases
9. Metric Description

---

## 2. 기본 화면 규격

### Page

- 화면 기준: PC Web
- Desktop-first design
- Target viewport width: `1440px` 이상
- Main content width: `1312px`
- Page background: `#F8FAFC`
- 기본 Section gap: `16px`
- 큰 Section gap: `24px`
- Grid system: `8px`

### Main Content Layout

```text
Main Content

├── Global Header
├── Breadcrumb
├── Page Title Section
├── Station Information Header
├── Key Metric Cards × 4
├── Analysis Chart Area
│   ├── Hourly Average Delay Chart
│   └── Alert vs Normal Delay Comparison Chart
├── Analysis Detail Area
│   ├── Weather Alert Statistics
│   └── Historical Major Cases
└── Metric Description
```

---

## 3. 공통 디자인 시스템

### Card Style

모든 주요 카드 컴포넌트는 아래 스타일을 기본으로 사용한다.

- Background: `#FFFFFF`
- Border: `1px solid #E5E7EB`
- Border radius: `12px`
- Shadow: `0 2px 8px rgba(0,0,0,0.04)`

강한 그림자는 사용하지 않는다.

### Color System

| Usage | Color |
|---|---|
| Page Background | `#F8FAFC` |
| Card Background | `#FFFFFF` |
| Primary Text | `#111827` |
| Secondary Text | `#374151` |
| Description Text | `#6B7280` |
| Caption Text | `#9CA3AF` |
| Primary Blue | `#2563EB` |
| Danger Red | `#EF4444` |
| Warning Orange | `#F59E0B` |
| Safe Green | `#22C55E` |
| Default Border | `#E5E7EB` |
| Input Border | `#D1D5DB` |

### Typography System

Font Family: `Pretendard`

| Usage | Size | Weight | Color |
|---|---:|---:|---|
| Page Title | `28px` | `700` | `#111827` |
| Station Name | `24px` | `700` | `#111827` |
| Metric Number | `28px` | `700` | `#111827` |
| Card Title | `16px` | `700` | `#111827` |
| Metric Title | `13px` | `600` | `#374151` |
| Normal Text | `13px` | `400` | `#374151` |
| Table Text | `12px` | `400` | `#374151` |
| Supporting Text | `12px` | `400` | `#6B7280` |
| Badge Text | `11~13px` | `600` | Status Color |

### Border Radius System

| Element | Radius |
|---|---:|
| Main Card | `12px` |
| Station Icon | `10px` |
| Risk Status Box | `10px` |
| Historical Case Item | `8px` |
| Large Button | `8px` |
| Small Button | `6px` |
| Badge | `6px` |
| Circle Icon Container | `50%` |

### Shadow System

```css
box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
```

---

## 4. Global Header

### Header Container

- Width: `100%`
- Height: `64px`
- Background: `#FFFFFF`
- Bottom border: `1px solid #E5E7EB`

Layout:

- Display: `flex`
- Align items: `center`
- Justify content: `space-between`

### Left Area: Menu Button

- Size: `40 × 40px`
- Icon: `Menu`
- Icon library: `Lucide`
- Icon size: `20 × 20px`
- Icon color: `#374151`

### Right Area

Contents:

1. Data timestamp
2. Notification icon
3. User avatar
4. User name
5. Dropdown icon

#### Data Timestamp Label

- Text: `데이터 기준:`
- Font size: `12px`
- Font weight: `400`
- Color: `#6B7280`

#### Data Timestamp Value

- Example: `2026.07.07 14:30`
- Font size: `13px`
- Font weight: `500`
- Color: `#374151`

#### Notification Icon

- Icon: `Bell`
- Size: `18 × 18px`
- Color: `#64748B`

#### User Avatar

- Size: `32 × 32px`
- Border radius: `50%`
- Background: `#E5E7EB`

#### User Name

- Font size: `13px`
- Font weight: `500`
- Color: `#111827`

#### Dropdown Icon

- Icon: `ChevronDown`
- Size: `14 × 14px`
- Color: `#64748B`

---

## 5. Breadcrumb

### Container

- Width: `1312px`
- Height: `24px`

Layout:

- Display: `flex`
- Align items: `center`
- Gap: `8px`

### Dashboard Text

- Text: `대시보드`
- Font size: `12px`
- Font weight: `400`
- Color: `#6B7280`

### Separator

- Icon: `ChevronRight`
- Size: `12 × 12px`
- Color: `#9CA3AF`

### Current Page

- Text: `역 상세`
- Font size: `12px`
- Font weight: `600`
- Color: `#2563EB`

---

## 6. Page Title Section

### Container

- Width: `1312px`
- Height: `64px`

Layout:

- Display: `flex`
- Justify content: `space-between`
- Align items: `center`

### Title Area

#### Page Title

- Text: `역 상세`
- Font size: `28px`
- Font weight: `700`
- Line height: `36px`
- Color: `#111827`

#### Description

- Text: `특정 역의 기상 영향 및 운행 현황을 종합적으로 확인합니다.`
- Font size: `14px`
- Font weight: `400`
- Line height: `20px`
- Color: `#6B7280`

#### Title / Description Gap

- Gap: `4px`

### Back Button

- Size: `120 × 40px`
- Background: `#FFFFFF`
- Border: `1px solid #D1D5DB`
- Border radius: `8px`

Layout:

- Display: `flex`
- Align items: `center`
- Justify content: `center`
- Gap: `8px`

Icon:

- Icon: `ArrowLeft`
- Size: `16 × 16px`
- Color: `#374151`

Text:

- Text: `목록으로`
- Font size: `13px`
- Font weight: `500`
- Color: `#374151`

---

## 7. Station Information Header

### Card Container

- Width: `1312px`
- Height: `104px`
- Background: `#FFFFFF`
- Border: `1px solid #E5E7EB`
- Border radius: `12px`
- Padding: `16px 20px`
- Shadow: `0 2px 8px rgba(0,0,0,0.04)`

Layout:

- Display: `flex`
- Align items: `center`
- Justify content: `space-between`

---

## 8. Station Information Area

### Layout

- Display: `flex`
- Align items: `center`
- Gap: `16px`

### Station Icon Container

- Size: `56 × 56px`
- Background: `#2563EB`
- Border radius: `10px`

Icon:

- Icon: `TrainFront`
- Size: `28 × 28px`
- Color: `#FFFFFF`

### Station Name Area

First Row contents:

1. Station name
2. Railway line badge

- Display: `flex`
- Align items: `center`
- Gap: `12px`

#### Station Name

- Example: `대전역`
- Font size: `24px`
- Font weight: `700`
- Color: `#111827`

#### Railway Line Badge

- Height: `28px`
- Padding: `0 10px`
- Background: `#F1F5F9`
- Border radius: `6px`

Text:

- Example: `경부선`
- Font size: `12px`
- Font weight: `500`
- Color: `#475569`

#### Station Address

- Example: `대전광역시 동구 중앙로 215`
- Font size: `13px`
- Font weight: `400`
- Color: `#64748B`

### Change Station Button

- Size: `80 × 36px`
- Background: `#FFFFFF`
- Border: `1px solid #D1D5DB`
- Border radius: `6px`

Text:

- Text: `역 변경`
- Font size: `12px`
- Font weight: `500`
- Color: `#374151`

---

## 9. Current Risk Status

### Container

- Size: `280 × 72px`
- Background: `#FFF7F7`
- Border radius: `10px`
- Padding: `16px 20px`

Layout:

- Display: `flex`
- Align items: `center`
- Gap: `16px`

### Alert Icon

- Icon: `TriangleAlert`
- Size: `28 × 28px`
- Color: `#EF4444`

### Risk Title

- Text: `현재 위험도: 높음`
- Font size: `14px`
- Font weight: `700`
- Color: `#EF4444`

### Alert Information

- Example: `호우 경보 · 07.07 14:00 기준`
- Font size: `12px`
- Font weight: `400`
- Color: `#64748B`

---

## 10. Key Metric Cards

### Section Container

- Width: `1312px`
- Height: `120px`

Layout:

- Display: `grid`
- Grid columns: `repeat(4, 1fr)`
- Gap: `16px`

Card width calculation:

```text
(1312 - 48) / 4 = 316px
```

Card size:

- Width: `316px`
- Height: `120px`

---

## 11. Metric Card Common Style

- Background: `#FFFFFF`
- Border: `1px solid #E5E7EB`
- Border radius: `12px`
- Padding: `20px`
- Shadow: `0 2px 8px rgba(0,0,0,0.04)`

Layout:

- Display: `flex`
- Align items: `center`
- Gap: `16px`

### Icon Container

- Size: `48 × 48px`
- Border radius: `50%`

Icon:

- Size: `24 × 24px`

### Metric Typography

#### Title

- Font size: `13px`
- Font weight: `600`
- Color: `#374151`

#### Value

- Font size: `28px`
- Font weight: `700`
- Line height: `36px`
- Color: `#111827`

#### Unit

- Font size: `13px`
- Font weight: `500`
- Color: `#4B5563`

#### Comparison Label

- Font size: `12px`
- Font weight: `400`
- Color: `#6B7280`

#### Comparison Value

- Font size: `12px`
- Font weight: `600`
- Color: `#EF4444`

---

## 12. Metric Card Data

### Metric Card 1

- Title: `평균 지연 시간`
- Value: `18.4분`
- Icon: `Clock3`
- Icon Background: `#FFF7ED`
- Icon Color: `#F59E0B`

### Metric Card 2

- Title: `평균 지연 증가량`
- Value: `+10.2분`
- Icon: `TrendingUp`
- Icon Background: `#F3E8FF`
- Icon Color: `#7C3AED`

### Metric Card 3

- Title: `지연률`
- Value: `12.6%`
- Icon: `Percent`
- Icon Background: `#F3E8FF`
- Icon Color: `#7C3AED`

### Metric Card 4

- Title: `운행 중단률`
- Value: `4.8%`
- Icon: `CircleMinus`
- Icon Background: `#FEF2F2`
- Icon Color: `#EF4444`

---

## 13. Analysis Chart Section

### Section Container

- Width: `1312px`
- Height: `320px`

Layout:

- Display: `grid`
- Grid columns: `1fr 1fr`
- Gap: `16px`

Card width calculation:

```text
(1312 - 16) / 2 = 648px
```

Card size:

- Width: `648px`
- Height: `320px`

---

## 14. Chart Card Common Style

- Background: `#FFFFFF`
- Border: `1px solid #E5E7EB`
- Border radius: `12px`
- Padding: `20px`
- Shadow: `0 2px 8px rgba(0,0,0,0.04)`

### Chart Header

- Height: `32px`

Layout:

- Display: `flex`
- Justify content: `space-between`
- Align items: `center`

#### Chart Title

- Font size: `16px`
- Font weight: `700`
- Color: `#111827`

#### Unit Label

- Font size: `12px`
- Font weight: `400`
- Color: `#6B7280`

### Chart Area

- Width: `608px`
- Height: `240px`
- Margin top: `12px`

---

## 15. Hourly Average Delay Chart

### Title

`시간대별 평균 지연 시간`

### Chart Type

`Line Chart`

### Main Line

- Color: `#2563EB`
- Stroke width: `2px`

### Main Data Point

- Size: `6 × 6px`
- Color: `#2563EB`

### Comparison Line

- Color: `#94A3B8`
- Stroke width: `2px`
- Style: `dashed`

### Grid Line

- Color: `#E5E7EB`
- Stroke width: `1px`

### Axis Text

- Font size: `11px`
- Color: `#64748B`

### Tooltip

- Background: `#2563EB`
- Border radius: `6px`
- Padding: `6px 10px`

Tooltip text:

- Font size: `12px`
- Font weight: `600`
- Color: `#FFFFFF`

---

## 16. Alert vs Normal Delay Comparison Chart

### Title

`특보 발생 시 / 평상시 평균 지연 비교`

### Chart Type

`Grouped Bar Chart`

### Categories

1. 호우
2. 대설
3. 강풍

### Normal Average Bar

- Color: `#2563EB`

### Weather Alert Average Bar

- Color: `#EF4444`

### Bar Width

- `48px`

### Bar Gap

- `12px`

### Category Gap

- `64px`

### Legend

Normal:

- Color: `#2563EB`
- Text: `평상시 평균`

Weather Alert:

- Color: `#EF4444`
- Text: `특보 발생 시 평균`

Legend text:

- Font size: `11px`
- Font weight: `400`
- Color: `#475569`

---

## 17. Analysis Detail Section

### Container

- Width: `1312px`
- Height: `320px`

Layout:

- Display: `grid`
- Grid columns: `1fr 1fr`
- Gap: `16px`

Card size:

- Width: `648px`
- Height: `320px`

---

## 18. Weather Alert Statistics Card

### Card Container

- Width: `648px`
- Height: `320px`
- Background: `#FFFFFF`
- Border: `1px solid #E5E7EB`
- Border radius: `12px`
- Padding: `20px`
- Shadow: `0 2px 8px rgba(0,0,0,0.04)`

### Header

Title:

- Text: `특보별 영향 통계`
- Font size: `16px`
- Font weight: `700`
- Color: `#111827`

Subtitle:

- Text: `최근 3개월`
- Font size: `12px`
- Font weight: `400`
- Color: `#6B7280`

### Table Header

- Height: `40px`
- Background: `#F8FAFC`

Columns:

1. 특보 종류
2. 발생 횟수
3. 평균 지연(분)
4. 지연률
5. 운행 중단률

Header text:

- Font size: `12px`
- Font weight: `600`
- Color: `#475569`

### Table Row

- Height: `44px`
- Border bottom: `1px solid #F1F5F9`

Text:

- Font size: `12px`
- Font weight: `400`
- Color: `#374151`

---

## 19. Weather Alert Icons

### Heavy Rain Warning

- Icon: `CloudRain`
- Color: `#EF4444`

### Heavy Rain Advisory

- Icon: `CloudRain`
- Color: `#F59E0B`

### Strong Wind Advisory

- Icon: `Wind`
- Color: `#22C55E`

### Heavy Snow Advisory

- Icon: `Snowflake`
- Color: `#2563EB`

### Heat Wave Advisory

- Icon: `Sun`
- Color: `#F59E0B`

Icon size:

- `18 × 18px`

---

## 20. Historical Major Cases Card

### Card Container

- Width: `648px`
- Height: `320px`
- Background: `#FFFFFF`
- Border: `1px solid #E5E7EB`
- Border radius: `12px`
- Padding: `20px`
- Shadow: `0 2px 8px rgba(0,0,0,0.04)`

### Header

Title:

- Text: `과거 주요 사례`
- Font size: `16px`
- Font weight: `700`
- Color: `#111827`

Subtitle:

- Text: `최근 3건`
- Font size: `12px`
- Font weight: `400`
- Color: `#6B7280`

---

## 21. Historical Case Item

### Item Container

- Width: `608px`
- Height: `76px`
- Border: `1px solid #E5E7EB`
- Border radius: `8px`
- Padding: `8px`
- Margin bottom: `8px`

Layout:

- Display: `flex`
- Align items: `center`

### Weather Alert Label

- Width: `104px`
- Height: `60px`
- Border radius: `8px`

High Risk Label:

- Background: `#FFF7F7`
- Text color: `#EF4444`

Warning Label:

- Background: `#FFF7ED`
- Text color: `#F59E0B`

Interest Label:

- Background: `#F0FDF4`
- Text color: `#16A34A`

Weather Alert Label Text:

- Font size: `13px`
- Font weight: `600`

### Case Information

- Flex: `1`
- Padding left/right: `16px`

Date + Alert:

- Font size: `13px`
- Font weight: `600`
- Color: `#111827`

Weather Information:

- Font size: `12px`
- Font weight: `400`
- Color: `#64748B`

Railway Impact Information:

- Font size: `12px`
- Font weight: `400`
- Color: `#64748B`

### Detail Button

- Size: `72 × 32px`
- Background: `#FFFFFF`
- Border: `1px solid #D1D5DB`
- Border radius: `6px`

Text:

- Text: `상세보기`
- Font size: `12px`
- Font weight: `500`
- Color: `#374151`

---

## 22. Metric Description

### Container

- Width: `1312px`
- Height: `32px`

Layout:

- Display: `flex`
- Align items: `center`
- Gap: `8px`

### Icon

- Icon: `CircleInfo`
- Size: `16 × 16px`
- Color: `#64748B`

### Text

- Example: `지표 설명: 평균 지연 증가량은 평상시 평균 지연 시간 대비 특보 발생 시 평균 지연 시간의 증가 수치입니다.`
- Font size: `12px`
- Font weight: `400`
- Color: `#64748B`

---

## 23. Icon System

Use Lucide Icons through `lucide-react`.

### Required Icons

- `Menu`
- `Bell`
- `ChevronDown`
- `ChevronRight`
- `ArrowLeft`
- `TrainFront`
- `TriangleAlert`
- `Clock3`
- `TrendingUp`
- `Percent`
- `CircleMinus`
- `CloudRain`
- `Wind`
- `Snowflake`
- `Sun`
- `CircleInfo`

### Icon Rules

- Do not mix multiple icon libraries.
- Use `lucide-react`.
- Default stroke width: `2px`.
- Small UI icon: `14~18px`.
- Metric card icon: `24px`.
- Station icon: `28px`.
- Risk icon: `28px`.

---

## 24. Page Spacing Rules

Use the following spacing system consistently.

| Usage | Size |
|---|---:|
| Very Small Gap | `4px` |
| Small Gap | `8px` |
| Component Gap | `16px` |
| Card Internal Padding | `20px` |
| Large Section Gap | `24px` |
| Main Dashboard Horizontal Margin | `64px` |

Do not randomly use spacing values outside this system unless necessary for precise alignment.

---

## 25. Removed Components

The following components must NOT be implemented.

### Timeline

Do not add the previous weather alert timeline section.

Reason:

- Information overlaps with Historical Major Cases.
- The Station Detail Page should focus on weather impact and railway operation risk analysis.

### Operation Count Metric

Do not add the previous `운행 횟수` metric card.

Use `평균 지연 증가량` instead.

### Recent 7-Day Delay Chart

Do not add the previous `최근 7일 지연 추이` chart.

Use `특보 발생 시 / 평상시 평균 지연 비교` instead.

---

## 26. Responsive and Implementation Rules

- Desktop-first design.
- Target viewport width: `1440px` or wider.
- Maintain the main content width close to `1312px`.
- Use reusable React components.
- Use CSS variables or design tokens.
- Do not hardcode repeated colors throughout individual components.
- Use the same Card, Button, Badge, and Typography styles as the Main Dashboard.
- Charts should be implemented as reusable chart components.
- Do not add unnecessary UI components.
- Do not add a geographical map to the Station Detail Page.
- Maintain visual consistency with the Main Dashboard.

---

## 27. Recommended React Component Structure

```text
StationDetailPage

├── GlobalHeader
├── Breadcrumb
├── PageTitleSection
├── StationInfoCard
│   ├── StationIdentity
│   ├── ChangeStationButton
│   └── CurrentRiskStatus
├── MetricCardGrid
│   ├── AverageDelayCard
│   ├── DelayIncreaseCard
│   ├── DelayRateCard
│   └── SuspensionRateCard
├── AnalysisChartGrid
│   ├── HourlyDelayChart
│   └── AlertNormalComparisonChart
├── AnalysisDetailGrid
│   ├── WeatherAlertStatisticsTable
│   └── HistoricalCasesCard
└── MetricDescription
```

---

## 28. Recommended Reusable Components

### Layout Components

- `GlobalHeader`
- `Breadcrumb`
- `PageTitleSection`

### Card Components

- `BaseCard`
- `MetricCard`
- `ChartCard`

### Station Components

- `StationInfoCard`
- `CurrentRiskStatus`

### Analysis Components

- `HourlyDelayChart`
- `AlertNormalComparisonChart`
- `WeatherAlertStatisticsTable`
- `HistoricalCasesCard`
- `HistoricalCaseItem`

### Common UI Components

- `Button`
- `Badge`
- `IconButton`
- `RiskBadge`

---

## 29. Codex Implementation Priority

When implementing this page, follow this priority order.

1. Follow the dimensions, spacing, colors, and typography defined in this document.
2. Use the attached Station Detail Page design image as a visual reference.
3. Reuse the existing Main Dashboard components and design tokens whenever possible.
4. Do not create duplicate components when an equivalent Main Dashboard component already exists.
5. Use `lucide-react` for all icons.
6. Keep chart components reusable.
7. Maintain consistent spacing and alignment.
8. Do not add UI sections that are not defined in this document.

---

## 30. Final Implementation Instruction

Implement the Station Detail Page based on this specification.

Use the attached Station Detail Page design image as a visual reference for layout and overall appearance.

However, when the image and this document contain conflicting dimensions, colors, typography, spacing, or component specifications, prioritize the values defined in this document.

Reuse the existing Main Dashboard design system and reusable components whenever possible.

The final implementation should visually match the Main Dashboard and feel like part of the same Korean railway weather risk decision support system.

Do not modify the existing Main Dashboard design unnecessarily while implementing the Station Detail Page.
