const SEGMENT_DETAIL_MOCK_URL = "../mock/segments_details.json";
const VULNERABILITY_SEGMENTS_MOCK_URL = "../mock/vulnerability_segments.json";
const SEGMENT_ID_QUERY_PARAM = "segment_id";

const HIGH_EXPECTED_DELAY_THRESHOLD = 15;
const WARNING_EXPECTED_DELAY_THRESHOLD = 5;
const HIGH_STOP_RATE_THRESHOLD = 0.05;
const WARNING_STOP_RATE_THRESHOLD = 0.02;
const LINE_CHART_MAX_VALUE = 40;
const LINE_CHART_MIN_X = 38;
const LINE_CHART_MAX_X = 438;
const LINE_CHART_MIN_Y = 24;
const LINE_CHART_MAX_Y = 192;
const BAR_CHART_MAX_VALUE = 20;
const BAR_CHART_MAX_HEIGHT = 150;
const BAR_CHART_MIN_HEIGHT = 8;
const HORIZONTAL_DELAY_MAX_VALUE = 20;
const HORIZONTAL_STOP_RATE_MAX_VALUE = 10;
const MINI_CHART_MAX_HEIGHT = 118;
const MINI_CHART_MIN_HEIGHT = 10;

const RISK_LABELS = {
  high: "높음",
  warning: "주의",
  interest: "관심",
  none: "정보 없음",
};

const routeTabs = Array.from(document.querySelectorAll("[data-route-tab]"));
const routePanels = Array.from(document.querySelectorAll("[data-route-panel]"));
const routeRiskCriteriaToggles = Array.from(document.querySelectorAll("[data-route-risk-criteria-toggle]"));

const routeSummaryElements = {
  breadcrumb: document.querySelector("[data-route-detail-breadcrumb]"),
  title: document.querySelector("[data-route-detail-title]"),
  description: document.querySelector("[data-route-detail-description]"),
  fromStation: document.querySelector("[data-route-detail-from-station]"),
  toStation: document.querySelector("[data-route-detail-to-station]"),
  line: document.querySelector("[data-route-detail-line]"),
  referenceTime: document.querySelector("[data-route-detail-reference-time]"),
  riskCard: document.querySelector("[data-route-detail-risk-card]"),
  riskBadge: document.querySelector("[data-route-detail-risk-badge]"),
  alert: document.querySelector("[data-route-detail-alert]"),
  riskTime: document.querySelector("[data-route-detail-risk-time]"),
};

const routeMetricElements = {
  avgDelay: document.querySelector('[data-route-detail-metric="avg-delay"]'),
  delayIncrease: document.querySelector('[data-route-detail-metric="delay-increase"]'),
  stopRate: document.querySelector('[data-route-detail-metric="stop-rate"]'),
  sampleCount: document.querySelector('[data-route-detail-metric="sample-count"]'),
};

const routeTableElements = {
  impactSummaryBody: document.querySelector("[data-route-detail-impact-summary-body]"),
  alertAnalysisBody: document.querySelector("[data-route-detail-alert-analysis-body]"),
  historyBody: document.querySelector("[data-route-detail-history-body]"),
};

const routeChartElements = {
  lineChart: document.querySelector("[data-route-detail-line-chart]"),
  lineActual: document.querySelector("[data-route-detail-line-actual]"),
  lineForecast: document.querySelector("[data-route-detail-line-forecast]"),
  linePoint: document.querySelector("[data-route-detail-line-point]"),
  lineTooltipBox: document.querySelector("[data-route-detail-line-tooltip-box]"),
  lineTooltip: document.querySelector("[data-route-detail-line-tooltip]"),
  barChart: document.querySelector("[data-route-detail-bar-chart]"),
  alertDelayChart: document.querySelector("[data-route-detail-alert-delay-chart]"),
  alertStopChart: document.querySelector("[data-route-detail-alert-stop-chart]"),
  historyCharts: {
    delay: document.querySelector('[data-route-detail-history-chart="delay"]'),
    increase: document.querySelector('[data-route-detail-history-chart="increase"]'),
    stop: document.querySelector('[data-route-detail-history-chart="stop"]'),
    rain: document.querySelector('[data-route-detail-history-chart="rain"]'),
  },
};

const routeHistoryFilterElements = {
  form: document.querySelector("[data-route-history-filter-form]"),
  alertTypeSelect: document.querySelector("[data-route-history-alert-type-select]"),
  alertLevelSelect: document.querySelector("[data-route-history-alert-level-select]"),
  periodSelect: document.querySelector("[data-route-history-period-select]"),
};

let routeHistoryState = null;
let isRouteHistoryFilterInitialized = false;

function setRouteTab(targetTab) {
  routeTabs.forEach((tab) => {
    const isActive = tab.dataset.routeTab === targetTab;

    tab.classList.toggle("route-tabs__button--active", isActive);
    tab.setAttribute("aria-selected", String(isActive));
  });

  routePanels.forEach((panel) => {
    panel.hidden = panel.dataset.routePanel !== targetTab;
  });
}

function formatStationName(stationName) {
  if (!stationName) {
    return "역 정보 없음";
  }

  return stationName.endsWith("역") ? stationName : `${stationName}역`;
}

function formatSegmentLabel(fromStation, toStation) {
  if (!fromStation || !toStation) {
    return "구간 상세";
  }

  return `${fromStation}→${toStation} 구간`;
}

function formatPercent(rate) {
  if (!Number.isFinite(rate)) {
    return "-";
  }

  return (rate * 100).toFixed(1);
}

function formatRatePercent(rate) {
  if (!Number.isFinite(rate)) {
    return "-";
  }

  return `${formatPercent(rate)}%`;
}

