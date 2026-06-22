import { useEffect } from 'react';
import { MapContainer, TileLayer, Polygon, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';

function BoundsFitter({ zones }: { zones: any[] }) {
  const map = useMap();
  useEffect(() => {
    if (zones && zones.length > 0) {
      const bounds = L.latLngBounds([]);
      zones.forEach(zone => {
        if (zone.geojson && zone.geojson.coordinates) {
          const coords = zone.geojson.coordinates[0].map((coord: any) => [coord[1], coord[0]]);
          bounds.extend(coords);
        }
      });
      if (bounds.isValid()) {
        map.fitBounds(bounds, { padding: [50, 50] });
      }
    }
  }, [zones, map]);
  return null;
}

export default function MapComponent({ zones }: { zones: any[] }) {
  const center: [number, number] = [12.9716, 77.5946];

  const getColor = (score: number) => {
    if (score > 0.7) return '#ef4444';
    if (score > 0.4) return '#f59e0b';
    return '#3b82f6';
  };

  return (
    <MapContainer center={center} zoom={11} style={{ height: '100%', width: '100%' }}>
      <TileLayer
        attribution='&copy; <a href="https://carto.com/attributions">CARTO</a>'
        url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
      />
      {zones.map((zone) => {
        if (!zone.geojson || !zone.geojson.coordinates) return null;
        const positions = zone.geojson.coordinates[0].map((coord: any) => [coord[1], coord[0]]);
        const color = getColor(zone.score);

        return (
          <Polygon 
            key={zone.zone_id} 
            positions={positions}
            pathOptions={{ color, fillColor: color, fillOpacity: 0.4, weight: 2 }}
          >
            <Popup>
              <div style={{ color: '#0f172a' }}>
                <h3 style={{ margin: '0 0 8px 0', fontSize: '16px' }}>Zone {zone.zone_id}</h3>
                <p><strong>Station:</strong> {zone.police_station}</p>
                <p><strong>Top Violation:</strong> {zone.dominant_violation_tag}</p>
                <p><strong>Vehicle Type:</strong> {zone.dominant_vehicle_type}</p>
                <p><strong>Violations:</strong> {zone.violation_count}</p>
                <p><strong>Score:</strong> {zone.score.toFixed(3)}</p>
              </div>
            </Popup>
          </Polygon>
        );
      })}
      <BoundsFitter zones={zones} />
    </MapContainer>
  );
}
