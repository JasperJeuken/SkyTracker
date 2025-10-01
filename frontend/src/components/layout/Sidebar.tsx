import { motion, AnimatePresence } from "motion/react";
import { AircraftDetails } from "../AircraftDetails";
import { useAircraftMap } from "../AircraftMapProvider";


export function Sidebar() {
    const { selectedAircraft, sidebarOpen } = useAircraftMap();
    return (
        <AnimatePresence>
            {sidebarOpen && (
                <motion.aside
                    initial={{ x: -260, opacity: 0 }}
                    animate={{ x: 0, opacity: 1 }}
                    exit={{ x: -260, opacity: 0 }}
                    transition={{ type: "tween", duration: 0.3 }}
                    className="absolute top-0 left-0 h-full w-100 border-r bg-white/70 backdrop-blur-md shadow-lg z-50 p-4 dark:bg-gray-800/80 flex flex-col"
                >
                    {selectedAircraft && <AircraftDetails showImages />}
                </motion.aside>
            )}
        </AnimatePresence>
    );
}
