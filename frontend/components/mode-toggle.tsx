"use client";

import { Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export function ModeToggle() {
    const { resolvedTheme, setTheme } = useTheme();
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
    }, []);

    const toggleTheme = () => {
        setTheme(resolvedTheme === "dark" ? "light" : "dark");
    };

    if (!mounted) {
        return (
            <Button
                variant="ghost"
                size="icon"
                className="cursor-pointer opacity-0"
                aria-label="Toggle theme"
            >
                <div className="h-[1.2rem] w-[1.2rem]" />
            </Button>
        );
    }

    return (
        <Button
            variant="ghost"
            size="icon"
            className="cursor-pointer hover:bg-(--accent) hover:text-(--accent-foreground) relative overflow-hidden p-0"
            onClick={toggleTheme}
            aria-label="Toggle theme"
        >
            <div className="relative h-9 w-9 flex items-center justify-center">
                <Sun
                    className={cn(
                        "h-[1.2rem] w-[1.2rem] transition-all duration-700 ease-in-out absolute",
                        resolvedTheme === "dark"
                            ? "-rotate-[360deg] scale-0 opacity-0 transform-gpu"
                            : "rotate-0 scale-100 opacity-100 transform-gpu animate-sun-shine"
                    )}
                />
                <Moon
                    className={cn(
                        "h-[1.2rem] w-[1.2rem] transition-all duration-700 ease-in-out absolute",
                        resolvedTheme === "dark"
                            ? "rotate-0 scale-100 opacity-100 transform-gpu animate-moon-glow"
                            : "rotate-[360deg] scale-0 opacity-0 transform-gpu"
                    )}
                />
            </div>
            <span className="sr-only">Toggle theme</span>
        </Button>
    );
}
