import { type ReactNode, useState } from "react";
import { Header } from "./Header";
import { Sidebar } from "./Sidebar";

export function Layout({ children }: { children: ReactNode | Function }) {
    const [sidebarOpen, setSidebarOpen] = useState(false);
    const [mapStyle, setMapStyle ] = useState<"Default" | "Satellite">("Default");

    return (
        <div className="w-screen h-screen flex flex-col overflow-hidden">
            <Header onToggleSidebar={() => setSidebarOpen(!sidebarOpen)} />
            <div className="flex-1 relative overflow-hidden">
                {/* {sidebarOpen && (<Sidebar onClose={() => setSidebarOpen(false)} />)} */}
                {children && typeof children === "function" ? children({ mapStyle }) : children}
                <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} mapStyle={mapStyle} setMapStyle={setMapStyle} />
            </div>
        </div>
    );
}
