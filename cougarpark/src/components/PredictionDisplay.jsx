import './PredictionDisplay.css';

export default function PredictionDisplay({ prediction, loading, error, activeModels = { occupancy: true, enforcement: true } }) {
  if (loading) {
    return (
      <div className="prediction-display loading">
        <div className="spinner"></div>
        <p>Getting prediction...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="prediction-display error">
        <h3>Error</h3>
        <p>{error}</p>
      </div>
    );
  }

  if (!prediction) {
    return (
      <div className="prediction-display empty">
        <p>Select a lot and time to see parking predictions</p>
      </div>
    );
  }

  // Check if this is a lot-level prediction (new format)
  const isLotLevel = prediction.lot_number !== undefined;

  if (isLotLevel) {
    const { location, alternative_location, datetime, occupancy, enforcement } = prediction;

    const getRiskColor = (level) => {
      const colors = {
        'VERY_LOW': '#2e7d32',
        'LOW': '#558b2f',
        'MODERATE': '#f57c00',
        'HIGH': '#e64a19',
        'VERY_HIGH': '#c62828'
      };
      return colors[level] || '#757575';
    };

    const getAvailabilityColor = (level) => {
      const colors = {
        'EXCELLENT': '#2e7d32',
        'GOOD': '#558b2f',
        'MODERATE': '#f57c00',
        'LOW': '#e64a19',
        'VERY_LOW': '#c62828',
        'UNKNOWN': '#757575'
      };
      return colors[level] || '#757575';
    };

    return (
      <div className="prediction-display">
        <div className="prediction-header">
          <h2>{location}</h2>
          {alternative_location && (
            <p className="alternative-location">{alternative_location.replace(/\|/g, ' & ')}</p>
          )}
          <p className="prediction-time">{new Date(datetime).toLocaleString('en-US', {
            month: 'long',
            day: 'numeric',
            year: 'numeric',
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
          })}</p>
        </div>

        <div className="prediction-cards">
          {occupancy && (
            <div className="card occupancy-card">
              <h3>Parking Availability</h3>

              <div className="big-number">
                <span className="number">{occupancy.available_spaces}</span>
                <span className="label">spaces available</span>
              </div>

              <div className="occupancy-bar">
                <div
                  className="occupancy-fill"
                  style={{
                    width: `${occupancy.percent_full}%`,
                    backgroundColor: getAvailabilityColor(occupancy.availability_level)
                  }}
                ></div>
              </div>

              <div className="occupancy-details">
                <div className="detail-row">
                  <span>Occupied:</span>
                  <span className="value">{occupancy.occupancy_count} / {occupancy.capacity}</span>
                </div>
                <div className="detail-row">
                  <span>Percent Full:</span>
                  <span className="value">{occupancy.percent_full}%</span>
                </div>
                <div className="detail-row">
                  <span>Status:</span>
                  <span
                    className="badge"
                    style={{ backgroundColor: getAvailabilityColor(occupancy.availability_level) }}
                  >
                    {occupancy.availability_level}
                  </span>
                </div>
              </div>
            </div>
          )}

          {enforcement && (
            <div className="card enforcement-card">
              <h3>Ticket Risk</h3>

              <div className="big-number">
                <span className="number">{enforcement.percentage}%</span>
                <span className="label">enforcement probability</span>
              </div>

              <div className="risk-level">
                <span
                  className="risk-badge"
                  style={{ backgroundColor: getRiskColor(enforcement.level) }}
                >
                  {enforcement.level} RISK
                </span>
              </div>

              <p className="risk-message">{enforcement.message}</p>
            </div>
          )}
        </div>

        <div className="recommendation-card">
          <h3>Recommendation</h3>
          <div className="recommendation-text">
            {occupancy && (
              <p><strong>Availability:</strong> {occupancy.available_spaces} spaces available ({occupancy.availability_level}).</p>
            )}
            {enforcement && (
              <p><strong>Ticket Risk:</strong> {enforcement.message}</p>
            )}

            {occupancy && occupancy.availability_level === 'VERY_LOW' ? (
              <div className="recommendation-verdict negative">Very limited parking - consider alternative</div>
            ) : occupancy && occupancy.availability_level === 'LOW' ? (
              <div className="recommendation-verdict neutral">Limited parking available</div>
            ) : enforcement && (enforcement.level === 'HIGH' || enforcement.level === 'VERY_HIGH') ? (
              <div className="recommendation-verdict negative">High ticket risk - ensure valid permit</div>
            ) : enforcement && enforcement.level === 'MODERATE' ? (
              <div className="recommendation-verdict neutral">Moderate risk - standard precautions</div>
            ) : (
              <div className="recommendation-verdict positive">Good parking option</div>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Old zone-level format (keep for backward compatibility)
  const { occupancy, enforcement, recommendation, zone, datetime } = prediction;

  // Check if models are actually active (from API response)
  const apiActiveModels = prediction.active_models || activeModels;
  const occupancyEnabled = apiActiveModels.occupancy && occupancy !== null;
  const enforcementEnabled = apiActiveModels.enforcement && enforcement !== null;

  const getAvailabilityColor = (level) => {
    const colors = {
      'EXCELLENT': '#2e7d32',
      'GOOD': '#558b2f',
      'MODERATE': '#f57c00',
      'LOW': '#e64a19',
      'VERY_LOW': '#c62828',
      'UNKNOWN': '#757575'
    };
    return colors[level] || '#757575';
  };

  const getRiskColor = (level) => {
    const colors = {
      'VERY_LOW': '#2e7d32',
      'LOW': '#558b2f',
      'MODERATE': '#f57c00',
      'HIGH': '#e64a19',
      'VERY_HIGH': '#c62828'
    };
    return colors[level] || '#757575';
  };

  const mae = 0.239;
  const uncertainty = `±${Math.round(mae)} cars`;

  return (
    <div className="prediction-display">
      <div className="prediction-header">
        <h2>Prediction for {zone}</h2>
        <p className="prediction-time">{new Date(datetime).toLocaleString('en-US', {
          month: 'long',
          day: 'numeric',
          year: 'numeric',
          hour: 'numeric',
          minute: '2-digit',
          hour12: true
        })}</p>
      </div>

      <div className="prediction-cards">
        {occupancyEnabled && (
          <div className="card occupancy-card">
            <h3>Parking Availability</h3>

            <div className="big-number">
              <span className="number">{occupancy.available_spaces}</span>
              <span className="label">spaces available</span>
            </div>

            <div className="occupancy-bar">
              <div
                className="occupancy-fill"
                style={{
                  width: `${occupancy.percent_full}%`,
                  backgroundColor: getAvailabilityColor(occupancy.availability_level)
                }}
              ></div>
            </div>

            <div className="occupancy-details">
              <div className="detail-row">
                <span>Occupied:</span>
                <span className="value">{occupancy.occupancy_count} / {occupancy.capacity}</span>
              </div>
              <div className="detail-row">
                <span>Percent Full:</span>
                <span className="value">{occupancy.percent_full}%</span>
              </div>
              <div className="detail-row">
                <span>Status:</span>
                <span
                  className="badge"
                  style={{ backgroundColor: getAvailabilityColor(occupancy.availability_level) }}
                >
                  {occupancy.availability_level}
                </span>
              </div>
            </div>

            <div className="uncertainty-info">
              <span className="uncertainty-label">Prediction Uncertainty:</span>
              <span className="uncertainty-value">{uncertainty}</span>
              <div className="uncertainty-explanation">
                Model MAE: {mae} cars - predictions are typically within this range
              </div>
            </div>
          </div>
        )}

        {enforcementEnabled && (
          <div className="card enforcement-card">
            <h3>Ticket Risk</h3>

            <div className="big-number">
              <span className="number">{enforcement.percentage}%</span>
              <span className="label">enforcement probability</span>
            </div>

            <div className="risk-level">
              <span
                className="risk-badge"
                style={{ backgroundColor: getRiskColor(enforcement.level) }}
              >
                {enforcement.level} RISK
              </span>
            </div>

            <p className="risk-message">{enforcement.message}</p>
          </div>
        )}

        {!occupancyEnabled && !enforcementEnabled && (
          <div className="card disabled-card">
            <h3>No Models Active</h3>
            <p>All prediction models are currently disabled.</p>
          </div>
        )}
      </div>

      {(occupancyEnabled || enforcementEnabled) && (
        <div className="recommendation-card">
          <h3>Recommendation</h3>

          {!occupancyEnabled || !enforcementEnabled ? (
            <div className="model-status-info">
              {occupancyEnabled && !enforcementEnabled && (
                <span className="info-badge">Based on Occupancy Only</span>
              )}
              {!occupancyEnabled && enforcementEnabled && (
                <span className="info-badge">Based on Enforcement Risk Only</span>
              )}
            </div>
          ) : null}

          <div className="recommendation-score">
            <div className="score-bar">
              <div
                className="score-fill"
                style={{
                  width: `${recommendation.score}%`,
                  backgroundColor: recommendation.score >= 60 ? '#2e7d32' : recommendation.score >= 40 ? '#f57c00' : '#c62828'
                }}
              ></div>
            </div>
            <span className="score-text">Score: {recommendation.score}/100</span>
          </div>
          <p className="recommendation-text">{recommendation.text}</p>
          {recommendation.should_park ? (
            <div className="recommendation-verdict positive">Good choice for parking</div>
          ) : (
            <div className="recommendation-verdict negative">Consider alternative zones</div>
          )}
        </div>
      )}
    </div>
  );
}
