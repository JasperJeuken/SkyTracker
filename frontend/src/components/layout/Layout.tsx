import { useLocation } from "react-router-dom";
import { Header } from "./Header";


export default function Layout({ children }: { children: React.ReactNode }) {
    const location = useLocation();
    const isHomepage = location.pathname == "/";
    return (
        <div className="flex flex-col min-h-screen bg-gray-100 dark:bg-gray-900 text-gray-900 dark:text-gray-100">
            <Header />
            <main className={`flex-1 overflow-y-auto p-4 ${!isHomepage && "pt-[56px]"}`}>{children}</main>
        </div>
    );
}
