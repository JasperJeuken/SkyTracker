import type { State } from "@/types/api";
import { SmallCard } from "@/components/ui/card-small";
import { useMapStore } from "@/store/mapStore";
import { Hash, Plane } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";

export function MapDetailsHeader({ stateData, loading, error, className }: {stateData: State | null, loading: boolean, error: string | null, className?: string}) {
    const selectedAircraft = useMapStore((state) => state.selectedAircraft);
    return (
        <div className={`flex items-center gap-1.5 ${className}`}>
            {loading && !error && <Skeleton className="h-10 w-20"/>}
            {!loading && (error || !stateData) && <SmallCard text="Failed to load data..." className="h-10 !px-4" />}
            {!loading && stateData && (
                <>
                    <SmallCard text={selectedAircraft ?? ""} tooltip="Callsign" className="h-10 !px-4 font-bold text-lg" variant="accent"/>
                    {stateData?.flight.number && <SmallCard text={stateData?.flight.number ?? ""} tooltip="Flight number" className="h-10" icon={Hash} />}
                    {stateData?.aircraft.icao && <SmallCard text={stateData?.aircraft.icao ?? ""} tooltip="Aircraft type" className="h-10" icon={Plane} />}
                </>
            )}
            
        </div>
    )   
}