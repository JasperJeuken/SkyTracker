import { ValueCard } from "@/components/ui/card-value";
import { type Loadable, type State } from "@/types/api";
import { ArrowUpFromLine, CircleArrowOutUpLeft, GitCommitHorizontal, GitCommitVertical } from "lucide-react";


export function MapDetailsPosition({ data }: { data: Loadable<State> }) {
    const lat = data.status === "success" ? Math.round(data.data.geography.position[0] * 1000) / 1000 : "N/A";
    const lon = data.status === "success" ? Math.round(data.data.geography.position[1] * 1000) / 1000 : "N/A";
    const heading = data.status === "success" ? (data.data.geography.heading ? Math.round(data.data.geography.heading) : "N/A") : "N/A";
    const altitude = data.status === "success" ? (data.data.geography.baro_altitude ? Math.round(data.data.geography.baro_altitude) : "N/A") : "N/A";
    return (
        <div className="flex flex-col gap-3">
            <div className="w-full flex gap-3">
                <ValueCard value={lat} loading={data.status === "loading"} unit="deg" label="Latitude" icon={GitCommitVertical} className="!w-[50%] depth-medium-reverse" />
                <ValueCard value={lon} loading={data.status === "loading"} unit="deg" label="Longitude" icon={GitCommitHorizontal} className="!w-[50%] depth-medium-reverse" />
            </div>
            <div className="w-full flex gap-3">
                <ValueCard value={heading} loading={data.status === "loading"} unit="deg" label="Heading" icon={(props) => (<CircleArrowOutUpLeft {...props} style={{ transform: `rotate(${data.status === "success" ? (data.data.geography.heading ? data.data.geography.heading + 45 : 45) : 45}deg)` }} />)} className="!w-[50%] depth-medium-reverse" />
                <ValueCard value={altitude} loading={data.status === "loading"} unit="m" label="Barometric altitude" icon={ArrowUpFromLine} className="!w-[50%] depth-medium-reverse" />
            </div>
        </div>
    )
}