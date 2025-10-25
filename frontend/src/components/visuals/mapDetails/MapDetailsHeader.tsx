import type { Loadable, State } from "@/types/api";
import { SmallCard } from "@/components/ui/card-small";
import { useMapStore } from "@/store/mapStore";
import { Hash, Locate, Plane } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";


export function MapDetailsHeader({ data, className }: {data: Loadable<State>, className?: string}) {
    const selectedAircraft = useMapStore((state) => state.selected);
    const currentPosition = useMapStore((state) => state.selectedPosition);
    const map = useMapStore((state) => state.mapRef);

    const recenter = () => {
        if (!map || data.status != "success") return;
        map.setView([currentPosition[0], currentPosition[1]], 10, { animate: true, duration: 0 });
    }

    return (
        <div className={`flex items-center gap-1.5 ${className} w-full relative`}>
            {data.status === "loading" && <Skeleton className="h-10 w-20"/>}
            {data.status === "error" && <SmallCard text="Failed to load data..." className="h-10 !px-4" />}
            {data.status === "success" && (
                <>
                    <SmallCard text={selectedAircraft ?? ""} tooltip="Callsign" className="h-10 !px-4 font-bold text-lg depth-small" variant="accent"/>
                    {data.data.flight.number && <SmallCard text={data.data.flight.number ?? ""} tooltip="Flight number" className="h-10 depth-small" icon={Hash} />}
                    {data.data.aircraft.icao && <SmallCard text={data.data.aircraft.icao ?? ""} tooltip="Aircraft type" className="h-10 depth-small" icon={Plane} />}
                    
                    <Tooltip>
                        <TooltipTrigger asChild>
                            <button onClick={recenter} className="absolute right-0 h-10 w-10 p-2 rounded-lg bg-gray-100 hover:bg-gray-200 dark:bg-gray-800 hover:dark:bg-gray-700 cursor-pointer flex items-center justify-center depth-small hover:depth-large">
                                <Locate className="h-5 w-5" />
                            </button>
                        </TooltipTrigger>
                        <TooltipContent side="bottom">
                            Recenter
                        </TooltipContent>
                    </Tooltip>
                </>
            )}
        </div>
    )
}
