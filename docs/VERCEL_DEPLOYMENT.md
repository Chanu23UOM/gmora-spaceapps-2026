# PyroSync on Vercel

Public production URL: https://pyrosync-gmora.vercel.app

The static dashboard and its generated 2025 data are deployed alongside `api/index.py`. Python 3.12 is pinned. The adapter reuses the existing evidence-checked scenario preparation and exposes the saved research summaries. Temporary server preparation uses `/tmp`; prepared states are also retained in the user's browser for reload and export.

Available online: both countries, month/metric selection, calendar/day interactions, map/source inspection, static-source toggle, period brief, CSV/GeoJSON/evidence/forecast exports, research summaries, scenario preparation, state download, and recovery of the prepared state after reload.

New paid MiroFish simulations remain a separately configured local-backend feature. The public capability endpoint states this clearly and the start button stays disabled. No Vertex, Zep, relay or other provider credentials are deployed. The public app does not claim cloud execution or persistent cross-device scenario storage.

## Deploy again

```sh
vercel deploy --yes --prod
```

The Vercel CLI must be signed into the project owner's account. `.vercel/` contains local project linkage and stays ignored. `.vercelignore` excludes local credentials, environments, raw observations, private simulation records, and authoring media; the generated `web_app/data` files and downloadable briefs are explicitly included.

## Before/after verification

Run the Vercel-compatible preview:

```sh
PYTHONPATH=. .venv/bin/python tools/preview_vercel.py
```

Against that preview and again against production:

```sh
PYROSYNC_AUDIT_URL=http://127.0.0.1:8767 node submission/colombo-2026/tools/audit_demo.mjs
PYROSYNC_AUDIT_URL=http://127.0.0.1:8767 node tools/check_hosted.mjs
PYROSYNC_AUDIT_URL=https://pyrosync-gmora.vercel.app node submission/colombo-2026/tools/audit_demo.mjs
PYROSYNC_AUDIT_URL=https://pyrosync-gmora.vercel.app node tools/check_hosted.mjs
```

Set `PYROSYNC_AUDIT_OUTPUT` to retain separate JSON results. The 14 observation checks and 16 deployment/export checks passed on both the local adapter and the public production site without credentials. The full Python suite passed 47 tests. Results are under `submission/colombo-2026/evidence/vercel_*.json`.

The first production check caught excluded Markdown evidence briefs; `.vercelignore` was corrected, redeployed, and all evidence downloads passed. The browser audit waits for country loading to finish before clicking downloads, reflecting the app's loading state.
