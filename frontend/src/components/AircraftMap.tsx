import "leaflet/dist/leaflet.css";
import { useEffect, useRef, useState } from "react";
import { MapContainer, TileLayer, useMapEvents } from "react-leaflet";
import L from "leaflet";
import MarkersCanvas from "../lib/leaflet-markers-canvas.js";
import { getLatestBatch } from "../services/api";


type Aircraft = {
    icao24: string;
    latitude: number;
    longitude: number;
    heading: number;
};

function AircraftFetcher({ setAircraft }: { setAircraft: (a: Aircraft[]) => void }) {
    const map = useMapEvents({

        // Fetch visible states after map is moved
        moveend: async () => {
            const bounds = map.getBounds();
            const ne = bounds.getNorthEast();
            const sw = bounds.getSouthWest();

            try {
                const data = await getLatestBatch({
                    lat_min: sw.lat,
                    lat_max: ne.lat,
                    lon_min: sw.lng,
                    lon_max: ne.lng
                });
                setAircraft(data);
            } catch (err) {
                console.error(err)
            }
        },
    });

    // Fetch initial data on component mount
    useEffect(() => {
        map.fire('moveend');
    }, [map]);

    return null;
}


function CanvasMarkersLayer({ aircraft }: { aircraft: Aircraft[] }) {
    // Get map instance and create reference for marker canvas
    const map = useMapEvents({});
    const markersCanvasRef = useRef<any>(null);

    // Initialize and cleanup of canvas layer
    useEffect(() => {

        // Initialize canvas marker layer
        if (!map) return;
        const canvasLayer = new MarkersCanvas();
        canvasLayer.addTo(map);
        markersCanvasRef.current = canvasLayer;

        // Cleanup function
        return () => {
            if (map && canvasLayer) {
                map.removeLayer(canvasLayer);
            }
        };
    }, [map]);

    // Update markers when aircraft data changes
    useEffect(() => {
        // Clear existing markers
        const layer = markersCanvasRef.current;
        if (!layer) return;
        layer.clear();
        if (!aircraft || aircraft.length === 0) return;

        // Create marker for each aircraft (rotated with heading)
        const markers = aircraft.map(a => {
            const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24"><path fill="#1E90FF" d="M21 15.984l-8.016-4.5V3.516a1.5 1.5 0 0 0-3 0v7.969L2.016 15.984V18l8.016-2.484V21l-2.016 1.5V24l3.516-0.984L15 22.5v-1.5L13.031 21v-5.484L21 18v-2.016z"/></svg>`;
            const iconUrl = `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`;
            const icon = L.icon({
                iconUrl,
                iconSize: [24, 24],
                iconAnchor: [12, 12],
                rotationAngle: a.heading,
            });
            return L.marker(
                [a.latitude, a.longitude],
                { icon }
            ).bindPopup(`ICAO24: ${a.icao24}<br>Heading: ${a.heading.toFixed(0)}°`);
        });

        // Add markers to canvas layer
        layer.addMarkers(markers);
    }, [aircraft]);

    return null;
}

export function AircraftMap() {
    const [aircraft, setAircraft] = useState<Aircraft[]>([]);

    return (
        <MapContainer style={{ height: "100vh", width: "100%"}} center={[52, 4]} zoom={6}>
            <TileLayer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            />
            <AircraftFetcher setAircraft={setAircraft} />
            <CanvasMarkersLayer aircraft={aircraft} />
        </MapContainer>
    );
}
