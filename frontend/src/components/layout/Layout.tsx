import { useLocation } from "react-router-dom";
import { Header } from "./Header";
import { useEffect, useRef, useState } from "react";


export default function Layout({ children }: { children: React.ReactNode }) {
    const location = useLocation();
    const isHomepage = location.pathname == "/";
    const [headerHeight, setHeaderHeight] = useState(0);
    const headerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (headerRef.current) {
            setHeaderHeight(headerRef.current.offsetHeight);
        }

        const handleResize = () => {
            if (headerRef.current) {
                setHeaderHeight(headerRef.current.offsetHeight);
            }
        };
        window.addEventListener("resize", handleResize);
        return () => window.removeEventListener("resize", handleResize);
    }, [])

    return (
        <div className="flex flex-col min-h-screen bg-gray-100 dark:bg-gray-900 text-gray-900 dark:text-gray-100">
            <Header ref={headerRef} />
            <main className={`flex-1 overflow-y-auto p-4`} style={{ paddingTop: isHomepage ? 0 : headerHeight }}>{children}</main>
        </div>
    );
}
