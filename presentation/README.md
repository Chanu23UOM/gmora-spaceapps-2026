# PyroSync — presenter pitch package

A 10-minute silent presenter video, synchronized script and reproducible browser-capture tools. The recording uses real controls, mouse motion, source inspection, downloads and an existing completed cloud scenario. Separate branded pitch cards introduce the problem and display measured backend results; they are labeled as evidence views rather than additional shipped dashboard screens.

## Present

1. Open [PyroSync_10min_Presenter.mp4](output/PyroSync_10min_Presenter.mp4) full screen.
2. Use [PITCH_SCRIPT.md](PITCH_SCRIPT.md) for your live narration. Start both at 00:00.
3. Speak at approximately 130 words per minute. Pause while the cursor points at a number or source row.
4. Use the embedded video chapters to rehearse individual sections. The master has no narration or audio track.

Editable slides, exported PDFs and speaker guidance are in [deck/](deck/). Use [the full pitch PDF](deck/PyroSync_10_Minute_Pitch.pdf) for the main presentation or [the seven-slide submission PDF](deck/PyroSync_7_Slide_Submission.pdf) for a shorter format.

The script includes stage directions, the audience-facing wording, rehearsal notes and likely judge questions. It distinguishes the 2025 dashboard experiment from the 2023/2024 historical backend evaluation and the synthetic policy study.

## Story arc

| Time | Purpose |
|---|---|
| 00:00–01:25 | Measurement problem and three product commitments |
| 01:25–03:45 | Real country/period controls, calendar and source evidence |
| 03:45–05:40 | Argentina, sensor/grid stress tests and real exports |
| 05:40–07:20 | Baselines, failed 2025 gate and stronger historical evaluation |
| 07:20–08:40 | Completed MiroFish run and validity checks on the actual study |
| 08:40–10:00 | Differentiation, next validation milestones and closing ask |

## Provenance and verification

- Product recording: `http://127.0.0.1:8765` on `feat/kusal-backend-research`, PR head `0e957d9`.
- The published video preserves that recorded interface. PR #10 subsequently reorganized the live dashboard into Overview, Explore, and Research tabs. The underlying evidence and results are the same; the capture tools now reveal the appropriate tab when recording the updated dashboard.
- Evidence cards: live `GET /api/research`, through the local stage server. Public snapshots are retained in `stage/` for inspection.
- No provider keys or service-account files are included in this package.
- The scenario demo opens completed scenario `6a739de93b819d525969`; it does not launch another paid run.
- Real downloaded outputs, still images, capture logs, chapter metadata and video metadata live under generated `output/`.
- The final is edited from genuine Playwright capture segments. No product values or successful simulation results are fabricated.
- This is a research prototype. Gate passage does not establish operational warning accuracy. Persona drift left no valid matched-policy comparison. The script retains those facts.

## Reproduce

Requires the running local product, system Chrome, FFmpeg/FFprobe and Playwright. The application/provider services are separate from the pitch-only server.

```sh
python3 presentation/tools/serve_pitch.py
# In another terminal, after archiving an existing output directory:
node presentation/tools/record_pitch.mjs --main-only
node presentation/tools/record_tail.mjs
python3 presentation/tools/render_pitch.py
```

The two capture commands run for approximately 6:20 and 3:40. Keep the stage server and product running during recording. The capture tools add a visible pointer and click ripple, and call real controls. Install their browser dependency with `npm install --prefix .qa --no-save playwright` if needed. Replaying the completed scenario requires the original ignored local run state; a fresh clone does not include private scenario reports. The recording scripts do not start a paid simulation.

Generated captures, intermediates and downloads under `output/` are ignored. The curated final `PyroSync_10min_Presenter.mp4` is intentionally tracked so the complete presenter package is available from both repositories. Its SHA-256 is `3f1af0ffba31ed931f0d4d0b8ba16929739b4c166073d05b42d5179abff24f52`.

The optional deck builder requires `python-pptx` and Pillow; these are authoring dependencies, separate from the product runtime. The deck validation manifest records 14 rendered pages, checked shape bounds, and no invented survey results.

## Knowledge handoff

[LLM_HANDOFF.md](../LLM_HANDOFF.md) contains the project/conversation knowledge source, architecture, results, local commands, GitHub assignments, PR status and remaining work, with credential values excluded.
