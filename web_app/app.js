const $ = (id) => document.getElementById(id);
const ns = "http://www.w3.org/2000/svg";
const months = Array.from({ length: 12 }, (_, i) =>
  new Date(Date.UTC(2025, i, 1)).toLocaleString("en", {
    month: "short",
    timeZone: "UTC",
  }),
);
const fullMonths = Array.from({ length: 12 }, (_, i) =>
  new Date(Date.UTC(2025, i, 1)).toLocaleString("en", {
    month: "long",
    timeZone: "UTC",
  }),
);
const labels = {
  last_week: "Last week",
  trailing_28: "28-day mean",
  weekday_8w: "8-week weekday",
  ridge_ar: "Ridge autoregression",
};
const sourceLabels = {
  modis: "MODIS · Terra + Aqua",
  "viirs-snpp": "VIIRS · S-NPP",
  "viirs-jpss1": "VIIRS · NOAA-20",
};
const fmt = (x) => Number(x).toLocaleString("en", { maximumFractionDigits: 0 });
const decimal = (x) =>
  Number(x).toLocaleString("en", { maximumFractionDigits: 2 });
const pct = (x) => (x == null ? "—" : `${(100 * x).toFixed(1)}%`);

const state = {
  view: "overview",
  country: "Sri_Lanka",
  month: "2025-08",
  selectedDay: null,
  mode: "active_cells",
  data: null,
  packet: null,
  mapCells: [],
  boundaries: null,
  manifest: null,
};

let countryRequest = 0;
let mapRequest = 0;
const cache = new Map();

function svgNode(tag, attrs = {}, text = "") {
  const n = document.createElementNS(ns, tag);
  for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v);
  if (text) n.textContent = text;
  return n;
}

async function json(path) {
  if (!cache.has(path)) {
    cache.set(
      path,
      fetch(path)
        .then((r) => {
          if (!r.ok) throw Error(`${path}: HTTP ${r.status}`);
          return r.json();
        })
        .catch((e) => {
          cache.delete(path);
          throw e;
        }),
    );
  }
  return cache.get(path);
}

