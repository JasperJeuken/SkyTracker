import { useAircraftMap } from "./AircraftMapProvider";

export function AircraftDetails() {
    const { selectedAircraft } = useAircraftMap();

    return (
        <p>{selectedAircraft}</p>
    );
}
