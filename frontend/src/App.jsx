import React, { useState } from 'react';
import axios from 'axios';
import RouteMap from './components/RouteMap';
import './App.css';

function App() {
  const [routes, setRoutes] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchOptimizedRoutes = async () => {
    setLoading(true);
    setError(null);
    try {
      // Example data from API documentation
      const payload = {
        locations: [
          { "lat": 34.0522, "long": -118.2437 },
          { "lat": 34.0622, "long": -118.2537 },
          { "lat": 34.0722, "long": -118.2637 },
          { "lat": 34.0822, "long": -118.2737 },
          { "lat": 34.0922, "long": -118.2837 },
          { "lat": 34.0550, "long": -118.2450 },
          { "lat": 34.0650, "long": -118.2550 }
        ],
        n_vehicles: 2
      };

      const response = await axios.post('/optimize-routes', payload);
      setRoutes(response.data.routes);
    } catch (err) {
      console.error("Error fetching routes:", err);
      setError("Failed to fetch routes. Make sure the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Vehicle Route Optimizer</h1>
        <button onClick={fetchOptimizedRoutes} disabled={loading}>
          {loading ? 'Optimizing...' : 'Generate Optimized Routes'}
        </button>
        {error && <p className="error-message">{error}</p>}
      </header>

      <div className="map-container">
        <RouteMap routes={routes} />
      </div>
    </div>
  );
}

export default App;
