import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import './ParkingMap.css';

// Fix for default marker icons in React Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

// WSU Campus center coordinates approximatly
const WSU_CENTER = [46.7305, -117.1595];

// Color mapping for zone types
const ZONE_COLORS = {
  'Green 1': '#2ECC71',
  'Green 2': '#2ECC71',
  'Green 3': '#2ECC71',
  'Green 4': '#2ECC71',
  'Green 5': '#2ECC71',
  'Red 1': '#E74C3C',
  'Red 2': '#E74C3C',
  'Red 3': '#E74C3C',
  'Red 4': '#E74C3C',
  'Red 5': '#E74C3C',
  'Yellow 1': '#F39C12',
  'Yellow 2': '#F39C12',
  'Yellow 3': '#F39C12',
  'Yellow 4': '#F39C12',
  'Yellow 5': '#F39C12',
  'Grey 1': '#95A5A6',
  'Grey 2': '#95A5A6',
  'Grey 3': '#95A5A6',
  'Grey 4': '#95A5A6',
  'Grey 5': '#95A5A6',
  'default': '#3498DB'
};

// Create custom marker icon with color and lot number
const createColoredIcon = (color, lotNumber) => {
  return L.divIcon({
    className: 'custom-marker',
    html: `
      <div style="
        background-color: ${color};
        width: 28px;
        height: 28px;
        border-radius: 50%;
        border: 2px solid white;
        box-shadow: 0 2px 5px rgba(0,0,0,0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 11px;
        font-weight: bold;
        text-shadow: 0 0 3px rgba(0,0,0,0.8);
      ">${lotNumber}</div>
    `,
    iconSize: [28, 28],
    iconAnchor: [14, 14],
    popupAnchor: [0, -14]
  });
};

// Component to handle map recentering
function MapUpdater({ center }) {
  const map = useMap();
  useEffect(() => {
    if (center) {
      map.setView(center, 15, { animate: true });  // Zoom level 17 for closer view
    }
  }, [center, map]);
  return null;
}

// Component to fit all markers in view on initial load ONLY
function FitBounds({ lots }) {
  const map = useMap();
  const [hasRun, setHasRun] = useState(false);

  useEffect(() => {
    // Only run once on initial load
    if (lots.length > 0 && !hasRun) {
      const bounds = L.latLngBounds(
        lots.map(lot => [lot.latitude, lot.longitude])
      );
      map.fitBounds(bounds, { padding: [50, 50] });
      setHasRun(true);
    }
  }, [lots, map, hasRun]);

  return null;
}

