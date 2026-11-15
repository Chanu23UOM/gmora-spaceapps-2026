# Sources and attribution

- Raw observations: NASA FIRMS country archives, supplied with this repository. [FIRMS](https://firms.modaps.eosdis.nasa.gov/) and [country archives](https://firms.modaps.eosdis.nasa.gov/country/). The build records hashes and rows of the exact six inputs. Do not infer independent verification of download authenticity from a hash.
- Instrument field interpretation: [NASA VIIRS attributes](https://firms.modaps.eosdis.nasa.gov/content/descriptions/FIRMS_VIIRS_Firehotspots.html). MODIS and VIIRS fields remain distinct quality indicators, not interchangeable probabilities.
- Burned-area limitations: [NASA FIRMS training Q&A, Part 3](https://appliedsciences.nasa.gov/sites/default/files/2025-05/Part%203%20FIRMS%202025%20Q%26A%20Session.docx.pdf).
- Country outlines: Natural Earth, 1:50m admin-0 countries, two features extracted from [natural-earth-vector source](https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_50m_admin_0_countries.geojson). Bundled in `web_app/data/boundaries.geojson`. [Natural Earth public-domain terms](https://www.naturalearthdata.com/about/terms-of-use/). Outlines are for orientation, not jurisdictional decisions.
- Spatial indexing: [H3 indexing API](https://h3geo.org/docs/api/indexing/), Python package h3 4.3.1.
- Temporal evaluation reference: [scikit-learn time-series validation](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html).
- Integrated simulation service: [MiroFish](https://github.com/666ghj/MiroFish), revision recorded in `integrations/mirofish.json`, upstream AGPL-3.0. Isolated backend runtime plus REST adapter; cloud simulations require LLM and Zep credentials. It does not supply numeric fire forecasts. [TimesFM](https://github.com/google-research/timesfm) remains an evaluated, uninstalled candidate.
- Typefaces: DM Sans and Space Grotesk via Google Fonts, with system fallback. Data and interactions work without a font request succeeding. No live map tiles or external JavaScript are required.

AI assistance was used to evaluate architecture, research sources, implement code, write documentation and design the interface. No generated or modified NASA logos or mission insignia are included. Local competition PDFs remain the source for the submission requirements; this prototype is not an official NASA product.
