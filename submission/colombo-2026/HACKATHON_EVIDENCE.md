# PyroSync — evidence achievable in 48 hours

This is a working hackathon research prototype. Completed surveys, agency adoption, independent operational trials, and a validated multi-decade climate record are not submission essentials in the supplied booklets. They should be future validation milestones, not promises or reasons to invent results.

## What we can demonstrate now

- The working country/month → calendar → period brief → map evidence → export journey.
- Four historical sensor-mapping comparisons, fitted and selected using earlier years.
- An exploratory simulated sensor-switch diagnostic and explicit limitations.
- Fourteen repeatable browser checks covering both countries; these are technical checks, not people answering tasks.
- Narrow fixes for source-export wording and map accessible labels.

## Historical sensor comparison

The reference is the VIIRS-only recorded active-cell union. It is another observation record, not true fire incidence. Values below measure how well mapped MODIS counts resemble that reference.

| Country | Test year | Selected mapping | Raw MODIS MAE | Mapped MAE | Error reduction |
| --- | --- | --- | ---: | ---: | ---: |
| Sri Lanka | 2023 | monthly quantile mapping | 22.84 | 16.10 | 29.5% |
| Sri Lanka | 2024 | monthly quantile mapping | 19.19 | 15.65 | 18.5% |
| Argentina | 2023 | monthly ratio | 285.32 | 110.18 | 61.4% |
| Argentina | 2024 | monthly ratio | 278.36 | 138.21 | 50.3% |

MAE is mean absolute daily count error. The mapping choice stays fixed from the original protocol. We did not switch Argentina 2024 to the better-looking test-set candidate after seeing its result.

## Simulated transition check

At each interior month boundary, construct a series using MODIS-derived values before the boundary and VIIRS observations after it. Compare its seven-day-before/after change with the all-VIIRS change on the same dates. This subtracts the reference change so genuine changes in the reference are not automatically treated as errors.

| Country | Year | Boundaries | Raw reference-relative jump | Mapped reference-relative jump |
| --- | --- | ---: | ---: | ---: |
| Sri Lanka | 2023 | 11 | 23.94 | 10.78 |
| Sri Lanka | 2024 | 11 | 21.40 | 9.54 |
| Argentina | 2023 | 11 | 275.39 | 50.17 |
| Argentina | 2024 | 11 | 272.58 | 69.40 |

Values are mean absolute reference-relative jumps in recorded active cells per day. Smaller is better in this constructed comparison. Post-switch error is zero by construction because both series then use VIIRS. This is not a real retirement/launch boundary experiment. It is exploratory analysis of already-seen 2023/2024 holdouts, not a new independent test or a revised promotion gate.

## Limits that remain visible

- Some days have no MODIS detections despite positive VIIRS observations. A fitted mapping cannot recover individual missed fire incidents.
- The cloud-free opportunity to observe is unknown. Zero detections do not establish absence of fire.
- A shared grid and a count mapping do not establish a validated climate trend, burned area, or operational early warning.
- User trials and independent AI policy review remain future work. Their absence is reported plainly; no participant scores are invented.

## Demo and technical verification

See `evidence/demo_audit.json` for all 14 checks. It tests selected counts against the data, peak month, brief and download, keyboard calendar navigation, source evidence, failed research gate, and 390px layout/24px day targets for both countries. It does not claim screen-reader certification or human task accuracy.

Reproduce from the repository root:

```sh
.venv/bin/python -m pyrosync.validation
node submission/colombo-2026/tools/audit_demo.mjs
.venv/bin/python -m unittest discover -s tests -q
```

Historical inputs must already exist (`make history-acquire && make history-build`). Serve the app on port 8765 before the browser audit (`make serve`); Playwright must be installed in `.qa`. No provider keys or paid AI calls are needed for these checks.

Evidence: `processed_data/evaluations/sensor_validation_audit.json`, `sensor_calibration_v1.json`, `experiments/forecast-v2.json`.
