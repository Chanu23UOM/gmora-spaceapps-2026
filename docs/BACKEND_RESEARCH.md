# KusalPabasara backend work

This implements the software and experiments for upstream issues #2, #3, #4 and #6. The 2025 dashboard keeps its existing data contract and visible flow; collaborators can consume the new results through `GET /api/research` when designing the optional research view.

## Secrets and real provider setup (#2)

Upstream repository secrets are `ZEP_API_KEY`, `LLM_API_KEY` (the private local relay key), and `GOOGLE_VERTEX_SERVICE_ACCOUNT_JSON`. Non-secret repository variables hold `VERTEX_PROJECT`, `VERTEX_LOCATION`, `LLM_MODEL_NAME` and `LLM_BASE_URL`. Credentials never appear in tracked files or browser data.

The Google service account and Zep credentials were supplied by the project operator. That operator owns their lifecycle and must retain access to the provider consoles. Rotate Zep by replacing its upstream secret and ignored local `.env` value, then restart MiroFish. Rotate the Google credential in IAM, replace the upstream JSON secret and local private file, restart the Vertex relay, verify access, then revoke the old key. Rotate the local bridge key in the upstream secret and ignored `.env`, restarting both services. Values must never be placed in issues or logs. Prefer workload identity for a future durable deployment rather than copying a long-lived service-account key into more environments.

`.github/workflows/mirofish-pilot.yml` runs only through `workflow_dispatch`, on the actual upstream `main`, after the paid-pilot boolean is explicitly selected. It runs one one-round scenario. It injects secrets only after the credential-free installation/build stage, uploads only sanitized result metadata, and removes credential files at teardown. It has no fork-PR trigger and no `pull_request_target` path. Ordinary validation never receives secrets or calls providers. A workflow round/timeout cap is not a monetary budget; provider account spending limits remain the operator's responsibility.

## Historical acquisition and coverage (#3)

```sh
make history-acquire
make history-build
```

