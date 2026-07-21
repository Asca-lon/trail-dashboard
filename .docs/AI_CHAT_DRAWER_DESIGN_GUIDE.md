# AI_CHAT_DRAWER_DESIGN_GUIDE

## 1. Scope

- 적용 화면: Main Dashboard, Station Detail, Route Detail
- 표시 방식: 별도 페이지 이동 없이 오른쪽 Drawer
- 백엔드 API, RAG 출처, 대화 저장, 스트리밍 응답은 현재 단계에서 구현하지 않는다.
- Mock 데이터로 UI 상태만 구현한다.

---

## 2. AI Trigger Button

| Element | Value |
|---|---|
| Position | Global Header 우측, 알림 아이콘 왼쪽 |
| Size | `40 × 40px` |
| Background | `#EEF2FF` |
| Border | `1px solid #C7D2FE` |
| Border Radius | `50%` |
| Icon | `Bot` |
| Icon Size | `20px` |
| Icon Color | `#6366F1` |
| Hover Background | `#E0E7FF` |
| Active Background | `#6366F1` |
| Active Icon Color | `#FFFFFF` |

---

## 3. Chat Drawer

| Element | Value |
|---|---|
| Width | `400px` |
| Height | `calc(100vh - 24px)` |
| Position | `fixed` |
| Top | `12px` |
| Right | `12px` |
| Z-index | `1000` |
| Background | `#FFFFFF` |
| Border | `1px solid #E5E7EB` |
| Border Radius | `16px` |
| Shadow | `0 12px 40px rgba(15, 23, 42, 0.16)` |
| Overflow | `hidden` |

- Overlay는 사용하지 않는다.

---

## 4. Drawer Structure

```text
AIChatDrawer

├── ChatHeader
├── ContextBanner
├── MessageArea
│   ├── EmptyState
│   ├── MessageBubbleList
│   ├── LoadingState
│   ├── ErrorState
│   └── NoDataState
├── SuggestedQuestions
└── ChatComposer
```

---

## 5. Chat Header

| Element | Value |
|---|---|
| Size | `400 × 64px` |
| Padding | `16px 20px` |
| Background | `#FFFFFF` |
| Border Bottom | `1px solid #E5E7EB` |
| Title | `AI 어시스턴트` |
| Title Font | `16px / 700 / #111827` |
| Subtitle | `현재 화면의 데이터를 기반으로 답변합니다.` |
| Subtitle Font | `12px / 400 / #6B7280` |

### Beta Badge

| Element | Value |
|---|---|
| Height | `22px` |
| Padding | `0 8px` |
| Background | `#EEF2FF` |
| Border Radius | `999px` |
| Text | `BETA` |
| Font | `10px / 700 / #6366F1` |

### Header Buttons

| Button | Icon | Size | Icon Size | Color |
|---|---|---:|---:|---|
| Minimize | `Minus` | `32 × 32px` | `16px` | `#64748B` |
| Close | `X` | `32 × 32px` | `16px` | `#64748B` |

Hover Background: `#F3F4F6`

---

## 6. Context Banner

| Element | Value |
|---|---|
| Margin | `12px 16px 0` |
| Padding | `12px` |
| Background | `#F8FAFC` |
| Border | `1px solid #E5E7EB` |
| Border Radius | `10px` |
| Label Font | `11px / 500 / #6B7280` |
| Title Font | `13px / 600 / #111827` |

페이지별 예시:

- Dashboard: `메인 대시보드`
- Station Detail: `대전역 상세`
- Route Detail: `대전 → 김천(구미) 구간`

---

## 7. Message Area

| Element | Value |
|---|---|
| Height | `fill` |
| Padding | `16px` |
| Background | `#FFFFFF` |
| Overflow Y | `auto` |
| Message Gap | `12px` |

---

## 8. Empty State

| Element | Value |
|---|---|
| Alignment | `center` |
| Padding Top | `24px` |
| Icon Container | `48 × 48px` |
| Icon Container Background | `#EEF2FF` |
| Icon Container Radius | `50%` |
| Icon | `Sparkles` |
| Icon Size | `24px` |
| Icon Color | `#6366F1` |
| Title | `현재 화면에 대해 질문해보세요` |
| Title Font | `15px / 700 / #111827` |
| Description | `화면에 표시된 수치와 분석 결과를 기준으로 답변합니다.` |
| Description Font | `12px / 400 / #6B7280` |
| Description Max Width | `280px` |

---

## 9. Message Bubble

### User Message

| Element | Value |
|---|---|
| Max Width | `82%` |
| Alignment | `right` |
| Background | `#4F46E5` |
| Border Radius | `14px 14px 4px 14px` |
| Padding | `10px 12px` |
| Text | `13px / 400 / #FFFFFF` |

### AI Message

| Element | Value |
|---|---|
| Max Width | `88%` |
| Alignment | `left` |
| Background | `#F3F4F6` |
| Border | `1px solid #E5E7EB` |
| Border Radius | `14px 14px 14px 4px` |
| Padding | `12px` |
| Text | `13px / 400 / #374151` |
| Line Height | `20px` |

### Message Time

| Element | Value |
|---|---|
| Font | `10px / 400` |
| Color | `#9CA3AF` |
| Margin Top | `4px` |

---

## 10. Suggested Questions

| Element | Value |
|---|---|
| Padding | `0 16px 12px` |
| Layout | `flex / wrap` |
| Gap | `8px` |

