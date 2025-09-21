import "leaflet/dist/leaflet.css";
import { useEffect, useState, useContext, useRef } from "react";
import { MapContainer, TileLayer, useMap, Polyline } from "react-leaflet";
import L from "leaflet";
import { getLatestBatch, getAircraftTrack } from "../services/api";
import { CanvasMarkersLayer } from "./CanvasMarkersLayer.js";
import { ThemeContext } from "./layout/ThemeProvider.js";
import { useAircraftMap } from "./AircraftMapProvider.js";


type Aircraft = {
    icao24: string;
    latitude: number;
    longitude: number;
    heading: number;
};

const MAP_TILES = {
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
    Default: {
        light: '&copy; <a href="https://www.stadiamaps.com/" target="_blank">Stadia Maps</a> &copy; <a href="https://openmaptiles.org/" target="_blank">OpenMapTiles</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        dark: '&copy; <a href="https://www.stadiamaps.com/" target="_blank">Stadia Maps</a> &copy; <a href="https://openmaptiles.org/" target="_blank">OpenMapTiles</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    },
    Satellite: {
        light: '&copy; CNES, Distribution Airbus DS, © Airbus DS, © PlanetObserver (Contains Copernicus Data) | &copy; <a href="https://www.stadiamaps.com/" target="_blank">Stadia Maps</a> &copy; <a href="https://openmaptiles.org/" target="_blank">OpenMapTiles</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        dark: '&copy; CNES, Distribution Airbus DS, © Airbus DS, © PlanetObserver (Contains Copernicus Data) | &copy; <a href="https://www.stadiamaps.com/" target="_blank">Stadia Maps</a> &copy; <a href="https://openmaptiles.org/" target="_blank">OpenMapTiles</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }
}


function AircraftTrackLayer({ icao24 }: { icao24: string | null }) {
    const [track, setTrack] = useState<Aircraft[]>([]);

    useEffect(() => {
        if (!icao24) {
            setTrack([]);
            return;
        }
        getAircraftTrack(icao24)
            .then(setTrack)
            .catch(() => setTrack([]));
    }, [icao24]);

    if (!track || track.length < 2) return null;

    const positions = track.map(a => [a.latitude, a.longitude] as [number, number]);
    return (
        <Polyline positions={positions} pathOptions={{ color: "red", weight: 3}} />
    );
}


// Aircraft state fetch helper
function AircraftFetcher({ setAircraft }: { setAircraft: (a: Aircraft[]) => void }) {
    const map = useMap();
    const initialFetchDone = useRef(false);

    useEffect(() => {
        if (!map) return;
        
        const fetchAircraft = async () => {
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
        };

        if (!initialFetchDone.current) {
            initialFetchDone.current = true;
            fetchAircraft();
        }

        map.on("moveend", fetchAircraft);
        
        return () => {
            map.off("moveend", fetchAircraft)
        };
    }, [map, setAircraft]);

    return null;
}

export function AircraftMap() {
    const { mapStyle, selectedAircraft } = useAircraftMap();
    const [aircraft, setAircraft] = useState<Aircraft[]>([]);
    const { theme } = useContext(ThemeContext);
    const tileLayerRef = useRef<L.TileLayer | null>(null);

    return (
        <MapContainer className="h-full w-full z-0" center={[52, 4]} zoom={6}>
            <TileLayer
                ref={tileLayerRef}
                url={MAP_TILES[mapStyle][theme]}
                attribution={TILE_ATTRIBUTIONS[mapStyle][theme]}
                key={`${mapStyle}-${theme}`}
            />
            <AircraftFetcher setAircraft={setAircraft} />
            <CanvasMarkersLayer aircraft={aircraft} />
            <AircraftTrackLayer icao24={selectedAircraft} />
        </MapContainer>
    );
}