The downloader uses the [official NASA yearly catalog](https://firms.modaps.eosdis.nasa.gov/data/country/yearly_summary_files.txt) and public per-country archive URLs. It checks catalog byte size and CSV header, records product versions, acquisition ranges, catalog update times and SHA-256 hashes, and caches raw files only in ignored `.integrations/firms-history/`. It does not require an Earthdata account. `processed_data/history_manifest.json` is the small tracked acquisition manifest.

The acquired scope is three sensor streams × two countries × five years (2020–2024): 30 files, 2,966,278 source rows. The historical builder verifies hashes before loading. Seven Argentina rows fail the existing numeric validity rules (including negative FRP); they are quarantined with source line/reason in generated history metadata rather than silently corrected. Original files are unchanged. Default loading remains fail-fast; quarantine is an explicit historical-build policy. The existing 2025 data and summaries retain their definitions/results.

Leap years use actual calendar length. Source files record `present`, `missing` or `not_in_catalog`; a catalog omission is not asserted to prove a physically inoperative sensor. Daily payloads expose `complete_source_inputs`, `observation_coverage`, `activity_status` and `observed_active_cells`. The full-union `active_cells` is null when any required source input is absent. No detections in complete files is labeled **no recorded qualifying detections**, not verified absence of fire.

Coverage remains **unknown**: positive-detection country CSVs cannot establish cloud-free observation opportunity. NASA's [MOD14/MYD14 fire-mask classes](https://www.earthdata.nasa.gov/s3fs-public/2023-09/MODIS_C6_C6.1_Fire_User_Guide_1.0.pdf) and [VIIRS VNP14IMG swath classification product](https://modaps.modaps.eosdis.nasa.gov/services/about/products/viirs-land-c1/VNP14IMG.html) are authoritative inputs for a later full-mask/geolocation coverage pipeline. FIRMS [data availability](https://firms.modaps.eosdis.nasa.gov/api/data_availability/) describes product date ranges, not per-cell cloud-free opportunity. Full swath masks were not acquired; unknown coverage is retained explicitly.

## Frozen forecast and sensor-comparison experiments (#4)

```sh
make research
```

`experiments/forecast-v2.json` was frozen locally before historical acquisition/scoring. It excludes the already-seen 2025 holdout. Outer test years are 2023 and 2024, with earlier selection and calibration years. Candidate families and hyperparameters are fixed: last-week, trailing mean, weekday mean, ridge and a fixed 14-day exponentially weighted mean. There is no future weather feature or annual interpolation. Foundation models are deferred because model-weight/pretraining audits and compute resources were not part of this experiment.

Each origin forecasts seven days from past data. Selection uses earlier years only; horizon-specific interval widths use a separate earlier calibration year. Targets never cross year boundaries. Reported metrics include MAE, RMSE, WAPE, interval coverage **and width**, quarter-level MAE and exploratory paired weekly bootstrap intervals. Missing source inputs prevent scoring instead of becoming zero observations. Observation coverage is unknown, so these are predictions of **recorded activity counts**, not fire-occurrence probabilities.

| Country | Outer year | Frozen choice | MAE skill over last week | Exploratory gate |
| --- | --- | --- | ---: | --- |
| Sri Lanka | 2023 | Ridge | +14.5% | Failed |
| Sri Lanka | 2024 | Ridge | +11.5% | Failed |
| Argentina | 2023 | Ridge | +19.2% | Passed |
| Argentina | 2024 | Ridge | +31.9% | Passed |

Passing the gate admits further research review; it is not operational validation. No promotion is forced for Sri Lanka. These held-out results are now visible and must be treated as spent for future model tuning.

Sensor calibration is evaluated separately: identity, monthly ratio and monthly quantile mapping, fitted on selection years and chosen on calibration years. Held-out targets are the **VIIRS-only observed cell union**, not ground truth. Reported extremes use a threshold derived from training data. Sri Lanka selects quantile mapping in both folds; Argentina selects monthly ratio. A mapping's ability to resemble VIIRS does not reconstruct true historical fires or validate a climate trend.

Compact tracked outputs: `processed_data/evaluations/forecast_v2.json` and `sensor_calibration_v1.json`. Full fold predictions and historical daily arrays are reproducible ignored artifacts. The research API returns summaries without expanding the default dashboard.

## Real MiroFish study and honest review status (#6)

`experiments/mirofish-policies-v1.json` fixes two countries, August 2025, independent/coordinated policies, two replicate labels, one round, fixed workload/capacity and four requested fictional roles. Replicate labels are not controlled random seeds.

The initial two setup runs generated seed posts but had no active discussion and stayed in upstream interview-wait mode. They are preserved and excluded. Before scored activity, a recorded amendment introduced a small versioned upstream patch: activate prepared participants for each tabletop round, set simulated hour 09, disable post-run interview waiting and enable unbuffered progress. Both policies receive the same runtime. `integrations/mirofish-tabletop.patch` is applied idempotently by setup and its hash enters each scenario identity. The amended budget is eight scored attempts plus two excluded setup runs. Failed or excessive-persona runs are retained, not retried until a favorable narrative appears.

```sh
# Executes paid provider work only when explicitly requested:
.venv/bin/python -m pyrosync.policy_study --run
# Reconcile saved runs and generate the review handoff without new simulations:
make policy-study
```

Results record phases, upstream IDs, actual persona metadata, elapsed time, model alias, report hashes and a separate deterministic capacity queue. The runner freezes source payload snapshots and checks their hashes so a dashboard rebuild cannot change an ongoing study. The relay records usage counts/model/latency without prompts, responses or credentials. Shared relay usage is not attributed per run; monetary cost stays null without a price/invoice audit. Policy prose cannot overwrite workload/capacity results. Role/persona drift and failed runs prevent clean causal comparisons and are reported explicitly.

Review exports are under ignored `processed_data/policy_review_private/`: randomized report IDs, a scoring CSV and a separate unblinding key. Policy may remain inferable from narrative content; reviewers must record their guesses. **Independent blinded domain-review scores remain pending.** No human judgments or policy efficacy findings are fabricated. The summary explicitly abstains from an operational-benefit claim until that review is completed.

Give reviewers only the randomized Markdown files, blank score sheet and this rubric; withhold the unblinding key and run-result summary until scoring is locked. Include the deterministic observation brief as a baseline. Use at least two independent domain reviewers where feasible and report disagreement rather than averaging it away without explanation. Reconciliation preserves already entered score rows.

| Score | Unsupported claims / omissions / contradictions | Usefulness |
| --- | --- | --- |
| 0 | None found, with supporting explanation | Unusable or misleading |
| 1 | One limited issue | Limited help; substantial interpretation needed |
| 2 | Several consequential issues | Helpful for the defined communication exercise |
| 3 | Dominant or severe issues | Clear, relevant and well-supported for the exercise |

For every nonzero error score, cite a passage and the source evidence or missing support. Do not judge policy benefit from persuasive wording alone. Record whether the reviewer guessed the policy and why; this narrative experiment cannot promise perfect blinding.

### Recorded live outcome

All eight amended study attempts reached a terminal state: **seven completed reports and one prevented simulation** due to excessive prepared personas. In addition, the two earlier inactive/interview-wait setup runs remain excluded and documented. Actual persona graphs drifted or duplicated identities, leaving **zero pairs with matching intended four-person roles**. Capacity baselines remained equal within each country. This is evidence that the current upstream graph/persona step is unsuitable for an isolated causal policy comparison without identity locking; it is not evidence that either policy is better.

The shared relay recorded 223 non-streaming responses and 967,762 provider-reported tokens after the runtime patch restart. This scope includes extraction/configuration/report generation and is not a per-run bill; monetary cost remains unavailable. Results, phases, failures, actual identities and report hashes are in `processed_data/evaluations/policy_study.json`. Domain reviewers can still assess narrative quality, but a policy-benefit study requires locked actor identities and a newly frozen protocol. Issue #6 remains open for that follow-up and independent human review.
