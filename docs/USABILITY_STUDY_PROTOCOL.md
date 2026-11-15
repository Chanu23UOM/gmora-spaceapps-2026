# UI usability study protocol (preregistered, not yet run)

This document fixes the tasks, scoring and analysis for the dashboard comparison **before** any participant data is collected, so results cannot be reinterpreted after the fact. It expands the "UI A/B protocol (designed, not run)" section of [evaluation protocol](EVALUATION_PROTOCOL.md).

**Status: no participants have been recruited, no sessions run and no scores recorded.** No result, participant count, effect size or significance claim exists for this study. The companion machine-readable plan is [`experiments/usability-ui-v1.json`](../experiments/usability-ui-v1.json); the blank collection sheets are under [`experiments/usability/`](../experiments/usability/).

A cleaner-looking dashboard is not evidence of clarity. The question is whether a first-time reader can interpret what the archive does and does not establish while completing ordinary tasks.

## 1. Research question and hypotheses

Primary question: does the simplified three-view dashboard let a first-time user answer core observation questions **correctly**, without increasing critical interpretation errors?

- H1 (accuracy): correct answers per participant differ between conditions.
- H2 (safety): critical interpretation errors per participant differ between conditions.
- H3 (effort): task completion time differs between conditions.

These are two-sided. A simplification that speeds users up while increasing critical errors is a **failure**, not a trade-off, and H2 takes precedence over H3 when they conflict.

## 2. Conditions and version identifiers

| Condition | Description | Version identifier |
| --- | --- | --- |
| A — baseline | Single-page dashboard before the navigation simplification | git commit `b17fedf` |
| B — simplified | Overview / Explore / Research views, selected-period brief and focused evidence drilldown | git commit recorded at session time, plus `manifest.json` `run_id` |

Both conditions must be served from the **same generated archive build**: identical country payloads, identical `run_id`, identical fonts and colours. Record the git commit, `run_id`, browser, viewport size, input method and operating system for every session. A session whose build or `run_id` differs from the recorded plan is excluded and reported as excluded.

Only navigation and explanation presentation may differ between conditions. Data, palette, period and interaction mechanics are held constant so the comparison isolates presentation.

## 3. Participants

- Target: adults who are not members of Team Gmora and have not seen the dashboard before.
- Record self-reported prior familiarity with satellite fire data, GIS or remote sensing on a 0–3 scale **before** tasks. Familiarity is a covariate and a reporting stratum, never a recruitment filter applied after seeing scores.
- Exclusions, defined now: withdrew mid-session; technical failure preventing task completion; prior exposure to the dashboard; declined consent. Excluded sessions are counted and reported.
- No identifiable information is stored. Participants are referred to as `P01`, `P02`, … Notes must not record names, employers, faces, voices or contact details, and raw recordings are not kept. Nothing identifiable goes into the repository or any public issue.
- Consent: participants are told the purpose, that participation is voluntary, that they may stop at any time, that only anonymous task outcomes are recorded, and that the prototype is research-only and not a warning system. Verbal or written agreement is obtained and the fact of consent is logged against the participant code.

### Sample size and stopping rule

This is an explicitly **underpowered pilot**, not a confirmatory trial. Target **n = 12** (6 per condition), with a stopping rule of "stop at 12 completed sessions, or at a prearranged cutoff date, whichever comes first". Recruitment does not continue because results look promising, and does not stop because they look unfavourable.

With n = 12 the study can only detect very large differences. It is powered to surface **reproducible usability defects and interpretation failure modes**, not to estimate effect sizes. Report descriptive statistics and interval estimates; do not report p-values as if confirmatory, and do not describe the pilot as establishing that one design is better.

## 4. Design and task assignment

Between-participants assignment to A or B, randomised in balanced blocks of 4 using a documented random seed recorded before the first session. The **participant is the independent unit**; the six tasks within a participant are repeated measures, not six independent observations.

Task order is counterbalanced across participants using a Latin-square rotation so that fatigue and learning do not load onto any single task. The facilitator reads a fixed script, gives no hints, and does not define "active cell-day", "raw detection" or "cell-day versus fire" during tasks.

## 5. Tasks and scoring

Each task is scored **before** data collection against this rubric. Scoring is binary correct/incorrect, plus a separate critical-error flag. The second scorer is blind to condition where feasible; disagreements are resolved by discussion and the rate of disagreement is reported.

