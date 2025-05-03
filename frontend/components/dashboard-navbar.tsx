"use client";

import { useAppDispatch, useAppSelector } from "@/app/store/hooks";
import { clearUser, selectUser } from "@/app/store/slices/userSlice";
import { ModeToggle } from "@/components/mode-toggle";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { cn } from "@/lib/utils";
import { motion, Variants } from "framer-motion";
import Cookies from "js-cookie";
import { LogOut, Settings, User } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { toast } from "sonner";

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

export function DashboardNavbar() {
    const [scrolled, setScrolled] = useState(false);
    const user = useAppSelector(selectUser);
    const dispatch = useAppDispatch();
    const router = useRouter();

    useEffect(() => {
        const handleScroll = () => {
            setScrolled(window.scrollY > 10);
        };
        window.addEventListener("scroll", handleScroll);
        return () => window.removeEventListener("scroll", handleScroll);
    }, []);

    const getUserInitials = () => {
        if (!user) return "U";

        if (user.full_name) {
            const nameParts = user.full_name.split(" ");
            if (nameParts.length >= 2) {
                return `${nameParts[0][0]}${nameParts[nameParts.length - 1][0]}`.toUpperCase();
            }
            return user.full_name[0].toUpperCase();
        }

        if (user.first_name && user.last_name) {
            return `${user.first_name[0]}${user.last_name[0]}`.toUpperCase();
        }

        return user.username[0].toUpperCase();
    };

    const handleLogout = () => {
        dispatch(clearUser());

        Cookies.remove("access_token");
        Cookies.remove("refresh_token");

        toast.success("Logged out successfully", {
            style: {
                backgroundColor: "oklch(0.45 0.18 142.71)",
                color: "white",
                border: "none",
            },
        });

        router.push("/");
    };

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
            <div className="container mx-auto flex h-16 items-center justify-between">
                <motion.div variants={logoVariants} className="flex">
                    <Link href="/dashboard" className="flex items-center space-x-2 group">
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
                    <ModeToggle />

                    {user && (
                        <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                                <motion.div
                                    initial={{ opacity: 0, scale: 0.8 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    transition={{ duration: 0.3 }}
                                    className="cursor-pointer"
                                >
                                    <div className="relative group">
                                        <Avatar className="h-9 w-9 border border-(--border) group-hover:border-(--primary) group-hover:shadow-sm transition-all duration-200">
                                            {user.avatar_url ? (
                                                <AvatarImage
                                                    src={user.avatar_url}
                                                    alt={user.username}
                                                />
                                            ) : null}
                                            <AvatarFallback className="bg-(--primary)/10 text-(--primary)">
                                                {getUserInitials()}
                                            </AvatarFallback>
                                        </Avatar>
                                        <span className="absolute -bottom-1 -right-1 w-3 h-3 bg-(--background) rounded-full flex items-center justify-center border border-(--border) group-hover:border-(--primary) transition-colors duration-200">
                                            <span className="w-1.5 h-1.5 bg-(--primary) rounded-full"></span>
                                        </span>
                                    </div>
                                </motion.div>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent
                                align="end"
                                className="w-56 bg-(--background) border border-(--border) shadow-lg rounded-md p-2"
                            >
                                <motion.div
                                    initial={{ opacity: 0, y: -5 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ duration: 0.2 }}
                                >
                                    <DropdownMenuLabel className="px-3">
                                        <p className="text-sm font-medium">
                                            {user.full_name || user.username}
                                        </p>
                                        <p className="text-xs text-(--muted-foreground) truncate">
                                            {user.email}
                                        </p>
                                    </DropdownMenuLabel>
                                </motion.div>
                                <DropdownMenuSeparator className="bg-(--border) h-[1px] my-2" />
                                <motion.div
                                    initial={{ opacity: 0, x: -5 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ duration: 0.2, delay: 0.1 }}
                                    whileHover={{ x: 3 }}
                                >
                                    <DropdownMenuItem
                                        className="cursor-pointer hover:bg-(--accent) focus:bg-(--accent) transition-colors duration-200 rounded-sm my-0.5 mx-1"
                                        onClick={() => router.push("/profile")}
                                    >
                                        <User className="mr-2 h-4 w-4" />
                                        <span>Profile</span>
                                    </DropdownMenuItem>
                                </motion.div>
                                <motion.div
                                    initial={{ opacity: 0, x: -5 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ duration: 0.2, delay: 0.2 }}
                                    whileHover={{ x: 3 }}
                                >
                                    <DropdownMenuItem className="cursor-pointer hover:bg-(--accent) focus:bg-(--accent) transition-colors duration-200 rounded-sm my-0.5 mx-1">
                                        <Settings className="mr-2 h-4 w-4" />
                                        <span>Settings</span>
                                    </DropdownMenuItem>
                                </motion.div>
                                <DropdownMenuSeparator className="bg-(--border) h-[1px] my-2" />
                                <motion.div
                                    initial={{ opacity: 0, x: -5 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ duration: 0.2, delay: 0.3 }}
                                    whileHover={{ x: 3 }}
                                >
                                    <DropdownMenuItem
                                        className="cursor-pointer text-(--destructive) hover:bg-(--destructive)/10 focus:bg-(--destructive)/10 transition-colors duration-200 rounded-sm my-0.5 mx-1"
                                        onClick={handleLogout}
                                    >
                                        <LogOut className="mr-2 h-4 w-4" />
                                        <span>Log out</span>
                                    </DropdownMenuItem>
                                </motion.div>
                            </DropdownMenuContent>
                        </DropdownMenu>
                    )}
                </div>
            </div>
        </motion.header>
    );
}
