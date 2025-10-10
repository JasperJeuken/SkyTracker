import { useEffect, useRef } from "react";
import { useMapEvents } from "react-leaflet";
import L from "leaflet";
import MarkersCanvas from "@/lib/leaflet-markers-canvas";
// import { useAircraftMap } from "./AircraftMapProvider.js";
import { type SimpleMapState } from "@/types/api.js";
import { useMapStore } from "@/store/mapStore";
import { getAircraftSVG } from "@/components/visuals/aircraftMap/AircraftMarkers";


declare module "leaflet" {
    interface IconOptions {
        rotationAngle: number | null;
    }
}


export function AircraftMarkerLayer({ aircraft, pane, selectedAircraft }: { aircraft: SimpleMapState[], pane: string, selectedAircraft: string | null }) {
    // Get map instance and create reference for marker canvas
    const setSelectedAircraft = useMapStore((state) => state.setSelectedAircraft);
    const setSidebarOpen = useMapStore((state) => state.setSidebarOpen);
    const markerClickedRef = useRef(false);
    const map = useMapEvents({
        click: () => {
            if (!markerClickedRef.current) {
                setSelectedAircraft(null);
                setSidebarOpen(false);
            }
            markerClickedRef.current = false;
        },
    });
    const markersCanvasRef = useRef<any>(null);

    // Initialize and cleanup of canvas layer
    useEffect(() => {

        // Initialize canvas marker layer
        if (!map) return;
        const canvasLayer = new MarkersCanvas({ pane: pane });
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
            const color = a.callsign == selectedAircraft ? "#0757a7" : "#1E90FF";
            const svg = getAircraftSVG(a.model ?? "", color);
            const iconUrl = `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`;
            const icon = L.icon({
                iconUrl,
                iconSize: [24, 24],
                iconAnchor: [12, 12],
                rotationAngle: a.heading,
                pane: pane
            });

            const marker = L.marker(
                a.position,
                { icon: icon, title: a.callsign },
            ).on('click', (evt) => {
                markerClickedRef.current = true;
                setSelectedAircraft(evt.target.options.title);
                setSidebarOpen(true);
            });

            // Bind popup to hover
            marker.bindPopup(`<div class="px-3 py-2 rounded-lg shadow-md bg-white dark:bg-gray-800 text-sm text-gray-900 dark:text-gray-100">
                    ${a.callsign}
                </div>`);
            marker.on('mouseover', function () {
                marker.openPopup();
            });
            marker.on('mouseout', function () {
                marker.closePopup();
            });

            return marker;
        });

        // Add markers to canvas layer
        layer.addMarkers(markers);
    }, [aircraft, selectedAircraft]);

    return null;
}
