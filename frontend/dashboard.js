/* 기존 mock를 가져오던 부분
const ALERTS_MOCK_URL = "../mock/alerts_active.json";
const LINES_MOCK_URL = "../mock/lines.json";
const CHECKLIST_MOCK_URL = "../mock/checklist.json";
const VULNERABILITY_SEGMENTS_MOCK_URL = "../mock/vulnerability_segments.json";
const VULNERABILITY_STATIONS_MOCK_URL = "../mock/vulnerability_stations.json";
const HEATMAP_MOCK_URL = "../mock/heatmap.json";
*/

const ALERTS_MOCK_URL = "/alerts/active";
const LINES_MOCK_URL = "/lines";
const CHECKLIST_MOCK_URL = "/checklist";
const VULNERABILITY_SEGMENTS_MOCK_URL = "/vulnerability/segments";
const VULNERABILITY_STATIONS_MOCK_URL = "/vulnerability/stations";
const HEATMAP_MOCK_URL = "/heatmap";

const HIGH_DELAY_THRESHOLD_MINUTES = 12;
const HIGH_VULNERABILITY_THRESHOLD = 0.7;
const WARNING_VULNERABILITY_THRESHOLD = 0.5;

const ALL_FILTER_VALUE = "all";
const DEFAULT_DASHBOARD_FILTERS = Object.freeze({
  line: "경부선",
  alertType: ALL_FILTER_VALUE,
  alertLevel: ALL_FILTER_VALUE,
  trainType: ALL_FILTER_VALUE,
});
const FILTER_QUERY_PARAM_NAMES = Object.freeze({
  line: "line",
  alertType: "alert_type",
  alertLevel: "alert_level",
  trainType: "train_type",
});
const ALERT_LEVEL_ORDER = Object.freeze(["주의보", "경보"]);
const TRAIN_TYPE_ORDER = Object.freeze(["KTX", "새마을", "무궁화"]);

const GYEONGBU_HIGH_SPEED_STATIONS = Object.freeze([
  { stationId: "seoul", station: "서울" },
  { stationId: "gwangmyeong", station: "광명" },
  { stationId: "cheonan_asan", station: "천안아산" },
  { stationId: "osong", station: "오송" },
  { stationId: "daejeon", station: "대전" },
  { stationId: "gimcheon_gumi", station: "김천구미" },
  { stationId: "dongdaegu", station: "동대구" },
  { stationId: "gyeongju", station: "경주" },
  { stationId: "ulsan", station: "울산" },
  { stationId: "busan", station: "부산" },
]);

const RISK_LEVELS = {
  high: { label: "높음", color: "#EF4444" },
  warning: { label: "주의", color: "#F59E0B" },
  interest: { label: "관심", color: "#22C55E" },
  insufficient: { label: "표본 부족", color: "#9CA3AF" },
  none: { label: "-", color: "#D1D5DB" },
};

const STATION_DETAIL_URL = "./station-detail.html";
const ROUTE_DETAIL_URL = "./route-detail.html";
const STATION_QUERY_PARAM = "station";
const STATION_ID_QUERY_PARAM = "station_id";
const SEGMENT_ID_QUERY_PARAM = "segment_id";

const alertElements = {
  updatedTime: document.querySelector("[data-dashboard-updated-time]"),
  banner: document.querySelector("[data-dashboard-alert-banner]"),
  list: document.querySelector("[data-dashboard-alert-list]"),
};

const filterElements = {
  form: document.querySelector("[data-dashboard-filter-form]"),
  lineSelect: document.querySelector("[data-dashboard-line-select]"),
  alertTypeSelect: document.querySelector("[data-dashboard-alert-type-select]"),
  alertLevelSelect: document.querySelector("[data-dashboard-alert-level-select]"),
  trainTypeSelect: document.querySelector("[data-dashboard-train-type-select]"),
};

const summaryCardElements = {
  affectedSegments: document.querySelector('[data-dashboard-summary-card="affected-segments"]'),
  delayedTrains: document.querySelector('[data-dashboard-summary-card="delayed-trains"]'),
  averageDelay: document.querySelector('[data-dashboard-summary-card="average-delay"]'),
  highRiskSegments: document.querySelector('[data-dashboard-summary-card="high-risk-segments"]'),
};

const heatmapElements = {
  title: document.querySelector("[data-dashboard-heatmap-title]"),
  routeMap: document.querySelector("[data-dashboard-route-map]"),
  routeList: document.querySelector("[data-dashboard-route-list]"),
  summary: {
    high: document.querySelector('[data-dashboard-heatmap-summary="high"]'),
    warning: document.querySelector('[data-dashboard-heatmap-summary="warning"]'),
    interest: document.querySelector('[data-dashboard-heatmap-summary="interest"]'),
    insufficient: document.querySelector('[data-dashboard-heatmap-summary="insufficient"]'),
    none: document.querySelector('[data-dashboard-heatmap-summary="none"]'),
  },
  referenceTime: document.querySelector("[data-dashboard-heatmap-reference-time]"),
  source: document.querySelector("[data-dashboard-heatmap-source]"),
};

const rankingElements = {
  segmentBody: document.querySelector("[data-dashboard-segment-ranking-body]"),
  stationBody: document.querySelector("[data-dashboard-station-ranking-body]"),
};

const inspectionElements = {
  body: document.querySelector("[data-dashboard-inspection-body]"),
  detail: document.querySelector("[data-dashboard-inspection-detail]"),
};

let dashboardState = null;

function formatDateTime(isoDateString) {
  const date = new Date(isoDateString);

  if (Number.isNaN(date.getTime())) {
    return "업데이트 정보 없음";
  }

  const formatter = new Intl.DateTimeFormat("ko-KR", {
    timeZone: "Asia/Seoul",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });

  const parts = Object.fromEntries(
    formatter.formatToParts(date).map((part) => [part.type, part.value]),
  );

  return `${parts.year}.${parts.month}.${parts.day}. ${parts.hour} : ${parts.minute}`;
}

function formatStandardTime(isoDateString) {
  const date = new Date(isoDateString);

  if (Number.isNaN(date.getTime())) {
    return "기준 시간 정보 없음";
  }

  const formatter = new Intl.DateTimeFormat("ko-KR", {
    timeZone: "Asia/Seoul",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });

  return `${formatter.format(date)} 기준 영향 가능 철도 구간`;
}

function formatCompactDateTime(isoDateString) {
  const date = new Date(isoDateString);

  if (Number.isNaN(date.getTime())) {
    return "기준 시간 정보 없음";
  }

  const formatter = new Intl.DateTimeFormat("ko-KR", {
    timeZone: "Asia/Seoul",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });

  const parts = Object.fromEntries(
    formatter.formatToParts(date).map((part) => [part.type, part.value]),
  );

  return `${parts.year}.${parts.month}.${parts.day} ${parts.hour}:${parts.minute}`;
}

