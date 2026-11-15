# Copy-ready NASA Space Apps submission

## Project name

PyroSync

## Team

Team Gmora

## Challenge

Harmonization of MODIS and VIIRS Hot Spots

https://www.spaceappschallenge.org/2026/challenges/modis-and-viirs-hot-spots/

## High-level summary

PyroSync helps people understand why different satellites can tell different stories about fire activity. Using NASA FIRMS observations from MODIS and VIIRS, we built a working dashboard for Sri Lanka and Argentina that combines an activity calendar, a map, source evidence, and downloadable briefs. A shared counting rule records each active grid cell once per day while preserving the observations behind it. Users can inspect sensor differences and see how results change when a source or analytical choice changes. We also evaluate seven-day forecasts against simple baselines using earlier data for model selection and later years for testing. Historical results are promising in Argentina, while Sri Lanka’s gains remain inconclusive. PyroSync is a research prototype, not a live emergency-warning service. Our goal is to help analysts compare, question, and explain satellite fire records before those records inform decisions.

## Link to Project Demo — use only this one URL

https://github.com/Chanu23UOM/gmora-spaceapps-2026/blob/submission-colombo-2026/submission/colombo-2026/PyroSync_Demo_30s.mp4

This is the 30-second video option with burned-in English subtitles and an adult synthetic narrator. Do not also paste the seven-slide deck into this field. The deck supports the five-minute live pitch.

## Link to Project

https://github.com/Chanu23UOM/gmora-spaceapps-2026

The repository provides runnable source, data definitions, results, and reproduction instructions. A public hosted application is not claimed. Initial local setup requires Python and dependency installation; the core dashboard requires no paid account or API key.

## Project details

### What it does

PyroSync is an instrument-aware fire observation lab. Its working dashboard covers Sri Lanka and Argentina using the 2025 NASA FIRMS archive. Users choose a country and month, read an activity calendar and selected-period brief, inspect mapped observations, compare contributing sources, and export a brief, daily CSV, or GeoJSON.

It addresses the challenge of comparing fire observations from different instruments. Its current contribution is an explicit shared observation unit and traceable evidence, supported by historical sensor-comparison experiments. A validated continuous multi-decade fire record remains a research objective.

### How it works

The Python pipeline validates unchanged source files and preserves file hashes, timestamps, and CSV row references. It separates source types and applies declared confidence rules. At least one qualifying vegetation detection within an H3 resolution-8 cell on one UTC day produces one active cell-day. The combined record takes the union across MODIS Terra/Aqua, VIIRS S-NPP, and VIIRS NOAA-20 streams. Map points group these units into resolution-7 parent cells for display.

This unit is reproducible but is not a distinct-fire census or burned-area estimate. Vegetation burning includes sources of unknown cause; agricultural burning is not automatically labelled wildfire. No detections means no qualifying detections in these inputs, not verified absence of fire.

Source-removal and grid/confidence experiments show how results depend on inputs and analytical choices. Evidence exports retain supported numbers and definitions. The structured verifier rejects unsupported claim names, altered values, and invalid evidence pointers; it does not guarantee arbitrary generated prose is true.

### Research and measured results

We acquired 30 official NASA archive files across three streams, two countries, and 2020–2024, containing 2,966,278 source rows. File hashes are checked; invalid rows are quarantined explicitly. Forecast selection, interval calibration, and outer testing use separate time periods. Each forecast uses only past observations and predicts the next seven days.

For Argentina, the model selected using earlier years reduced mean absolute error versus repeating last week's values by 19.2% on the 2023 outer test and 31.9% on the 2024 outer test. These passed an exploratory research gate, not operational validation. Sri Lanka's historical point improvements remained inconclusive. In the separate original 2025 experiment, both frozen country choices failed promotion. We retain those failures instead of choosing a model after seeing the test results.

Historical sensor mappings are evaluated separately against VIIRS's observed cell union, not against ground truth. Agreement with another instrument does not establish true fire counts or climate trends.

### Benefits and intended users

Fire analysts, researchers, environmental teams, and report writers can investigate why source counts differ and carry evidence into their own workflows. A Sri Lankan analyst can inspect a selected month and explain which instruments contributed to a result. Argentina provides a second landscape and observation context. These are intended use cases, not demonstrated customers or agency partnerships. User time savings and operational benefit have not yet been measured.

### AI communication research

