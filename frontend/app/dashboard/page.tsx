"use client";

import { DashboardNavbar } from "@/components/dashboard-navbar";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { motion } from "framer-motion";
import Cookies from "js-cookie";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { toast } from "sonner";

export default function DashboardPage() {
    const router = useRouter();
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const accessToken = Cookies.get("access_token");
        if (!accessToken) {
            toast.error("Please log in to access the dashboard", {
                style: {
                    backgroundColor: "var(--destructive)",
                    color: "white",
                    border: "none",
                },
            });
            router.push("/auth/login");
            return;
        }

        setIsLoading(false);
    }, [router]);

    const handleLogout = () => {
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

    if (isLoading) {
        return (
            <div className="min-h-screen flex flex-col bg-(--background)">
                <DashboardNavbar />
                <div className="flex-1 flex items-center justify-center pt-16">
                    <p>Loading...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen flex flex-col bg-(--background)">
            <DashboardNavbar />
            <div className="flex-1 container mx-auto px-4 pt-24 pb-8">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5 }}
                >
                    <Card className="border shadow-lg">
                        <CardHeader>
                            <CardTitle className="text-2xl font-bold">Dashboard</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p className="mb-6">Welcome to AgentSphere Dashboard!</p>

                            <Button
                                onClick={handleLogout}
                                className="font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--primary) bg-(--primary) text-(--primary-foreground) dark:bg-(--primary) dark:text-(--primary-foreground) dark:border-(--primary) px-8 h-12 cursor-pointer"
                            >
                                <span className="relative z-10">Log Out</span>
                                <span className="absolute inset-0 bg-(--primary-foreground)/10 dark:bg-(--primary-foreground)/20 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                            </Button>
                        </CardContent>
                    </Card>
                </motion.div>
            </div>
        </div>
    );
}
