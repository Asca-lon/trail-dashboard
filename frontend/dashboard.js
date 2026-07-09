const ALERTS_MOCK_URL = "../mock/alerts_active.json";
const LINES_MOCK_URL = "../mock/lines.json";
const CHECKLIST_MOCK_URL = "../mock/checklist.json";
const VULNERABILITY_SEGMENTS_MOCK_URL = "../mock/vulnerability_segments.json";
const VULNERABILITY_STATIONS_MOCK_URL = "../mock/vulnerability_stations.json";
const HEATMAP_MOCK_URL = "../mock/heatmap.json";

const HIGH_DELAY_THRESHOLD_MINUTES = 12;
const HIGH_VULNERABILITY_THRESHOLD = 0.7;
const WARNING_VULNERABILITY_THRESHOLD = 0.5;

const RISK_LEVELS = {
  high: { label: "높음", color: "#EF4444" },
  warning: { label: "주의", color: "#F59E0B" },
  interest: { label: "관심", color: "#22C55E" },
  none: { label: "-", color: "#D1D5DB" },
};

const STATION_DETAIL_URL = "./station-detail.html";
const STATION_QUERY_PARAM = "station";
const STATION_ID_QUERY_PARAM = "station_id";

const alertElements = {
  updatedTime: document.querySelector("[data-dashboard-updated-time]"),
  banner: document.querySelector("[data-dashboard-alert-banner]"),
  badge: document.querySelector("[data-dashboard-alert-badge]"),
  text: document.querySelector("[data-dashboard-alert-text]"),
  standardTime: document.querySelector("[data-dashboard-alert-standard-time]"),
  count: document.querySelector("[data-dashboard-alert-count]"),
};