function getAffectedSegmentCount(activeAlerts) {
  return activeAlerts.reduce((total, alert) => {
    const affected = Array.isArray(alert.affected) ? alert.affected : [];
    const segmentCount = affected.filter((item) => item.type === "segment").length;

    return total + segmentCount;
  }, 0);
}

function groupActiveAlerts(activeAlerts) {
  const groups = new Map();

  activeAlerts.forEach((alert) => {
    const alertType = alert.alert_type || "특보";
    const alertLevel = alert.alert_level || "";
    const key = `${alertType}:${alertLevel}`;
    const group = groups.get(key) || {
      label: `${alertType} ${alertLevel}`.trim(),
      regions: [],
      affectedSegmentCount: 0,
    };

    if (alert.region_name && !group.regions.includes(alert.region_name)) {
      group.regions.push(alert.region_name);
    }

    group.affectedSegmentCount += getAffectedSegmentCount([alert]);
    groups.set(key, group);
  });

  return [...groups.values()];
}

function createHiddenRegionList(regions, alertLabel) {
  const container = document.createElement("span");
  const button = document.createElement("button");
  const tooltip = document.createElement("span");

  container.className = "alert-banner__region-overflow";
  button.className = "alert-banner__region-button";
  button.type = "button";
  button.textContent = `외 ${regions.length}개 지역`;
  button.setAttribute("aria-expanded", "false");
  button.setAttribute("aria-label", `${alertLabel} 나머지 지역 ${regions.length}개 보기`);

  tooltip.className = "alert-banner__region-tooltip";
  tooltip.setAttribute("role", "tooltip");
  tooltip.textContent = regions.join("\n");

  container.addEventListener("mouseleave", () => {
    container.dataset.open = "false";
    button.setAttribute("aria-expanded", "false");

    if (button.matches(":focus")) {
      button.blur();
    }
  });

  container.append(button, tooltip);
  return container;
}

function createAlertGroupItem(group, updatedAt) {
  const item = document.createElement("div");
  const badge = document.createElement("span");
  const regionText = document.createElement("p");
  const standardTime = document.createElement("span");
  const count = document.createElement("strong");
  const [primaryRegion = "영향 지역 정보 없음", ...hiddenRegions] = group.regions;

  item.className = "alert-banner__item";
  badge.className = "alert-banner__badge";
  badge.textContent = group.label;
  regionText.className = "alert-banner__text";
  regionText.append(document.createTextNode(primaryRegion));

  if (hiddenRegions.length > 0) {
    regionText.append(document.createTextNode(" "), createHiddenRegionList(hiddenRegions, group.label));
  }

  standardTime.className = "alert-banner__muted";
  standardTime.textContent = formatStandardTime(updatedAt);
  count.className = "alert-banner__count";
  count.textContent = `${group.affectedSegmentCount}개`;
  item.append(badge, regionText, standardTime, count);

  return item;
}

function getChecklistItems(checklistData) {
  return Array.isArray(checklistData.items) ? checklistData.items : [];
}

function getSegmentKey(fromStation, toStation) {
  return [fromStation, toStation].sort((left, right) => left.localeCompare(right, "ko")).join(":");
}

function isHighSpeedSegment(fromStation, toStation) {
  const fromIndex = GYEONGBU_HIGH_SPEED_STATIONS.findIndex(
    (station) => station.station === fromStation,
  );
  const toIndex = GYEONGBU_HIGH_SPEED_STATIONS.findIndex(
    (station) => station.station === toStation,
  );

  return fromIndex >= 0 && toIndex >= 0 && Math.abs(fromIndex - toIndex) === 1;
}

function getUniqueAffectedHighSpeedSegmentCount(activeAlerts) {
  const segmentKeys = new Set();

  activeAlerts.forEach((alert) => {
    const affected = Array.isArray(alert.affected) ? alert.affected : [];

    affected.forEach((item) => {
      if (item.type === "segment" && isHighSpeedSegment(item.from, item.to)) {
        segmentKeys.add(getSegmentKey(item.from, item.to));
      }
    });
  });

  return segmentKeys.size;
}

function getWeightedAverageHighSpeedDelay(segmentsData) {
  const segments = Array.isArray(segmentsData.segments) ? segmentsData.segments : [];
  const validSegments = segments.filter((segment) =>
    isHighSpeedSegment(segment.from, segment.to)
    && Number.isFinite(segment.avg_delay_incr)
    && Number.isFinite(segment.sample_n)
    && segment.sample_n > 0,
  );

  if (validSegments.length === 0) {
    return null;
  }

  const totalSampleCount = validSegments.reduce((sum, segment) => sum + segment.sample_n, 0);
  const weightedDelayTotal = validSegments.reduce(
    (sum, segment) => sum + (segment.avg_delay_incr * segment.sample_n),
    0,
  );

  return weightedDelayTotal / totalSampleCount;
}

function getHighRiskHighSpeedSegmentCount(heatmapData) {
  const edges = Array.isArray(heatmapData.edges) ? heatmapData.edges : [];

  return edges.filter((edge) =>
    isHighSpeedSegment(edge.from, edge.to)
    && edge.risk_level === "high",
  ).length;
}

function updateRecentUpdatedTime(updatedAt) {
  if (!alertElements.updatedTime) {
    return;
  }

  alertElements.updatedTime.dateTime = updatedAt || "";
  alertElements.updatedTime.textContent = formatDateTime(updatedAt);
}

function renderEmptyAlertBanner() {
  if (alertElements.list) {
    const message = document.createElement("p");

    message.className = "alert-banner__empty";
    message.textContent = "현재 발효 중인 기상특보가 없습니다.";
    alertElements.list.replaceChildren(message);
  }

  if (alertElements.banner) {
    alertElements.banner.setAttribute("aria-label", "현재 발효 중인 기상특보 없음");
  }
}

function renderAlertBanner(alertsData) {
  const activeAlerts = Array.isArray(alertsData.active) ? alertsData.active : [];

  updateRecentUpdatedTime(alertsData.updated_at);

  if (activeAlerts.length === 0) {
    renderEmptyAlertBanner();
    return;
  }

  const groups = groupActiveAlerts(activeAlerts);

  if (alertElements.list) {
    alertElements.list.replaceChildren(
      ...groups.map((group) => createAlertGroupItem(group, alertsData.updated_at)),
    );
  }

  if (alertElements.banner) {
    alertElements.banner.setAttribute(
      "aria-label",
      `현재 발효 중인 기상특보 ${groups.map((group) =>
        `${group.label}, ${group.regions.join(", ") || "영향 지역 정보 없음"}, 영향 가능 철도 구간 ${group.affectedSegmentCount}개`
      ).join("; ")}`,
    );
  }
}

