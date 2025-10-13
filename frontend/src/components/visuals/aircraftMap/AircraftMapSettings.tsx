import { useAppStore } from "@/store/appStore";
import { Button } from "@/components/ui/button";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Settings2 } from "lucide-react";
import { MapStyleSelect } from "@/components/ui/map-style-select";

export function AircraftMapSettings() {
    const headerHeight = useAppStore((state) => state.headerHeight);

    return (
        <div className="absolute right-4 z-1000" style={{ top: headerHeight + 12 }}>
            <Popover>
                <PopoverTrigger asChild>
                    <Button variant="secondary" size="icon" className="shadow-md backdrop-blur-md bg-gray-100/80 dark:bg-gray-900/80 hover:bg-gray-200/80 hover:dark:bg-gray-800/80 cursor-pointer">
                        <Settings2 className="h-5 w-5" />
                    </Button>
                </PopoverTrigger>

                <PopoverContent align="end" sideOffset={8} className=" w-full bg-white/70 dark:bg-gray-800/70 backdrop-blur-md border border-gray-200 dark:border-gray-700 shadow-xl rounded-xl p-4">
                    <div className="space-y-2">
                        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                            Map style
                        </label>
                        <MapStyleSelect />
                    </div>
                </PopoverContent>
            </Popover>
        </div>
    )
}