const filterElements = {
  lineSelect: document.querySelector("[data-dashboard-line-select]"),
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

function getRegionSummary(activeAlerts) {
  const regions = [...new Set(activeAlerts.map((alert) => alert.region_name).filter(Boolean))];

  if (regions.length === 0) {
    return "영향 지역 정보 없음";
  }

  if (regions.length === 1) {
    return regions[0];
  }

  return `${regions[0]} 외 ${regions.length - 1}개 지역`;
}

function getAffectedSegmentCount(activeAlerts) {
  return activeAlerts.reduce((total, alert) => {
    const affected = Array.isArray(alert.affected) ? alert.affected : [];
    const segmentCount = affected.filter((item) => item.type === "segment").length;

    return total + segmentCount;
  }, 0);
}

function getChecklistItems(checklistData) {
  return Array.isArray(checklistData.items) ? checklistData.items : [];
}

function getAverageDelayIncrease(checklistData) {
  const delayValues = getChecklistItems(checklistData)
    .map((item) => item.avg_delay_incr)
    .filter((value) => Number.isFinite(value));

  if (delayValues.length === 0) {
    return null;
  }

  const total = delayValues.reduce((sum, value) => sum + value, 0);

  return total / delayValues.length;
}

function getHighRiskSegmentCount(segmentsData) {
  const segments = Array.isArray(segmentsData.segments) ? segmentsData.segments : [];

  return segments.filter((segment) => segment.avg_delay_incr >= HIGH_DELAY_THRESHOLD_MINUTES).length;
}

function getRiskLevelByVulnerability(vulnerability) {
  if (!Number.isFinite(vulnerability)) {
    return "none";
  }

  if (vulnerability >= HIGH_VULNERABILITY_THRESHOLD) {
    return "high";
  }

  if (vulnerability >= WARNING_VULNERABILITY_THRESHOLD) {
    return "warning";
  }

  return "interest";
}

function getRiskLevelByDelayIncrease(delayIncrease) {
  if (!Number.isFinite(delayIncrease)) {
    return "none";
  }

  if (delayIncrease >= HIGH_DELAY_THRESHOLD_MINUTES) {
    return "high";
  }

  if (delayIncrease >= 7) {
    return "warning";
  }

  return "interest";
}

function updateRecentUpdatedTime(updatedAt) {
  if (!alertElements.updatedTime) {
    return;
  }

  alertElements.updatedTime.dateTime = updatedAt || "";
  alertElements.updatedTime.textContent = formatDateTime(updatedAt);
}

function renderEmptyAlertBanner() {
  if (alertElements.badge) {
    alertElements.badge.textContent = "특보 없음";
  }

  if (alertElements.text) {
    alertElements.text.firstChild.textContent = "현재 발효 중인 기상특보가 없습니다. ";
  }

  if (alertElements.standardTime) {
    alertElements.standardTime.textContent = "영향 가능 철도 구간";
  }

  if (alertElements.count) {
    alertElements.count.textContent = "0개";
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

  const primaryAlert = activeAlerts[0];
  const badgeText = `${primaryAlert.alert_type || "특보"} ${primaryAlert.alert_level || ""}`.trim();
  const regionSummary = getRegionSummary(activeAlerts);
  const affectedSegmentCount = getAffectedSegmentCount(activeAlerts);

  if (alertElements.badge) {
    alertElements.badge.textContent = badgeText;
  }

  if (alertElements.text) {
    alertElements.text.firstChild.textContent = `${regionSummary} `;
  }

  if (alertElements.standardTime) {
    alertElements.standardTime.textContent = formatStandardTime(alertsData.updated_at);
  }

  if (alertElements.count) {
    alertElements.count.textContent = `${affectedSegmentCount}개`;
  }

  if (alertElements.banner) {
    alertElements.banner.setAttribute(
      "aria-label",
      `현재 발효 중인 기상특보 ${badgeText}, ${regionSummary}, 영향 가능 철도 구간 ${affectedSegmentCount}개`,
    );
  }
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
    "mock 데이터 없음",
    "영향 가능 구간 데이터 없음",
  );
  setSummaryCard(
    summaryCardElements.delayedTrains,
    "-",
    "편",
    "mock 데이터 없음",
    "운행 지연 예상 열차 데이터 없음",
  );
  setSummaryCard(
    summaryCardElements.averageDelay,
    "-",
    "분",
    "mock 데이터 없음",
    "평균 지연 시간 데이터 없음",
  );
  setSummaryCard(
    summaryCardElements.highRiskSegments,
    "0",
    "개",
    "mock 데이터 없음",
    "취약도 높음 구간 데이터 없음",
  );
}

function renderSummaryCards(alertsData, checklistData, vulnerabilitySegmentsData) {
  const activeAlerts = Array.isArray(alertsData.active) ? alertsData.active : [];
  const affectedSegmentCount = getAffectedSegmentCount(activeAlerts);
  const averageDelayIncrease = getAverageDelayIncrease(checklistData);
  const highRiskSegmentCount = getHighRiskSegmentCount(vulnerabilitySegmentsData);
  const averageDelayText =
    averageDelayIncrease === null ? "-" : averageDelayIncrease.toFixed(1);

  setSummaryCard(
    summaryCardElements.affectedSegments,
    String(affectedSegmentCount),
    "개",
    "발효 특보 기준",
    `영향 가능 구간 ${affectedSegmentCount}개, 발효 특보 기준`,
  );
  setSummaryCard(
    summaryCardElements.delayedTrains,
    "-",
    "편",
    "mock 데이터 없음",
    "운행 지연 예상 열차 데이터 없음",
  );
  setSummaryCard(
    summaryCardElements.averageDelay,
    averageDelayText,
    "분",
    "우선 점검 대상 평균",
    `평균 지연 시간 예상 ${averageDelayText}분, 우선 점검 대상 평균`,
  );
  setSummaryCard(
    summaryCardElements.highRiskSegments,
    String(highRiskSegmentCount),
    "개",
    `${HIGH_DELAY_THRESHOLD_MINUTES}분 이상 기준`,
    `취약도 높음 구간 ${highRiskSegmentCount}개, ${HIGH_DELAY_THRESHOLD_MINUTES}분 이상 기준`,
  );
}

function createRouteMapItem(node) {
  const riskLevel = getRiskLevelByVulnerability(node.vuln);
  const risk = RISK_LEVELS[riskLevel];
  const item = document.createElement("li");
  const station = document.createElement("span");
  const marker = document.createElement("span");
  const dash = document.createElement("span");
  const status = document.createElement("span");
  const chevron = document.createElement("span");

  item.className = `route-map__item route-map__item--${riskLevel}`;
  item.setAttribute("aria-label", `${node.station} 취약도 ${risk.label}`);

  station.className = "route-map__station";
  station.textContent = node.station;

  marker.className = "route-map__marker";
  dash.className = "route-map__dash";

  status.className = "route-map__status";
  status.textContent = risk.label;

  chevron.className = "route-map__chevron";
  chevron.textContent = "›";

  item.append(station, marker, dash, status, chevron);

  return item;
}

function countHeatmapEdgesByRiskLevel(edges) {
  return edges.reduce(
    (counts, edge) => {
      const riskLevel = getRiskLevelByVulnerability(edge.vuln);
      counts[riskLevel] += 1;

      return counts;
    },
    { high: 0, warning: 0, interest: 0, none: 0 },
  );
}

function buildRouteRiskGradient(nodes) {
  if (nodes.length === 0) {
    return RISK_LEVELS.none.color;
  }

  const step = 100 / nodes.length;
  const stops = nodes.flatMap((node, index) => {
    const riskLevel = getRiskLevelByVulnerability(node.vuln);
    const color = RISK_LEVELS[riskLevel].color;
    const start = (step * index).toFixed(2);
    const end = (step * (index + 1)).toFixed(2);

    return [`${color} ${start}%`, `${color} ${end}%`];
  });

  return `linear-gradient(180deg, ${stops.join(", ")})`;
}

function renderEmptyHeatmap() {
  if (heatmapElements.title) {
    heatmapElements.title.textContent = "기상 취약도 현황";
  }

  if (heatmapElements.routeMap) {
    heatmapElements.routeMap.setAttribute("aria-label", "역별 취약도 데이터 없음");
  }

  if (heatmapElements.routeList) {
    heatmapElements.routeList.replaceChildren();
    heatmapElements.routeList.style.setProperty("--route-risk-gradient", RISK_LEVELS.none.color);
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

function renderHeatmap(heatmapData, updatedAt) {
  const nodes = Array.isArray(heatmapData.nodes) ? heatmapData.nodes : [];
  const edges = Array.isArray(heatmapData.edges) ? heatmapData.edges : [];
  const lineName = heatmapData.line || "노선";
  const edgeCounts = countHeatmapEdgesByRiskLevel(edges);

  if (nodes.length === 0) {
    renderEmptyHeatmap();
    return;
  }

  if (heatmapElements.title) {
    heatmapElements.title.textContent = `${lineName} 기상 취약도 현황`;
  }

  if (heatmapElements.routeMap) {
    heatmapElements.routeMap.setAttribute("aria-label", `${lineName} 역별 취약도`);
  }

  if (heatmapElements.routeList) {
    heatmapElements.routeList.replaceChildren(...nodes.map(createRouteMapItem));
    heatmapElements.routeList.style.setProperty("--route-risk-gradient", buildRouteRiskGradient(nodes));
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
    rankingElements.segmentBody.replaceChildren(createEmptyRankingRow("취약 구간 데이터가 없습니다.", 5));
  }

  if (rankingElements.stationBody) {
    rankingElements.stationBody.replaceChildren(createEmptyRankingRow("취약 역 데이터가 없습니다.", 5));
  }
}

function createSegmentRankingRow(segment, index, lineName) {
  const row = document.createElement("tr");
  const riskLevel = getRiskLevelByDelayIncrease(segment.avg_delay_incr);
  const riskCell = document.createElement("td");

  if (segment.segment_id) {
    row.dataset.segmentId = segment.segment_id;
  }

  riskCell.append(createRiskBadge(riskLevel));
  row.append(
    createRankingCell(String(index + 1)),
    createRankingCell(`${segment.from}-${segment.to}`, "ranking-table__target"),
    createRankingCell(lineName),
    riskCell,
    createRankingCell(segment.avg_delay_incr.toFixed(1), "ranking-table__number"),
  );

  return row;
}

function createStationRankingRow(station, index, lineName) {
  const row = document.createElement("tr");
  const riskLevel = getRiskLevelByVulnerability(station.delay_rate);
  const riskCell = document.createElement("td");

  riskCell.append(createRiskBadge(riskLevel));
  row.append(
    createRankingCell(String(index + 1)),
    createStationLinkCell(station.station, station.station_id),
    createRankingCell(lineName),
    riskCell,
    createRankingCell(String(station.sample_n ?? "-"), "ranking-table__number"),
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
      ...(segmentRows.length > 0 ? segmentRows : [createEmptyRankingRow("취약 구간 데이터가 없습니다.", 5)]),
    );
  }

  if (rankingElements.stationBody) {
    rankingElements.stationBody.replaceChildren(
      ...(stationRows.length > 0 ? stationRows : [createEmptyRankingRow("취약 역 데이터가 없습니다.", 5)]),
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

function getInspectionRecommendation(riskLevel) {
  if (riskLevel === "high") {
    return "즉시 현장 점검 및 운행 관리 강화";
  }

  if (riskLevel === "warning") {
    return "시설 및 선로 사전 점검";
  }

  return "상황 모니터링";
}

function renderInspectionDetail(item, stations = []) {
  if (!inspectionElements.detail) {
    return;
  }

  const riskLevel = getRiskLevelByDelayIncrease(item.avg_delay_incr);
  const stationName = getStationNameFromInspectionItem(item, stations);
  const stationId = getStationByName(stationName, stations)?.station_id;
  const title = document.createElement("h3");
  const list = document.createElement("dl");
  const fields = [
    ["대상", item.target || "-"],
    ["위험도", RISK_LEVELS[riskLevel].label],
    ["기상특보", getAlertLabelFromReason(item.reason)],
    ["주요 위험", item.reason || "-"],
    ["평균 지연 증가", Number.isFinite(item.avg_delay_incr) ? `+${item.avg_delay_incr.toFixed(1)}분` : "-"],
    ["분석 표본", Number.isFinite(item.sample_n) ? `${item.sample_n}건` : "-"],
    ["대응 권고", getInspectionRecommendation(riskLevel)],
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

  cell.className = "inspection-table__target";

  if (stationName) {
    cell.append(createStationDetailLink(stationName, item.target, stationId));
    return cell;
  }

  cell.textContent = item.target;

  return cell;
}

function createInspectionRow(item, stations) {
  const row = document.createElement("tr");
  const riskLevel = getRiskLevelByDelayIncrease(item.avg_delay_incr);
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
    createRankingCell(getInspectionRecommendation(riskLevel)),
    detailCell,
  );

  return row;
}

function renderEmptyInspectionTable() {
  if (!inspectionElements.body) {
    return;
  }

  inspectionElements.body.replaceChildren(createTableMessageRow("우선 점검 대상 데이터가 없습니다.", 6));

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
    ...(rows.length > 0 ? rows : [createTableMessageRow("우선 점검 대상 데이터가 없습니다.", 6)]),
  );

  if (items.length > 0) {
    renderInspectionDetail(items[0], stations);
    setSelectedInspectionRow(rows[0]);
  }
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

    renderAlertBanner(alertsData);
    renderLineSelect(linesData);
    renderSummaryCards(alertsData, checklistData, vulnerabilitySegmentsData);
    renderHeatmap(heatmapData, alertsData.updated_at);
    renderRankings(vulnerabilitySegmentsData, vulnerabilityStationsData);
    renderInspectionTable(checklistData, vulnerabilityStationsData);
  } catch (error) {
    console.error(error);
    updateRecentUpdatedTime(null);
    renderEmptyAlertBanner();
    renderEmptyLineSelect();
    renderEmptySummaryCards();
    renderEmptyHeatmap();
    renderEmptyRankings();
    renderEmptyInspectionTable();
  }
}

initializeDashboard();
