import { useRef, useEffect } from "react";
import { type MapState } from "@/types/api";
import { useMap } from "react-leaflet";
import { useMapStore } from "@/store/mapStore";


export function AircraftMapFetcher({ setAircraftStates }: { setAircraftStates: (a: MapState[]) => void }) {
    const map = useMap();
    const workerRef = useRef<Worker | null>(null);
    const selected = useMapStore((state) => state.selected);
    const setLastUpdate = useMapStore((state) => state.setLastUpdate);
    const appendHistoryPoint = useMapStore((state) => state.appendHistoryPoint);

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
                    south: bounds.getSouthWest().lat - 1,
                    west: bounds.getSouthWest().lng - 1,
                    north: bounds.getNorthEast().lat + 1,
                    east: bounds.getNorthEast().lng - 1,
                }
            });
        };

        // Setup handlers
        const handleMessage = (e: MessageEvent) => {
            const aircraftStates = e.data.data as MapState[];
            if (aircraftStates) {
                setLastUpdate(new Date(aircraftStates[0].time).valueOf());
                setAircraftStates(aircraftStates);
                if (selected) {
                    for (const state of aircraftStates) {
                        if (state.callsign === selected) {
                            appendHistoryPoint(state.callsign, state);
                            break;
                        }
                    }
                }
            } else {
                setAircraftStates([]);
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