function initializeAlertRegionTooltips() {
  if (!alertElements.list) {
    return;
  }

  alertElements.list.addEventListener("click", (event) => {
    const button = event.target.closest(".alert-banner__region-button");

    if (!button) {
      return;
    }

    const container = button.closest(".alert-banner__region-overflow");
    const isOpen = container.dataset.open === "true";

    alertElements.list.querySelectorAll(".alert-banner__region-overflow[data-open='true']")
      .forEach((openContainer) => {
        openContainer.dataset.open = "false";
        openContainer.querySelector(".alert-banner__region-button")?.setAttribute("aria-expanded", "false");
      });

    container.dataset.open = String(!isOpen);
    button.setAttribute("aria-expanded", String(!isOpen));
  });

  alertElements.list.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") {
      return;
    }

    const container = event.target.closest(".alert-banner__region-overflow");

    if (container) {
      container.dataset.open = "false";
      container.querySelector(".alert-banner__region-button")?.setAttribute("aria-expanded", "false");
    }
  });
}

function createOption(value, label, isSelected = false) {
  const option = document.createElement("option");

  option.value = value;
  option.textContent = label;
  option.selected = isSelected;

  return option;
}

function renderEmptyLineSelect() {
  if (!filterElements.lineSelect) {
    return;
  }

  filterElements.lineSelect.replaceChildren(createOption("", "데이터 없음", true));
  filterElements.lineSelect.disabled = true;
}

function renderLineSelect(linesData) {
  if (!filterElements.lineSelect) {
    return;
  }

  const lines = Array.isArray(linesData.lines) ? linesData.lines : [];
  const lineNames = lines.map((line) => line.line).filter(Boolean);

  if (lineNames.length === 0) {
    renderEmptyLineSelect();
    return;
  }

  const options = lineNames.map((lineName, index) => createOption(lineName, lineName, index === 0));

  filterElements.lineSelect.disabled = false;
  filterElements.lineSelect.replaceChildren(...options);
}

function getUniqueFilterValues(values) {
  return [...new Set(values.filter((value) => typeof value === "string" && value.trim()))];
}

function sortFilterValues(values, preferredOrder = []) {
  const orderIndexes = new Map(preferredOrder.map((value, index) => [value, index]));

  return values.slice().sort((left, right) => {
    const leftIndex = orderIndexes.get(left) ?? Number.MAX_SAFE_INTEGER;
    const rightIndex = orderIndexes.get(right) ?? Number.MAX_SAFE_INTEGER;

    if (leftIndex !== rightIndex) {
      return leftIndex - rightIndex;
    }

    return left.localeCompare(right, "ko");
  });
}

function renderDynamicFilterSelect(select, values, preferredOrder, emptyMessage) {
  if (!select) {
    return;
  }

  const uniqueValues = sortFilterValues(getUniqueFilterValues(values), preferredOrder);
  const options = [
    createOption(ALL_FILTER_VALUE, "전체", true),
    ...uniqueValues.map((value) => createOption(value, value)),
  ];

  select.replaceChildren(...options);
  select.disabled = uniqueValues.length === 0;
  select.title = uniqueValues.length === 0 ? emptyMessage : "";
}

function collectNestedFilterValues(source, singularKey, pluralKey, values = []) {
  if (Array.isArray(source)) {
    source.forEach((item) => collectNestedFilterValues(item, singularKey, pluralKey, values));
    return values;
  }

  if (!source || typeof source !== "object") {
    return values;
  }

  if (typeof source[singularKey] === "string") {
    values.push(source[singularKey]);
  }

  if (Array.isArray(source[pluralKey])) {
    values.push(...source[pluralKey]);
  }

  Object.values(source).forEach((value) => {
    if (value && typeof value === "object") {
      collectNestedFilterValues(value, singularKey, pluralKey, values);
    }
  });

  return values;
}

function renderDashboardFilterOptions(data) {
  const filterSources = [
    data.alertsData,
    data.checklistData,
    data.vulnerabilitySegmentsData,
    data.vulnerabilityStationsData,
    data.heatmapData,
  ];
  const alertTypes = collectNestedFilterValues(filterSources, "alert_type", "alert_types");
  const alertLevels = collectNestedFilterValues(filterSources, "alert_level", "alert_levels");
  const trainTypes = collectNestedFilterValues(filterSources, "train_type", "train_types");

  renderDynamicFilterSelect(
    filterElements.alertTypeSelect,
    alertTypes,
    [],
    "특보 종류 데이터가 제공되지 않습니다.",
  );
  renderDynamicFilterSelect(
    filterElements.alertLevelSelect,
    alertLevels,
    ALERT_LEVEL_ORDER,
    "특보 등급 데이터가 제공되지 않습니다.",
  );
  renderDynamicFilterSelect(
    filterElements.trainTypeSelect,
    trainTypes,
    TRAIN_TYPE_ORDER,
    "열차 종류 데이터가 제공되지 않습니다.",
  );
}

function renderEmptyDashboardFilterOptions() {
  renderDynamicFilterSelect(filterElements.alertTypeSelect, [], [], "특보 종류 데이터가 없습니다.");
  renderDynamicFilterSelect(filterElements.alertLevelSelect, [], [], "특보 등급 데이터가 없습니다.");
  renderDynamicFilterSelect(filterElements.trainTypeSelect, [], [], "열차 종류 데이터가 없습니다.");
}

function setSummaryCard(card, value, unit, comparisonText, ariaLabel) {
  if (!card) {
    return;
  }

  const valueElement = card.querySelector("[data-dashboard-summary-value]");
  const unitElement = card.querySelector("[data-dashboard-summary-unit]");
  const comparisonElement = card.querySelector("[data-dashboard-summary-comparison]");

  if (valueElement) {
    valueElement.textContent = value;
  }

  if (unitElement) {
    unitElement.textContent = unit;
  }

  if (comparisonElement) {
    comparisonElement.textContent = comparisonText;
  }

  card.setAttribute("aria-label", ariaLabel);
}

function renderEmptySummaryCards() {
  setSummaryCard(
    summaryCardElements.affectedSegments,
    "0",
    "개",
    "전일 비교 데이터 없음",
    "영향 가능 구간 데이터 없음",
  );
  setSummaryCard(
    summaryCardElements.delayedTrains,
    "-",
    "편",
    "집계 데이터 없음",
    "운행 지연 예상 열차 데이터 없음",
  );
  setSummaryCard(
    summaryCardElements.averageDelay,
    "-",
    "분",
    "전일 비교 데이터 없음",
    "평균 신규 지연 데이터 없음",
  );
  setSummaryCard(
    summaryCardElements.highRiskSegments,
    "0",
    "개",
    "전일 비교 데이터 없음",
    "위험도 높음 구간 데이터 없음",
  );
}

function getSummaryContainers(dataSources) {
  return dataSources.flatMap((source) => [source?.dashboard_summary, source?.summary, source])
    .filter((source) => source && typeof source === "object");
}