function download(name, content, type = "application/json") {
  const a = document.createElement("a");
  const url = URL.createObjectURL(new Blob([content], { type }));
  a.href = url;
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function unitLabel(mode = state.mode) {
  return mode === "raw" ? "raw detections" : "active cell-days";
}

function monthName(monthKey, full = false) {
  const [year, m] = monthKey.split("-");
  const idx = Number(m) - 1;
  const list = full ? fullMonths : months;
  return `${list[idx] ?? monthKey} ${year}`;
}

function rangeDays() {
  return state.data.daily.filter((d) => d.date.startsWith(state.month));
}

function color(v, max) {
  const t = max ? Math.log1p(v) / Math.log1p(max) : 0;
  const a = [38, 48, 40];
  const b = [232, 244, 160];
  return `rgb(${a.map((x, i) => Math.round(x + (b[i] - x) * t)).join(",")})`;
}

function resetMetricPlaceholders() {
  for (const id of [
    "stat-cells",
    "stat-raw",
    "stat-peak",
    "stat-multi",
    "stat-industrial",
  ]) {
    $(id).textContent = "—";
  }
}

function setLoadingBanner(message, isError = false) {
  const banner = $("loading");
  banner.hidden = false;
  banner.classList.toggle("error", isError);
  banner.setAttribute("role", isError ? "alert" : "status");
  $("loading-text").textContent = message;
  $("retry-load").hidden = !isError;
}

function switchView(view, moveFocus = false) {
  const views = ["overview", "explore", "research"];
  if (!views.includes(view)) return;
  state.view = view;
  for (const name of views) {
    const active = name === view;
    const tab = $(`tab-${name}`);
    const panel = $(`view-${name}`);
    tab.setAttribute("aria-selected", String(active));
    tab.tabIndex = active ? 0 : -1;
    panel.hidden = !active;
  }
  if (moveFocus) {
    $(`view-${view}`).focus({ preventScroll: false });
  }
}

function updateContext() {
  const year = state.data?.year ?? state.manifest?.dataset_year ?? 2025;
  const countryLabel = state.country.replaceAll("_", " ");
  const shortMonth = monthName(state.month, false);
  const upperMonth = shortMonth.toUpperCase();
  $("ctx-country").textContent = countryLabel;
  $("ctx-period").textContent = `Jan–Dec ${year} (Selected: ${shortMonth})`;
  $("rail-year").textContent = String(year);
  $("calendar-year-chip").textContent = String(year);
  $("explore-month-chip").textContent = upperMonth;
  $("explore-heading").textContent =
    `Spatial footprint & sensor breakdown · ${shortMonth}`;
  $("stat-cells-label").textContent = `ACTIVE CELL-DAYS · ${upperMonth}`;
  $("stat-raw-label").textContent = `RAW DETECTIONS · ${upperMonth}`;
  $("stat-peak-label").textContent = `PEAK RECORDED MONTH · ${year}`;
  $("overview-next").textContent = `Explore ${shortMonth} map & sensors →`;
}

function updateDayReadout(dayRecord = null) {
  const readout = $("day-readout");
  if (dayRecord) {
    readout.textContent = `${dayRecord.date}: ${fmt(dayRecord.active_cells)} active cell-days · ${fmt(dayRecord.raw)} raw detections`;
    return;
  }
  const days = rangeDays();
  const totalCells = days.reduce((sum, d) => sum + d.active_cells, 0);
  const totalRaw = days.reduce((sum, d) => sum + d.raw, 0);
  readout.textContent = `${monthName(state.month, true)}: ${fmt(totalCells)} active cell-days · ${fmt(totalRaw)} raw detections. Select any day tile for daily totals.`;
}

function renderCalendar() {
  const calendar = $("calendar");
  calendar.replaceChildren();
  const year = state.data.year || 2025;
  const maxDay = Math.max(0, ...state.data.daily.map((d) => d[state.mode]));
  const monthRows = Array.from({ length: 12 }, (_, m) => {
    const key = `${year}-${String(m + 1).padStart(2, "0")}`;
    const days = state.data.daily.filter((d) => d.date.startsWith(key));
    const total = days.reduce((sum, d) => sum + d[state.mode], 0);
    return { m, key, shortLabel: months[m], fullLabel: fullMonths[m], days, total };
  });
  const maxMonthTotal = Math.max(0, ...monthRows.map((r) => r.total));
  const peakMonth = maxMonthTotal > 0 ? monthRows.find((r) => r.total === maxMonthTotal) : null;
  const peakDayRecord =
    maxDay > 0
      ? state.data.daily.find((d) => d[state.mode] === maxDay)
      : null;

  const focusDate =
    state.selectedDay && state.selectedDay.startsWith(state.month)
      ? state.selectedDay
      : `${state.month}-01`;

  const dayButtons = [];

  for (const rowData of monthRows) {
    const isSelected = rowData.key === state.month;
    const isPeak = peakMonth && rowData.key === peakMonth.key;
    const row = document.createElement("div");
    row.className = "calendar-row";
    if (isSelected) row.classList.add("selected");
    if (isPeak) row.classList.add("is-peak");

    const monthBtn = document.createElement("button");
    monthBtn.type = "button";
    monthBtn.className = "month-btn";
    monthBtn.textContent = rowData.shortLabel;
    monthBtn.setAttribute("aria-pressed", String(isSelected));
    monthBtn.setAttribute(
      "aria-label",
      `${rowData.fullLabel} ${year}: ${fmt(rowData.total)} ${unitLabel()}${isPeak ? ", peak month" : ""}`,
    );
    monthBtn.onclick = () => {
      state.month = rowData.key;
      state.selectedDay = null;
      $("month").value = rowData.key;
      renderMonth();
    };
    row.append(monthBtn);

    const daysWrap = document.createElement("div");
    daysWrap.className = "month-days";

    rowData.days.forEach((d) => {
      const tile = document.createElement("button");
      tile.type = "button";
      tile.className = "day-tile";
      if (peakDayRecord && d.date === peakDayRecord.date) {
        tile.classList.add("peak-day");
      }
      if (state.selectedDay === d.date) {
        tile.classList.add("selected-day");
      }
      tile.dataset.date = d.date;
      tile.style.background = color(d[state.mode], maxDay);
      const label = `${d.date}: ${fmt(d[state.mode])} ${unitLabel()}`;
      tile.title = label;
      tile.setAttribute("aria-label", label);
      tile.tabIndex = d.date === focusDate ? 0 : -1;
      tile.onclick = () => {
        state.month = rowData.key;
        state.selectedDay = d.date;
        $("month").value = rowData.key;
        renderMonth();
      };
      tile.onmouseenter = () => updateDayReadout(d);
      tile.onfocus = () => updateDayReadout(d);
      tile.onmouseleave = () => {
        const selectedRecord = state.selectedDay
          ? state.data.daily.find((item) => item.date === state.selectedDay)
          : null;
        updateDayReadout(selectedRecord || null);
      };
      dayButtons.push(tile);
      daysWrap.append(tile);
    });

    for (let n = rowData.days.length; n < 31; n++) {
      const empty = document.createElement("span");
      empty.className = "day-tile empty";
      empty.setAttribute("aria-hidden", "true");
      daysWrap.append(empty);
    }
    row.append(daysWrap);

    const meta = document.createElement("span");
    meta.className = "month-meta";
    const totalSpan = document.createElement("span");
    totalSpan.textContent = fmt(rowData.total);
    meta.append(totalSpan);
    if (isPeak) {
      const pill = document.createElement("span");
      pill.className = "peak-pill";
      pill.textContent = "PEAK";
      meta.append(pill);
    }
    row.append(meta);
    calendar.append(row);
  }

  dayButtons.forEach((tile, idx) => {
    tile.onkeydown = (e) => {
      let nextIdx = null;
      if (e.key === "ArrowRight") nextIdx = Math.min(dayButtons.length - 1, idx + 1);
      else if (e.key === "ArrowLeft") nextIdx = Math.max(0, idx - 1);
      else if (e.key === "ArrowDown") nextIdx = Math.min(dayButtons.length - 1, idx + 31);
      else if (e.key === "ArrowUp") nextIdx = Math.max(0, idx - 31);
      if (nextIdx !== null && nextIdx !== idx) {
        e.preventDefault();
        dayButtons[idx].tabIndex = -1;
        dayButtons[nextIdx].tabIndex = 0;
        dayButtons[nextIdx].focus();
      }
    };
  });

  $("calendar-label").textContent =
    state.mode === "raw"
      ? "Showing raw satellite detections (all confidence levels & source types). Select a month row or day tile to focus that period."
      : "Showing quality-filtered vegetation active cell-days (H3 resolution 8, UTC day). Select a month row or day tile to focus that period.";

  const selectedRecord = state.selectedDay
    ? state.data.daily.find((item) => item.date === state.selectedDay)
    : null;
  updateDayReadout(selectedRecord || null);
}

function chart(svg, series, width, height, options = {}) {
  svg.replaceChildren();
  const left = 42;
  const right = 15;
  const top = 16;
  const bottom = 28;
  const all = series.flatMap((s) => s.values);
  const max = Math.max(1, ...all, ...(options.upper || [])) * 1.05;
  const n = series[0].values.length;
  const x = (i) => left + (i * (width - left - right)) / Math.max(1, n - 1);
  const y = (v) => height - bottom - ((height - top - bottom) * v) / max;
  for (let i = 0; i < 4; i++) {
    const value = (max * i) / 3;
    const yy = y(value);
    svg.append(
      svgNode("line", {
        x1: left,
        y1: yy,
        x2: width - right,
        y2: yy,
        stroke: "#303a32",
        "stroke-width": 1,
      }),
    );
    svg.append(
      svgNode(
        "text",
        { x: left - 8, y: yy + 3, "text-anchor": "end" },
        fmt(value),
      ),
    );
  }
  if (options.upper) {
    const points = [
      ...options.upper.map((v, i) => `${x(i)},${y(v)}`),
      ...options.lower.map((v, i) => `${x(i)},${y(v)}`).reverse(),
    ].join(" ");
    svg.append(
      svgNode("polygon", { points, fill: "#e8f4a0", "fill-opacity": ".10" }),
    );
  }
  for (const s of series) {
    const path = s.values
      .map((v, i) => `${i ? "L" : "M"}${x(i)},${y(v)}`)
      .join(" ");
    svg.append(
      svgNode("path", {
        d: path,
        fill: "none",
        stroke: s.color,
        "stroke-width": 2,
      }),
    );
  }
  const ticks = [0, Math.floor((n - 1) / 2), n - 1];
  for (const i of new Set(ticks)) {
    svg.append(
      svgNode(
        "text",
        { x: x(i), y: height - 7, "text-anchor": "middle" },
        options.labels?.[i] ?? String(i + 1),
      ),
    );
  }
}

function renderActivity() {
  const days = rangeDays();
  const hasAny = days.some((d) => d.active_cells > 0 || d.raw > 0);
  const emptyNote = $("activity-empty");
  if (!hasAny) {
    emptyNote.hidden = false;
    emptyNote.textContent =
      "No qualifying detections recorded in this month’s archive files (observation coverage unknown; zero is not confirmed fire absence).";
  } else {
    emptyNote.hidden = true;
    emptyNote.textContent = "";
  }
  chart(
    $("activity-chart"),
    [
      { color: "#f08752", values: days.map((d) => d.active_cells) },
      { color: "#75b9bb", values: days.map((d) => d.source_cells.modis) },
      {
        color: "#a1a9ce",
        values: days.map((d) => d.source_cells["viirs-snpp"]),
      },
      {
        color: "#c9b185",
        values: days.map((d) => d.source_cells["viirs-jpss1"]),
      },
    ],
    620,
    170,
    { labels: days.map((d) => d.date.slice(8)) },
  );
}

function coordLabel(lat, lon) {
  const ns = `${Math.abs(lat).toFixed(2)}°${lat >= 0 ? "N" : "S"}`;
  const ew = `${Math.abs(lon).toFixed(2)}°${lon >= 0 ? "E" : "W"}`;
  return `${ns}, ${ew}`;
}

// Focused inspection panel for one selected map cell: a plain-language summary
// first, with source rows and exact grid details behind optional disclosures.
// Reuses the existing #map-evidence element — no new always-visible section.
function showEvidence(c) {
  const box = $("map-evidence");
  box.replaceChildren();
  box.classList.add("inspecting");
  const year = state.data.year || 2025;
  const countryLabel = state.country.replaceAll("_", " ");
  const period = monthName(state.month, true);
  const isStatic = c.type === 2;
  const streams = Object.entries(c.sensors);
  const streamNames = streams.map(([s]) => sourceLabels[s]);

  const heading = document.createElement("div");
  heading.className = "evidence-heading";
  const title = document.createElement("strong");
  title.textContent = isStatic
    ? "Static thermal source · excluded from the vegetation series"
    : `${fmt(c.cell_days)} active cell-day${c.cell_days === 1 ? "" : "s"} recorded here`;
  const where = document.createElement("span");
  where.className = "evidence-where";
  where.textContent = `Near ${coordLabel(c.lat, c.lon)} · ${countryLabel} · ${period}`;
  heading.append(title, where);
  box.append(heading);

  // Plain summary: label raw observations and aggregated cell-days consistently,
  // and explain the difference as repeat views, not false detections.
  const summary = document.createElement("p");
  summary.className = "evidence-summary";
  if (isStatic) {
    summary.textContent =
      `This grid cell holds ${fmt(c.raw)} raw detection${c.raw === 1 ? "" : "s"} flagged as a static thermal source (type 2) — a persistent stationary heat signature. It is shown only as an optional layer and is kept out of the vegetation active cell-day counts. The source type is a satellite flag; no specific facility is identified here.`;
  } else if (c.raw === c.cell_days) {
    summary.textContent =
      `${fmt(c.raw)} raw detection${c.raw === 1 ? "" : "s"} from ${streamNames.length} satellite stream${streamNames.length === 1 ? "" : "s"} (${streamNames.join(", ")}), counted as ${fmt(c.cell_days)} active cell-day${c.cell_days === 1 ? "" : "s"}.`;
  } else {
    summary.textContent =
      `${fmt(c.raw)} raw detections here group into ${fmt(c.cell_days)} active cell-day${c.cell_days === 1 ? "" : "s"}. The same landscape is seen by many 375 m pixels and several satellite passes, so each grid cell counts once per UTC day. The difference is repeat views of the same area, not a count of false detections.`;
  }
  box.append(summary);

  // Selected period, source counts and the active filters, shown together.
  const chips = document.createElement("div");
  chips.className = "evidence-chips";
  const addChip = (text) => {
    const span = document.createElement("span");
    span.textContent = text;
    chips.append(span);
  };
  streams.forEach(([s, n]) =>
    addChip(`${sourceLabels[s]}: ${fmt(n)} obs`),
  );
  addChip("Quality filter: on");
  addChip($("industrial").checked ? "Static sources: shown" : "Static sources: hidden");
  box.append(chips);

  // Optional source timestamps and CSV row references, on demand.
  const sources = document.createElement("details");
  sources.className = "evidence-details";
  const sourcesSummary = document.createElement("summary");
  sourcesSummary.textContent = "Source timestamps & CSV rows";
  sources.append(sourcesSummary);
  const sampleList = document.createElement("div");
  sampleList.className = "evidence-samples";
  c.samples.forEach((r) => {
    const row = document.createElement("div");
    row.textContent = `${r.source}/${year}/${r.source}_${year}_${state.country}.csv:${r.row} · ${r.utc} · ${decimal(r.frp_mw)} MW`;
    sampleList.append(row);
  });
  const note = document.createElement("p");
  note.className = "evidence-sample-note";
  note.textContent =
    c.cell_days > c.samples.length || c.raw > c.samples.length
      ? `Showing ${c.samples.length} example row${c.samples.length === 1 ? "" : "s"} only — not the full set for this cell. Use “Export selected GeoJSON” or the daily CSV for every record.`
      : `Example row${c.samples.length === 1 ? "" : "s"} for this cell. Use the GeoJSON/CSV exports for machine-readable detail.`;
  sources.append(sampleList, note);
  box.append(sources);

  // Advanced disclosure: exact grid definition kept out of the plain summary.
  const grid = document.createElement("details");
  grid.className = "evidence-details";
  const gridSummary = document.createElement("summary");
  gridSummary.textContent = "How this point is aggregated (advanced)";
  grid.append(gridSummary);
  const gridBody = document.createElement("p");
  gridBody.className = "evidence-grid-body";
  gridBody.textContent =
    `Map points combine H3 resolution-8 cell-days (~0.74 km²) into their resolution-7 parent cell (~5.16 km²) for a readable footprint. Each point sits at the parent-cell centre. Parent cell: ${c.h3}. An active cell-day means at least one quality-filtered detection in one resolution-8 cell on one UTC day — not a distinct fire or burned area.`;
  grid.append(gridBody);
  box.append(grid);
}

function renderMap() {
  const svg = $("map");
  svg.replaceChildren();
  const country = state.boundaries.features.find(
    (f) => f.properties.name === state.country.replace("_", " "),
  );
  const polygons =
    country.geometry.type === "MultiPolygon"
      ? country.geometry.coordinates
      : [country.geometry.coordinates];
  const points = polygons.flat(2);
  const [minLon, maxLon, minLat, maxLat] = [
    Math.min(...points.map((p) => p[0])),
    Math.max(...points.map((p) => p[0])),
    Math.min(...points.map((p) => p[1])),
    Math.max(...points.map((p) => p[1])),
  ];
  const midLat = (((minLat + maxLat) / 2) * Math.PI) / 180;
  const ratio = Math.cos(midLat);
  const scale = Math.min(
    490 / ((maxLon - minLon) * ratio),
    330 / (maxLat - minLat),
  );
  const px = (lon) => 280 + (lon - (maxLon + minLon) / 2) * scale * ratio;
  const py = (lat) => 195 - (lat - (maxLat + minLat) / 2) * scale;
  for (let j = 0; j < 5; j++) {
    const lat = minLat + ((maxLat - minLat) * j) / 4;
    svg.append(
      svgNode("line", {
        x1: 20,
        x2: 540,
        y1: py(lat),
        y2: py(lat),
        stroke: "#26332b",
      }),
    );
    svg.append(
      svgNode(
        "text",
        { x: 22, y: py(lat) - 5 },
        `${Math.abs(lat).toFixed(1)}°${lat >= 0 ? "N" : "S"}`,
      ),
    );
  }
  polygons.forEach((p) => {
    const d = p
      .map(
        (ring) =>
          ring
            .map(([lon, lat], i) => `${i ? "L" : "M"}${px(lon)},${py(lat)}`)
            .join(" ") + " Z",
      )
      .join(" ");
    svg.append(
      svgNode("path", {
        d,
        fill: "#202e23",
        stroke: "#5b7055",
        "stroke-width": 1,
        "fill-rule": "evenodd",
      }),
    );
  });
  const cells = state.mapCells.filter(
    (c) => c.type === 0 || $("industrial").checked,
  );
  const max = Math.max(1, ...cells.map((c) => c.cell_days));
  const sorted = [...cells].sort((a, b) => b.cell_days - a.cell_days);
  // Render less active points first so the most active remain selectable on top.
  [...sorted].reverse().forEach((c, i) => {
    const dot = svgNode("circle", {
      cx: px(c.lon),
      cy: py(c.lat),
      r: 1.5 + 3 * Math.sqrt(c.cell_days / max),
      fill: c.type === 2 ? "#75b9bb" : "#f08752",
      "fill-opacity": c.type === 2 ? ".95" : ".65",
      class: "map-dot",
      tabindex: i >= cells.length - 20 ? "0" : "-1",
      role: "button",
      "aria-label": `${c.h3}: ${c.cell_days} cell-days, source type ${c.type}`,
    });
    dot.append(svgNode("title", {}, `${c.h3}: ${c.cell_days} cell-days`));
    dot.onclick = () => showEvidence(c);
    dot.onkeydown = (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        showEvidence(c);
      }
    };
    svg.append(dot);
  });
  const evidence = $("map-evidence");
  evidence.classList.remove("inspecting");
  evidence.textContent = cells.length
    ? `${fmt(cells.length)} mapped parent cells for ${monthName(state.month, true)}. Select a dot to inspect what was observed and why counts differ; the 20 most active also support keyboard selection.`
    : "No qualifying map observations recorded for this selection (coverage unknown).";
}

