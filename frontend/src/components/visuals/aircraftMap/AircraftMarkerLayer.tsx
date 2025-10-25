import { useEffect, useRef } from "react";
import { useMapEvents, useMap } from "react-leaflet";
import L from "leaflet";
import MarkersCanvas from "@/lib/leaflet-markers-canvas";
import { type MapState } from "@/types/api.js";
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

function positionOffset({ position, altitude, map }: { position: [number, number], altitude: number | null, map: L.Map }): [number, number] {
    let [lat, lon] = position;
    const point = map.latLngToContainerPoint(L.latLng(lat, lon));
    const scale =  1 + 2 * (altitude ?? 0) / 36000;
    const offsetPoint = L.point(point.x + 3 * scale, point.y + 3 * scale);
    const offsetLatLng = map.containerPointToLatLng(offsetPoint);
    const latDiff = offsetLatLng.lat - lat;
    const lonDiff = offsetLatLng.lng - lon;
    return [latDiff, lonDiff]
}

export function AircraftMarkerLayer({
    aircraft,
    selectedAircraft,
    pane, color,
    selectedColor = color,
    strokeColor = color,
    altitudeOffset = false,
    popup = false,
    selectable = false,
    animateMarkers = true
}: {
    aircraft: MapState[], 
    selectedAircraft: string | null, 
    pane: string, color: string,
    selectedColor?: string,
    strokeColor?: string, 
    altitudeOffset?: boolean, 
    popup?: boolean, 
    selectable?: boolean,
    animateMarkers?: boolean
}) {
    // Get map instance and create reference for marker canvas
    const setSelectedAircraft = useMapStore((state) => state.setSelected);
    const setSidebarOpen = useMapStore((state) => state.setSidebarOpen);
    const setSelectedPosition = useMapStore((state) => state.setSelectedPosition);
    const lastUpdate = useMapStore((state) => state.lastUpdate);
    const markerClickedRef = useRef(false);
    const layerRef = useRef<any>(null);
    const markersRef = useRef<Record<string, L.Marker>>({});
    const offsetRef = useRef<Record<string, [number, number]>>({});
    const aircraftRef = useRef<MapState[]>(aircraft);

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

        return () => { map.removeLayer(layer); };
    }, [map]);

    // Update markers when aircraft data changes
    useEffect(() => {

        // Clear existing markers
        const layer = layerRef.current;
        if (!layer) return;
        layer.clear();
        markersRef.current = {};
        offsetRef.current = {};
        aircraftRef.current = aircraft;
        if (!aircraft || aircraft.length === 0) return;

        // Create marker for each aircraft (rotated with heading)
        const markers = aircraft.map(a => {
            
            const currentColor = a.callsign == selectedAircraft ? selectedColor : color;
            const icon = createAircraftIcon({ color: currentColor, strokeColor: strokeColor, model: a.model, angle: a.heading ?? 0, pane: pane })

            let [lat, lon] = [a.position[0], a.position[1]];
            let offset: [number, number] = [0, 0];
            if (altitudeOffset) {
                offset = positionOffset({ position: a.position, altitude: a.altitude, map });
                offsetRef.current[a.callsign] = offset;
            } else if (a.callsign == selectedAircraft) {
                setSelectedPosition([lat, lon]);
            }
            const marker = L.marker([lat + offset[0], lon + offset[1]], { icon: icon, title: a.callsign });

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
            markersRef.current[a.callsign] = marker;
            return marker;
        });
        layer.addMarkers(markers);
    }, [aircraft, selectedAircraft]);

    // Animation
    useEffect(() => {
        if (!animateMarkers) return;
        if (!map) return;
        let frame: number | null = null;
        const R = 6371000;

        const animate = () => {
            const now = Date.now();
            const dt = (now - lastUpdate) / 1000;
            const layer = layerRef.current;
            if (!layer) return;

            const updateMarkers: L.Marker[] = [];

            for (const a of aircraftRef.current) {
                const marker = markersRef.current[a.callsign];
                const offset = offsetRef.current[a.callsign] ?? [0., 0.];
                if (!marker) continue;
                if (!a.velocity || !a.heading) continue;

                const distance = a.velocity * dt;
                const headingRad = (a.heading * Math.PI) / 180;
                const lat1 = (a.position[0] * Math.PI) / 180;
                const lon1 = (a.position[1] * Math.PI) / 180;
                const lat2 = Math.asin(Math.sin(lat1) * Math.cos(distance / R) + Math.cos(lat1) * Math.sin(distance / R) * Math.cos(headingRad));
                const lon2 = lon1 + Math.atan2(Math.sin(headingRad) * Math.sin(distance / R) * Math.cos(lat1), Math.cos(distance / R) - Math.sin(lat1) * Math.sin(lat2));
                const newLat = (lat2 * 180) / Math.PI + offset[0];
                const newLon = (lon2 * 180) / Math.PI + offset[1];
                if (a.callsign == selectedAircraft && offset[0] == 0 && offset[1] == 0) {
                    setSelectedPosition([newLat, newLon]);
                }

                marker.setLatLng([newLat, newLon]);
                updateMarkers.push(marker);
            }

            if (updateMarkers.length > 0) {
                layer.clear();
                layer.addMarkers(Object.values(markersRef.current));
            } 
            frame = requestAnimationFrame(animate);
        };

        const startAnimation = () => {
            if (frame == null) {
                frame = requestAnimationFrame(animate);
            }
        };
        const stopAnimation = () => {
            if (frame != null) {
                cancelAnimationFrame(frame);
                frame = null;
            }
        };
        const handleZoom = () => {
            if (map.getZoom() < 9) {
                stopAnimation();
            } else {
                startAnimation();
            }
        };

        handleZoom();
        map.on("zoomend", handleZoom);
        return () => {
            stopAnimation();
            map.off("zoomend", handleZoom);
        };
    }, [map, animateMarkers, lastUpdate, selectedAircraft])

    return null;
}
