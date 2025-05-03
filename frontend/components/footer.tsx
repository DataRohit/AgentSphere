"use client";

import { motion, Variants } from "framer-motion";
import { Github, Linkedin } from "lucide-react";
import Link from "next/link";

const footerVariants: Variants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
        opacity: 1,
        y: 0,
        transition: {
            duration: 0.6,
            when: "beforeChildren",
            staggerChildren: 0.1,
        },
    },
};

const itemVariants: Variants = {
    hidden: { opacity: 0, y: 10 },
    visible: {
        opacity: 1,
        y: 0,
        transition: {
            type: "spring",
            stiffness: 150,
            damping: 20,
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
            stiffness: 200,
            damping: 15,
        },
    },
};

const iconVariants: Variants = {
    hidden: { opacity: 0, scale: 0 },
    visible: {
        opacity: 1,
        scale: 1,
        transition: {
            type: "spring",
            stiffness: 300,
            damping: 15,
        },
    },
    hover: {
        scale: 1.2,
        rotate: 20,
        transition: {
            type: "spring",
            stiffness: 400,
            damping: 10,
        },
    },
};

export function Footer() {
    return (
        <motion.footer
            className="border-t py-12 md:py-16"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.3 }}
            variants={footerVariants}
        >
            <div className="container px-4 md:px-6 mx-auto max-w-screen-xl">
                <motion.div
                    className="flex flex-col space-y-4 md:space-y-0 md:flex-row justify-between items-center"
                    variants={footerVariants}
                >
                    <motion.div className="mb-6 md:mb-0" variants={itemVariants}>
                        <motion.div
                            className="flex items-center space-x-2 w-36 group cursor-pointer"
                            variants={logoVariants}
                            whileHover={{ scale: 1.05 }}
                        >
                            <motion.svg
                                xmlns="http://www.w3.org/2000/svg"
                                viewBox="0 0 24 24"
                                fill="none"
                                stroke="currentColor"
                                strokeWidth="2"
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                className="h-5 w-5"
                                animate={{ rotate: 0 }}
                                whileHover={{
                                    rotate: 360,
                                    transition: { duration: 0.7, ease: "easeInOut" },
                                }}
                            >
                                <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
                                <polyline points="3.29 7 12 12 20.71 7" />
                                <line x1="12" y1="22" x2="12" y2="12" />
                            </motion.svg>
                            <motion.span
                                className="font-medium"
                                whileHover={{ color: "var(--primary)" }}
                                transition={{ duration: 0.2 }}
                            >
                                AgentSphere
                            </motion.span>
                        </motion.div>
                    </motion.div>
                    <motion.div
                        className="flex flex-col items-center gap-2"
                        variants={itemVariants}
                    >
                        <motion.p
                            className="text-(--muted-foreground)"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: 0.3, duration: 0.5 }}
                        >
                            Created by Rohit Ingole / DataRohit
                        </motion.p>
                    </motion.div>
                    <motion.div
                        className="flex md:space-x-4 w-20 md:w-36 mt-2 md:mt-0 justify-around md:justify-end"
                        variants={itemVariants}
                    >
                        <motion.div variants={iconVariants} whileHover="hover">
                            <Link
                                href="https://github.com/DataRohit/AgentSphere"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-(--muted-foreground) hover:text-(--foreground) transition-all duration-300"
                            >
                                <Github className="h-5 w-5" />
                                <span className="sr-only">GitHub</span>
                            </Link>
                        </motion.div>
                        <motion.div variants={iconVariants} whileHover="hover">
                            <Link
                                href="https://www.linkedin.com/in/rohit-vilas-ingole/"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-(--muted-foreground) hover:text-(--foreground) transition-all duration-300"
                            >
                                <Linkedin className="h-5 w-5" />
                                <span className="sr-only">LinkedIn</span>
                            </Link>
                        </motion.div>
                    </motion.div>
                </motion.div>
            </div>
        </motion.footer>
    );
}