function formatSignedNumber(value) {
  if (!Number.isFinite(value)) {
    return "-";
  }

  return `+${value.toFixed(1)}`;
}

function formatChartDateLabel(dateString) {
  const date = new Date(dateString);

  if (Number.isNaN(date.getTime())) {
    return "-";
  }

  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");

  return `${month}/${day}`;
}

function formatCaseDate(dateString) {
  const date = new Date(dateString);

  if (Number.isNaN(date.getTime())) {
    return "날짜 정보 없음";
  }

  const formatter = new Intl.DateTimeFormat("ko-KR", {
    timeZone: "Asia/Seoul",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  });
  const parts = Object.fromEntries(
    formatter.formatToParts(date).map((part) => [part.type, part.value]),
  );

  return `${parts.year}.${parts.month}.${parts.day}`;
}

function formatCompactCaseDate(dateString) {
  const date = new Date(dateString);

  if (Number.isNaN(date.getTime())) {
    return "날짜 없음";
  }

  const formatter = new Intl.DateTimeFormat("ko-KR", {
    timeZone: "Asia/Seoul",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  });
  const parts = Object.fromEntries(
    formatter.formatToParts(date).map((part) => [part.type, part.value]),
  );

  return `${parts.year}.${parts.month}.${parts.day}`;
}

function getRiskLevel(expectedDelay, stopRate) {
  const hasExpectedDelay = Number.isFinite(expectedDelay);
  const hasStopRate = Number.isFinite(stopRate);

  if (!hasExpectedDelay && !hasStopRate) {
    return "none";
  }

  if (
    (hasExpectedDelay && expectedDelay >= HIGH_EXPECTED_DELAY_THRESHOLD)
    || (hasStopRate && stopRate >= HIGH_STOP_RATE_THRESHOLD)
  ) {
    return "high";
  }

  if (
    (hasExpectedDelay && expectedDelay >= WARNING_EXPECTED_DELAY_THRESHOLD)
    || (hasStopRate && stopRate >= WARNING_STOP_RATE_THRESHOLD)
  ) {
    return "warning";
  }

  return "interest";
}

function getStatusBadgeClass(alertLevel) {
  if (alertLevel === "경보") {
    return "route-status-badge--high";
  }

  if (alertLevel === "주의보") {
    return "route-status-badge--warning";
  }

  return "route-status-badge--info";
}

function getAlertIconPath(alertType) {
  if (alertType === "폭염") {
    return "./assets/icons/sun.svg";
  }

  if (alertType === "강풍") {
    return "./assets/icons/trending-up.svg";
  }

  if (alertType === "대설") {
    return "./assets/icons/snowflake.svg";
  }

  return "./assets/icons/cloud-rain.svg";
}

function getAlertChartColor(alertStat) {
  if (alertStat.alert_level === "경보") {
    return "var(--color-danger-red)";
  }

  if (alertStat.alert_type === "호우") {
    return "#F59E0B";
  }

  if (alertStat.alert_type === "대설") {
    return "#2563EB";
  }

  if (alertStat.alert_type === "강풍") {
    return "#22C55E";
  }

  if (alertStat.alert_type === "폭염") {
    return "#F97316";
  }

  return "#94A3B8";
}

function getSegments(vulnerabilitySegmentsData) {
  return Array.isArray(vulnerabilitySegmentsData.segments)
    ? vulnerabilitySegmentsData.segments
    : [];
}

function getSegmentById(segmentId, vulnerabilitySegmentsData) {
  return getSegments(vulnerabilitySegmentsData).find((segment) => segment.segment_id === segmentId) || null;
}

function getSegmentByEndpoints(segmentDetailData, vulnerabilitySegmentsData) {
  return getSegments(vulnerabilitySegmentsData).find(
    (segment) => segment.from === segmentDetailData.from && segment.to === segmentDetailData.to,
  ) || null;
}

function getSegmentDetails(segmentDetailsData) {
  if (Array.isArray(segmentDetailsData.segments)) {
    return segmentDetailsData.segments;
  }

  return segmentDetailsData.segment_id || segmentDetailsData.from || segmentDetailsData.to
    ? [segmentDetailsData]
    : [];
}

function getSegmentDetailById(segmentId, segmentDetailsData) {
  return getSegmentDetails(segmentDetailsData).find((segmentDetail) => segmentDetail.segment_id === segmentId) || null;
}

function getSegmentDetailByEndpoints(selectedSegment, segmentDetailsData) {
  if (!selectedSegment) {
    return null;
  }

  return getSegmentDetails(segmentDetailsData).find(
    (segmentDetail) => segmentDetail.from === selectedSegment.from && segmentDetail.to === selectedSegment.to,
  ) || null;
}

function getFirstSegmentDetail(segmentDetailsData) {
  return getSegmentDetails(segmentDetailsData)[0] || null;
}

function getInitialSegmentId() {
  const params = new URLSearchParams(window.location.search);

  return params.get(SEGMENT_ID_QUERY_PARAM);
}

function getInitialSegment(vulnerabilitySegmentsData, segmentDetailsData) {
  const segmentIdFromUrl = getInitialSegmentId();
  const firstSegmentDetail = getFirstSegmentDetail(segmentDetailsData);

  return getSegmentById(segmentIdFromUrl, vulnerabilitySegmentsData)
    || getSegmentByEndpoints(firstSegmentDetail || {}, vulnerabilitySegmentsData)
    || getSegments(vulnerabilitySegmentsData)[0]
    || null;
}

