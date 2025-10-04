import { createContext, useContext, useEffect, useState, type ReactNode } from "react";


type AircraftMapContextType = {
    selectedAircraft: string | null;
    setSelectedAircraft: (aircraft: string | null) => void;
    mapStyle: "Default" | "Satellite" | "OpenStreetMap";
    setMapStyle: (style: "Default" | "Satellite" | "OpenStreetMap") => void;
    sidebarOpen: boolean
    setSidebarOpen: (sidebarOpen: boolean) => void;
};

const AircraftMapContext = createContext<AircraftMapContextType | undefined>(undefined);

export function useAircraftMap() {
    const ctx = useContext(AircraftMapContext);
    if (!ctx) throw new Error("Aircraft map must be used within AircraftMapProvider");
    return ctx
}

export function AircraftMapProvider({ children }: { children: ReactNode }) {
    const [selectedAircraft, setSelectedAircraft] = useState<string | null>(() => {
        // return (localStorage.getItem("selectedAircraft") || null);
        return null;
    });
    const [mapStyle, setMapStyle] = useState<"Default" | "Satellite" | "OpenStreetMap">(() => {
        return (localStorage.getItem("mapStyle") as "Default" | "Satellite" | "OpenStreetMap") || "OpenStreetMap";
    });
    const [sidebarOpen, setSidebarOpen] = useState(() => {
        // return localStorage.getItem('sidebarOpen') ? localStorage.getItem('sidebarOpen') == "true" : false;
        return false;
    });

    useEffect(() => {
        localStorage.setItem("mapStyle", mapStyle);
    }, [mapStyle])

    // useEffect(() => {
    //     localStorage.setItem('sidebarOpen', sidebarOpen ? "true" : "false");
    // }, [sidebarOpen])

    // useEffect(() => {
    //     localStorage.setItem('selectedAircraft', selectedAircraft ?? "");
    // }, [selectedAircraft])

    return (
        <AircraftMapContext.Provider value={{
            selectedAircraft, setSelectedAircraft,
            mapStyle, setMapStyle,
            sidebarOpen, setSidebarOpen
        }}>
            {children}
        </AircraftMapContext.Provider>
    );
}
