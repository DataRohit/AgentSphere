"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { motion, Variants } from "framer-motion";
import { UserIcon, UsersIcon } from "lucide-react";

const sectionVariants: Variants = {
    hidden: { opacity: 0 },
    visible: {
        opacity: 1,
        transition: {
            duration: 0.5,
            when: "beforeChildren",
        },
    },
};

const titleVariants: Variants = {
    hidden: { opacity: 0, y: -20 },
    visible: {
        opacity: 1,
        y: 0,
        transition: {
            duration: 0.5,
            type: "spring",
            stiffness: 200,
            damping: 20,
            when: "beforeChildren",
            staggerChildren: 0.1,
        },
    },
};

const cardContainerVariants: Variants = {
    hidden: { opacity: 0 },
    visible: {
        opacity: 1,
        transition: {
            staggerChildren: 0.2,
            delayChildren: 0.2,
        },
    },
};

const cardVariants: Variants = {
    hidden: { opacity: 0, y: 20 },
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

const iconVariants: Variants = {
    hidden: { scale: 0, opacity: 0 },
    visible: {
        scale: 1,
        opacity: 1,
        transition: {
            type: "spring",
            stiffness: 200,
            damping: 15,
        },
    },
};

const listItemVariants: Variants = {
    hidden: { opacity: 0, x: -10 },
    visible: {
        opacity: 1,
        x: 0,
        transition: {
            type: "spring",
            stiffness: 200,
            damping: 20,
        },
    },
};

export function UseCasesSection() {
    return (
        <motion.section
            id="use-cases"
            className="py-20 md:py-28"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.2 }}
            variants={sectionVariants}
        >
            <div className="container mx-auto px-4 md:px-6">
                <motion.div className="text-center mb-12" variants={titleVariants}>
                    <motion.h2
                        className="text-3xl md:text-4xl font-bold tracking-tighter mb-4"
                        variants={titleVariants}
                    >
                        Use Cases
                    </motion.h2>
                    <motion.p
                        className="text-(--muted-foreground) max-w-[700px] mx-auto"
                        variants={titleVariants}
                    >
                        Discover how AgentSphere can enhance your productivity and streamline your
                        workflows
                    </motion.p>
                </motion.div>

                <motion.div
                    className="grid grid-cols-1 xl:grid-cols-2 gap-8 mb-16"
                    variants={cardContainerVariants}
                >
                    <motion.div
                        variants={cardVariants}
                        whileHover={{
                            y: -5,
                            boxShadow: "0 10px 25px rgba(0, 0, 0, 0.1)",
                            transition: { type: "spring", stiffness: 300 },
                        }}
                    >
                        <Card className="border bg-(--background) gap-0 justify-center h-full">
                            <CardHeader>
                                <div className="flex items-center space-x-4 mb-2">
                                    <motion.div
                                        className="p-2 rounded-full bg-(--primary)/10"
                                        variants={iconVariants}
                                        whileHover={{
                                            scale: 1.1,
                                            transition: { type: "spring", stiffness: 300 },
                                        }}
                                    >
                                        <UserIcon className="h-6 w-6 text-(--primary)" />
                                    </motion.div>
                                    <CardTitle>One-on-One Chat</CardTitle>
                                </div>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <motion.p
                                    className="text-(--muted-foreground)"
                                    initial={{ opacity: 0 }}
                                    animate={{
                                        opacity: 1,
                                        transition: { delay: 0.3, duration: 0.5 },
                                    }}
                                >
                                    Direct conversations with specialized AI agents for focused
                                    assistance and information retrieval.
                                </motion.p>
                                <motion.ul
                                    className="space-y-2"
                                    initial="hidden"
                                    animate="visible"
                                    variants={{
                                        hidden: { opacity: 0 },
                                        visible: {
                                            opacity: 1,
                                            transition: {
                                                staggerChildren: 0.15,
                                                delayChildren: 0.4,
                                            },
                                        },
                                    }}
                                >
                                    <motion.li
                                        className="flex items-start"
                                        variants={listItemVariants}
                                    >
                                        <span className="mr-2">•</span>
                                        <span className="text-sm text-(--muted-foreground)">
                                            Personal assistance for specific tasks
                                        </span>
                                    </motion.li>
                                    <motion.li
                                        className="flex items-start"
                                        variants={listItemVariants}
                                    >
                                        <span className="mr-2">•</span>
                                        <span className="text-sm text-(--muted-foreground)">
                                            Detailed information from specialized agents
                                        </span>
                                    </motion.li>
                                    <motion.li
                                        className="flex items-start"
                                        variants={listItemVariants}
                                    >
                                        <span className="mr-2">•</span>
                                        <span className="text-sm text-(--muted-foreground)">
                                            Message history tracking and editing
                                        </span>
                                    </motion.li>
                                </motion.ul>
                            </CardContent>
                        </Card>
                    </motion.div>

                    <motion.div
                        variants={cardVariants}
                        whileHover={{
                            y: -5,
                            boxShadow: "0 10px 25px rgba(0, 0, 0, 0.1)",
                            transition: { type: "spring", stiffness: 300 },
                        }}
                    >
                        <Card className="border bg-(--background) gap-0 h-full">
                            <CardHeader>
                                <div className="flex items-center space-x-4 mb-2">
                                    <motion.div
                                        className="p-2 rounded-full bg-(--primary)/10"
                                        variants={iconVariants}
                                        whileHover={{
                                            scale: 1.1,
                                            transition: { type: "spring", stiffness: 300 },
                                        }}
                                    >
                                        <UsersIcon className="h-6 w-6 text-(--primary)" />
                                    </motion.div>
                                    <CardTitle>Group Chat</CardTitle>
                                </div>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <motion.p
                                    className="text-(--muted-foreground)"
                                    initial={{ opacity: 0 }}
                                    animate={{
                                        opacity: 1,
                                        transition: { delay: 0.3, duration: 0.5 },
                                    }}
                                >
                                    Multi-agent conversations where different specialized agents
                                    collaborate to solve complex problems.
                                </motion.p>
                                <motion.ul
                                    className="space-y-2"
                                    initial="hidden"
                                    animate="visible"
                                    variants={{
                                        hidden: { opacity: 0 },
                                        visible: {
                                            opacity: 1,
                                            transition: {
                                                staggerChildren: 0.15,
                                                delayChildren: 0.4,
                                            },
                                        },
                                    }}
                                >
                                    <motion.li
                                        className="flex items-start"
                                        variants={listItemVariants}
                                    >
                                        <span className="mr-2">•</span>
                                        <span className="text-sm text-(--muted-foreground)">
                                            Collaborative problem-solving with multiple agents
                                        </span>
                                    </motion.li>
                                    <motion.li
                                        className="flex items-start"
                                        variants={listItemVariants}
                                    >
                                        <span className="mr-2">•</span>
                                        <span className="text-sm text-(--muted-foreground)">
                                            Automated routing to appropriate agents
                                        </span>
                                    </motion.li>
                                    <motion.li
                                        className="flex items-start"
                                        variants={listItemVariants}
                                    >
                                        <span className="mr-2">•</span>
                                        <span className="text-sm text-(--muted-foreground)">
                                            Complex workflows with multiple steps
                                        </span>
                                    </motion.li>
                                </motion.ul>
                            </CardContent>
                        </Card>
                    </motion.div>
                </motion.div>
            </div>
        </motion.section>
    );
}
