import type { State } from "@/types/api";
import { SmallCard } from "@/components/ui/card-small";
import { useMapStore } from "@/store/mapStore";
import { Hash, Locate, Plane } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";

export function MapDetailsHeader({ stateData, loading, error, className }: {stateData: State | null, loading: boolean, error: string | null, className?: string}) {
    const selectedAircraft = useMapStore((state) => state.selectedAircraft);
    const map = useMapStore((state) => state.mapRef);

    const recenter = () => {
        if (!map || !stateData || !stateData.geography.position) return;
        map.setView([stateData!.geography.position[0], stateData!.geography.position[1]], 10, { animate: true, duration: 1 });
    }

    return (
        <div className={`flex items-center gap-1.5 ${className} w-full relative`}>
            {loading && !error && <Skeleton className="h-10 w-20"/>}
            {!loading && (error || !stateData) && <SmallCard text="Failed to load data..." className="h-10 !px-4" />}
            {!loading && stateData && (
                <>
                    <SmallCard text={selectedAircraft ?? ""} tooltip="Callsign" className="h-10 !px-4 font-bold text-lg" variant="accent"/>
                    {stateData?.flight.number && <SmallCard text={stateData?.flight.number ?? ""} tooltip="Flight number" className="h-10" icon={Hash} />}
                    {stateData?.aircraft.icao && <SmallCard text={stateData?.aircraft.icao ?? ""} tooltip="Aircraft type" className="h-10" icon={Plane} />}
                    
                    <Tooltip>
                        <TooltipTrigger asChild>
                            <button onClick={recenter} className="absolute right-0 h-10 w-10 p-2 rounded-lg bg-gray-100 hover:bg-gray-200 dark:bg-gray-800 hover:dark:bg-gray-700 cursor-pointer flex items-center justify-center">
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