async function loadMap() {
  const request = ++mapRequest;
  const entry = state.data.map_months[state.month];
  if (!entry) {
    state.mapCells = [];
    $("map").replaceChildren();
    $("map-evidence").textContent =
      "Map payload unavailable for this selected period.";
    return;
  }
  const evidence = $("map-evidence");
  evidence.classList.remove("inspecting");
  evidence.textContent = "Loading selected month…";
  $("map").replaceChildren();
  state.mapCells = [];
  try {
    const cells = await json(entry.path);
    if (request !== mapRequest) return;
    state.mapCells = cells;
    renderMap();
  } catch (e) {
    if (request === mapRequest) {
      $("map-evidence").textContent = `Map unavailable (offline or missing payload): ${e.message}`;
    }
  }
}

function renderPeakMetric() {
  const year = state.data.year || 2025;
  const monthSums = Array.from({ length: 12 }, (_, m) => {
    const key = `${year}-${String(m + 1).padStart(2, "0")}`;
    const total = state.data.daily
      .filter((d) => d.date.startsWith(key))
      .reduce((sum, d) => sum + d[state.mode], 0);
    return { key, total };
  });
  const peakMonth = monthSums.reduce((best, cur) =>
    cur.total > best.total ? cur : best,
  );
  const peakDay = state.data.daily.reduce((best, cur) =>
    cur[state.mode] > best[state.mode] ? cur : best,
  );
  if (peakMonth.total === 0) {
    $("stat-peak").textContent = "None recorded";
    $("stat-peak-note").textContent =
      `No qualifying ${unitLabel()} recorded in ${year} (coverage unknown).`;
    return;
  }
  $("stat-peak").textContent = monthName(peakMonth.key, false);
  const peakDayShort = `${months[Number(peakDay.date.slice(5, 7)) - 1]} ${Number(peakDay.date.slice(8))}`;
  $("stat-peak-note").textContent =
    `${fmt(peakMonth.total)} ${unitLabel()} · Peak day: ${peakDayShort} (${fmt(peakDay[state.mode])})`;
}