function findFiniteSummaryValue(dataSources, fieldName) {
  const container = getSummaryContainers(dataSources).find(
    (source) => Number.isFinite(source[fieldName]),
  );

  return container ? container[fieldName] : null;
}

function getMetricPreviousValue(dataSources, metricName) {
  for (const container of getSummaryContainers(dataSources)) {
    const nestedPreviousValue = container[metricName]?.previous;
    const comparisonPreviousValue = container.comparisons?.[metricName]?.previous;
    const flatPreviousValue = container[`${metricName}_previous`];
    const previousValue = [nestedPreviousValue, comparisonPreviousValue, flatPreviousValue]
      .find((value) => Number.isFinite(value));

    if (Number.isFinite(previousValue)) {
      return previousValue;
    }
  }

  return null;
}

function formatMetricNumber(value) {
  return Number.isInteger(value) ? String(value) : value.toFixed(1);
}

function formatDayOverDayComparison(currentValue, previousValue) {
  if (!Number.isFinite(currentValue) || !Number.isFinite(previousValue)) {
    return "전일 비교 데이터 없음";
  }

  const difference = currentValue - previousValue;

  if (difference === 0) {
    return "전일과 동일";
  }

  const sign = difference > 0 ? "+" : "";
  const arrow = difference > 0 ? "↑" : "↓";

  return `전일 대비 ${sign}${formatMetricNumber(difference)} ${arrow}`;
}

function getExpectedDelayedTrainCount(dataSources) {
  const directCount = findFiniteSummaryValue(dataSources, "expected_delayed_train_count");

  if (directCount !== null) {
    return directCount;
  }

  for (const container of getSummaryContainers(dataSources)) {
    if (!Array.isArray(container.expected_delayed_trains)) {
      continue;
    }

    const trainKeys = new Set(
      container.expected_delayed_trains
        .filter((train) => train?.run_date && train?.train_no)
        .map((train) => `${train.run_date}:${train.train_no}`),
    );

    return trainKeys.size;
  }

  return null;
}

function renderSummaryCards(
  alertsData,
  checklistData,
  vulnerabilitySegmentsData,
  heatmapData,
) {
  const dataSources = [alertsData, checklistData, vulnerabilitySegmentsData, heatmapData];
  const activeAlerts = Array.isArray(alertsData.active) ? alertsData.active : [];
  const affectedSegmentCount = getUniqueAffectedHighSpeedSegmentCount(activeAlerts);
  const expectedDelayedTrainCount = getExpectedDelayedTrainCount(dataSources);
  const averageDelayIncrease = getWeightedAverageHighSpeedDelay(vulnerabilitySegmentsData);
  const highRiskSegmentCount = getHighRiskHighSpeedSegmentCount(heatmapData);
  const affectedSegmentsComparison = formatDayOverDayComparison(
    affectedSegmentCount,
    getMetricPreviousValue(dataSources, "affected_segments"),
  );
  const delayedTrainsComparison = formatDayOverDayComparison(
    expectedDelayedTrainCount,
    getMetricPreviousValue(dataSources, "expected_delayed_trains"),
  );
  const averageDelayComparison = formatDayOverDayComparison(
    averageDelayIncrease,
    getMetricPreviousValue(dataSources, "average_delay_increase"),
  );
  const highRiskSegmentsComparison = formatDayOverDayComparison(
    highRiskSegmentCount,
    getMetricPreviousValue(dataSources, "high_risk_segments"),
  );
  const averageDelayText =
    averageDelayIncrease === null ? "-" : averageDelayIncrease.toFixed(1);
  const expectedDelayedTrainText = expectedDelayedTrainCount === null
    ? "-"
    : String(expectedDelayedTrainCount);

  setSummaryCard(
    summaryCardElements.affectedSegments,
    String(affectedSegmentCount),
    "개",
    affectedSegmentsComparison,
    `영향 가능 고속철도 구간 ${affectedSegmentCount}개, 현재 발효 특보 기준, ${affectedSegmentsComparison}`,
  );
  setSummaryCard(
    summaryCardElements.delayedTrains,
    expectedDelayedTrainText,
    "편",
    expectedDelayedTrainCount === null ? "집계 데이터 없음" : delayedTrainsComparison,
    expectedDelayedTrainCount === null
      ? "운행 지연 예상 열차 데이터 없음"
      : `운행 지연 예상 열차 ${expectedDelayedTrainText}편, ${delayedTrainsComparison}`,
  );
  setSummaryCard(
    summaryCardElements.averageDelay,
    averageDelayText,
    "분",
    averageDelayComparison,
    `평균 신규 지연 예상 ${averageDelayText}분, 고속철도 구간 표본 가중평균, ${averageDelayComparison}`,
  );
  setSummaryCard(
    summaryCardElements.highRiskSegments,
    String(highRiskSegmentCount),
    "개",
    highRiskSegmentsComparison,
    `위험도 높음 고속철도 구간 ${highRiskSegmentCount}개, 위험도 점수 기준, ${highRiskSegmentsComparison}`,
  );
}

function createRouteMapItem(node, segment, stations = []) {
  const riskLevel = node.risk_level || "none";
  const risk = RISK_LEVELS[riskLevel] || RISK_LEVELS.none;
  const segmentRiskLevel = segment?.risk_level || "none";
  const stationInfo = getStationByName(node.station, stations);
  const stationId = stationInfo?.station_id || node.stationId;
  const item = document.createElement("li");
  const station = document.createElement("span");
  const marker = document.createElement("span");
  const segmentLine = document.createElement("span");
  const dash = document.createElement("span");
  const status = document.createElement("span");
  const chevron = document.createElement("a");

  item.className = `route-map__item route-map__item--${riskLevel}`;
  item.setAttribute("aria-label", `${node.station} 위험도 ${risk.label}`);

  station.className = "route-map__station";
  station.textContent = node.station;

  marker.className = "route-map__marker";
  segmentLine.className = `route-map__segment route-map__segment--${segmentRiskLevel}`;
  segmentLine.setAttribute("aria-hidden", "true");
  dash.className = "route-map__dash";

  status.className = "route-map__status";
  status.textContent = risk.label;

  chevron.className = "route-map__chevron";
  chevron.href = createStationDetailUrl(node.station, stationId);
  chevron.textContent = "›";
  chevron.setAttribute(
    "aria-label",
    stationInfo
      ? `${node.station}역 상세 화면으로 이동`
      : `${node.station}역 상세 화면으로 이동, 현재 mock 상세 데이터 없음`,
  );
  chevron.title = stationInfo
    ? `${node.station}역 상세 화면으로 이동`
    : `${node.station}역 상세 화면으로 이동합니다. 현재 mock 상세 데이터는 없습니다.`;

  item.append(station, marker, segmentLine, dash, status, chevron);

  return item;
}

