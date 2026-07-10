const STATION_DETAIL_MOCK_URL = "../mock/station_details.json";
const VULNERABILITY_STATIONS_MOCK_URL = "../mock/vulnerability_stations.json";
const STATION_QUERY_PARAM = "station";
const STATION_ID_QUERY_PARAM = "station_id";

const HIGH_DELAY_RATE_THRESHOLD = 0.4;
const WARNING_DELAY_RATE_THRESHOLD = 0.25;
const LINE_CHART_MAX_VALUE = 40;
const LINE_CHART_MIN_X = 42;
const LINE_CHART_MAX_X = 590;
const LINE_CHART_MIN_Y = 24;
const LINE_CHART_MAX_Y = 192;
const BAR_CHART_MAX_VALUE = 30;
const BAR_CHART_MAX_HEIGHT = 180;
const BAR_CHART_MIN_HEIGHT = 8;

const RISK_LABELS = {
  high: "높음",
  warning: "주의",
  interest: "관심",
  none: "정보 없음",
};

const STATION_ADDRESS_BY_NAME = {
  대전: "대전광역시 동구 중앙로 215",
};

const stationInfoElements = {
  name: document.querySelector("[data-station-detail-name]"),
  line: document.querySelector("[data-station-detail-line]"),
  address: document.querySelector("[data-station-detail-address]"),
  riskCard: document.querySelector("[data-station-detail-risk-card]"),
  riskTitle: document.querySelector("[data-station-detail-risk-title]"),
  riskText: document.querySelector("[data-station-detail-risk-text]"),
};

const metricElements = {
  avgDelay: document.querySelector('[data-station-detail-metric="avg-delay"]'),
  deltaDelay: document.querySelector('[data-station-detail-metric="delta-delay"]'),
  delayRate: document.querySelector('[data-station-detail-metric="delay-rate"]'),
  stopRate: document.querySelector('[data-station-detail-metric="stop-rate"]'),
};

const alertTableElements = {
  body: document.querySelector("[data-station-detail-alert-table-body]"),
};

const historyElements = {
  list: document.querySelector("[data-station-detail-history-list]"),
};

const chartElements = {
  lineChart: document.querySelector("[data-station-detail-line-chart]"),
  lineWeekday: document.querySelector("[data-station-detail-line-weekday]"),
  lineHoliday: document.querySelector("[data-station-detail-line-holiday]"),
  linePoint: document.querySelector("[data-station-detail-line-point]"),
  lineTooltipBox: document.querySelector("[data-station-detail-line-tooltip-box]"),
  lineTooltip: document.querySelector("[data-station-detail-line-tooltip]"),
  alertComparisonChart: document.querySelector("[data-station-detail-alert-comparison-chart]"),
};

const stationSelectionElements = {
  toggleButton: document.querySelector("[data-station-select-toggle]"),
  selector: document.querySelector("[data-station-selector]"),
  select: document.querySelector("[data-station-select]"),
};

function getRiskLevelByDelayRate(delayRate) {
  if (!Number.isFinite(delayRate)) {
    return "none";
  }

  if (delayRate >= HIGH_DELAY_RATE_THRESHOLD) {
    return "high";
  }

  if (delayRate >= WARNING_DELAY_RATE_THRESHOLD) {
    return "warning";
  }

  return "interest";
}

function formatStationName(stationName) {
  if (!stationName) {
    return "역 정보 없음";
  }

  return stationName.endsWith("역") ? stationName : `${stationName}역`;
}

function formatStationAddress(stationName) {
  return STATION_ADDRESS_BY_NAME[stationName] || "주소 정보 없음(mock 미제공)";
}

function formatPercent(rate) {
  if (!Number.isFinite(rate)) {
    return "-";
  }

  return (rate * 100).toFixed(1);
}

function formatSignedNumber(value) {
  if (!Number.isFinite(value)) {
    return "-";
  }

  return `+${value.toFixed(1)}`;
}

