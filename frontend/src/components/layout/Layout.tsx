import { type ReactNode, useState } from "react";
import { Header } from "./Header";
import { Sidebar } from "./Sidebar";
import { AircraftMap } from "../AircraftMap";
import { AircraftMapProvider } from "../AircraftMapProvider";


export function Layout() {
    const [sidebarOpen, setSidebarOpen] = useState(false);
    // const [mapStyle, setMapStyle ] = useState<"Default" | "Satellite">("Default");

    return (
        <AircraftMapProvider>
            <div className="w-screen h-screen flex flex-col overflow-hidden">
                <Header onToggleSidebar={() => setSidebarOpen(!sidebarOpen)} />
                <div className="flex-1 relative overflow-hidden">
                    <AircraftMap />
                    <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
                </div>
            </div>
        </AircraftMapProvider>
    );
}
