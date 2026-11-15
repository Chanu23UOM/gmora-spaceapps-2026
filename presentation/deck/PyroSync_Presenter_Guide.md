# PyroSync presenter guide

The main deck has 10 pitch slides, followed by 4 evidence slides for Q&A. The seven-slide submission cut uses main slides 1, 2, 3, 4, 7, 8, and 10. It combines the analyst workflow with the product demo, the stress-test explanation with the forecast results, and the next steps with the closing ask.

Speak at about 120–130 words per minute, allowing time for pauses and pointing to charts. Each slide follows the 10-minute script supplied in the conversation. Main-slide text is at least 18 pt, with 23–32 pt body text and 38–78 pt headlines or numbers. Source citations and definitions are in speaker notes, not dense footers.

| Slide | Time | Spoken words |
| --- | --- | ---: |
| 1 | 00:00–01:00 | 116 |
| 2 | 01:00–02:00 | 131 |
| 3 | 02:00–03:00 | 126 |
| 4 | 03:00–04:00 | 109 |
| 5 | 04:00–05:00 | 123 |
| 6 | 05:00–06:00 | 121 |
| 7 | 06:00–07:00 | 123 |
| 8 | 07:00–08:00 | 127 |
| 9 | 08:00–09:00 | 122 |
| 10 | 09:00–10:00 | 123 |

## Slide 1 · 00:00–01:00

Imagine you are responsible for watching fire activity in your country. One satellite gives you a number. Another gives you a number eight times higher. Which one should you use? Has fire activity increased? Is one satellite seeing smaller sources of heat? Or are the instruments simply measuring things differently? Before you decide what to do, you need to understand what those numbers mean. That is the problem we are working on. Good morning. We are Team Gmora, and our product is PyroSync. PyroSync helps people compare satellite fire observations, understand the differences, and follow the evidence behind the numbers. Our idea is simple: better decisions begin with a clearer picture of what we actually know.

Presenter detail: Pause after the opening question. Do not imply operational warning capability.

Sources:
- README.md
- docs/ARCHITECTURE_REVIEW.md

## Slide 2 · 01:00–02:00

We started with NASA satellite data from Sri Lanka and Argentina. In our Sri Lanka files for 2025, MODIS recorded 684 observations. VIIRS on the Suomi-NPP satellite recorded 5,519. That is about eight times as many observations of the same country during the same year. But it does not mean there were eight times as many fires. Different instruments see different levels of detail. They pass over places at different times. The same burning area may appear in several observations. Some heat sources may also come from industrial activity. If we put all those numbers into a chart without explaining them, the chart can tell a misleading story. For someone studying fire patterns or preparing a report, that difference matters. A number is only useful when we understand what it counts.

Presenter detail: Raw rows, all types. Ratio is S-NPP VIIRS only divided by Terra/Aqua MODIS, not both VIIRS streams. The bar axis starts at zero; maximum 5,519.

