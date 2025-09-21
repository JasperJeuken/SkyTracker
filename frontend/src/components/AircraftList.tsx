import { useEffect, useState } from "react";
import { getLatestBatch } from "../services/api";

export function AircraftList() {
    const [aircraft, setAircraft] = useState<any[]>([]);

    useEffect(() => {
        getLatestBatch().then(setAircraft).catch(console.error);
    }, []);

    return (
        <ul>
            {aircraft.map((a) => (
                <li key={a.icao24}>{a.icao24}: ({a.latitude}, {a.longitude})</li>
            ))}
        </ul>
    );
}
