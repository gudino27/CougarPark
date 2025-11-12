import { useState } from 'react';
import './FindParkingNow.css';

export default function FindParkingNow({ onQuickSearch }) {
  const [searching, setSearching] = useState(false);

  const handleFindNow = async () => {
    setSearching(true);
    await onQuickSearch();
    setSearching(false);
  };

  return (
    <div className="find-parking-now">
      <h2>Find Parking Now</h2>
      <p>Get instant recommendations for the best parking options right now</p>

      <button
        className="find-now-button"
        onClick={handleFindNow}
        disabled={searching}
      >
        {searching ? 'Searching...' : 'Find Best Parking Now'}
      </button>
    </div>
  );
}
