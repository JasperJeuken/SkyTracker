import { PlaneLanding, PlaneTakeoff, Route } from "lucide-react";
import { type State } from "@/types/api";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";


export function AirportCard({ data, className }: { data: State | null, className?: string }) {
    return (
        <TooltipProvider>
            <div className={`relative flex w-full rounded-2xl shadow-md overflow-hidden text-skytracker-dark dark:text-skytracker-light font-light ${className}`}>
                <Tooltip>
                    <TooltipTrigger asChild>
                        <div className="flex-1 flex flex-col items-center justify-center p-2 bg-skytracker-light dark:bg-skytracker-dark border-r-1 border-skytracker-dark dark:border-skytracker-light">
                            <PlaneTakeoff className="w-7 h-7 mb-1" />
                            <span className="text-lg">{data?.airport.departure_iata ?? "N/A"}</span>
                        </div>
                    </TooltipTrigger>
                    <TooltipContent className="max-w-xs text-sm" side="bottom">
                        Departure airport
                    </TooltipContent>
                </Tooltip>
                <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 bg-skytracker-dark dark:bg-skytracker-light rounded-full p-2 shadow-sm z-10">
                    <Route className="w-6 h-6 text-skytracker-light dark:text-skytracker-dark" />
                </div>
                <Tooltip>
                    <TooltipTrigger asChild>
                        <div className="flex-1 flex flex-col items-center justify-center p-2 bg-skytracker-light dark:bg-skytracker-dark border-l-1 border-skytracker-dark dark:border-skytracker-light">
                            <PlaneLanding className="w-7 h-7 mb-1" />
                            <span className="text-lg">{data?.airport.arrival_iata ?? "N/A"}</span>
                        </div>
                    </TooltipTrigger>
                    <TooltipContent className="max-w-xs text-sm" side="bottom">
                        Arrival airport
                    </TooltipContent>
                </Tooltip>
            </div>
        </TooltipProvider>
    )
}
