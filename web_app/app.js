const $ = (id) => document.getElementById(id);
const ns = "http://www.w3.org/2000/svg";
const months = Array.from({ length: 12 }, (_, i) =>
  new Date(Date.UTC(2025, i, 1)).toLocaleString("en", {
    month: "short",
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
  country: "Sri_Lanka",
  month: "2025-08",
  mode: "active_cells",
  data: null,
  packet: null,
  mapCells: [],
  boundaries: null,
  manifest: null,
};
let countryRequest = 0,
  mapRequest = 0;
const cache = new Map();
function svgNode(tag, attrs = {}, text = "") {
  const n = document.createElementNS(ns, tag);
  for (const [k, v] of Object.entries(attrs)) n.setAttribute(k, v);
  if (text) n.textContent = text;
  return n;
}
async function json(path) {
  if (!cache.has(path))
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
function rangeDays() {
  return state.data.daily.filter((d) => d.date.startsWith(state.month));
}
function color(v, max) {
  const t = max ? Math.log1p(v) / Math.log1p(max) : 0;
  const a = [38, 48, 40],
    b = [232, 244, 160];
  return `rgb(${a.map((x, i) => Math.round(x + (b[i] - x) * t)).join(",")})`;
}

function renderCalendar() {
  const calendar = $("calendar");
  calendar.replaceChildren();
  const max = Math.max(...state.data.daily.map((d) => d[state.mode]));
  for (let m = 0; m < 12; m++) {
    const key = `2025-${String(m + 1).padStart(2, "0")}`;
    const label = document.createElement("span");
    label.className = "month-label";
    label.textContent = months[m];
    calendar.append(label);
    const days = state.data.daily.filter((d) => d.date.startsWith(key));
    days.forEach((d) => {
      const b = document.createElement("button");
      b.style.background = color(d[state.mode], max);
      b.className = key === state.month ? "selected" : "";
      b.title = `${d.date}: ${fmt(d[state.mode])} ${state.mode === "raw" ? "raw observations" : "active cell-days"}`;
      b.setAttribute("aria-label", b.title);
      b.onclick = () => {
        state.month = key;
        $("month").value = key;
        renderMonth();
      };
      calendar.append(b);
    });
    for (let n = days.length; n < 31; n++) {
      const empty = document.createElement("span");
      empty.className = "empty";
      calendar.append(empty);
    }
  }
  $("calendar-label").textContent =
    state.mode === "raw"
      ? "All source types and confidence levels · raw observation counts"
      : "Presumed vegetation · quality filtered · distinct H3 resolution-8 cells per UTC day";
}

function chart(svg, series, width, height, options = {}) {
  svg.replaceChildren();
  const left = 42,
    right = 15,
    top = 16,
    bottom = 28;
  const all = series.flatMap((s) => s.values);
  const max = Math.max(1, ...all, ...(options.upper || [])) * 1.05;
  const n = series[0].values.length;
  const x = (i) => left + (i * (width - left - right)) / Math.max(1, n - 1),
    y = (v) => height - bottom - ((height - top - bottom) * v) / max;
  for (let i = 0; i < 4; i++) {
    const value = (max * i) / 3,
      yy = y(value);
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
  for (const i of new Set(ticks))
    svg.append(
      svgNode(
        "text",
        { x: x(i), y: height - 7, "text-anchor": "middle" },
        options.labels?.[i] ?? String(i + 1),
      ),
    );
}

function renderActivity() {
  const days = rangeDays();
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

function showEvidence(c) {
  const box = $("map-evidence");
  box.replaceChildren();
  const strong = document.createElement("strong");
  strong.textContent = `${c.h3} · ${fmt(c.cell_days)} active cell-days · type ${c.type}`;
  box.append(strong, document.createElement("br"));
  box.append(
    document.createTextNode(
      Object.entries(c.sensors)
        .map(([s, n]) => `${sourceLabels[s]}: ${fmt(n)} observations`)
        .join(" · "),
    ),
    document.createElement("br"),
  );
  c.samples.forEach((r) => {
    const p = document.createElement("div");
    p.textContent = `${r.source}/2025/${r.source}_2025_${state.country}.csv:${r.row} · ${r.utc} · ${decimal(r.frp_mw)} MW`;
    box.append(p);
  });
  box.append(
    document.createTextNode(
      "Up to 3 source-row examples. Map cells and samples use the quality filter.",
    ),
  );
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
  let [minLon, maxLon, minLat, maxLat] = [
    Math.min(...points.map((p) => p[0])),
    Math.max(...points.map((p) => p[0])),
    Math.min(...points.map((p) => p[1])),
    Math.max(...points.map((p) => p[1])),
  ];
  const midLat = (((minLat + maxLat) / 2) * Math.PI) / 180,
    ratio = Math.cos(midLat);
  const scale = Math.min(
    490 / ((maxLon - minLon) * ratio),
    330 / (maxLat - minLat),
  );
  const px = (lon) => 280 + (lon - (maxLon + minLon) / 2) * scale * ratio,
    py = (lat) => 195 - (lat - (maxLat + minLat) / 2) * scale;
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
  $("map-evidence").textContent = cells.length
    ? `${fmt(cells.length)} mapped parent cells. Select a dot; the 20 most active also support keyboard selection.`
    : "No qualifying map observations for this selection.";
}

async function loadMap() {
  const request = ++mapRequest;
  const path = state.data.map_months[state.month].path;
  $("map-evidence").textContent = "Loading selected month…";
  $("map").replaceChildren();
  state.mapCells = [];
  try {
    const cells = await json(path);
    if (request !== mapRequest) return;
    state.mapCells = cells;
    renderMap();
  } catch (e) {
    if (request === mapRequest)
      $("map-evidence").textContent = `Map could not load: ${e.message}`;
  }
}

function renderMonth() {
  const days = rangeDays(),
    sum = (k) => days.reduce((n, d) => n + d[k], 0);
  $("stat-raw").textContent = fmt(sum("raw"));
  $("stat-cells").textContent = fmt(sum("active_cells"));
  $("stat-multi").textContent = fmt(sum("multi_sensor_cells"));
  $("stat-industrial").textContent = fmt(sum("industrial_raw"));
  $("cells-mode").setAttribute(
    "aria-pressed",
    String(state.mode === "active_cells"),
  );
  $("raw-mode").setAttribute("aria-pressed", String(state.mode === "raw"));
  renderCalendar();
  renderActivity();
  loadMap();
}

function renderBenchmark() {
  const b = state.data.benchmark,
    body = $("benchmark");
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
  const p = document.createElement("p");
  const ci = b.paired_mae_delta_ci95.map(decimal).join(" to ");
  p.textContent = `${b.promotion_passed ? "Offline gate passed." : "Research only · promotion gate not passed."} Selected-model MAE skill vs last week: ${pct(b.skill_vs_last_week)}. Paired weekly MAE difference, exploratory 95% block-bootstrap interval: ${ci}. Negative favors the candidate. ${b.results[0].holdout_origins} holdout origins; too little evidence for operational validation.`;
  promotion.append(p);
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
  const country = state.country;
  $("loading").hidden = false;
  $("loading").textContent = "Loading the observation archive…";
  $("app").hidden = true;
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
    if (request === countryRequest)
      $("loading").textContent =
        `Unable to load archive: ${e.message}. Serve web_app over HTTP; see README.`;
  }
}

$("country").onchange = loadCountry;
$("month").onchange = () => {
  state.month = $("month").value;
  renderMonth();
};
$("industrial").onchange = renderMap;
for (const [id, mode] of [
  ["cells-mode", "active_cells"],
  ["raw-mode", "raw"],
])
  $(id).onclick = () => {
    state.mode = mode;
    renderCalendar();
    $("cells-mode").setAttribute(
      "aria-pressed",
      String(mode === "active_cells"),
    );
    $("raw-mode").setAttribute("aria-pressed", String(mode === "raw"));
  };
$("brief-download").onclick = async () => {
  const response = await fetch(`data/${state.country}_brief.md`);
  if (response.ok)
    download(
      `${state.country}_brief.md`,
      await response.text(),
      "text/markdown",
    );
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
  for (const fold of state.data.benchmark.predictions)
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
try {
  [state.manifest, state.boundaries] = await Promise.all([
    json("data/manifest.json"),
    json("data/boundaries.geojson"),
  ]);
  await loadCountry();
} catch (e) {
  $("loading").textContent = `Archive initialization failed: ${e.message}`;
}
