import { ValueCard } from "@/components/ui/card-value";
import { type State } from "@/types/api";
import { ArrowUpFromLine, CircleArrowOutUpLeft, GitCommitHorizontal, GitCommitVertical } from "lucide-react";


export function MapDetailsPosition({ data, loading, error }: { data: State | null, loading: boolean, error: string | null }) {
    const lat = data?.geography.position ? Math.round(data!.geography.position[0] * 1000) / 1000 : "N/A";
    const lon = data?.geography.position ? Math.round(data!.geography.position[1] * 1000) / 1000 : "N/A";
    const heading = data?.geography.heading ? Math.round(data!.geography.heading) : "N/A";
    const altitude = data?.geography.baro_altitude ? Math.round(data!.geography.baro_altitude) : "N/A";
    return (
        <div className="flex flex-col gap-3">
            <div className="w-full flex gap-3">
                <ValueCard value={lat} loading={loading} unit="deg" label="Latitude" icon={GitCommitVertical} className="!w-[50%]" />
                <ValueCard value={lon} loading={loading} unit="deg" label="Longitude" icon={GitCommitHorizontal} className="!w-[50%]" />
            </div>
            <div className="w-full flex gap-3">
                <ValueCard value={heading} loading={loading} unit="deg" label="Heading" icon={(props) => (<CircleArrowOutUpLeft {...props} style={{ transform: `rotate(${data?.geography.heading ? data!.geography.heading + 45 : 45}deg)` }} />)} className="!w-[50%]" />
                <ValueCard value={altitude} loading={loading} unit="m" label="Barometric altitude" icon={ArrowUpFromLine} className="!w-[50%]" />
            </div>
        </div>
    )
}