function getLineChartPoint(item, index, itemCount, valueKey) {
  const safeCount = Math.max(itemCount - 1, 1);
  const value = Number.isFinite(item[valueKey]) ? item[valueKey] : 0;
  const x = LINE_CHART_MIN_X + ((LINE_CHART_MAX_X - LINE_CHART_MIN_X) / safeCount) * index;
  const clampedValue = Math.max(0, Math.min(value, LINE_CHART_MAX_VALUE));
  const y = LINE_CHART_MAX_Y - (clampedValue / LINE_CHART_MAX_VALUE) * (LINE_CHART_MAX_Y - LINE_CHART_MIN_Y);

  return {
    x: Number(x.toFixed(1)),
    y: Number(y.toFixed(1)),
    value,
  };
}

function getLineChartPoints(hourlyDelayData, valueKey) {
  return hourlyDelayData.map((item, index) => getLineChartPoint(item, index, hourlyDelayData.length, valueKey));
}

function toPolylinePoints(points) {
  return points.map((point) => `${point.x},${point.y}`).join(" ");
}

function getBarHeight(value) {
  if (!Number.isFinite(value)) {
    return BAR_CHART_MIN_HEIGHT;
  }

  return Math.max(
    BAR_CHART_MIN_HEIGHT,
    Math.min((value / BAR_CHART_MAX_VALUE) * BAR_CHART_MAX_HEIGHT, BAR_CHART_MAX_HEIGHT),
  );
}

function setMetricCard(card, value, unit, comparisonLabel, comparisonValue, ariaLabel) {
  if (!card) {
    return;
  }

  const valueElement = card.querySelector("[data-station-detail-metric-value]");
  const unitElement = card.querySelector("[data-station-detail-metric-unit]");
  const comparisonElement = card.querySelector("[data-station-detail-metric-comparison]");

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
      const strong = document.createElement("strong");

      strong.textContent = comparisonValue;
      comparisonElement.append(strong);
    }
  }

  card.setAttribute("aria-label", ariaLabel);
}

function renderEmptyStationDetail() {
  if (stationInfoElements.name) {
    stationInfoElements.name.textContent = "역 정보 없음";
  }

  if (stationInfoElements.line) {
    stationInfoElements.line.textContent = "노선 정보 없음";
  }

  if (stationInfoElements.riskTitle) {
    stationInfoElements.riskTitle.textContent = "현재 위험도: 정보 없음";
  }

  if (stationInfoElements.riskText) {
    stationInfoElements.riskText.textContent = "기준 정보 없음";
  }

  setMetricCard(metricElements.avgDelay, "-", "분", "mock 데이터", "없음", "평균 지연 시간 데이터 없음");
  setMetricCard(metricElements.deltaDelay, "-", "분", "mock 데이터", "없음", "평균 지연 증가량 데이터 없음");
  setMetricCard(metricElements.delayRate, "-", "%", "mock 데이터", "없음", "지연률 데이터 없음");
  setMetricCard(metricElements.stopRate, "-", "%", "mock 데이터", "없음", "운행 중단률 데이터 없음");
  renderEmptyAlertStatsTable();
  renderEmptyHistoryList();
  renderStationCharts({});
}

function getSelectedStationMetrics(stationName, vulnerabilityStationsData) {
  const stations = Array.isArray(vulnerabilityStationsData.stations)
    ? vulnerabilityStationsData.stations
    : [];

  return stations.find((station) => station.station === stationName) || null;
}

function getStations(vulnerabilityStationsData) {
  return Array.isArray(vulnerabilityStationsData.stations)
    ? vulnerabilityStationsData.stations
    : [];
}

function getStationByName(stationName, vulnerabilityStationsData) {
  return getStations(vulnerabilityStationsData).find((station) => station.station === stationName) || null;
}

function getStationById(stationId, vulnerabilityStationsData) {
  return getStations(vulnerabilityStationsData).find((station) => station.station_id === stationId) || null;
}

function getStationNameById(stationId, vulnerabilityStationsData) {
  return getStationById(stationId, vulnerabilityStationsData)?.station || null;
}

function getStationIdByName(stationName, vulnerabilityStationsData) {
  return getStationByName(stationName, vulnerabilityStationsData)?.station_id || null;
}

