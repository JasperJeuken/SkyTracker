import { X } from "lucide-react";
import { useAircraftMap } from "./AircraftMapProvider";
import { Card, CardAction, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { getAircraftDetails } from "@/services/api";
import { useEffect, useState } from "react";


type AircraftDetails = {
    icao24: string,
    known_callsigns: string[],
    origin_country: string,
    last_state: number,
    last_position: number,
    last_contact: number,
    last_latitude: number | null,
    last_longitude: number | null,
    last_baro_altitude: number | null,
    last_geo_altitude: number | null,
    last_velocity: number | null,
    last_heading: number | null,
    last_vertical_rate: number | null,
    last_on_ground: boolean,
    last_spi: boolean,
    last_squawk: string | null,
    last_position_source: string,
    last_category: string,
};


export function AircraftDetails() {
    const { selectedAircraft, setSelectedAircraft } = useAircraftMap();
    const [details, setDetails] = useState<AircraftDetails | null>(null);
    const [loading, setLoading] = useState(false);

    const onDeselect = () => {
        setSelectedAircraft(null);
    };

    useEffect(() => {
        if (!selectedAircraft) {
            setDetails(null);
            return;
        }
        setLoading(true);
        getAircraftDetails(selectedAircraft)
            .then(data => setDetails(data))
            .catch(console.error)
            .finally(() => setLoading(false));
    }, [selectedAircraft]);

    return (
        <Card>
            <CardHeader>
                <CardTitle>Selected aircraft</CardTitle>
                <CardDescription>Info</CardDescription>
                <CardAction>
                    <Button variant="ghost" size="icon" onClick={onDeselect} aria-label="Deselect">
                        <X className="h-4 w-4" />
                    </Button>
                </CardAction>
            </CardHeader>
            <CardContent>
                {loading ? (
                    <Skeleton className="h-16 w-full" />
                ) : details ? (
                    <div>
                        <div>Callsign: {details.known_callsigns[0] || "N/A"}</div>
                        <div>Latitude: {details.last_latitude ?? "N/A"}</div>
                        <div>Longitude: {details.last_longitude ?? "N/A"}</div>
                    </div>
                ) : (
                    <Skeleton className="h-16 w-full" />
                )}
            </CardContent>
        </Card>
    );
}