function getSelectedSegmentDetail(selectedSegment, segmentDetailsData) {
  const segmentIdFromUrl = getInitialSegmentId();

  return getSegmentDetailById(segmentIdFromUrl, segmentDetailsData)
    || getSegmentDetailById(selectedSegment?.segment_id, segmentDetailsData)
    || getSegmentDetailByEndpoints(selectedSegment, segmentDetailsData)
    || getFirstSegmentDetail(segmentDetailsData)
    || {};
}

function setMetricCard(card, value, unit, comparisonLabel, comparisonValue, ariaLabel) {
  if (!card) {
    return;
  }

  const valueElement = card.querySelector("[data-route-detail-metric-value]");
  const unitElement = card.querySelector("[data-route-detail-metric-unit]");
  const comparisonElement = card.querySelector("[data-route-detail-metric-comparison]");

  if (valueElement) {
    valueElement.textContent = value;
  }

  if (unitElement) {
    unitElement.textContent = unit;
  }

  if (comparisonElement) {
    comparisonElement.replaceChildren();
    comparisonElement.append(document.createTextNode(`${comparisonLabel} `));

    if (comparisonValue) {
      const strong = document.createElement("b");

      strong.textContent = comparisonValue;
      comparisonElement.append(strong);
    }
  }

  card.setAttribute("aria-label", ariaLabel);
}

function createTableCell(text) {
  const cell = document.createElement("td");

  cell.textContent = text;

  return cell;
}

function getLineChartPoint(item, index, itemCount) {
  const safeCount = Math.max(itemCount - 1, 1);
  const value = Number.isFinite(item.delay_min) ? item.delay_min : 0;
  const x = LINE_CHART_MIN_X + ((LINE_CHART_MAX_X - LINE_CHART_MIN_X) / safeCount) * index;
  const clampedValue = Math.max(0, Math.min(value, LINE_CHART_MAX_VALUE));
  const y = LINE_CHART_MAX_Y - (clampedValue / LINE_CHART_MAX_VALUE) * (LINE_CHART_MAX_Y - LINE_CHART_MIN_Y);

  return {
    x: Number(x.toFixed(1)),
    y: Number(y.toFixed(1)),
    value,
  };
}

function getLineChartPoints(chartData, type) {
  const items = chartData.filter((item) => item.type === type);

  return items.map((item) => {
    const sourceIndex = chartData.indexOf(item);

    return getLineChartPoint(item, sourceIndex, chartData.length);
  });
}

function toPolylinePoints(points) {
  return points.map((point) => `${point.x},${point.y}`).join(" ");
}

function createDelayTrendBar(trendItem, index, itemCount) {
  const bar = document.createElement("div");
  const value = document.createElement("span");
  const label = document.createElement("strong");
  const height = Math.max(
    BAR_CHART_MIN_HEIGHT,
    Math.min((trendItem.delay_increase / BAR_CHART_MAX_VALUE) * BAR_CHART_MAX_HEIGHT, BAR_CHART_MAX_HEIGHT),
  );
  const isToday = index === itemCount - 1;

  bar.className = `route-bar-chart__item${isToday ? " route-bar-chart__item--today" : ""}`;
  bar.style.height = `${height.toFixed(0)}px`;
  value.textContent = Number.isFinite(trendItem.delay_increase) ? trendItem.delay_increase.toFixed(1) : "-";
  label.textContent = formatChartDateLabel(trendItem.date);

  bar.append(value, label);

  return bar;
}

function createHorizontalChartRow(label, valueText, widthPercent, color) {
  const row = document.createElement("div");
  const labelElement = document.createElement("span");
  const bar = document.createElement("i");
  const value = document.createElement("strong");

  row.className = "route-horizontal-chart__row";
  labelElement.textContent = label;
  bar.style.width = `${Math.max(0, Math.min(widthPercent, 100)).toFixed(0)}%`;
  bar.style.background = color;
  value.textContent = valueText;

  row.append(labelElement, bar, value);

  return row;
}

function createHorizontalChartEmptyRow(message) {
  const row = document.createElement("div");

  row.className = "route-horizontal-chart__row";
  row.textContent = message;

  return row;
}

function createMiniBar(value, label, options = {}) {
  const bar = document.createElement("i");
  const valueElement = document.createElement("b");
  const labelElement = document.createElement("span");
  const maxValue = Number.isFinite(options.maxValue) && options.maxValue > 0 ? options.maxValue : 1;
  const height = Math.max(
    MINI_CHART_MIN_HEIGHT,
    Math.min((value / maxValue) * MINI_CHART_MAX_HEIGHT, MINI_CHART_MAX_HEIGHT),
  );

  bar.className = `route-mini-bar-chart__bar${options.isCurrent ? " route-mini-bar-chart__bar--forecast" : ""}`;
  bar.style.height = `${height.toFixed(0)}px`;
  valueElement.textContent = options.formatValue(value);
  labelElement.innerHTML = label;
  bar.append(valueElement, labelElement);

  return bar;
}

function createMessageRow(message, columnCount) {
  const row = document.createElement("tr");
  const cell = document.createElement("td");

  cell.colSpan = columnCount;
  cell.textContent = message;
  row.append(cell);

  return row;
}

function createAlertHeaderCell(alertStat) {
  const header = document.createElement("th");
  const icon = document.createElement("img");

  header.scope = "row";
  icon.src = getAlertIconPath(alertStat.alert_type);
  icon.alt = "";
  icon.setAttribute("aria-hidden", "true");

  header.append(icon, document.createTextNode(alertStat.alert_type || "특보"));

  return header;
}

function createAlertLevelCell(alertLevel) {
  const cell = document.createElement("td");
  const badge = document.createElement("span");

  badge.className = `route-status-badge ${getStatusBadgeClass(alertLevel)}`;
  badge.textContent = alertLevel || "-";
  cell.append(badge);

  return cell;
}

