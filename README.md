# PyroSync · Team Gmora

An instrument-aware fire observation lab for the NASA Space Apps harmonization challenge. Compare MODIS and VIIRS observations, inspect source evidence, stress-test sensor availability, and evaluate seven-day forecasts against baselines.

**Dashboard scope:** Sri Lanka and Argentina, 2025 archive. The backend also acquires 2020–2024 archives and evaluates frozen historical forecast and sensor-comparison experiments. This is a research prototype: active cell-days are not distinct fires or burned area, and the archive is not a live warning feed. Climate anomalies and operational historical harmonization are not validated.

## Run locally

Requires Python 3.12, pip and network access for initial dependency installation. Node is only needed for the JavaScript syntax check, not for serving the dashboard.

```sh
make setup
make build
make test
make serve
```

Open **http://127.0.0.1:8765**. The build generates all analysis and browser data from the six unchanged CSV files. No API keys, model downloads or paid services are required. Override the port with `make serve PORT=9000` if needed.

Equivalent commands without Make:

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m pyrosync build
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m pyrosync.server --port 8765
```

## What works

- Daily calendar, raw-count comparison, month/region selection, static-source toggle and monthly geographic evidence inspector.
- H3 resolution-8 active cell-day union, across Terra/Aqua MODIS, S-NPP VIIRS and NOAA-20 VIIRS. Map points aggregate these units into resolution-7 parents.
- Confidence/type filtering, source-row examples, input hashes, method manifest and CSV/GeoJSON downloads.
- Sensor-dropout counterfactuals and grid/confidence sensitivity experiments.
- Forecast tournament: last-week, trailing mean, weekday mean and ridge autoregression. Frozen selection/calibration windows, forward holdout scoring, empirical uncertainty bands, paired bootstrap diagnostics and a promotion gate.
- Verified evidence briefs plus a MiroFish communication-policy lab: local scenario preparation, upstream graph/simulation/report lifecycle, saved run recovery and report downloads. Cloud execution requires separately configured credentials.

## First measured results

| Country | Raw rows | Filtered vegetation active cell-days | Pre-July model choice | Q4 MAE skill vs last week | Promotion gate |
| --- | ---: | ---: | --- | ---: | --- |
| Sri Lanka | 11,654 | 8,473 | 28-day mean | −15.0% | Failed |
| Argentina | 389,118 | 182,998 | Ridge autoregression | +21.2% | Failed |

Argentina's point estimate improves, but its exploratory paired error interval crosses zero. Sri Lanka's frozen choice underperforms. Both remain research-only. Q4 is now an observed evaluation set; future tuning needs a fresh outer evaluation. Full metrics are in [evaluation_summary.json](processed_data/evaluation_summary.json).

## Structure

```text
pyrosync/            input validation, aggregation, forecasts, evidence tools, build CLI
web_app/             buildless local dashboard; generated data loaded by month
processed_data/      tracked evaluation summary; generated briefs/evidence packets
tests/               scientific invariants, input edge cases, leakage and evidence tests
docs/                architecture decisions, evaluation protocol, source attribution
modis/2025/          two country inputs + NASA attributes readme
viirs-snpp/2025/     two country inputs + NASA attributes readme
viirs-jpss1/2025/    two country inputs + NASA attributes readme
```

Large reproducible outputs are ignored by Git. Build generates per-country daily series, monthly maps, fold predictions, CSVs, evidence packets and briefs under `web_app/data/`, plus a manifest with input/code/output hashes. Country boundary data is bundled and attributed; the only optional browser network request is for fonts.

## Evidence tools

```sh
.venv/bin/python -m pyrosync brief Sri_Lanka
.venv/bin/python -m pyrosync verify Sri_Lanka claims.json
```

The claims file is a nonempty list such as:

```json
[{"name":"active_cell_days","value":8473,"evidence":"/summary/active_cell_days"}]
```

The verifier checks only supported structured claims, not arbitrary prose. The MiroFish lab keeps generated simulation reports separate from these verified claims.

## MiroFish integration

The pinned upstream backend is installed separately from the analysis environment. Its REST adapter runs synthetic stakeholder communication exercises using the selected archive month. Compare independent updates with a coordinated bulletin; both get the same observation workload and declared review capacity. MiroFish does not generate the numerical fire forecasts above.

```sh
make mirofish-setup
# Fill LLM_API_KEY and ZEP_API_KEY in .integrations/mirofish/.env.
# Also choose LLM_BASE_URL and LLM_MODEL_NAME for your provider.
make mirofish-start
```

In another terminal, `make serve`, then use **MiroFish Tabletop** in the dashboard. Prepare locally, check connection, and start the workflow. Runs and reports persist under ignored `processed_data/scenarios/`. The pilot defaults to 4 rounds, supports up to 12, and checks that 1–8 personas were prepared before starting the simulation. Extraction and report generation also incur provider usage; a round cap is not a monetary budget.

Before a simulation starts, the adapter requires exactly one prepared profile per intended fictional actor and fails the run before any paid simulation if extraction drifts, so incomparable runs are neither paid for nor scored. The first policy study (`mirofish-policies-v1`) is a recorded negative result: no role-comparable independent/coordinated pair was produced. The replacement protocol `mirofish-policies-v2` is frozen but not yet run, and no blinded human scores exist, so no policy difference is claimed. See [blinded review rubric](docs/POLICY_REVIEW_RUBRIC.md).

`make mirofish-status` checks setup and connection without exposing keys. For CLI preparation and one-step workflow advancement, see [MiroFish integration guide](docs/MIROFISH_INTEGRATION.md). Local Zep authentication and a real MiroFish JSON call through Vertex have passed. A complete cloud simulation/report has not yet been validated; lifecycle tests use a local HTTP stub.

Vertex AI is also supported through `make vertex-start`, a local relay that refreshes Google Application Default Credentials for MiroFish and its simulation subprocesses. See the Vertex section in the integration guide. A Google OAuth web-client file alone is not an authenticated Vertex credential. Optional dependencies: `make vertex-setup`.

## Design and evidence

The work for KusalPabasara's issues #2/#3/#4/#6 is documented in [Backend research and reproduction](docs/BACKEND_RESEARCH.md). Run `make history-acquire`, `make history-build`, then `make research` for the historical experiments. Full raw/history/prediction data stay out of Git; compact manifests and measured summaries are tracked. `GET /api/research` exposes the summaries for the optional research UI. Real cloud work is isolated in the manually dispatched pilot workflow; ordinary CI stays credential-free.

- [Architecture review and technology decisions](docs/ARCHITECTURE_REVIEW.md)
- [Evaluation protocol, forecasting and proposed UI A/B study](docs/EVALUATION_PROTOCOL.md)
- [Data sources and attribution](docs/DATA_SOURCES.md)
- [Original master plan](TEAM_GMORA_MASTER_PLAN.md): aspirational competition strategy, superseded by the review for current implementation and claims.
- Local PDFs: project submission requirements and Colombo judging guide.

NASA FIRMS data courtesy of NASA/GSFC ESDIS. This independent research prototype has no validated operational warning capability.
