# PyroSync — NASA Space Apps Colombo 2026 submission

Prepared from upstream `4b39801` against the two user-supplied submission booklets. This package replaces the older ten-minute material for competition purposes.

## Paste into the official form

Copy [PROJECT_SUBMISSION.md](PROJECT_SUBMISSION.md). It contains the 138-word summary, project details, actual NASA/other sources, AI disclosure, and the separate project-source link. Paste only the single designated demo URL into the Project Demo field:

https://github.com/Chanu23UOM/gmora-spaceapps-2026/blob/submission-colombo-2026/submission/colombo-2026/PyroSync_Demo_30s.mp4

The demo is 30 seconds with burned-in English subtitles. Its narrator is the adult synthetic Charon preset generated using the supplied Google Vertex AI configuration. It contains no human portraits or recorded human voices. [English captions](PyroSync_Demo_30s.en.srt) are also provided separately.

## Present live

Use [the seven-slide PDF](PyroSync_Submission_7_Slides.pdf) or [editable PowerPoint](PyroSync_Submission_7_Slides.pptx), with [the five-minute script](LIVE_PITCH_5_MIN.md). The seven slides include the title and closing slide; no appendix is attached. The booklets allow five minutes of presentation followed by five minutes of Q&A.

The local narrated five-minute rehearsal video (`PyroSync_Live_Pitch_5min.mp4`) is for practice; do not put it in the submission's 30-second demo field. The local audio-only rehearsal (`PyroSync_Live_Pitch_5min.mp3`) includes pauses for pointing and transitions. These two larger practice files are kept locally, outside the published Git package. [The short-demo voice track](PyroSync_Demo_Voice.mp3) is available for editing. [Deck overview](DECK_PREVIEW.png).

## Assessment

[GUIDELINE_REVIEW.md](GUIDELINE_REVIEW.md) maps the booklet requirements to the deliverables and gives a provisional internal assessment of 36/50. This is not an official score or prediction. The main limitations are unmeasured user benefit, unknown observation opportunity, and unvalidated full historical harmonization/operational warning skill. New AI role checks and the frozen v2 study are implementation progress; the v2 study and user trials have not run.

[PACKAGE_VALIDATION.json](PACKAGE_VALIDATION.json) records tests, artifact checks and anonymous access. [VOICE_PROVENANCE.json](VOICE_PROVENANCE.json) records the model, preset and timing adjustments. No key, bearer token, service-account JSON or private simulation report is distributed.

## Authoring and verification

- `python3 tools/build_submission.py` reuses the existing project's deck primitives, refreshes the seven-slide PPTX, speaker notes and copy-ready summary.
- Refresh `render/calendar.png` and `render/map.png` from the running app with Playwright before rebuilding. These files are ignored and must be recreated in a clean clone. The curated deck embeds them.
- Export the PPTX to PDF with LibreOffice, then render pages with `pdftoppm -scale-to 1920 -png PyroSync_Submission_7_Slides.pdf render/slide`.
- `python3 tools/voiceover.py` explicitly invokes paid Vertex speech generation using the pre-existing ignored local credential configuration; completed WAV files are reused. It does not modify provider credentials.
- `python3 tools/check_audio.py demo_30s` optionally invokes a separate Vertex audio transcription check to obtain captions. Review timestamps before export.
- `python3 tools/render_media.py` composes the 30-second captioned demo and the five-minute narrated rehearsal. `--demo-only` skips the latter. FFmpeg normalizes loudness; original WAV takes and provider response metadata remain ignored.

The official NASA submission form has not been posted or finalized by this task. The package provides the public materials and copy-ready fields for the team to enter.