function createHistoryAlertCell(caseItem) {
  const cell = document.createElement("td");
  const wrapper = document.createElement("span");
  const icon = document.createElement("img");
  const badge = document.createElement("b");
  const alertType = caseItem.alert_type || "평상시";

  wrapper.className = "route-history-alert";
  icon.src = getAlertIconPath(caseItem.alert_type);
  icon.alt = "";
  icon.setAttribute("aria-hidden", "true");
  badge.className = `route-status-badge ${caseItem.alert_type ? "route-status-badge--warning" : "route-status-badge--safe"}`;
  badge.textContent = caseItem.alert_type ? `${alertType} 기록` : alertType;

  wrapper.append(icon, badge);
  cell.append(wrapper);

  return cell;
}

function getSimilarityStars(delayMinutes) {
  if (!Number.isFinite(delayMinutes)) {
    return "★★★☆☆";
  }

  if (delayMinutes >= 18) {
    return "★★★★★";
  }

  if (delayMinutes >= 10) {
    return "★★★★☆";
  }

  return "★★★☆☆";
}

function createSimilarityCell(delayMinutes) {
  const cell = document.createElement("td");
  const stars = document.createElement("span");
  const starText = getSimilarityStars(delayMinutes);

  stars.className = "route-history-stars";
  stars.textContent = starText;
  stars.setAttribute("aria-label", `유사도 ${starText}`);
  cell.append(stars);

  return cell;
}

function createHistoryRow(caseItem) {
  const row = document.createElement("tr");
  const delayText = Number.isFinite(caseItem.delay_min) ? caseItem.delay_min.toFixed(1) : "-";
  const increaseCell = createTableCell(Number.isFinite(caseItem.delay_increase) ? formatSignedNumber(caseItem.delay_increase) : "-");

  increaseCell.className = "route-history-table__increase";
  row.append(
    createTableCell(formatCaseDate(caseItem.date)),
    createHistoryAlertCell(caseItem),
    createTableCell(Number.isFinite(caseItem.rain_mm) ? caseItem.rain_mm.toFixed(1) : "-"),
    createTableCell(delayText),
    increaseCell,
    createTableCell(Number.isFinite(caseItem.stop_rate) ? formatPercent(caseItem.stop_rate) : "-"),
    createTableCell(Number.isFinite(caseItem.affected_trains) ? String(caseItem.affected_trains) : "-"),
    createSimilarityCell(caseItem.delay_min),
    createTableCell(""),
  );

  return row;
}

function createSummaryAlertRow(alertStat) {
  const row = document.createElement("tr");
  const avgDelay = Number.isFinite(alertStat.avg_delay) ? alertStat.avg_delay.toFixed(1) : "-";
  const delayIncrease = Number.isFinite(alertStat.delay_increase) ? formatSignedNumber(alertStat.delay_increase) : "-";
  const stopRate = Number.isFinite(alertStat.stop_rate) ? formatPercent(alertStat.stop_rate) : "-";
  const sampleCount = Number.isFinite(alertStat.sample_n) ? `${alertStat.sample_n} 회` : "-";

  row.append(
    createAlertHeaderCell(alertStat),
    createAlertLevelCell(alertStat.alert_level),
    createTableCell(avgDelay),
    createTableCell(delayIncrease),
    createTableCell(stopRate),
    createTableCell(sampleCount),
    createTableCell(""),
  );

  return row;
}

function createAlertAnalysisRow(alertStat) {
  const row = document.createElement("tr");
  const avgDelay = Number.isFinite(alertStat.avg_delay) ? alertStat.avg_delay.toFixed(1) : "-";
  const delayIncrease = Number.isFinite(alertStat.delay_increase) ? formatSignedNumber(alertStat.delay_increase) : "-";
  const stopRate = Number.isFinite(alertStat.stop_rate) ? formatPercent(alertStat.stop_rate) : "-";
  const sampleCount = Number.isFinite(alertStat.sample_n) ? `${alertStat.sample_n} 회` : "-";

  row.append(
    createAlertHeaderCell(alertStat),
    createAlertLevelCell(alertStat.alert_level),
    createTableCell(sampleCount),
    createTableCell(avgDelay),
    createTableCell(delayIncrease),
    createTableCell(stopRate),
    createTableCell("-"),
    createTableCell("-"),
  );

  return row;
}

function renderRouteAlertTables(segmentDetailData) {
  const alertStats = Array.isArray(segmentDetailData.by_alert) ? segmentDetailData.by_alert : [];

  if (routeTableElements.impactSummaryBody) {
    const summaryRows = alertStats.map(createSummaryAlertRow);

    routeTableElements.impactSummaryBody.replaceChildren(
      ...(summaryRows.length > 0 ? summaryRows : [createMessageRow("특보별 영향 요약 데이터가 없습니다.", 7)]),
    );
  }

  if (routeTableElements.alertAnalysisBody) {
    const analysisRows = alertStats.map(createAlertAnalysisRow);

    routeTableElements.alertAnalysisBody.replaceChildren(
      ...(analysisRows.length > 0 ? analysisRows : [createMessageRow("특보별 영향 비교 데이터가 없습니다.", 8)]),
    );
  }
}

function renderHorizontalChart(chartElement, rows, emptyMessage) {
  if (!chartElement) {
    return;
  }

  const axis = chartElement.querySelector(".route-horizontal-chart__axis");
  const chartRows = rows.length > 0 ? rows : [createHorizontalChartEmptyRow(emptyMessage)];

  chartElement.replaceChildren(...chartRows, ...(axis ? [axis] : []));
}

