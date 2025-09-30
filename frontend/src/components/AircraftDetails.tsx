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
import { AircraftDetailImages } from "./AircraftDetailImages";
import { type AircraftDetails, type AircraftImage } from "@/types/api";



export function AircraftDetails({ showImages = false }: { showImages?: boolean }) {
    const { selectedAircraft, setSelectedAircraft } = useAircraftMap();
    const [details, setDetails] = useState<AircraftDetails | null>(null);
    const [loadingDetails, setLoadingDetails] = useState(false);
    const [images, setImages] = useState<AircraftImage[] | null>(null);
    const [loadingImages, setLoadingImages] = useState(false);

    const onDeselect = () => {
        setSelectedAircraft(null);
    };

    useEffect(() => {
        if (!selectedAircraft) {
            setDetails(null);
            setImages(null);
            return;
        }

        setLoadingDetails(true);
        if (showImages) setLoadingImages(true);
        
        // Load aircraft details
        getAircraftDetails(selectedAircraft)
            .then(data => setDetails(data))
            .catch((err) => {
                setDetails(null);
                console.error(err);
            })
            .finally(() => setLoadingDetails(false));
        
        // Load aircraft images
        if (showImages) getAircraftImages(selectedAircraft)
            .then((data) => setImages(data))
            .catch((err) => {
                setImages(null);
                console.error(err);
            })
            .finally(() => setLoadingImages(false));
    }, [selectedAircraft]);

    return (
        <Card className="backdrop-blur-md shadow-lg">
            <CardHeader>
                <CardTitle>Selected aircraft</CardTitle>
                <CardDescription>Callsign: {details?.flight_icao || ""}</CardDescription>
                <CardAction>
                    <Button variant="ghost" size="icon" onClick={onDeselect} aria-label="Deselect">
                        <X className="h-4 w-4" />
                    </Button>
                </CardAction>
            </CardHeader>
            <CardContent>
                {loadingDetails ? (
                    <Skeleton className="h-140 w-full" />
                ) : details ? (
                    <>
                        {/* Badges */}
                        <AircraftDetailBadge icon={details.is_on_ground ? <TowerControl className="h-4 w-4" /> : <Plane className="h-4 w-4" />} text={details.is_on_ground ? "On ground" : "In flight"} />
                        {/* <AircraftDetailBadge icon={<SatelliteDish className="h-4 w-4" />} text={details.last_position_source} /> */}
                        {/* {details.last_spi && <AircraftDetailBadge icon={<Star className="h-4 w-4" />} text="Special" />} */}
                        {/* <AircraftDetailBadge icon={<ReactCountryFlag svg countryCode={details.origin_country} />} text={details.origin_country} /> */}

                        {/* Image carousel */}
                        {/* {showImages && (loadingImages ? (
                            <Skeleton className="w-full aspect-[16/9] rounded-2xl mt-4" />
                        ) : (
                            <AircraftDetailImages images={images ?? []} />
                        ))} */}
                        { showImages && (loadingImages ? 
                            <Skeleton className="w-full aspect-[16/9] rounded-2xl mt-4" /> 
                            : 
                            <AircraftDetailImages images={images ?? []} />)
                        }

                        {/* Information cards */}
                        <div className="aircraft-details-grid mt-4">
                            <AircraftDetailItem full label="Callsign" icon={Tag} value={details.flight_icao} />
                            <Separator className="aircraft-details-full" />
                            <AircraftDetailItem label="Latitude" icon={GitCommitVertical} value={details.position[0] ? Math.round(details.position[0] * 1000) / 1000 : "N/A"} unit="deg" />
                            <AircraftDetailItem label="Longitude" icon={GitCommitHorizontal} value={details.position[1] ? Math.round(details.position[1] * 1000) / 1000 : "N/A"} unit="deg" />
                            <AircraftDetailItem label="Baro. altitude" icon={ArrowUpFromLine} value={details.baro_altitude ? Math.round(details.baro_altitude) : "N/A"} unit="m" />
                            <AircraftDetailItem label="Velocity" icon={Gauge} value={details.speed_horizontal ? Math.round(details.speed_horizontal* 1.94384449 * 10) / 10: "N/A"} unit="kts" />
                            <Separator className="aircraft-details-full" />
                            <AircraftDetailItem label="Heading" icon={(props) => (<CircleArrowOutUpLeft {...props} style={{ transform: `rotate(${details.heading ? details.heading + 45 : 45}deg)` }} />)} value={details.heading ? Math.round(details.heading) : "N/A"} unit="deg" />
                            <AircraftDetailItem label="Vertical speed" icon={MoveVertical} value={details.speed_vertical ? Math.round(details.speed_vertical * 10) / 10 : "N/A"} unit="m/s" />
                            <AircraftDetailItem full label="Squawk" icon={RadioTower} value={details.squawk || "N/A"} />
                        </div>
                    </>
                ) : (
                    loadingDetails ? <Skeleton className="h-16 w-full" /> : <p>Could not load aircraft details...</p>
                )}
            </CardContent>
        </Card>
    );
}
