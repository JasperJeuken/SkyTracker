import { getLatestState } from "@/services/api/state";
import { getAirport } from "@/services/api/airport";
import { getAirline } from "@/services/api/airline";
import { getAircraft, getAircraftPhotos } from "@/services/api/aircraft";
import { useMapStore } from "@/store/mapStore";
import { useEffect, useState } from "react";
import { type State, type Aircraft, type Airport, type Airline, type AircraftPhoto } from "@/types/api";
import { ScrollArea } from "@/components/ui/scroll-area";
import { MapDetailsAirport } from "./MapDetailsAirport";
import { MapDetailsImages } from "./MapDetailsImages";
import { MapDetailsHeader } from "./MapDetailsHeader";


function useMapDetails(callsign: string | null) {
    // Data states
    const [stateData, setStateData] = useState<State | null>(null);
    const [aircraftData, setAircraftData] = useState<Aircraft | null>(null);
    const [airlineData, setAirlineData] = useState<Airline | null>(null);
    const [photosData, setPhotosData] = useState<AircraftPhoto[] | null>(null);
    const [airportData, setAirportData] = useState<{
        arrival: Airport | null,
        departure: Airport | null,
    }>({ arrival: null, departure: null });

    // Loading/error states
    const [loading, setLoading] = useState({
        state: false,
        aircraft: false,
        airline: false,
        airport: false,
        photos: false,
    });
    const [error, setError] = useState({
        state: null as string | null,
        aircraft: null as string | null,
        airline: null as string | null,
        airport: null as string | null,
        photos: null as string | null,
    });

    useEffect(() => {
        // Reset
        setStateData(null);
        setAircraftData(null);
        setAirlineData(null);
        setPhotosData(null);
        setAirportData({ arrival: null, departure: null });
        setLoading({ state: true, aircraft: true, airline: true, airport: true, photos: true });
        setError({ state: null, aircraft: null, airline: null, airport: null, photos: null });
        if (!callsign) return;

        const fetchData = async () => {
            try {
                // Fetch latest state
                const state = await getLatestState(callsign);
                setStateData(state);
                setLoading((v) => ({ ...v, state: false }));

                // Fetch aircraft data (parallel)
                const aircraftPromise = state.aircraft.registration 
                    ? (async () => {
                        setLoading((v) => ({ ...v, aircraft: true }));
                        try {
                            const data = await getAircraft(state.aircraft.registration!);
                            setAircraftData(data);
                        } catch {
                            setAircraftData(null);
                            setError((e) => ({ ...e, aircraft: "Aircraft not found" }));
                        } finally {
                            setLoading((v) => ({ ...v, aircraft: false}));
                        }
                    })()
                    : (async () => {
                        setError((e) => ({ ...e, aircraft: "No aircraft registration" }));
                        setLoading((v) => ({ ...v, aircraft: false}));
                    })();

                // Fetch airline data (parallel)
                const airlinePromise = state.airline.icao 
                    ? (async () => {
                        setLoading((v) => ({ ...v, airline: true }));
                        try {
                            const data = await getAirline(state.airline.icao!);
                            setAirlineData(data);
                        } catch {
                            setAirlineData(null);
                            setError((e) => ({ ...e, airline: "Airline not found" }));
                        } finally {
                            setLoading((v) => ({ ...v, airline: false}));
                        }
                    })()
                    : (async () => {
                        setError((e) => ({ ...e, airline: "No airline ICAO code" }));
                        setLoading((v) => ({ ...v, airline: false}));
                    })();

                // Fetch photos data (parallel)
                const photosPromise = state.aircraft.registration 
                    ? (async () => {
                        setLoading((v) => ({ ...v, photos: true }));
                        try {
                            const data = await getAircraftPhotos(state.aircraft.registration!);
                            setPhotosData(data);
                        } catch {
                            setPhotosData(null);
                            setError((e) => ({ ...e, photos: "Photos not found" }));
                        } finally {
                            setLoading((v) => ({ ...v, photos: false}));
                        }
                    })()
                    : (async () => {
                        setError((e) => ({ ...e, photos: "No aircraft registration" }));
                        setLoading((v) => ({ ...v, photos: false}));
                    })();

                // Fetch airport data (parallel)
                const airportPromise = state.airport.departure_iata || state.airport.arrival_iata
                    ? (async () => {
                        setLoading((v) => ({ ...v, airport: true }));
                        try {
                            const [dep, arr] = await Promise.all([
                                state.airport.departure_iata 
                                    ? getAirport(state.airport.departure_iata)
                                    : Promise.resolve(null),
                                state.airport.arrival_iata
                                    ? getAirport(state.airport.arrival_iata)
                                    : Promise.resolve(null),
                            ]);
                            setAirportData({ departure: dep, arrival: arr });
                        } catch {
                            setAirportData({ departure: null, arrival: null });
                            setError((e) => ({ ...e, airport: "Airport not found" }));
                        } finally {
                            setLoading((v) => ({ ...v, airport: false }));
                        }
                    })()
                    : (async () => {
                        setError((e) => ({ ...e, airport: "No airport IATA code" }));
                        setLoading((v) => ({ ...v, airport: false }));
                    })();
                
                await Promise.all([aircraftPromise, airlinePromise, photosPromise, airportPromise]);
            } catch (err) {
                console.error(err);
                setError((e) => ({ ...e, state: "State fetch failed" }));
                setLoading((v) => ({ ...v, state: false }));
            }
        };

        fetchData();
    }, [callsign]);

    return {
        stateData,
        aircraftData,
        airlineData,
        photosData,
        airportData,
        loading,
        error,
    };
}


export function MapDetails() {
    const selectedAircraft = useMapStore((state) => state.selectedAircraft);
    const { stateData, photosData, airportData, loading, error } = useMapDetails(selectedAircraft);

    return (
        <ScrollArea className="flex-1 overflow-y-auto p-3">
            <MapDetailsHeader stateData={stateData} loading={loading['state']} error={error['state']} className="mb-3" />
            <MapDetailsImages photosData={photosData} error={error.photos} className="mb-3" />
            <MapDetailsAirport data={{state: stateData, airport: airportData}} loading={{state: loading['state'], airport: loading['airport']}} error={{state: error['state'], airport: error['airport']}} className="mb-3" />
        </ScrollArea>
    );
}
