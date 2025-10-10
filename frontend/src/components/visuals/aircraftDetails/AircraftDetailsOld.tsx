// import { X, TowerControl, Plane, GitCommitHorizontal,
//     GitCommitVertical, ArrowUpFromLine, Gauge, MoveVertical, Tag, CircleArrowOutUpLeft, RadioTower, PlaneTakeoff, PlaneLanding } from "lucide-react";
// import { useAircraftMap } from "./AircraftMapProvider";
// import { Card, CardAction, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
// import { Button } from "@/components/ui/button";
// import { Skeleton } from "@/components/ui/skeleton";
// import { ScrollArea } from "./ui/scroll-area";
// import { SeparatorWithText } from "./ui/separatorWithText";
// import { getLatestState } from "@/services/api/state";
// import { getAircraftPhotos } from "@/services/api/aircraft";
// import { useEffect, useState } from "react";
// import ReactCountryFlag from "react-country-flag";
// import { AircraftDetailItem } from "./AircraftDetailItem";
// import { AircraftDetailBadge } from "./AircraftDetailBadge";
// import { AircraftDetailImages } from "./AircraftDetailImages";
// import { type State, type AircraftPhoto } from "@/types/api";



// export function AircraftDetails({ showImages = false }: { showImages?: boolean }) {
//     const { selectedAircraft, setSelectedAircraft, setSidebarOpen } = useAircraftMap();
//     const [details, setDetails] = useState<State | null>(null);
//     const [loadingDetails, setLoadingDetails] = useState(false);
//     const [images, setImages] = useState<AircraftPhoto[] | null>(null);
//     const [loadingImages, setLoadingImages] = useState(false);

//     const onDeselect = () => {
//         setSelectedAircraft(null);
//         setSidebarOpen(false);
//     };

//     useEffect(() => {
//         if (!selectedAircraft) {
//             setDetails(null);
//             setImages(null);
//             return;
//         }

//         setLoadingDetails(true);
//         if (showImages) setLoadingImages(true);
        
//         // Load aircraft details
//         getLatestState(selectedAircraft)
//             .then(data => setDetails(data))
//             .catch(() => {
//                 setDetails(null);
//             })
//             .finally(() => setLoadingDetails(false));
        
//         // Load aircraft images
//         if (showImages) getAircraftPhotos(selectedAircraft)
//             .then((data) => setImages(data))
//             .catch(() => {
//                 setImages(null);
//             })
//             .finally(() => setLoadingImages(false));
//     }, [selectedAircraft]);

//     return (
//         <Card className="backdrop-blur-md shadow-lg flex flex-col h-full">
//             <CardHeader>
//                 <CardTitle>Selected aircraft</CardTitle>
//                 <CardDescription>Callsign: {details?.flight.icao || ""}</CardDescription>
//                 <CardAction>
//                     <Button variant="ghost" size="icon" onClick={onDeselect} aria-label="Deselect">
//                         <X className="h-4 w-4" />
//                     </Button>
//                 </CardAction>
//             </CardHeader>
//             <CardContent className="flex-1 flex flex-col overflow-hidden">
//                 {loadingDetails ? (
//                     <Skeleton className="flex-1 w-full overflow-y-auto mt-4" />
//                 ) : details ? (
//                     <>
//                         {/* Badges */}
//                         <AircraftDetailBadge icon={details.geography.is_on_ground ? <TowerControl className="h-4 w-4" /> : <Plane className="h-4 w-4" />} text={details.geography.is_on_ground ? "On ground" : "In flight"} />
//                         {/* <AircraftDetailBadge icon={<SatelliteDish className="h-4 w-4" />} text={details.last_position_source} /> */}
//                         {/* {details.last_spi && <AircraftDetailBadge icon={<Star className="h-4 w-4" />} text="Special" />} */}
//                         {/* <AircraftDetailBadge icon={<ReactCountryFlag svg countryCode={details.origin_country} />} text={details.origin_country} /> */}

//                         {/* Image carousel */}
//                         {/* {showImages && (loadingImages ? (
//                             <Skeleton className="w-full aspect-[16/9] rounded-2xl mt-4" />
//                         ) : (
//                             <AircraftDetailImages images={images ?? []} />
//                         ))} */}
//                         { showImages && (loadingImages ? 
//                             <Skeleton className="w-full aspect-[16/9] rounded-2xl mt-4" /> 
//                             : 
//                             <AircraftDetailImages images={images ?? []} />)
//                         }

//                         {/* Information cards */}
//                         <ScrollArea className="flex-1 w-full overflow-y-auto mt-4">
//                             <div className="aircraft-details-grid mt-4">
//                                 <AircraftDetailItem label="Departure" icon={PlaneTakeoff} value={details.airport.departure_iata || "N/A"} />
//                                 <AircraftDetailItem label="Arrival" icon={PlaneLanding} value={details.airport.arrival_iata || "N/A"} />
//                                 <SeparatorWithText className="aircraft-details-full" text="Aircraft" />
//                                 <AircraftDetailItem label="Type" icon={Tag} value={details.aircraft.iata || "N/A"} />
//                                 <AircraftDetailItem label="24-bit address" icon={Tag} value={details.aircraft.icao24 || "N/A"} />
//                                 <AircraftDetailItem full label="Registration" icon={Tag} value={details.aircraft.registration || "N/A"} />
//                                 <SeparatorWithText className="aircraft-details-full" text="Location" />
//                                 <AircraftDetailItem label="Latitude" icon={GitCommitVertical} value={details.geography.position[0] ? Math.round(details.geography.position[0] * 1000) / 1000 : "N/A"} unit="deg" />
//                                 <AircraftDetailItem label="Longitude" icon={GitCommitHorizontal} value={details.geography.position[1] ? Math.round(details.geography.position[1] * 1000) / 1000 : "N/A"} unit="deg" />
//                                 <AircraftDetailItem label="Baro. altitude" icon={ArrowUpFromLine} value={details.geography.baro_altitude ? Math.round(details.geography.baro_altitude) : "N/A"} unit="m" />
//                                 <AircraftDetailItem label="Heading" icon={(props) => (<CircleArrowOutUpLeft {...props} style={{ transform: `rotate(${details.geography.heading ? details.geography.heading + 45 : 45}deg)` }} />)} value={details.geography.heading ? Math.round(details.geography.heading) : "N/A"} unit="deg" />
//                                 <SeparatorWithText className="aircraft-details-full" text="Speed" />
//                                 <AircraftDetailItem label="Velocity" icon={Gauge} value={details.geography.speed_horizontal ? Math.round(details.geography.speed_horizontal* 1.94384449 * 10) / 10: "N/A"} unit="kts" />
//                                 <AircraftDetailItem label="Vertical speed" icon={MoveVertical} value={details.geography.speed_vertical ? Math.round(details.geography.speed_vertical * 10) / 10 : "N/A"} unit="m/s" />
//                                 <AircraftDetailItem full label="Squawk" icon={RadioTower} value={details.transponder.squawk || "N/A"} />
//                             </div>
//                         </ScrollArea>
//                     </>
//                 ) : (
//                     loadingDetails ? <Skeleton className="h-16 w-full" /> : <p>Could not load aircraft details...</p>
//                 )}
//             </CardContent>
//         </Card>
//     );
// }
