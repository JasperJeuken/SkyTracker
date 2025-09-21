import { createContext, useContext, useState, type ReactNode } from "react";


type AircraftMapContextType = {
    selectedAircraft: string | null;
    setSelectedAircraft: (aircraft: string | null) => void;
    mapStyle: "Default" | "Satellite";
    setMapStyle: (style: "Default" | "Satellite") => void;
};

const AircraftMapContext = createContext<AircraftMapContextType | undefined>(undefined);

export function useAircraftMap() {
    const ctx = useContext(AircraftMapContext);
    if (!ctx) throw new Error("Aircraft map must be used within AircraftMapProvider");
    return ctx
}

export function AircraftMapProvider({ children }: { children: ReactNode }) {
    const [selectedAircraft, setSelectedAircraft] = useState<string | null>(null);
    const [mapStyle, setMapStyle] = useState<"Default" | "Satellite">("Default");

    return (
        <AircraftMapContext.Provider value={{
            selectedAircraft, setSelectedAircraft,
            mapStyle, setMapStyle
        }}>
            {children}
        </AircraftMapContext.Provider>
    );
}
