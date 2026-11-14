# 🔥 Team Gmora — Harmonization of MODIS & VIIRS Hot Spots

**NASA Space Apps Challenge 2026 | Sri Lanka (Colombo) — Virtual Track**

Welcome to the official Team **Gmora** repository for the **Harmonization of MODIS and VIIRS Hot Spots** challenge (authored by Marina Companuchi, CONAE — Argentina Space Agency).

---

## 📖 Start Here
👉 Read our complete execution blueprint, scientific methodology, judging strategy, and team task breakdown in:  
**[TEAM_GMORA_MASTER_PLAN.md](./TEAM_GMORA_MASTER_PLAN.md)**

---

## 📂 What Is in This Repository
- `TEAM_GMORA_MASTER_PLAN.md` — Complete step-by-step master plan, 5-stage harmonization pipeline, 7-slide deck outline, 5-minute pitch script, and submission checklist.
- `Components of Project - NASA Space Apps Challenge.pdf` — Official NASA Space Apps 2026 project submission requirements.
- `NASA Space Apps Colombo 2026 Contestant Judging Guide.pdf` — Official Colombo 2026 50-mark rubric & 10 sub-category awards guide.
- `modis/2025/`, `viirs-snpp/2025/`, `viirs-jpss1/2025/` — Anchor country 2025 datasets (`Sri_Lanka` & `Argentina`) + `AttributesReadme.txt`. *(All other 230+ countries from the 3.08 GB global 2025 archive are excluded via `.gitignore` to keep the repo fast and within GitHub limits.)*

---

## 📊 Key Local Data Insights (2025 Baseline)
| Country | MODIS Rows | VIIRS S-NPP Rows | VIIRS NOAA-20 (JPSS-1) Rows | VIIRS:MODIS Ratio |
| :--- | :---: | :---: | :---: | :---: |
| **Sri Lanka** | 684 | 5,519 | 5,451 | **~8.07×** |
| **Argentina** | 48,121 | 170,674 | 170,323 | **~3.55×** |

---

## 📥 Adding Year-by-Year Historical Data (2000–2026)
Download historical country CSVs from [NASA FIRMS Archive Download](https://firms.modaps.eosdis.nasa.gov/download/) or [FIRMS Country Archives](https://firms.modaps.eosdis.nasa.gov/country/) and place them under:
- `modis/<YEAR>/modis_<YEAR>_<Country>.csv` (`2000–2025`)
- `viirs-snpp/<YEAR>/viirs-snpp_<YEAR>_<Country>.csv` (`2012–2025`)
- `viirs-jpss1/<YEAR>/viirs-jpss1_<YEAR>_<Country>.csv` (`2018–2025`)

`.gitignore` is pre-configured so `*_Sri_Lanka.csv` and `*_Argentina.csv` files for any year can be safely committed and shared with teammates, while huge global country files stay local.

---

## 🙏 Data Attribution
Active fire/hotspot data courtesy of **NASA FIRMS** (Fire Information for Resource Management System), operated by NASA/GSFC Earth Science Data and Information System (ESDIS) — `https://firms.modaps.eosdis.nasa.gov/`.
