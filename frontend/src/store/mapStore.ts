import { create } from "zustand";
import { Map } from "leaflet";


export interface MapState {
    selectedAircraft: string | null;
    setSelectedAircraft: (aircraft: string | null) => void;
    mapStyle: "Default" | "Satellite" | "OpenStreetMap";
    setMapStyle: (style: "Default" | "Satellite" | "OpenStreetMap") => void;
    sidebarOpen: boolean;
    setSidebarOpen: (open: boolean) => void;
    mapRef: Map | null;
    setMapRef: (map: Map | null) => void;
};

export const useMapStore = create<MapState>()((set) => ({
    selectedAircraft: null,
    setSelectedAircraft: (aircraft) => set(() => ({ selectedAircraft: aircraft })),
    mapStyle: (localStorage.getItem("mapStyle") as "Default" | "Satellite" | "OpenStreetMap") || "OpenStreetMap",
    setMapStyle: (style) => set(() => ({ mapStyle: style })),
    sidebarOpen: false,
    setSidebarOpen: (open) => set(() => ({ sidebarOpen: open })),
    mapRef: null,
    setMapRef: (map) => set(() => ({ mapRef: map })),
}));