function renderRouteAlertCharts(segmentDetailData) {
  const alertStats = Array.isArray(segmentDetailData.by_alert) ? segmentDetailData.by_alert : [];
  const delayRows = alertStats.map((alertStat) => {
    const value = Number.isFinite(alertStat.avg_delay) ? alertStat.avg_delay : 0;
    const widthPercent = (value / HORIZONTAL_DELAY_MAX_VALUE) * 100;

    return createHorizontalChartRow(
      `${alertStat.alert_type || "특보"} (${alertStat.alert_level || "-"})`,
      Number.isFinite(alertStat.avg_delay) ? alertStat.avg_delay.toFixed(1) : "-",
      widthPercent,
      getAlertChartColor(alertStat),
    );
  });
  const stopRows = alertStats.map((alertStat) => {
    const value = Number.isFinite(alertStat.stop_rate) ? Number(formatPercent(alertStat.stop_rate)) : 0;
    const widthPercent = (value / HORIZONTAL_STOP_RATE_MAX_VALUE) * 100;

    return createHorizontalChartRow(
      `${alertStat.alert_type || "특보"} (${alertStat.alert_level || "-"})`,
      formatRatePercent(alertStat.stop_rate),
      widthPercent,
      getAlertChartColor(alertStat),
    );
  });

  renderHorizontalChart(routeChartElements.alertDelayChart, delayRows, "특보별 평균 지연 데이터가 없습니다.");
  renderHorizontalChart(routeChartElements.alertStopChart, stopRows, "특보별 운행 중단률 데이터가 없습니다.");
}

function renderRouteHistoryTable(segmentDetailData) {
  if (!routeTableElements.historyBody) {
    return;
  }

  const cases = Array.isArray(segmentDetailData.cases) ? segmentDetailData.cases : [];
  const rows = cases.map(createHistoryRow);

  routeTableElements.historyBody.replaceChildren(
    ...(rows.length > 0 ? rows : [createMessageRow("과거 유사 사례 데이터가 없습니다.", 9)]),
  );
}

function getTopHistoryCases(segmentDetailData) {
  const cases = Array.isArray(segmentDetailData.cases) ? segmentDetailData.cases : [];

  return cases.slice(0, 3);
}

function renderMiniChart(chartElement, items, currentItem, valueKey, valueFormatter, emptyMessage) {
  if (!chartElement) {
    return;
  }

  const values = [
    ...items.map((item) => item[valueKey]).filter(Number.isFinite),
    currentItem[valueKey],
  ].filter(Number.isFinite);
  const maxValue = Math.max(...values, 1);
  const bars = items.map((item) => createMiniBar(
    Number.isFinite(item[valueKey]) ? item[valueKey] : 0,
    formatCompactCaseDate(item.date),
    {
      maxValue,
      formatValue: valueFormatter,
    },
  ));
  const currentBar = createMiniBar(
    Number.isFinite(currentItem[valueKey]) ? currentItem[valueKey] : 0,
    currentItem.label,
    {
      maxValue,
      formatValue: valueFormatter,
      isCurrent: true,
    },
  );

  chartElement.replaceChildren(
    ...(bars.length > 0 ? [...bars, currentBar] : [createHorizontalChartEmptyRow(emptyMessage)]),
  );
}

function renderRouteHistoryCharts(segmentDetailData, selectedSegment) {
  const topCases = getTopHistoryCases(segmentDetailData);
  const currentItem = {
    delay_min: selectedSegment?.avg_delay_incr,
    delay_increase: selectedSegment?.avg_delay_incr,
    stop_rate: selectedSegment?.stop_rate,
    rain_mm: segmentDetailData.current_rain_mm,
    label: "현재 예측",
  };

  renderMiniChart(
    routeChartElements.historyCharts.delay,
    topCases,
    currentItem,
    "delay_min",
    (value) => Number.isFinite(value) ? value.toFixed(1) : "-",
    "평균 지연 시간 비교 데이터가 없습니다.",
  );
  renderMiniChart(
    routeChartElements.historyCharts.increase,
    topCases,
    currentItem,
    "delay_increase",
    (value) => Number.isFinite(value) ? formatSignedNumber(value) : "-",
    "지연 증가량 비교 데이터가 없습니다.",
  );
  renderMiniChart(
    routeChartElements.historyCharts.stop,
    topCases,
    currentItem,
    "stop_rate",
    (value) => Number.isFinite(value) ? formatPercent(value) : "-",
    "운행 중단률 비교 데이터가 없습니다.",
  );
  renderMiniChart(
    routeChartElements.historyCharts.rain,
    topCases,
    currentItem,
    "rain_mm",
    (value) => Number.isFinite(value) ? value.toFixed(1) : "-",
    "누적 강수량 비교 데이터가 없습니다.",
  );
}

function getRouteHistoryFilterValues() {
  return {
    alertType: routeHistoryFilterElements.alertTypeSelect?.value || "",
    alertLevel: routeHistoryFilterElements.alertLevelSelect?.value || "all",
    period: routeHistoryFilterElements.periodSelect?.value || "1y",
  };
}

function getHistoryCaseLevel(caseItem) {
  if (caseItem.delay_min >= 18) {
    return "high";
  }

  if (caseItem.delay_min >= 10) {
    return "warning";
  }

  return "interest";
}

function getLatestHistoryCaseDate(cases) {
  const timestamps = cases
    .map((caseItem) => new Date(caseItem.date).getTime())
    .filter(Number.isFinite);

  if (timestamps.length === 0) {
    return null;
  }

  return new Date(Math.max(...timestamps));
}

