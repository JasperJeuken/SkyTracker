import { ThemeToggle } from "@/components/ui/themeToggle";
import { Link, NavLink, useLocation } from "react-router-dom";
import { NavigationMenu, NavigationMenuContent, NavigationMenuItem,
    NavigationMenuLink, NavigationMenuList, NavigationMenuTrigger,
    navigationMenuTriggerStyle } from "@/components/ui/navigation-menu";
import { type LucideIcon, Plane, TowerControl, TicketsPlane, Search, Code } from "lucide-react";


export function Header() {
    const location = useLocation();
    const isHomepage = location.pathname == "/";

    const searchComponents: { title: string; href: string; description: string; icon: LucideIcon}[] = [
        {
            title: "Aircraft",
            href: "/search",
            description: "Search for data about a specific aircraft",
            icon: Plane,
        },
        {
            title: "Airline",
            href: "/search",
            description: "Search for data about a specific airline",
            icon: TicketsPlane,
        },
        {
            title: "Airport",
            href: "/search",
            description: "Search for data about a specific airport",
            icon: TowerControl,
        },
    ];

    return (
        <header className={`fixed top-0 left-0 right-0 z-20 flex items-center justify-between px-4 py-2 border-b shadow-sm ${isHomepage ? "bg-gray-100/70 dark:bg-gray-900/70 backdrop-blur-md" : "bg-gray-100 dark:bg-gray-900"}`}>
            <div className="flex items-center gap-8">
                {/* Logo */}
                <Link to="/" className="flex items-center gap-2">
                    <img src="logo.svg" alt="Logo" className="h-8 w-8" />
                    <span className="text-xl font-semibold">SkyTracker</span>
                </Link>

                {/* Navigation */}
                <NavigationMenu>
                    <NavigationMenuList>
                        {/* Home */}
                        <NavigationMenuItem>
                            <NavLink to="/">
                                <NavigationMenuLink className="bg-gray-200 hover:bg-gray-300 dark:bg-gray-800 dark:hover:bg-gray-700 rounded-sm">
                                    Home
                                </NavigationMenuLink>
                            </NavLink>
                        </NavigationMenuItem>
                        {/* About */}
                        <NavigationMenuItem>
                            <NavLink to="/about">
                                <NavigationMenuLink className="bg-gray-200 hover:bg-gray-300 dark:bg-gray-800 dark:hover:bg-gray-700 rounded-sm">
                                    About
                                </NavigationMenuLink>
                            </NavLink>
                        </NavigationMenuItem>
                        {/* Search */}
                        <NavigationMenuItem>
                            <NavigationMenuTrigger className="bg-gray-200 hover:bg-gray-300 dark:bg-gray-800 dark:hover:bg-gray-700 rounded-sm">Search</NavigationMenuTrigger>
                            <NavigationMenuContent>
                                <ul className="grid gap-2 md:w-[400px] lg:w-[500px] lg:grid-cols-[.75fr_1fr]">
                                    <li className="row-span-3">
                                        <NavigationMenuLink asChild>
                                            <NavLink to="/search" className="from-muted/50 to-muted flex h-full w-full flex-col justify-end rounded-md bg-linear-to-b p-6 no-underline outline-hidden select-none focus:shadow-md">
                                                <div className="mt-4 mb-2 text-lg font-medium flex items-center gap-2">
                                                    <Search className="h-6 w-6" />
                                                    Search
                                                </div>
                                                <p className="text-muted-foreground text-sm leading-tight">
                                                    Search for specific data
                                                </p>
                                            </NavLink>
                                        </NavigationMenuLink>
                                    </li>
                                    {searchComponents.map((component) => (
                                        <ListItem key={component.title} title={component.title} href={component.href} icon={component.icon}>
                                            {component.description}
                                        </ListItem>
                                    ))}
                                </ul>
                            </NavigationMenuContent>
                        </NavigationMenuItem>
                    </NavigationMenuList>
                </NavigationMenu>
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
}


function ListItem({ title, children, href, icon: Icon, ...props }: React.ComponentPropsWithoutRef<"li"> & { href: string, icon: LucideIcon }) {
    return (
        <li {...props}>
            <NavigationMenuLink asChild>
                <NavLink to={href}>
                    <div className="text-sm leading-none font-medium tracking-tight flex items-center gap-2">
                        <Icon className="h-5 w-5" />
                        {title}
                    </div>
                    <p className="text-muted-foreground line-clamp-2 text-sm leading-snug">
                        {children}
                    </p>
                </NavLink>
            </NavigationMenuLink>
        </li>
    );
}
