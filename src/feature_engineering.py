"""Feature engineering for parking prediction"""

import pandas as pd
from datetime import datetime, timedelta

class FeatureEngineer:
    """Prepare features for occupancy prediction"""

    def __init__(self, calendar_df, games_df, weather_df, zone_capacity_dict,
                 occupancy_history_2025=None, enforcement_history=None):
        self.calendar = calendar_df
        self.games = games_df
        self.weather = weather_df
        self.zone_capacity_dict = zone_capacity_dict
        self.occupancy_history = occupancy_history_2025
        self.enforcement_history = enforcement_history

        # Detect whether enforcement_history uses Zone or Lot_Name
        if enforcement_history is not None:
            if 'Lot_Name' in enforcement_history.columns:
                self.enforcement_lookup_col = 'Lot_Name'
            elif 'Zone' in enforcement_history.columns:
                self.enforcement_lookup_col = 'Zone'
            else:
                self.enforcement_lookup_col = None
        else:
            self.enforcement_lookup_col = None

        self.calendar['Start_Date'] = pd.to_datetime(self.calendar['Start_Date'])
        self.calendar['End_Date'] = pd.to_datetime(self.calendar['End_Date'])
        self.games['Date'] = pd.to_datetime(self.games['Date'])

        if 'date' in self.weather.columns:
            self.weather['date'] = pd.to_datetime(self.weather['date'])
        else:
            self.weather['date'] = pd.to_datetime(self.weather['datetime']).dt.date

    def create_features(self, zone, dt, zone_encoder):
        """Create feature vector for prediction"""
        if isinstance(dt, str):
            dt = pd.to_datetime(dt)

        features = {}

        features['hour'] = dt.hour
        features['day_of_week'] = dt.dayofweek
        features['month'] = dt.month
        features['year'] = dt.year
        features['is_weekend'] = 1 if dt.dayofweek >= 5 else 0

        # Add time_of_day categorization
        hour = dt.hour
        if 6 <= hour < 12:
            time_of_day = 'Morning'
        elif 12 <= hour < 18:
            time_of_day = 'Afternoon'
        elif 18 <= hour < 22:
            time_of_day = 'Evening'
        elif 22 <= hour < 24:
            time_of_day = 'Night'
        else:  # 0-5
            time_of_day = 'Late Night'

        # Encode time_of_day 
        time_of_day_map = {
            'Afternoon': 0,
            'Evening': 1,
            'Late Night': 2,
            'Morning': 3,
            'Night': 4
        }
        features['time_of_day_code'] = time_of_day_map[time_of_day]

        date_only = dt.date()
        features['is_game_day'] = int(date_only in self.games['Date'].dt.date.values)

        for event_type in ['Dead_Week', 'Finals_Week', 'Spring_Break',
                          'Thanksgiving_Break', 'Winter_Break']:
            event_periods = self.calendar[self.calendar['Event_Type'] == event_type]
            is_in_period = False
            for _, period in event_periods.iterrows():
                if period['Start_Date'].date() <= date_only <= period['End_Date'].date():
                    is_in_period = True
                    break
            features[f'is_{event_type.lower()}'] = int(is_in_period)

        features['is_any_break'] = int(
            features['is_spring_break'] or
            features['is_thanksgiving_break'] or
            features['is_winter_break']
        )

        weather_row = self.weather[self.weather['date'] == date_only]
        if len(weather_row) > 0:
            weather_row = weather_row.iloc[0]
            features['temp_mean_f'] = weather_row.get('temp_mean_f', 50.0)
            features['precipitation_inches'] = weather_row.get('precipitation_inches', 0.0)
            features['is_rainy'] = int(weather_row.get('is_rainy', 0))
            features['is_snowy'] = int(weather_row.get('is_snowy', 0))
            features['is_cold'] = int(weather_row.get('is_cold', 0))
            features['is_hot'] = int(weather_row.get('is_hot', 0))
            features['is_windy'] = int(weather_row.get('is_windy', 0))
        else:
            features['temp_mean_f'] = 50.0
            features['precipitation_inches'] = 0.0
            features['is_rainy'] = 0
            features['is_snowy'] = 0
            features['is_cold'] = 0
            features['is_hot'] = 0
            features['is_windy'] = 0

        features['Max_Capacity'] = self.zone_capacity_dict.get(zone, 100)

        try:
            features['Zone_encoded'] = zone_encoder.transform([zone])[0]
        except:
            features['Zone_encoded'] = 0

        # Compute occupancy lag features
        occupancy_lag_features = self._compute_lag_features(zone, dt)
        features.update(occupancy_lag_features)

        # Compute enforcement lag features
        enforcement_lag_features = self._compute_enforcement_lag_features(zone, dt)
        features.update(enforcement_lag_features)

        # Compute enforcement-specific features 
        enforcement_features = self._compute_enforcement_features(zone, dt)
        features.update(enforcement_features)

        return features

    def _compute_lag_features(self, zone, dt):
        """Compute lag features from 2025 historical averages"""
        lag_features = {
            'occupancy_lag_1': 0.0,
            'occupancy_lag_24': 0.0,
            'occupancy_rolling_3': 0.0,
            'occupancy_rolling_24': 0.0,
            'occupancy_dow_hour_avg': 0.0
        }

        if self.occupancy_history is None:
            return lag_features

        # Filter to this zone
        zone_history = self.occupancy_history[
            self.occupancy_history['Zone'] == zone
        ]

        if len(zone_history) == 0:
            return lag_features

        occupancy_col = 'occupancy_mean' if 'occupancy_mean' in zone_history.columns else 'occupancy_count'

        prev_hour = (dt.hour - 1) % 24
        prev_hour_data = zone_history[zone_history['hour'] == prev_hour]
        if len(prev_hour_data) > 0:
            lag_features['occupancy_lag_1'] = prev_hour_data[occupancy_col].mean()

        same_hour_data = zone_history[zone_history['hour'] == dt.hour]
        if len(same_hour_data) > 0:
            lag_features['occupancy_lag_24'] = same_hour_data[occupancy_col].mean()

        hours_for_rolling = [(dt.hour - i) % 24 for i in range(1, 4)]
        rolling_data = zone_history[zone_history['hour'].isin(hours_for_rolling)]
        if len(rolling_data) > 0:
            lag_features['occupancy_rolling_3'] = rolling_data[occupancy_col].mean()

        lag_features['occupancy_rolling_24'] = zone_history[occupancy_col].mean()

        dow_hour_data = zone_history[
            (zone_history['day_of_week'] == dt.dayofweek) &
            (zone_history['hour'] == dt.hour)
        ]
        if len(dow_hour_data) > 0:
            lag_features['occupancy_dow_hour_avg'] = dow_hour_data[occupancy_col].mean()
        else:
            lag_features['occupancy_dow_hour_avg'] = lag_features['occupancy_lag_24']

        return lag_features

    def _compute_enforcement_lag_features(self, zone, dt):
        """Compute enforcement lag features from historical enforcement data"""
        lag_features = {
            'enforcement_lag_1': 0.0,
            'tickets_lag_1': 0.0,
            'enforcement_lag_24': 0.0,
            'tickets_lag_24': 0.0,
            'enforcement_rolling_3': 0.0,
            'enforcement_rolling_24': 0.0,
            'tickets_rolling_24': 0.0,
            'enforcement_dow_hour_avg': 0.0
        }

        if self.enforcement_history is None or self.enforcement_lookup_col is None:
            return lag_features

        # Filter to this zone or lot 
        zone_history = self.enforcement_history[
            self.enforcement_history[self.enforcement_lookup_col] == zone
        ]

        if len(zone_history) == 0:
            return lag_features

        # Sort by datetime for lag calculations
        zone_history = zone_history.sort_values('datetime')

        # 1. Lag 1 hour 
        lag_1_hour = dt - timedelta(hours=1)
        prev_hour_data = zone_history[zone_history['datetime'] == lag_1_hour]
        if len(prev_hour_data) > 0:
            # has_ticket is binary, but we want enforcement probability
            lag_features['enforcement_lag_1'] = float(prev_hour_data['tickets_issued'].iloc[0] > 0)
            lag_features['tickets_lag_1'] = float(prev_hour_data['tickets_issued'].iloc[0])

        # 2. Lag 24 hours 
        lag_24_hour = dt - timedelta(hours=24)
        prev_day_data = zone_history[zone_history['datetime'] == lag_24_hour]
        if len(prev_day_data) > 0:
            lag_features['enforcement_lag_24'] = float(prev_day_data['tickets_issued'].iloc[0] > 0)
            lag_features['tickets_lag_24'] = float(prev_day_data['tickets_issued'].iloc[0])

        # 3. Rolling 3-hour enforcement rate 
        hours_for_rolling_3 = [dt - timedelta(hours=i) for i in range(1, 4)]
        rolling_3_data = zone_history[zone_history['datetime'].isin(hours_for_rolling_3)]
        if len(rolling_3_data) > 0:
            # Average of binary has_ticket across last 3 hours
            lag_features['enforcement_rolling_3'] = (rolling_3_data['tickets_issued'] > 0).mean()

        # 4. Rolling 24-hour enforcement rate and tickets
        hours_for_rolling_24 = [dt - timedelta(hours=i) for i in range(1, 25)]
        rolling_24_data = zone_history[zone_history['datetime'].isin(hours_for_rolling_24)]
        if len(rolling_24_data) > 0:
            lag_features['enforcement_rolling_24'] = (rolling_24_data['tickets_issued'] > 0).mean()
            lag_features['tickets_rolling_24'] = float(rolling_24_data['tickets_issued'].sum())

        # 5. Day-of-week + hour average 
        dow_hour_data = zone_history[
            (zone_history['datetime'] < dt) &  # Only past data
            (zone_history['day_of_week'] == dt.dayofweek) &
            (zone_history['hour'] == dt.hour)
        ]
        if len(dow_hour_data) > 0:
            lag_features['enforcement_dow_hour_avg'] = (dow_hour_data['tickets_issued'] > 0).mean()

        return lag_features

    def _compute_enforcement_features(self, zone, dt):
        """
        Compute enforcement-specific features that model expects
        These are estimated from historical patterns since we can't know future values
        """
        features = {
            'lpr_scans': 0.0,
            'amp_sessions': 0.0,
            'unpaid_estimate': 0.0,
            'compliance_ratio': 0.0,
            'zone_avg_enforcement': 0.0,
            'vulnerability_score': 0.0,
            'high_risk': 0
        }

        if self.enforcement_history is None or self.enforcement_lookup_col is None:
            return features

        # Calculate zone/lot average enforcement rate 
        zone_history = self.enforcement_history[
            self.enforcement_history[self.enforcement_lookup_col] == zone
        ]

        if len(zone_history) == 0:
            return features

        # Zone average enforcement (mean enforcement rate for this zone)
        features['zone_avg_enforcement'] = (zone_history['tickets_issued'] > 0).mean()

        # Estimate typical lpr_scans, amp_sessions, unpaid_estimate for this zone-dow-hour
        # Use historical averages for same day-of-week and hour
        similar_hours = zone_history[
            (zone_history['day_of_week'] == dt.dayofweek) &
            (zone_history['hour'] == dt.hour)
        ]

        if len(similar_hours) > 0:
            features['lpr_scans'] = similar_hours['lpr_scans'].mean()
            features['amp_sessions'] = similar_hours['amp_sessions'].mean()
            features['unpaid_estimate'] = similar_hours['unpaid_estimate'].mean()

            # Compliance ratio
            if features['lpr_scans'] > 0:
                features['compliance_ratio'] = min(1.0, features['amp_sessions'] / features['lpr_scans'])

            # Vulnerability score
            features['vulnerability_score'] = features['unpaid_estimate'] * features['zone_avg_enforcement']

            # High-risk indicator 
            # 75th percentile of unpaid_estimate and 50th percentile of zone/lot avg_enforcement
            unpaid_75th = zone_history['unpaid_estimate'].quantile(0.75)
            zone_enf_50th = self.enforcement_history.groupby(self.enforcement_lookup_col)['tickets_issued'].apply(
                lambda x: (x > 0).mean()
            ).median()

            features['high_risk'] = int(
                (features['unpaid_estimate'] > unpaid_75th) and
                (features['zone_avg_enforcement'] > zone_enf_50th)
            )

        return features

    def features_to_array(self, features, feature_names):
        """Convert feature dict to DataFrame with proper column names"""
        import pandas as pd
        values = [features.get(name, 0) for name in feature_names]
        return pd.DataFrame([values], columns=feature_names)
