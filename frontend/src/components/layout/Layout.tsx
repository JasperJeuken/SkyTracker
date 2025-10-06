import { useLocation } from "react-router-dom";
import { Header } from "./Header";
import { useEffect, useRef } from "react";
import { useAppStore } from "@/store/appStore";


export default function Layout({ children }: { children: React.ReactNode }) {
    const location = useLocation();
    const isHomepage = location.pathname == "/";
    const headerHeight = useAppStore((state) => state.headerHeight);
    const setHeaderHeight = useAppStore((state) => state.setHeaderHeight)
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
            <main className={`relative flex-1 overflow-hidden`} style={{ paddingTop: isHomepage ? 0 : headerHeight }}>
                {children}
            </main>
        </div>
    );
}
