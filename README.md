<<<<<<< HEAD

# Final Project — Anime Popularity & Rating Analysis

## Overview
This repository contains a full end-to-end data project that studies anime popularity, rating behavior, and production capacity evolution between 2016–2025, and produces a candidate prediction list for Winter 2026. The work covers:

- Data collection from the AniList GraphQL API
- Robust data cleaning and feature engineering
- Exploratory analysis and visualization (static + interactive)
- A Streamlit dashboard demo for interactive exploration (`src/app.py`)
- A prediction pipeline to score Winter 2026 candidates using historical features

## Motivation
The motivation for this research stems from the research team's long-term focus on and in-depth exploration of animation culture and the industrial forms behind it. As a cultural and creative industry integrating artistic expression and industrial production characteristics, animation has continuously expanded its global influence, showing a highly dynamic development trend over the past decade—high-quality original overseas works have entered the domestic market in batches through streaming media platforms, promoting the structural upgrading of the local market and the deepening of cross-cultural communication. The period from 2016 to 2025 is even a crucial phase for the industry's transformation from "workshop-style creation" to "assembly-line industrialized production". Mechanisms such as IP development and capital intervention have become increasingly mature, making the animation industry an excellent research sample for observing the industrialization process of cultural industries. Meanwhile, content dissemination in the internet environment exhibits complex and non-linear characteristics. "Blockbuster works that break through niche circles" emerge frequently but are difficult to explain with traditional experience. Their success is often deeply bound to structural factors such as the production capacity layout of production entities, types of content sources, and selection of theme styles. However, most existing studies focus on content analysis, leaving an obvious gap in the quantitative exploration of industrial structure.
Based on the above industry background and research gaps, this study relies on historical data from 2016 to 2025 and is supported by data science methods as the core, focusing on six specific research directions: first, building a multi-dimensional data visualization Dashboard to realize the intuitive exploration of core data such as animation genres, dissemination platforms, and production studios; second, conducting quantitative analysis of popularity-influencing factors, dissecting the core characteristics of high-popularity works from seven dimensions including format, source material, and theme; third, analyzing the industrial capacity structure to explore the ecological pattern of the "long-tail distribution" of Japanese animation studios and the survival logic of small and medium-sized studios; fourth, focusing on the emerging blockbuster genre of Isekai (Another World), exploring the inherent connection between its modular creation and industrialized production; fifth, systematically sorting out the distribution characteristics and development trends of six major animation production source materials such as light novels, manga, and original works; sixth, extracting industrial laws based on the aforementioned analyses to prospectively predict the popularity potential of new anime series in January 2026. Through the above research, it not only deepens the theoretical understanding of the development logic of the animation industry but also provides data-driven practical support for practitioners' strategic layout and investors' decision-making, possessing both academic exploration value and practical application significance.

## Data Sources
- Primary: AniList GraphQL API (https://graphql.anilist.co) — used to collect historical anime metadata (2016–2025) and airing schedules for candidate acquisition (Jan 2026 window).
- Stored datasets:
	- `DataAnalysisPart/animation_data/raw/` — raw CSV exports
	- `DataAnalysisPart/animation_data/cleaned/` — cleaned CSVs used in analysis
	- `public/data/` — data copies used by the dashboard

Key datasets produced:
- `anilist_anime_2016_2025.csv` — historical training dataset (deduplicated)
- `anilist_winter_2026_candidates_filtered.csv` — filtered candidate list for Winter 2026

## Data Collection & Reliability
- Implemented pagination and rate-aware GraphQL requests with retry/backoff for fault tolerance.
- Merged season-based fetches with airing-schedule queries to improve candidate coverage.
- Performed uniqueness, completeness, and format validation; exported CSV files with `utf-8-sig` encoding for multilingual support.

## Data Cleaning & Feature Engineering
Major steps and engineered features used in analysis and modeling:

- Normalized column names and cleaned text fields (`clean_text`, `normalize_columns`).
- Converted dates to `datetime`, standardized missing-day handling (default day=15 where needed).
- Engineered features: `is_sequel`, `genre_count`, `total_duration`, `start_year`, `is_big_studio`, `score_percentile`, `popularity_percentile`.
- Built reusable cleaning/feature pipelines to ensure cross-dataset consistency and reproducibility.

Business rationale: features represent franchise effects, content diversity, production investment, studio reputation, and relative standing over time.

## Modeling & Analysis
- Goal: identify structural drivers of popularity and score, and predict short-term popularity potential for Winter 2026 candidates.
- Analyses performed: correlation analysis, scatter plots (score vs popularity), seasonal aggregations, studio concentration analysis, and outlier inspection.
- Visualizations include distribution plots, heatmaps, time-series peak detection, and interactive scatter plots with annotations.

## Key Findings (summary)
- Popularity and average score are positively correlated but noisy; distribution shows a long tail dominated by a few hits.
- Genre and multi-genre combinations strongly influence both popularity and score distributions.
- Seasonality matters: release season and airing schedule impact early attention cycles.
- Data quality issues (tagging inconsistency, missing studio data) remain important limitations to address.

## Streamlit Dashboard (demo)
- Entry point: `src/app.py` — runs the interactive app with multiple pages under `src/pages/`.
- Features: search by title, filters (genre/year/score), interactive plots (`plotly`, `pyecharts`), and studio-level summaries.
- Performance tips: use `st.cache_data`/`st.cache_resource`, server-side aggregation and pagination for large result sets.

## Notebooks & Locations
- `Final Project Notebook/GroupBD_Final Project notebook.ipynb` — end-to-end analysis, cleaning code, and candidate prediction pipeline.
- `DataAnalysisPart/` — preprocessing notebooks, data cleaning utilities, and exploratory analysis notebooks used to generate figures.

## How to Run (local)
1. Create and activate a virtual environment:

```bash
python -m venv .venv
# PowerShell
.venv\\Scripts\\Activate.ps1
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the dashboard:

```bash
streamlit run src/app.py
```

4. To reproduce analyses, open the notebooks in `Final Project Notebook/` and run cells after ensuring the cleaned CSVs are available under `DataAnalysisPart/animation_data/cleaned/` or `public/data/`.

## Dependencies
Primary Python packages used: `pandas`, `numpy`, `matplotlib`, `plotly`, `pyecharts`, `streamlit`, `streamlit_echarts`, `requests`, `json`, `os`, `datetime`.
See `requirements.txt` for exact versions.

## Reproducibility & Notes
- The notebooks are written to be re-run end-to-end given the raw CSVs. If you re-run data collection against the AniList API, expect variation due to API pagination and live popularity metrics.
- For reproducible results, work from the provided cleaned CSVs and avoid re-scraping unless necessary.

## Future Work & Productionization
- Extend analyses with network analysis (studios/directors/voice actors) and sentiment analysis on user reviews.
- Productionize with Docker, CI/CD, centralized logging, error reporting, monitoring, and data-drift detection.

## Team
Xu Jianwei, Lü Lirui, Zhou Hang, Pei Yu, Wang Siran — a cross-functional team combining data engineering, analytics, and web visualization skills, united by a shared passion for anime.