function renderMonth() {
  if (!state.data) return;
  const days = rangeDays();
  const sum = (k) => days.reduce((n, d) => n + d[k], 0);
  $("stat-raw").textContent = fmt(sum("raw"));
  $("stat-cells").textContent = fmt(sum("active_cells"));
  $("stat-multi").textContent = fmt(sum("multi_sensor_cells"));
  $("stat-industrial").textContent = fmt(sum("industrial_raw"));
  $("cells-mode").setAttribute(
    "aria-pressed",
    String(state.mode === "active_cells"),
  );
  $("raw-mode").setAttribute("aria-pressed", String(state.mode === "raw"));
  updateContext();
  renderPeakMetric();
  renderCalendar();
  renderActivity();
  loadMap();
}

function renderBenchmark() {
  const b = state.data.benchmark;
  const body = $("benchmark");
  body.replaceChildren();
  for (const r of b.results) {
    const tr = document.createElement("tr");
    tr.className = r.model === b.selected_model ? "chosen" : "";
    const name = document.createElement("td");
    name.textContent = labels[r.model];
    if (r.model === b.selected_model) {
      const tag = document.createElement("span");
      tag.className = "model-tag";
      tag.textContent = "PRE-JULY PICK";
      name.append(tag);
    }
    tr.append(name);
    for (const v of [
      decimal(r.holdout.mae),
      pct(r.holdout.wape),
      pct(r.coverage_80),
    ]) {
      const td = document.createElement("td");
      td.textContent = v;
      tr.append(td);
    }
    body.append(tr);
  }
  const promotion = $("promotion");
  promotion.replaceChildren();
  const arrow = document.createElement("span");
  arrow.textContent = "↳";
  const p = document.createElement("p");
  const ci = b.paired_mae_delta_ci95.map(decimal).join(" to ");
  p.textContent = `${b.promotion_passed ? "Offline gate passed." : "Research only · promotion gate not passed."} Selected-model MAE skill vs last week: ${pct(b.skill_vs_last_week)}. Paired weekly MAE difference, exploratory 95% block-bootstrap interval: ${ci}. Negative favors the candidate. ${b.results[0].holdout_origins} holdout origins; too little evidence for operational validation.`;
  promotion.append(arrow, p);
  $("forecast-model").textContent =
    `Candidate: ${labels[b.selected_model]} · target: daily active cell-days · shaded band: 80% calibration target`;
  chart(
    $("forecast-chart"),
    [{ color: "#e8f4a0", values: b.forecast.map((d) => d.prediction) }],
    560,
    220,
    {
      lower: b.forecast.map((d) => d.lower),
      upper: b.forecast.map((d) => d.upper),
      labels: b.forecast.map((d) => d.date.slice(5)),
    },
  );
}

