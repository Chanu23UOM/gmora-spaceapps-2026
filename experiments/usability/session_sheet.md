# Usability session sheet — copy once per participant

Protocol: `usability-ui-v1-2026-11-15` · see [docs/USABILITY_STUDY_PROTOCOL.md](../../docs/USABILITY_STUDY_PROTOCOL.md)

Do not write names, employers, contact details or any other identifying information on this sheet.

## Session metadata

| Field | Value |
| --- | --- |
| Participant code | P__ |
| Condition (A baseline / B simplified) | |
| Date (UTC) | |
| Git commit served | |
| `manifest.json` run_id | |
| Browser and version | |
| Viewport (px) and device | |
| Input method (mouse / keyboard / touch) | |
| Prior familiarity 0–3 (asked before tasks) | |
| Consent obtained (yes/no) | |
| Task order (Latin-square row) | |

## Facilitator script

Read aloud, once, verbatim. Do not define "active cell-day", "raw detection", "cell-day versus fire", or point at any control.

> This is a research prototype that shows where satellites recorded possible fire activity. It is not a warning system. I will ask you to find a few things and explain what you see. There are no wrong answers about you — I am testing the interface, not you. Please think aloud. You can stop at any time, and I am only recording anonymous notes about the tasks. If you get stuck, say so and we will move on.

After each task, ask: *"How confident are you in that answer, from 0 (not at all) to 3 (very)?"* Record the number without comment.

If the participant asks what a term means, respond: *"Whatever you can work out from the screen is the right answer for me."*

## Tasks

Fill the assigned region/period into T1 before the session.

| # | Task prompt (read aloud) | Correct? | Critical error? | Time (s) | Conf 0–3 |
| --- | --- | --- | --- | --- | --- |
| T1 | "Show me the data for **______** in **______**." | | | | |
| T2 | "Which month in this year had the most recorded activity, and what is being counted?" | | | | |
| T3 | "The raw detection number is larger than the active cell-day number. Why?" | | | | |
| T4 | "This day/period shows nothing. What does that tell you about fire there?" | | | | |
| T5 | "Find the forecast (or the MiroFish scenario output). Would you rely on it to send a crew today? Why?" | | | | |
| T6 | "If this number goes up, what exactly has gone up?" | | | | |

Scoring criteria are in the protocol table — apply them as written; do not reinterpret during the session.

Totals: correct **__ / 6** · critical errors **__ / 6** · high-confidence critical errors **__**

## Accessibility and mobile checks

| Check | Pass/Fail | Reproduction note |
| --- | --- | --- |
| Keyboard: view tabs reachable and operable, focus visible | | |
| Keyboard: region/month selects operable | | |
| Keyboard: calendar month + day tiles, arrow-key navigation | | |
| Keyboard: period-brief disclosure opens/closes | | |
| Keyboard: map evidence point selectable, panel updates | | |
| Screen reader: calendar tiles announce period, unit, value | | |
| Screen reader: map points and metric tiles announce unit | | |
| Touch at 390px: complete T1–T3 | | |
| Touch at 390px: no horizontal page scroll; brief and evidence readable without zoom | | |

## Post-session

Usability rating (0–10): **__**

One free-text comment (participant's words, no identifying detail):

> 

Observed difficulties, in the facilitator's words (one line each, note the task):

- 
- 

Negative or unfavourable feedback must be recorded here verbatim, not paraphrased away.

## Filing

- Append one row to `experiments/usability/scores.csv`.
- File each reproducible accessibility or mobile defect as a focused issue, or append it to the issue owning that view, with the reproduction steps and this participant code.