Sources:
- modis/2025/*_Sri_Lanka.csv
- viirs-snpp/2025/*_Sri_Lanka.csv

## Slide 3 · 02:00–03:00

PyroSync brings these observations into one place and gives people a clear way to explore them. We organise the land into small grid cells. When a cell has at least one vegetation fire detection that passes our checks on a given day, we count that cell once for that day. We call this an active cell-day. Think of it as marking a square on a calendar: this place had recorded activity on this day. If several satellites observe that same cell that day, we keep their source details, while counting the cell-day once. This gives us a shared counting rule. It does not tell us the exact number of separate fires. But it makes the comparison clearer, and it gives users a definition they can check.

Presenter detail: Concept illustration. Active cell-day = at least one qualifying presumed-vegetation detection in an H3 resolution-8 cell on a UTC day. Cell-days are not distinct incidents or burned area.

Sources:
- docs/ARCHITECTURE_REVIEW.md
- pyrosync/pipeline.py

## Slide 4 · 03:00–04:00

Let me show you how that works. This is our burning activity calendar. Each day gives us a quick view of the activity recorded in our data. We can select a month and explore it in more detail. We can also switch between raw observation counts and active cell-days. That lets us see how the picture changes when we change the way we count. Next, we open the map. We can select an area and inspect which satellite sources contributed to it. Instead of stopping at a coloured dot, the user can ask: where did this result come from? PyroSync keeps that connection between the picture and the evidence.

Presenter detail: Screenshots captured from the real local dashboard, August 2025. Map dots aggregate resolution-8 cell-days into resolution-7 parent cells; they are not incident boundaries. Use the dashboard live if convenient. Slide-native labels remain readable; embedded UI is visual evidence, not text to read aloud.

Sources:
- web_app/index.html
- web_app/data/Sri_Lanka.json
- web_app/data/Sri_Lanka_2025-08_map.json

## Slide 5 · 04:00–05:00

Imagine an analyst preparing a monthly report. They see a rise in recorded activity and need to explain it. With PyroSync, they can compare the sources, inspect the locations, and check the original observation details. They can also view static heat sources separately, so those sources are not silently mixed into the vegetation activity count. Then they can download the data and an evidence brief to share with their team. The same workflow works for Argentina. That matters because the differences between instruments are not the same everywhere. Our two countries already show different observation ratios. A single rule that multiplies every number by the same amount would hide those differences. PyroSync helps the analyst investigate them and explain the result with evidence.

Presenter detail: This is a comparison of implemented capabilities with starting from separate CSV files, not a measured usability study, a competitor benchmark, or a claim of faster task completion.

Sources:
- README.md
- web_app/index.html

## Slide 6 · 05:00–06:00

We also built tools to challenge our own results. For example, what happens if we remove one satellite source? How much recorded activity remains? That helps us understand how much the combined record depends on each source. We can also change the grid size and the confidence filters, then see how the results change. These checks matter because every method involves choices. If a small change in our method produces a large change in the answer, the user should be able to see it. We apply the same thinking to quiet days. A day with no recorded detections does not prove that no fire happened. Clouds or gaps in observation may affect what satellites see. PyroSync makes room for that uncertainty.

Presenter detail: Each source stream is removed and the annual active-cell-day union is recomputed. Bars start at zero and have a 100% maximum. This measures observation redundancy, not the proportion of true fires recovered. Full grid/confidence sensitivity appears in appendix A2.

Sources:
- processed_data/evaluation_summary.json#/Sri_Lanka/sensor_dropout
- docs/EVALUATION_PROTOCOL.md

## Slide 7 · 06:00–07:00

We also explore a practical question: can past recorded activity help us estimate the next seven days? To test that, we compare forecasting models with simple methods, such as using last week’s values. We choose the models using earlier data, then test them on later periods they have not seen. Our historical work covers almost three million source records from 2020 to 2024. In Argentina, our selected model reduced average forecast error by about 19 percent in the 2023 test and 32 percent in the 2024 test, compared with using last week’s values. Those are promising research results. Sri Lanka’s results were less conclusive, and both models in our original 2025 experiment failed our checks for moving forward. We report those outcomes too.

Presenter detail: Forecast target is recorded quality-filtered active-cell counts, not ignition probability. Both Argentina folds passed an exploratory screening gate, not operational validation. Earlier years select ridge; a separate earlier year calibrates intervals; test years are 2023 and 2024. All bars share a zero baseline and scale 0–450 active cells/day MAE. Sri Lanka improvements are inconclusive. Both original 2025 country selections failed promotion; see appendix A1.

Sources:
- processed_data/evaluations/forecast_v2.json
- experiments/forecast-v2.json
- docs/BACKEND_RESEARCH.md

## Slide 8 · 07:00–08:00

There is another part of the problem: how people communicate about the evidence. A team may have useful data and still struggle to produce a clear, shared update. Our experimental MiroFish lab explores that question through AI-generated discussions between fictional stakeholder roles. It lets us explore separate updates and a coordinated bulletin using the same observation workload. This is a practice exercise. It does not predict how real people will behave. Our first study produced seven completed reports, but the AI did not keep the intended roles consistent across the comparisons. So we cannot yet say which communication approach works better. That gives us a clear next step: keep the roles fixed and have independent experts review the outputs. Generated discussion stays separate from our verified data.

Presenter detail: Synthetic MiroFish communication exercise, not physical fire prediction. Eight amended study attempts, seven completed reports, one prevented due to excessive prepared personas. Zero pairs maintained the intended four role identities. Two earlier setup runs excluded. Independent domain review pending. The visual depicts the policy comparison concept, not an observed successful coordination outcome.

Sources:
- processed_data/evaluations/policy_study.json
- docs/BACKEND_RESEARCH.md

## Slide 9 · 08:00–09:00

The people we want to help include fire analysts, researchers, environmental teams, and people preparing public information. For them, the value is practical. They can compare observations, investigate a surprising result, explain their method, and share the supporting evidence. Today, we have a working research prototype with a 2025 dashboard for Sri Lanka and Argentina, supported by earlier historical experiments. Our next step is to work with real users and domain experts. We want to learn which questions take them the most time, which parts of the interface need to be simpler, and what evidence they need before trusting a result. We also need better information about where satellites had a clear chance to observe. That will help us make stronger comparisons.

Presenter detail: No participant survey, usability study, agency adoption, or operational benefit has been demonstrated. The user-study plan measures interpretation correctness, errors, completion time, and usability. No invented satisfaction percentages or sample sizes. Appendix A4 explains the planned study.

Sources:
- docs/EVALUATION_PROTOCOL.md#ui-ab-protocol-designed-not-run
- docs/BACKEND_RESEARCH.md

## Slide 10 · 09:00–10:00

At the start, we asked a simple question. If one satellite records eight times more observations, what does that actually mean? PyroSync gives people a way to investigate the answer. They can compare the sources. They can follow the evidence. They can test the assumptions. And they can see when a forecast has not yet earned their trust. Our long-term vision is to make satellite fire records easier to understand and compare as instruments change over time. Our ask today is for the chance to validate this work with fire analysts, researchers, and emergency planning teams. Because the people making important decisions deserve information they can understand, question, and explain. We are Team Gmora. This is PyroSync. Clearer evidence. Stronger decisions. Thank you.

Presenter detail: Look at the audience. Pause between compare, trace, and test. End on the ask; do not promise live warnings or existing agency customers.

Sources:
- README.md
- docs/BACKEND_RESEARCH.md

## Slide 11 · APPENDIX · Q&A only

Use this table to distinguish historical results from the original 2025 dashboard experiment. Positive values mean lower average absolute error than last week. Sri Lanka is not promoted despite positive historical point estimates.

Presenter detail: 2023/2024 use frozen historical outer folds. 2025 uses October–December holdout and pre-July model choice. These experiments have separate evaluation windows. MAE reduction = 1 − selected MAE / baseline MAE. No post-hoc reselection.

Sources:
- processed_data/evaluations/forecast_v2.json
- processed_data/evaluation_summary.json

## Slide 12 · APPENDIX · Q&A only

Our default uses H3 resolution 8 with the quality filter enabled. Changing the grid or confidence rule changes observed totals. That sensitivity is visible instead of hidden.

Presenter detail: This is method sensitivity, not accuracy against a ground-truth inventory. Quality off still uses the intended source-type selection; it is not every raw thermal row.

Sources:
- processed_data/evaluation_summary.json#/Sri_Lanka/sensitivity

## Slide 13 · APPENDIX · Q&A only

Historical acquisition contains 30 official country files across three sensor streams, two countries, and five years. The total is 2,966,278 source rows. The dashboard separately uses the 2025 archive.

Presenter detail: Official catalog: https://firms.modaps.eosdis.nasa.gov/data/country/yearly_summary_files.txt . Seven Argentina records are quarantined under explicit numeric validity rules. Source rows remain unchanged. NASA FIRMS data courtesy NASA/GSFC ESDIS. Independent project; NASA source attribution does not imply endorsement. Product data: MODIS Terra/Aqua, S-NPP VIIRS, NOAA-20 VIIRS. No validated operational warnings, burned-area estimates, or 26-year harmonized record.

Sources:
- processed_data/history_manifest.json
- docs/BACKEND_RESEARCH.md
- docs/DATA_SOURCES.md

## Slide 14 · APPENDIX · Q&A only

There are no completed participant surveys or usability trials in this repository. This is the existing planned A/B protocol, not a reported survey result.

Presenter detail: The plan compares calendar + raw sensor counts with the same data plus unit explanations, source agreement, and evidence inspection. Primary measure: scientifically correct answers per participant. Secondary measures: critical interpretation errors, task completion time, confidence calibration, usability. Sample size and stopping rules must be set before collecting results. No fabricated sample sizes or significance.

Sources:
- docs/EVALUATION_PROTOCOL.md#ui-ab-protocol-designed-not-run
