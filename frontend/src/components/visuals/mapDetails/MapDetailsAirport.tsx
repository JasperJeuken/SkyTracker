import { PlaneLanding, PlaneTakeoff, Route } from "lucide-react";
import { type Airport, type State } from "@/types/api";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { Skeleton } from "@/components/ui/skeleton";
import { useMapStore } from "@/store/mapStore";
import type { Map } from "leaflet";
import ReactCountryFlag from "react-country-flag";


export function MapDetailsAirport({
    data,
    loading,
    error,
    className 
}: {
    data: {state: State | null, airport: {departure: Airport | null, arrival: Airport | null}},
    loading: {state: boolean, airport: boolean}, 
    error: {state: string | null, airport: string | null}, 
    className?: string 
}) {
    const map = useMapStore((state) => state.mapRef);
    const arrivalOnclick = getOnclick({ data: data['airport']['arrival'], loading: loading['airport'], error: error['airport'], map});
    const departureOnclick = getOnclick({ data: data['airport']['departure'], loading: loading['airport'], error: error['airport'], map});
    return (
        <TooltipProvider>
            <div className={`relative flex w-full rounded-2xl shadow-md overflow-hidden text-skytracker-dark dark:text-skytracker-light font-light ${className}`}>
                <Tooltip>
                    <TooltipTrigger asChild>
                        <div className={`flex-1 flex flex-col items-center justify-center p-2 bg-skytracker-light dark:bg-skytracker-dark border-r-1 border-skytracker-dark dark:border-skytracker-light ${data['airport']['arrival'] ? "cursor-pointer" : ""}`} onClick={departureOnclick}>
                            <PlaneTakeoff className="w-7 h-7 mb-1" />
                            {loading['airport'] ? (
                                <Skeleton className="h-4 w-7" />
                            ) : (
                                <div className="flex gap-1 items-center">
                                    {data['airport']['departure']?.country_iso2 && (
                                        <Tooltip>
                                            <TooltipTrigger asChild>
                                                <ReactCountryFlag svg countryCode={data['airport']['departure']!.country_iso2} width="10px" />
                                            </TooltipTrigger>
                                            <TooltipContent className="max-w-xs text-sm" side="bottom">
                                                {data['airport']['departure']!.country_name}
                                            </TooltipContent>
                                        </Tooltip>
                                    )}
                                    <span className="text-lg">{data['state']?.airport.departure_iata ?? "N/A"}</span>
                                </div>
                            )}
                        </div>
                    </TooltipTrigger>
                    <TooltipContent className="max-w-xs text-sm" side="bottom">
                        <AirportTooltip data={data['airport']['departure']} loading={loading['airport']} error={error['airport']} alt="Departure airport" />
                    </TooltipContent>
                </Tooltip>
                <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 bg-skytracker-dark dark:bg-skytracker-light rounded-full p-2 shadow-sm z-10">
                    <Route className="w-6 h-6 text-skytracker-light dark:text-skytracker-dark" />
                </div>
                <Tooltip>
                    <TooltipTrigger asChild>
                        <div className={`flex-1 flex flex-col items-center justify-center p-2 bg-skytracker-light dark:bg-skytracker-dark border-l-1 border-skytracker-dark dark:border-skytracker-light ${data['airport']['departure'] ? "cursor-pointer": ""}`} onClick={arrivalOnclick}>
                            <PlaneLanding className="w-7 h-7 mb-1" />
                            {loading['airport'] ? (
                                <Skeleton className="h-4 w-7" />
                            ) : (
                                <div className="flex gap-1 items-center">
                                    {data['airport']['arrival']?.country_iso2 && (
                                        <Tooltip>
                                            <TooltipTrigger asChild>
                                                <ReactCountryFlag svg countryCode={data['airport']['arrival']!.country_iso2} width="10px" />
                                            </TooltipTrigger>
                                            <TooltipContent className="max-w-xs text-sm" side="bottom">
                                                {data['airport']['arrival']!.country_name}
                                            </TooltipContent>
                                        </Tooltip>
                                    )}
                                    <span className="text-lg">{data['state']?.airport.arrival_iata ?? "N/A"}</span>
                                </div>
                            )}
                        </div>
                    </TooltipTrigger>
                    <TooltipContent className="max-w-xs text-sm" side="bottom">
                        <AirportTooltip data={data['airport']['arrival']} loading={loading['airport']} error={error['airport']} alt="Arrival airport" />
                    </TooltipContent>
                </Tooltip>
            </div>
        </TooltipProvider>
    )
}

function getOnclick({ data, loading, error, map }: { data: Airport | null, loading: boolean, error: string | null, map: Map | null }) {
    if (loading || error || !data) return () => {};
    if (!map || data.latitude == null || data.longitude == null) return () => {};
    return () => {
        map.setView([data.latitude!, data.longitude!], 14, { animate: true, duration: 1 });
    }
}

function AirportTooltip({ data, loading, error, alt }: { data: Airport | null, loading: boolean, error: string | null, alt: string }) {
    if (loading && !error) return <Skeleton className="h-4 w-10" />
    if (!loading && data) return (
        <div className="flex flex-col items-center">
            <span>{data.name}</span>
            <span>({data.iata}/{data.icao})</span>
        </div>
    )
    return <span>{alt}</span>
}
