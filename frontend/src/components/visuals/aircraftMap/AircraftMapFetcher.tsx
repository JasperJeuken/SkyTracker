import { useRef, useEffect } from "react";
import { type MapState } from "@/types/api";
import { useMap } from "react-leaflet";
import { useMapStore } from "@/store/mapStore";


export function AircraftMapFetcher({ setAircraftStates }: { setAircraftStates: (a: MapState[]) => void }) {
    const map = useMap();
    const workerRef = useRef<Worker | null>(null);
    const selected = useMapStore((state) => state.selected);
    const prependHistoryPoint = useMapStore((state) => state.prependHistoryPoint);

    useEffect(() => {
        if (!map) return;
        if (!workerRef.current) {
            workerRef.current = new Worker(new URL('@/workers/aircraftMapWorker.js', import.meta.url), { type: "module" });
        }
        const worker = workerRef.current;

        const fetchAircraft = () => {
            const bounds = map.getBounds();
            worker.postMessage({
                bounds: {
                    south: bounds.getSouthWest().lat,
                    west: bounds.getSouthWest().lng,
                    north: bounds.getNorthEast().lat,
                    east: bounds.getNorthEast().lng,
                }
            });
        };

        // Setup handlers
        const handleMessage = (e: MessageEvent) => {
            const aircraftStates = e.data.data as MapState[];
            if (e.data.data) {
                setAircraftStates(aircraftStates);
                console.log(selected);
                if (selected) {
                    console.log("searching");
                    for (const state of aircraftStates) {
                        if (state.callsign === selected) {
                            console.log("prepending");
                            console.log(state);
                            prependHistoryPoint(state.callsign, state);
                            break;
                        }
                    }
                }
            };
            if (e.data.error) console.error(e.data.error);
        };
        worker.addEventListener('message', handleMessage);
        fetchAircraft();
        map.on('moveend', fetchAircraft);
        const interval = setInterval(fetchAircraft, 10000);

        // Remove handlers
        return () => {
            map.off('moveend', fetchAircraft);
            clearInterval(interval);
            worker.removeEventListener('message', handleMessage);
            worker.terminate();
            workerRef.current = null;
        };
    }, [map, setAircraftStates, selected]);

    return null;
}
