"use client";

import { Button } from "@/components/ui/button";
import { AnimatePresence, motion, Variants } from "framer-motion";
import { Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";
import { useEffect, useState } from "react";

const sunVariants: Variants = {
    hidden: {
        rotate: -360,
        scale: 0,
        opacity: 0,
    },
    visible: {
        rotate: 0,
        scale: 1,
        opacity: 1,
        transition: {
            type: "spring",
            duration: 0.7,
            bounce: 0.3,
        },
    },
    exit: {
        rotate: 360,
        scale: 0,
        opacity: 0,
        transition: {
            duration: 0.4,
        },
    },
    shine: {
        scale: [1, 1.05, 1],
        transition: {
            repeat: Infinity,
            repeatType: "reverse" as const,
            duration: 2,
            ease: "easeInOut",
        },
    },
};

const moonVariants: Variants = {
    hidden: {
        rotate: 360,
        scale: 0,
        opacity: 0,
    },
    visible: {
        rotate: 0,
        scale: 1,
        opacity: 1,
        transition: {
            type: "spring",
            duration: 0.7,
            bounce: 0.3,
        },
    },
    exit: {
        rotate: -360,
        scale: 0,
        opacity: 0,
        transition: {
            duration: 0.4,
        },
    },
    glow: {
        filter: [
            "drop-shadow(0 0 0px rgba(255, 255, 255, 0))",
            "drop-shadow(0 0 2px rgba(255, 255, 255, 0.5))",
            "drop-shadow(0 0 0px rgba(255, 255, 255, 0))",
        ],
        scale: [1, 1.05, 1],
        rotate: [0, 3, 0, -3, 0],
        transition: {
            repeat: Infinity,
            repeatType: "reverse" as const,
            duration: 4,
            ease: "easeInOut",
        },
    },
};

const MotionButton = motion.create(Button);

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

    const isDark = resolvedTheme === "dark";

    return (
        <MotionButton
            variant="ghost"
            size="icon"
            className="cursor-pointer hover:bg-(--accent) hover:text-(--accent-foreground) relative overflow-hidden p-0"
            onClick={toggleTheme}
            aria-label="Toggle theme"
            whileTap={{ scale: 0.95 }}
        >
            <div className="relative h-9 w-9 flex items-center justify-center">
                <AnimatePresence mode="wait" initial={false}>
                    {!isDark ? (
                        <motion.div
                            key="sun"
                            className="absolute"
                            initial="hidden"
                            animate={["visible", "shine"]}
                            exit="exit"
                            variants={sunVariants}
                        >
                            <Sun className="h-[1.2rem] w-[1.2rem]" />
                        </motion.div>
                    ) : (
                        <motion.div
                            key="moon"
                            className="absolute"
                            initial="hidden"
                            animate={["visible", "glow"]}
                            exit="exit"
                            variants={moonVariants}
                        >
                            <Moon className="h-[1.2rem] w-[1.2rem]" />
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
            <span className="sr-only">Toggle theme</span>
        </MotionButton>
    );
}
