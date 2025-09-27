import React, { type ReactNode, useEffect, useState } from "react";


export function ThemeProvider({ children }: { children: ReactNode }) {
    const [theme, setTheme] = useState<"light" | "dark">(() => {
        return (localStorage.getItem("theme") as "light" | "dark") || "dark";
    });

    useEffect(() => {
        const root = window.document.documentElement;
        if (theme === "dark") {
            root.classList.add("dark");
        } else {
            root.classList.remove("dark");
        }
        localStorage.setItem('theme', theme);
    }, [theme]);

    const toggleTheme = () => {
        setTheme((prev) => (prev === "light" ? "dark" : "light"));
    };

    return (
        <ThemeContext.Provider value={{ theme, toggleTheme }}>
            {children}
        </ThemeContext.Provider>
    );
}


export const ThemeContext = React.createContext<{
    theme: "light" | "dark";
    toggleTheme: () => void;
}>({
    theme: "light",
    toggleTheme: () => {}
});
