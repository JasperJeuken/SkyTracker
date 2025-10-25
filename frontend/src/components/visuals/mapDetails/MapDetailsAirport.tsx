import { PlaneLanding, PlaneTakeoff, Route } from "lucide-react";
import { type Airport, type Loadable, type State } from "@/types/api";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { Skeleton } from "@/components/ui/skeleton";
import { useMapStore } from "@/store/mapStore";
import type { Map } from "leaflet";
import ReactCountryFlag from "react-country-flag";


export function MapDetailsAirport({
    data,
    className 
}: {
    data: {state: Loadable<State>, airport: { departure: Loadable<Airport>, arrival: Loadable<Airport> }},
    className?: string 
}) {
    const map = useMapStore((state) => state.mapRef);
    const arrivalOnclick = getOnclick({ data: data['airport']['arrival'], map});
    const departureOnclick = getOnclick({ data: data['airport']['departure'], map});
    return (
        <TooltipProvider>
            <div className={`relative flex w-full rounded-2xl overflow-hidden bg-skytracker-light dark:bg-skytracker-dark text-skytracker-dark dark:text-skytracker-light font-medium dark:font-light ${className}`}>
                <Tooltip>
                    <TooltipTrigger asChild>
                        <div className={`flex-1 flex flex-col items-center justify-center p-2 border-r-1 border-skytracker-dark dark:border-skytracker-light ${data.airport.departure.status === "success" ? "cursor-pointer" : ""}`} onClick={departureOnclick}>
                            <PlaneTakeoff className="w-7 h-7 mb-1" />
                            <div className="flex gap-1 items-center">
                                {data.airport.departure.status === "success" && data.airport.departure.data.country_iso2 && (
                                    <Tooltip>
                                        <TooltipTrigger asChild>
                                            <ReactCountryFlag svg countryCode={data.airport.departure.data.country_iso2} width="10px" />
                                        </TooltipTrigger>
                                        <TooltipContent className="max-w-xs text-sm" side="bottom">
                                            {data.airport.departure.data.country_name}
                                        </TooltipContent>
                                    </Tooltip>
                                )}
                                {data.state.status === "loading" && <Skeleton className="h-4 w-7" /> }
                                {(data.state.status === "error" || data.state.status === "idle") && <span>N/A</span> }
                                {data.state.status === "success" && <span className="text-lg">{data.state.data.airport.departure_iata ?? "N/A"}</span> }
                            </div>
                        </div>
                    </TooltipTrigger>
                    <TooltipContent className="max-w-xs text-sm" side="bottom">
                        <AirportTooltip data={data.airport.departure} alt="Departure airport" />
                    </TooltipContent>
                </Tooltip>
                <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 bg-skytracker-dark dark:bg-skytracker-light rounded-full p-2 shadow-sm z-10 depth-medium-reverse">
                    <Route className="w-6 h-6 text-skytracker-light dark:text-skytracker-dark" />
                </div>
                <Tooltip>
                    <TooltipTrigger asChild>
                        <div className={`flex-1 flex flex-col items-center justify-center p-2 border-skytracker-dark dark:border-skytracker-light ${data.airport.arrival.status === "success" ? "cursor-pointer" : ""}`} onClick={arrivalOnclick}>
                            <PlaneLanding className="w-7 h-7 mb-1" />
                            <div className="flex gap-1 items-center">
                                {data.airport.arrival.status === "success" && data.airport.arrival.data.country_iso2 && (
                                    <Tooltip>
                                        <TooltipTrigger asChild>
                                            <ReactCountryFlag svg countryCode={data.airport.arrival.data.country_iso2} width="10px" />
                                        </TooltipTrigger>
                                        <TooltipContent className="max-w-xs text-sm" side="bottom">
                                            {data.airport.arrival.data.country_name}
                                        </TooltipContent>
                                    </Tooltip>
                                )}
                                {data.state.status === "loading" && <Skeleton className="h-4 w-7" /> }
                                {(data.state.status === "error" || data.state.status === "idle") && <span>N/A</span> }
                                {data.state.status === "success" && <span className="text-lg">{data.state.data.airport.arrival_iata ?? "N/A"}</span> }
                            </div>
                        </div>
                    </TooltipTrigger>
                    <TooltipContent className="max-w-xs text-sm" side="bottom">
                        <AirportTooltip data={data.airport.arrival} alt="Arrival airport" />
                    </TooltipContent>
                </Tooltip>
            </div>
        </TooltipProvider>
    )
}

function getOnclick({ data, map }: { data: Loadable<Airport>, map: Map | null }) {
    if (data.status !== "success") return () => {};
    if (!map || data.data.latitude == null || data.data.longitude == null) return () => {};
    return () => {
        map.setView([data.data.latitude!, data.data.longitude!], 14, { animate: true, duration: 1 });
    }
}

function AirportTooltip({ data, alt }: { data: Loadable<Airport>, alt: string }) {
    if (data.status === "loading") return <Skeleton className="h-4 w-10" />;
    if (data.status === "error" || data.status === "idle") return <span>{alt}</span>
    return <div className="flex flex-col items-center">
        <span>{data.data.name}</span>
        <span>({data.data.iata}/{data.data.icao})</span>
    </div>
}
