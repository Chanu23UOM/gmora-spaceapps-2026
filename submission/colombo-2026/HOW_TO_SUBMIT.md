# How to submit PyroSync — Team Gmora

This is the team's submission guide. It follows the two supplied booklets and treats PyroSync fairly as a 48-hour working prototype. The official form has not been submitted automatically.

## 1. Use these files

| Purpose | File | What to do |
| --- | --- | --- |
| All written project fields | [PROJECT_SUBMISSION.md](PROJECT_SUBMISSION.md) | Copy each named section into its matching form field. |
| High-level summary | [SUMMARY.txt](SUMMARY.txt) | Paste all 151 words. Allowed range: 50–200. |
| Submitted demo | [PyroSync_Demo_30s.mp4](PyroSync_Demo_30s.mp4) | Use the single public video URL below. It is exactly 30 seconds, with English subtitles and a synthetic adult Vertex narrator. |
| Live pitch | [PyroSync_Submission_7_Slides.pdf](PyroSync_Submission_7_Slides.pdf) | Present these seven slides, including the title. |
| Editable deck | [PyroSync_Submission_7_Slides.pptx](PyroSync_Submission_7_Slides.pptx) | Use only if you need PowerPoint editing/presentation. |
| Spoken live script | [LIVE_PITCH_5_MIN.md](LIVE_PITCH_5_MIN.md) | Rehearse to five minutes, then allow five minutes for questions. |
| Technical proof / judge questions | [HACKATHON_EVIDENCE.md](HACKATHON_EVIDENCE.md) | Refer to the measured results and limits; do not append it to the seven-slide demo deck. |
| Format and test record | [PACKAGE_VALIDATION.json](PACKAGE_VALIDATION.json) | Supporting evidence; no need to paste JSON into the submission form. |

The older ten-minute deck/video and the five-minute rehearsal video do **not** meet the submitted video's 30-second limit. The longer rehearsal MP4/MP3 stay local under this folder and are for practice only.

## 2. Open your official team project page