function getInitialSelectedStationName(stationDetailData, vulnerabilityStationsData) {
  const stations = getStations(vulnerabilityStationsData);
  const params = new URLSearchParams(window.location.search);
  const stationIdFromUrl = params.get(STATION_ID_QUERY_PARAM);
  const stationNameFromUrl = params.get(STATION_QUERY_PARAM);
  const stationNameById = getStationNameById(stationIdFromUrl, vulnerabilityStationsData);

  if (stationNameById) {
    return stationNameById;
  }

  if (getStationByName(stationNameFromUrl, vulnerabilityStationsData)) {
    return stationNameFromUrl;
  }

  return getStationByName(stationDetailData.station, vulnerabilityStationsData)
    ? stationDetailData.station
    : stations[0]?.station;
}

function updateStationQueryString(stationName, vulnerabilityStationsData) {
  const url = new URL(window.location.href);
  const stationId = getStationIdByName(stationName, vulnerabilityStationsData);

  if (stationId) {
    url.searchParams.set(STATION_ID_QUERY_PARAM, stationId);
    url.searchParams.delete(STATION_QUERY_PARAM);
  } else {
    url.searchParams.set(STATION_QUERY_PARAM, stationName);
    url.searchParams.delete(STATION_ID_QUERY_PARAM);
  }

  window.history.pushState({ stationName, stationId }, "", url);
}

function createSelectedStationDetail(stationDetailData, selectedStationName) {
  const hasStationSpecificDetail = stationDetailData.station === selectedStationName;

  return {
    ...stationDetailData,
    station: selectedStationName,
    by_alert: hasStationSpecificDetail ? stationDetailData.by_alert : [],
    cases: hasStationSpecificDetail ? stationDetailData.cases : [],
    hourly_delay: hasStationSpecificDetail ? stationDetailData.hourly_delay : [],
    alert_delay_comparison: hasStationSpecificDetail ? stationDetailData.alert_delay_comparison : [],
  };
}

function renderStationInfo(stationDetailData, vulnerabilityStationsData, stationMetrics) {
  const stationName = formatStationName(stationDetailData.station);
  const lineName = vulnerabilityStationsData.line || "노선 정보 없음";
  const riskLevel = getRiskLevelByDelayRate(stationMetrics?.delay_rate);
  const riskLabel = RISK_LABELS[riskLevel];
  const alertType = vulnerabilityStationsData.alert_type || "특보";
  const alertLevel = vulnerabilityStationsData.alert_level || "";

  if (stationInfoElements.name) {
    stationInfoElements.name.textContent = stationName;
  }

  if (stationInfoElements.line) {
    stationInfoElements.line.textContent = lineName;
  }

  if (stationInfoElements.address) {
    stationInfoElements.address.textContent = formatStationAddress(stationDetailData.station);
  }

  if (stationInfoElements.riskTitle) {
    stationInfoElements.riskTitle.textContent = `현재 위험도: ${riskLabel}`;
  }

  if (stationInfoElements.riskText) {
    stationInfoElements.riskText.textContent = `${alertType} ${alertLevel}`.trim() + " 기준";
  }

  if (stationInfoElements.riskCard) {
    stationInfoElements.riskCard.setAttribute(
      "aria-label",
      `${stationName} 현재 위험도 ${riskLabel}, ${alertType} ${alertLevel} 기준`,
    );
  }
}

function renderStationMetrics(stationMetrics) {
  setMetricCard(
    metricElements.avgDelay,
    Number.isFinite(stationMetrics?.avg_delay) ? stationMetrics.avg_delay.toFixed(1) : "-",
    "분",
    "mock 기준",
    "평균 지연",
    `평균 지연 시간 ${Number.isFinite(stationMetrics?.avg_delay) ? stationMetrics.avg_delay.toFixed(1) : "-"}분`,
  );
  setMetricCard(
    metricElements.deltaDelay,
    formatSignedNumber(stationMetrics?.delta_delay),
    "분",
    "평상시 대비",
    "증가량",
    `평균 지연 증가량 ${formatSignedNumber(stationMetrics?.delta_delay)}분`,
  );
  setMetricCard(
    metricElements.delayRate,
    formatPercent(stationMetrics?.delay_rate),
    "%",
    "mock 기준",
    "지연률",
    `지연률 ${formatPercent(stationMetrics?.delay_rate)}퍼센트`,
  );
  setMetricCard(
    metricElements.stopRate,
    formatPercent(stationMetrics?.stop_rate),
    "%",
    "mock 기준",
    "운행 중단률",
    `운행 중단률 ${formatPercent(stationMetrics?.stop_rate)}퍼센트`,
  );
}