A separate MiroFish lab explores synthetic stakeholder communication using declared roles, observation workloads, and review capacity. It does not create the numerical fire forecasts. The first study completed seven reports but produced zero role-comparable policy pairs, so no communication-policy winner is claimed. Latest upstream code verifies actor identities before simulation; a replacement protocol is frozen but has not been run. Independent domain review remains pending. Generated narratives are kept separate from verified observation facts.

### Next steps

Validate interpretation tasks with analysts using the preregistered usability protocol; acquire authoritative cloud/fire-mask information about observation opportunity; repeat matched communication exercises under the new actor checks and independent review; expand sensor-transition evaluation before claiming an operational harmonized historical record.

### Tools and technology

Python 3.12, NumPy, H3 spatial indexing, a NumPy implementation of ridge autoregression, and Python's local HTTP server support the analysis. The dashboard uses HTML, CSS, JavaScript ES modules, and SVG. MiroFish and Zep support the separate synthetic communication experiment; Gemini on Google Vertex AI provides its language-model service. OpenAI Codex/ChatGPT assisted development, research, documentation, and presentation authoring. Python-pptx, Pillow, LibreOffice, Playwright, and FFmpeg produce the presentation assets. Google Vertex AI Gemini 2.5 Pro TTS with the adult synthetic voice Charon provides the submitted narration.

## Use of SI / AI — tools and disclosure

Select the available form entries corresponding to the tools actually used, and use an Other entry where needed: OpenAI Codex/ChatGPT; Google Gemini / Vertex AI; MiroFish; Zep. Do not claim use of uninstalled forecasting foundation models or an image generator.

AI assistants helped with architecture, source research, code, documentation, interface and submission design. Gemini via Vertex AI powers the synthetic communication experiment and generates the adult synthetic voiceover. MiroFish orchestrates the synthetic actors; Zep supports their context. Measured observation counts and forecast scores come from the reproducible numerical pipeline. AI narrative outputs are not admitted as verified numerical evidence. No NASA logos, flags, mission identifiers, or other NASA branding were generated or modified. Visuals contain the product UI and original abstract shapes. No under-18 names, voices, or likenesses are included.

## NASA data — official resources used

- NASA FIRMS: https://firms.modaps.eosdis.nasa.gov/
- FIRMS country archives: https://firms.modaps.eosdis.nasa.gov/country/
- Official historical yearly file catalog: https://firms.modaps.eosdis.nasa.gov/data/country/yearly_summary_files.txt
- MODIS and VIIRS archive access: https://firms.modaps.eosdis.nasa.gov/download/
- NASA VIIRS attribute definitions: https://firms.modaps.eosdis.nasa.gov/content/descriptions/FIRMS_VIIRS_Firehotspots.html

The actual observations are MODIS Terra/Aqua, S-NPP VIIRS, and NOAA-20 VIIRS country records. Exact source-file manifests and hashes are in the repository. Data courtesy NASA/GSFC ESDIS. This independent project is not endorsed by NASA.

## Space agency partner data and other resources

No additional space-agency partner dataset was used. CONAE is an intended challenge/use-case context, not a data supplier or collaborating customer of this prototype.

- Natural Earth country outlines: https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_50m_admin_0_countries.geojson ; public-domain terms: https://www.naturalearthdata.com/about/terms-of-use/
- H3: https://h3geo.org/docs/
- scikit-learn time-series validation: https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html
- NumPy numerical computing: https://numpy.org/
- MiroFish source and licence: https://github.com/666ghj/MiroFish (pinned revision in `integrations/mirofish.json`; upstream AGPL-3.0)
- Zep: https://www.getzep.com/
- Google Gemini TTS / Vertex synthesis documentation: https://docs.cloud.google.com/text-to-speech/docs/gemini-tts
- OpenAI Codex: https://openai.com/codex/ ; ChatGPT: https://chatgpt.com/
- Interface typefaces: https://fonts.google.com/specimen/DM+Sans and https://fonts.google.com/specimen/Space+Grotesk
- Presentation typeface: https://rsms.me/inter/
- Presentation tooling: https://python-pptx.readthedocs.io/ ; https://python-pillow.github.io/ ; https://www.libreoffice.org/ ; https://playwright.dev/ ; https://ffmpeg.org/
- Complete project source attribution: https://github.com/Chanu23UOM/gmora-spaceapps-2026/blob/main/docs/DATA_SOURCES.md

The user-supplied Components of Project and Colombo Contestant Judging Guide PDFs govern this submission's format. They are not presented as research evidence. No external stock photography, NASA logo art, or generated portraits were used.
