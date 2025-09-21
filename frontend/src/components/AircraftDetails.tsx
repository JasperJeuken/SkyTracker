import { X } from "lucide-react";
import { useAircraftMap } from "./AircraftMapProvider";
import { Card, CardAction, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";


export function AircraftDetails() {
    const { selectedAircraft, setSelectedAircraft } = useAircraftMap();

    const onDeselect = () => {
        setSelectedAircraft(null);
    };

    return (
        <Card>
            <CardHeader>
                <CardTitle>Selected aircraft</CardTitle>
                <CardDescription>Info</CardDescription>
                <CardAction>
                    <Button variant="ghost" size="icon" onClick={onDeselect} aria-label="Deselect">
                        <X className="h-4 w-4" />
                    </Button>
                </CardAction>
            </CardHeader>
            <CardContent>
                <p>{selectedAircraft}</p>
            </CardContent>
        </Card>
    );
}