function getHistoryPeriodStartDate(period, cases) {
  const monthCountByPeriod = {
    "3m": 3,
    "6m": 6,
    "1y": 12,
  };
  const monthCount = monthCountByPeriod[period] || monthCountByPeriod["1y"];
  const referenceDate = getLatestHistoryCaseDate(cases) || new Date();
  const startDate = new Date(referenceDate);

  startDate.setMonth(startDate.getMonth() - monthCount);
  startDate.setHours(0, 0, 0, 0);

  return startDate;
}

function isHistoryCaseInPeriod(caseItem, period, cases) {
  const caseDate = new Date(caseItem.date);

  if (Number.isNaN(caseDate.getTime())) {
    return false;
  }

  return caseDate >= getHistoryPeriodStartDate(period, cases);
}

function filterRouteHistoryCases(cases, filters) {
  return cases.filter((caseItem) => {
    const isMatchingAlertType = !filters.alertType || caseItem.alert_type === filters.alertType;
    const isMatchingAlertLevel =
      filters.alertLevel === "all" || getHistoryCaseLevel(caseItem) === filters.alertLevel;

    return isMatchingAlertType
      && isMatchingAlertLevel
      && isHistoryCaseInPeriod(caseItem, filters.period, cases);
  });
}

function renderFilteredRouteHistory() {
  if (!routeHistoryState) {
    return;
  }

  const cases = Array.isArray(routeHistoryState.segmentDetailData.cases)
    ? routeHistoryState.segmentDetailData.cases
    : [];
  const filteredSegmentDetailData = {
    ...routeHistoryState.segmentDetailData,
    cases: filterRouteHistoryCases(cases, getRouteHistoryFilterValues()),
  };

  renderRouteHistoryTable(filteredSegmentDetailData);
  renderRouteHistoryCharts(filteredSegmentDetailData, routeHistoryState.selectedSegment);
}

function initializeRouteHistoryFilter() {
  if (!routeHistoryFilterElements.form || isRouteHistoryFilterInitialized) {
    return;
  }

  routeHistoryFilterElements.form.addEventListener("submit", (event) => {
    event.preventDefault();
    renderFilteredRouteHistory();
  });

  isRouteHistoryFilterInitialized = true;
}

function renderRouteLineChart(segmentDetailData) {
  const chartData = Array.isArray(segmentDetailData.hourly_delay) ? segmentDetailData.hourly_delay : [];
  const actualPoints = getLineChartPoints(chartData, "actual");
  const forecastPoints = [
    ...(actualPoints.length > 0 ? [actualPoints[actualPoints.length - 1]] : []),
    ...getLineChartPoints(chartData, "forecast"),
  ];
  const highlightPoint = actualPoints[actualPoints.length - 1] || forecastPoints[0] || null;

  if (routeChartElements.lineChart) {
    routeChartElements.lineChart.setAttribute(
      "aria-label",
      chartData.length > 0
        ? `${formatSegmentLabel(segmentDetailData.from, segmentDetailData.to)} 시간대별 평균 지연 시간 선 그래프`
        : "시간대별 평균 지연 시간 데이터 없음",
    );
  }

  if (routeChartElements.lineActual) {
    routeChartElements.lineActual.setAttribute("points", toPolylinePoints(actualPoints));
  }

  if (routeChartElements.lineForecast) {
    routeChartElements.lineForecast.setAttribute("points", toPolylinePoints(forecastPoints));
  }

  if (routeChartElements.linePoint) {
    routeChartElements.linePoint.toggleAttribute("hidden", !highlightPoint);

    if (highlightPoint) {
      routeChartElements.linePoint.setAttribute("cx", String(highlightPoint.x));
      routeChartElements.linePoint.setAttribute("cy", String(highlightPoint.y));
    }
  }

  if (routeChartElements.lineTooltip) {
    routeChartElements.lineTooltip.textContent = highlightPoint ? highlightPoint.value.toFixed(1) : "-";

    if (highlightPoint) {
      routeChartElements.lineTooltip.setAttribute("x", String(highlightPoint.x));
      routeChartElements.lineTooltip.setAttribute("y", String(Math.max(highlightPoint.y - 17, 18)));
    }
  }

  if (routeChartElements.lineTooltipBox) {
    routeChartElements.lineTooltipBox.toggleAttribute("hidden", !highlightPoint);

    if (highlightPoint) {
      routeChartElements.lineTooltipBox.setAttribute("x", String(highlightPoint.x - 22));
      routeChartElements.lineTooltipBox.setAttribute("y", String(Math.max(highlightPoint.y - 38, 0)));
    }
  }
}

function renderRouteDelayTrendChart(segmentDetailData) {
  if (!routeChartElements.barChart) {
    return;
  }

  const trendItems = Array.isArray(segmentDetailData.delay_increase_trend)
    ? segmentDetailData.delay_increase_trend
    : [];
  const axisItems = Array.from(routeChartElements.barChart.querySelectorAll(".route-bar-chart__y"));
  const bars = trendItems.map((trendItem, index) => createDelayTrendBar(trendItem, index, trendItems.length));

  routeChartElements.barChart.replaceChildren(...axisItems, ...bars);
}

function renderRouteCharts(segmentDetailData, selectedSegment) {
  renderRouteLineChart(segmentDetailData);
  renderRouteDelayTrendChart(segmentDetailData);
  renderRouteAlertCharts(segmentDetailData);
  renderRouteHistoryCharts(segmentDetailData, selectedSegment);
}