function getAlertIconPath(alertType) {
  if (alertType === "폭염") {
    return "./assets/icons/sun.svg";
  }

  if (alertType === "강풍") {
    return "./assets/icons/wind.svg";
  }

  if (alertType === "대설") {
    return "./assets/icons/snowflake.svg";
  }

  return "./assets/icons/cloud-rain.svg";
}

function createAlertStatsRow(alertStat) {
  const row = document.createElement("tr");
  const header = document.createElement("th");
  const icon = document.createElement("img");
  const label = document.createElement("span");

  header.scope = "row";
  icon.src = getAlertIconPath(alertStat.alert_type);
  icon.alt = "";
  icon.setAttribute("aria-hidden", "true");
  label.textContent = `${alertStat.alert_type || "특보"} ${alertStat.alert_level || ""}`.trim();
  header.append(icon, label);

  row.append(
    header,
    createTableCell(Number.isFinite(alertStat.sample_n) ? `${alertStat.sample_n} 회` : "-"),
    createTableCell(Number.isFinite(alertStat.avg_delay) ? alertStat.avg_delay.toFixed(1) : "-"),
    createTableCell("-"),
    createTableCell("-"),
  );

  return row;
}

function createTableCell(text) {
  const cell = document.createElement("td");

  cell.textContent = text;

  return cell;
}

function createMessageRow(message, columnCount) {
  const row = document.createElement("tr");
  const cell = document.createElement("td");

  cell.colSpan = columnCount;
  cell.textContent = message;

  row.append(cell);

  return row;
}

function renderEmptyAlertStatsTable() {
  if (!alertTableElements.body) {
    return;
  }

  alertTableElements.body.replaceChildren(createMessageRow("특보별 영향 통계 데이터가 없습니다.", 5));
}

