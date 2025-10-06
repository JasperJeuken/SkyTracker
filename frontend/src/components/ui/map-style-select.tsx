import { Select, SelectTrigger, SelectItem, SelectContent, SelectValue } from "@/components/ui/select";
import { useMapStore } from "@/store/mapStore";


export function MapStyleSelect() {
    const mapStyle = useMapStore((state) => state.mapStyle);
    const setMapStyle = useMapStore((state) => state.setMapStyle);

    return (
        <Select defaultValue={mapStyle} onValueChange={(val) => setMapStyle(val as "Default" | "Satellite" | "OpenStreetMap")}>
            <SelectTrigger>
                <SelectValue placeholder="Choose theme" />
            </SelectTrigger>
            <SelectContent>
                <SelectItem value="Default">Default</SelectItem>
                <SelectItem value="Satellite">Satellite</SelectItem>
                <SelectItem value="OpenStreetMap">OpenStreetMap</SelectItem>
            </SelectContent>
        </Select>
    );
}
