# Evaluation protocol

The dashboard distinguishes observation aggregation, forecasting, explanation verification and UI usability. They need different evidence; one aggregate accuracy number would be misleading.

## Observation pipeline

Checks: reproduce raw row counts and type counts; validate coordinates, timestamps, finite FRP, positive footprint and confidence range; preserve file SHA-256 and CSV line numbers. Exact duplicates are audited. Aggregation obeys `multi-source cell-days ≤ cell-days ≤ filtered rows ≤ raw rows` daily and annually. Monthly map totals reconcile with daily totals.

Counterfactuals: remove each source stream and recompute the annual union; report retained fraction and lost cell-days. Report H3 7/8/9 × quality filter on/off. These are ablations and sensitivity analyses, not precision or recall against true fires. MODIS–VIIRS Jaccard uses exact same-cell/day occupancy, not nearest-neighbor event matching or ground truth.

Missing coverage prevents detection-rate/recall estimates. No weather adjustment, climatology, threshold-based emergency classification, burned-area validation or historical inter-calibration is claimed.

## Forecast tournament (implemented)

Target: daily union of quality-filtered vegetation H3 resolution-8 cells, across all three streams. Grid/quality definition is fixed before comparing models. Annual data start is January 1, 2025; missing recorded detections are count zero with unknown observation coverage.

Candidates, fixed before results:

- Last-week seasonal naive: repeat the last 7 daily counts.
- Trailing-28 mean: constant daily prediction.
- Weekday-8-week mean: average of the corresponding weekday in the last 56 observations.
- Ridge autoregression: log1p target and lags 1/2/7/14/21/28, lagged means 7/28, weekly sine/cosine. Alpha=10 fixed; standardized using each training window only; at most 112 training target days, recursive horizon. Nonnegative predictions capped at 3× the training maximum to bound unstable extrapolation. No annual seasonality is inferred.

Origins start after 84 days and advance 7 days. Each produces a 7-day forecast; test horizons do not overlap. Blocks crossing selection-window boundaries are dropped.

1. **Selection:** origins whose targets end by June 30. Select lowest MAE separately per country. Tie order is fixed model order.
2. **Calibration:** July 1–September 30 target blocks; use separate horizon-wise absolute residuals for each candidate. Freeze band widths before Q4. Calibration data do not choose the candidate.
3. **Holdout:** October–December target blocks. Refit at each origin using only data preceding that origin, as a deployed rolling forecast would. The model family, feature definition and alpha remain fixed. There are 13 origins (91 scored days), not 91 independent experiments.
4. **Archive continuation:** refit the pre-July choice through December 31 and forecast January 1–7, 2026. This is not a current forecast. The displayed forecast remains research-only when its gate fails.

MAE is the selection metric. RMSE and WAPE are secondary; WAPE is undefined for an all-zero actual total. Forecast values are expected counts and can be fractional. The UI reports actual interval coverage alongside the 80% calibration target; wide intervals can cover well while being unhelpful. Full artifacts also contain interval width. With only 13 calibration values per horizon and temporal dependence, the residual bands carry no distribution-free coverage guarantee.

The promotion gate requires the selected candidate to beat the last-week baseline by ≥5% holdout MAE and have an exploratory paired 95% moving-block bootstrap interval entirely below zero for its MAE difference. The bootstrap uses adjacent pairs of weekly origin errors, 2,000 resamples, seed 42. This is a screening gate, not proof of operational validity. Short single-year holdouts do not establish seasonal robustness or robust hypothesis-test significance. Failure means **do not promote**. A different candidate looking good in Q4 does not allow retrospective reselection.

All origins, training-end dates, actual values and predictions are downloadable. A regression test mutates Q4 observations and confirms that selection, calibration predictions and the first Q4 prediction do not change. This follows the time-order principle described in [scikit-learn's time-series validation documentation](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html); the implementation uses custom explicit folds, not random cross-validation.

Holdout status: these 2025 outputs are now visible to developers. Treat Q4 as **spent** for future model tuning. Freeze this first comparison; use genuinely unseen future periods or a newly preregistered outer evaluation for later candidates. Foundation model pretraining might include dates from this archive; document that limitation before calling a comparison leakage-free.

## Brief and agent evaluation (implemented boundary)

Positive: generated structured claims exactly match allowlisted artifact pointers; briefs bind to country and artifact hash. Negative: fabricated values, unsupported claim names, invalid evidence pointers, empty claims, and wrong-country packets must fail. This validates the bounded tool contract, not free-form LLM truthfulness. MiroFish is integrated separately for synthetic communication exercises; no cloud LLM simulation has been evaluated here without credentials.

Before autonomous narration, create a fixed question set with expected evidence and abstentions (including "how many distinct wildfires?", "what burned area?" and "is today an emergency?"). Score supported-claim precision, evidence-link accuracy, abstention accuracy, latency and cost. Compare plain retrieval + templates against an LLM using the same tool outputs, with blinded human scientific review. Require zero unsupported numeric claims in the release test set; report sample size rather than implying universal reliability.

## UI A/B protocol (designed, not run)

Question: does showing sensor evidence improve interpretation without making the task unreasonably slow?

- A: calendar + raw sensor counts. B: same data plus active-cell unit explanations, source agreement and evidence inspector. Match colors, period and interaction mechanics to isolate evidence presentation.
- Tasks: identify the peak recorded month; explain a raw-versus-grid discrepancy; identify an industrial source; distinguish no detections from confirmed fire absence; decide whether the forecast passed its gate.
- Primary: scientifically correct answers per participant. Secondary: critical interpretation errors, task completion time, confidence calibration and usability rating.
- Randomize participants between conditions or counterbalance order with separate matched tasks. The participant is the independent unit. Define exclusions, minimum detectable difference, sample-size rationale and stopping rule before collecting results. Report effect intervals and all failures. Do not invent sample sizes or significance.

No participant data collection, live traffic experiment or event tracking is enabled in this prototype.

## Reproduction

`make setup && make build && make test`. Results are in `processed_data/evaluation_summary.json`; detailed artifacts, source hashes and fold predictions are under `web_app/data/`. No claimed acceptance threshold is changed automatically after observing results.
