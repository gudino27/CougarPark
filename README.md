
<img src="https://github.com/gudino27/CougarPark/blob/b4541b8f5c72b695a94e86aa11cb0c0daa9baf26/cougarpark.png" width="30%" style="position: relative; top: 0; right: 0;" alt="Project Logo"/>

# CougarPark

<div align="center">

<img src="https://img.shields.io/github/license/gudino27/CougarPark?style=flat&logo=opensourceinitiative&logoColor=white&color=0080ff" alt="license">
<img src="https://img.shields.io/github/last-commit/gudino27/CougarPark?style=flat&logo=git&logoColor=white&color=0080ff" alt="last-commit">
<img src="https://img.shields.io/github/languages/top/gudino27/CougarPark?style=flat&color=0080ff" alt="top-language">
<img src="https://img.shields.io/github/languages/count/gudino27/CougarPark?style=flat&color=0080ff" alt="language-count">

<img src="https://img.shields.io/badge/Python-3776AB.svg?style=flat&logo=Python&logoColor=white" alt="Python">
<img src="https://img.shields.io/badge/React-61DAFB.svg?style=flat&logo=React&logoColor=black" alt="React">
<img src="https://img.shields.io/badge/FastAPI-009688.svg?style=flat&logo=FastAPI&logoColor=white" alt="FastAPI">
<img src="https://img.shields.io/badge/Jupyter-F37626.svg?style=flat&logo=Jupyter&logoColor=white" alt="Jupyter">
<img src="https://img.shields.io/badge/scikitlearn-F7931E.svg?style=flat&logo=scikit-learn&logoColor=white" alt="scikit-learn">
<img src="https://img.shields.io/badge/pandas-150458.svg?style=flat&logo=pandas&logoColor=white" alt="pandas">

</div>

---

## Overview

CougarPark is a smart parking prediction system for the WSU Pullman campus. It uses machine learning to forecast parking lot occupancy and enforcement risk, helping students and staff find parking before they drive there.

The system is built on real data from the WSU Transportation Department: License Plate Recognition (LPR) records, AMP parking session logs, and enforcement ticket history spanning multiple years. Weather data from the Open-Meteo API and WSU academic calendar events are integrated as features to improve prediction accuracy.

---

## What It Does

**Occupancy Prediction:** given a parking zone and time, predicts how full the lot is likely to be. Trained on hourly aggregated occupancy rates derived from raw parking session data.

**Enforcement Risk Prediction:** predicts the likelihood of a ticket in a given zone at a given time. Trained on historical ticket and LPR data, with lot-level granularity (CUE Garage, Library Garage, etc. modeled separately).

**User Feedback Loop:** the React frontend collects user confirmations of whether parking was found and how long the search took, providing ground truth for future model iterations.

---

## Data Pipeline

The `notebooks/` directory contains the full ML pipeline in numbered sequence:

**Shared preprocessing:**
- `01_data_exploration.ipynb`: initial examination of raw WSU Transportation data — structure, quality, coverage
- `02_data_preprocessing.ipynb`: merges LPR and AMP data, temporal feature engineering, quality checks
- `03_calendar_enrichment.ipynb` / `04_lpr_calendar_enrichment.ipynb`: integrates WSU academic calendar context
- `06_fetch_weather_data.ipynb` / `07_weather_enrichment.ipynb`: pulls and merges Open-Meteo historical weather
- `08_exploratory_data_analysis.ipynb`: distributions, correlations, temporal patterns
- `09_model_validation_strategy.ipynb`: cross-validation approach to prevent overfitting
- `10_create_amp_zone_mapping.ipynb`: standardizes zone naming across datasets
- `11_data_cleaning_validation.ipynb`: removes stale lots, validates parking type classifications

**Occupancy models:**
- `01_occupancy_data_transformation.ipynb`: converts raw session data to hourly occupancy rates per zone
- `02_occupancy_prediction_models.ipynb`: trains and evaluates occupancy forecasting models

**Enforcement models:**
- `01_ticket_analysis.ipynb` through `10_create_zone_level_from_lots.ipynb`: ticket analysis, pattern identification, fixed camera identification, lot-level and zone-level enforcement model training

---

## Models

| Model | Type | Purpose |
|---|---|---|
| Occupancy | Gradient Boosted (XGBoost / LightGBM) | Predict hourly lot occupancy rate |
| Enforcement Risk | XGBoost with lag + temporal features | Predict ticket likelihood per lot |

Model metadata (features, hyperparameters, performance metrics) stored in `models/`.

---

## Architecture

```
React Frontend (cougarpark/)
        │
        ▼
FastAPI Backend (src/parking_api.py)
        │
   ┌────┴────┐
   ▼         ▼
Occupancy   Enforcement
Model       Risk Model
        │
feature_engineering.py
(temporal, weather, calendar, LPR lag features)
```

---

## Project Structure

```
CougarPark/
├── src/
│   ├── parking_api.py          # FastAPI backend: prediction endpoints, feature prep, model inference
│   └── feature_engineering.py # Feature generation: temporal, weather, enforcement, historical lags
├── notebooks/
│   ├── shared/                 # Data exploration, preprocessing, enrichment, EDA, validation
│   ├── occupancy/              # Occupancy data transformation and model training
│   └── enforcement/            # Ticket analysis, enforcement patterns, risk model training
├── models/
│   ├── occupancy_model_metadata.json
│   └── enforcement_model_metadata.json
├── cougarpark/                 # React + Vite frontend
│   └── src/
│       ├── App.jsx             # Zone/time selection, prediction fetch, recommendations
│       └── components/         # ZoneSelector, TimeSelector, PredictionDisplay, FeedbackForm, FindParkingNow
├── config.json                 # Active models, API config, feature toggles
└── requirements.txt
```

---

## Getting Started

### Prerequisites

- Python ≥ 3.10
- Node.js ≥ 18

### Backend

```bash
git clone https://github.com/gudino27/CougarPark
cd CougarPark

pip install -r requirements.txt
pip install -r src/requirements.txt

# Start the API
python src/parking_api.py
```

### Frontend

```bash
cd cougarpark
npm install
npm run dev
```

### Running the ML Pipeline

Run notebooks in order within each subdirectory: `shared/` first, then `occupancy/` and `enforcement/` in parallel.

```bash
cd notebooks
jupyter notebook
```

### Tests

```bash
pytest
```

---

## License

MIT. See [LICENSE](LICENSE) for details.
