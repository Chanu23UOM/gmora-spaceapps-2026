# PyroSync — Colombo 2026 submission assessment

Evaluated after fast-forwarding `main` from `0fde77d` to upstream `4b39801` on 2026-11-15 (Asia/Colombo). Source documents are the two PDFs supplied by the user. They are submission requirements, not evidence that the product has achieved their ambitions.

## Required format

| Requirement | Source | Package decision |
| --- | --- | --- |
| Five-minute live presentation, then five-minute Q&A | Judging guide p. 4 | Replace the earlier ten-minute competition pitch with `LIVE_PITCH_5_MIN.md` and seven slides. |
| Summary of 50–200 words | Components p. 1; judging guide p. 6 | `SUMMARY.txt`: 138 words. |
| Exactly one demo link: at most seven slides, including title, OR a 30-second video with English subtitles | Components p. 1; judging guide p. 7 | Canonical demo is the 30-second subtitled video. The seven-slide deck supports the live pitch, not a second URL in the demo field. |
| Public access without password, registration, or permission | Components p. 1; judging guide p. 7 | Public artifact links must be checked anonymously after publication; local files alone do not satisfy this. |
| No under-18 names, voices, or likenesses | Components p. 1; judging guide p. 7 | Product screenshots and abstract visuals only; synthetic adult narrator. No human voice recordings or portraits. |
| At least one official NASA resource; list resources actually used | Components p. 2; judging guide p. 8 | FIRMS country archives are core input, with MODIS and VIIRS sources named and linked. Confirm the final chosen challenge resource list when entering the official form. |
| Declare SI/AI use and do not generate or modify NASA marks | Components p. 2; judging guide p. 9 | Explicit coding, research, authoring, simulation, and synthetic-voice disclosure. No NASA logos/flags/mission insignia included. |
| Details: operation, method, benefits, aims, tools | Components p. 1 | Copy-ready project description in `PROJECT_SUBMISSION.md`. |
| Partner data optional; cite other code/text/images used | Components p. 2 | No CONAE data or agency adoption claimed; bibliography names actual source material and dependencies. |

## Provisional rubric assessment

These are internal estimates to prioritise work, not judge scores or predicted awards.

| Criterion | Estimate / 10 | Evidence | Remaining weakness |
| --- | ---: | --- | --- |
| Impact | 6 | Useful analyst tasks; Sri Lankan and Argentine cases; portable briefs and evidence | No measured user benefit, adoption, or operational impact; two-country scope |
| Creativity | 7 | Shared observation unit plus evidence drilldown, sensor-removal checks, and an abstaining model gate | Integrated workflow is a proposed differentiator; worldwide novelty unproven |
| Validity | 7 | 41 automated tests passed; source provenance; historical held-out evaluations; explicit failed gates | Observation opportunity unknown; true-fire accuracy unvalidated; UI study and independent policy review not run |
| Relevance | 8 | NASA MODIS/VIIRS core data, common units, calendar, region/time selection, exports, historical sensor experiments | Full operational historical harmonization, climate baselines, and sensor-transition continuity unvalidated |
| Presentation | 8 | Seven clear slides; 541-word script; actual UI and measured results; concise ask | Rehearsal and public-link verification required; do not submit the older ten-minute video as the 30-second demo |
| Total | 36 / 50 | Internal assessment only | No score guarantee |

## Strongest subcategory opportunities

Best Use of Data and Best Use of Science have the clearest evidence. Local Impact has plausible Sri Lankan relevance but no demonstrated agency use. Storytelling and Art & Technology are supported by the visual calendar and clear explanation. Global Connection is a two-country research context, not an international partnership. Best Mission Concept is not a close fit: this project does not design a space mission.

## Upstream changes reflected in this package

- Overview, Explore, and Research are separate views.
- The selected-period brief and two-minute tour give nontechnical users a clear path.
- Map selection exposes which instruments and source rows support a result.
- Calendar controls now have at least 24px touch targets; map nested-interactive and disclosure issues were fixed. These fixes do not establish full accessibility conformance.
- The MiroFish adapter now checks exactly one profile per intended actor before simulation. Protocol v2 is frozen, not run. The v1 negative result remains preserved.
- The usability protocol, tasks, rubric, and sample rationale are preregistered. The score sheet has no participant results. No survey scores may be claimed.

## Current evidence and claim limits

2025 dashboard: Sri Lanka has 11,654 raw observations and 8,473 quality-filtered vegetation active cell-days; Argentina has 389,118 and 182,998. These are different units, not separate-fire counts.

Historical inputs: 30 official archive files; 2,966,278 source rows; three streams, two countries, 2020–2024. Argentina's selected ridge model reduced MAE versus repeating last week by 19.2% (2023) and 31.9% (2024), passing exploratory gates. Sri Lanka's improvements remained inconclusive. Both original 2025 selections failed promotion. Gate passage is not operational validation.

AI v1: seven completed reports out of eight amended attempts, one prevented simulation, zero role-comparable pairs. No policy winner. New actor checks and a frozen v2 protocol are implementation progress, not new efficacy results.

No live alerts, real-fire recall, burned-area estimates, avoided losses, survey results, or validated multi-decade climate trends are claimed.

## Verification performed

- `git fetch upstream`, then `git merge --ff-only upstream/main`.
- `.venv/bin/python -m unittest discover -s tests -q`: 41 passed.
- `node --check web_app/app.js`: passed.
- Updated UI screenshots captured from the local app after pulling upstream.
- Final presentation page count, summary length, narration/media duration, public access, and render checks recorded in `PACKAGE_VALIDATION.json`.
