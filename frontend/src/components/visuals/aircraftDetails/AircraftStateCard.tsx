import { type State } from "@/types/api";

export function AircraftStateCard({ data }: { data: State | null }) {
    return (
        data ? <p>{data.flight.icao}</p> : <p>No data</p>
    )
}
