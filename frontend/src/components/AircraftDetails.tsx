import { X, TowerControl, Plane, Star, SatelliteDish, GitCommitHorizontal,
    GitCommitVertical, ArrowUpFromLine, Gauge, MoveVertical, Tag, CircleArrowOutUpLeft, RadioTower } from "lucide-react";
import { useAircraftMap } from "./AircraftMapProvider";
import { Card, CardAction, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Carousel, CarouselItem } from "@/components/ui/carousel";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Separator } from "@/components/ui/separator";
import { getAircraftDetails, getAircraftImages } from "../services/api";
import { useEffect, useState } from "react";
import ReactCountryFlag from "react-country-flag";
import { AircraftDetailItem } from "./AircraftDetailItem";
import { AircraftDetailBadge } from "./AircraftDetailBadge";


type AircraftDetails = {
    icao24: string,
    known_callsigns: string[], //
    origin_country: string, //
    last_state: number,
    last_position: number,
    last_contact: number,
    last_latitude: number | null, //
    last_longitude: number | null, //
    last_baro_altitude: number | null, //
    last_geo_altitude: number | null, //
    last_velocity: number | null, //
    last_heading: number | null,
    last_vertical_rate: number | null,
    last_on_ground: boolean, //
    last_spi: boolean, //
    last_squawk: string | null,
    last_position_source: string, //
    last_category: string,
};

type AircraftImage = {
    image_url: string,
    detail_url: string
};


export function AircraftDetails() {
    const { selectedAircraft, setSelectedAircraft } = useAircraftMap();
    const [details, setDetails] = useState<AircraftDetails | null>(null);
    // const [aircraftImages, setAircraftImages] = useState<AircraftImage[] | null>(null);
    const [loadingDetails, setLoadingDetails] = useState(false);

    const onDeselect = () => {
        setSelectedAircraft(null);
    };

    useEffect(() => {
        if (!selectedAircraft) {
            setDetails(null);
            return;
        }
        setLoadingDetails(true);
        console.log(selectedAircraft);
        getAircraftDetails(selectedAircraft)
            .then(data => setDetails(data))
            .catch((err) => {
                console.error(err);
                setDetails(null);
            })
            .finally(() => setLoadingDetails(false));
    }, [selectedAircraft]);

    return (
        <Card className="backdrop-blur-md shadow-lg">
            <CardHeader>
                <CardTitle>Selected aircraft</CardTitle>
                <CardDescription>ICAO24: {details?.icao24.toUpperCase() || ""}</CardDescription>
                <CardAction>
                    <Button variant="ghost" size="icon" onClick={onDeselect} aria-label="Deselect">
                        <X className="h-4 w-4" />
                    </Button>
                </CardAction>
            </CardHeader>
            <CardContent>
                {loadingDetails ? (
                    <Skeleton className="h-120 w-full" />
                ) : details ? (
                    <>
                        <AircraftDetailBadge icon={details.last_on_ground ? <TowerControl className="h-4 w-4" /> : <Plane className="h-4 w-4" />} text={details.last_on_ground ? "On ground" : "In flight"} />
                        <AircraftDetailBadge icon={<SatelliteDish className="h-4 w-4" />} text={details.last_position_source} />
                        {details.last_spi && <AircraftDetailBadge icon={<Star className="h-4 w-4" />} text="Special" />}
                        <AircraftDetailBadge icon={<ReactCountryFlag svg countryCode={details.origin_country} />} text={details.origin_country} />
                        <div className="aircraft-details-grid mt-4">
                            <AircraftDetailItem full label="Callsign" icon={Tag} value={details.known_callsigns[0] || "N/A"} />
                            <Separator className="aircraft-details-full" />
                            <AircraftDetailItem label="Latitude" icon={GitCommitVertical} value={details.last_latitude ? Math.round(details.last_latitude * 1000) / 1000 : "N/A"} unit="deg" />
                            <AircraftDetailItem label="Longitude" icon={GitCommitHorizontal} value={details.last_longitude ? Math.round(details.last_longitude * 1000) / 1000 : "N/A"} unit="deg" />
                            <AircraftDetailItem label="Baro. altitude" icon={ArrowUpFromLine} value={details.last_baro_altitude ? Math.round(details.last_baro_altitude) : "N/A"} unit="m" />
                            <AircraftDetailItem label="Velocity" icon={Gauge} value={details.last_velocity ? Math.round(details.last_velocity* 1.94384449 * 10) / 10: "N/A"} unit="kts" />
                            <Separator className="aircraft-details-full" />
                            <AircraftDetailItem label="Heading" icon={(props) => (<CircleArrowOutUpLeft {...props} style={{ transform: `rotate(${details.last_heading ? details.last_heading + 45 : 45}deg)` }} />)} value={details.last_heading ? Math.round(details.last_heading) : "N/A"} unit="deg" />
                            <AircraftDetailItem label="Vertical speed" icon={MoveVertical} value={details.last_vertical_rate ? Math.round(details.last_vertical_rate * 10) / 10 : "N/A"} unit="m/s" />
                            <AircraftDetailItem full label="Squawk" icon={RadioTower} value={details.last_squawk} />
                        </div>
                    </>
                ) : (
                    loadingDetails ? <Skeleton className="h-16 w-full" /> : <p>Could not load aircraft details...</p>
                )}
            </CardContent>
        </Card>
    );
}
