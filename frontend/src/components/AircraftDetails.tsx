import { X, TowerControl, Plane, Star, SatelliteDish } from "lucide-react";
import { useAircraftMap } from "./AircraftMapProvider";
import { Card, CardAction, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { getAircraftDetails } from "../services/api";
import { useEffect, useState } from "react";
import ReactCountryFlag from "react-country-flag";


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
        <Card className="backdrop-blur-md shadow-lg">
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
                    <>
                        <Badge variant="secondary">
                            {details.last_on_ground ? <TowerControl className="h-4 w-4" /> : <Plane className="h-4 w-4" />}
                            <p>{details.last_on_ground ? "On ground" : "In flight"}</p>
                        </Badge>
                        <Badge variant="secondary" className="ml-2">
                            <SatelliteDish className="h-4 w-4" /><p>{details.last_position_source}</p>
                        </Badge>
                        {details.last_spi && (
                            <Badge variant="secondary" className="ml-2">
                                <Star className="h-4 w-4" /><p>Special</p>
                            </Badge>
                        )}
                        <Badge variant="secondary" className="ml-2">
                            <ReactCountryFlag svg countryCode={details.origin_country} />
                            <p>{details.origin_country}</p>
                        </Badge>
                        <div className="aircraft-details-grid mt-4">
                            <div className="aircraft-details-item aircraft-details-full bg-gray-50 backdrop-blur-md shadow-lg p-3 dark:bg-gray-800">
                                <span className="aircraft-details-label !text-gray-600 dark:!text-gray-400">Callsign</span>
                                <span className="aircraft-details-value">{details.known_callsigns[0] || "N/A"}</span>
                            </div>
                            <div className="aircraft-details-item bg-gray-50 backdrop-blur-md shadow-lg p-3 dark:bg-gray-800">
                                <span className="aircraft-details-label !text-gray-600 dark:!text-gray-400">Latitude</span>
                                <span className="aircraft-details-value">
                                    {details.last_latitude ? Math.round(details.last_latitude * 10000) / 10000 : "N/A"}
                                    <span className="aircraft-details-unit !text-gray-600 dark:!text-gray-400">{details.last_latitude !== null ? "deg": ""}</span>
                                </span>
                            </div>
                            <div className="aircraft-details-item bg-gray-50 backdrop-blur-md shadow-lg p-3 dark:bg-gray-800">
                                <span className="aircraft-details-label !text-gray-600 dark:!text-gray-400">Longitude</span>
                                <span className="aircraft-details-value">
                                    {details.last_longitude ? Math.round(details.last_longitude * 10000) / 10000 : "N/A"}
                                    <span className="aircraft-details-unit !text-gray-600 dark:!text-gray-400">{details.last_longitude !== null ? "deg": ""}</span>
                                </span>
                            </div>
                            <div className="aircraft-details-item bg-gray-50 backdrop-blur-md shadow-lg p-3 dark:bg-gray-800">
                                <span className="aircraft-details-label !text-gray-600 dark:!text-gray-400">Baro. altitude</span>
                                <span className="aircraft-details-value">
                                    {details.last_baro_altitude ? Math.round(details.last_baro_altitude) : "N/A"}
                                    <span className="aircraft-details-unit !text-gray-600 dark:!text-gray-400">{details.last_baro_altitude !== null ? "m": ""}</span>
                                </span>
                            </div>
                            <div className="aircraft-details-item border-r bg-gray-50 backdrop-blur-md shadow-lg p-3 dark:bg-gray-800">
                                <span className="aircraft-details-label !text-gray-600 dark:!text-gray-400">Velocity</span>
                                <span className="aircraft-details-value">
                                    {details.last_velocity ? Math.round(details.last_velocity * 1.94384449 * 10) / 10 : "N/A"}
                                    <span className="aircraft-details-unit !text-gray-600 dark:!text-gray-400">{details.last_velocity !== null ? "kts": ""}</span>
                                </span>
                            </div>
                        </div>
                    </>
                ) : (
                    <Skeleton className="h-16 w-full" />
                )}
            </CardContent>
        </Card>
    );
}
