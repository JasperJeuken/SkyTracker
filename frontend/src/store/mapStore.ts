import { create } from "zustand";
import { Map } from "leaflet";
import { type Aircraft, type AircraftPhoto, type Airline, type Airport, type MapState, type SidebarDetails, type State, type Loadable } from "@/types/api";


const emptySidebarDetails: SidebarDetails = {
    state: { status: "idle" },
    photos: { status: "idle" },
    aircraft: { status: "idle" },
    airport: { departure: { status: "idle" }, arrival: { status: "idle" } },
    airline: { status: "idle" }
}


export interface MapStore {
    // States: selected aircraft
    selected: string | null;
    lastHistoryUpdate: number;
    history: MapState[];
    details: SidebarDetails;
    animatedPosition: [number, number];

    // States: map settings
    mapStates: MapState[];
    lastMapUpdate: number;
    mapStyle: "Default" | "Satellite" | "OpenStreetMap";
    sidebarOpen: boolean;
    mapRef: Map | null;
    animationZoomLimit: number;

    // Actions: selected aircraft
    setSelected: (callsign: string | null) => void;
    setLastHistoryUpdate: (update: number) => void;
    setLastHistoryUpdateString: (update: string) => void;
    setHistory: (history: MapState[]) => void;
    appendHistory: (point: MapState) => void;
    prependHistory: (point: MapState) => void;
    setDetails: (details: SidebarDetails) => void;
    setDetailState: (state: Loadable<State>) => void;
    setDetailAircraft: (aircraft: Loadable<Aircraft>) => void;
    setDetailAirline: (airline: Loadable<Airline>) => void;
    setDetailDeparture: (departure: Loadable<Airport>) => void;
    setDetailArrival: (arrival: Loadable<Airport>) => void;
    setDetailPhotos: (photos: Loadable<AircraftPhoto[]>) => void;
    setDetailLoading: () => void;
    setDetailError: (error: string) => void;
    setAnimatedPosition: (position: [number, number]) => void;
    resetSelected: () => void;

    // Actions: map settings
    setMapStates: (states: MapState[]) => void;
    setLastMapUpdate: (update: number) => void;
    setLastMapUpdateString: (update: string) => void;
    setMapStyle: (style: "Default" | "Satellite" | "OpenStreetMap") => void;
    setSidebarOpen: (open: boolean) => void;
    setMapRef: (map: Map | null) => void;
};

export const useMapStore = create<MapStore>()((set) => ({
    // States: selected aircraft
    selected: null,
    lastHistoryUpdate: Date.now(),
    history: [],
    details: structuredClone(emptySidebarDetails),
    animatedPosition: [0., 0.],

    // States: map settings
    mapStates: [],
    lastMapUpdate: Date.now(),
    mapStyle: (localStorage.getItem("mapStyle") as "Default" | "Satellite" | "OpenStreetMap") || "OpenStreetMap",
    sidebarOpen: false,
    mapRef: null,
    animationZoomLimit: 9,

    // Actions: selected aircraft
    setSelected: (callsign) => set({ selected: callsign }),
    setLastHistoryUpdate: (update) => set({ lastHistoryUpdate: update }),
    setLastHistoryUpdateString: (updateString) => set({ lastHistoryUpdate: new Date(updateString).valueOf() }),
    setHistory: (history) => set({ history: history }),
    appendHistory: (point) => set((store) => {
        const pointTime = new Date(point.time).valueOf();
        for (const state of store.history) {
            if (new Date(state.time).valueOf() == pointTime) {
                return { history: store.history };
            }
        }
        return { history: [...store.history, point] };
    }),
    prependHistory: (point) => set((store) => {
        const pointTime = new Date(point.time).valueOf();
        for (const state of store.history) {
            if (new Date(state.time).valueOf() == pointTime) {
                return { history: store.history };
            }
        }
        return { history: [point, ...store.history] };
    }),
    setDetails: (details) => set({ details: details }),
    setDetailState: (state) => set((store) => ({ details: { ...store.details, state: state }})),
    setDetailAircraft: (aircraft) => set((store) => ({ details: { ...store.details, aircraft: aircraft }})),
    setDetailAirline: (airline) => set((store) => ({ details: { ...store.details, airline: airline }})),
    setDetailDeparture: (airport) => set((store) => ({ details: { ...store.details, airport: { ...store.details.airport, departure: airport } } })),
    setDetailArrival: (airport) => set((store) => ({ details: { ...store.details, airport: { ...store.details.airport, arrival: airport } } })),
    setDetailPhotos: (photos) => set((store) => ({ details: { ...store.details, photos: photos } })),
    setDetailLoading: () => set({ details: {
        state: { status: "loading" },
        aircraft: { status: "loading" },
        airline: { status: "loading" },
        airport: { departure: { status: "loading" }, arrival: { status: "loading" } },
        photos: { status: "loading" },
    } }),
    setDetailError: (error) => set({ details: {
        state: { status: "error", error },
        aircraft: { status: "error", error },
        airline: { status: "error", error },
        airport: { departure: { status: "error", error }, arrival: { status: "error", error } },
        photos: { status: "error", error },
    } }),
    setAnimatedPosition: (position) => set({ animatedPosition: position }),
    resetSelected: () => set({ history: [], details: structuredClone(emptySidebarDetails), animatedPosition: [0., 0.] }),

    // Actions: map settings
    setLastMapUpdate: (update) => set({ lastMapUpdate: update }),
    setLastMapUpdateString: (updateString) => set({ lastMapUpdate: new Date(updateString).valueOf() }),
    setMapStates: (states) => set({ mapStates: states }),
    setMapStyle: (style) => { localStorage.setItem('mapStyle', style); set({ mapStyle: style }); },
    setSidebarOpen: (open) => set({ sidebarOpen: open }),
    setMapRef: (map) => set({ mapRef: map }),
}));
