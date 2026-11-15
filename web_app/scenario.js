// MiroFish calls go through the local PyroSync server; no API keys in the page.
const $ = (id) => document.getElementById(id);
let connected = false;
let scenario = null;
let timer = null;
let generation = 0;
async function request(path, data) {
  const response = await fetch(
    path,
    data === undefined
      ? {}
      : {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(data),
        },
  );
  if (
    !(response.headers.get("content-type") || "").includes("application/json")
  )
    throw Error("Use make serve to enable the local scenario API.");
  const value = await response.json();
  if (!response.ok) throw Error(value.error || `HTTP ${response.status}`);
  return value;
}
function download(name, content) {
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([content], { type: "text/plain" }));
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
}
function render() {
  if (!scenario) return;
  $("scenario-detail").hidden = false;
  const b = scenario.capacity_baseline;
  $("scenario-summary").textContent =
    `${scenario.country.replaceAll("_", " ")} · ${scenario.month} · ${scenario.policy} · ${scenario.phase}${scenario.busy ? " (working)" : ""}. Assumed capacity: ${b.daily_capacity} reviews/day. Deterministic end backlog: ${b.end_backlog}. This queue is not a MiroFish result.${scenario.last_error ? " " + scenario.last_error : ""}${scenario.pending_operation ? " Pending operation: " + scenario.pending_operation + ". Reconcile upstream before retrying." : ""}`;
  $("scenario-start").disabled =
    !connected ||
    scenario.busy ||
    !!scenario.pending_operation ||
    ["completed", "failed"].includes(scenario.phase);
  $("scenario-report").disabled = scenario.phase !== "completed";
  $("scenario-trace").textContent =
    `Scenario ${scenario.id}\n` +
    scenario.trace.map((t) => `${t.operation}: ${t.result}`).join("\n");
}
async function check() {
  try {
    const status = await request("/api/mirofish");
    connected = status.connected;
    $("mirofish-status").textContent = status.message;
  } catch (e) {
    connected = false;
    $("mirofish-status").textContent = e.message;
  }
  render();
}
async function poll(id, token) {
  try {
    const value = await request(`/api/scenarios/${id}`);
    if (token !== generation) return;
    scenario = value;
    render();
    if (scenario.busy) timer = setTimeout(() => poll(id, token), 3000);
  } catch (e) {
    if (token === generation) $("scenario-summary").textContent = e.message;
  }
}
$("mirofish-refresh").onclick = check;
$("scenario-form").onsubmit = async (event) => {
  event.preventDefault();
  clearTimeout(timer);
  const token = ++generation;
  try {
    const value = await request("/api/scenarios", {
      country: $("country").value,
      month: $("month").value,
      policy: $("scenario-policy").value,
      reviewers: Number($("scenario-reviewers").value),
      reviews_per_day: Number($("scenario-capacity").value),
      max_rounds: Number($("scenario-rounds").value),
      replicate: Number($("scenario-replicate").value),
    });
    if (token !== generation) return;
    scenario = value;
    localStorage.setItem("pyrosync-scenario", scenario.id);
    render();
    if (scenario.busy) poll(scenario.id, token);
  } catch (e) {
    $("mirofish-status").textContent = e.message;
  }
};
$("scenario-start").onclick = async () => {
  if (!scenario) return;
  $("scenario-start").disabled = true;
  const id = scenario.id,
    token = generation;
  try {
    await request(`/api/scenarios/${id}/advance`, {});
    await poll(id, token);
  } catch (e) {
    $("scenario-summary").textContent = e.message;
    render();
  }
};
$("scenario-seed").onclick = () =>
  download(`${scenario.id}_state.json`, JSON.stringify(scenario, null, 2));
$("scenario-report").onclick = async () => {
  try {
    const value = await request(`/api/scenarios/${scenario.id}/report`);
    download(`${scenario.id}_synthetic_report.md`, value.markdown);
  } catch (e) {
    $("scenario-summary").textContent = e.message;
  }
};
await check();
const previous = localStorage.getItem("pyrosync-scenario");
if (previous && /^[0-9a-f]{20}$/.test(previous))
  await poll(previous, generation);