| # | Task | Correct answer criterion | Critical error if the participant… |
| --- | --- | --- | --- |
| T1 | Select a given region and month | Reaches the stated country and month; stated figures correspond to that selection | Reports figures from a different country or period |
| T2 | Identify peak recorded activity | Names the highest recorded month for the active metric, and names the metric | States the peak as the month with "most fires" |
| T3 | Explain a raw-versus-aggregated discrepancy | Explains that raw detections exceed active cell-days because the same area is seen by multiple pixels and repeat passes, counted once per cell per UTC day | Says the difference is false detections, errors, or double-reported fires |
| T4 | Distinguish no detections from absence of fire | States that a zero or blank period means no qualifying detections were recorded and that coverage is unknown | Asserts that no fire occurred |
| T5 | Identify research status of a forecast or scenario | Identifies the forecast as research-only / gate not passed, or the MiroFish output as a synthetic discussion, not an observation | Treats a forecast or a synthetic narrative as a verified observation or an operational warning |
| T6 | Report the activity unit | States that the metric is grid cell-days, not distinct fires or burned area | States the metric is a count of fires or an area burned |

Per participant, record: correct answers (0–6), critical interpretation errors (0–6), per-task completion time in seconds, per-task self-reported confidence (0–3, collected after each answer), and a post-session usability rating (0–10) with one free-text comment.

Confidence is used to compute **calibration**: high confidence combined with a critical error is the most serious outcome and is reported separately, because a confidently wrong fire manager is worse than an uncertain one.

### Accessibility and mobile checks

Run in every session, scored pass/fail with a reproduction note:

- **Keyboard only:** reach and operate the view tabs, region and month selects, calendar month and day tiles (arrow-key navigation), the period-brief disclosure, and the map evidence selection, with a visible focus indicator throughout.
- **Screen-reader labels:** the calendar day tiles, map points, metric tiles and live regions announce the period, unit and value, not bare numbers.
- **Mobile / touch:** at 390 px width, complete T1–T3 by touch; confirm no horizontal page scroll, that tap targets are reachable, and that the evidence panel and brief are readable without zooming.

Every reproducible accessibility or mobile defect is filed as a focused follow-up issue, or appended to the issue that owns the affected view, with the reproduction steps and the session code.

## 6. Analysis and reporting

Fixed before collection:

1. Report per-condition descriptive statistics for every measure, with the actual completed sample size and all exclusions.
2. Report differences with uncertainty intervals, described as a pilot estimate. Do not claim statistical significance from n = 12.
3. Report **all** failure modes and negative feedback, including confusion about forecasts, scenarios, coverage and activity units, and including findings unfavourable to the simplified design.
4. Report critical interpretation errors and the high-confidence-error subset separately from the accuracy headline.
5. If no difference is observed, say so plainly. A null result is the expected outcome at this sample size and must be published as such.

Prohibited in the write-up: inventing participant counts; reporting significance tests as confirmatory; describing the simplified design as "validated", "proven" or "preferred by users"; summarising only favourable comments; promoting a change on a single participant's remark.

## 7. From findings to fixes

After collection, produce a short prioritised list of changes, each grounded in a specific observed difficulty and traceable to the session codes that showed it. Rank by: number of participants affected, then whether it caused a critical interpretation error, then effort.

Then **verify the most consequential fixes** — re-run the affected task with new participants, or, where a defect is deterministic (a keyboard trap, a missing label, a stale value), demonstrate the fix with a reproducible check rather than a new session. Record which fixes were verified and which remain unverified.

## 8. Reproduction

1. Serve condition B: `make setup && make build && make serve`, then open `http://127.0.0.1:8765`.
2. Serve condition A from the baseline commit: `git worktree add ../pyrosync-baseline b17fedf`, then build and serve that worktree on a different port.
3. Record the git commit and `manifest.json` `run_id` for both.
4. Copy [`experiments/usability/session_sheet.md`](../experiments/usability/session_sheet.md) per participant and append a row to [`experiments/usability/scores.csv`](../experiments/usability/scores.csv).
5. Results, when they exist, are written to `processed_data/evaluations/usability_ui_v1.json` with the completed sample size, exclusions and all failure modes. Until then that artifact does not exist and no usability result may be cited.
