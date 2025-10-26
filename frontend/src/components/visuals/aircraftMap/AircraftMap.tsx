import "leaflet/dist/leaflet.css";
import { useEffect, useState, useRef } from "react";
import { MapContainer, TileLayer, useMap, Pane } from "react-leaflet";
import L, { type LatLngExpression } from "leaflet";
import { AircraftMarkerLayer } from "@/components/visuals/aircraftMap/AircraftMarkerLayer.js";
import { AircraftTrackLayer } from "@/components/visuals/aircraftMap/AircraftTrackLayer.js"
import { useMapStore } from "@/store/mapStore.js";
import { useTheme } from "next-themes";
import { AircraftMapSettings } from "@/components/visuals/aircraftMap/AircraftMapSettings.js";
import { AircraftMapFetcher } from "@/components/visuals/aircraftMap/AircraftMapFetcher"



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

function MapRefSetter() {
    const setMapRef = useMapStore((state) => state.setMapRef);
    const map = useMap();
    useEffect(() => {
        setMapRef(map);
    }, [map, setMapRef]);
    return null;
}

export function AircraftMap() {
    // Get variables
    const mapStyle = useMapStore((state) => state.mapStyle);
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
            <MapContainer className="h-full w-full" center={initialView.center as LatLngExpression} zoom={initialView.zoom} minZoom={3.5} zoomControl={false}>
                <AircraftMapFetcher />
                <MapViewSaver />
                <MapRefSetter />
                <TileLayer
                    ref={tileLayerRef}
                    url={MAP_TILES[mapStyle][currentTheme]}
                    attribution={TILE_ATTRIBUTIONS[mapStyle][currentTheme]}
                    key={`${mapStyle}-${currentTheme}`}
                />
                <Pane name="aircraft-track" style={{ zIndex: 500 }}>
                    <AircraftTrackLayer pane="aircraft-track" />
                </Pane>
                <Pane name="aircraft-shadows" style={{ zIndex: 700 }}>
                    <AircraftMarkerLayer pane="aircraft-shadows" color="#2d2e3040" altitudeOffset />
                </Pane>
                <Pane name="aircraft-markers" style={{ zIndex: 900 }}>
                    <AircraftMarkerLayer pane="aircraft-markers" color="#1E90FF" selectedColor="#0757a7" strokeColor="#081623ff" selectable popup />
                </Pane>
            </MapContainer>
        </div>
    );
}