function countHeatmapEdgesByRiskLevel(edges) {
  return edges.reduce(
    (counts, edge) => {
      const riskLevel = edge.risk_level || "none";
      counts[riskLevel] = (counts[riskLevel] ?? 0) + 1;

      return counts;
    },
    { high: 0, warning: 0, interest: 0, insufficient: 0, none: 0 },
  );
}

function findHeatmapNode(stationName, nodes) {
  return nodes.find((node) => node.station === stationName) || null;
}

function findHeatmapEdge(fromStation, toStation, edges) {
  return edges.find((edge) =>
    (edge.from === fromStation && edge.to === toStation)
    || (edge.from === toStation && edge.to === fromStation),
  ) || null;
}

function buildHighSpeedRoute(nodes, edges) {
  return GYEONGBU_HIGH_SPEED_STATIONS.map((stationReference, index) => {
    const nextStationReference = GYEONGBU_HIGH_SPEED_STATIONS[index + 1];
    const stationName = stationReference.station;
    const nextStationName = nextStationReference?.station;
    const node = findHeatmapNode(stationName, nodes);
    const segment = nextStationName
      ? findHeatmapEdge(stationName, nextStationName, edges)
      : null;

    return {
      node: {
        stationId: stationReference.stationId,
        station: stationName,
        risk_level: node?.risk_level ?? "none",
      },
      segment: nextStationName
        ? { from: stationName, to: nextStationName, risk_level: segment?.risk_level ?? "none" }
        : null,
    };
  });
}

function renderEmptyHeatmap() {
  if (heatmapElements.title) {
    heatmapElements.title.textContent = "경부선 고속철도 기상 위험도 현황";
  }

  if (heatmapElements.routeMap) {
    heatmapElements.routeMap.setAttribute("aria-label", "경부선 고속철도 역별 위험도 데이터 없음");
  }

  if (heatmapElements.routeList) {
    heatmapElements.routeList.replaceChildren();
  }

  Object.values(heatmapElements.summary).forEach((element) => {
    if (element) {
      element.textContent = "0개";
    }
  });

  if (heatmapElements.referenceTime) {
    heatmapElements.referenceTime.textContent = "기준 시간 : 정보 없음";
  }

  if (heatmapElements.source) {
    heatmapElements.source.textContent = "데이터 출처 : mock/heatmap.json";
  }
}

function renderHeatmap(heatmapData, updatedAt, vulnerabilityStationsData = {}) {
  const nodes = Array.isArray(heatmapData.nodes) ? heatmapData.nodes : [];
  const edges = Array.isArray(heatmapData.edges) ? heatmapData.edges : [];
  const stations = getStationsFromData(vulnerabilityStationsData);
  const lineName = heatmapData.line || "노선";
  const highSpeedRoute = buildHighSpeedRoute(nodes, edges);
  const routeSegments = highSpeedRoute.map((item) => item.segment).filter(Boolean);
  const edgeCounts = countHeatmapEdgesByRiskLevel(routeSegments);

  if (heatmapElements.title) {
    heatmapElements.title.textContent = `${lineName} 고속철도 기상 위험도 현황`;
  }

  if (heatmapElements.routeMap) {
    heatmapElements.routeMap.setAttribute("aria-label", `${lineName} 고속철도 역별 위험도`);
  }

  if (heatmapElements.routeList) {
    heatmapElements.routeList.replaceChildren(
      ...highSpeedRoute.map(({ node, segment }) => createRouteMapItem(node, segment, stations)),
    );
  }

  Object.entries(edgeCounts).forEach(([riskLevel, count]) => {
    const element = heatmapElements.summary[riskLevel];

    if (element) {
      element.textContent = `${count}개`;
    }
  });

  if (heatmapElements.referenceTime) {
    heatmapElements.referenceTime.textContent = `기준 시간 : ${formatCompactDateTime(updatedAt)}`;
  }

  if (heatmapElements.source) {
    heatmapElements.source.textContent = "데이터 출처 : mock/heatmap.json";
  }
}

function createRiskBadge(riskLevel) {
  const badge = document.createElement("span");
  const risk = RISK_LEVELS[riskLevel] || RISK_LEVELS.none;

  badge.className = `risk-badge risk-badge--${riskLevel}`;
  badge.textContent = risk.label;

  return badge;
}

function createRankingCell(text, className = "") {
  const cell = document.createElement("td");

  if (className) {
    cell.className = className;
  }

  cell.textContent = text;

  return cell;
}

function getStationsFromData(vulnerabilityStationsData) {
  return Array.isArray(vulnerabilityStationsData.stations)
    ? vulnerabilityStationsData.stations
    : [];
}

function getStationByName(stationName, stations) {
  return stations.find((station) => station.station === stationName) || null;
}

function getStationById(stationId, stations) {
  return stations.find((station) => station.station_id === stationId) || null;
}

function createStationDetailUrl(stationName, stationId) {
  const params = new URLSearchParams({
    [stationId ? STATION_ID_QUERY_PARAM : STATION_QUERY_PARAM]: stationId || stationName,
  });

  return `${STATION_DETAIL_URL}?${params.toString()}`;
}

function createStationLinkCell(stationName, stationId) {
  const cell = document.createElement("td");
  const link = document.createElement("a");

  cell.className = "ranking-table__target";
  link.className = "ranking-table__link";
  link.href = createStationDetailUrl(stationName, stationId);
  link.textContent = stationName;
  link.setAttribute("aria-label", `${stationName}역 상세 화면으로 이동`);
  cell.append(link);

  return cell;
}

function createSegmentDetailUrl(segmentId) {
  const params = new URLSearchParams({
    [SEGMENT_ID_QUERY_PARAM]: segmentId,
  });

  return `${ROUTE_DETAIL_URL}?${params.toString()}`;
}

function createSegmentLinkCell(segment) {
  const cell = document.createElement("td");
  const link = document.createElement("a");
  const segmentLabel = `${segment.from}-${segment.to}`;

  cell.className = "ranking-table__target";

  if (!segment.segment_id) {
    cell.textContent = segmentLabel;
    return cell;
  }

  link.className = "ranking-table__link";
  link.href = createSegmentDetailUrl(segment.segment_id);
  link.textContent = segmentLabel;
  link.setAttribute("aria-label", `${segment.from}에서 ${segment.to} 구간 상세 화면으로 이동`);
  cell.append(link);

  return cell;
}

function getStationNameFromInspectionTarget(target, stations) {
  if (!target || !target.endsWith("역")) {
    return null;
  }

  const stationName = target.slice(0, -1);

  return getStationByName(stationName, stations)?.station || null;
}

function getStationNameFromInspectionItem(item, stations) {
  if (item.target_type === "station" && item.station_id) {
    const station = getStationById(item.station_id, stations);

    return station?.station || null;
  }

  return getStationNameFromInspectionTarget(item.target, stations);
}

