import { useRef, useEffect } from "react";
import { type MapState, type State } from "@/types/api";
import { useMap } from "react-leaflet";
import { useMapStore } from "@/store/mapStore";
import { getHistoryStates, getLatestState } from "@/services/api/state";
import { getAircraft, getAircraftPhotos } from "@/services/api/aircraft";
import { getAirline } from "@/services/api/airline";
import { getAirport } from "@/services/api/airport";


function stateToMapState(state: State): MapState {
    return {
        time: state.time,
        callsign: state.flight.icao,
        position: state.geography.position,
        heading: state.geography.heading,
        model: state.aircraft.icao,
        altitude: state.geography.baro_altitude,
        velocity: state.geography.speed_horizontal,
    } as MapState;
}


export function AircraftMapFetcher({
    areaPadding = {south: 1, west: 1, north: 1, east: 1},
    refreshRate = 10000,
    historyDuration = "10h",
    historyLimit = 0,
    photosLimit = 5,
}: {
    areaPadding?: {south: number, west: number, north: number, east: number},
    refreshRate?: number,
    historyDuration?: string,
    historyLimit?: number,
    photosLimit?: number,
}) {
    const map = useMap();
    const mapWorkerRef = useRef<Worker | null>(null);
    const selected = useMapStore((state) => state.selected);
    const setMapStates = useMapStore((state) => state.setMapStates);
    const setLastHistoryUpdateString = useMapStore((state) => state.setLastHistoryUpdateString);
    const setLastMapUpdateString = useMapStore((state) => state.setLastMapUpdateString);
    const setHistory = useMapStore((state) => state.setHistory);
    const prependHistory = useMapStore((state) => state.prependHistory);
    const setDetailState = useMapStore((state) => state.setDetailState);
    const setDetailAircraft = useMapStore((state) => state.setDetailAircraft);
    const setDetailAirline = useMapStore((state) => state.setDetailAirline);
    const setDetailPhotos = useMapStore((state) => state.setDetailPhotos);
    const setDetailArrival = useMapStore((state) => state.setDetailArrival);
    const setDetailDeparture = useMapStore((state) => state.setDetailDeparture);
    const setDetailLoading = useMapStore((state) => state.setDetailLoading);
    const setDetailError = useMapStore((state) => state.setDetailError);
    const resetSelected = useMapStore((state) => state.resetSelected);

    // Update map states when map moves
    useEffect(() => {
        if (!map) return;
        if (!mapWorkerRef.current) {
            mapWorkerRef.current = new Worker(new URL('@/workers/aircraftMapWorker.js', import.meta.url), { type: "module" });
        }

        // Add worker message
        const startFetch = () => {
            const bounds = map.getBounds();
            const sw = bounds.getSouthWest();
            const ne = bounds.getNorthEast();
            mapWorkerRef.current!.postMessage({
                bounds: {
                    south: sw.lat - areaPadding.south,
                    west: sw.lng - areaPadding.west,
                    north: ne.lat + areaPadding.north,
                    east: ne.lng + areaPadding.east,
                }
            });
        };

        // Handle worker message
        const handleFetch = (e: MessageEvent) => {
            const data = e.data;
            if (data.error) {
                return;
            }

            const aircraftStates = data.data as MapState[];
            if (aircraftStates) {
                setLastMapUpdateString(aircraftStates[0].time);
                setMapStates(aircraftStates);
            } else {
                setMapStates([]);
            }
        };

        // Attach handlerss
        mapWorkerRef.current!.addEventListener("message", handleFetch);
        map.on("moveend", startFetch);
        const interval = setInterval(startFetch, refreshRate);
        startFetch();

        // Remove handlers
        return () => {
            map.off("moveend", startFetch);
            clearInterval(interval);
            if (mapWorkerRef.current) {
                mapWorkerRef.current.removeEventListener("message", handleFetch)
                mapWorkerRef.current.terminate();
                mapWorkerRef.current = null;
            }
        }
    }, [map]);

    // Update data when selected aircraft changes
    useEffect(() => {
        resetSelected();
        if (!selected) return;
        let isCancelled = false;
        setDetailLoading();

        const fetchInitial = async () => {
            try {
                // Get state history
                const [history, latestState] = await Promise.all([
                    getHistoryStates(selected, { duration: historyDuration, limit: historyLimit }),
                    getLatestState(selected),
                ]);
                if (isCancelled) return;

                // Update history
                setLastHistoryUpdateString(history[0].time);
                setHistory(history);
                setDetailState({ status: "success", data: latestState });

                // Get aircraft details
                const aircraftPromise = latestState.aircraft.registration ? (
                    (async () => {
                        try {
                            const data = await getAircraft(latestState.aircraft.registration!);
                            if (isCancelled) return;
                            setDetailAircraft({ status: "success", data });
                        } catch {
                            if (isCancelled) return;
                            setDetailAircraft({ status: "error", error: "Aircraft not found" });
                        }
                    })()
                ) : (
                    (async () => {
                        if (isCancelled) return;
                        setDetailAircraft({ status: "error", error: "Aircraft registration unknown" });
                    })()
                );

                // Get airline details
                const airlinePromise = latestState.airline.icao ? (
                    (async () => {
                        try {
                            const data = await getAirline(latestState.airline.icao!);
                            if (isCancelled) return;
                            setDetailAirline({ status: "success", data });
                        } catch {
                            if (isCancelled) return;
                            setDetailAirline({ status: "error", error: "Airline not found" })
                        }
                    })()
                ) : (
                    (async () => {
                        if (isCancelled) return;
                        setDetailAirline({ status: "error", error: "Airline ICAO code unknown" });
                    })()
                );

                // Get arrival airport details
                const arrivalPromise = latestState.airport.arrival_iata ? (
                    (async () => {
                        try {
                            const data = await getAirport(latestState.airport.arrival_iata!);
                            if (isCancelled) return;
                            setDetailArrival({ status: "success", data });
                        } catch {
                            if (isCancelled) return;
                            setDetailArrival({ status: "error", error: "Arrival airport not found" });
                        }
                    })()
                ) : (
                    (async () => {
                        if (isCancelled) return;
                        setDetailArrival({ status: "error", error: "Arrival airport IATA code unknown" });
                    })()
                );

                // Get departure airport details
                const departurePromise = latestState.airport.departure_iata ? (
                    (async () => {
                        try {
                            const data = await getAirport(latestState.airport.departure_iata!);
                            if (isCancelled) return;
                            setDetailDeparture({ status: "success", data });
                        } catch {
                            if (isCancelled) return;
                            setDetailDeparture({ status: "error", error: "Departure airport not found" });
                        }
                    })()
                ) : (
                    (async () => {
                        if (isCancelled) return;
                        setDetailDeparture({ status: "error", error: "Departure airport IATA code unknown" });
                    })()
                );

                // Get aircraft photos
                const photosPromise = latestState.aircraft.registration ? (
                    (async () => {
                        try {
                            const data = await getAircraftPhotos(latestState.aircraft.registration!, { limit: photosLimit });
                            if (isCancelled) return;
                            setDetailPhotos({ status: "success", data });
                        } catch {
                            if (isCancelled) return;
                            setDetailPhotos({ status: "error", error: "Aircraft photos not found" });
                        }
                    })()
                ) : (
                    (async () => {
                        if (isCancelled) return;
                        setDetailPhotos({ status: "error", error: "Aircraft registration unknown" });
                    })()
                );

                await Promise.all([aircraftPromise, airlinePromise, arrivalPromise, departurePromise, photosPromise]);
            } catch (err) {
                if (isCancelled) return;
                setDetailError("Could not get history data");
            }
        }
        fetchInitial();

        // Periodically fetch latest state
        const fetchLatestState = async () => {
            try {
                const latestState = await getLatestState(selected);
                const mapState = stateToMapState(latestState);
                if (isCancelled) return;
                setLastHistoryUpdateString(latestState.time);
                prependHistory(mapState);
                setDetailState({ status: "success", data: latestState });
            } catch (err) {
                if (isCancelled) return;
            }
        };
        const interval = setInterval(fetchLatestState, refreshRate);

        // Cleanup
        return () => {
            isCancelled = true;
            clearInterval(interval);
        }
    }, [selected]);

    return null;
}
