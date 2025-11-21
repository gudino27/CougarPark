"""CougarPark API - Smart Parking Prediction System"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import pandas as pd
import numpy as np
from datetime import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from feature_engineering import FeatureEngineer

app = Flask(__name__)
# Configure CORS for both local development and GitHub Pages deployment
CORS(app, origins=[
    "http://localhost:5173",  # Vite dev server
    "http://localhost:3000",  # Alternative local port
    "https://gudino27.github.io",  # GitHub Pages
    "https://cougarpark.gudinocustom.com"  # Production domain
])

# Get paths relative to project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(PROJECT_ROOT, 'models')
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
CONFIG_FILE = os.path.join(PROJECT_ROOT, 'config.json')
CONFIG_LOCAL_FILE = os.path.join(PROJECT_ROOT, 'config.local.json')

# Load configuration
def load_config():
    """Load configuration from config.json, with optional local override"""
    config = {}

    # Load base config
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
    else:
        print("WARNING: config.json not found, using default settings")
        config = {
            'models': {
                'occupancy': {'enabled': True},
                'enforcement': {'enabled': True}
            }
        }

    # Override with local config if it exists
    if os.path.exists(CONFIG_LOCAL_FILE):
        print(f"Loading local config overrides from {CONFIG_LOCAL_FILE}")
        with open(CONFIG_LOCAL_FILE, 'r') as f:
            local_config = json.load(f)
            # Deep merge local config into base config
            if 'models' in local_config:
                config['models'].update(local_config['models'])

    return config

config = load_config()
OCCUPANCY_ENABLED = config['models']['occupancy'].get('enabled', True)
ENFORCEMENT_ENABLED = config['models']['enforcement'].get('enabled', True)

print("="*80)
print("Loading models...")
print(f"  Occupancy Model: {'ENABLED' if OCCUPANCY_ENABLED else 'DISABLED'}")
print(f"  Enforcement Model: {'ENABLED' if ENFORCEMENT_ENABLED else 'DISABLED'}")
print("="*80)

# Conditionally load models based on config
occupancy_model = None
occupancy_zone_encoder = None
occupancy_features = None
occupancy_metadata = None

# Lot-level LPR model (NEW - for individual lot predictions)
lot_level_lpr_model = None
lot_level_lpr_metadata = None
lot_level_lpr_features = None

enforcement_model = None
enforcement_features = None
enforcement_metadata = None

if OCCUPANCY_ENABLED:
    print("Loading occupancy models...")

    # Load zone-level AMP occupancy model (62 lots)
    with open(f'{MODEL_DIR}/occupancy_lightgbm_tuned.pkl', 'rb') as f:
        occupancy_model = pickle.load(f)

    with open(f'{MODEL_DIR}/occupancy_zone_encoder.pkl', 'rb') as f:
        occupancy_zone_encoder = pickle.load(f)

    with open(f'{MODEL_DIR}/occupancy_feature_list_lags.pkl', 'rb') as f:
        occupancy_features = pickle.load(f)

    with open(f'{MODEL_DIR}/occupancy_model_metadata.json', 'r') as f:
        occupancy_metadata = json.load(f)
    print("  Zone-level occupancy model loaded (62 lots with AMP data)")

    # Load lot-level LPR model (185 lots)
    try:
        with open(f'{MODEL_DIR}/occupancy_lot_level_lpr_model.pkl', 'rb') as f:
            lot_level_lpr_model = pickle.load(f)

        with open(f'{MODEL_DIR}/occupancy_lot_level_lpr_metadata.json', 'r') as f:
            lot_level_lpr_metadata = json.load(f)
            lot_level_lpr_features = lot_level_lpr_metadata['features']['feature_list']

        print(f"  Lot-level LPR model loaded ({lot_level_lpr_metadata['num_lots']} lots)")
    except FileNotFoundError:
        print("  WARNING: Lot-level LPR model not found, only zone-level predictions available")

if ENFORCEMENT_ENABLED:
    print("Loading enforcement model...")
    with open(f'{MODEL_DIR}/enforcement_xgboost_tuned.pkl', 'rb') as f:
        enforcement_model = pickle.load(f)

    with open(f'{MODEL_DIR}/enforcement_feature_list_lags.pkl', 'rb') as f:
        enforcement_features = pickle.load(f)

    with open(f'{MODEL_DIR}/enforcement_model_metadata.json', 'r') as f:
        enforcement_metadata = json.load(f)
    print("  Enforcement model loaded successfully!")

# Load lot mapping data (prefer version with coordinates if available)
import os
lot_mapping_with_coords = f'{DATA_DIR}/lot_mapping_enhanced_with_coords.csv'
if os.path.exists(lot_mapping_with_coords):
    lot_mapping = pd.read_csv(lot_mapping_with_coords)
    print("  Loaded lot mapping with coordinates")
else:
    lot_mapping = pd.read_csv(f'{DATA_DIR}/lot_mapping_enhanced.csv')
    print("  Loaded lot mapping (no coordinates yet)")

# Build capacity dictionary and lot->AMP zone mapping from lot_mapping_enhanced.csv
zone_capacity_dict = {}
lot_to_amp_zone = {}  # Maps lot_number -> AMP zone name for occupancy predictions
lot_capacities = {}  # Maps lot_number -> capacity
lot_amp_coverage = {}  # Maps lot_number -> AMP coverage ratio (amp_cap / lot_cap)

# Load AMP zone capacities from occupancy data
amp_zone_capacities = {}
if OCCUPANCY_ENABLED:
    occupancy_data_path = f'{DATA_DIR}/processed/occupancy_lot_level_full.csv'
    if os.path.exists(occupancy_data_path):
        occ_df = pd.read_csv(occupancy_data_path)
        amp_zone_capacities = occ_df.groupby('Zone')['Max_Capacity'].first().to_dict()
        print(f"Loaded {len(amp_zone_capacities)} AMP zone capacities from occupancy data")

for _, row in lot_mapping.iterrows():
    lot_num = int(row['Lot_number'])
    capacity = float(row['capacity']) if pd.notna(row.get('capacity')) else 0

    # Store lot capacity
    lot_capacities[lot_num] = capacity

    # Map alternative_location_description (AMP zone names) to capacity
    zone_name = row.get('alternative_location_description')
    if pd.notna(zone_name):
        for name in str(zone_name).split('|'):
            name = name.strip()
            if name:
                if name in zone_capacity_dict:
                    zone_capacity_dict[name] += capacity
                else:
                    zone_capacity_dict[name] = capacity

                # Store first AMP zone name for this lot and calculate coverage
                if lot_num not in lot_to_amp_zone:
                    lot_to_amp_zone[lot_num] = name

                    # Calculate AMP coverage ratio
                    amp_cap = amp_zone_capacities.get(name, 0)
                    if capacity > 0 and amp_cap > 0:
                        coverage_ratio = amp_cap / capacity
                        lot_amp_coverage[lot_num] = coverage_ratio

    # Also add aggregated Zone_Name -> total capacity
    zone_type = row.get('Zone_Name')
    if pd.notna(zone_type):
        if zone_type in zone_capacity_dict:
            zone_capacity_dict[zone_type] += capacity
        else:
            zone_capacity_dict[zone_type] = capacity

print(f"Loaded capacities for {len(zone_capacity_dict)} zones/lots from lot_mapping_enhanced.csv")
print(f"Mapped {len(lot_to_amp_zone)} lots to AMP zones for occupancy predictions")
print(f"  {len([c for c in lot_amp_coverage.values() if c >= 0.8])} lots with good AMP coverage (>=80%)")
print(f"  {len([c for c in lot_amp_coverage.values() if c < 0.8])} lots with partial AMP coverage (<80%), will use time-pattern estimates")

# Load shared data files
calendar_df = pd.read_csv(f'{DATA_DIR}/academic_calendar.csv')
games_df = pd.read_csv(f'{DATA_DIR}/football_games.csv')
weather_df = pd.read_csv(f'{DATA_DIR}/weather_pullman_hourly_2020_2025.csv')
occupancy_history_2025 = pd.read_csv(f'{DATA_DIR}/processed/occupancy_history_2025.csv')

# Load lot-level LPR historical data for lag features
# MEMORY OPTIMIZATION: Only load last 60 days of data (sufficient for 168h lag features)
lpr_history = None
if lot_level_lpr_model is not None:
    lpr_history_path = f'{DATA_DIR}/processed/occupancy_lot_level_lpr_full.csv'
    if os.path.exists(lpr_history_path):
        print(f"Loading lot-level LPR history (last 60 days only)...")
        # Only load recent data to reduce memory usage
        lpr_history = pd.read_csv(
            lpr_history_path,
            parse_dates=['datetime'],
            usecols=['lot_number', 'datetime', 'lpr_scans', 'date', 'hour']  # Only needed columns
        )
        # Filter to last 60 days
        cutoff_date = pd.Timestamp.now() - pd.Timedelta(days=60)
        lpr_history = lpr_history[lpr_history['datetime'] >= cutoff_date].copy()
        print(f"  LPR history loaded: {len(lpr_history):,} records ({lpr_history['lot_number'].nunique()} lots, last 60 days)")
    else:
        print(f"  WARNING: LPR history not found at {lpr_history_path}")

# Initialize feature engineers based on enabled models
feature_engineer_occupancy = None
feature_engineer_enforcement = None

if OCCUPANCY_ENABLED:
    # Load ZONE-LEVEL enforcement history for occupancy predictions
    enforcement_history_zone = pd.read_csv(f'{DATA_DIR}/processed/enforcement_full_extended.csv', parse_dates=['datetime'])
    print(f"Loaded ZONE-LEVEL enforcement history: {len(enforcement_history_zone):,} records")
    print(f"  Unique zones: {enforcement_history_zone['Zone'].nunique()}")

    # Create feature engineer for OCCUPANCY predictions
    feature_engineer_occupancy = FeatureEngineer(
        calendar_df=calendar_df,
        games_df=games_df,
        weather_df=weather_df,
        zone_capacity_dict=zone_capacity_dict,
        occupancy_history_2025=occupancy_history_2025,
        enforcement_history=enforcement_history_zone
    )
    print("  Occupancy feature engineer initialized!")

if ENFORCEMENT_ENABLED:
    # Load ZONE-LEVEL enforcement history for enforcement predictions
    enforcement_history_lot = pd.read_csv(f'{DATA_DIR}/processed/enforcement_full_extended.csv', parse_dates=['datetime'])
    print(f"Loaded ZONE-LEVEL enforcement history: {len(enforcement_history_lot):,} records")
    print(f"  Unique zones: {enforcement_history_lot['Zone'].nunique()}")

    # Create feature engineer for ENFORCEMENT predictions
    feature_engineer_enforcement = FeatureEngineer(
        calendar_df=calendar_df,
        games_df=games_df,
        weather_df=weather_df,
        zone_capacity_dict=zone_capacity_dict,
        occupancy_history_2025=occupancy_history_2025,
        enforcement_history=enforcement_history_lot
    )
    print("  Enforcement feature engineer initialized!")

print("\n" + "="*80)
if OCCUPANCY_ENABLED or ENFORCEMENT_ENABLED:
    print("Models loaded successfully!")
    print(f"Feature engineers initialized with 2025 historical data")
    print(f"  - Zones in history: {occupancy_history_2025['Zone'].nunique()}")
    print(f"  - Weather data: {len(weather_df)} hourly records")
else:
    print("WARNING: All models are disabled!")
print("="*80)

def get_risk_level(probability):
    """Convert probability to risk level"""
    if not enforcement_metadata:
        return 'UNKNOWN'

    thresholds = enforcement_metadata['risk_thresholds']
    if probability < thresholds['VERY_LOW']:
        return 'VERY_LOW'
    elif probability < thresholds['LOW']:
        return 'LOW'
    elif probability < thresholds['MODERATE']:
        return 'MODERATE'
    elif probability < thresholds['HIGH']:
        return 'HIGH'
    else:
        return 'VERY_HIGH'

def get_availability_level(occupancy, capacity):
    """Convert occupancy to availability level"""
    if capacity == 0:
        return 'UNKNOWN'
    
    pct_full = (occupancy / capacity) * 100
    
    if pct_full >= 95:
        return 'VERY_LOW'  # Almost full
    elif pct_full >= 80:
        return 'LOW'
    elif pct_full >= 60:
        return 'MODERATE'
    elif pct_full >= 40:
        return 'GOOD'
    else:
        return 'EXCELLENT'

def get_recommendation_score(availability_level, risk_level):
    """
    Combine availability and risk into a recommendation score (0-100)
    Higher is better
    """
    availability_scores = {
        'EXCELLENT': 100,
        'GOOD': 80,
        'MODERATE': 60,
        'LOW': 40,
        'VERY_LOW': 20,
        'UNKNOWN': 50
    }
    
    risk_penalties = {
        'VERY_LOW': 0,
        'LOW': 10,
        'MODERATE': 25,
        'HIGH': 50,
        'VERY_HIGH': 70
    }
    
    base_score = availability_scores.get(availability_level, 50)
    penalty = risk_penalties.get(risk_level, 25)
    
    return max(0, base_score - penalty)

def get_recommendation_text(score, availability_level, risk_level):
    """Generate human-readable recommendation"""
    if score >= 80:
        return "EXCELLENT CHOICE - Good availability and low ticket risk"
    elif score >= 60:
        return "GOOD OPTION - Decent availability, acceptable risk"
    elif score >= 40:
        return "RISKY - Limited availability or moderate ticket risk"
    elif score >= 20:
        return "NOT RECOMMENDED - Poor availability or high ticket risk"
    else:
        return "AVOID - Very poor availability and/or very high ticket risk"

@app.route('/')
def home():
    """API documentation homepage"""
    return jsonify({
        'name': 'CougarPark API',
        'version': '1.0',
        'description': 'Smart parking prediction system for WSU campus',
        'endpoints': {
            '/api/health': 'Health check',
            '/api/occupancy/predict': 'Predict parking occupancy',
            '/api/enforcement/risk': 'Predict ticket risk',
            '/api/parking/recommend': 'Get combined parking recommendation',
            '/api/zones/list': 'List all available parking zones',
            '/api/zones/<zone_name>/info': 'Get zone information',
            '/api/models/info': 'Get model metadata'
        }
    })

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'models_loaded': OCCUPANCY_ENABLED or ENFORCEMENT_ENABLED,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/status')
def status():
    """Get API and model status"""
    return jsonify({
        'status': 'running',
        'active_models': {
            'occupancy': OCCUPANCY_ENABLED,
            'enforcement': ENFORCEMENT_ENABLED
        },
        'models_info': {
            'occupancy': {
                'enabled': OCCUPANCY_ENABLED,
                'level': 'zone-level' if OCCUPANCY_ENABLED else None,
                'loaded': occupancy_model is not None
            },
            'enforcement': {
                'enabled': ENFORCEMENT_ENABLED,
                'level': 'lot-level' if ENFORCEMENT_ENABLED else None,
                'loaded': enforcement_model is not None
            }
        },
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/occupancy/predict', methods=['POST'])
def predict_occupancy():
    """
    Predict parking occupancy for a given zone and time

    Request body:
    {
        "zone": "Green 5",
        "datetime": "2024-11-15T10:30:00",  // ISO format
        "weather": {  // Optional
            "temp_f": 65,
            "precipitation": 0.0,
            "is_rainy": false
        }
    }
    """
    try:
        if not OCCUPANCY_ENABLED:
            return jsonify({'error': 'Occupancy model is disabled'}), 503

        data = request.json

        zone = data.get('zone')
        dt_str = data.get('datetime')

        if not zone or not dt_str:
            return jsonify({'error': 'Missing required fields: zone, datetime'}), 400

        dt = pd.to_datetime(dt_str)

        # Get all lots in this zone from lot_mapping
        zone_lots = lot_mapping[lot_mapping['Zone_Name'] == zone]

        if len(zone_lots) > 0:
            # This is an aggregated zone - predict for each lot that has AMP data
            total_predicted_occupancy = 0
            total_capacity = 0

            for _, row in zone_lots.iterrows():
                lot_num = int(row['Lot_number'])
                lot_capacity = lot_capacities.get(lot_num, 0)

                # Check if this lot has AMP data
                if lot_num in lot_to_amp_zone:
                    amp_zone = lot_to_amp_zone[lot_num]
                    try:
                        features = feature_engineer_occupancy.create_features(amp_zone, dt, occupancy_zone_encoder)
                        feature_array = feature_engineer_occupancy.features_to_array(features, occupancy_features)

                        lot_occupancy = float(occupancy_model.predict(feature_array)[0])
                        lot_occupancy = max(0, min(lot_occupancy, lot_capacity))

                        total_predicted_occupancy += lot_occupancy
                        total_capacity += lot_capacity
                    except Exception as e:
                        print(f"Warning: Could not predict for lot {lot_num} (AMP zone: {amp_zone}): {e}")
                        # Add capacity even if prediction fails
                        total_capacity += lot_capacity
                else:
                    # No AMP data for this lot, just add capacity
                    total_capacity += lot_capacity

            predicted_occupancy = total_predicted_occupancy
            capacity = total_capacity
        else:
            # Not an aggregated zone - might be a specific AMP zone name
            capacity = zone_capacity_dict.get(zone, 0)

            try:
                features = feature_engineer_occupancy.create_features(zone, dt, occupancy_zone_encoder)
                feature_array = feature_engineer_occupancy.features_to_array(features, occupancy_features)
                predicted_occupancy = float(occupancy_model.predict(feature_array)[0])
                predicted_occupancy = max(0, min(predicted_occupancy, capacity))
            except Exception as e:
                print(f"Warning: Could not predict for zone '{zone}': {e}")
                predicted_occupancy = 0

        available_spaces = max(0, capacity - predicted_occupancy)

        availability_level = get_availability_level(predicted_occupancy, capacity)

        return jsonify({
            'zone': zone,
            'datetime': dt_str,
            'prediction': {
                'occupancy_count': int(predicted_occupancy),
                'available_spaces': int(available_spaces),
                'capacity': int(capacity),
                'percent_full': round((predicted_occupancy / capacity * 100) if capacity > 0 else 0, 1),
                'availability_level': availability_level
            },
            'model_info': {
                'model_type': occupancy_metadata['model_type'],
                'test_mae': float(occupancy_metadata['performance']['test_mae'])
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def create_lot_level_features(lot_number, dt, lpr_history_df):
    """
    Create features for lot-level LPR predictions

    Returns a pandas DataFrame with a single row containing all features
    """
    # Ensure dt is timezone-naive to match lpr_history data
    if hasattr(dt, 'tz') and dt.tz is not None:
        dt = dt.tz_localize(None)

    # Get lot info from mapping
    lot_info = lot_mapping[lot_mapping['Lot_number'] == lot_number]
    if len(lot_info) == 0:
        raise ValueError(f"Lot {lot_number} not found in mapping")

    lot_info = lot_info.iloc[0]
    zone = lot_info['Zone_Name']
    capacity = float(lot_info['capacity']) if pd.notna(lot_info['capacity']) else 0

    # Temporal features
    hour = dt.hour
    day_of_week = dt.dayofweek
    month = dt.month
    year = dt.year
    is_weekend = 1 if day_of_week >= 5 else 0

    # Calendar features from games_df and calendar_df
    date_normalized = dt.normalize()

    # Game day
    games_df['Date'] = pd.to_datetime(games_df['Date']).dt.normalize()
    is_game_day = 1 if date_normalized in games_df['Date'].values else 0

    # Academic calendar events
    calendar_df['Start_Date'] = pd.to_datetime(calendar_df['Start_Date']).dt.normalize()
    calendar_df['End_Date'] = pd.to_datetime(calendar_df['End_Date']).dt.normalize()

    is_dead_week = 0
    is_finals_week = 0
    is_spring_break = 0
    is_thanksgiving_break = 0
    is_winter_break = 0

    for _, event in calendar_df.iterrows():
        if event['Start_Date'] <= date_normalized <= event['End_Date']:
            event_type = event['Event_Type']
            if event_type == 'Dead_Week':
                is_dead_week = 1
            elif event_type == 'Finals_Week':
                is_finals_week = 1
            elif event_type == 'Spring_Break':
                is_spring_break = 1
            elif event_type == 'Thanksgiving_Break':
                is_thanksgiving_break = 1
            elif event_type == 'Winter_Break':
                is_winter_break = 1

    is_any_break = 1 if (is_spring_break or is_thanksgiving_break or is_winter_break) else 0

    # Weather features
    weather_df['date'] = pd.to_datetime(weather_df['date']).dt.normalize()
    weather_row = weather_df[weather_df['date'] == date_normalized]

    if len(weather_row) > 0:
        weather_row = weather_row.iloc[0]
        temp_mean_f = float(weather_row.get('temp_mean_f', 50))
        precipitation_inches = float(weather_row.get('precipitation_inches', 0))
        weather_category = str(weather_row.get('weather_category', 'Clear'))
        is_rainy = int(weather_row.get('is_rainy', 0))
        is_snowy = int(weather_row.get('is_snowy', 0))
        is_cold = int(weather_row.get('is_cold', 0))
        is_hot = int(weather_row.get('is_hot', 0))
    else:
        temp_mean_f = 50.0
        precipitation_inches = 0.0
        weather_category = 'Clear'
        is_rainy = 0
        is_snowy = 0
        is_cold = 0
        is_hot = 0

    # Lag features - look up historical LPR scans
    lag_offsets = [1, 2, 3, 24, 168]  # hours ago
    lag_features = {}

    for lag_hours in lag_offsets:
        lag_dt = dt - pd.Timedelta(hours=lag_hours)

        # Look up LPR scans from history
        hist_row = lpr_history_df[
            (lpr_history_df['lot_number'] == lot_number) &
            (lpr_history_df['datetime'] == lag_dt)
        ]

        if len(hist_row) > 0:
            lag_features[f'lpr_scans_lag_{lag_hours}h'] = int(hist_row.iloc[0]['lpr_scans'])
        else:
            lag_features[f'lpr_scans_lag_{lag_hours}h'] = 0

    # Build feature dictionary
    features = {
        'hour': hour,
        'day_of_week': day_of_week,
        'month': month,
        'year': year,
        'is_weekend': is_weekend,
        'lot_number': lot_number,
        'Zone': zone,
        'capacity': capacity,
        'is_game_day': is_game_day,
        'is_dead_week': is_dead_week,
        'is_finals_week': is_finals_week,
        'is_any_break': is_any_break,
        'temp_mean_f': temp_mean_f,
        'precipitation_inches': precipitation_inches,
        'weather_category': weather_category,
        'is_rainy': is_rainy,
        'is_snowy': is_snowy,
        'is_cold': is_cold,
        'is_hot': is_hot,
        **lag_features
    }

    # Convert to DataFrame
    return pd.DataFrame([features])

@app.route('/api/occupancy/predict-lot', methods=['POST'])
def predict_lot_occupancy():
    """
    Predict parking activity (LPR scans) for a specific lot

    Request body:
    {
        "lot_number": 9,
        "datetime": "2024-11-15T10:30:00",  // ISO format
        "parking_duration_hours": 3  // Optional, defaults to 1
    }
    """
    try:
        if lot_level_lpr_model is None:
            return jsonify({'error': 'Lot-level LPR model not available'}), 503

        if lpr_history is None:
            return jsonify({'error': 'LPR historical data not loaded'}), 503

        data = request.json

        lot_number = data.get('lot_number')
        dt_str = data.get('datetime')
        parking_duration_hours = data.get('parking_duration_hours', 1)

        if lot_number is None or not dt_str:
            return jsonify({'error': 'Missing required fields: lot_number, datetime'}), 400

        lot_number = int(lot_number)
        dt = pd.to_datetime(dt_str)

        # Create features
        features_df = create_lot_level_features(lot_number, dt, lpr_history)

        # Ensure feature order matches model
        features_df = features_df[lot_level_lpr_features]

        # Convert categorical columns to category dtype
        for col in ['Zone', 'weather_category']:
            if col in features_df.columns and features_df[col].dtype == 'object':
                features_df[col] = features_df[col].astype('category')

        # Make prediction
        predicted_scans = float(lot_level_lpr_model.predict(features_df)[0])
        predicted_scans = max(0, predicted_scans)  # No negative predictions

        # Get lot info
        lot_info = lot_mapping[lot_mapping['Lot_number'] == lot_number].iloc[0]
        zone = lot_info['Zone_Name']
        zone_type = str(lot_info.get('zone_type', '')) if pd.notna(lot_info.get('zone_type')) else ''

        # Check if lot is restricted (University Vehicles, ADA, Guest Pass, etc.)
        if 'University' in zone_type or 'ADA' in zone_type or 'Guest' in zone_type:
            return jsonify({'error': f'Lot {lot_number} is restricted to {zone_type}'}), 403

        capacity = float(lot_info['capacity']) if pd.notna(lot_info['capacity']) else 0
        location = str(lot_info.get('location_description', '')) if pd.notna(lot_info.get('location_description')) else ''
        alternative_location = str(lot_info.get('alternative_location_description', '')) if pd.notna(lot_info.get('alternative_location_description')) else ''

        # Add occupancy prediction
        occupancy_data = None
        occupancy_source = None

        # Try AMP-based occupancy first (for PAID lots with AMP sensors AND good coverage)
        # Only use AMP for paid/hourly lots (Yellow zones, garages, meters) where everyone must pay
        # For permit lots (Green, Red, Grey), AMP only tracks ~20-40% who pay, use time-pattern instead
        amp_coverage = lot_amp_coverage.get(lot_number, 0)
        is_paid_lot = (zone.startswith('Yellow') or 'Garage' in location or
                      'GARAGE' in location.upper() or 'Meter' in location or
                      'HOURLY' in location.upper())
        use_amp = (OCCUPANCY_ENABLED and occupancy_model is not None and
                   lot_number in lot_to_amp_zone and amp_coverage >= 0.8 and is_paid_lot)

        if use_amp:
            try:
                # Use the specific AMP zone name for occupancy model
                # The occupancy model was trained on 62 specific AMP zone names like "Green 1 Bustad Lot"
                amp_zone = lot_to_amp_zone[lot_number]
                features = feature_engineer_occupancy.create_features(amp_zone, dt, occupancy_zone_encoder)
                feature_array = feature_engineer_occupancy.features_to_array(features, occupancy_features)
                predicted_occupancy = float(occupancy_model.predict(feature_array)[0])
                predicted_occupancy = max(0, min(predicted_occupancy, capacity))

                available_spaces = max(0, capacity - predicted_occupancy)
                percent_full = round((predicted_occupancy / capacity * 100), 1) if capacity > 0 else 0
                availability_level = get_availability_level(predicted_occupancy, capacity)

                occupancy_data = {
                    'occupancy_count': round(predicted_occupancy, 1),
                    'available_spaces': int(available_spaces),
                    'capacity': int(capacity),
                    'percent_full': percent_full,
                    'availability_level': availability_level,
                    'source': 'amp'
                }
                occupancy_source = 'amp'
            except Exception as e:
                print(f"Warning: Could not generate AMP occupancy prediction for lot {lot_number}: {e}")

        # Fallback: Estimate occupancy based on typical patterns (for lots without AMP data)
        if occupancy_data is None and capacity > 0:
            # Estimate occupancy based on time patterns
            # Typical university parking patterns:
            hour = dt.hour
            day_of_week = dt.dayofweek  # 0=Monday, 6=Sunday
            is_weekend = day_of_week >= 5
            month = dt.month

            # Determine if semester is in session
            # WSU academic calendar: Fall (Aug-Dec), Spring (Jan-May), Summer (Jun-Aug)
            is_summer = month in [6, 7] or (month == 8 and dt.day < 20)
            is_winter_break = (month == 12 and dt.day > 15) or (month == 1 and dt.day < 10)
            is_spring_break = month == 3 and 10 <= dt.day <= 20
            in_session = not (is_summer or is_winter_break or is_spring_break)

            # Base occupancy rates by time of day and semester status
            if not in_session:
                # Summer/breaks: very low occupancy
                if is_weekend:
                    base_rate = 0.02  # 2% on weekends
                elif 8 <= hour <= 17:
                    base_rate = 0.05  # 5% during day
                else:
                    base_rate = 0.01  # 1% off hours
            elif is_weekend:
                # Weekends during semester: low occupancy
                if 9 <= hour <= 17:
                    base_rate = 0.20  # 20% during day
                else:
                    base_rate = 0.10  # 10% off hours
            else:
                # Weekdays during semester: high occupancy
                if 8 <= hour <= 17:
                    base_rate = 0.55  # 55% during peak hours
                elif 7 <= hour < 8 or 17 < hour <= 19:
                    base_rate = 0.35  # 35% shoulder hours
                else:
                    base_rate = 0.15  # 15% off hours

            # Adjust based on zone type (permit vs paid)
            zone_type = lot_info.get('zone_type', 'Permit')
            if zone_type == 'Paid':
                base_rate *= 0.8  # Paid lots typically less full

            estimated_occupancy = capacity * base_rate

            available_spaces = max(0, capacity - estimated_occupancy)
            percent_full = round((estimated_occupancy / capacity * 100), 1) if capacity > 0 else 0
            availability_level = get_availability_level(estimated_occupancy, capacity)

            occupancy_data = {
                'occupancy_count': round(estimated_occupancy, 1),
                'available_spaces': int(available_spaces),
                'capacity': int(capacity),
                'percent_full': percent_full,
                'availability_level': availability_level,
                'source': 'time_pattern_estimate'
            }
            occupancy_source = 'time_pattern_estimate'

        # Add enforcement prediction if enabled
        # Calculate cumulative risk: probability of getting a ticket at least once during parking duration
        enforcement_data = None
        if ENFORCEMENT_ENABLED and enforcement_model is not None:
            try:
                # Calculate probability of NO ticket in each hour, then get inverse
                probability_no_ticket = 1.0
                max_hourly_risk = 0.0
                max_risk_hour = dt

                # Check enforcement risk for each hour during parking duration
                for hour_offset in range(int(parking_duration_hours)):
                    current_time = dt + pd.Timedelta(hours=hour_offset)
                    features = feature_engineer_enforcement.create_features(zone, current_time, occupancy_zone_encoder)
                    feature_array = feature_engineer_enforcement.features_to_array(features, enforcement_features)
                    hourly_risk = float(enforcement_model.predict_proba(feature_array)[0][1])
                    hourly_risk = max(0.0, min(hourly_risk, 1.0))

                    # Track highest single-hour risk for display
                    if hourly_risk > max_hourly_risk:
                        max_hourly_risk = hourly_risk
                        max_risk_hour = current_time

                    # Multiply probability of no ticket: P(no ticket all hours) = (1-p1)*(1-p2)*...
                    probability_no_ticket *= (1.0 - hourly_risk)

                # Cumulative risk: P(at least one ticket) = 1 - P(no tickets at all)
                cumulative_risk = 1.0 - probability_no_ticket
                cumulative_risk = max(0.0, min(cumulative_risk, 1.0))

                risk_level = get_risk_level(cumulative_risk)

                enforcement_data = {
                    'probability': round(cumulative_risk, 4),
                    'percentage': round(cumulative_risk * 100, 1),
                    'level': risk_level,
                    'message': enforcement_metadata['risk_messages'][risk_level],
                    'peak_risk_time': max_risk_hour.strftime('%I:%M %p'),
                    'parking_duration_hours': int(parking_duration_hours)
                }
            except Exception as e:
                print(f"Warning: Could not generate enforcement prediction: {e}")
                enforcement_data = None

        response = {
            'lot_number': int(lot_number),
            'zone': zone,
            'location': location,
            'alternative_location': alternative_location,
            'datetime': dt_str,
            'lpr_activity': {
                'lpr_scans_predicted': round(predicted_scans, 2),
                'activity_level': 'high' if predicted_scans > 5 else 'moderate' if predicted_scans > 1 else 'low'
            },
            'model_info': {
                'model_type': lot_level_lpr_metadata['model_type'],
                'test_mae': float(lot_level_lpr_metadata['performance']['test_mae']),
                'num_lots': lot_level_lpr_metadata['num_lots']
            }
        }

        if occupancy_data:
            response['occupancy'] = occupancy_data

        if enforcement_data:
            response['enforcement'] = enforcement_data

        return jsonify(response)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/enforcement/risk', methods=['POST'])
def predict_enforcement_risk():
    """
    Predict enforcement/ticket risk for a given zone and time

    Request body:
    {
        "zone": "Green 5",
        "datetime": "2024-11-15T10:30:00",
        "is_game_day": false,  // Optional
        "is_finals_week": false  // Optional
    }
    """
    try:
        if not ENFORCEMENT_ENABLED:
            return jsonify({'error': 'Enforcement model is disabled'}), 503

        data = request.json

        zone = data.get('zone')
        dt_str = data.get('datetime')

        if not zone or not dt_str:
            return jsonify({'error': 'Missing required fields: zone, datetime'}), 400

        dt = pd.to_datetime(dt_str)

        features = feature_engineer_enforcement.create_features(zone, dt, occupancy_zone_encoder)
        feature_array = feature_engineer_enforcement.features_to_array(features, enforcement_features)

        risk_probability = float(enforcement_model.predict_proba(feature_array)[0][1])
        risk_probability = max(0.0, min(risk_probability, 1.0))

        risk_level = get_risk_level(risk_probability)

        risk_messages = enforcement_metadata['risk_messages']

        return jsonify({
            'zone': zone,
            'datetime': dt_str,
            'risk': {
                'probability': round(risk_probability, 4),
                'level': risk_level,
                'message': risk_messages[risk_level],
                'percentage': round(risk_probability * 100, 1)
            },
            'model_info': {
                'model_type': enforcement_metadata['model_type'],
                'test_roc_auc': float(enforcement_metadata['performance']['test_roc_auc'])
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/parking/recommend', methods=['POST'])
def recommend_parking():
    """
    Get combined parking recommendation (occupancy + enforcement)
    Adapts based on which models are enabled

    Request body:
    {
        "zone": "Green 5",
        "datetime": "2024-11-15T10:30:00",
        "duration_hours": 3,  // Optional, defaults to 1
        "weather": {  // Optional
            "temp_f": 65,
            "precipitation": 0.0
        },
        "is_game_day": false,  // Optional
        "is_finals_week": false  // Optional
    }
    """
    try:
        data = request.json

        zone = data.get('zone')
        dt_str = data.get('datetime')
        duration_hours = int(data.get('duration_hours', 1))

        if not zone or not dt_str:
            return jsonify({'error': 'Missing required fields: zone, datetime'}), 400

        if not OCCUPANCY_ENABLED and not ENFORCEMENT_ENABLED:
            return jsonify({'error': 'All models are disabled'}), 503

        dt = pd.to_datetime(dt_str)

        # Initialize response
        response = {
            'zone': zone,
            'datetime': dt_str,
            'active_models': {
                'occupancy': OCCUPANCY_ENABLED,
                'enforcement': ENFORCEMENT_ENABLED
            }
        }

        # Predict occupancy if model is enabled
        occupancy_data = None
        availability_level = 'UNKNOWN'

        if OCCUPANCY_ENABLED:
            # Get all lots in this zone from lot_mapping
            zone_lots = lot_mapping[lot_mapping['Zone_Name'] == zone]

            if len(zone_lots) > 0:
                # This is an aggregated zone - predict for each lot that has AMP data
                total_predicted_occupancy = 0
                total_capacity = 0

                for _, row in zone_lots.iterrows():
                    lot_num = int(row['Lot_number'])
                    lot_capacity = lot_capacities.get(lot_num, 0)

                    # Check if this lot has AMP data
                    if lot_num in lot_to_amp_zone:
                        amp_zone = lot_to_amp_zone[lot_num]
                        try:
                            features = feature_engineer_occupancy.create_features(amp_zone, dt, occupancy_zone_encoder)
                            occupancy_feature_array = feature_engineer_occupancy.features_to_array(features, occupancy_features)

                            lot_occupancy = float(occupancy_model.predict(occupancy_feature_array)[0])
                            lot_occupancy = max(0, min(lot_occupancy, lot_capacity))

                            total_predicted_occupancy += lot_occupancy
                            total_capacity += lot_capacity
                        except Exception as e:
                            print(f"Warning: Could not predict occupancy for lot {lot_num} (AMP zone: {amp_zone}): {e}")
                            # Add capacity even if prediction fails
                            total_capacity += lot_capacity
                    else:
                        # No AMP data for this lot, just add capacity
                        total_capacity += lot_capacity

                predicted_occupancy = total_predicted_occupancy
                capacity = total_capacity
            else:
                # Not an aggregated zone - might be a specific AMP zone name
                capacity = zone_capacity_dict.get(zone, 0)

                try:
                    features = feature_engineer_occupancy.create_features(zone, dt, occupancy_zone_encoder)
                    occupancy_feature_array = feature_engineer_occupancy.features_to_array(features, occupancy_features)
                    predicted_occupancy = float(occupancy_model.predict(occupancy_feature_array)[0])
                    predicted_occupancy = max(0, min(predicted_occupancy, capacity))
                except Exception as e:
                    print(f"Warning: Could not predict for zone '{zone}': {e}")
                    predicted_occupancy = 0

            available_spaces = max(0, capacity - predicted_occupancy)

            availability_level = get_availability_level(predicted_occupancy, capacity)

            occupancy_data = {
                'occupancy_count': int(predicted_occupancy),
                'available_spaces': int(available_spaces),
                'capacity': int(capacity),
                'percent_full': round((predicted_occupancy / capacity * 100) if capacity > 0 else 0, 1),
                'availability_level': availability_level
            }
            response['occupancy'] = occupancy_data
        else:
            response['occupancy'] = None

        # Predict enforcement risk if model is enabled
        enforcement_data = None
        risk_level = 'UNKNOWN'

        if ENFORCEMENT_ENABLED:
            # Calculate cumulative enforcement risk across parking duration
            # Enforcement model predicts HOURLY risk (trained on hourly data)
            # Call model once per hour, then compound probabilities
            hourly_risks = []
            for hour_offset in range(duration_hours):
                hour_dt = dt + pd.Timedelta(hours=hour_offset)
                hour_features = feature_engineer_enforcement.create_features(zone, hour_dt, occupancy_zone_encoder)
                enforcement_feature_array = feature_engineer_enforcement.features_to_array(hour_features, enforcement_features)
                hour_risk = float(enforcement_model.predict_proba(enforcement_feature_array)[0][1])
                hourly_risks.append(max(0.0, min(hour_risk, 1.0)))

            # Compound probability: P(ticket) = 1 - P(no enforcement in all hours)
            no_enforcement_prob = 1.0
            for risk in hourly_risks:
                no_enforcement_prob *= (1 - risk)

            risk_probability = 1 - no_enforcement_prob
            risk_probability = max(0.0, min(risk_probability, 1.0))

            risk_level = get_risk_level(risk_probability)
            risk_messages = enforcement_metadata['risk_messages']

            enforcement_data = {
                'probability': round(risk_probability, 4),
                'level': risk_level,
                'message': risk_messages[risk_level],
                'percentage': round(risk_probability * 100, 1),
                'duration_hours': duration_hours,
                'hourly_risks': [round(r * 100, 2) for r in hourly_risks]
            }
            response['enforcement'] = enforcement_data
        else:
            response['enforcement'] = None

        # Calculate recommendation based on available models
        if OCCUPANCY_ENABLED and ENFORCEMENT_ENABLED:
            # Both models enabled - use combined logic
            score = get_recommendation_score(availability_level, risk_level)
            recommendation = get_recommendation_text(score, availability_level, risk_level)
        elif OCCUPANCY_ENABLED:
            # Only occupancy enabled - base recommendation on availability
            availability_scores = {'EXCELLENT': 100, 'GOOD': 80, 'MODERATE': 60, 'LOW': 40, 'VERY_LOW': 20, 'UNKNOWN': 50}
            score = availability_scores.get(availability_level, 50)
            if score >= 80:
                recommendation = "EXCELLENT AVAILABILITY - Plenty of spaces likely available"
            elif score >= 60:
                recommendation = "GOOD AVAILABILITY - Should find parking with moderate search"
            elif score >= 40:
                recommendation = "LIMITED AVAILABILITY - May take some time to find parking"
            else:
                recommendation = "LOW AVAILABILITY - Very limited parking expected"
        elif ENFORCEMENT_ENABLED:
            # Only enforcement enabled - base recommendation on risk
            risk_scores = {'VERY_LOW': 100, 'LOW': 75, 'MODERATE': 50, 'HIGH': 25, 'VERY_HIGH': 0, 'UNKNOWN': 50}
            score = risk_scores.get(risk_level, 50)
            if score >= 75:
                recommendation = "LOW TICKET RISK - Safe to park here"
            elif score >= 50:
                recommendation = "MODERATE TICKET RISK - Exercise caution"
            elif score >= 25:
                recommendation = "HIGH TICKET RISK - Consider alternative parking"
            else:
                recommendation = "VERY HIGH TICKET RISK - Not recommended"
        else:
            score = 0
            recommendation = "No models available"

        response['recommendation'] = {
            'score': score,
            'text': recommendation,
            'should_park': score >= 50
        }

        # Add lot information
        zone_lots = lot_mapping[lot_mapping['Zone_Name'] == zone]
        lots = []
        for _, row in zone_lots.head(5).iterrows():
            # Prefer alternative_location_description, fallback to location_description or Zone_Name
            location = row.get('alternative_location_description')
            if pd.isna(location) or not location:
                location = row.get('location_description', row.get('Zone_Name', 'Unknown'))

            lots.append({
                'lot_number': int(row['Lot_number']),
                'location': location
            })

        response['lots'] = lots[:5]

        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/zones/list')
def list_zones():
    """List all available parking zones (excluding restricted zones)"""
    try:
        # Exclude restricted zones from recommendations
        excluded_zones = {'Authorized Vehicles Only', 'Buisness Parking'}

        zones = sorted([z for z in zone_capacity_dict.keys() if z not in excluded_zones])

        zone_info = []
        for zone in zones:
            capacity = zone_capacity_dict.get(zone, 0)
            lots_count = len(lot_mapping[lot_mapping['alternative_location_description'] == zone])

            zone_info.append({
                'name': zone,
                'capacity': int(capacity),
                'lots_count': lots_count
            })

        return jsonify({
            'total_zones': len(zones),
            'zones': zone_info
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/lots/list')
def list_lots():
    """List all available parking lots (excluding Business and Authorized lots)"""
    try:
        lots_list = []
        for _, row in lot_mapping.iterrows():
            zone_type = str(row.get('zone_type', 'Unknown')) if pd.notna(row.get('zone_type')) else 'Unknown'

            # Skip restricted lots (University Vehicles, ADA, Guest Pass, etc.)
            if 'University' in zone_type or 'ADA' in zone_type or 'Guest' in zone_type:
                continue

            lot_info = {
                'lot_number': int(row['Lot_number']),
                'zone_name': str(row['Zone_Name']) if pd.notna(row['Zone_Name']) else 'Unknown',
                'location': str(row['location_description']) if pd.notna(row.get('location_description')) else '',
                'zone_type': zone_type,
                'capacity': int(row['capacity']) if pd.notna(row.get('capacity')) else 0
            }

            if pd.notna(row.get('alternative_location_description')):
                lot_info['alternative_location'] = str(row['alternative_location_description'])

            # Add coordinates if available
            if pd.notna(row.get('latitude')) and pd.notna(row.get('longitude')):
                lot_info['latitude'] = float(row['latitude'])
                lot_info['longitude'] = float(row['longitude'])

            # Add additional coordinates if available (for split lots)
            if pd.notna(row.get('additional_coords')):
                lot_info['additional_coords'] = str(row['additional_coords'])

            lots_list.append(lot_info)

        return jsonify({
            'total_lots': len(lots_list),
            'lots': lots_list
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/zones/<zone_name>/info')
def get_zone_info(zone_name):
    """Get detailed information about a specific zone"""
    try:
        # Get zone capacity
        capacity = zone_capacity_dict.get(zone_name, 0)
        
        # Get lots in this zone
        zone_lots = lot_mapping[lot_mapping['Zone_Name'] == zone_name]
        
        lots = []
        for _, row in zone_lots.iterrows():
            lots.append({
                'lot_number': int(row['Lot_number']),
                'location': row['location_description'],
                'lot_name': row.get('lot_name', 'N/A')
            })
        
        return jsonify({
            'zone': zone_name,
            'capacity': int(capacity),
            'lots_count': len(lots),
            'lots': lots
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/models/info')
def get_models_info():
    """Get information about the loaded models"""
    response = {
        'active_models': {
            'occupancy': OCCUPANCY_ENABLED,
            'enforcement': ENFORCEMENT_ENABLED
        }
    }

    if OCCUPANCY_ENABLED and occupancy_metadata:
        response['occupancy_model'] = {
            'enabled': True,
            'type': occupancy_metadata['model_type'],
            'performance': occupancy_metadata['performance'],
            'training_date': occupancy_metadata['training_date'],
            'features_count': occupancy_metadata['features']['total'],
            'level': 'zone-level'
        }
    else:
        response['occupancy_model'] = {
            'enabled': False,
            'message': 'Occupancy model is disabled'
        }

    if ENFORCEMENT_ENABLED and enforcement_metadata:
        response['enforcement_model'] = {
            'enabled': True,
            'type': enforcement_metadata['model_type'],
            'performance': enforcement_metadata['performance'],
            'training_date': enforcement_metadata['training_date'],
            'features_count': enforcement_metadata['features']['total'],
            'level': 'lot-level'
        }
    else:
        response['enforcement_model'] = {
            'enabled': False,
            'message': 'Enforcement model is disabled'
        }

    return jsonify(response)

@app.route('/api/feedback/submit', methods=['POST'])
def submit_feedback():
    """
    Submit user feedback on parking prediction accuracy

    Request body:
    {
        "zone": "CUE Garage",
        "datetime": "2024-11-15T10:30:00",
        "predicted_occupancy": 250,
        "predicted_available": 625,
        "found_parking": true,
        "search_duration_minutes": 5  // Optional
    }
    """
    try:
        data = request.json

        required_fields = ['zone', 'datetime', 'found_parking']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        data['submission_time'] = datetime.now().isoformat()

        feedback_file = f'{DATA_DIR}/processed/user_feedback.csv'
        feedback_df = pd.DataFrame([data])

        if os.path.exists(feedback_file):
            feedback_df.to_csv(feedback_file, mode='a', header=False, index=False)
        else:
            feedback_df.to_csv(feedback_file, mode='w', header=True, index=False)

        return jsonify({
            'status': 'success',
            'message': 'Feedback submitted successfully',
            'thank_you': 'Your feedback helps improve our predictions!'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/feedback/stats', methods=['GET'])
def get_feedback_stats():
    """Get statistics on prediction accuracy from user feedback"""
    try:
        feedback_file = f'{DATA_DIR}/processed/user_feedback.csv'

        if not os.path.exists(feedback_file):
            return jsonify({
                'total_feedback': 0,
                'message': 'No feedback data available yet'
            })

        feedback = pd.read_csv(feedback_file)

        total = len(feedback)
        found_parking = feedback['found_parking'].sum()
        accuracy_rate = (found_parking / total * 100) if total > 0 else 0

        zone_stats = feedback.groupby('zone').agg({
            'found_parking': ['count', 'sum', 'mean']
        }).round(3)

        zone_stats.columns = ['total_searches', 'successful', 'success_rate']
        zone_stats = zone_stats.reset_index().to_dict('records')

        return jsonify({
            'total_feedback': int(total),
            'overall_success_rate': round(accuracy_rate, 2),
            'by_zone': zone_stats
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*80)
    print("CougarPark API Server Starting...")
    print("="*80)

    if OCCUPANCY_ENABLED and occupancy_metadata:
        print(f"\nOccupancy Model: {occupancy_metadata['model_type']}")
        print(f"  Test MAE: {occupancy_metadata['performance']['test_mae']:.3f} cars")
        print(f"  Status: ENABLED (zone-level)")
    else:
        print("\nOccupancy Model: DISABLED")

    if ENFORCEMENT_ENABLED and enforcement_metadata:
        print(f"\nEnforcement Model: {enforcement_metadata['model_type']}")
        print(f"  Test ROC-AUC: {enforcement_metadata['performance']['test_roc_auc']:.4f}")
        print(f"  Status: ENABLED (lot-level)")
    else:
        print("\nEnforcement Model: DISABLED")

    print("\n" + "="*80)
    print("Server running at: http://localhost:5000")
    print("API Documentation: http://localhost:5000")
    print("API Status: http://localhost:5000/api/status")
    print("="*80 + "\n")

    app.run(debug=False, host='0.0.0.0', port=5000)
