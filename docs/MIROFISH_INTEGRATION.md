# MiroFish integration

PyroSync connects to the official [MiroFish backend](https://github.com/666ghj/MiroFish) at the exact source revision in `integrations/mirofish.json`. It is a separate local service, with its upstream license and isolated Python environment. PyroSync's existing numerical forecasts and verified evidence briefs remain independent.

## Install and configure

The current workspace has the source and CPU runtime installed. For a fresh checkout:

```sh
make setup
make build
make mirofish-setup
```

The helper requires Git and [uv](https://docs.astral.sh/uv/getting-started/installation/). It checks out the pinned upstream revision, installs CPU Torch and the backend dependencies, and creates a private local `.integrations/mirofish/.env` from the tracked example. It does not overwrite an existing `.env`. Compatibility constraints from upstream's lockfile avoid the MCP 2.x FastMCP import break in CAMEL 0.2.78. The simulation dependencies are substantially larger than PyroSync's two analysis dependencies.

Configure these values in `.integrations/mirofish/.env`:

- `LLM_API_KEY`: provider API key.
- `LLM_BASE_URL`: OpenAI-compatible provider endpoint.
- `LLM_MODEL_NAME`: a model supported by that endpoint.
- `ZEP_API_KEY`: Zep Cloud key for upstream graph construction.

Keep keys in the ignored file. Do not enter them in the dashboard or commit them. PyroSync only returns their presence as booleans. Upstream reads its own `.env`; account balances and provider authentication are not established by a local presence check.

### Vertex AI provider

For Vertex, run `make vertex-setup` and configure the ignored MiroFish `.env`:

```dotenv
LLM_BASE_URL=http://127.0.0.1:5002/v1
LLM_API_KEY=GENERATE_A_PRIVATE_RANDOM_LOCAL_BRIDGE_KEY
LLM_MODEL_NAME=google/gemini-3.8-flash
VERTEX_PROJECT=YOUR_GOOGLE_CLOUD_PROJECT_ID
VERTEX_LOCATION=global
```

The local bridge key authenticates MiroFish to the relay; it is not a Google access token. Select a Gemini model available in the chosen project/location. An OAuth web-client JSON identifies an application and does not grant Vertex access. Do not point `GOOGLE_APPLICATION_CREDENTIALS` at that web-client file.

Sign in as an account authorized for the target project using [Google's local ADC flow](https://docs.cloud.google.com/docs/authentication/set-up-adc-local-dev-environment):

```sh
gcloud auth application-default login --project=YOUR_GOOGLE_CLOUD_PROJECT_ID
```

The project needs Vertex API access, appropriate IAM permissions and billing. The bridge uses Application Default Credentials, independently of the active `gcloud` CLI account; it does not fall back to an unrelated configured project. Use `GOOGLE_APPLICATION_CREDENTIALS` only for a supported service-account/federated credential when that is your intended authentication method.

For a service-account file, keep a private copy under ignored `.integrations/`, restrict it to mode `0600`, and set `GOOGLE_APPLICATION_CREDENTIALS` to its absolute path in MiroFish's ignored `.env`. The relay explicitly loads that file and uses `VERTEX_PROJECT` as the target/quota project. An explicit file takes precedence over ambient ADC; no `gcloud` sign-in is required when that credential is valid.

Start `make vertex-start` in a separate terminal, then `make mirofish-start` and `make serve`. The loopback relay replaces its local key with Google authorization and lets the official authentication library refresh expiring credentials before requests. This also covers MiroFish's simulation subprocesses. It relays only chat-completion requests to the configured Vertex project, supports streaming, and does not log prompts or credentials. Live model access must be checked after sign-in; a healthy local relay alone does not establish Google authorization.

Start two terminals:

```sh
make mirofish-start
```

```sh
make serve
```

Open `http://127.0.0.1:8765`, select a country/month, and scroll to **MiroFish Tabletop**. The upstream frontend is not required. The bridge defaults to `http://127.0.0.1:5001`; `PYROSYNC_MIROFISH_URL` can select another loopback port. Remote HTTP proxy targets are rejected. MiroFish's backend itself has no API authentication; keep it local.

## What a scenario means

The seed includes the exact artifact hash, selected daily active-cell counts, four named fictional stakeholder roles, policy and declared capacity. One cell-day is assumed to generate one review ticket. These are synthetic workload units, not verified incidents or operational staffing recommendations.

Policy A: each stakeholder issues independent evidence-grounded updates. Policy B: a coordinator collects updates into one daily evidence-grounded bulletin. Both get the same observations and capacity assumptions. The independently computed capacity queue starts empty and is identical across policies; conversation does not automatically change processing throughput. The engine may suggest communication benefits, but it cannot establish them from generated prose alone.

The upstream engine simulates Reddit/Twitter-like interactions. This integration uses only its simulated Reddit discussion board; it does not publish to real social media or send messages. It requests fictional analyst, field coordinator, agricultural liaison and skeptical reviewer personas. Graph extraction is stochastic and may not recover exactly these four; PyroSync checks the prepared profile count before running and refuses more than eight. It does not claim validated role fidelity.

Local preparation makes no provider calls. **Start/resume** uploads the seed summary and uses the upstream LLM/Zep services. Default four rounds, maximum twelve, one platform, template-based profiles and graph memory updates disabled reduce pilot work. They do not impose a dollar cap: ontology extraction, graph construction, generated configuration, per-round reasoning and reporting have their own costs. Provider-side spending limits remain separate.

## Lifecycle and recovery

The bridge follows these upstream API contracts:

1. Multipart Markdown seed to `POST /api/graph/ontology/generate`.
2. `POST /api/graph/build`, poll `GET /api/graph/task/{id}`, confirm project graph readiness.
3. `POST /api/simulation/create` and `/prepare`, poll `/prepare/status`.
4. Check prepared profiles, then `POST /api/simulation/start` with bounded rounds, no force restart, Reddit only.
5. Poll `GET /api/simulation/{id}/run-status` until completed/stopped. Failures do not become reports.
6. `POST /api/report/generate`, poll `/generate/status`, retrieve completed report.

Each transition persists IDs and phase in `processed_data/scenarios/{scenario_id}/state.json`. The seed, full assumptions and source hash persist alongside it. The dashboard remembers the latest scenario ID locally; after reload it restores state. A server restart requires Start/resume again; no paid run is launched automatically on startup. Background orchestration has a 45-minute local polling window; it does not cancel an upstream run when that window ends. Resume continues status checks from the saved phase.

Before every upstream mutation, a pending-operation marker is saved. A network timeout or malformed success response leaves that marker intact. The bridge refuses automatic retry because the upstream may already have performed the operation. Reconcile the project/task/simulation/report IDs in local MiroFish before manually repairing state. Do not clear a pending marker without confirming whether the mutation occurred. No create endpoint is represented as exactly-once.

Completed Markdown/JSON reports are stored separately and explicitly marked **unvalidated synthetic narrative**. The dashboard exports report text without rendering model HTML or admitting its numbers to the evidence verifier. No simulated response delay, casualty estimate or accuracy metric is promoted to observed fact.

## CLI

```sh
make mirofish-status
.venv/bin/python -m pyrosync mirofish prepare Sri_Lanka --month 2025-08 --policy independent --max-rounds 4
.venv/bin/python -m pyrosync mirofish prepare Sri_Lanka --month 2025-08 --policy coordinated --max-rounds 4
.venv/bin/python -m pyrosync mirofish status SCENARIO_ID
.venv/bin/python -m pyrosync mirofish advance SCENARIO_ID
```

CLI `advance` performs one transition, without a long polling loop. Dashboard Start/resume drives the full background workflow. Preparing the same evidence/assumptions/policy returns the same local scenario; `--replicate 1` creates a distinct run for repeated simulation. Replicate labels are not random seeds: upstream has no exposed seed contract here.

## Evaluation and current limits

Tests exercise the real HTTP adapter against a local API stub through the complete lifecycle, including multipart upload, bounded start parameters, policy isolation, deterministic capacity baseline, malformed/failed responses and persistence across restart. Local server tests cover preparation and cross-origin rejection. Browser checks cover offline setup, preparation, downloads, reload recovery and mobile layout. Upstream app initialization/health and OASIS imports are separate runtime smoke checks.

**Local provider smoke checks passed:** service-account authentication and a real MiroFish JSON request through the Vertex relay, plus a read-only Zep graph listing. A complete real LLM/Zep simulation and generated report remain unvalidated. Stub results are not recorded as MiroFish research findings.

To evaluate policy usefulness, preregister a question set; use matched independent/coordinated runs with identical evidence and assumptions; repeat across runs and countries; have blinded domain reviewers score unsupported claims, omission of uncertainty, internal contradictions and usefulness. Record provider model/version, actual personas, round counts, tokens/cost and latency. Generated confidence or agreement is not forecast calibration. Numeric capacity outcomes require a separate validated operational model, not counting simulated posts.
