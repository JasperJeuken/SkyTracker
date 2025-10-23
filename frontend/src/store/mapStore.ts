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
    // States
    selected: string | null;
    history: Record<string, MapState[]>;
    details: Record<string, SidebarDetails>;
    mapStyle: "Default" | "Satellite" | "OpenStreetMap";
    sidebarOpen: boolean;
    mapRef: Map | null;

    // Actions
    setSelected: (callsign: string | null) => void;
    setHistory: (callsign: string, history: MapState[]) => void;
    appendHistoryPoint: (callsign: string, point: MapState) => void;
    prependHistoryPoint: (callsign: string, point: MapState) => void;
    setDetails: (callsign: string, details: SidebarDetails) => void;
    setDetailState: (callsign: string, state: Loadable<State>) => void;
    setDetailAircraft: (callsign: string, aircraft: Loadable<Aircraft>) => void;
    setDetailAirline: (callsign: string, airline: Loadable<Airline>) => void;
    setDetailDeparture: (callsign: string, departure: Loadable<Airport>) => void;
    setDetailArrival: (callsign: string, arrival: Loadable<Airport>) => void;
    setDetailPhotos: (callsign: string, photos: Loadable<AircraftPhoto[]>) => void;
    setMapStyle: (style: "Default" | "Satellite" | "OpenStreetMap") => void;
    setSidebarOpen: (open: boolean) => void;
    setMapRef: (map: Map | null) => void;
};

export const useMapStore = create<MapStore>()((set) => ({
    // States
    selected: null,
    history: {},
    details: {},
    mapStyle: (localStorage.getItem("mapStyle") as "Default" | "Satellite" | "OpenStreetMap") || "OpenStreetMap",
    sidebarOpen: false,
    mapRef: null,

    // Actions
    setSelected: (callsign) => set({ selected: callsign }),
    setHistory: (callsign, history) => set((store) => ({ history: { ...store.history, [callsign]: history } })),
    appendHistoryPoint: (callsign, point) => set((store) => {
        const current = store.history[callsign] || [];
        return { history: { ...store.history, [callsign]: [...current, point] } }
    }),
    prependHistoryPoint: (callsign, point) => set((store) => {
        const current = store.history[callsign] || [];
        return { history: { ...store.history, [callsign]: [point, ...current] } }
    }),
    setDetails: (callsign, details) => set((store) => ({ details: { ...store.details, [callsign]: details } })),
    setDetailState: (callsign, state) => set((store) => {
        const current = store.details[callsign] || structuredClone(emptySidebarDetails);
        return { details: { ...store.details, [callsign]: { ...current, state: state } } }
    }),
    setDetailAircraft: (callsign, aircraft) => set((store) => {
        const current = store.details[callsign] || structuredClone(emptySidebarDetails);
        return { details: { ...store.details, [callsign]: { ...current, aircraft: aircraft } } }
    }),
    setDetailAirline: (callsign, airline) => set((store) => {
        const current = store.details[callsign] || structuredClone(emptySidebarDetails);
        return { details: { ...store.details, [callsign]: { ...current, airline: airline } } }
    }),
    setDetailDeparture: (callsign, departure) => set((store) => {
        const current = store.details[callsign] || structuredClone(emptySidebarDetails);
        return { details: { ...store.details, [callsign]: { ...current, airport: { ...current.airport, departure: departure } } } }
    }),
    setDetailArrival: (callsign, arrival) => set((store) => {
        const current = store.details[callsign] || structuredClone(emptySidebarDetails);
        return { details: { ...store.details, [callsign]: { ...current, airport: { ...current.airport, arrival: arrival } } } }
    }),
    setDetailPhotos: (callsign, photos) => set((store) => {
        const current = store.details[callsign] || structuredClone(emptySidebarDetails);
        return { details: { ...store.details, [callsign]: { ...current, photos: photos } } }
    }),
    setMapStyle: (style) => { localStorage.setItem('mapStyle', style); set({ mapStyle: style }); },
    setSidebarOpen: (open) => set({ sidebarOpen: open }),
    setMapRef: (map) => set({ mapRef: map }),
}));
