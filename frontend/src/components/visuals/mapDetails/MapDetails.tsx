import { getLatestState } from "@/services/api/state";
import { getAirport } from "@/services/api/airport";
import { getAirline } from "@/services/api/airline";
import { getAircraft, getAircraftPhotos } from "@/services/api/aircraft";
import { useMapStore } from "@/store/mapStore";
import { useEffect } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { MapDetailsAirport } from "./MapDetailsAirport";
import { MapDetailsImages } from "./MapDetailsImages";
import { MapDetailsHeader } from "./MapDetailsHeader";
import { MapDetailsPosition } from "./MapDetailsPosition";


function useMapDetails(callsign: string | null) {
    const details = useMapStore((state) => callsign ? state.details[callsign] : null);
    const setDetails = useMapStore((state) => state.setDetails);
    const setDetailAircraft = useMapStore((state) => state.setDetailAircraft);
    const setDetailAirline = useMapStore((state) => state.setDetailAirline);
    const setDetailArrival = useMapStore((state) => state.setDetailArrival);
    const setDetailDeparture = useMapStore((state) => state.setDetailDeparture);
    const setDetailPhotos = useMapStore((state) => state.setDetailPhotos);
    const setDetailState = useMapStore((state) => state.setDetailState);

    useEffect(() => {
        if (!callsign) return;
        setDetails(callsign, {
            aircraft: { status: "loading" },
            airline: { status: "loading" },
            airport: {
                departure: { status: "loading" },
                arrival: { status: "loading" }
            },
            photos: { status: "loading" },
            state: { status: "loading" },
        });

        const fetchData = async () => {
            try {
                // Fetch latest state
                const state = await getLatestState(callsign);
                setDetailState(callsign, { status: "success", data: state });

                // Fetch aircraft data (parallel)
                const aircraftPromise = state.aircraft.registration 
                    ? (async () => {
                        try {
                            const data = await getAircraft(state.aircraft.registration!);
                            setDetailAircraft(callsign, { status: "success", data });
                        } catch {
                            setDetailAircraft(callsign, { status: "error", error: "Aircraft not found" });
                        }
                    })()
                    : (async () => {
                        setDetailAircraft(callsign, { status: "error", error: "Aircraft registration unknown" });
                    })();

                // Fetch airline data (parallel)
                const airlinePromise = state.airline.icao 
                    ? (async () => {
                        try {
                            const data = await getAirline(state.airline.icao!);
                            setDetailAirline(callsign, { status: "success", data });
                        } catch {
                            setDetailAirline(callsign, { status: "error", error: "Airline not found" });
                        }
                    })()
                    : (async () => {
                        setDetailAirline(callsign, { status: "error", error: "Airline ICAO code unknown" });
                    })();

                // Fetch photos data (parallel)
                const photosPromise = state.aircraft.registration 
                    ? (async () => {
                        try {
                            const data = await getAircraftPhotos(state.aircraft.registration!);
                            setDetailPhotos(callsign, { status: "success", data});
                        } catch {
                            setDetailPhotos(callsign, { status: "error", error: "Photos not found" });
                        }
                    })()
                    : (async () => {
                        setDetailPhotos(callsign, { status: "error", error: "Aircraft registration unknown" });
                    })();

                // Fetch airport data (parallel)
                const airportPromise = state.airport.departure_iata || state.airport.arrival_iata
                    ? (async () => {
                        try {
                            const [dep, arr] = await Promise.all([
                                state.airport.departure_iata 
                                    ? getAirport(state.airport.departure_iata)
                                    : Promise.resolve(null),
                                state.airport.arrival_iata
                                    ? getAirport(state.airport.arrival_iata)
                                    : Promise.resolve(null),
                            ]);
                            if (arr) {
                                setDetailArrival(callsign, { status: "success", data: arr });
                            } else {
                                setDetailArrival(callsign, { status: "error", error: "Arrival airport not found" });
                            }
                            if (dep) {
                                setDetailDeparture(callsign, { status: "success", data: dep});
                            } else {
                                setDetailDeparture(callsign, { status: "error", error: "Departure airport not found" });
                            }
                        } catch {
                            setDetailArrival(callsign, { status: "error", error: "Airport not found" })
                            setDetailDeparture(callsign, { status: "error", error: "Airport not found" })
                        }
                    })()
                    : (async () => {
                        setDetailArrival(callsign, { status: "error", error: "Arrival airport IATA code unknown" });
                        setDetailDeparture(callsign, { status: "error", error: "Departure airport IATA code unknown" });
                    })();
                
                await Promise.all([aircraftPromise, airlinePromise, photosPromise, airportPromise]);
            }
            catch (err) {
                const errorMessage = "Failed to fetch state";
                setDetails(callsign, {
                    aircraft: { status: "error", error: errorMessage },
                    airline: { status: "error", error: errorMessage },
                    airport: {
                        departure: { status: "error", error: errorMessage },
                        arrival: { status: "error", error: errorMessage }
                    },
                    photos: { status: "error", error: errorMessage },
                    state: { status: "error", error: errorMessage },
                })
            }
        };

        fetchData();
    }, [callsign]);

    return details;
}


export function MapDetails() {
    const selectedAircraft = useMapStore((state) => state.selected);
    const details = useMapDetails(selectedAircraft);

    if (!details) return null;

    return (
        <ScrollArea className="flex-1 overflow-y-auto p-3">
            <MapDetailsHeader data={details.state} className="mb-3" />
            <MapDetailsImages data={details.photos} className="mb-3" />
            <MapDetailsAirport data={{state: details.state, airport: details.airport}} className="mb-3" />
            <MapDetailsPosition data={details.state} />
        </ScrollArea>
    );
}
