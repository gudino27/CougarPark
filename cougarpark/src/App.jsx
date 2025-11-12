import { useState, useEffect } from 'react';
import ZoneSelector from './components/ZoneSelector';
import TimeSelector from './components/TimeSelector';
import PredictionDisplay from './components/PredictionDisplay';
import FindParkingNow from './components/FindParkingNow';
import FeedbackForm from './components/FeedbackForm';
import './App.css';

function App() {
  const [selectedZone, setSelectedZone] = useState(null);
  const [predictionZone, setPredictionZone] = useState(null);
  const [selectedDateTime, setSelectedDateTime] = useState(null);
  const [parkingDuration, setParkingDuration] = useState(1);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeModels, setActiveModels] = useState({
    occupancy: true,
    enforcement: true
  });

  // Fetch active models status on mount
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/status');
        if (response.ok) {
          const data = await response.json();
          setActiveModels(data.active_models);
        }
      } catch (err) {
        console.error('Failed to fetch model status:', err);
      }
    };

    fetchStatus();
  }, []);

  const fetchPrediction = async (zone, datetime, durationHours) => {
    if (!zone || !datetime) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:5000/api/parking/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          zone,
          datetime,
          duration_hours: durationHours || parkingDuration
        })
      });

      if (!response.ok) {
        throw new Error('Failed to fetch prediction');
      }

      const data = await response.json();
      setPrediction(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleZoneChange = (zone, lotInfo) => {
    const zoneForPrediction = lotInfo?.alternative_location || zone;
    setSelectedZone(zone);
    setPredictionZone(zoneForPrediction);
    if (zoneForPrediction && selectedDateTime) {
      fetchPrediction(zoneForPrediction, selectedDateTime, parkingDuration);
    }
  };

  const handleDateTimeChange = (datetime) => {
    setSelectedDateTime(datetime);
    if (predictionZone && datetime) {
      fetchPrediction(predictionZone, datetime, parkingDuration);
    }
  };

  const handleDurationChange = (duration) => {
    setParkingDuration(duration);
    if (predictionZone && selectedDateTime) {
      fetchPrediction(predictionZone, selectedDateTime, duration);
    }
  };

  const handleGetPrediction = () => {
    if (predictionZone && selectedDateTime) {
      fetchPrediction(predictionZone, selectedDateTime, parkingDuration);
    }
  };

  const handleQuickSearch = async () => {
    const now = new Date();
    const datetime = now.toISOString().slice(0, 19);

    setLoading(true);
    setError(null);

    try {
      const zonesResponse = await fetch('http://localhost:5000/api/zones/list');
      const zonesData = await zonesResponse.json();

      const predictions = await Promise.all(
        zonesData.zones.slice(0, 10).map(async (zone) => {
          const response = await fetch('http://localhost:5000/api/parking/recommend', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ zone: zone.name, datetime })
          });
          return response.json();
        })
      );

      const bestZone = predictions.sort((a, b) => b.recommendation.score - a.recommendation.score)[0];

      setSelectedZone(bestZone.zone);
      setSelectedDateTime(datetime);
      setPrediction(bestZone);
    } catch (err) {
      setError('Failed to find best parking');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>CougarPark</h1>
        <p>Smart Parking for WSU Campus</p>
      </header>

      <main className="app-main">
        <FindParkingNow onQuickSearch={handleQuickSearch} />

        <div className="app-grid">
          <div className="left-panel">
            <ZoneSelector
              selectedZone={selectedZone}
              onZoneChange={handleZoneChange}
            />

            <TimeSelector
              selectedDateTime={selectedDateTime}
              onDateTimeChange={handleDateTimeChange}
              onDurationChange={handleDurationChange}
            />

            {predictionZone && selectedDateTime && (
              <button className="predict-button" onClick={handleGetPrediction}>
                Get Prediction
              </button>
            )}
          </div>

          <div className="right-panel">
            <PredictionDisplay
              prediction={prediction}
              loading={loading}
              error={error}
              activeModels={activeModels}
            />

            {prediction && (
              <FeedbackForm
                prediction={prediction}
                onFeedbackSubmitted={() => console.log('Feedback submitted')}
              />
            )}
          </div>
        </div>
      </main>

      <footer className="app-footer">
        <p>Powered by Machine Learning</p>
        <p>WSU CptS 437 Project CourgarPark</p>
      </footer>
    </div>
  );
}

export default App;
