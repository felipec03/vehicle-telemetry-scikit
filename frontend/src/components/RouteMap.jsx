import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Polyline, Marker, Popup, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix for default marker icon in React Leaflet
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});

L.Marker.prototype.options.icon = DefaultIcon;

// Component to update map view bounds based on routes
function MapUpdater({ routes }) {
    const map = useMap();

    useEffect(() => {
        if (routes && Object.keys(routes).length > 0) {
            const allPoints = [];
            Object.values(routes).forEach(route => {
                route.forEach(point => allPoints.push(point));
            });

            if (allPoints.length > 0) {
                const bounds = L.latLngBounds(allPoints);
                map.fitBounds(bounds, { padding: [50, 50] });
            }
        }
    }, [routes, map]);

    return null;
}

const colors = ['blue', 'red', 'green', 'purple', 'orange', 'darkblue', 'darkred'];

const RouteMap = ({ routes }) => {
    // Default center (e.g., Los Angeles as in the example)
    const defaultCenter = [34.0522, -118.2437];

    return (
        <MapContainer center={defaultCenter} zoom={13} style={{ height: '100%', width: '100%' }}>
            <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />

            {routes && Object.entries(routes).map(([vehicleId, path], index) => (
                <React.Fragment key={vehicleId}>
                    <Polyline
                        positions={path}
                        pathOptions={{ color: colors[index % colors.length], weight: 5 }}
                    >
                        <Popup>Vehicle {vehicleId}</Popup>
                    </Polyline>

                    {/* Mark start and end points */}
                    {path.length > 0 && (
                        <>
                            <Marker position={path[0]}>
                                <Popup>Start Vehicle {vehicleId}</Popup>
                            </Marker>
                            <Marker position={path[path.length - 1]}>
                                <Popup>End Vehicle {vehicleId}</Popup>
                            </Marker>
                        </>
                    )}
                </React.Fragment>
            ))}

            <MapUpdater routes={routes} />
        </MapContainer>
    );
};

export default RouteMap;
