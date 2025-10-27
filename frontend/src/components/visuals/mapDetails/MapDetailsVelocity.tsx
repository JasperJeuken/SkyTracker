import { ValueCard } from "@/components/ui/card-value";
import { type Loadable, type State } from "@/types/api";
import { Gauge, ArrowUpFromLine, ArrowDownFromLine, Minus } from "lucide-react";
import { getMachNumber } from "@/utils/atmosphere";


export function MapDetailsVelocity({ data }: { data: Loadable<State> }) {

    // Get relevant properties
    const horizontalData = data.status === "success" ? data.data.geography.speed_horizontal : null;
    const verticalData = data.status === "success" ? data.data.geography.speed_vertical : null;
    const altitudeData = data.status === "success" ? data.data.geography.baro_altitude : null;
    const velocityHorizontal = horizontalData ? horizontalData.toFixed(1) : "N/A";
    const velocityVertical = verticalData ? (verticalData > 0 ? "+" + verticalData.toFixed(1) : verticalData.toFixed(1)) : "N/A";
    const verticalIcon = (() => {
        if (verticalData && verticalData > 0) return ArrowUpFromLine;
        if (verticalData && verticalData < 0) return ArrowDownFromLine;
        return Minus;
    })();

    // Calculate alternative units
    const horizontalAlternatives = horizontalData ? [
        (horizontalData * 3.6).toFixed(1) + " km/h",
        (horizontalData / 0.514444444).toFixed(1) + " kts",
        (horizontalData / 0.44704).toFixed(1) + " mph",
        "Mach " + (horizontalData * 0.0029136).toFixed(2) + " (sea-level)"
    ] : [];
    if (altitudeData && horizontalData) {
        horizontalAlternatives.push(`Mach ${getMachNumber(altitudeData, horizontalData).toFixed(2)} (ISA @ ${Math.round(altitudeData)}m)`)
    }
    const verticalAlternatives = verticalData ? [
        (verticalData * 3.6).toFixed(1) + " km/h",
        (verticalData / 0.514444444).toFixed(1) + " kts",
        (verticalData / 0.44704).toFixed(1) + " mph",
        Math.round(verticalData * 196.850394) + " ft/min"
    ] : [];

    return (
        <div className="flex flex-col gap-3">
            <div className="w-full flex gap-3">
                <ValueCard value={velocityHorizontal} loading={data.status === "loading"} unit="m/s" label="Horizontal" icon={Gauge} className="!w-[50%] depth-medium-reverse" tooltip longLabel="Horizontal velocity" description="Horizontal component of velocity relative to the ground, ground speed." alternatives={horizontalData ? horizontalAlternatives : []} />
                <ValueCard value={velocityVertical} loading={data.status === "loading"} unit="m/s" label="Vertical" icon={verticalIcon} className="!w-[50%] depth-medium-reverse" tooltip longLabel="Vertical velocity" description="Vertical component of velocity, indicates climb (+) or descent (-)." alternatives={verticalAlternatives} />
            </div>
        </div>
    )
}