# Blinded review rubric — MiroFish communication-policy study

Instructions and scoring rules for the independent reviewers of the synthetic tabletop reports. Protocol: [`experiments/mirofish-policies-v2.json`](../experiments/mirofish-policies-v2.json). See also [MiroFish integration guide](MIROFISH_INTEGRATION.md) and [evaluation protocol](EVALUATION_PROTOCOL.md).

**Status: no human scores have been recorded.** The v1 attempt produced zero role-comparable pairs, so there is nothing yet to compare. This rubric is frozen so that scoring cannot be designed around results once reports exist.

## What is being judged

Each document you will read is either a **generated synthetic discussion report** or a **deterministic evidence brief** built directly from the archive. You will not be told which, nor which communication policy produced it.

You are judging **communication quality**: whether the document's statements are supported by the observations it was given, whether it keeps the uncertainty, and whether it would be useful to someone deciding how to communicate about recorded satellite detections.

You are **not** judging writing style, length, or whether the scenario sounds realistic. You are not judging fire-management decisions, and no document here can tell you anything about actual fire behaviour.

## Essential background for scoring

The underlying data supports only these kinds of statements:

- **Active cell-day:** one H3 resolution-8 grid cell (~0.74 km²) with at least one quality-filtered vegetation detection in one UTC day. It is an observation unit. It is **not** a fire, a count of fires, or an area.
- **Raw detections:** all CSV rows before merging overlapping pixels and repeat satellite passes. Raw counts exceed cell-days because the same ground area is seen repeatedly, **not** because the surplus is false.
- **Coverage is unknown:** these files carry no cloud or overpass masks. Zero detections means nothing qualifying was recorded, **not** that no fire occurred.
- **Reviewer capacity** in the scenario is a *declared assumption*, not a measured staffing level. The queue/backlog figures are computed deterministically outside the simulation.
- Source type 0 includes agricultural burning; no wildfire-versus-agricultural attribution is available.

Any claim beyond these — a number of distinct fires, a burned area, a cause, a response time, lives or property affected, an emergency classification, or an assertion that discussion improved the backlog — is **unsupported**, regardless of how reasonable it sounds.

## Scoring

Score each document on four 0–3 scales. Record every score in `processed_data/policy_review_private/scores.csv` against the document's blind ID, with your reviewer code.

### A. Unsupported claims (0–3) — lower is better

| Score | Criterion |
| --- | --- |
| 0 | No statement exceeds what the observations support. |
| 1 | One minor overreach, hedged or incidental. |
| 2 | Several overreaches, or one clear unsupported quantitative claim. |
| 3 | Central conclusions rest on unsupported claims (distinct fires, burned area, cause, response times, efficacy). |

### B. Uncertainty omissions (0–3) — lower is better

| Score | Criterion |
| --- | --- |
| 0 | Coverage limits, the cell-day unit and the assumed capacity are all stated where they matter. |
| 1 | Mentioned, but thinly or only once in passing. |
| 2 | A material limitation is omitted where it changes the reading. |
| 3 | Reads as a confident account of what happened, with the limitations effectively absent. |

### C. Contradictions (0–3) — lower is better

| Score | Criterion |
| --- | --- |
| 0 | Internally consistent; figures agree between sections. |
| 1 | A minor inconsistency in wording or emphasis. |
| 2 | Conflicting numbers or conflicting conclusions in the same document. |
| 3 | Pervasive inconsistency; the document cannot be relied on to say one thing. |

### D. Usefulness (0–3) — higher is better

| Score | Criterion |
| --- | --- |
| 0 | Adds nothing a reader could act on. |
| 1 | Restates the figures with little added clarity. |
| 2 | Organises the evidence and surfaces at least one genuine open question. |
| 3 | Clearly separates what is known from what is assumed, and names the specific unresolved questions worth following up. |

A fluent, persuasive narrative that invents specifics must score **worse** than a dull, accurate one. Persuasiveness is not evidence.

## Required procedure

1. Score independently. Do not discuss any document with the other reviewer, or with the run operator, until both of you have submitted all scores.
2. Score in the order the files are listed for you. Do not skip ahead to compare.
3. For every document, record an **unblinding guess**: `independent`, `coordinated`, `baseline`, or `unsure`. Blinding is imperfect — a narrative may reveal its own policy — so these guesses are part of the result, not a failure of it.
4. Add a one-line free-text note for any score of 2 or 3, naming the specific passage. A score without a reason cannot be used.
5. If a document is truncated, empty, or obviously incomplete, mark it `incomplete` and do not score it. Do not infer what it would have said.
6. Do not look up the archive figures to re-derive numbers. Judge internal support and consistency as presented.

## Analysis constraints, fixed in advance

- Report the full score distribution per policy, both reviewers' scores, and inter-reviewer disagreement. Do not report only a mean.
- Report the unblinding-guess accuracy. If reviewers can reliably identify the policy, the comparison is confounded and must be described as such.
- Compare generated reports against the **deterministic baseline brief**, not only against each other.
- No efficacy claim may be made from a single pair, or from a persuasive narrative. The protocol requires at least two eligible pairs per country before any policy comparison is reported.
- Report null and negative results plainly, including the outcome that the coordinated policy is no better, or worse.
- Generated reports stay separate from verified observation claims. A simulation report is never cited as evidence about fire activity.

## Where the files are

`make policy-study` regenerates the review packet. Reviewer-facing files are written to `processed_data/policy_review_private/` (git-ignored, and containing no credentials or provider detail):

| File | Contents |
| --- | --- |
| `<blind_id>.md` | One document to score, filename-anonymised and shuffled |
| `scores.csv` | Pre-seeded with one row per blind ID; reviewers fill the score columns |
| `unblinding_key.json` | Policy and run mapping — **operator only, do not open before scoring** |
| `review_labels.json` | Stable blind-ID mapping across regenerations |

Reviewers should be given only the `<blind_id>.md` files and `scores.csv`.