function renderEmptyRouteDetail() {
  if (routeSummaryElements.breadcrumb) {
    routeSummaryElements.breadcrumb.textContent = "구간 상세";
  }

  if (routeSummaryElements.title) {
    routeSummaryElements.title.textContent = "구간 상세";
  }

  if (routeSummaryElements.description) {
    routeSummaryElements.description.textContent = "구간 정보를 불러오지 못했습니다.";
  }

  document.title = "구간 상세 | 기상-철도 리스크 의사결정 지원 시스템";

  if (routeSummaryElements.fromStation) {
    routeSummaryElements.fromStation.textContent = "출발역 정보 없음";
  }

  if (routeSummaryElements.toStation) {
    routeSummaryElements.toStation.textContent = "도착역 정보 없음";
  }

  if (routeSummaryElements.line) {
    routeSummaryElements.line.textContent = "노선 정보 없음";
  }

  if (routeSummaryElements.riskBadge) {
    routeSummaryElements.riskBadge.textContent = RISK_LABELS.none;
  }

  if (routeSummaryElements.alert) {
    routeSummaryElements.alert.textContent = "특보 정보 없음";
  }

  setMetricCard(routeMetricElements.avgDelay, "-", "분", "mock 데이터", "없음", "평균 예상 지연 시간 데이터 없음");
  setMetricCard(routeMetricElements.delayIncrease, "-", "분", "mock 데이터", "없음", "지연 증가량 데이터 없음");
  setMetricCard(routeMetricElements.stopRate, "-", "%", "mock 데이터", "없음", "운행 중단률 데이터 없음");
  setMetricCard(routeMetricElements.sampleCount, "-", "건", "mock 데이터", "없음", "분석 표본 수 데이터 없음");
  renderRouteAlertTables({});
  renderRouteHistoryTable({});
  renderRouteCharts({}, null);
}

function renderRoutePageMeta(segmentDetailData, selectedSegment) {
  const fromStation = selectedSegment?.from || segmentDetailData.from;
  const toStation = selectedSegment?.to || segmentDetailData.to;
  const segmentLabel = formatSegmentLabel(fromStation, toStation);

  if (routeSummaryElements.breadcrumb) {
    routeSummaryElements.breadcrumb.textContent = segmentLabel;
  }

  if (routeSummaryElements.title) {
    routeSummaryElements.title.textContent = segmentLabel;
  }

  if (routeSummaryElements.description) {
    routeSummaryElements.description.textContent = `${segmentLabel}의 기상 영향과 철도 운행 현황을 확인할 수 있습니다.`;
  }

  document.title = `${segmentLabel} | 구간 상세`;
}

function renderRouteSummary(segmentDetailData, vulnerabilitySegmentsData, selectedSegment) {
  const fromStation = selectedSegment?.from || segmentDetailData.from;
  const toStation = selectedSegment?.to || segmentDetailData.to;
  const riskLevel = getRiskLevel(selectedSegment?.avg_delay_incr, selectedSegment?.stop_rate);
  const alertText = `${vulnerabilitySegmentsData.alert_type || "특보"} ${vulnerabilitySegmentsData.alert_level || ""}`.trim();

  if (routeSummaryElements.fromStation) {
    routeSummaryElements.fromStation.textContent = formatStationName(fromStation);
  }

  if (routeSummaryElements.toStation) {
    routeSummaryElements.toStation.textContent = formatStationName(toStation);
  }

  if (routeSummaryElements.line) {
    routeSummaryElements.line.textContent = vulnerabilitySegmentsData.line || "노선 정보 없음";
  }

  if (routeSummaryElements.referenceTime) {
    routeSummaryElements.referenceTime.textContent = "mock 데이터 기준";
  }

  if (routeSummaryElements.riskBadge) {
    routeSummaryElements.riskBadge.textContent = RISK_LABELS[riskLevel];
  }

  if (routeSummaryElements.alert) {
    routeSummaryElements.alert.textContent = alertText || "특보 정보 없음";
  }

  if (routeSummaryElements.riskTime) {
    routeSummaryElements.riskTime.textContent = "mock 기준";
  }

  if (routeSummaryElements.riskCard) {
    routeSummaryElements.riskCard.setAttribute(
      "aria-label",
      `${formatStationName(fromStation)}에서 ${formatStationName(toStation)} 구간 현재 위험도 ${RISK_LABELS[riskLevel]}, ${alertText} 기준`,
    );
  }
}

function renderRouteMetrics(selectedSegment) {
  const avgDelay = Number.isFinite(selectedSegment?.avg_delay_incr)
    ? selectedSegment.avg_delay_incr.toFixed(1)
    : "-";
  const delayIncrease = formatSignedNumber(selectedSegment?.avg_delay_incr);
  const stopRate = formatPercent(selectedSegment?.stop_rate);
  const sampleCount = Number.isFinite(selectedSegment?.sample_n) ? String(selectedSegment.sample_n) : "-";

  setMetricCard(
    routeMetricElements.avgDelay,
    avgDelay,
    "분",
    "특보 기준",
    "평균 지연",
    `평균 예상 지연 시간 ${avgDelay}분`,
  );
  setMetricCard(
    routeMetricElements.delayIncrease,
    delayIncrease,
    "분",
    "평상시 대비",
    "증가량",
    `지연 증가량 ${delayIncrease}분`,
  );
  setMetricCard(
    routeMetricElements.stopRate,
    stopRate,
    "%",
    "mock 기준",
    "운행 중단률",
    `운행 중단률 ${stopRate}퍼센트`,
  );
  setMetricCard(
    routeMetricElements.sampleCount,
    sampleCount,
    "건",
    "mock 기준",
    "분석 표본",
    `분석 표본 수 ${sampleCount}건`,
  );
}

