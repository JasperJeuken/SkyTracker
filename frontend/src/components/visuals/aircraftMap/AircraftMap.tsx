import "leaflet/dist/leaflet.css";
import { useEffect, useState, useRef } from "react";
import { MapContainer, TileLayer, useMap, Pane } from "react-leaflet";
import L, { type LatLngExpression } from "leaflet";
import { getAreaStates } from "@/services/api/state.js";
import { AircraftMarkerLayer } from "@/components/visuals/aircraftMap/AircraftMarkerLayer.js";
import { type SimpleMapState } from "@/types/api.js";
import { AircraftTrackLayer } from "@/components/visuals/aircraftMap/AircraftTrackLayer.js"
import { useMapStore } from "@/store/mapStore.js";
import { useTheme } from "next-themes";
import { AircraftMapSettings } from "@/components/visuals/aircraftMap/AircraftMapSettings.js";



const MAP_TILES = {
    OpenStreetMap: {
        light: "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
        dark: "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
    },
    Default: {
        light: "https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png",
        dark: "https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png",
    },
    Satellite: {
        light: "https://tiles.stadiamaps.com/tiles/alidade_satellite/{z}/{x}/{y}{r}.jpg",
        dark: "https://tiles.stadiamaps.com/tiles/alidade_satellite/{z}/{x}/{y}{r}.jpg",
    }
}

const TILE_ATTRIBUTIONS = {
    OpenStreetMap: {
        light: '&copy; <a href="https://openmaptiles.org/" target="_blank">OpenMapTiles</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        dark: '&copy; <a href="https://openmaptiles.org/" target="_blank">OpenMapTiles</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    },
    Default: {
        light: '&copy; <a href="https://www.stadiamaps.com/" target="_blank">Stadia Maps</a> &copy; <a href="https://openmaptiles.org/" target="_blank">OpenMapTiles</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        dark: '&copy; <a href="https://www.stadiamaps.com/" target="_blank">Stadia Maps</a> &copy; <a href="https://openmaptiles.org/" target="_blank">OpenMapTiles</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    },
    Satellite: {
        light: '&copy; CNES, Distribution Airbus DS, © Airbus DS, © PlanetObserver (Contains Copernicus Data) | &copy; <a href="https://www.stadiamaps.com/" target="_blank">Stadia Maps</a> &copy; <a href="https://openmaptiles.org/" target="_blank">OpenMapTiles</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        dark: '&copy; CNES, Distribution Airbus DS, © Airbus DS, © PlanetObserver (Contains Copernicus Data) | &copy; <a href="https://www.stadiamaps.com/" target="_blank">Stadia Maps</a> &copy; <a href="https://openmaptiles.org/" target="_blank">OpenMapTiles</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }
}

// Aircraft state fetch helper
function MapStateFetcher({ setAircraft }: { setAircraft: (a: SimpleMapState[]) => void }) {
    const map = useMap();
    const initialFetchDone = useRef(false);

    useEffect(() => {
        if (!map) return;
        
        const fetchAircraft = async () => {
            const bounds = map.getBounds();
            const ne = bounds.getNorthEast();
            const sw = bounds.getSouthWest();

            try {
                const data = await getAreaStates({
                    south: sw.lat,
                    north: ne.lat,
                    west: sw.lng,
                    east: ne.lng
                });
                setAircraft(data);
            } catch (err) {
                console.error(err)
            }
        };

        if (!initialFetchDone.current) {
            initialFetchDone.current = true;
            fetchAircraft();
        }

        map.on("moveend", fetchAircraft);
        const interval = setInterval(fetchAircraft, 10000);
        
        return () => {
            map.off("moveend", fetchAircraft);
            clearInterval(interval);
        };
    }, [map, setAircraft]);

    return null;
}

// Aircraft map state saver
function MapViewSaver() {
    const map = useMap();
    useEffect(() => {
        const saveView = () => {
            const center = map.getCenter();
            const zoom = map.getZoom();
            localStorage.setItem('mapView', JSON.stringify({
                center: [center.lat, center.lng],
                zoom
            }));
        };
        map.on('moveend', saveView);
        map.on('zoomend', saveView);
        return () => {
            map.off('moveend', saveView);
            map.off('zoomend', saveView);
        };
    }, [map]);
    return null;
}

export function AircraftMap() {
    // Get variables
    const mapStyle = useMapStore((state) => state.mapStyle);
    const selectedAircraft = useMapStore((state) => state.selectedAircraft);
    const [aircraft, setAircraft] = useState<SimpleMapState[]>([]);
    const { resolvedTheme } = useTheme();
    const currentTheme = (resolvedTheme === undefined ? "dark" : resolvedTheme) as "light" | "dark";
    const tileLayerRef = useRef<L.TileLayer | null>(null);
    
    // Restore center/zoom from local storage
    const defaultCenter = [52, 4];
    const defaultZoom = 6;
    const [initialView] = useState(() => {
        const saved = localStorage.getItem('mapView');
        if (saved) {
            try {
                const { center, zoom } = JSON.parse(saved);
                if (Array.isArray(center) && typeof zoom === "number") {
                    return { center, zoom };
                }
            } catch {}
        }
        return { center: defaultCenter, zoom: defaultZoom };
    });

    return (
        <div className="absolute inset-0 z-0">
            <AircraftMapSettings />
            <MapContainer className="h-full w-full" center={initialView.center as LatLngExpression} zoom={initialView.zoom} minZoom={3} zoomControl={false}>
                <TileLayer
                    ref={tileLayerRef}
                    url={MAP_TILES[mapStyle][currentTheme]}
                    attribution={TILE_ATTRIBUTIONS[mapStyle][currentTheme]}
                    key={`${mapStyle}-${currentTheme}`}
                />
                <MapStateFetcher setAircraft={setAircraft} />
                <MapViewSaver />
                <Pane name="aircraft-track" style={{ zIndex: 500 }}>
                    <AircraftTrackLayer callsign={selectedAircraft} pane="aircraft-track" />
                </Pane>
                <Pane name="aircraft-markers" style={{ zIndex: 900 }}>
                    <AircraftMarkerLayer aircraft={aircraft} pane="aircraft-markers" selectedAircraft={selectedAircraft} />
                </Pane>
            </MapContainer>
        </div>
    );
}