function renderDiagnostics() {
  const box = $("dropout");
  box.replaceChildren();
  for (const r of state.data.sensor_dropout) {
    const row = document.createElement("div");
    row.className = "bar-row";
    const label = document.createElement("div");
    label.className = "bar-label";
    const name = document.createElement("span");
    name.textContent = `Without ${sourceLabels[r.removed]}`;
    const value = document.createElement("span");
    value.textContent = `${pct(r.retained_fraction)} retained`;
    label.append(name, value);
    const track = document.createElement("div");
    track.className = "bar-track";
    const fill = document.createElement("div");
    fill.className = "bar-fill";
    fill.style.width = pct(r.retained_fraction);
    track.append(fill);
    row.append(label, track);
    box.append(row);
  }
  $("sensitivity").replaceChildren();
  for (const res of [7, 8, 9]) {
    const tr = document.createElement("tr");
    for (const v of [
      String(res),
      ...[true, false].map((q) =>
        fmt(
          state.data.sensitivity.find(
            (r) => r.resolution === res && r.quality === q,
          ).active_cell_days,
        ),
      ),
    ]) {
      const td = document.createElement("td");
      td.textContent = v;
      tr.append(td);
    }
    $("sensitivity").append(tr);
  }
  $("evidence-claims").replaceChildren();
  for (const c of state.packet.claims.slice(0, 3)) {
    const row = document.createElement("div");
    row.className = "claim";
    const name = document.createElement("span");
    name.textContent = c.name.replaceAll("_", " ");
    const value = document.createElement("code");
    value.textContent = fmt(c.value);
    row.append(name, value);
    row.title = `Evidence: ${c.evidence}`;
    $("evidence-claims").append(row);
  }
  $("run-id").textContent = state.manifest.run_id;
  $("limitations").replaceChildren();
  state.data.limitations.forEach((t) => {
    const li = document.createElement("li");
    li.textContent = t;
    $("limitations").append(li);
  });
  $("csv-download").href = `data/${state.country}_daily.csv`;
}