function createStationDetailLink(stationName, label, stationId) {
  const link = document.createElement("a");

  link.className = "inspection-link";
  link.href = createStationDetailUrl(stationName, stationId);
  link.textContent = label;
  link.setAttribute("aria-label", `${label} 상세 화면으로 이동`);

  return link;
}

function createRouteDetailLink(segmentId, label) {
  const link = document.createElement("a");

  link.className = "inspection-link";
  link.href = createSegmentDetailUrl(segmentId);
  link.textContent = label;
  link.setAttribute("aria-label", `${label} 구간 상세 화면으로 이동`);

  return link;
}

function createEmptyRankingRow(message, columnCount) {
  const row = document.createElement("tr");
  const cell = document.createElement("td");

  cell.colSpan = columnCount;
  cell.textContent = message;

  row.append(cell);

  return row;
}

function createTableMessageRow(message, columnCount) {
  const row = document.createElement("tr");
  const cell = document.createElement("td");

  cell.colSpan = columnCount;
  cell.textContent = message;

  row.append(cell);

  return row;
}

function renderEmptyRankings() {
  if (rankingElements.segmentBody) {
    rankingElements.segmentBody.replaceChildren(createEmptyRankingRow("위험 구간 데이터가 없습니다.", 5));
  }

  if (rankingElements.stationBody) {
    rankingElements.stationBody.replaceChildren(createEmptyRankingRow("위험 역 데이터가 없습니다.", 5));
  }
}

function createSegmentRankingRow(segment, index, lineName) {
  const row = document.createElement("tr");
  const riskLevel = segment.risk_level || "none";
  const riskCell = document.createElement("td");

  if (segment.segment_id) {
    row.dataset.segmentId = segment.segment_id;
  }

  riskCell.append(createRiskBadge(riskLevel));
  row.append(
    createRankingCell(String(index + 1)),
    createSegmentLinkCell(segment),
    createRankingCell(lineName),
    riskCell,
    createRankingCell(segment.avg_delay_incr.toFixed(1), "ranking-table__number"),
  );

  return row;
}

function createStationRankingRow(station, index, lineName) {
  const row = document.createElement("tr");
  const riskLevel = station.risk_level || "none";
  const riskCell = document.createElement("td");
  const hasExactDelayCount = Number.isFinite(station.delay_count);
  const estimatedDelayCount = Number.isFinite(station.sample_n) && Number.isFinite(station.delay_rate)
    ? Math.round(station.sample_n * station.delay_rate)
    : null;
  const delayCountText = hasExactDelayCount
    ? `${station.delay_count}건`
    : Number.isFinite(estimatedDelayCount)
      ? `약 ${estimatedDelayCount}건`
      : "-";

  riskCell.append(createRiskBadge(riskLevel));
  row.append(
    createRankingCell(String(index + 1)),
    createStationLinkCell(station.station, station.station_id),
    createRankingCell(lineName),
    riskCell,
    createRankingCell(delayCountText, "ranking-table__number"),
  );

  return row;
}

function renderRankings(vulnerabilitySegmentsData, vulnerabilityStationsData) {
  const segments = Array.isArray(vulnerabilitySegmentsData.segments)
    ? vulnerabilitySegmentsData.segments
    : [];
  const stations = Array.isArray(vulnerabilityStationsData.stations)
    ? vulnerabilityStationsData.stations
    : [];
  const segmentRows = [...segments]
    .sort((a, b) => b.avg_delay_incr - a.avg_delay_incr)
    .slice(0, 5)
    .map((segment, index) =>
      createSegmentRankingRow(segment, index, vulnerabilitySegmentsData.line || "-"),
    );
  const stationRows = [...stations]
    .sort((a, b) => b.delay_rate - a.delay_rate)
    .slice(0, 5)
    .map((station, index) =>
      createStationRankingRow(station, index, vulnerabilityStationsData.line || "-"),
    );

  if (rankingElements.segmentBody) {
    rankingElements.segmentBody.replaceChildren(
      ...(segmentRows.length > 0 ? segmentRows : [createEmptyRankingRow("위험 구간 데이터가 없습니다.", 5)]),
    );
  }

  if (rankingElements.stationBody) {
    rankingElements.stationBody.replaceChildren(
      ...(stationRows.length > 0 ? stationRows : [createEmptyRankingRow("위험 역 데이터가 없습니다.", 5)]),
    );
  }
}

function getAlertLabelFromReason(reason) {
  if (!reason) {
    return "-";
  }

  const match = reason.match(/^(.*?)\s시/);

  return match ? match[1].replace(/\s/g, "") : "-";
}

function renderInspectionDetail(item, stations = []) {
  if (!inspectionElements.detail) {
    return;
  }

  const riskLevel = item.risk_level || "none";
  const stationName = getStationNameFromInspectionItem(item, stations);
  const stationId = getStationByName(stationName, stations)?.station_id;
  const segmentId = item.target_type === "segment" ? item.segment_id : null;
  const title = document.createElement("h3");
  const list = document.createElement("dl");
  const fields = [
    ["대상", item.target || "-"],
    ["위험도", (RISK_LEVELS[riskLevel] || RISK_LEVELS.none).label],
    ["기상특보", getAlertLabelFromReason(item.reason)],
    ["주요 위험", item.reason || "-"],
    ["평균 지연 증가", Number.isFinite(item.avg_delay_incr) ? `+${item.avg_delay_incr.toFixed(1)}분` : "-"],
    ["분석 표본", Number.isFinite(item.sample_n) ? `${item.sample_n}건` : "-"],
  ];

  title.className = "inspection-detail-panel__title";
  title.textContent = `${item.target || "점검 대상"} 상세`;
  list.className = "inspection-detail-panel__list";

  fields.forEach(([label, value]) => {
    const term = document.createElement("dt");
    const description = document.createElement("dd");

    term.textContent = label;

    if (label === "대상" && stationName) {
      description.append(createStationDetailLink(stationName, value, stationId));
    } else if (label === "대상" && segmentId) {
      description.append(createRouteDetailLink(segmentId, value));
    } else {
      description.textContent = value;
    }

    list.append(term, description);
  });

  inspectionElements.detail.replaceChildren(title, list);
}

function setSelectedInspectionRow(selectedRow) {
  if (!inspectionElements.body) {
    return;
  }

  inspectionElements.body.querySelectorAll("tr").forEach((row) => {
    const isSelected = row === selectedRow;

    row.classList.toggle("inspection-table__row--selected", isSelected);
    row.setAttribute("aria-selected", String(isSelected));
  });
}

function createInspectionTargetCell(item, stations) {
  const cell = document.createElement("td");
  const stationName = getStationNameFromInspectionItem(item, stations);
  const stationId = getStationByName(stationName, stations)?.station_id;
  const segmentId = item.target_type === "segment" ? item.segment_id : null;

  cell.className = "inspection-table__target";

  if (stationName) {
    cell.append(createStationDetailLink(stationName, item.target, stationId));
    return cell;
  }

  if (segmentId) {
    cell.append(createRouteDetailLink(segmentId, item.target));
    return cell;
  }

  cell.textContent = item.target;

  return cell;
}

