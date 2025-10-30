import { ValueCard } from "@/components/ui/card-value";
import { useMapStore } from "@/store/mapStore";
import { type Loadable, type State } from "@/types/api";
import { ArrowUpFromLine, CircleArrowOutUpLeft, GitCommitHorizontal, GitCommitVertical } from "lucide-react";


export function MapDetailsPosition({ data }: { data: Loadable<State> }) {
    const selected = useMapStore((state) => state.selected);
    const lastState = useMapStore((state) => {
        if (!selected) return null;
        const selectedHistory = state.history;
        if (!selectedHistory || selectedHistory.length == 0) return null;
        return selectedHistory[0];
    });
    const animatedPosition = useMapStore((state) => state.animatedPosition);

    // Get relevant properties
    const animatedLat = animatedPosition[0].toFixed(3);
    const animatedLon = animatedPosition[1].toFixed(3);
    const lat = data.status === "success" ? data.data.geography.position[0].toFixed(3) : "N/A";
    const lon = data.status === "success" ? data.data.geography.position[1].toFixed(3) : "N/A";
    const heading = lastState ? (lastState.heading ? Math.round(lastState.heading) : "N/A") : "N/A";
    const altitudeData = lastState ? lastState.altitude : null;
    const altitude = altitudeData ? Math.round(altitudeData) : "N/A";

    return (
        <div className="flex flex-col gap-3">
            <div className="w-full flex gap-3">
                <ValueCard value={animatedLat} loading={lastState == null} unit="deg" label="Latitude" icon={GitCommitVertical} className="!w-[50%] depth-medium-reverse" tooltip description="Specifies the north-south position, between -90° and 90°." alternatives={data.status === "success" ? [`Last known: ${lat} deg`] : []} />
                <ValueCard value={animatedLon} loading={lastState == null} unit="deg" label="Longitude" icon={GitCommitHorizontal} className="!w-[50%] depth-medium-reverse" tooltip description="Specifies the east-west position, between -180° and 180°." alternatives={data.status === "success" ? [`Last known: ${lon} deg`] : []} />
            </div>
            <div className="w-full flex gap-3">
                <ValueCard value={heading} loading={lastState == null} unit="deg" label="Heading" icon={(props) => (<CircleArrowOutUpLeft {...props} style={{ transform: `rotate(${lastState ? (lastState.heading ? lastState.heading + 45 : 45) : 45}deg)` }} />)} className="!w-[50%] depth-medium-reverse" tooltip description="Aircraft nose direction, measured in degrees clockwise from north." />
                <ValueCard value={altitude} loading={lastState == null} unit="m" label="Barometric altitude" icon={ArrowUpFromLine} className="!w-[50%] depth-medium-reverse" tooltip description="Height above sea level, measured through atmospheric pressure." alternatives={altitudeData ? [Math.round(altitudeData / 0.3048) + " ft", "FL" + Math.round(altitudeData / 0.3048 / 100)] : []} />
            </div>
        </div>
    )
}