async function loadCountry() {
  const request = ++countryRequest;
  mapRequest++;
  state.country = $("country").value;
  state.selectedDay = null;
  const country = state.country;
  resetMetricPlaceholders();
  setLoadingBanner(`Loading ${country.replaceAll("_", " ")} archive…`, false);
  $("app").hidden = true;
  updateContext();
  try {
    const [data, packet] = await Promise.all([
      json(`data/${country}.json`),
      json(`data/${country}_evidence.json`),
    ]);
    if (request !== countryRequest) return;
    state.data = data;
    state.packet = packet;
    renderBenchmark();
    renderDiagnostics();
    renderMonth();
    $("loading").hidden = true;
    $("app").hidden = false;
  } catch (e) {
    if (request === countryRequest) {
      setLoadingBanner(
        `Unable to load archive (offline or unbuilt): ${e.message}. Run pyrosync build and serve over HTTP.`,
        true,
      );
    }
  }
}

async function initArchive() {
  setLoadingBanner("Loading the 2025 observation archive…", false);
  $("app").hidden = true;
  resetMetricPlaceholders();
  try {
    if (!state.manifest || !state.boundaries) {
      [state.manifest, state.boundaries] = await Promise.all([
        json("data/manifest.json"),
        json("data/boundaries.geojson"),
      ]);
    }
    await loadCountry();
  } catch (e) {
    setLoadingBanner(
      `Archive unavailable (offline or unbuilt): ${e.message}. Run pyrosync build and serve over HTTP.`,
      true,
    );
  }
}

