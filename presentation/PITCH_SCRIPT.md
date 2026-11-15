# PyroSync — 10-minute presenter script

**Format:** play `output/PyroSync_10min_Presenter.mp4` full screen and speak live. The master is intentionally silent. Timecodes refer to the final 10:00 video. Aim for a calm 125–140 words per minute; leave space for the cursor and numbers. Do not read the bracketed stage directions.

**Core message:** PyroSync makes the measurement chain inspectable: compare observations, trace evidence, challenge models, and stop unsupported conclusions.

**Claim discipline:** “active cell-days” are observation units, not distinct fires. The product is a research prototype using archived observations. We have not established operational warning accuracy, agency adoption, policy efficacy or worldwide novelty. The supplementary evidence cards are labeled pitch views, populated from the live backend API; they are not additional dashboard screens.

## 00:00–00:25 — Open with the question

[Title. Look at the audience. Pause after the first question.]

If a satellite sees eight times more hotspots, did the landscape become eight times more dangerous—or did the instrument change?

That question sits between a striking map and a decision someone can defend.

We are Team Gmora, and this is PyroSync: a working prototype that makes satellite fire observations comparable, traceable and testable.

## 00:25–01:05 — Make the problem concrete

[Point to MODIS, then VIIRS as the cursor moves.]

These are real observations from Sri Lanka in 2025. MODIS recorded 684 rows. VIIRS on Suomi-NPP recorded 5,519. That is an eight-point-zero-seven-times difference.

But those rows are not a census of distinct fires. Instruments differ in resolution, sensitivity and observation times. The same activity can be observed repeatedly, while some thermal sources are industrial rather than vegetation burning.

If we confuse an observation count with a fire count, a technical difference can become a misleading story. Our challenge is to make that difference understandable and measurable.

## 01:05–01:25 — State the product idea

[Three commitments. Keep the delivery direct.]

Our approach has three commitments.

First, compare observations using a clearly defined common unit.

Second, preserve a route back to the original evidence.

Third, make a model earn its place against a baseline.

Those commitments connect the interface you are about to see with the backend behind it.

## 01:25–02:10 — Enter the real prototype

[Live dashboard. Region, month, raw count and active-cell count.]

This is the running product, displaying the actual archived observations.

I start with Sri Lanka and August 2025. The controls establish the country and period. The figures separate raw observations, qualifying vegetation activity, observations shared across source streams, and static thermal sources.

The central unit is an active cell-day: at least one qualifying vegetation detection in the same geographic grid cell on the same UTC day.

That definition gives us something reproducible to compare. It does not pretend that we have reconstructed individual fire incidents. The meaning of the number stays attached to the number.

## 02:10–02:55 — Show how interpretation changes

[Calendar; raw/active toggle; January, then August.]

The calendar makes a year readable at a glance. I can switch between raw detections and active cell-days, and select different months to inspect the pattern.

The toggle changes the unit we count. Validated reconstruction of individual fire events remains a separate scientific task.

Notice the explanation for quiet days. No qualifying detections in these files does not establish that there was no fire. We do not have the cloud and observation-opportunity masks needed for that conclusion.

That distinction is easy to lose in a beautiful heatmap. Here, it is part of the product.

## 02:55–03:45 — Trace a result to its source

[Map selection, evidence rows, static-source toggle.]

Now I select a mapped area. The inspector shows which source streams contributed, the timestamps, and references to the original CSV rows.

A user can investigate a result rather than accept an unexplained dot. The interface also states when the displayed source rows are only examples.

I can turn on static thermal sources. These may be valid thermal detections, but they answer a different question from vegetation activity. Separating them avoids silently mixing source types.

The map itself groups our observation units for display. These dots are not incident boundaries or burned-area polygons. The visual is useful because its meaning and evidence are inspectable together.

## 03:45–04:20 — Demonstrate a second case

[Switch to Argentina. Calendar and geographic pattern.]

The same workflow works for Argentina, our second case study.

In the 2025 input files, its raw VIIRS-to-MODIS ratio is about three and a half, compared with roughly eight in Sri Lanka. A single multiplier cannot be justified from those two ratios alone.

The product lets us compare these observation regimes without disguising them as identical landscapes. The interface remains consistent, while the backend preserves which instruments and filters produced the record.

## 04:20–05:05 — Show the first differentiator: challenge the record

[Sensor-dropout bars and grid/confidence table.]

Here is the next question: how much of this record depends on a particular source stream?

The backend removes one stream and recomputes the union. These bars show the fraction of observed cell-days retained. That is an observation-redundancy test, not a claim about the fraction of real fires recovered.

We also change grid resolution and confidence filtering. If the result changes when an analytical choice changes, that sensitivity should be visible.

This is our first differentiator: the system shows the assumptions beneath the result, rather than leaving the user to discover them later.

## 05:05–05:40 — Make the evidence portable

[Download the real evidence brief, scenario packet and fold predictions later.]

A useful analysis must leave the screen.

We can export the observation series, geographic data and an evidence brief. The brief binds its supported structured claims to specific artifact fields, and the verifier rejects unsupported claim names or altered values.

This is a bounded check, not a promise that arbitrary AI prose is always true.

The point is practical: a teammate can carry the result into another workflow and still know where its numbers came from.

## 05:40–06:20 — Show that a model can fail

[The 2025 tournament and failed promotion gate.]

The forecasting panel deliberately keeps the baseline visible.