function renderAlertStatsTable(stationDetailData) {
  if (!alertTableElements.body) {
    return;
  }

  const rows = Array.isArray(stationDetailData.by_alert)
    ? stationDetailData.by_alert.map(createAlertStatsRow)
    : [];

  alertTableElements.body.replaceChildren(
    ...(rows.length > 0 ? rows : [createMessageRow("특보별 영향 통계 데이터가 없습니다.", 5)]),
  );
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

function getHistoryRiskLevel(caseItem) {
  if (!caseItem.alert_type) {
    return "interest";
  }

  if (caseItem.delay_min >= 20) {
    return "high";
  }

  return "warning";
}

function createHistoryItem(caseItem) {
  const item = document.createElement("li");
  const label = document.createElement("span");
  const content = document.createElement("div");
  const title = document.createElement("strong");
  const alertDescription = document.createElement("p");
  const delayDescription = document.createElement("p");
  const button = document.createElement("button");
  const alertLabel = caseItem.alert_type || "평상시";
  const riskLevel = getHistoryRiskLevel(caseItem);
  const formattedDate = formatCaseDate(caseItem.date);

  item.className = "station-history-item";
  label.className = `station-history-item__label station-history-item__label--${riskLevel}`;
  label.textContent = alertLabel;

  content.className = "station-history-item__content";
  title.textContent = `${formattedDate} ${alertLabel}`;
  alertDescription.textContent = caseItem.alert_type
    ? `${caseItem.alert_type} 영향 기록`
    : "특보 미발효 기준 기록";
  delayDescription.textContent = Number.isFinite(caseItem.delay_min)
    ? `기록된 지연 ${caseItem.delay_min}분`
    : "지연 정보 없음";
  content.append(title, alertDescription, delayDescription);

  button.className = "station-history-item__button";
  button.type = "button";
  button.textContent = "상세보기";
  button.setAttribute("aria-label", `${formattedDate} ${alertLabel} 사례 상세보기`);

  item.append(label, content, button);

  return item;
}

function renderEmptyHistoryList() {
  if (!historyElements.list) {
    return;
  }

  const item = document.createElement("li");

  item.className = "station-history-item";
  item.textContent = "과거 주요 사례 데이터가 없습니다.";
  historyElements.list.replaceChildren(item);
}

function renderHistoryList(stationDetailData) {
  if (!historyElements.list) {
    return;
  }

  const rows = Array.isArray(stationDetailData.cases)
    ? stationDetailData.cases.map(createHistoryItem)
    : [];

  if (rows.length === 0) {
    renderEmptyHistoryList();
    return;
  }

  historyElements.list.replaceChildren(...rows);
}

function renderStationLineChart(stationDetailData) {
  const hourlyDelayData = Array.isArray(stationDetailData.hourly_delay) ? stationDetailData.hourly_delay : [];
  const weekdayPoints = getLineChartPoints(hourlyDelayData, "weekday_delay");
  const holidayPoints = getLineChartPoints(hourlyDelayData, "holiday_delay");
  const highlightPoint = weekdayPoints[weekdayPoints.length - 1] || null;

  if (chartElements.lineChart) {
    chartElements.lineChart.setAttribute(
      "aria-label",
      hourlyDelayData.length > 0
        ? `${formatStationName(stationDetailData.station)} 시간대별 평균 지연 시간 차트`
        : "시간대별 평균 지연 시간 데이터 없음",
    );
  }

  if (chartElements.lineWeekday) {
    chartElements.lineWeekday.setAttribute("points", toPolylinePoints(weekdayPoints));
  }

  if (chartElements.lineHoliday) {
    chartElements.lineHoliday.setAttribute("points", toPolylinePoints(holidayPoints));
  }

  if (chartElements.linePoint) {
    chartElements.linePoint.toggleAttribute("hidden", !highlightPoint);

    if (highlightPoint) {
      chartElements.linePoint.setAttribute("cx", String(highlightPoint.x));
      chartElements.linePoint.setAttribute("cy", String(highlightPoint.y));
    }
  }

  if (chartElements.lineTooltip) {
    chartElements.lineTooltip.textContent = highlightPoint ? `${highlightPoint.value.toFixed(1)}분` : "-";

    if (highlightPoint) {
      chartElements.lineTooltip.setAttribute("x", String(highlightPoint.x));
      chartElements.lineTooltip.setAttribute("y", String(Math.max(highlightPoint.y - 12, 18)));
    }
  }

  if (chartElements.lineTooltipBox) {
    chartElements.lineTooltipBox.toggleAttribute("hidden", !highlightPoint);

    if (highlightPoint) {
      chartElements.lineTooltipBox.setAttribute("x", String(highlightPoint.x - 29));
      chartElements.lineTooltipBox.setAttribute("y", String(Math.max(highlightPoint.y - 42, 0)));
    }
  }
}

function createAlertComparisonGroup(comparisonItem) {
  const group = document.createElement("div");
  const normalBar = document.createElement("div");
  const alertBar = document.createElement("div");
  const normalValue = document.createElement("span");
  const alertValue = document.createElement("span");
  const label = document.createElement("strong");

  group.className = "station-bar-chart__group";
  normalBar.className = "station-bar-chart__bar station-bar-chart__bar--normal";
  alertBar.className = "station-bar-chart__bar station-bar-chart__bar--alert";
  normalBar.style.height = `${getBarHeight(comparisonItem.normal_avg_delay).toFixed(0)}px`;
  alertBar.style.height = `${getBarHeight(comparisonItem.alert_avg_delay).toFixed(0)}px`;
  normalValue.textContent = Number.isFinite(comparisonItem.normal_avg_delay)
    ? comparisonItem.normal_avg_delay.toFixed(1)
    : "-";
  alertValue.textContent = Number.isFinite(comparisonItem.alert_avg_delay)
    ? comparisonItem.alert_avg_delay.toFixed(1)
    : "-";
  label.textContent = comparisonItem.alert_type || "특보";

  normalBar.append(normalValue);
  alertBar.append(alertValue);
  group.append(normalBar, alertBar, label);

  return group;
}

function renderStationAlertComparisonChart(stationDetailData) {
  if (!chartElements.alertComparisonChart) {
    return;
  }

  const axisItems = Array.from(chartElements.alertComparisonChart.querySelectorAll(".station-bar-chart__y"));
  const comparisonData = Array.isArray(stationDetailData.alert_delay_comparison)
    ? stationDetailData.alert_delay_comparison
    : [];
  const groups = comparisonData.map(createAlertComparisonGroup);

  chartElements.alertComparisonChart.replaceChildren(...axisItems, ...groups);
}

function renderStationCharts(stationDetailData) {
  renderStationLineChart(stationDetailData);
  renderStationAlertComparisonChart(stationDetailData);
}

function renderStationDetail(stationDetailData, vulnerabilityStationsData, selectedStationName = stationDetailData.station) {
  const selectedStationDetail = createSelectedStationDetail(stationDetailData, selectedStationName);
  const stationMetrics = getSelectedStationMetrics(selectedStationName, vulnerabilityStationsData);

  if (stationSelectionElements.select) {
    stationSelectionElements.select.value =
      getStationIdByName(selectedStationName, vulnerabilityStationsData) || selectedStationName;
  }

  renderStationInfo(selectedStationDetail, vulnerabilityStationsData, stationMetrics);
  renderStationMetrics(stationMetrics);
  renderAlertStatsTable(selectedStationDetail);
  renderHistoryList(selectedStationDetail);
  renderStationCharts(selectedStationDetail);
}

function buildStationSelectOptions(vulnerabilityStationsData, selectedStationName) {
  if (!stationSelectionElements.select) {
    return;
  }

  const stations = getStations(vulnerabilityStationsData);
  const options = stations.map((station) => {
    const option = document.createElement("option");

    option.value = station.station_id || station.station;
    option.textContent = formatStationName(station.station);

    return option;
  });

  stationSelectionElements.select.replaceChildren(...options);
  stationSelectionElements.select.value =
    getStationIdByName(selectedStationName, vulnerabilityStationsData) || selectedStationName;
}

function initializeStationSelection(stationDetailData, vulnerabilityStationsData, selectedStationName) {
  const queryParams = new URLSearchParams(window.location.search);
  const hasStationQuery = queryParams.has(STATION_ID_QUERY_PARAM) || queryParams.has(STATION_QUERY_PARAM);

  buildStationSelectOptions(vulnerabilityStationsData, selectedStationName);

  if (stationSelectionElements.toggleButton && stationSelectionElements.selector) {
    stationSelectionElements.selector.hidden = !hasStationQuery;
    stationSelectionElements.toggleButton.setAttribute("aria-expanded", String(hasStationQuery));

    stationSelectionElements.toggleButton.addEventListener("click", () => {
      const shouldShowSelector = stationSelectionElements.selector.hidden;

      stationSelectionElements.selector.hidden = !shouldShowSelector;
      stationSelectionElements.toggleButton.setAttribute("aria-expanded", String(shouldShowSelector));

      if (shouldShowSelector) {
        stationSelectionElements.select?.focus();
      }
    });
  }

  if (stationSelectionElements.select) {
    stationSelectionElements.select.addEventListener("change", (event) => {
      const selectedStationName =
        getStationNameById(event.target.value, vulnerabilityStationsData) || event.target.value;

      updateStationQueryString(selectedStationName, vulnerabilityStationsData);
      renderStationDetail(stationDetailData, vulnerabilityStationsData, selectedStationName);
    });
  }

  window.addEventListener("popstate", () => {
    const selectedStationNameFromUrl = getInitialSelectedStationName(stationDetailData, vulnerabilityStationsData);

    renderStationDetail(stationDetailData, vulnerabilityStationsData, selectedStationNameFromUrl);
  });
}

async function fetchJson(url) {
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`Mock 데이터를 불러오지 못했습니다. status: ${response.status}`);
  }

  return response.json();
}

async function initializeStationDetail() {
  try {
    const [stationDetailData, vulnerabilityStationsData] = await Promise.all([
      fetchJson(STATION_DETAIL_MOCK_URL),
      fetchJson(VULNERABILITY_STATIONS_MOCK_URL),
    ]);

    const selectedStationName = getInitialSelectedStationName(stationDetailData, vulnerabilityStationsData);

    initializeStationSelection(stationDetailData, vulnerabilityStationsData, selectedStationName);
    renderStationDetail(stationDetailData, vulnerabilityStationsData, selectedStationName);
  } catch (error) {
    console.error(error);
    renderEmptyStationDetail();
  }
}

initializeStationDetail();
