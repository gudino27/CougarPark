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
CORS(app)

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

enforcement_model = None
enforcement_features = None
enforcement_metadata = None

if OCCUPANCY_ENABLED:
    print("Loading occupancy model...")
    with open(f'{MODEL_DIR}/occupancy_lightgbm_tuned.pkl', 'rb') as f:
        occupancy_model = pickle.load(f)

    with open(f'{MODEL_DIR}/occupancy_zone_encoder.pkl', 'rb') as f:
        occupancy_zone_encoder = pickle.load(f)

    with open(f'{MODEL_DIR}/occupancy_feature_list_lags.pkl', 'rb') as f:
        occupancy_features = pickle.load(f)

    with open(f'{MODEL_DIR}/occupancy_model_metadata.json', 'r') as f:
        occupancy_metadata = json.load(f)
    print("  Occupancy model loaded successfully!")

if ENFORCEMENT_ENABLED:
    print("Loading enforcement model...")
    with open(f'{MODEL_DIR}/enforcement_xgboost_tuned.pkl', 'rb') as f:
        enforcement_model = pickle.load(f)

    with open(f'{MODEL_DIR}/enforcement_feature_list_lags.pkl', 'rb') as f:
        enforcement_features = pickle.load(f)

    with open(f'{MODEL_DIR}/enforcement_model_metadata.json', 'r') as f:
        enforcement_metadata = json.load(f)
    print("  Enforcement model loaded successfully!")

lot_mapping = pd.read_csv(f'{DATA_DIR}/lot_mapping_enhanced.csv')

# Build capacity dictionary from lot_mapping_enhanced.csv
# Map alternative_location_description -> capacity for all lots
zone_capacity_dict = {}
for _, row in lot_mapping.iterrows():
    zone_name = row.get('alternative_location_description')
    if pd.notna(zone_name) and pd.notna(row.get('capacity')):
        capacity = float(row['capacity'])
        if zone_name in zone_capacity_dict:
            zone_capacity_dict[zone_name] += capacity
        else:
            zone_capacity_dict[zone_name] = capacity

    # Also add Zone_Name as fallback
    zone_type = row.get('Zone_Name')
    if pd.notna(zone_type) and pd.notna(row.get('capacity')):
        capacity = float(row['capacity'])
        if zone_type in zone_capacity_dict:
            zone_capacity_dict[zone_type] += capacity
        else:
            zone_capacity_dict[zone_type] = capacity

print(f"Loaded capacities for {len(zone_capacity_dict)} zones/lots from lot_mapping_enhanced.csv")

# Load shared data files
calendar_df = pd.read_csv(f'{DATA_DIR}/academic_calendar.csv')
games_df = pd.read_csv(f'{DATA_DIR}/football_games.csv')
weather_df = pd.read_csv(f'{DATA_DIR}/weather_pullman_hourly_2020_2025.csv')
occupancy_history_2025 = pd.read_csv(f'{DATA_DIR}/processed/occupancy_history_2025.csv')

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
    # Load LOT-LEVEL enforcement history for enforcement predictions
    enforcement_history_lot = pd.read_csv(f'{DATA_DIR}/processed/enforcement_lot_level_extended.csv', parse_dates=['datetime'])
    print(f"Loaded LOT-LEVEL enforcement history: {len(enforcement_history_lot):,} records")
    print(f"  Unique lots: {enforcement_history_lot['Lot_number'].nunique()}")

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
        capacity = zone_capacity_dict.get(zone, 0)

        features = feature_engineer_occupancy.create_features(zone, dt, occupancy_zone_encoder)
        feature_array = feature_engineer_occupancy.features_to_array(features, occupancy_features)

        predicted_occupancy = float(occupancy_model.predict(feature_array)[0])
        predicted_occupancy = max(0, min(predicted_occupancy, capacity))
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
        capacity = zone_capacity_dict.get(zone, 0)

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
            features = feature_engineer_occupancy.create_features(zone, dt, occupancy_zone_encoder)
            occupancy_feature_array = feature_engineer_occupancy.features_to_array(features, occupancy_features)
            predicted_occupancy = float(occupancy_model.predict(occupancy_feature_array)[0])
            predicted_occupancy = max(0, min(predicted_occupancy, capacity))
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
    """List all available parking lots"""
    try:
        lots_list = []
        for _, row in lot_mapping.iterrows():
            lot_info = {
                'lot_number': int(row['Lot_number']),
                'zone_name': row['Zone_Name'],
                'location': row['location_description'],
                'zone_type': row.get('zone_type', 'Unknown')
            }

            if pd.notna(row.get('alternative_location_description')):
                lot_info['alternative_location'] = row['alternative_location_description']

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

    app.run(debug=True, host='0.0.0.0', port=5000)
