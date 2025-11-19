import { useState, useEffect } from 'react';
import './LotSelector.css';

export default function LotSelector({ onLotChange, selectedLot }) {
  const [lots, setLots] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchLots = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/lots/list');
        const data = await response.json();

        // Sort lots by number
        const sortedLots = (data.lots || []).sort((a, b) => a.lot_number - b.lot_number);
        setLots(sortedLots);
      } catch (error) {
        console.error('Failed to fetch lots:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchLots();
  }, []);

  const filteredLots = lots.filter(lot => {
    const searchLower = searchTerm.toLowerCase();
    return (
      lot.lot_number.toString().includes(searchLower) ||
      (lot.zone_name && lot.zone_name.toLowerCase().includes(searchLower)) ||
      (lot.location && lot.location.toLowerCase().includes(searchLower)) ||
      (lot.alternative_location && lot.alternative_location.toLowerCase().includes(searchLower))
    );
  });

  const handleLotSelect = (lot) => {
    onLotChange(lot.lot_number, lot);
  };

  if (loading) {
    return <div className="lot-selector loading">Loading lots...</div>;
  }

  return (
    <div className="lot-selector">
      <h3>Select Parking Lot</h3>

      <input
        type="text"
        className="lot-search"
        placeholder="Search by location name or zone..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
      />

      <div className="lot-list">
        {filteredLots.length === 0 ? (
          <div className="no-lots">No lots found</div>
        ) : (
          filteredLots.map(lot => (
            <div
              key={lot.lot_number}
              className={`lot-item ${selectedLot === lot.lot_number ? 'selected' : ''}`}
              onClick={() => handleLotSelect(lot)}
            >
              <div className="lot-header">
                <span className="lot-location">{lot.location || `Lot ${lot.lot_number}`}</span>
                <span className="lot-zone">{lot.zone_name}</span>
              </div>
              <div className="lot-capacity">
                Capacity: {lot.capacity || 'Unknown'} spaces
              </div>
              {lot.alternative_location && (
                <div className="lot-alternative">{lot.alternative_location.replace(/\|/g, ' & ')}</div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
