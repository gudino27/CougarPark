# CougarPark

Predicting Parking Availability Across WSU Campus Lots Using Machine Learning

## Project Description

CougarPark addresses the parking challenges at WSU Pullman campus by using machine learning to predict hourly parking availability across campus lots. The system helps approximately 16,000 students, 1,500 faculty/staff, and campus visitors find parking more efficiently.

## Problem Statement

WSU's Pullman campus has limited parking spaces relative to demand. Students typically arrive 15-45 minutes early to find parking spots, especially in high-demand zones near the CUB, library, and academic buildings. Parking availability is unpredictable due to varying factors including class schedules, weather, special events (football games), and seasonal variations.

## Solution Approach

Develop a machine learning model that predicts parking availability on an hourly basis by:

- Analyzing historical parking occupancy data of the past 5 years.
- Incorporating contextual factors: academic calendar, special events, weather conditions
- Providing real-time predictions of available parking spaces per lot
- Suggesting optimal arrival times based on predicted availability

## Target Model Types

- Random Forest Regression
- Gradient Boosting Models
- Time Series Forecasting

Model selection will depend on available data characteristics and prediction accuracy.

## Project Structure

```
437_project/
├── data/              # Raw and processed data files
│   ├── processed/     # Cleaned and transformed data  
│   └── raw/   	       # Original data from transportation department
├── models/            # Saved trained models
├── notebooks/         # Jupyter notebooks for analysis and modeling
└── src/               # Python modules for reusable functions
 
```

## Setup

Create and activate virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Run Jupyter notebooks:

```bash
jupyter notebook
# Or
jupyter lab
```

## Expected Outcomes

- Hourly parking availability predictions for campus lots
- Identification of optimal parking times and locations
- Reduced time spent searching for parking
- Improved campus traffic flow
- Data-driven insights into parking patterns and trends
- see when enforcement is likely to pass by

## Team

Jaime Gudino, Kenneth Son, Kyle Grentz
