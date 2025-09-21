import { X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { motion, AnimatePresence } from "motion/react";


type SidebarProps = {
    open: boolean;
    onClose: () => void;
    mapStyle: "Default" | "Satellite";
    setMapStyle: (style: "Default" | "Satellite") => void;
};


export function Sidebar({ open, onClose, mapStyle, setMapStyle }: SidebarProps) {
    return (
        <AnimatePresence>
            {open && (
                <motion.aside
                    initial={{ x: -260, opacity: 0 }}
                    animate={{ x: 0, opacity: 1 }}
                    exit={{ x: -260, opacity: 0 }}
                    transition={{ type: "tween", duration: 0.3 }}
                    className="absolute top-0 left-0 h-full w-64 border-r bg-white/70 backdrop-blur-md shadow-lg z-50 p-4 dark:bg-gray-800/80"
                >
                    <div className="flex justify-between items-center mb-4">
                        <h2 className="text-md font-semibold">Options</h2>
                        <Button variant="ghost" size="icon" onClick={onClose}>
                            <X className="h-4 w-4" />
                        </Button>
                    </div>

                    <div className="mb-4">
                        <label className="text-sm font-medium">Map theme</label>
                        <Select defaultValue={mapStyle} onValueChange={(val) => setMapStyle(val as "Default" | "Satellite")}>
                            <SelectTrigger className="w-full mt-1">
                                <SelectValue placeholder="Choose theme" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="Default">Default</SelectItem>
                                <SelectItem value="Satellite">Satellite</SelectItem>
                            </SelectContent>
                        </Select>
                    </div>
                </motion.aside>
            )}
        </AnimatePresence>
    );
}
