import { useState, useEffect } from 'react';
import MapComponent from './MapComponent';
import Sidebar from './Sidebar';

function App() {
  const [zones, setZones] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    fetch(`${apiUrl}/api/v1/zones`)
      .then(res => res.json())
      .then(data => {
        setZones(data.data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching zones", err);
        setLoading(false);
      });
  }, []);

  return (
    <div className="app-container">
      <header className="glass-header">
        <div className="logo">
          <span className="gradient-text">Parking Intelligence</span> System
        </div>
      </header>
      <main className="main-content">
        <Sidebar zones={zones} loading={loading} />
        <div className="map-container">
          <MapComponent zones={zones} />
        </div>
      </main>
    </div>
  );
}

export default App;