In this original 2025 experiment, both frozen country choices failed the promotion gate. We did not relabel that as success because one candidate looked impressive after seeing the test results.

Each candidate is tested forward in time. Model selection, uncertainty calibration and holdout scoring have separate windows. We export the individual predictions, and report interval coverage alongside interval width.

Our second differentiator is that failure is a supported product outcome. A model has to earn a stronger claim.

## 06:20–07:20 — Reveal the backend depth and measured gain

[Labeled pitch evidence view; data come from the live research API.]

The next experiment goes beyond the dashboard's 2025 snapshot.

We acquired thirty official NASA files across three streams, two countries and five earlier years: almost three million source rows. The build checks provenance and hashes, handles leap years, and quarantines invalid rows with their original line numbers preserved.

We froze the evaluation plan before scoring these historical data, and excluded the already-seen 2025 holdout.

For Argentina, the ridge model chosen using earlier data reduced held-out mean absolute error by nineteen-point-two percent in 2023 and thirty-one-point-nine percent in 2024, passing the exploratory gate.

Sri Lanka's improvements remained inconclusive. These are forecasts of recorded activity counts, not proven ignition probabilities or operational alerts.

We also evaluate sensor mappings separately, so matching another instrument's record is not confused with forecasting—or with ground truth.

## 07:20–08:00 — Show the real agentic integration

[Return to the live product; open an existing completed run and download its report.]

The next layer asks a different question: how might stakeholders communicate about the same evidence?

MiroFish connects through our authenticated local bridge to Vertex AI and Zep. It supports a synthetic discussion exercise, with declared workload, roles and review-capacity assumptions.

Here, I am opening an already completed one-round run—not claiming that a new cloud simulation finishes instantly. Its report is downloadable from the actual prototype.

Generated discussion stays separate from verified observation facts and numerical forecasts. That boundary matters when adding agents to a scientific product.

## 08:00–08:40 — Show the third differentiator: validate the simulation

[Labeled backend evidence view: seven reports, one prevented run, zero comparable pairs.]

We tested that integration rather than stopping at an AI-generated report.

Across eight amended study attempts, seven reports completed. One simulation was prevented by the persona limit. But the graph and persona steps drifted or duplicated identities, leaving zero pairs that preserved our intended four actors.

So we cannot claim that one communication policy wins.

That finding tells us exactly what to fix next. The system preserves failures, flags invalid comparisons, and hands the reports to independent reviewers instead of manufacturing a confident conclusion.

## 08:40–09:15 — Explain why this product deserves attention

[The complete workflow.]

Our differentiator is the combination: observation, a common unit, traceable evidence, stress tests and held-out evaluation in one working workflow.

An analyst can explain a discrepancy. A manager can see source dependence and uncertainty. A research team can reproduce the experiment and identify which claim is not yet justified.

We do not claim to have invented fire mapping. We have built a practical route from a point on a map to a result that can be questioned, reproduced and defended.

## 09:15–09:35 — Show a credible next step

[Coverage, actor locking, users.]

Our next milestones are specific: authoritative observation-coverage data, locked identities for matched scenario tests, independent domain review, and a simpler everyday view validated with users.

We will scale the evidence before scaling the claims. Each milestone has a defined test, rather than another unchecked feature promise.

## 09:35–10:00 — Close with the ask

[Closing card. Stop explaining details; look at the audience.]

PyroSync turns fire observations into decisions you can defend.

Trace the evidence. Challenge the model. Know when the answer is still unknown.

Our ask is to validate this working prototype with fire analysts and authoritative coverage data, so the next product claims are earned.

We are Team Gmora. Thank you.

---

# Presenter rehearsal notes

- Start the video and script together. The small chapter clock supports recovery if you lose your place.
- Pause on the three figures in the problem slide, the selected source rows, and the historical improvement figures.
- Say **“recorded observations”**, **“active cell-days”**, **“exploratory gate”** and **“synthetic discussion”** precisely.
- Keep the 2025 screen results separate from the 2023/2024 backend evaluation. The video explicitly transitions between them.
- Never call the raw/active toggle a fully validated multi-decade harmonization engine.
- Do not imply that CONAE or Sri Lanka's DMC has adopted or validated the prototype. They are intended user contexts, not demonstrated customers.
- If behind time, shorten the map and export explanations; retain the problem, measured result, simulation limitation and closing ask.

# Likely judge questions

**What is unique when NASA FIRMS already maps fires?**
Our proposed differentiation is the integrated measurement-and-validation workflow: a defined observation unit, source-row provenance, sensor-dropout/grid-sensitivity tests, frozen forecast comparisons and an explicit gate on scenario claims. We do not claim worldwide first-of-kind novelty.

**Are you counting fires?**
No. We count qualifying active grid cells per UTC day. Incident reconstruction and burned-area estimation need different evidence.

**Why show a failed simulation study?**
Because generated reports are not validation. Persona drift prevented a controlled policy comparison; hiding that would make the result less credible. The next experiment needs locked identities and independent review.

**Are your forecasts ready for emergency operations?**
No. Argentina passed an exploratory recorded-count gate in two held-out years. Coverage, operational outcomes and prospective validation are still needed.

**What does the extra model complexity buy?**
We measure it against simple baselines and retain negative results. A foundation model is not automatically admitted for novelty.

**What is still missing?**
Authoritative observation opportunity/cloud information, a validated historical continuity product, prospective operational evaluation, matched actor identities and independent scenario review. The simpler default dashboard is a separate assigned workstream.
