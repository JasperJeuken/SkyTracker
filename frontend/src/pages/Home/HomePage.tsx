import { AircraftMap } from "@/components/visuals/aircraftMap/AircraftMap";
import { Sidebar } from "@/components/layout/Sidebar";

export default function HomePage() {
    return (
        <>
            <AircraftMap />
            <Sidebar />
        </>
    );
}
