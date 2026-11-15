# PyroSync: architecture and scientific review

Review date: 2026-11-15. This document supersedes the original master plan wherever they conflict. The original plan is a proposal, not evidence that its described system exists.

## Product decision

Build an **instrument-aware fire observation lab**: show what changed in the landscape, what changed with the instrument, and what cannot yet be inferred. The differentiator is a traceable chain from raw CSV rows to a measured result, an uncertainty estimate, a stress test and a verified brief. This is our proposed positioning, not a claim of research novelty.

The first deliverable uses the six available 2025 files for Sri Lanka and Argentina. It must reproduce counts, preserve provenance, expose spatial aggregation assumptions, evaluate forecasts forward in time, and serve an interactive local dashboard. No API keys or paid services are required.

## Evaluate the original proposal

| Original choice | Assessment | Current decision |
| --- | --- | --- |
| Python processing → precomputed browser data | Good separation; avoids making browsers parse 400k CSV rows | Keep; split map payloads by country/month |
| React/Next + Plotly + Deck.gl + MapLibre | Reasonable at scale, excessive for the first two-country snapshot | Buildless ES modules + SVG, no frontend runtime dependency; introduce a map engine when interaction scale requires it |
| Standardize both sensors | Necessary; does not make spectral bands or confidence values equivalent | Preserve source identity; use explicit quality filters, not invented confidence probabilities |
| `scan × track` footprint | Useful measurement metadata | Preserve source footprints; do not assert FRP/area removes sensor bias |
| H3 clustering | Useful common observation unit | Unique `(H3 resolution-8 cell, UTC date)`; call it active cell-days, not fire events |
| Day/night bins plus daily deduplication | Ambiguous definition and potential double counting | One UTC daily union regardless of daynight; retain exact source timestamps |
| Fixed pixel matching | Cell boundaries and grid size introduce sensitivity | Report resolutions 7/8/9, quality-filtered versus all-confidence results |
| One multiplier for all places | Unsupported | No global multiplier; historical calibration requires multi-year data and independent evaluation |
| Empirical quantile mapping | Candidate method, not proof of validity; can flatten real extremes | Defer; compare against seasonal scaling and identity on withheld years and regions |
| Guaranteed removal of 2012/2018 jumps | Overclaim: smoothness alone can be manufactured | Require transition tests, uncertainty and independent validation |
| “MODIS misses 85% of fires” | Observation-count ratios cannot establish event recall | Remove this claim; distinguish pixels, observations, active cell-days and true fire events |
| `type=0` wildfire isolation | Includes vegetation burning with unknown cause | Say presumed vegetation; do not label agricultural burning as wildfire |
| Industrial detections as false positives | They can be valid thermal anomalies outside the target use case | Separate type 2 rather than claim detector error |
| FRP converted into cumulative energy | Requires time integration and sampling assumptions | Report source FRP metadata only; no energy or emissions estimates |
| Climate anomaly Z scores from 2025 | One annual cycle cannot establish a climatological baseline | No climate alert labels; no fabricated historical years |
| R² > 0.89 slide claim | No supporting experiment | Remove; persist measured MAE/RMSE/WAPE and interval diagnostics |
| 26-year/global product | The local repo has one year and two countries | Restrict current claims to that coverage |

Observation-only CSVs have no non-fire pixels, cloud masks, effective observation opportunity or a validated fire-event inventory. A zero is a zero **recorded qualifying detection count**, not confirmed fire absence. Dataset completeness and instrument availability need separate manifests before historical harmonization.

