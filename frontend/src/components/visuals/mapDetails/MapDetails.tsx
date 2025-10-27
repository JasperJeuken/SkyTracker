import { useMapStore } from "@/store/mapStore";
import { ScrollArea } from "@/components/ui/scroll-area";
import { MapDetailsAirport } from "./MapDetailsAirport";
import { MapDetailsImages } from "./MapDetailsImages";
import { MapDetailsHeader } from "./MapDetailsHeader";
import { MapDetailsAccordion } from "./MapDetailsAccordion";


export function MapDetails() {
    const details = useMapStore((state) => state.details);

    return (
        <ScrollArea className="flex-1 overflow-y-auto">
            <div className="p-4">
                <MapDetailsHeader data={details.state} className="mb-3" />
                <MapDetailsImages data={details.photos} className="mb-3" />
                <MapDetailsAirport data={{state: details.state, airport: details.airport}} className="mb-3 depth-medium" />
                <MapDetailsAccordion data={details} />
            </div>
        </ScrollArea>
    );
}
