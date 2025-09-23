import { useEffect, useRef } from "react";
import { useMapEvents } from "react-leaflet";
import L from "leaflet";
import MarkersCanvas from "../lib/leaflet-markers-canvas";
import { useAircraftMap } from "./AircraftMapProvider.js";


type Aircraft = {
    icao24: string;
    latitude: number;
    longitude: number;
    heading: number;
};

declare module "leaflet" {
    interface IconOptions {
        rotationAngle?: number;
    }
}


export function CanvasMarkersLayer({ aircraft }: { aircraft: Aircraft[] }) {
    // Get map instance and create reference for marker canvas
    const { setSelectedAircraft, setSidebarOpen } = useAircraftMap();
    const markerClickedRef = useRef(false);
    const map = useMapEvents({
        click: () => {
            if (!markerClickedRef.current) {
                setSelectedAircraft(null);
            }
            markerClickedRef.current = false;
        },
    });
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

            const marker = L.marker(
                [a.latitude, a.longitude],
                { icon: icon, title: a.icao24, zIndexOffset: 100 },
            ).on('click', (evt) => {
                markerClickedRef.current = true;
                setSelectedAircraft(evt.target.options.title);
                setSidebarOpen(true);
            });

            // Bind popup to hover
            // marker.bindPopup(`ICAO24: ${a.icao24}`);
            // marker.on('mouseover', function () {
            //     marker.openPopup();
            // });
            // marker.on('mouseout', function () {
            //     marker.closePopup();
            // });

            return marker;
        });

        // Add markers to canvas layer
        layer.addMarkers(markers);
    }, [aircraft]);

    return null;
}