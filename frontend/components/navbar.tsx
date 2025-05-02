"use client";

import { ModeToggle } from "@/components/mode-toggle";
import { cn } from "@/lib/utils";
import Link from "next/link";
import { useEffect, useState } from "react";

export function Navbar() {
    const [scrolled, setScrolled] = useState(false);

    useEffect(() => {
        const handleScroll = () => {
            setScrolled(window.scrollY > 10);
        };
        window.addEventListener("scroll", handleScroll);
        return () => window.removeEventListener("scroll", handleScroll);
    }, []);

    return (
        <header
            className={cn(
                "fixed top-0 z-50 w-full transition-all duration-300",
                scrolled ? "bg-(--background)/80 backdrop-blur-md border-b" : "bg-transparent"
            )}
        >
            <div className="container mx-auto flex h-16 items-center justify-between">
                <Link href="/" className="flex items-center space-x-2 group">
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        className="h-6 w-6 transition-transform duration-700 ease-in-out group-hover:rotate-[360deg]"
                    >
                        <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
                        <polyline points="3.29 7 12 12 20.71 7" />
                        <line x1="12" y1="22" x2="12" y2="12" />
                    </svg>
                    <span className="font-medium text-lg">AgentSphere</span>
                </Link>
                <div className="flex items-center space-x-4">
                    <nav className="h-full hidden md:flex items-center space-x-6">
                        <Link
                            href="#features"
                            className="relative text-sm font-medium transition-all duration-300 hover:text-(--primary) focus:outline-none focus:text-(--primary) group"
                        >
                            <span>Features</span>
                            <span className="absolute -bottom-2 left-0 w-0 h-0.5 bg-(--primary) transition-all duration-300 group-hover:w-full group-focus:w-full"></span>
                        </Link>
                        <Link
                            href="#agents"
                            className="relative text-sm font-medium transition-all duration-300 hover:text-(--primary) focus:outline-none focus:text-(--primary) group"
                        >
                            <span>Agents</span>
                            <span className="absolute -bottom-2 left-0 w-0 h-0.5 bg-(--primary) transition-all duration-300 group-hover:w-full group-focus:w-full"></span>
                        </Link>
                        <Link
                            href="#use-cases"
                            className="relative text-sm font-medium transition-all duration-300 hover:text-(--primary) focus:outline-none focus:text-(--primary) group"
                        >
                            <span>Use Cases</span>
                            <span className="absolute -bottom-2 left-0 w-0 h-0.5 bg-(--primary) transition-all duration-300 group-hover:w-full group-focus:w-full"></span>
                        </Link>
                    </nav>
                    <ModeToggle />
                </div>
            </div>
        </header>
    );
}