function renderRouteDetail(segmentDetailsData, vulnerabilitySegmentsData) {
  const selectedSegment = getInitialSegment(vulnerabilitySegmentsData, segmentDetailsData);

  if (!selectedSegment) {
    renderEmptyRouteDetail();
    return;
  }

  const selectedSegmentDetail = getSelectedSegmentDetail(selectedSegment, segmentDetailsData);
  routeHistoryState = {
    segmentDetailData: selectedSegmentDetail,
    selectedSegment,
  };

  renderRoutePageMeta(selectedSegmentDetail, selectedSegment);
  renderRouteSummary(selectedSegmentDetail, vulnerabilitySegmentsData, selectedSegment);
  renderRouteMetrics(selectedSegment);
  renderRouteAlertTables(selectedSegmentDetail);
  renderRouteHistoryTable(selectedSegmentDetail);
  renderRouteCharts(selectedSegmentDetail, selectedSegment);
  initializeRouteHistoryFilter();
}

async function fetchJson(url) {
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`Mock 데이터를 불러오지 못했습니다. status: ${response.status}`);
  }

  return response.json();
}

async function initializeRouteDetail() {
  try {
    const [segmentDetailData, vulnerabilitySegmentsData] = await Promise.all([
      fetchJson(SEGMENT_DETAIL_MOCK_URL),
      fetchJson(VULNERABILITY_SEGMENTS_MOCK_URL),
    ]);

    renderRouteDetail(segmentDetailData, vulnerabilitySegmentsData);
  } catch (error) {
    console.error(error);
    renderEmptyRouteDetail();
  }
}

routeTabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    setRouteTab(tab.dataset.routeTab);
  });
});

routeRiskCriteriaToggles.forEach((toggle) => {
  const panelId = toggle.getAttribute("aria-controls");
  const panel = panelId ? document.getElementById(panelId) : null;

  if (!panel) {
    return;
  }

  toggle.addEventListener("click", () => {
    const isExpanded = toggle.getAttribute("aria-expanded") === "true";

    toggle.setAttribute("aria-expanded", String(!isExpanded));
    panel.hidden = isExpanded;
  });
});

initializeRouteDetail();

const ROUTE_CHANGE_SEGMENT_LABELS = {
  "daejeon-gimcheon_gumi": "대전역 - 김천(구미)역",
  "cheonan-daejeon": "천안역 - 대전역",
  "yeongdeungpo-suwon": "영등포역 - 수원역",
  "dongdaegu-miryang": "동대구역 - 밀양역",
  "gimcheon_gumi-dongdaegu": "김천(구미)역 - 동대구역",
  "miryang-busan": "밀양역 - 부산역",
};

const routeChangeElements = {
  openButton: document.querySelector("[data-route-change-open]"),
  modal: document.querySelector("[data-route-change-modal]"),
  form: document.querySelector("[data-route-change-form]"),
  select: document.querySelector("[data-route-change-select]"),
  closeButtons: Array.from(document.querySelectorAll("[data-route-change-close]")),
};

function getRouteChangeLabel(segment) {
  return ROUTE_CHANGE_SEGMENT_LABELS[segment.segment_id]
    || `${segment.from || "출발역"} - ${segment.to || "도착역"}`;
}

function getCurrentRouteSegmentId() {
  return new URLSearchParams(window.location.search).get(SEGMENT_ID_QUERY_PARAM) || "daejeon-gimcheon_gumi";
}

function openRouteChangeModal() {
  if (!routeChangeElements.modal) {
    return;
  }

  routeChangeElements.modal.hidden = false;
  routeChangeElements.select?.focus();
}

function closeRouteChangeModal() {
  if (!routeChangeElements.modal) {
    return;
  }

  routeChangeElements.modal.hidden = true;
  routeChangeElements.openButton?.focus();
}

function moveToSelectedRoute(segmentId) {
  if (!segmentId) {
    return;
  }

  const nextUrl = new URL(window.location.href);

  nextUrl.searchParams.set(SEGMENT_ID_QUERY_PARAM, segmentId);
  window.location.href = nextUrl.toString();
}

function renderRouteChangeOptions(segments) {
  if (!routeChangeElements.select) {
    return;
  }

  const currentSegmentId = getCurrentRouteSegmentId();
  const options = segments.map((segment) => {
    const option = document.createElement("option");

    option.value = segment.segment_id;
    option.textContent = getRouteChangeLabel(segment);
    option.selected = segment.segment_id === currentSegmentId;

    return option;
  });

  if (options.length > 0) {
    routeChangeElements.select.replaceChildren(...options);
  }
}

async function initializeRouteChangeModal() {
  if (!routeChangeElements.openButton || !routeChangeElements.modal || !routeChangeElements.form) {
    return;
  }

  try {
    const vulnerabilitySegmentsData = await fetchJson(VULNERABILITY_SEGMENTS_MOCK_URL);
    renderRouteChangeOptions(getSegments(vulnerabilitySegmentsData));
  } catch (error) {
    console.error(error);
  }

  routeChangeElements.openButton.addEventListener("click", openRouteChangeModal);
  routeChangeElements.closeButtons.forEach((button) => {
    button.addEventListener("click", closeRouteChangeModal);
  });
  routeChangeElements.modal.addEventListener("click", (event) => {
    if (event.target === routeChangeElements.modal) {
      closeRouteChangeModal();
    }
  });
  routeChangeElements.form.addEventListener("submit", (event) => {
    event.preventDefault();
    moveToSelectedRoute(routeChangeElements.select?.value);
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !routeChangeElements.modal.hidden) {
      closeRouteChangeModal();
    }
  });
}

initializeRouteChangeModal();
