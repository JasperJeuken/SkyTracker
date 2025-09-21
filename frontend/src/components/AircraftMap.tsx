// import { MapContainer, TileLayer, Marker, useMapEvents } from "react-leaflet";
// import "leaflet/dist/leaflet.css";
import { useEffect, useRef, useState, useCallback } from "react";
import Map from "react-map-gl";
import { DeckGL } from "@deck.gl/react";
import { ScatterplotLayer } from "@deck.gl/layers";
import 'mapbox-gl/dist/mapbox-gl.css';
import { getLatestBatch } from "../services/api";

type Aircraft = {
    icao24: string;
    latitude: number;
    longitude: number;
    heading: number;
};


export function AircraftMap() {
    const [aircraft, setAircraft] = useState<Aircraft[]>([]);
    const mapRef = useRef(null);
    const [viewState, setViewState] = useState({
        longitude: 4,
        latitude: 52,
        zoom: 6,
        pitch: 0,
        bearing: 0,
    });

    const fetchBatch = useCallback(async () => {
        if (!mapRef.current) {
            return null;
        }
        const mapInstance = mapRef.current.getMap();
        const bounds = mapInstance.getBounds();
        const ne = bounds.getNorthEast();
        const sw = bounds.getSouthWest();

        try {
            const data = await getLatestBatch({
                lat_min: sw.lat,
                lat_max: ne.lat,
                lon_min: sw.lng,
                lon_max: ne.lng,
            });
            setAircraft(data);
        } catch (err) {
            console.error(err);
        }
    }, []);

    useEffect(() => {
        fetchBatch();
    }, [fetchBatch]);

    const layers = [
        new ScatterplotLayer({
            id: "aircraft-layer",
            data: aircraft,
            pickable: true,
            getPosition: (d: Aircraft) => [d.longitude, d.latitude],
            getFillColor: [255, 0, 0],
            getRadius: 20000,
            radiusMinPixels: 2,
            radiusMaxPixels: 10,
        }),
    ];

    return (
        <DeckGL
            viewState={viewState}
            controller={true}
            layers={layers}
            onViewStateChange={({ viewState }) => {setViewState(viewState)}}
            style={{ width: "100vw", height: "100vh" }}
        >
            {/* TODO: fix Map */}
            <Map
                ref={mapRef}
                reuseMaps
                mapLib={import("maplibre-gl")}
                mapStyle="https://demotiles.maplibre.org/style.json"
                onMoveEnd={fetchBatch}
            />
        </DeckGL>
    );
}


// export function AircraftMap() {
//     const [aircraft, setAircraft] = useState<Aircraft[]>([]);

//     return (
//         <MapContainer style={{ height: "100vh", width: "100%"}} center={[52, 3]} zoom={10}>
//             <TileLayer
//                 url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
//                 attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
//             />
//             <AircraftFetcher setAircraft={setAircraft} />
//             {aircraft.map((a) => (
//                 <Marker key={a.icao24} position={[a.latitude, a.longitude]}></Marker>
//             ))}
//         </MapContainer>
//     );
// }
