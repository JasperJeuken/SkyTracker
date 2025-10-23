import { motion, AnimatePresence } from "motion/react";
import { useMapStore } from "@/store/mapStore";
import { useAppStore } from "@/store/appStore";
import { MapDetails } from "@/components/visuals/mapDetails/MapDetails";


export function Sidebar() {
    const sidebarOpen = useMapStore((state) => state.sidebarOpen);
    const selectedAircraft = useMapStore((state) => state.selected)
    const headerHeight = useAppStore((state) => state.headerHeight);
    return (
        <AnimatePresence>
            {sidebarOpen && (
                <motion.aside
                    initial={{ x: -260, opacity: 0 }}
                    animate={{ x: 0, opacity: 1 }}
                    exit={{ x: -260, opacity: 0 }}
                    transition={{ type: "tween", duration: 0.3 }}
                    className="absolute top-0 left-0 h-full w-100 border-r bg-white/70 backdrop-blur-md shadow-lg z-50 p-4 dark:bg-gray-800/80 flex flex-col"
                    style={{ marginTop: headerHeight - 1, padding: 0 }}
                >
                    {selectedAircraft && (
                        <MapDetails />
                    )}
                </motion.aside>
            )}
        </AnimatePresence>
    );
}