function createInspectionRow(item, stations) {
  const row = document.createElement("tr");
  const riskLevel = item.risk_level || "none";
  const riskCell = document.createElement("td");
  const detailCell = document.createElement("td");
  const detailButton = document.createElement("button");
  const targetId = item.station_id || item.segment_id;

  if (item.target_type) {
    row.dataset.targetType = item.target_type;
  }

  if (targetId) {
    row.dataset.targetId = targetId;
  }

  riskCell.append(createRiskBadge(riskLevel));
  detailButton.className = "inspection-table__button";
  detailButton.type = "button";
  detailButton.textContent = "상세보기";
  detailButton.setAttribute("aria-label", `${item.target} 상세보기`);
  detailButton.addEventListener("click", () => {
    renderInspectionDetail(item, stations);
    setSelectedInspectionRow(row);
  });
  detailCell.append(detailButton);

  row.append(
    riskCell,
    createInspectionTargetCell(item, stations),
    createRankingCell(getAlertLabelFromReason(item.reason)),
    createRankingCell(item.reason || "-"),
    detailCell,
  );

  return row;
}

function renderEmptyInspectionTable() {
  if (!inspectionElements.body) {
    return;
  }

  inspectionElements.body.replaceChildren(createTableMessageRow("우선 점검 대상 데이터가 없습니다.", 5));

  if (inspectionElements.detail) {
    const title = document.createElement("h3");
    const description = document.createElement("p");

    title.className = "inspection-detail-panel__title";
    title.textContent = "점검 상세";
    description.className = "inspection-detail-panel__description";
    description.textContent = "표시할 우선 점검 대상 데이터가 없습니다.";
    inspectionElements.detail.replaceChildren(title, description);
  }
}

function renderInspectionTable(checklistData, vulnerabilityStationsData) {
  if (!inspectionElements.body) {
    return;
  }

  const stations = getStationsFromData(vulnerabilityStationsData);
  const items = getChecklistItems(checklistData)
    .slice()
    .sort((a, b) => a.rank - b.rank);
  const rows = items.map((item) => createInspectionRow(item, stations));

  inspectionElements.body.replaceChildren(
    ...(rows.length > 0 ? rows : [createTableMessageRow("우선 점검 대상 데이터가 없습니다.", 5)]),
  );

  if (items.length > 0) {
    renderInspectionDetail(items[0], stations);
    setSelectedInspectionRow(rows[0]);
  }
}

function getSelectedFilterValues() {
  return normalizeDashboardFilters({
    line: filterElements.lineSelect?.value,
    alertType: filterElements.alertTypeSelect?.value,
    alertLevel: filterElements.alertLevelSelect?.value,
    trainType: filterElements.trainTypeSelect?.value,
  });
}

function normalizeFilterValue(value, fallback) {
  const normalizedValue = String(value || "").trim();

  if (!normalizedValue || normalizedValue === "전체") {
    return fallback;
  }

  return normalizedValue;
}

function normalizeDashboardFilters(filters = {}) {
  return {
    line: normalizeFilterValue(filters.line, DEFAULT_DASHBOARD_FILTERS.line),
    alertType: normalizeFilterValue(filters.alertType, DEFAULT_DASHBOARD_FILTERS.alertType),
    alertLevel: normalizeFilterValue(filters.alertLevel, DEFAULT_DASHBOARD_FILTERS.alertLevel),
    trainType: normalizeFilterValue(filters.trainType, DEFAULT_DASHBOARD_FILTERS.trainType),
  };
}

function createDashboardFilterQuery(filters) {
  const normalizedFilters = normalizeDashboardFilters(filters);
  const params = new URLSearchParams();

  Object.entries(FILTER_QUERY_PARAM_NAMES).forEach(([filterName, queryParamName]) => {
    const value = normalizedFilters[filterName];
    // "all"(전체)은 파라미터를 아예 넘기지 않는다.
    // API 는 허용값(호우/폭염, 주의보/경보)만 받아 "all" 을 주면 400 이고,
    // 생략하면 전체를 합쳐서 준다.
    if (isAllFilterValue(value)) {
      return;
    }
    params.set(queryParamName, value);
  });

  return params.toString();
}

// 필터를 붙인 URL. 쿼리가 비면(전체) 기본 경로 그대로.
function withFilterQuery(baseUrl, query, allowedParams) {
  if (!query) {
    return baseUrl;
  }
  const source = new URLSearchParams(query);
  const params = new URLSearchParams();
  allowedParams.forEach((name) => {
    // 엔드포인트마다 받는 파라미터가 다르다. 안 받는 걸 넘기면 무시되거나 400 이다.
    if (source.has(name)) {
      params.set(name, source.get(name));
    }
  });
  const qs = params.toString();
  return qs ? `${baseUrl}?${qs}` : baseUrl;
}

function isAllFilterValue(value) {
  return !value || value === ALL_FILTER_VALUE || value === "전체";
}

function isMatchingLine(dataLine, selectedLine) {
  return isAllFilterValue(selectedLine) || dataLine === selectedLine;
}

function isMatchingAlertType(alertType, selectedAlertType) {
  return isAllFilterValue(selectedAlertType) || alertType === selectedAlertType;
}

function isMatchingAlertLevel(alertLevel, selectedAlertLevel) {
  return isAllFilterValue(selectedAlertLevel) || alertLevel === selectedAlertLevel;
}

function includesFilterText(sourceText, filterText) {
  return isAllFilterValue(filterText) || String(sourceText || "").includes(filterText);
}

function filterAlertsData(alertsData, filters) {
  const activeAlerts = Array.isArray(alertsData.active) ? alertsData.active : [];

  if (!isMatchingLine(alertsData.line, filters.line)) {
    return { ...alertsData, active: [] };
  }

  return {
    ...alertsData,
    active: activeAlerts.filter((alert) =>
      isMatchingAlertType(alert.alert_type, filters.alertType)
      && isMatchingAlertLevel(alert.alert_level, filters.alertLevel),
    ),
  };
}

function filterChecklistData(checklistData, filters) {
  const items = getChecklistItems(checklistData);

  if (!isMatchingLine(checklistData.line, filters.line)) {
    return { ...checklistData, items: [] };
  }

  return {
    ...checklistData,
    items: items.filter((item) =>
      includesFilterText(item.reason, filters.alertType)
      && includesFilterText(item.reason, filters.alertLevel),
    ),
  };
}

