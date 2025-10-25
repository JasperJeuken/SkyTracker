import { NavigationMenu, NavigationMenuContent, NavigationMenuItem,
    NavigationMenuLink, NavigationMenuList, NavigationMenuTrigger } from "@/components/ui/navigation-menu";
import { NavLink } from "react-router-dom";
import { type LucideIcon, Plane, TowerControl, TicketsPlane, Search } from "lucide-react";


export function NavMenu() {

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
    const navLinkClass = "bg-gray-300/40 hover:bg-gray-100/40 dark:bg-gray-800/40 dark:hover:bg-gray-700/40 rounded-sm font-medium depth-small px-3";

    return (
        <NavigationMenu>
            <NavigationMenuList>
                {/* Home */}
                <NavigationMenuItem>
                <NavigationMenuLink asChild>
                    <NavLink to="/" className={navLinkClass}>
                        Home
                    </NavLink>
                </NavigationMenuLink>
                </NavigationMenuItem>
                {/* About */}
                <NavigationMenuItem>
                    <NavigationMenuLink asChild>
                        <NavLink to="/about" className={navLinkClass}>
                                About
                        </NavLink>
                    </NavigationMenuLink>
                </NavigationMenuItem>
                {/* Search */}
                <NavigationMenuItem>
                    <NavigationMenuTrigger className={navLinkClass}>Search</NavigationMenuTrigger>
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