const tabs = Array.from(document.querySelectorAll('.view-tabs [role="tab"]'));
tabs.forEach((tab, idx) => {
  tab.onclick = () => switchView(tab.dataset.view, false);
  tab.onkeydown = (e) => {
    let target = null;
    if (e.key === "ArrowRight") target = tabs[(idx + 1) % tabs.length];
    else if (e.key === "ArrowLeft") target = tabs[(idx - 1 + tabs.length) % tabs.length];
    else if (e.key === "Home") target = tabs[0];
    else if (e.key === "End") target = tabs[tabs.length - 1];
    if (target) {
      e.preventDefault();
      switchView(target.dataset.view, false);
      target.focus();
    }
  };
});

$("overview-next").onclick = () => {
  switchView("explore", true);
  window.scrollTo({ top: 0, behavior: "smooth" });
};
$("explore-to-research").onclick = () => {
  switchView("research", true);
  window.scrollTo({ top: 0, behavior: "smooth" });
};
$("retry-load").onclick = initArchive;

$("country").onchange = loadCountry;
$("month").onchange = () => {
  state.month = $("month").value;
  state.selectedDay = null;
  renderMonth();
};
$("industrial").onchange = renderMap;

for (const [id, mode] of [
  ["cells-mode", "active_cells"],
  ["raw-mode", "raw"],
]) {
  $(id).onclick = () => {
    state.mode = mode;
    if (state.data) {
      renderPeakMetric();
      renderCalendar();
    }
    $("cells-mode").setAttribute(
      "aria-pressed",
      String(mode === "active_cells"),
    );
    $("raw-mode").setAttribute("aria-pressed", String(mode === "raw"));
  };
}

