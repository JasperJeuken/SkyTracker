import { useEffect, useRef } from "react";
import { useMapEvents, useMap } from "react-leaflet";
import L from "leaflet";
import MarkersCanvas from "@/lib/leaflet-markers-canvas";
import { type SimpleMapState } from "@/types/api.js";
import { useMapStore } from "@/store/mapStore";
import { getAircraftSVG } from "@/components/visuals/aircraftMap/AircraftMarkers";


declare module "leaflet" {
    interface IconOptions {
        rotationAngle: number | null;
    }
}


function createAircraftIcon({color, strokeColor, model, angle, pane}: {color: string, strokeColor: string, model: string | null, angle: number, pane: string}) {
    const svg = getAircraftSVG(model ?? "", color, strokeColor);
    const iconUrl = `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`;
    const icon = L.icon({
        iconUrl: iconUrl,
        iconSize: [24, 24],
        iconAnchor: [12, 12],
        rotationAngle: angle,
        pane: pane
    });
    return icon;
}

export function AircraftMarkerLayer({
    aircraft,
    selectedAircraft,
    pane, color,
    selectedColor = color,
    strokeColor = color,
    altitudeOffset = false,
    popup = false,
    selectable = false
}: {
    aircraft: SimpleMapState[], 
    selectedAircraft: string | null, 
    pane: string, color: string,
    selectedColor?: string,
    strokeColor?: string, 
    altitudeOffset?: boolean, 
    popup?: boolean, 
    selectable?: boolean 
}) {
    // Get map instance and create reference for marker canvas
    const setSelectedAircraft = useMapStore((state) => state.setSelectedAircraft);
    const setSidebarOpen = useMapStore((state) => state.setSidebarOpen);
    const markerClickedRef = useRef(false);
    const layerRef = useRef<any>(null);
    
    // Get a map reference (attach click event if selectable)
    let map = null;
    if (selectable) {
        map = useMapEvents({
            click: () => {
                if (!markerClickedRef.current) {
                    setSelectedAircraft(null);
                    setSidebarOpen(false);
                }
                markerClickedRef.current = false;
            },
        });
    } else {
        map = useMap();
    }

    // Initialize canvas layer
    useEffect(() => {
        if (!map) return;
        const layer = new MarkersCanvas({ pane: pane });
        layer.addTo(map);
        layerRef.current = layer;

        return () => {
            if (map && layer) {
                map.removeLayer(layer);
            }
        };
    }, [map]);

    // Update markers when aircraft data changes
    useEffect(() => {

        // Clear existing markers
        const layer = layerRef.current;
        if (!layer) return;
        layer.clear();
        if (!aircraft || aircraft.length === 0) return;

        // Create marker for each aircraft (rotated with heading)
        const markers = aircraft.map(a => {
            
            const currentColor = a.callsign == selectedAircraft ? selectedColor : color;
            const icon = createAircraftIcon({ color: currentColor, strokeColor: strokeColor, model: a.model, angle: a.heading ?? 0, pane: pane })

            let [lat, lon] = [a.position[0], a.position[1]];
            if (altitudeOffset) {
                const point = map.latLngToContainerPoint(L.latLng(a.position[0], a.position[1]));
                const scale =  1 + 2 * (a.altitude ?? 0) / 36000;
                const offsetPoint = L.point(point.x + 3 * scale, point.y + 3 * scale);
                const offsetLatLng = map.containerPointToLatLng(offsetPoint);
                lat = offsetLatLng.lat;
                lon = offsetLatLng.lng;
            }
            const marker = L.marker(
                [lat, lon], { icon: icon, title: a.callsign }
            );
            

            if (selectable) {
                marker.on('click', (evt) => {
                    markerClickedRef.current = true;
                    setSelectedAircraft(evt.target.options.title);
                    setSidebarOpen(true);
                });
            }
            if (popup) {
                marker.bindPopup(`<div class="px-3 py-2 rounded-lg shadow-md bg-white dark:bg-gray-800 text-sm text-gray-900 dark:text-gray-100" style="user-select: none; pointer-events: none;">
                        ${a.callsign}
                    </div>`, { autoPan: false }
                );
                marker.on('mouseover', () => marker.openPopup());
                marker.on('mouseout', () => marker.closePopup());
            }
            return marker;
        });
        layer.addMarkers(markers);
    }, [aircraft, selectedAircraft]);
    return null;
}
