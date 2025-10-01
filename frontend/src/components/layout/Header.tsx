import { Button } from "@/components/ui/button";
import { Menu, Sun, Moon } from "lucide-react";
import { cn } from "@/lib/utils"
import { useContext } from "react";
import { ThemeContext } from "./ThemeProvider";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useAircraftMap } from "../AircraftMapProvider";


export function Header() {
    const { theme, toggleTheme } = useContext(ThemeContext);
    const { sidebarOpen, setSidebarOpen, mapStyle, setMapStyle } = useAircraftMap();

    const onToggleSidebar = () => {
        setSidebarOpen(!sidebarOpen);
    };
    
    return (
        <header className={cn(
            "flex items-center justify-between",
            "px-4 py-2 border-b bg-white/80 backdrop-blur-md shadow-sm dark:bg-gray-900/80 dark:text-white")}
        >
            <div className="flex items-center gap-2">
                <Button variant="ghost" size="icon" onClick={onToggleSidebar} aria-label="Toggle sidebar">
                    <Menu className="h-5 w-5" />
                </Button>
                <span className="text-lg font-semibold">SkyTracker</span>
            </div>

            <div className="flex gap-2">
                <Select defaultValue={mapStyle} onValueChange={(val) => setMapStyle(val as "Default" | "Satellite" | "OpenStreetMap")}>
                    <SelectTrigger className="w-full">
                        <SelectValue placeholder="Choose theme" />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="Default">Default</SelectItem>
                        <SelectItem value="Satellite">Satellite</SelectItem>
                        <SelectItem value="OpenStreetMap">OpenStreetmap</SelectItem>
                    </SelectContent>
                </Select>
                <Button variant="outline" size="icon" aria-label="Toggle theme" onClick={toggleTheme}>
                    {theme === "light" ? (
                        <Moon className="h-4 w-4" />
                    ) : (
                        <Sun className="h-4 w-4" />
                    )}
                </Button>
            </div>
        </header>
    );
}
