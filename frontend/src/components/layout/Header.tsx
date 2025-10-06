import { ThemeToggle } from "@/components/ui/theme-toggle";
import { Link, useLocation } from "react-router-dom";
import { Code } from "lucide-react";
import { NavMenu } from "@/components/layout/NavMenu";
import { forwardRef } from "react";


export const Header = forwardRef<HTMLDivElement>((props, ref) => {
    const location = useLocation();
    const isHomepage = location.pathname == "/";

    return (
        <header ref={ref} className={`fixed top-0 left-0 right-0 z-20 flex items-center justify-between px-4 py-2 border-b shadow-sm ${isHomepage ? "bg-gray-100/70 dark:bg-gray-900/70 backdrop-blur-md" : "bg-gray-100 dark:bg-gray-900"}`} {...props}>
            <div className="flex items-center gap-8">
                {/* Logo */}
                <Link to="/" className="flex items-center gap-2">
                    <img src="logo.svg" alt="Logo" className="h-8 w-8" />
                    <span className="text-xl font-semibold">SkyTracker</span>
                </Link>

                {/* Navigation */}
                <NavMenu />
            </div>

            {/* Icon buttons */}
            <div className="flex items-center gap-2">
                <Link to="https://github.com/JasperJeuken/SkyTracker">
                    <button className="p-2 rounded-lg bg-gray-100 hover:bg-gray-200 dark:bg-gray-800 hover:dark:bg-gray-700">
                        <Code className="h-4 w-4" />
                    </button>
                </Link>
                <ThemeToggle />
            </div>
        </header>
    );
});