$("brief-download").onclick = async () => {
  const response = await fetch(`data/${state.country}_brief.md`);
  if (response.ok) {
    download(
      `${state.country}_brief.md`,
      await response.text(),
      "text/markdown",
    );
  }
};
$("packet-download").onclick = () =>
  download(
    `${state.country}_evidence_and_scenario.json`,
    JSON.stringify(state.packet, null, 2),
  );
$("predictions-download").onclick = () => {
  const rows = [
    "model,split,origin,train_end,target_date,horizon,actual,predicted",
  ];
  for (const fold of state.data.benchmark.predictions) {
    fold.actual.forEach((a, i) => {
      const d = new Date(`${fold.origin}T00:00:00Z`);
      d.setUTCDate(d.getUTCDate() + i);
      rows.push(
        [
          fold.model,
          fold.split,
          fold.origin,
          fold.train_end,
          d.toISOString().slice(0, 10),
          i + 1,
          a,
          fold.predicted[i],
        ].join(","),
      );
    });
  }
  download(`${state.country}_forecast_folds.csv`, rows.join("\n"), "text/csv");
};
$("geojson-download").onclick = () =>
  download(
    `${state.country}_${state.month}_map.geojson`,
    JSON.stringify({
      type: "FeatureCollection",
      metadata: {
        unit: "resolution-8 cell-days grouped by resolution-7 parent; points are cell centers",
        month: state.month,
        quality_filter: true,
      },
      features: state.mapCells
        .filter((c) => c.type === 0 || $("industrial").checked)
        .map((c) => ({
          type: "Feature",
          geometry: { type: "Point", coordinates: [c.lon, c.lat] },
          properties: c,
        })),
    }),
  );

months.forEach((name, i) => {
  const o = document.createElement("option");
  o.value = `2025-${String(i + 1).padStart(2, "0")}`;
  o.textContent = `${name} 2025`;
  $("month").append(o);
});
$("month").value = state.month;

await initArchive();
