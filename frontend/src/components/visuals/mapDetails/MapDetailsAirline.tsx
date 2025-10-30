import { ValueCard } from "@/components/ui/card-value";
import { type Airline, type Loadable, type State } from "@/types/api";
import { TicketsPlane, Hash } from "lucide-react";


export function MapDetailsAirline({ data }: { data: {state: Loadable<State>, airline: Loadable<Airline>} }) {

    // Get relevant properties
    const name = data.airline.status === "success" ? data.airline.data.name : null;
    const code = data.state.status === "success" ? data.state.data.airline.icao : null;
    
    return (
        <div className="flex flex-col gap-3">
            <div className="w-full flex gap-3">
                <ValueCard value={name ?? "N/A"} loading={data.airline.status === "loading"} label="Name" icon={TicketsPlane} className="!w-[50%] depth-medium-reverse" tooltip longLabel="Airline name" description="Name of the airline." />
                <ValueCard value={code ?? "N/A"} loading={data.state.status === "loading"} label="ICAO" icon={Hash} className="!w-[50%] depth-medium-reverse" tooltip longLabel="Airline ICAO code" description="Designator for the airline, issued by ICAO." />
            </div>
        </div>
    )
}