1. Sign into the official [NASA Space Apps website](https://www.spaceappschallenge.org/).
2. Open your Team Gmora entry for Colombo 2026 and its project submission/edit form. Use the actual team's existing entry; do not create an extra team or duplicate project.
3. Confirm the selected challenge is **Harmonization of MODIS and VIIRS Hot Spots**.
4. Enter the fields below. The booklets do not provide the team's private editor URL, so this guide does not invent one. Button labels may differ in the live form.

Challenge reference: https://www.spaceappschallenge.org/2026/challenges/modis-and-viirs-hot-spots/

## 3. Fill the project fields

### Project name

```text
PyroSync
```

### Team

```text
Team Gmora
```

### High-level summary

Paste [SUMMARY.txt](SUMMARY.txt), unchanged. It is within the 50–200-word range.

### Link to Project Demo — paste only ONE link

Use this public, narrated, English-subtitled 30-second video:

```text
https://github.com/Chanu23UOM/gmora-spaceapps-2026/blob/submission-colombo-2026/submission/colombo-2026/PyroSync_Demo_30s.mp4
```

Do not paste a folder, two URLs, the five-minute rehearsal, or the older ten-minute video into this field.

If the platform has trouble previewing the video, open/download it from the public link. You may instead choose the seven-slide PDF below, **replacing** the video URL rather than adding a second link:

```text
https://raw.githubusercontent.com/Chanu23UOM/gmora-spaceapps-2026/submission-colombo-2026/submission/colombo-2026/PyroSync_Submission_7_Slides.pdf
```

The supplied rules allow seven slides OR the 30-second subtitled video. The prepared default is the video.

### Link to Project — this is a separate field

Paste the public working website:

```text
https://pyrosync-gmora.vercel.app
```

The site requires no login. Observation views, source evidence, exports, research summaries, and scenario preparation work online. New paid MiroFish simulations run only through the separately configured local backend. The source remains available at https://github.com/Chanu23UOM/gmora-spaceapps-2026/tree/submission-colombo-2026 .

### Project Details

Copy the complete **Project details** section from [PROJECT_SUBMISSION.md](PROJECT_SUBMISSION.md), including the sensor-comparison evidence, benefits, current scope, tools and next steps.

The strongest claims to retain are:

- A working calendar → brief → map → evidence → export journey for Sri Lanka and Argentina.
- NASA MODIS/VIIRS observations remain traceable to original source rows.
- Historical mappings reduce count error against the VIIRS observation reference in the two tested years; the reference is not ground truth.
- The browser audit checks both countries and mobile/keyboard paths reproducibly.
- Forecast and AI results retain their negative outcomes and research status.

Do not turn observation cell-days into “number of fires”, or describe the prototype as a validated emergency-warning system.

### Use of SI / AI

Select the available entries corresponding to tools actually used, and use an Other/free-text field where needed:

- OpenAI Codex / ChatGPT: architecture, coding, research, documentation, interface and submission authoring.
- Google Gemini / Vertex AI: synthetic communication experiment and the adult synthetic narration.
- MiroFish: orchestration of the fictional stakeholder exercise.
- Zep: context service for that exercise; it is infrastructure rather than a speech model.

Paste the full disclosure from [PROJECT_SUBMISSION.md](PROJECT_SUBMISSION.md). The narrator is the Charon preset from Gemini 2.5 Pro TTS on Vertex AI. No NASA logos/flags/mission insignia were generated or altered. There are no under-18 names, human recordings, or likenesses in the prepared demo.

### NASA Data

Copy the official links and descriptions from the **NASA data** section in [PROJECT_SUBMISSION.md](PROJECT_SUBMISSION.md). At minimum retain:

```text
NASA FIRMS: https://firms.modaps.eosdis.nasa.gov/
Country archives: https://firms.modaps.eosdis.nasa.gov/country/
Historical file catalog: https://firms.modaps.eosdis.nasa.gov/data/country/yearly_summary_files.txt
Archive download: https://firms.modaps.eosdis.nasa.gov/download/
```

Name the actual products: MODIS Terra/Aqua, S-NPP VIIRS, NOAA-20 VIIRS. These are core inputs, not decorative references. If the live form requires choosing a resource specifically from the challenge Resources tab, match the FIRMS/MODIS/VIIRS entries there.

### Space Agency Partner Data and Other Resources

Copy the complete bibliography from [PROJECT_SUBMISSION.md](PROJECT_SUBMISSION.md), including code, outlines, fonts and authoring tools. No extra partner dataset was used. Do not list CONAE or Sri Lankan agencies as customers or collaborators.

## 4. Check the public links once before submitting

1. Open a private/incognito browser window without signing into GitHub.
2. Open the exact demo URL pasted into the form. Play/download it, check the voice and visible English captions, and confirm its duration is 30 seconds.
3. Open the project source link. Confirm it does not ask for access approval or a password.
4. If you choose the slide option instead, confirm the PDF opens and contains exactly seven pages, including title and closing.
5. Save/preview the project page. Confirm the summary, single demo link, separate project link, NASA sources, and AI disclosure survived pasting.
6. Use the official form's final submit/publish action when the team is ready. Record the confirmation or public project-page URL. This guide does not claim that action has already happened.

The branch's raw demo, PDF, and project text have already been checked anonymously against the local file hashes. Rechecking the exact pasted link catches accidental copy errors or changes in availability.

## 5. Live presentation

Use the seven-slide deck and [LIVE_PITCH_5_MIN.md](LIVE_PITCH_5_MIN.md). The Colombo guide sets **five minutes presenting + five minutes Q&A**.

Have the local dashboard ready as an optional backup (`make serve`, then `http://127.0.0.1:8765`). A safe demo is Sri Lanka → August 2025 → period brief → Explore map & sensors → source evidence → export. This core path does not require a paid AI call or a cloud simulation to complete on stage.

For the sensor question, say:

> We improve agreement between recorded MODIS and VIIRS counts in the tested years. VIIRS is the reference observation record, not verified ground truth. Full operational historical harmonization is the next research step.

For the user-testing question, say:

> Within the 48 hours, we built and checked the complete workflow, including mobile and keyboard use. We have not run a participant study. We already have a protocol for testing interpretation with users after the hackathon.

For the AI question, say:

> The AI exercise is separate from the observed data and numerical forecasts. The first policy comparison was inconclusive; we preserved that result and now check actor identities before simulation.

## 6. What is ready, and what is later work

**Ready:** working prototype, reproducible input pipeline, source inspection, exports, two-country historical comparisons, exploratory transition diagnostics, deterministic browser checks, 47 automated tests, public demo, summary, deck, citations and disclosure.

**After the event:** real-user sessions, independent domain review, full observation-coverage inputs, real sensor-transition/longer-history validation, and operational benefit measurement. These are useful validation milestones, not fabricated results or extra submission prerequisites in the supplied booklets.
