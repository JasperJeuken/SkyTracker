import { create } from "zustand";


export interface MapState {
    selectedAircraft: string | null;
    setSelectedAircraft: (aircraft: string | null) => void;
    mapStyle: "Default" | "Satellite" | "OpenStreetMap";
    setMapStyle: (style: "Default" | "Satellite" | "OpenStreetMap") => void;
    sidebarOpen: boolean;
    setSidebarOpen: (open: boolean) => void;
};

export const useMapStore = create<MapState>()((set) => ({
    selectedAircraft: null,
    setSelectedAircraft: (aircraft) => set(() => ({ selectedAircraft: aircraft })),
    mapStyle: (localStorage.getItem("mapStyle") as "Default" | "Satellite" | "OpenStreetMap") || "OpenStreetMap",
    setMapStyle: (style) => set(() => ({ mapStyle: style })),
    sidebarOpen: false,
    setSidebarOpen: (open) => set(() => ({ sidebarOpen: open })),
}));
