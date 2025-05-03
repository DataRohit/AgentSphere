"use client";

import { ModeToggle } from "@/components/mode-toggle";
import { cn } from "@/lib/utils";
import { motion, Variants } from "framer-motion";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";

const navVariants: Variants = {
    hidden: { opacity: 0, y: -10 },
    visible: {
        opacity: 1,
        y: 0,
        transition: {
            duration: 0.5,
            ease: "easeOut",
            when: "beforeChildren",
            staggerChildren: 0.1,
        },
    },
};

const itemVariants: Variants = {
    hidden: { opacity: 0, y: -5 },
    visible: {
        opacity: 1,
        y: 0,
        transition: { duration: 0.3 },
    },
};

const logoVariants: Variants = {
    hidden: { opacity: 0, scale: 0.8 },
    visible: {
        opacity: 1,
        scale: 1,
        transition: {
            type: "spring",
            stiffness: 300,
            damping: 20,
        },
    },
};

export function Navbar() {
    const [scrolled, setScrolled] = useState(false);
    const pathname = usePathname();

    const isAuthPage = pathname?.startsWith("/auth");

    useEffect(() => {
        const handleScroll = () => {
            setScrolled(window.scrollY > 10);
        };
        window.addEventListener("scroll", handleScroll);
        return () => window.removeEventListener("scroll", handleScroll);
    }, []);

    return (
        <motion.header
            initial="hidden"
            animate="visible"
            variants={navVariants}
            className={cn(
                "fixed top-0 z-50 w-full transition-all duration-300",
                scrolled ? "bg-(--background)/80 backdrop-blur-md border-b" : "bg-transparent"
            )}
        >
            <div className="container mx-auto flex h-16 items-center justify-between px-4">
                <motion.div variants={logoVariants} className="flex">
                    <Link href="/" className="flex items-center space-x-2 group">
                        <motion.svg
                            xmlns="http://www.w3.org/2000/svg"
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="2"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            className="h-6 w-6"
                            whileHover={{ rotate: 360 }}
                            transition={{ duration: 0.7, ease: "easeInOut" }}
                        >
                            <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
                            <polyline points="3.29 7 12 12 20.71 7" />
                            <line x1="12" y1="22" x2="12" y2="12" />
                        </motion.svg>
                        <span className="font-medium text-lg">AgentSphere</span>
                    </Link>
                </motion.div>
                <div className="flex items-center space-x-4">
                    {!isAuthPage && (
                        <nav className="h-full hidden md:flex items-center space-x-6">
                            <motion.div variants={itemVariants} className="flex items-center">
                                <Link
                                    href="#features"
                                    className="relative text-sm font-medium transition-all duration-300 hover:text-(--primary) focus:outline-none focus:text-(--primary)"
                                >
                                    <span>Features</span>
                                    <motion.span
                                        className="absolute -bottom-2 left-0 h-0.5 bg-(--primary)"
                                        initial={{ width: 0 }}
                                        whileHover={{ width: "100%" }}
                                        transition={{ duration: 0.3 }}
                                    ></motion.span>
                                </Link>
                            </motion.div>
                            <motion.div variants={itemVariants} className="flex items-center">
                                <Link
                                    href="#agents"
                                    className="relative text-sm font-medium transition-all duration-300 hover:text-(--primary) focus:outline-none focus:text-(--primary)"
                                >
                                    <span>Agents</span>
                                    <motion.span
                                        className="absolute -bottom-2 left-0 h-0.5 bg-(--primary)"
                                        initial={{ width: 0 }}
                                        whileHover={{ width: "100%" }}
                                        transition={{ duration: 0.3 }}
                                    ></motion.span>
                                </Link>
                            </motion.div>
                            <motion.div variants={itemVariants} className="flex items-center">
                                <Link
                                    href="#use-cases"
                                    className="relative text-sm font-medium transition-all duration-300 hover:text-(--primary) focus:outline-none focus:text-(--primary)"
                                >
                                    <span>Use Cases</span>
                                    <motion.span
                                        className="absolute -bottom-2 left-0 h-0.5 bg-(--primary)"
                                        initial={{ width: 0 }}
                                        whileHover={{ width: "100%" }}
                                        transition={{ duration: 0.3 }}
                                    ></motion.span>
                                </Link>
                            </motion.div>
                        </nav>
                    )}
                    <ModeToggle />
                </div>
            </div>
        </motion.header>
    );
}
