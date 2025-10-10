import { type State } from "@/types/api";
import { getLatestState } from "@/services/api/state";
import { useEffect, useState } from "react";
import { useMapStore } from "@/store/mapStore";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { SmallCard } from "@/components/ui/small-card";


function StateDetailsFetcher({ selectedAircraft, setDetails, setLoading }: { selectedAircraft: string | null, setDetails: (state: State | null) => void, setLoading: (loading: boolean) => void }) {
    useEffect(() => {
        if (!selectedAircraft) {
            setDetails(null);
            setLoading(false);
            return;
        }

        setLoading(true);
        getLatestState(selectedAircraft)
            .then(data => {
                console.log(data);
                setDetails(data);
            })
            .catch((err) => {
                setDetails(null);
                console.error(err);
            })
            .finally(() => setLoading(false));
    }, [selectedAircraft])

    return null;
}

export function StateDetails() {
    const selectedAircraft = useMapStore((state) => state.selectedAircraft);
    const [details, setDetails] = useState<State | null>(null);
    const [loading, setLoading] = useState<boolean>(false);

    return (
        <>
            <StateDetailsFetcher selectedAircraft={selectedAircraft} setDetails={setDetails} setLoading={setLoading} />
            <ScrollArea className="flex-1 overflow-y-auto p-2">
                <div className="items-center gap-2">
                    <p>Test</p>
                    <p>More test</p>
                </div>
                <SmallCard text="hello" description="more text here..." />
                {/* <Card className="w-full">
                    <CardHeader>
                        <CardTitle>{loading  && selectedAircraft}</CardTitle>
                        <CardDescription>{details?.flight.icao || ""}</CardDescription>
                    </CardHeader>
                </Card> */}
            </ScrollArea>
        </>
    )
}
