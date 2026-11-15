# 🚀 TEAM GMORA: Master Plan & Step-by-Step Walkthrough Guide
> **Implementation status (2026-11-15):** This is the original aspirational plan. Its multi-decade/global product descriptions, calibration methods and submission language are not measured results. The [architecture review](docs/ARCHITECTURE_REVIEW.md) supersedes scientific and implementation claims here. See [README](README.md) for the working 2025 prototype and [evaluation protocol](docs/EVALUATION_PROTOCOL.md) for measured checks. Do not copy the submission draft as a statement of completed work.
**Event:** NASA Space Apps Challenge 2026 — Sri Lanka (Colombo Virtual Track)  
**Challenge:** Harmonization of MODIS and VIIRS Hot Spots  
**Challenge Author:** Marina Companuchi, CONAE (*Comisión Nacional de Actividades Espaciales* — Argentina Space Agency, Teófilo Tabanera Space Center, Córdoba)  
**Live Virtual Pitching:** November 15, 2026 @ 10:00 AM IST (Alphabetical Order by Team Name — Team **Gmora** is in the **G** slot!)

---

## 📌 Table of Contents
1. [Executive Winning Strategy for Team Gmora](#1-executive-winning-strategy-for-team-gmora)
2. [Deep-Dive Analysis of Our Local 2025 Dataset & The Core Problem](#2-deep-dive-analysis-of-our-local-2025-dataset--the-core-problem)
3. [Year-by-Year Historical Data Guide (2000–2026) & Git Storage Strategy](#3-year-by-year-historical-data-guide-20002026--git-storage-strategy)
4. [The 5-Stage Scientific Harmonization Pipeline (Step-by-Step)](#4-the-5-stage-scientific-harmonization-pipeline-step-by-step)
5. [Web Application & "Burning Activity Calendar" Walkthrough](#5-web-application--burning-activity-calendar-walkthrough)
6. [Repository Structure & Parallel Team Workstreams](#6-repository-structure--parallel-team-workstreams)
7. [Colombo 2026 Judging Rubric Optimization (50 Marks + 10 Sub-Categories)](#7-colombo-2026-judging-rubric-optimization-50-marks--10-sub-categories)
8. [The 7-Slide Deck, 5-Minute Live Pitch Script & Q&A Cheat Sheet](#8-the-7-slide-deck-5-minute-live-pitch-script--qa-cheat-sheet)
9. [Ready-to-Use NASA Project Submission Page Template & Compliance Checklist](#9-ready-to-use-nasa-project-submission-page-template--compliance-checklist)

---

## 1. Executive Winning Strategy for Team Gmora

> **Why Most Teams Lose Marks on This Challenge:**  
> Most teams will simply take the MODIS and VIIRS CSV files, plot raw dots on a map, or average their monthly counts. **That is scientifically invalid** and fails the *Validity* (10 marks) and *Relevance* (10 marks) criteria.

### Our Winning Edge:
1. **Scientifically Grounded 5-Stage Harmonization:** We explicitly solve the 4 physical discrepancies between MODIS and VIIRS:
   - **Pixel Footprint Geometry:** MODIS nadir pixels are $1.0\text{ km} \times 1.0\text{ km}$ ($1.0\text{ km}^2$) vs. VIIRS $375\text{ m} \times 375\text{ m}$ ($0.14\text{ km}^2$) — roughly **7.1 VIIRS pixels per 1 MODIS pixel** at nadir.
   - **Minimum Radiative Sensitivity:** VIIRS detects low-intensity fires ($\text{FRP} \approx 0.5\text{ MW}$) that MODIS completely misses ($\text{FRP threshold} \approx 7\text{–}10\text{ MW}$).
   - **Multi-Satellite Overpass Duplication:** Terra, Aqua, Suomi-NPP, and NOAA-20 (JPSS-1) pass over the same fire multiple times per day.
   - **Non-Wildfire Thermal Anomalies (`type=2`):** Industrial heat sources (like cement kilns and gas flares) appear as persistent false "fires" in VIIRS unless filtered using the `type` column.
2. **Dual-Anchor Case Study (Global Nominee + Sri Lanka Local Impact Award):**
   - **Case Study A — Argentina (CONAE):** Focus on **Chilecito / La Rioja, Córdoba, and the Paraná Delta** (specifically referencing the July wildfire emergency highlighted by challenge author Marina Companuchi from CONAE).
   - **Case Study B — Sri Lanka (Local Impact):** Focus on **Badulla, Nuwara Eliya, Monaragala, Knuckles Range, and Wilpattu**, solving Sri Lanka's acute split between montane forest fires and seasonal agricultural (*Chena*) burning for the **Disaster Management Centre (DMC) of Sri Lanka**.

---

## 2. Deep-Dive Analysis of Our Local 2025 Dataset & The Core Problem

We inspected the exact 2025 CSV files inside `D:\SpaceApps\modis\2025`, `D:\SpaceApps\viirs-snpp\2025`, and `D:\SpaceApps\viirs-jpss1\2025`. Every team member must understand these exact differences:

### 2.1 Column-by-Column Schema Comparison

| Field Purpose | `modis/2025/*.csv` | `viirs-snpp/2025/*.csv` | `viirs-jpss1/2025/*.csv` | Harmonization Action Needed |
| :--- | :--- | :--- | :--- | :--- |
| **Coordinates** | `latitude`, `longitude` | `latitude`, `longitude` | `latitude`, `longitude` | WGS84 projection. Map to standardized grid / Uber H3 hexagons. |
| **Primary Thermal Band** | `brightness` (Band 21/22, ~3.96 µm, K) | `bright_ti4` (Channel I4, 3.74 µm, K) | `bright_ti4` (Channel I4, 3.74 µm, K) | Rename to `temp_mir_k`. Note: VIIRS `bright_ti4` saturates at 367 K during intense fires. |
| **Background Thermal Band** | `bright_t31` (Band 31, ~11.0 µm, K) | `bright_ti5` (Channel I5, 11.45 µm, K) | `bright_ti5` (Channel I5, 11.45 µm, K) | Rename to `temp_tir_k`. Compute $\Delta T = T_{\text{MIR}} - T_{\text{TIR}}$. |
| **Pixel Dimensions** | `scan`, `track` (in km; $\ge 1.0\text{ km}$) | `scan`, `track` (in km; $\approx 0.33\text{–}0.8\text{ km}$) | `scan`, `track` (in km; $\approx 0.33\text{–}0.8\text{ km}$) | Compute true ground footprint area: $A_{\text{pixel}} = \text{scan} \times \text{track}$ ($\text{km}^2$). |
| **Timestamp** | `acq_date` (`YYYY-MM-DD`), `acq_time` (`HHMM` UTC) | `acq_date`, `acq_time` (`HHMM` UTC) | `acq_date`, `acq_time` (`HHMM` UTC) | Combine with `daynight` (`D`/`N`) to group same-day overpasses. |
| **Satellite & Sensor** | `satellite` (`Terra`, `Aqua`), `instrument` (`MODIS`) | `satellite` (`N`), `instrument` (`VIIRS`) | `satellite` (`N20`), `instrument` (`VIIRS`) | Standardize satellite IDs (`TERRA`, `AQUA`, `SNPP`, `NOAA20`). |
| **Confidence** | Numeric `0`–`100` (e.g., `70`, `62`) | Categorical string: `l`, `n`, `h` | Categorical string: `l`, `n`, `h` | Map both to a unified confidence score $w_{\text{conf}} \in [0, 1]$. |
| **Fire Radiative Power** | `frp` (Megawatts, MW) | `frp` (Megawatts, MW) | `frp` (Megawatts, MW) | Normalize by pixel area ($\text{FRP} / (\text{scan} \times \text{track})$) and cross-calibrate. |
| **Thermal Anomaly Type** | `type` (`0`=veg fire, `1`=volcano, `2`=static land, `3`=offshore) | `type` (`0`, `1`, `2`, `3`) | `type` (`0`, `1`, `2`, `3`) | **CRITICAL:** Filter `type == 0` for wildfire calendars; isolate `type == 2` as industrial heat sources! |

### 2.2 Real Statistics from Our 2025 Folder (Use This in Our Pitch!)

Look at the actual row counts in our `D:\SpaceApps` 2025 datasets:
- **Sri Lanka (2025):**
  - `modis_2025_Sri_Lanka.csv`: **684 rows** (Terra + Aqua combined)
  - `viirs-snpp_2025_Sri_Lanka.csv`: **5,519 rows** (**8.07×** MODIS!)
  - `viirs-jpss1_2025_Sri_Lanka.csv`: **5,451 rows** (**7.97×** MODIS!)
  - *Interpretation:* The observation-count ratio alone cannot establish the fraction of distinct fires missed by MODIS or attribute detections to a particular land-use activity. `type=2` static thermal sources should be separated from presumed vegetation detections. Attribution to a specific facility requires independent verification.
- **Argentina (2025):**
  - `modis_2025_Argentina.csv`: **48,121 rows**
  - `viirs-snpp_2025_Argentina.csv`: **170,674 rows** (**3.55×** MODIS)
  - `viirs-jpss1_2025_Argentina.csv`: **170,323 rows** (**3.54×** MODIS)
  - *Why?* Argentina experiences larger savanna, rangeland, and woodland fire fronts that exceed the MODIS detection threshold, resulting in a ~3.5× VIIRS-to-MODIS ratio rather than 8.1×.
- **Key Scientific Conclusion:** A single global constant multiplier (e.g., dividing VIIRS by 4) **does not work**. Harmonization MUST be **spatially, seasonally, and biome-calibrated**!

---

## 3. Year-by-Year Historical Data Guide (2000–2026) & Git Storage Strategy

### 3.1 Sensor Operational Timeline (What Years Exist for Each Sensor?)
When downloading year-by-year data, note the physical launch dates of each satellite:
- **MODIS (`modis`):** **2000 – 2026** (Terra launched late 1999, data starts Nov 2000; Aqua starts July 2002). *26 years of historical heritage.*
- **VIIRS S-NPP (`viirs-snpp`):** **2012 – 2026** (Suomi-NPP launched Oct 2011, active fire data starts Jan 20, 2012). *14+ years of overlap with MODIS.*
- **VIIRS JPSS-1 / NOAA-20 (`viirs-jpss1`):** **2018 – 2026** (Launched Nov 2017, data starts early 2018). *8+ years of overlap.*

### 3.2 Where to Get the Year-by-Year Files
1. **NASA FIRMS Country Yearly Archive (`https://firms.modaps.eosdis.nasa.gov/country/` & `https://firms.modaps.eosdis.nasa.gov/download/`):**
   - Provides annual country CSV files matching your exact folder structure:
     - `modis/<YEAR>/modis_<YEAR>_<Country>.csv` (Years: `2000` to `2025`)
     - `viirs-snpp/<YEAR>/viirs-snpp_<YEAR>_<Country>.csv` (Years: `2012` to `2025`)
     - `viirs-jpss1/<YEAR>/viirs-jpss1_<YEAR>_<Country>.csv` (Years: `2018` to `2025`)
   - **Fastest way to get all years (2000–2026) for Sri Lanka & Argentina in one zip file:**
     - Go to `https://firms.modaps.eosdis.nasa.gov/download/`
     - Log in with a free NASA Earthdata account.
     - Click **Create New Request** $\rightarrow$ Select **Country** (`Sri Lanka` and `Argentina`, plus optional benchmark countries like `Australia`, `Brazil`, `Spain`) $\rightarrow$ Set Date Range `2000-11-01` to `2026-11-14` $\rightarrow$ Select `MODIS`, `VIIRS S-NPP`, and `VIIRS NOAA-20` $\rightarrow$ Output format: **CSV**.
     - You will receive a single clean download per sensor containing the entire 2000–2026 multi-decade time series!
2. **NASA FIRMS Live API (For Near-Real-Time 2026 Data):**
   - Get a free `MAP_KEY` at `https://firms.modaps.eosdis.nasa.gov/api/`
   - URL format: `https://firms.modaps.eosdis.nasa.gov/api/country/csv/{MAP_KEY}/{SOURCE}/{COUNTRY_CODE}/{DAY_RANGE}/{DATE}`

### 3.3 CRITICAL: How to Organize Data in the Repo Without Breaking GitHub
- **DO NOT commit all 235 countries for all 25 years as raw CSVs into Git!**
  - Your `2025` folders alone (`modis/2025`, `viirs-snpp/2025`, `viirs-jpss1/2025`) are **>1.5 GB**. Pushing 25 years of global raw CSVs (~35 GB) will cause GitHub to block your push (100 MB per-file limit, 2 GB repo limit).
- **What to Put in Git vs. Local/Shared Drive:**
  1. **Keep Raw Global Folders Local / in Google Drive:** Add `modis/`, `viirs-snpp/`, and `viirs-jpss1/` to `.gitignore` (or only track `*Sri_Lanka.csv` and `*Argentina.csv` inside them!).
  2. **Track Target Multi-Year Country CSVs in Git:** All 25 years (`2000–2025`) of `Sri_Lanka.csv` across all 3 sensors is **less than 15 MB total**! Every teammate can pull that in 2 seconds.
  3. **Track Pre-Computed Harmonized JSON/Parquet Summaries in Git:** Run a local pre-processing script on the 2025 global folders once to produce a lightweight `global_country_calibration_2025.json` (`< 500 KB`) and `harmonized_calendar_data.json` (`< 10 MB`) that the web app loads directly.

---

## 4. The 5-Stage Scientific Harmonization Pipeline (Step-by-Step)

This is the core intellectual property of Team Gmora. Document these 5 stages clearly in your UI and presentation:

### Stage 1: Schema Unification, Source Classification & Confidence Weighting
1. **Unify Columns:** Standardize `brightness`/`bright_ti4` $\rightarrow$ `t_mir` and `bright_t31`/`bright_ti5` $\rightarrow$ `t_tir`.
2. **Separate Vegetation Fires from Static Industrial Sources:**
   - Filter `type == 0` (Presumed Vegetation Fire) as the default for the **Wildfire & Agricultural Burning Activity Calendar**.
   - Provide a toggle in the UI to inspect `type == 2` (Static Industrial/Urban Thermal Anomalies) so managers aren't fooled by factories or oil refineries.
3. **Harmonize Detection Confidence ($w_{\text{conf}}$):**
   - MODIS numeric confidence (`0–100`) and VIIRS categorical confidence (`l`, `n`, `h`) are mapped to a continuous reliability weight:
     - Standard filter removes low-confidence solar glint/noise (`MODIS confidence < 30` and `VIIRS confidence == 'l'` during daytime if isolated).
     - Weight mapping:
       $$w_{\text{conf}} = \begin{cases} \text{confidence} / 100.0 & \text{for MODIS} \\ 0.30 \text{ (low)}, \; 0.70 \text{ (nominal)}, \; 0.95 \text{ (high)} & \text{for VIIRS} \end{cases}$$

### Stage 2: Scan-Angle & Pixel Footprint Geometry Normalization
1. **True Ground Pixel Area ($A_{\text{pixel}}$):**
   - Neither MODIS nor VIIRS pixels are points, and pixels stretch significantly toward the edge of the satellite swath (high View Zenith Angle).
   - Calculate the actual ground footprint of every detection using the `scan` and `track` columns:
     $$A_{\text{pixel}} = \text{scan} \times \text{track} \quad (\text{km}^2)$$
   - At nadir, $A_{\text{MODIS}} \approx 1.0\text{ km}^2$ and $A_{\text{VIIRS}} \approx 0.14\text{ km}^2$ (ratio $\approx 7.14 : 1$).
2. **Area-Normalized Fire Radiative Power Density ($\text{FRPD}$):**
   $$\text{FRPD} = \frac{\text{FRP}}{A_{\text{pixel}}} \quad \left(\text{MW/km}^2\right)$$

### Stage 3: Spatio-Temporal Co-Location & Cluster Deduplication
To ensure *"it doesn't matter if one hotspot came from one sensor or the other"* (as Marina Companuchi stated in the video):
1. **Spatial Indexing onto a Unified Grid (Uber H3 Hexagons or $1\text{ km}^2$ Grid):**
   - Assign every `(latitude, longitude)` point to an **H3 Hexagonal Cell** (Resolution 7 $\approx 5.16\text{ km}^2$ for regional aggregation; Resolution 8 $\approx 0.74\text{ km}^2$ for MODIS-equivalent $1\text{ km}^2$ footprint matching).
2. **Intra-Day & Multi-Sensor Overpass Deduplication:**
   - Within each `(H3_cell, acq_date, daynight)` bin:
     - **Spatial Cluster Merging:** If 6 adjacent 375m VIIRS pixels light up inside the same $1\text{ km}^2$-equivalent cell during a single overpass, merge them into **1 Unified Fire Cluster (UFC)** rather than counting 6 separate fires!
     - **Cross-Satellite Overpass Merging:** If Terra, Aqua, S-NPP, and NOAA-20 all detect the same active fire cell on the same day, merge them into a single **Daily Active Fire Cell-Day**, recording:
       - `cluster_count = 1` (preventing quad-counting across 4 satellites!)
       - `harmonized_frp = max(cluster_frp_per_overpass)` (or confidence-weighted mean cluster FRP)
       - `sensors_detected = ["MODIS_TERRA", "VIIRS_SNPP", "VIIRS_NOAA20"]`

### Stage 4: Overlap-Era Statistical Inter-Calibration (2012–2025 Bridge)
Even after spatial clustering (Stage 3), VIIRS still detects small sub-canopy or smallholder fires ($\text{FRP} < 5\text{ MW}$) that never trigger a MODIS pixel.
1. **Use the 2012–2025 Overlap Period (14 Years of Dual Operation):**
   - For any selected region $R$ and calendar month $m \in \{1..12\}$, we have simultaneous daily/monthly series from MODIS ($M_{t}$) and spatially-clustered VIIRS ($V_{t}$) during 2012–2025.
2. **Cross-Sensor Transfer Function (Empirical Quantile Mapping / Seasonal Scaling):**
   - Compute the seasonal biome scaling factor $\gamma_{R, m}$ and quantile distribution mapping during the overlap period:
     $$\hat{H}_{t} = \begin{cases} F_{\text{Harmonized}}^{-1}\left(F_{\text{MODIS}, m}(M_t)\right) & \text{if } t < 2012 \text{ (MODIS-only era)} \\ w_M \cdot \tilde{M}_t + w_V \cdot \tilde{V}_t & \text{if } 2012 \le t \le \text{MODIS retirement (Overlap era)} \\ \tilde{V}_t & \text{if post-MODIS retirement (VIIRS continuity era)} \end{cases}$$
   - **Research objective, not an achieved result:** A comparable historical activity index. Any reduction in sensor-transition artifacts must be measured on withheld periods without suppressing genuine changes. Only 2025 data is present; no historical transfer function is currently fitted.

### Stage 5: Climatological Baseline, Trends & Anomaly Detection
For the **Burning Activity Calendar**, compute for every cell `(Year y, Month/Week m)`:
1. **Harmonized Fire Activity ($H_{y, m}$):** Standardized active fire cluster-days and cumulative radiative energy (MWh / TJ).
2. **25-Year Historical Climatology ($\mu_m, \sigma_m$):** Mean and standard deviation for month/week $m$ across all historical years.
3. **Standardized Burning Anomaly ($Z$-Score):**
   $$Z_{y, m} = \frac{H_{y, m} - \mu_m}{\sigma_m}$$
   - **Normal Seasonal Activity:** $-1.0 \le Z_{y, m} \le +1.0$
   - **Moderate Positive Anomaly (Watch):** $+1.0 < Z_{y, m} \le +2.0$
   - **Extreme Fire Emergency (Red Alert):** $Z_{y, m} > +2.0$

---

## 5. Web Application & "Burning Activity Calendar" Walkthrough

Build the web application around **4 core interactive modules** that directly fulfill every requirement in the challenge video:

### Module 1: The Harmonized Burning Activity Calendar (Hero View)
- **Visual Design:** A rich interactive **Year (2000–2026) $\times$ Month / Week / Day Matrix Heatmap**.
- **Interactive Controls:**
  - **Region Selector:** Global Country Dropdown + Sub-national Province/District selector (e.g., *La Rioja / Córdoba* in Argentina; *Badulla / Nuwara Eliya / Monaragala / Puttalam* in Sri Lanka) or Custom Bounding Box tool.
  - **Metric Selector:**
    1. *Harmonized Fire Cluster Count* (Sensor-unified fire events)
    2. *Harmonized Fire Radiative Power (FRP Density)* (Fire intensity)
    3. *Climatological Anomaly ($Z$-Score)* (Red/Blue diverging palette showing abnormal burning months)
  - **The "Before vs. After Harmonization" Live Toggle (Judge Favourite!):**
    - Allows the judge to flip between **Raw Unharmonized Data** (visibly broken by the 2012/2018 sensor transitions) and **Gmora Harmonized Data** (smooth, scientifically calibrated 26-year record).

### Module 2: Geospatial Hotspot & Pixel Footprint Explorer
- **Interactive Map:** Displays hotspots and H3 hexagonal fire clusters for the selected date/month/year on the calendar.
- **Sensor Footprint Visualizer:** When zooming into a fire event, render the actual `scan × track` rectangle of MODIS ($1\text{ km}^2+$) alongside the `scan × track` rectangles of VIIRS ($0.14\text{ km}^2$) so users can visually see how 1 MODIS hotspot corresponds to a cluster of VIIRS hotspots.
- **Source Type Filter:** Checkboxes to toggle `Type 0 (Vegetation/Wildfire)` vs. `Type 2 (Industrial/Static Source)`.

### Module 3: Multi-Decade Trend & Seasonality Analytics Panel
- **Seasonal Fire Regime Curve:** Plots the 12-month climatological average curve (with 10th–90th percentile shaded bands) overlaid with the user's selected year (e.g., showing how July 2026 in Chilecito, Argentina or August 2025 in Badulla, Sri Lanka spiked above the historical 90th percentile).
- **Sensor Inter-Calibration Diagnostic Card:** Displays the overlap-period correlation ($R^2$), local VIIRS:MODIS sensitivity ratio (e.g., `8.07x` for Sri Lanka, `3.55x` for Argentina), and Mann-Kendall long-term trend slope.

### Module 4: Analytics & Emergency Brief Exporter
- **Download Buttons:**
  1. **Download Harmonized Time-Series (`.csv` / `.json`)** for the selected region and years.
  2. **Download Spatial Clusters (`.geojson`)** for GIS integration (QGIS / ArcGIS).
  3. **Generate 1-Page Fire Manager Situation Brief (`.pdf` / Printable Report)** summarizing peak fire months, current anomaly status ($Z$-score), and historical recurrence interval.

---

## 6. Repository Structure & Parallel Team Workstreams

### 6.1 Recommended Directory Structure for `D:\SpaceApps`
```text
D:\SpaceApps\
├── .gitignore                        # Ignores raw multi-GB folders so Git stays fast!
├── README.md                         # Overview, architecture, and setup instructions
├── TEAM_GMORA_MASTER_PLAN.md         # This complete team guide
├── data_pipeline/                    # Data Engineering & Harmonization Scripts
│   ├── extract_target_countries.py
│   ├── harmonize_modis_viirs.py
│   └── generate_web_payloads.py
├── processed_data/                   # Committed to Git (< 20 MB total)
│   ├── sri_lanka_2000_2026_harmonized.json
│   ├── argentina_2000_2026_harmonized.json
│   ├── global_2025_sensor_ratios.json
│   └── sample_footprints_cluster.geojson
├── web_app/                          # Interactive Burning Activity Calendar Web App
│   ├── public/
│   ├── src/
│   └── package.json
└── submission_assets/                # Pitch Deck (Max 7 Slides) & Submission Text
    ├── Team_Gmora_7_Slides.pdf
    └── NASA_Submission_Form_Text.md
```

### 6.2 Recommended `.gitignore` Contents
Before initializing or pushing to GitHub, create a `.gitignore` file with:
```gitignore
# Ignore massive raw global CSV folders (>1.5 GB)
modis/
viirs-snpp/
viirs-jpss1/

# Exception: Allow tracking Sri Lanka and Argentina raw CSVs if desired
!modis/**/modis_*_Sri_Lanka.csv
!modis/**/modis_*_Argentina.csv
!viirs-snpp/**/viirs-snpp_*_Sri_Lanka.csv
!viirs-snpp/**/viirs-snpp_*_Argentina.csv
!viirs-jpss1/**/viirs-jpss1_*_Sri_Lanka.csv
!viirs-jpss1/**/viirs-jpss1_*_Argentina.csv

# Standard Python / Node ignores
node_modules/
__pycache__/
.venv/
venv/
.env
*.zip
```

### 6.3 Step-by-Step Team Task Breakdown
1. **Member 1 (Data Pipeline & Multi-Year Acquisition):**
   - Set up `.gitignore` and Git repo.
   - Fetch the 2000–2024 historical CSVs for **Sri Lanka** and **Argentina** from NASA FIRMS Archive (`https://firms.modaps.eosdis.nasa.gov/download/`).
   - Compute the 2025 global country ratio table across all 235 countries from your local `2025` folders.
2. **Member 2 (Harmonization Algorithm & Scientific Validation):**
   - Implement the 5-stage pipeline (Schema unification $\rightarrow$ `type=0` filtering $\rightarrow$ `scan*track` footprint math $\rightarrow$ H3/grid spatial-temporal clustering $\rightarrow$ 2012–2025 overlap quantile calibration).
   - Export the clean JSON files for the web app and generate the validation statistics ($R^2$, RMSE, before/after step-change removal).
3. **Member 3 (Frontend UI — Burning Activity Calendar & Charts):**
   - Build the interactive Year $\times$ Month/Week **Burning Activity Calendar Matrix**, the **Raw vs. Harmonized Toggle**, the **Seasonality Clock/Envelope Chart**, and the **CSV/Report Exporter**.
4. **Member 4 (Geospatial Map & Footprint Visualizer):**
   - Build the interactive map showing H3 fire clusters and the zoom-in **1km MODIS vs. 375m VIIRS pixel footprint overlay** for Argentina (La Rioja/Córdoba) and Sri Lanka (Badulla/Ella/Puttalam).
   - Deploy the web app to a public URL (Vercel / Netlify / GitHub Pages / Streamlit Cloud).
5. **Member 5 (Storytelling, 7-Slide Deck, Submission Page & Live Pitch Prep):**
   - Finalize the NASA Space Apps Project Submission Page text, verify all public links in an Incognito window, create the 7-Slide Presentation Deck (or 30s subtitled video), and lead rehearsal for the 5-minute live virtual pitch.

---

## 7. Colombo 2026 Judging Rubric Optimization (50 Marks + 10 Sub-Categories)

From `NASA Space Apps Colombo 2026 Contestant Judging Guide.pdf`:
- **How Scoring Works:** You will pitch live for **5 minutes + 5 minutes Q&A** in the Virtual Track on **Nov 15 starting at 10:00 AM**. Your session is recorded and scored by **all 6 judges** (3 Virtual + 3 Physical).
- **Global Nominees:** Determined by the highest average score out of **50 Marks** across the 5 Core Criteria.
- **Sub-Category Winners:** Every judge also scores your team from **0 to 10** across **all 10 Sub-Categories**. **A single team can win multiple sub-category awards!**

### 7.1 Checklist to Score 10/10 on Each Core Criterion (50 Marks)
1. **Impact (10/10):** Quantify both global reach (calibrating 235 countries across 26 years of NASA Earth Observation) and tangible local utility (helping CONAE in Argentina and the Disaster Management Centre & Forest Department in Sri Lanka anticipate wildfire peaks and manage agricultural burning).
2. **Creativity (10/10):** Highlight 3 novel innovations:
   - The **Live Raw-vs-Harmonized Calendar Toggle** that visually exposes sensor bias.
   - **Physical Swath Footprint Geometry (`scan × track`) + H3 Hexagonal Co-Location**.
   - **Automated `type=2` Static Industrial Heat Source Separation** (catching false wildfire positives like cement kilns).
3. **Validity (10/10):** Show the mathematical rigor of your 5-stage calibration and prove it with before/after correlation metrics ($R^2$ improvement during the 2012–2025 overlap period) and real historical drought-fire validation.
4. **Relevance (10/10):** Directly fulfill every prompt from Marina Companuchi's challenge briefing: sensor-independent hotspot harmonization + interactive web-based Burning Activity Calendar + regional/temporal selection + downloadable analytics + deep integration of NASA FIRMS MODIS & VIIRS datasets.
5. **Presentation (10/10):** Deliver a structured, high-energy 5-minute live demo + a crystal-clear Project Submission Page and 7-slide deck.

### 7.2 How Our Plan Captures Multiple Sub-Category Awards
- 🏆 **10. Local Impact Award:** Dedicated **Sri Lanka Wildfire & Chena Early Warning Calendar** (with district-level analytics for Badulla, Nuwara Eliya, Monaragala, Knuckles, and Puttalam industrial anomaly filtering).
- 🏆 **01. Best Use of Science:** Grounded in orbital radiative transfer physics (`bright_ti4` vs Band 21, nadir-to-edge scan geometry, FRP density conservation, and empirical quantile mapping).
- 🏆 **02. Best Use of Data:** Seamless fusion of multi-decade archival CSVs across **3 NASA/NOAA satellite platforms** (`Terra/Aqua MODIS`, `Suomi-NPP VIIRS`, `NOAA-20 VIIRS`).
- 🏆 **08. Global Connection:** Bridges **CONAE (Argentina)** and **Sri Lanka** in a unified Southern Hemisphere & Tropical fire intelligence platform.
- 🏆 **07. Best Storytelling & 09. Art & Technology:** Visual storytelling through the interactive climate-stripes Burning Activity Calendar and real-time pixel footprint overlays.

---

## 8. The 7-Slide Deck, 5-Minute Live Pitch Script & Q&A Cheat Sheet

### 8.1 Exact 7-Slide Structure (Strict 7-Slide Limit Including Title Slide!)
1. **Slide 1 — Title Slide:** *Project Name* by Team Gmora | Harmonizing 26 Years of NASA MODIS & VIIRS Hotspots into a Unified Global & Sri Lankan Burning Activity Calendar.
2. **Slide 2 — The Problem (Backed by Our 2025 Data):** Why raw MODIS and VIIRS cannot be compared. Show the real numbers from our dataset: *Sri Lanka 2025 has 684 MODIS hotspots vs. 10,970 VIIRS hotspots (S-NPP + NOAA-20) — a 16× raw count explosion! With MODIS retiring, 25 years of baseline history is at risk.*
3. **Slide 3 — Our 5-Stage Harmonization Architecture:** Clean visual diagram of: (1) Schema & `type=0` Vegetation Filtering $\rightarrow$ (2) `scan × track` Footprint Area Normalization $\rightarrow$ (3) H3 Hexagonal Spatio-Temporal Clustering $\rightarrow$ (4) 2012–2025 Overlap Quantile Calibration $\rightarrow$ (5) $Z$-Score Anomaly Indexing.
4. **Slide 4 — Measured Evaluation:** Present actual 2025 grid/confidence sensitivity, source-dropout diagnostics and forward forecast errors. Do not claim a validated 2000–2025 record or an overlap R²: neither has been computed. Both current forecast candidates fail the promotion gate.
5. **Slide 5 — The Interactive Web App & Burning Activity Calendar:** Annotated UI showcase highlighting the Year $\times$ Month Calendar Matrix, Raw-vs-Harmonized Toggle, H3 Footprint Map, Seasonality Clock, and One-Click Analytics Export.
6. **Slide 6 — Dual Real-World Case Studies (Argentina CONAE & Sri Lanka DMC):**
   - *Argentina:* Tracking the July winter fire anomaly in Chilecito / La Rioja & Córdoba (CONAE use case).
   - *Sri Lanka:* Separating dry-season montane wildfires in Badulla/Ella and *Chena* burns from Puttalam's `type=2` industrial cement kiln thermal anomalies.
7. **Slide 7 — Impact, Tech Stack & Mandatory NASA/AI Citations:** Summary of open-source deployment, NASA FIRMS & CONAE resources used, and AI transparency disclosure.

### 8.2 Minute-by-Minute Script for the 5-Minute Virtual Pitch
- **Minute 0:00 – 0:45 | The Hook:** Introduce Team Gmora and show the shocking 2025 Sri Lanka & Argentina sensor discrepancy (`684` MODIS vs `5,519` VIIRS S-NPP in Sri Lanka). Explain that as MODIS retires, fire managers lose their historical yardstick unless we harmonize the sensors.
- **Minute 0:45 – 1:45 | The Science:** Briefly show Slide 3 & 4. Explain how we use `scan × track` pixel area, filter out `type=2` industrial false positives, cluster adjacent 375m VIIRS pixels into H3 cells so one fire isn't counted 10 times, and calibrate across the 2012–2025 overlap window.
- **Minute 1:45 – 3:45 | Live Interactive Web App Demo (2 Full Minutes):**
  - Share the live web app screen.
  - **Step 1:** Load **Argentina** $\rightarrow$ Show the **Burning Activity Calendar** in *Raw Mode* (point out the broken 2012 jump) $\rightarrow$ Flip the switch to **Harmonized Mode** $\rightarrow$ Click on **July** to inspect the winter fire anomaly highlighted by CONAE.
  - **Step 2:** Switch to **Sri Lanka** $\rightarrow$ Zoom into a fire cluster to show the **1km MODIS box overlapping multiple 375m VIIRS pixels** $\rightarrow$ Toggle the `type=2` filter to show how we catch false industrial alarms in Puttalam $\rightarrow$ Click **Export Analytics Report**.
- **Minute 3:45 – 4:45 | Global & Sri Lankan Impact:** Explain how this empowers both CONAE emergency responders and Sri Lanka's Disaster Management Centre & Forest Department.
- **Minute 4:45 – 5:00 | Wrap-Up:** Thank the judges and open the floor for the 5-minute Q&A.

---

## 9. Ready-to-Use NASA Project Submission Page Template & Compliance Checklist

Copy and adapt these exact sections when filling out your official project page on `spaceappschallenge.org` (per `Components of Project - NASA Space Apps Challenge.pdf`):

### 9.1 High-Level Summary (Strictly 50–200 Words — Below Draft is 148 Words)
> For over two decades, NASA’s MODIS and VIIRS satellite instruments have tracked global active fires, but differences in spatial resolution (1 km vs. 375 m), radiative sensitivity, and orbital overpass schedules make their raw records impossible to compare directly. In 2025 alone, VIIRS recorded 8.1 times more hotspots in Sri Lanka and 3.5 times more in Argentina than MODIS—creating artificial statistical jumps that obscure true climate-driven fire trends just as MODIS nears retirement.  
> Team Gmora developed **PyroSync**, a scientifically grounded spatio-temporal harmonization engine and interactive **Burning Activity Calendar** web application. Using a 5-stage pipeline—filtering non-vegetation industrial anomalies (`type=2`), normalizing `scan × track` pixel footprint areas, deduplicating multi-satellite overpasses via Uber H3 hexagonal clustering, and applying Empirical Quantile Mapping across the 2012–2025 overlap era—PyroSync delivers a seamless 26-year fire intelligence record for emergency responders at CONAE, Sri Lanka’s DMC, and worldwide.

### 9.2 Project Details (Structured Answers for Judges)
- **What exactly does it do?** Ingests multi-decade NASA FIRMS active fire archives from MODIS (Terra/Aqua) and VIIRS (Suomi-NPP and NOAA-20/JPSS-1), removes sensor-induced resolution and sensitivity biases, and visualizes a continuous 2000–2026+ Burning Activity Calendar with anomaly detection ($Z$-scores), interactive footprint mapping, and downloadable analytics.
- **How does it work?** Implements a 5-Stage Harmonization Pipeline: (1) Schema & Confidence Unification + `type=0` wildfire isolation, (2) Effective Pixel Area ($A = \text{scan} \times \text{track}$) & FRP Density normalization, (3) Spatio-Temporal H3 Hexagonal Clustering to eliminate fragmentation and multi-overpass double-counting, (4) 2012–2025 Overlap Inter-Calibration via biome-aware seasonal scaling and quantile mapping, and (5) Climatological $Z$-score anomaly computation.
- **What benefits does it have?** Preserves 25+ years of MODIS historical baseline after Terra/Aqua retirement; eliminates false wildfire alarms from static industrial sources; provides instant seasonal anomaly alerts for both global agencies (CONAE Argentina) and local authorities (Sri Lanka Disaster Management Centre & Department of Forest Conservation).
- **What tools, coding languages, hardware, or software did you use?** Python (Pandas, NumPy, GeoPandas, H3, SciPy/Scikit-learn) for the scientific harmonization pipeline; React / Next.js / Tailwind CSS / MapLibre / Deck.gl / Plotly for the interactive Burning Activity Calendar web application; Git & GitHub for version control.

### 9.3 Mandatory NASA Data & Partner Citations (Copy-Paste to Resources Section)
- **NASA FIRMS (Fire Information for Resource Management System) — Country Archive & API:** `https://firms.modaps.eosdis.nasa.gov/` & `https://firms.modaps.eosdis.nasa.gov/country/`
- **NASA MODIS Collection 6.1 Active Fire Product (MCD14DL / MCD14ML):** `https://www.earthdata.nasa.gov/learn/find-data/near-real-time/firms/mcd14dl-nrt`
- **NASA/NOAA VIIRS S-NPP 375m Active Fire Product (VNP14IMGTDL):** `https://www.earthdata.nasa.gov/learn/find-data/near-real-time/firms/v1-vnp14imgt`
- **NASA/NOAA VIIRS NOAA-20 (JPSS-1) 375m Active Fire Product (VJ114IMGTDL):** `https://firms.modaps.eosdis.nasa.gov/download/`
- **Space Agency Partner Reference:** **CONAE (*Comisión Nacional de Actividades Espaciales* — Argentina Space Agency)** Burning Activity Calendar methodology and emergency response framework.

### 9.4 Mandatory Use of AI / SI Disclosure Statement
> **Use of Artificial Intelligence (AI / SI) Disclosure:**  
> Team Gmora utilized AI coding and research assistants (LLMs) to accelerate scientific literature synthesis, harmonization pipeline architecture planning, documentation structuring, and frontend UI component scaffolding. No NASA logos, flags, or mission insignias were generated, altered, or modified using AI tools.

### 9.5 Final Pre-Submission Verification Checklist
- [ ] High-Level Summary is strictly between **50 and 200 words**.
- [ ] **Project Demo Link** contains **ONLY ONE LINK** (either a **maximum 7-slide presentation** where the title slide counts as Slide 1, OR a **30-second video with English subtitles**).
- [ ] Demo link and GitHub/Web App link have been tested in an **Incognito browser window** to guarantee **Public Access** with zero login/password prompts.
- [ ] Confirmed **no names, voices, or images of anyone under age 18** are included.
- [ ] Confirmed **no NASA logos or branding** were generated or altered by AI.
