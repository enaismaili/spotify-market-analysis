Spotify APAC Market Analysis: Local Genre Growth Opportunity

This project analyzes local genre trends across APAC music markets using Spotify’s API. It automates data collection, transforms raw data into structured datasets, and applies advanced analytics techniques such as clustering, opportunity scoring, and content gap analysis. Insights are delivered via JSON outputs and an interactive HTML dashboard.

Note:
Currently, we have example data for India (IN) and Japan (JP). The dashboard visualization component is implemented only for India.

---

Table of Contents
1. Project Overview
2. Data Flow
3. Key Components
4. Running the Project
5. Tests
6. Future Improvements
7. Final Output Screenshots

---

Project Overview

The main goal of this project is to identify growth opportunities for Spotify to deepen its market penetration across APAC music markets by:
- Collecting raw playlist, track, artist, and genre data for specific markets (e.g., India, Japan) from the Spotify API.
- Processing and transforming raw data into structured CSV or JSON formats for deeper analysis.
- Performing advanced analytics to uncover strategic insights, including:
   - Genre Clustering: Discovering which genres naturally group together and analyzing their popularity trends.
   - Market Opportunity Scoring: Evaluating each market’s potential for expansion based on genre diversity, local content representation, and audience engagement.
   - Content Gap Analysis: Identifying underrepresented or emerging genres that present new content or marketing opportunities.
- Delivering insights through structured JSON files and, for India, an interactive HTML dashboard that visualizes key opportunities.

The system is designed to scale easily, supporting expansion into additional APAC markets beyond the initial India and Japan examples.

---

Data Flow

1. Data Collection (`spotify_client.py`): Fetches raw data from Spotify’s API, including playlists, tracks, artists, and genres.
3. Data Processing (`data_processing.py`): Transforms the raw JSON data into structured CSV files for downstream analysis.
4. Data Analysis (`advanced_analytics.py`): Applies advanced analytics techniques such as:
   - Genre clustering (K-Means)
   - Market opportunity scoring
   - Content gap identification (missing or underrepresented genres)
6. Data Storage:
   - Raw JSON files are saved in `collected_data/raw_data/`
   - Processed CSV files are stored in `collected_data/processed_data/`
   - Analytical insights (JSON) are saved in `market_analytics/`
7. Data Visualization (`analyze_market_dashboard.py`): Generates an interactive HTML dashboard based on the processed data and insights.

---

Key Components

1. `spotify_client.py`
- Authenticates via SpotifyClientCredentials.
- Fetches playlists, tracks, artist, and genre data.
- Caches API results to minimize redundant requests.

2. `data_processing.py`
- Converts raw JSON to structured Pandas DataFrames.
- Outputs CSVs for downstream analytics.

3. `advanced_analytics.py`
- Applies clustering (K-Means) on genres.
- Scores markets for growth opportunity.
- Identifies missing or underrepresented genres.

4. Market Scripts
- `analyze_market.py`: Full data pipeline for a market.
- `analyze_market_dashboard.py`: Generates dashboards (currently India only).

5. `config.py`
- Environment settings.
- Spotify API credentials (loaded via `.env` file).
- Market-specific genre lists.

---

Running the Project

```bash
#1. Create and Activate a Virtual Environment
python -m venv venv
source venv/bin/activate     # (Mac/Linux)
venv\Scripts\activate        # (Windows)

#2. Install Dependencies
pip install -r requirements.txt

#3. Set Up Environment Variables
Create a .env file in the root folder and add:
SPOTIPY_CLIENT_ID=your_spotify_client_id
SPOTIPY_CLIENT_SECRET=your_spotify_client_secret

#4. Run Market Analysis
python src/utils/analyze_market.py

#5. Generate the Dashboard
#First, make sure the correct JSON file is loaded in analyze_market_dashboard.py.
#Then run:
python src/utils/analyze_market_dashboard.py

#The dashboard will appear in outputs/ as india_music_market_dashboard.html.
```
---

Tests

- test_spotify_client.py -> Mocks Spotify API and verifies client behavior and caching.
- test_data_processing.py -> Validates correct CSV structure and parsing.

Run tests with: ```bash pytest tests/ ```

---

Future Improvements

- Improve clustering techniques with additional feature engineering (e.g., artist metadata, playlist characteristics).
- Extend dashboard generation to additional APAC markets beyond India.
- Automate multi-market batch processing for faster analysis.
- Add CI/CD pipelines for automated testing and deployment.
- Enhance visualizations with interactive filtering and drill-down capabilities.

--- 

Dashbord Sscreenshots
<img width="1495" alt="Screenshot 2025-04-28 at 16 49 08" src="https://github.com/user-attachments/assets/170b875b-b6f0-4b95-9fc6-9d07a521247f" />
<img width="1230" alt="Screenshot 2025-04-28 at 16 49 47" src="https://github.com/user-attachments/assets/5e6cbb26-a604-44cd-878d-04e533d1933c" />






