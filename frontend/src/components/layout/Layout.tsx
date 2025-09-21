import { Header } from "./Header";
import { Sidebar } from "./Sidebar";
import { AircraftMap } from "../AircraftMap";
import { AircraftMapProvider } from "../AircraftMapProvider";


export function Layout() {
    return (
        <AircraftMapProvider>
            <div className="w-screen h-screen flex flex-col overflow-hidden">
                <Header />
                <div className="flex-1 relative overflow-hidden">
                    <AircraftMap />
                    <Sidebar />
                </div>
            </div>
        </AircraftMapProvider>
    );
}
