"use client";

import { Navbar } from "@/components/navbar";
import { Button } from "@/components/ui/button";
import { motion, Variants } from "framer-motion";
import Cookies from "js-cookie";
import { ArrowRight, Search } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

interface BlobAnimationProps {
    x: number;
    y: number;
    dx: number;
    dy: number;
}

const containerVariants: Variants = {
    hidden: { opacity: 0 },
    visible: {
        opacity: 1,
        transition: {
            staggerChildren: 0.2,
            delayChildren: 0.3,
            when: "beforeChildren",
        },
    },
};

const itemVariants: Variants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
        y: 0,
        opacity: 1,
        transition: {
            type: "spring",
            damping: 12,
            stiffness: 200,
        },
    },
};

const blobVariants: Variants = {
    initial: (custom: BlobAnimationProps) => ({
        opacity: 0.5,
        scale: 1,
        x: custom.x,
        y: custom.y,
    }),
    animate: (custom: BlobAnimationProps) => ({
        opacity: 0.6,
        scale: [1, 1.15, 1],
        x: [custom.x, custom.x + custom.dx, custom.x],
        y: [custom.y, custom.y + custom.dy, custom.y],
        transition: {
            duration: 10,
            repeat: Infinity,
            repeatType: "mirror",
            ease: "easeInOut",
        },
    }),
};

export function HeroSection() {
    const router = useRouter();
    const [isLoggedIn, setIsLoggedIn] = useState(false);

    useEffect(() => {
        const accessToken = Cookies.get("access_token");
        if (accessToken) {
            setIsLoggedIn(true);
        }
    }, []);

    const handleGetStarted = () => {
        if (isLoggedIn) {
            router.push("/dashboard");
        } else {
            router.push("/auth/signup");
        }
    };

    return (
        <motion.section
            initial="hidden"
            animate="visible"
            className="relative min-h-screen flex flex-col items-center justify-center overflow-hidden"
        >
            <Navbar />
            <motion.div
                className="fixed inset-0 -z-30 pointer-events-none"
                style={{
                    background:
                        "radial-gradient(ellipse 80% 60% at 50% 0%, rgba(99,102,241,0.18) 0%, transparent 100%), linear-gradient(120deg, rgba(16,185,129,0.10) 0%, rgba(99,102,241,0.10) 100%)",
                }}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 1.2 }}
            />
            <motion.div
                className="fixed top-[-10%] left-[-10%] w-[350px] h-[350px] rounded-full bg-indigo-400 opacity-30 blur-3xl -z-20"
                custom={{ x: 0, y: 0, dx: 60, dy: 40 }}
                variants={blobVariants}
                initial="initial"
                animate="animate"
            />
            <motion.div
                className="fixed bottom-[-12%] right-[-8%] w-[300px] h-[300px] rounded-full bg-emerald-400 opacity-20 blur-3xl -z-20"
                custom={{ x: 0, y: 0, dx: -40, dy: 50 }}
                variants={blobVariants}
                initial="initial"
                animate="animate"
            />
            <motion.div
                className="fixed top-[30%] right-[10%] w-[200px] h-[200px] rounded-full bg-fuchsia-400 opacity-20 blur-2xl -z-20"
                custom={{ x: 0, y: 0, dx: 30, dy: -30 }}
                variants={blobVariants}
                initial="initial"
                animate="animate"
            />
            <motion.div
                variants={containerVariants}
                className="container flex flex-col items-center text-center z-10 px-4 md:px-6"
            >
                <motion.h1
                    variants={itemVariants}
                    className="text-4xl md:text-5xl lg:text-6xl font-bold tracking-tighter mb-4"
                >
                    AgentSphere
                </motion.h1>
                <motion.p
                    variants={itemVariants}
                    className="text-xl md:text-2xl text-(--muted-foreground) max-w-[800px] mb-8"
                >
                    A dynamic AI platform enabling one-on-one and group interactions with
                    specialized AI agents
                </motion.p>
                <motion.div variants={itemVariants} className="flex flex-col sm:flex-row gap-4">
                    <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.98 }}>
                        <Button
                            size="lg"
                            className="font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--primary) bg-(--primary) text-(--primary-foreground) dark:bg-(--primary) dark:text-(--primary-foreground) dark:border-(--primary) px-8 w-40 h-12 cursor-pointer"
                            onClick={handleGetStarted}
                        >
                            <span className="relative z-10 flex items-center">
                                {isLoggedIn ? "Dashboard" : "Get Started"}
                                <motion.span
                                    initial={{ x: 0 }}
                                    whileHover={{ x: 5 }}
                                    transition={{ type: "spring", stiffness: 400 }}
                                >
                                    <ArrowRight className="ml-2 h-4 w-4" />
                                </motion.span>
                            </span>
                            <span className="absolute inset-0 bg-(--primary-foreground)/80 dark:bg-(--primary-foreground)/20 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                        </Button>
                    </motion.div>
                    <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.98 }}>
                        <Button
                            size="lg"
                            className="font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--secondary) bg-(--secondary) text-(--secondary-foreground) dark:bg-(--secondary) dark:text-(--secondary-foreground) dark:border-(--secondary) px-8 w-40 h-12 cursor-pointer"
                        >
                            <span className="relative z-10 flex items-center">
                                Explore{" "}
                                <motion.span
                                    initial={{ scale: 1 }}
                                    whileHover={{ scale: 1.2 }}
                                    transition={{ type: "spring", stiffness: 400 }}
                                >
                                    <Search className="ml-2 h-4 w-4" />
                                </motion.span>
                            </span>
                            <span className="absolute inset-0 bg-(--secondary-foreground)/10 dark:bg-(--secondary-foreground)/20 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-right"></span>
                        </Button>
                    </motion.div>
                </motion.div>
            </motion.div>
        </motion.section>
    );
}
