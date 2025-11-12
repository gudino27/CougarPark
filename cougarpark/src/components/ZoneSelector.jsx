import { useState, useEffect } from 'react';
import './ZoneSelector.css';

export default function ZoneSelector({ selectedZone, onZoneChange }) {
  const [lots, setLots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchLots();
  }, []);

  const fetchLots = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/lots/list');
      const data = await response.json();
      setLots(data.lots);
      setLoading(false);
    } catch (err) {
      setError('Failed to load parking lots');
      setLoading(false);
    }
  };

  const filteredLots = lots.filter(lot =>
    lot.lot_number.toString().includes(searchTerm) ||
    lot.zone_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    lot.location.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (lot.alternative_location && lot.alternative_location.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  if (loading) return <div className="zone-selector loading">Loading lots...</div>;
  if (error) return <div className="zone-selector error">{error}</div>;

  return (
    <div className="zone-selector">
      <h3>Select Parking Lot</h3>
      <p className="lot-count">{lots.length} lots available</p>

      <input
        type="text"
        placeholder="Search by lot number, zone, or location..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        className="zone-search"
      />

      <div className="zone-list">
        {filteredLots.map((lot) => (
          <button
            key={`${lot.lot_number}-${lot.zone_name}`}
            className={`zone-item ${selectedZone === lot.zone_name ? 'selected' : ''}`}
            onClick={() => onZoneChange(lot.zone_name, lot)}
          >
            <div className="lot-number">Lot {lot.lot_number}</div>
            <div className="zone-name">{lot.zone_name}</div>
            <div className="zone-details">
              <span className="location">{lot.location}</span>
              {lot.alternative_location && (
                <span className="alt-location">{lot.alternative_location}</span>
              )}
            </div>
          </button>
        ))}
      </div>

      {filteredLots.length === 0 && (
        <div className="no-results">No lots found matching "{searchTerm}"</div>
      )}
    </div>
  );
}