NASA describes VIIRS points as approximate pixel centers, confidence as an algorithm quality indicator, and FRP as pixel-integrated radiative power. These do not establish equivalence between instruments. See the [NASA VIIRS attribute description](https://firms.modaps.eosdis.nasa.gov/content/descriptions/FIRMS_VIIRS_Firehotspots.html). NASA also advises against deriving burned area directly from hotspot locations: [FIRMS training Q&A](https://appliedsciences.nasa.gov/sites/default/files/2025-05/Part%203%20FIRMS%202025%20Q%26A%20Session.docx.pdf).

## Implemented structure

```text
raw FIRMS country CSVs (unchanged)
  → data.py: schema/range/time checks + file hashes + CSV line provenance
  → pipeline.py: quality/type separation + H3 union + counterfactual tests
  → forecast.py: baselines + ridge + frozen temporal evaluation
  → evidence.py: structured evidence claims + exact verifier + brief/scenario packet
  → __main__.py: reproducible build, manifest, CSV/JSON/Markdown artifacts
  → web_app/: monthly explorer, map, tournament and export UI
```

Artifacts declare their definition and limitations. Maps sum resolution-8 cell-days into resolution-7 parent cells and display their centers. They are not incident boundaries or exact pixel polygons. Up to three original CSV rows accompany each mapped monthly cell. Input hashes, code hash, output hashes and runtime versions are recorded; the run ID excludes wall-clock time.

Exact duplicate CSV rows are audited in the manifest. The set union is idempotent for duplicates; raw row counts intentionally remain raw. All six supplied files have zero exact duplicate rows. Neighboring cells can still describe a single fire, and independent fires can share a cell-day. This is not event reconstruction.

Monthly map files are generated locally and ignored by Git. The small evaluation summary and source code are tracked. This avoids committing both raw input and another large derived dataset. Country boundaries are a bundled Natural Earth visualization asset; their source and attribution are in `DATA_SOURCES.md`.

## Technology admission decisions

| Technology | Fit and decision | Evidence required to advance |
| --- | --- | --- |
| H3 | Implemented; shared spatial indexing and explicit unit | Sensitivity, edge tests and footprint-aware matching on reference cases |
| Ridge autoregression | Implemented alongside 3 simple baselines | Past-only holdout skill and uncertainty behavior |
| TimesFM / Chronos | Promising additional forecasting candidates; not installed | Exact model/version, pretrained cutoff, compute cost, same frozen origins and no future weather; account for possible pretraining contamination |
| Weather-informed model | High priority after more data | Weather forecast vintages available at issue time; observed future reanalysis cannot stand in for forecasts |
| MiroFish | Integrated REST workflow and isolated upstream runtime; cloud execution awaits credentials | Fixed assumptions, independent versus coordinated communication, repeated runs and independent domain review |
| Agent tools | Implemented as bounded local evidence/brief/verification CLI; deterministic workflow roles | Measure unsupported-claim rejection, reproducibility and analyst effort before adding autonomous loops |
| RAG / vector database | No current need: small, structured dataset with direct row pointers | Add only when a versioned document corpus improves a defined decision |
| Live NASA ingestion | Deferred; 2025 archive is not live data | Availability manifest, product-version controls, missing-day handling and data freshness UI |
| UI A/B experiment | Design in evaluation protocol; not a live user experiment | Participant consent, predefined task/error measures and enough independent participants |

[MiroFish's source project](https://github.com/666ghj/MiroFish) describes a multi-agent prediction/simulation engine. This is not evidence of skill for ignition or fire spread. Our inference is that it fits **response-policy scenarios** better than physical forecasting. The generated scenario handoff includes analyst, coordinator, agricultural liaison and reviewer roles. It supplies historical workload, not predicted human behavior. Do not treat simulation agreement as real-world validation.

[TimesFM's official repository](https://github.com/google-research/timesfm) describes a pretrained time-series model. It belongs in the forecast tournament as a challenger, not as an automatic upgrade. Model weights, hardware and model provenance add meaningful cost; the current forecasting interface is deliberately small so future candidates can use the same history-only input contract.

## Agentic work: what is real now

`python -m pyrosync brief Sri_Lanka` creates a bounded evidence brief. `python -m pyrosync verify Sri_Lanka claims.json` checks proposed structured claims. Supported claim names and JSON pointers are allowlisted. Unknown metrics, wrong values, wrong types and wrong pointers fail. The brief also verifies artifact hash, country and required claim completeness.

The evidence brief remains a deterministic three-role workflow with no LLM calls. A separate MiroFish lab now connects to a pinned upstream service for explicit synthetic communication simulations with fictional personas. Only starting that lab invokes the upstream LLM/Zep workflow. Its generated prose is not admitted to the verified observation claims or numeric forecast benchmark. See `MIROFISH_INTEGRATION.md` for setup, lifecycle and validation limits.

## Next scientific increments, in order

1. Acquire several complete overlap years; record exact product collections, sensor availability and observation coverage. Verify the actual archive availability rather than equating launch dates with data coverage.
2. Add independently verified reference episodes and a spatial/temporal matching experiment. Compare overlap and ±distance/time matches, including boundary sensitivity.
3. Fit alternative inter-sensor mappings using only training years. Hold out entire years, seasons and regions; preserve extreme-event behavior. Do not choose a mapping merely because it smooths a chart.
4. Add weather and land cover with issue-time availability controls. Evaluate multi-year rolling origins and validate forecast intervals in active and quiet seasons.
5. Configure the integrated MiroFish service and run a communication-policy exercise with domain reviewers. Establish usefulness against a predefined baseline before making efficacy claims.

These are data and validation dependencies, not features that can be honestly substituted with generated history.
