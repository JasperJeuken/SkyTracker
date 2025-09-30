import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { motion, AnimatePresence } from "motion/react";
import { AircraftDetails } from "../AircraftDetails";
import { useAircraftMap } from "../AircraftMapProvider";


export function Sidebar() {
    const { mapStyle, setMapStyle, selectedAircraft, sidebarOpen } = useAircraftMap();
    return (
        <AnimatePresence>
            {sidebarOpen && (
                <motion.aside
                    initial={{ x: -260, opacity: 0 }}
                    animate={{ x: 0, opacity: 1 }}
                    exit={{ x: -260, opacity: 0 }}
                    transition={{ type: "tween", duration: 0.3 }}
                    className="absolute top-0 left-0 h-full w-100 border-r bg-white/70 backdrop-blur-md shadow-lg z-50 p-4 dark:bg-gray-800/80"
                >
                    <div className="mb-4">
                        <label className="text-sm font-medium">Map theme</label>
                        <Select defaultValue={mapStyle} onValueChange={(val) => setMapStyle(val as "Default" | "Satellite" | "OpenStreetMap")}>
                            <SelectTrigger className="w-full mt-1">
                                <SelectValue placeholder="Choose theme" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="Default">Default</SelectItem>
                                <SelectItem value="Satellite">Satellite</SelectItem>
                                <SelectItem value="OpenStreetMap">OpenStreetmap</SelectItem>
                            </SelectContent>
                        </Select>
                    </div>

                    <Separator className="mb-4" />

                    <div className="mb-4">
                        {selectedAircraft && <AircraftDetails showImages />}
                    </div>
                </motion.aside>
            )}
        </AnimatePresence>
    );
}