function ParkingMap({ lots, onLotSelect, selectedZone, predictions }) {
  const [mapCenter, setMapCenter] = useState(WSU_CENTER);

  // Update map center when a lot is selected
  useEffect(() => {
    if (selectedZone && lots.length > 0) {
      const selectedLot = lots.find(lot =>
        lot.zone_name === selectedZone ||
        lot.alternative_location === selectedZone
      );
      if (selectedLot && selectedLot.latitude && selectedLot.longitude) {
        setMapCenter([selectedLot.latitude, selectedLot.longitude]);
      }
    }
  }, [selectedZone, lots]);

  const handleMarkerClick = (lot) => {
    // Pass the lot_number (numeric ID) to the parent
    onLotSelect(lot.lot_number, lot);
    setMapCenter([lot.latitude, lot.longitude]);
  };

  // Filter lots that have coordinates
  const lotsWithCoords = lots.filter(lot => lot.latitude && lot.longitude);

  // Debug logging
  console.log('ParkingMap - Total lots:', lots.length);
  console.log('ParkingMap - Lots with coords:', lotsWithCoords.length);
  if (lotsWithCoords.length > 0) {
    console.log('ParkingMap - Sample lot:', lotsWithCoords[0]);
  }

  if (lotsWithCoords.length === 0) {
    return (
      <div className="parking-map-container">
        <div className="no-coords-message">
          <p>Map is loading coordinates...</p>
          <p>Loaded {lots.length} lots, but only {lotsWithCoords.length} have coordinates.</p>
          <p>Check browser console for details.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="parking-map-container">
      <MapContainer
        center={mapCenter}
        zoom={14}
        style={{ height: '700px', width: '100%' }}
        scrollWheelZoom={true}
      >
        {/* Google Maps Satellite imagery */}
        <TileLayer
          attribution='&copy; Google Maps'
          url={`https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}&key=${import.meta.env.VITE_GOOGLE_MAPS_API_KEY || ''}`}
          maxZoom={20}
        />
        {/* Google Maps hybrid labels overlay */}
        <TileLayer
          attribution='&copy; Google Maps'
          url={`https://mt1.google.com/vt/lyrs=h&x={x}&y={y}&z={z}&key=${import.meta.env.VITE_GOOGLE_MAPS_API_KEY || ''}`}
          maxZoom={20}
        />

        <MapUpdater center={mapCenter} />
        <FitBounds lots={lotsWithCoords} />

        {lotsWithCoords.map((lot) => {
          const color = ZONE_COLORS[lot.zone_name] || ZONE_COLORS['default'];
          const icon = createColoredIcon(color, lot.lot_number);

          // Check if this lot has predictions
          let occupancyText = '';
          if (predictions && predictions.zones) {
            const zoneName = lot.alternative_location || lot.zone_name;
            const prediction = predictions.zones.find(p => p.zone_name === zoneName);
            if (prediction) {
              occupancyText = `\nOccupancy: ${prediction.predicted_occupancy_percentage}% (${prediction.predicted_available_spaces} spaces)`;
            }
          }

          // Parse additional coordinates for split lots
          const coords = [[lot.latitude, lot.longitude]];
          if (lot.additional_coords) {
            // Format: "lat1,lon1;lat2,lon2;lat3,lon3"
            const additionalPairs = lot.additional_coords.split(';');
            additionalPairs.forEach(pair => {
              const [lat, lon] = pair.trim().split(',').map(Number);
              if (!isNaN(lat) && !isNaN(lon)) {
                coords.push([lat, lon]);
              }
            });
          }

          // Create markers for all coordinate pairs
          return coords.map((position, index) => (
            <Marker
              key={`lot-${lot.lot_number}-${index}`}
              position={position}
              icon={icon}
              eventHandlers={{
                click: () => handleMarkerClick(lot)
              }}
            >
              <Popup>
                <div className="marker-popup">
                  <h3>{lot.alternative_location ? lot.alternative_location.replace(/\|/g, ' & ') : lot.zone_name}</h3>
                  <p><strong>Lot #:</strong> {lot.lot_number}</p>
                  <p><strong>Location:</strong> {lot.location}</p>
                  <p><strong>Zone Type:</strong> {lot.zone_type}</p>
                  {occupancyText && <p>{occupancyText}</p>}
                  <button
                    onClick={() => handleMarkerClick(lot)}
                    className="select-lot-btn"
                  >
                    Get Predictions
                  </button>
                </div>
              </Popup>
            </Marker>
          ));
        })}
      </MapContainer>

      {/* Legend */}
      <div className="map-legend">
        <h4>Zone Types</h4>
        <div className="legend-items">
          <div className="legend-item">
            <span className="legend-color" style={{ backgroundColor: ZONE_COLORS['Green 1'] }}></span>
            <span>Green Zones</span>
          </div>
          <div className="legend-item">
            <span className="legend-color" style={{ backgroundColor: ZONE_COLORS['Red 1'] }}></span>
            <span>Red Zones</span>
          </div>
          <div className="legend-item">
            <span className="legend-color" style={{ backgroundColor: ZONE_COLORS['Yellow 1'] }}></span>
            <span>Yellow Zones</span>
          </div>
          <div className="legend-item">
            <span className="legend-color" style={{ backgroundColor: ZONE_COLORS['Grey 1'] }}></span>
            <span>Grey Zones</span>
          </div>
          <div className="legend-item">
            <span className="legend-color" style={{ backgroundColor: ZONE_COLORS['default'] }}></span>
            <span>Other</span>
          </div>
        </div>
        <p className="legend-note">
          Showing {lotsWithCoords.length} of {lots.length} parking lots
        </p>
      </div>
    </div>
  );
}

export default ParkingMap;
