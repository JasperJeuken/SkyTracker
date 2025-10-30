import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { type SidebarDetails } from "@/types/api";
import { MapDetailsPosition } from "./MapDetailsPosition";
import { MapDetailsVelocity } from "./MapDetailsVelocity";
import { MapDetailsAircraft } from "./MapDetailsAircraft";
import { MapDetailsAirline } from "./MapDetailsAirline";

export function MapDetailsAccordion({data}: {data: SidebarDetails}) {

    return (
        <Accordion type="multiple" className="w-full" defaultValue={["item-position", "item-velocity", "item-aircraft", "item-airline"]} >
            <AccordionItem value="item-position">
                <AccordionTrigger className="hover:cursor-pointer">Position</AccordionTrigger>
                <AccordionContent>
                    <MapDetailsPosition data={data.state} />
                </AccordionContent>
            </AccordionItem>
            <AccordionItem value="item-velocity">
                <AccordionTrigger className="hover:cursor-pointer">Velocity</AccordionTrigger>
                <AccordionContent>
                    <MapDetailsVelocity data={data.state} />
                </AccordionContent>
            </AccordionItem>
            <AccordionItem value="item-aircraft">
                <AccordionTrigger className="hover:cursor-pointer">Aircraft</AccordionTrigger>
                <AccordionContent>
                    <MapDetailsAircraft data={{ state: data.state, aircraft: data.aircraft }} />
                </AccordionContent>
            </AccordionItem>
            <AccordionItem value="item-airline">
                <AccordionTrigger className="hover:cursor-pointer">Airline</AccordionTrigger>
                <AccordionContent>
                    <MapDetailsAirline data={{ state: data.state, airline: data.airline }} />
                </AccordionContent>
            </AccordionItem>
        </Accordion>
    )
}