### Question Chip

| Element | Value |
|---|---|
| Min Height | `32px` |
| Padding | `6px 10px` |
| Background | `#FFFFFF` |
| Border | `1px solid #C7D2FE` |
| Border Radius | `8px` |
| Font | `12px / 500` |
| Text Color | `#4F46E5` |
| Hover Background | `#EEF2FF` |

### Dashboard Questions

- `현재 위험도가 가장 높은 구간은?`
- `우선 점검 대상을 요약해줘`
- `현재 필터 조건을 설명해줘`

### Station Detail Questions

- `이 역의 지연률이 높은 이유는?`
- `가장 영향이 큰 특보는?`
- `평상시와 특보 발생 시 차이는?`

### Route Detail Questions

- `이 구간이 위험한 이유는?`
- `현재 상태와 과거 사례를 비교해줘`
- `우선 확인할 항목은?`

---

## 11. Chat Composer

| Element | Value |
|---|---|
| Min Height | `96px` |
| Padding | `12px 16px 16px` |
| Background | `#FFFFFF` |
| Border Top | `1px solid #E5E7EB` |

### Input Container

| Element | Value |
|---|---|
| Min Height | `48px` |
| Max Height | `120px` |
| Padding | `10px 44px 10px 12px` |
| Background | `#FFFFFF` |
| Border | `1px solid #D1D5DB` |
| Border Radius | `10px` |
| Focus Border | `#6366F1` |
| Focus Shadow | `0 0 0 3px rgba(99, 102, 241, 0.12)` |

### Textarea

| Element | Value |
|---|---|
| Placeholder | `궁금한 내용을 질문하세요...` |
| Font | `13px / 400` |
| Text Color | `#111827` |
| Placeholder Color | `#9CA3AF` |
| Resize | `none` |

### Send Button

| Element | Value |
|---|---|
| Size | `36 × 36px` |
| Position | `absolute / right 6px / bottom 6px` |
| Background | `#6366F1` |
| Disabled Background | `#E0E7FF` |
| Border Radius | `8px` |
| Icon | `SendHorizontal` |
| Icon Size | `18px` |
| Icon Color | `#FFFFFF` |

### Character Count

| Element | Value |
|---|---|
| Text | `0 / 500` |
| Font | `10px / 400` |
| Color | `#9CA3AF` |
| Margin Top | `6px` |

### AI Notice

| Element | Value |
|---|---|
| Text | `AI 답변은 참고용으로 활용해 주세요.` |
| Font | `10px / 400` |
| Color | `#9CA3AF` |
| Alignment | `center` |

---

## 12. Loading State

| Element | Value |
|---|---|
| Dot Size | `6 × 6px` |
| Dot Color | `#9CA3AF` |
| Dot Gap | `4px` |
| Animation | `pulse` |
| Text | `답변을 생성하고 있습니다.` |
| Text Font | `12px / 400 / #6B7280` |

---

## 13. Error State

| Element | Value |
|---|---|
| Background | `#FFF7F7` |
| Border | `1px solid #FECACA` |
| Border Radius | `10px` |
| Padding | `12px` |
| Icon | `CircleAlert / 18px / #EF4444` |
| Title | `답변을 불러오지 못했습니다.` |
| Title Font | `13px / 600 / #B91C1C` |
| Description Font | `12px / 400 / #6B7280` |

### Retry Button

| Element | Value |
|---|---|
| Height | `32px` |
| Padding | `0 12px` |
| Background | `#FFFFFF` |
| Border | `1px solid #FCA5A5` |
| Border Radius | `6px` |
| Text | `다시 시도` |
| Font | `12px / 600 / #DC2626` |

---

## 14. No Data State

| Element | Value |
|---|---|
| Background | `#F8FAFC` |
| Border | `1px solid #E5E7EB` |
| Border Radius | `10px` |
| Padding | `16px` |
| Icon | `DatabaseX / 20px / #94A3B8` |
| Title | `현재 화면에 분석 가능한 데이터가 없습니다.` |
| Title Font | `13px / 600 / #374151` |
| Description Font | `12px / 400 / #6B7280` |

---

## 15. Motion

| State | Value |
|---|---|
| Open | `right → left / 220ms / ease-out` |
| Close | `left → right / 180ms / ease-in` |

---

## 16. Responsive

| Breakpoint | Drawer |
|---|---|
| Desktop | `400px`, top/right `12px` |
| Tablet | `360px`, top/right `8px` |
| Mobile | `inset: 0`, width/height `100%`, radius `0` |

---

## 17. Required Icons

Use `lucide-react`.

- `Bot`
- `Sparkles`
- `Minus`
- `X`
- `SendHorizontal`
- `CircleAlert`
- `DatabaseX`

---

## 18. Components

```text
AIChat

├── AIChatTrigger
├── AIChatDrawer
│   ├── AIChatHeader
│   ├── AIContextBanner
│   ├── AIMessageList
│   │   ├── AIEmptyState
│   │   ├── AIMessageBubble
│   │   ├── AILoadingState
│   │   ├── AIErrorState
│   │   └── AINoDataState
│   ├── AISuggestedQuestions
│   └── AIChatComposer
```

---

## 19. Mock UI States

1. Drawer Closed
2. Drawer Open / Empty
3. User Message + AI Message
4. Answer Loading
5. Error
6. No Data
7. Suggested Question Clicked
