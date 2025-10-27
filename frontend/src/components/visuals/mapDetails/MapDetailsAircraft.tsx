import { ValueCard } from "@/components/ui/card-value";
import { Separator } from "@/components/ui/separator";
import { Timeline } from "@/components/ui/timeline";
import { type Aircraft, type Loadable, type State } from "@/types/api";
import { Tag, BookOpen, User, PenLine, Truck, Factory, Plane, Fan, SquareStack, PlaneTakeoff } from "lucide-react";


export function MapDetailsAircraft({ data }: { data: {state: Loadable<State>, aircraft: Loadable<Aircraft>} }) {

    // Get relevant properties
    const icao24 = data.state.status === "success" ? data.state.data.aircraft.icao24 : null;
    const registration = data.state.status === "success" ? data.state.data.aircraft.registration : null;
    const owner = data.aircraft.status === "success" ? data.aircraft.data.identity.owner : null;
    const model = data.aircraft.status === "success" ? data.aircraft.data.model.type_iata : null;
    const family = data.aircraft.status === "success" ? data.aircraft.data.model.sub_family : null;
    const engineCount = data.aircraft.status === "success" ? data.aircraft.data.model.engine_count : null;
    const dateDeliveryData = data.aircraft.status === "success" ? data.aircraft.data.lifecycle.date_delivery : null;
    const dateRolloutData = data.aircraft.status === "success" ? data.aircraft.data.lifecycle.date_rollout : null;
    const dateRegistrationData = data.aircraft.status === "success" ? data.aircraft.data.lifecycle.date_registration : null;
    const dateFirstFlightData = data.aircraft.status === "success" ? data.aircraft.data.lifecycle.date_first_flight : null;
    const dateDelivery = dateDeliveryData ? new Date(dateDeliveryData).toLocaleDateString() : "N/A";
    const dateRollout = dateRolloutData ? new Date(dateRolloutData).toLocaleDateString() : "N/A";
    const dateRegistration = dateRegistrationData ? new Date(dateRegistrationData).toLocaleDateString() : "N/A";
    const dateFirstFlight = dateFirstFlightData ? new Date(dateFirstFlightData).toLocaleDateString() : "N/A";

    const dateEvents = [
        { date: new Date("1970-01-01") },
        { date: new Date("1990-01-01") },
        { date: new Date("1991-01-01") },
        { date: new Date("2025-01-01") },
    ]

    return (
        <>
            <div className="flex flex-col gap-3">
                <div className="w-full flex gap-3">
                    <ValueCard value={icao24 ?? "N/A"} loading={data.state.status === "loading"} label="ICAO24" icon={Tag} className="!w-[50%] depth-medium-reverse" tooltip longLabel="ICAO 24-bit address" description="Unique 24-bit identifier (hexadecimal) for an aircraft, issued by ICAO." />
                    <ValueCard value={registration ?? "N/A"} loading={data.state.status === "loading"} label="Registration" icon={BookOpen} className="!w-[50%] depth-medium-reverse" tooltip description="Unique code for an aircraft, issued by a civil aviation authority." />
                </div>
                <Timeline events={dateEvents} />
                {data.aircraft.status === "success" && (<>
                    <div className="w-full flex gap-3">
                        <ValueCard fullWidth value={owner ?? "N/A"} label="Owner" icon={User} className="depth-medium-reverse" tooltip longLabel="Aircraft owner" description="Owner of the aircraft." />
                    </div>
                    <div className="w-full flex gap-3">
                        <ValueCard value={model ?? "N/A"} label="Model" icon={Plane} className="!w-[50%] depth-medium-reverse" tooltip longLabel="Aircraft model" description="Designator of the model of the aircraft." />
                        <ValueCard value={engineCount ?? "N/A"} label="# engines" icon={Fan} className="!w-[50%] depth-medium-reverse" tooltip longLabel="Number of engines" description="Number of engines the aircraft has." />
                    </div>
                    <div className="w-full flex gap-3">
                        <ValueCard fullWidth value={family ?? "N/A"} label="Family" icon={SquareStack} className="depth-medium-reverse" tooltip longLabel="Aircraft family" description="Name of aircraft family from manufacturer." />
                    </div>
                    <Separator />
                    <div className="w-full flex gap-3">
                        <ValueCard value={dateDelivery} label="Delivery" icon={Truck} className="!w-[50%] depth-medium-reverse" tooltip longLabel="Date of delivery" description="Date the manufacturer delivered the aircraft to the operator." />
                        <ValueCard value={dateRegistration} label="Registration" icon={PenLine} className="!w-[50%] depth-medium-reverse" tooltip longLabel="Date of registration" description="Date on which the aircraft was registered, usually corresponding to a change of ownership. " />
                    </div>
                    <div className="w-full flex gap-3">
                        <ValueCard value={dateRollout} label="Rollout" icon={Factory} className="!w-[50%] depth-medium-reverse" tooltip longLabel="Date of rollout" description="Date on which the aircraft was first completed by the manufacturer." />
                        <ValueCard value={dateFirstFlight} label="First flight" icon={PlaneTakeoff} className="!w-[50%] depth-medium-reverse" tooltip longLabel="Date of first flight" description="Date on which the aircraft flew for the first time." />
                    </div>
                </>)}
            </div>
        </>
    )
}