function filterVulnerabilitySegmentsData(vulnerabilitySegmentsData, filters) {
  const segments = Array.isArray(vulnerabilitySegmentsData.segments)
    ? vulnerabilitySegmentsData.segments
    : [];
  const isMatched =
    isMatchingLine(vulnerabilitySegmentsData.line, filters.line)
    && isMatchingAlertType(vulnerabilitySegmentsData.alert_type, filters.alertType)
    && isMatchingAlertLevel(vulnerabilitySegmentsData.alert_level, filters.alertLevel);

  return {
    ...vulnerabilitySegmentsData,
    segments: isMatched ? segments : [],
  };
}

function filterVulnerabilityStationsData(vulnerabilityStationsData, filters) {
  const stations = Array.isArray(vulnerabilityStationsData.stations)
    ? vulnerabilityStationsData.stations
    : [];
  const isMatched =
    isMatchingLine(vulnerabilityStationsData.line, filters.line)
    && isMatchingAlertType(vulnerabilityStationsData.alert_type, filters.alertType)
    && isMatchingAlertLevel(vulnerabilityStationsData.alert_level, filters.alertLevel);

  return {
    ...vulnerabilityStationsData,
    stations: isMatched ? stations : [],
  };
}

function filterHeatmapData(heatmapData, filters) {
  if (isMatchingLine(heatmapData.line, filters.line)) {
    return heatmapData;
  }

  return {
    ...heatmapData,
    nodes: [],
    edges: [],
  };
}

function getFilteredDashboardData(state, filters) {
  return {
    alertsData: filterAlertsData(state.alertsData, filters),
    checklistData: filterChecklistData(state.checklistData, filters),
    vulnerabilitySegmentsData: filterVulnerabilitySegmentsData(
      state.vulnerabilitySegmentsData,
      filters,
    ),
    vulnerabilityStationsData: filterVulnerabilityStationsData(
      state.vulnerabilityStationsData,
      filters,
    ),
    heatmapData: filterHeatmapData(state.heatmapData, filters),
  };
}

function renderDashboardData(data) {
  renderAlertBanner(data.alertsData);
  renderSummaryCards(
    data.alertsData,
    data.checklistData,
    data.vulnerabilitySegmentsData,
    data.heatmapData,
  );
  renderHeatmap(data.heatmapData, data.alertsData.updated_at, data.vulnerabilityStationsData);
  renderRankings(data.vulnerabilitySegmentsData, data.vulnerabilityStationsData);
  renderInspectionTable(data.checklistData, data.vulnerabilityStationsData);
}

// 필터가 걸린 데이터를 API 에서 새로 받아 dashboardState 를 갱신한다.
//
// 왜 재호출이 필요한가(리뷰 3.8):
//   API 응답은 이미 그 조합으로 집계된 결과다. 예를 들어 /vulnerability/stations 는
//   {alert_type, alert_level, stations[]} 를 주지 특보별 내역을 주지 않는다.
//   따라서 받아온 데이터를 프론트에서 다시 특보별로 거르는 건 불가능하다.
//   필터를 바꾸면 서버에서 그 조합으로 다시 받아야 한다.
async function fetchFilteredDashboardData(query) {
  const [vulnerabilitySegmentsData, vulnerabilityStationsData, heatmapData] = await Promise.all([
    // 엔드포인트마다 받는 파라미터가 다르다(히트맵은 등급·열차종을 안 받는다).
    fetchJson(withFilterQuery(VULNERABILITY_SEGMENTS_MOCK_URL, query, ["alert_type", "alert_level", "train_type"])),
    fetchJson(withFilterQuery(VULNERABILITY_STATIONS_MOCK_URL, query, ["alert_type", "alert_level"])),
    fetchJson(withFilterQuery(HEATMAP_MOCK_URL, query, ["alert_type"])),
  ]);

  return { vulnerabilitySegmentsData, vulnerabilityStationsData, heatmapData };
}

async function renderFilteredDashboard() {
  if (!dashboardState) {
    return;
  }

  const filters = getSelectedFilterValues();
  const query = createDashboardFilterQuery(filters);

  dashboardState.activeFilters = filters;
  dashboardState.filterQuery = query;

  try {
    const fresh = await fetchFilteredDashboardData(query);
    Object.assign(dashboardState, fresh);
  } catch (error) {
    // 재호출이 실패해도 화면을 비우지 않는다 — 직전 데이터로 계속 그린다.
    console.error("필터 적용 중 데이터를 새로 받지 못했습니다.", error);
  }

  // 노선 필터는 서버가 이미 처리하지만, 클라이언트 필터도 그대로 둔다(중복 적용은 무해).
  renderDashboardData(getFilteredDashboardData(dashboardState, filters));
}

async function renderUnfilteredDashboard() {
  if (!dashboardState) {
    return;
  }

  const filters = { ...DEFAULT_DASHBOARD_FILTERS };
  const query = createDashboardFilterQuery(filters);   // 전체 → 빈 문자열

  dashboardState.activeFilters = filters;
  dashboardState.filterQuery = query;

  try {
    const fresh = await fetchFilteredDashboardData(query);
    Object.assign(dashboardState, fresh);
  } catch (error) {
    console.error("필터 초기화 중 데이터를 새로 받지 못했습니다.", error);
  }

  renderDashboardData(dashboardState);
}

function initializeDashboardFilters() {
  if (!filterElements.form) {
    return;
  }

  filterElements.form.addEventListener("submit", (event) => {
    event.preventDefault();
    renderFilteredDashboard();
  });

  filterElements.form.addEventListener("reset", () => {
    window.setTimeout(renderUnfilteredDashboard, 0);
  });
}

async function fetchJson(url) {
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`Mock 데이터를 불러오지 못했습니다. status: ${response.status}`);
  }

  return response.json();
}

async function initializeDashboard() {
  try {
    const [
      alertsData,
      linesData,
      checklistData,
      vulnerabilitySegmentsData,
      vulnerabilityStationsData,
      heatmapData,
    ] = await Promise.all([
      fetchJson(ALERTS_MOCK_URL),
      fetchJson(LINES_MOCK_URL),
      fetchJson(CHECKLIST_MOCK_URL),
      fetchJson(VULNERABILITY_SEGMENTS_MOCK_URL),
      fetchJson(VULNERABILITY_STATIONS_MOCK_URL),
      fetchJson(HEATMAP_MOCK_URL),
    ]);

    dashboardState = {
      alertsData,
      linesData,
      checklistData,
      vulnerabilitySegmentsData,
      vulnerabilityStationsData,
      heatmapData,
    };

    renderLineSelect(linesData);
    renderDashboardFilterOptions(dashboardState);
    initializeAlertRegionTooltips();
    initializeDashboardFilters();
    renderUnfilteredDashboard();
  } catch (error) {
    console.error(error);
    updateRecentUpdatedTime(null);
    renderEmptyAlertBanner();
    renderEmptyLineSelect();
    renderEmptyDashboardFilterOptions();
    renderEmptySummaryCards();
    renderEmptyHeatmap();
    renderEmptyRankings();
    renderEmptyInspectionTable();
  }
}

initializeDashboard();
