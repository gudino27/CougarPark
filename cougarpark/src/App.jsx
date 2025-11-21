import { useState, useEffect } from 'react';
import LotSelector from './components/LotSelector';
import ParkingMap from './components/ParkingMap';
import TimeSelector from './components/TimeSelector';
import PredictionDisplay from './components/PredictionDisplay';
import FindParkingNow from './components/FindParkingNow';
import FeedbackForm from './components/FeedbackForm';
import { API_URL } from './config';
import './App.css';

function App() {
  const [selectedLot, setSelectedLot] = useState(null);
  const [selectedDateTime, setSelectedDateTime] = useState(null);
  const [parkingDuration, setParkingDuration] = useState(1);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeModels, setActiveModels] = useState({
    occupancy: true,
    enforcement: true
  });
  const [viewMode, setViewMode] = useState('list'); // 'map' or 'list'
  const [lots, setLots] = useState([]);

  // Fetch active models status on mount
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await fetch(`${API_URL}/api/status`);
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

  // Fetch parking lots data on mount
  useEffect(() => {
    const fetchLots = async () => {
      try {
        const response = await fetch(`${API_URL}/api/lots/list`);
        if (response.ok) {
          const data = await response.json();
          setLots(data.lots || []);
        }
      } catch (err) {
        console.error('Failed to fetch lots:', err);
      }
    };

    fetchLots();
  }, []);

  const fetchPrediction = async (lotNumber, datetime) => {
    if (!lotNumber || !datetime) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_URL}/api/occupancy/predict-lot`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          lot_number: lotNumber,
          datetime
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

  const handleLotChange = (lotNumber, lotInfo) => {
    setSelectedLot(lotNumber);
    if (lotNumber && selectedDateTime) {
      fetchPrediction(lotNumber, selectedDateTime);
    }
  };

  const handleDateTimeChange = (datetime) => {
    setSelectedDateTime(datetime);
    if (selectedLot && datetime) {
      fetchPrediction(selectedLot, datetime);
    }
  };

  const handleDurationChange = (duration) => {
    setParkingDuration(duration);
    // Duration not used for lot-level predictions yet
  };

  const handleGetPrediction = () => {
    if (selectedLot && selectedDateTime) {
      fetchPrediction(selectedLot, selectedDateTime);
    }
  };

  const handleQuickSearch = async () => {
    const now = new Date();
    const datetime = now.toISOString().slice(0, 19);

    setLoading(true);
    setError(null);

    try {
      const lotsResponse = await fetch(`${API_URL}/api/lots/list`);
      const lotsData = await lotsResponse.json();

      // Filter out apartment, authorized, and disability lots
      const filteredLots = lotsData.lots.filter(lot => {
        if (!lot.zone_name && !lot.zone_type) return true;
        const zoneName = (lot.zone_name || '').toLowerCase();
        const zoneType = (lot.zone_type || '').toLowerCase();
        return !zoneName.includes('apartment') &&
               !zoneName.includes('authorized') &&
               !zoneName.includes('disability') &&
               !zoneType.includes('ada');
      });

      // Get predictions for all non-apartment lots
      const predictions = await Promise.all(
        filteredLots.map(async (lot) => {
          try {
            const response = await fetch(`${API_URL}/api/occupancy/predict-lot`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ lot_number: lot.lot_number, datetime })
            });
            const data = await response.json();
            return { ...data, lot_info: lot };
          } catch (err) {
            return null;
          }
        })
      );

      // Filter valid predictions with occupancy data and sort by most available spaces
      const validPredictions = predictions.filter(p =>
        p !== null && p.occupancy && p.occupancy.available_spaces > 0
      );

      // Sort by: 1) Most available spaces, 2) Lowest enforcement risk
      const bestLot = validPredictions.sort((a, b) => {
        const spaceDiff = b.occupancy.available_spaces - a.occupancy.available_spaces;
        if (spaceDiff !== 0) return spaceDiff;
        // If same available spaces, prefer lower enforcement risk
        const aRisk = a.enforcement ? a.enforcement.percentage : 0;
        const bRisk = b.enforcement ? b.enforcement.percentage : 0;
        return aRisk - bRisk;
      })[0];

      if (bestLot) {
        setSelectedLot(bestLot.lot_number);
        setSelectedDateTime(datetime);
        setPrediction(bestLot);
      } else {
        setError('No parking available at this time');
      }
    } catch (err) {
      setError('Failed to find best parking: ' + err.message);
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
            {/* View Mode Toggle */}
            <div className="view-toggle">
              <button
                className={`toggle-btn ${viewMode === 'map' ? 'active' : ''}`}
                onClick={() => setViewMode('map')}
              >
                Map View
              </button>
              <button
                className={`toggle-btn ${viewMode === 'list' ? 'active' : ''}`}
                onClick={() => setViewMode('list')}
              >
                List View
              </button>
            </div>

            {viewMode === 'map' ? (
              <ParkingMap
                lots={lots}
                onLotSelect={handleLotChange}
                selectedLot={selectedLot}
                predictions={prediction}
              />
            ) : (
              <LotSelector
                selectedLot={selectedLot}
                onLotChange={handleLotChange}
              />
            )}

            <TimeSelector
              selectedDateTime={selectedDateTime}
              onDateTimeChange={handleDateTimeChange}
              onDurationChange={handleDurationChange}
            />

            {selectedLot && selectedDateTime && (
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
