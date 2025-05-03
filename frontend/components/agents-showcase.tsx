"use client";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CloudIcon, MagnifyingGlassIcon, NewspaperIcon } from "@heroicons/react/24/outline";
import { motion, Variants } from "framer-motion";

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
            staggerChildren: 0.15,
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

const badgeVariants: Variants = {
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

const agents = [
    {
        name: "News Agent",
        description: "Stay updated with the latest news & headlines from various sources.",
        icon: NewspaperIcon,
        tags: ["News", "Headlines", "Updates"],
    },
    {
        name: "Weather Agent",
        description: "Get real-time weather forecasts and alerts for any location worldwide",
        icon: CloudIcon,
        tags: ["Weather", "Forecast", "Alerts"],
    },
    {
        name: "SerpAPI Google Agent",
        description: "Search the web and retrieve information from Google search results",
        icon: MagnifyingGlassIcon,
        tags: ["Search", "Web", "Information"],
    },
];

export function AgentsShowcase() {
    return (
        <motion.section
            id="agents"
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
                        Specialized Agents
                    </motion.h2>
                    <motion.p
                        className="text-(--muted-foreground) max-w-[700px] mx-auto"
                        variants={titleVariants}
                    >
                        Interact with purpose-built AI agents designed to handle specific tasks and
                        provide valuable information
                    </motion.p>
                </motion.div>

                <motion.div
                    className="grid grid-cols-1 xl:grid-cols-3 gap-8"
                    variants={cardContainerVariants}
                >
                    {agents.map((agent, index) => (
                        <motion.div
                            key={index}
                            variants={cardVariants}
                            whileHover={{
                                y: -5,
                                scale: 1.02,
                                boxShadow: "0 10px 25px rgba(0, 0, 0, 0.1)",
                                transition: { type: "spring", stiffness: 300 },
                            }}
                        >
                            <Card className="border bg-(--background) overflow-hidden transition-all h-full">
                                <CardHeader className="pb-2">
                                    <div className="flex items-center justify-between">
                                        <motion.div
                                            variants={iconVariants}
                                            whileHover={{
                                                rotate: [0, -5, 5, 0],
                                                scale: 1.1,
                                                transition: { duration: 0.5 },
                                            }}
                                        >
                                            <agent.icon className="h-8 w-8 text-(--primary)" />
                                        </motion.div>
                                        <motion.div
                                            className="h-10 w-10 rounded-full bg-(--muted) flex items-center justify-center"
                                            initial={{ scale: 0 }}
                                            animate={{
                                                scale: 1,
                                                transition: {
                                                    type: "spring",
                                                    stiffness: 260,
                                                    damping: 20,
                                                    delay: 0.2 + index * 0.1,
                                                },
                                            }}
                                        >
                                            <span className="text-xs font-medium">AI</span>
                                        </motion.div>
                                    </div>
                                    <CardTitle className="text-xl mt-4">{agent.name}</CardTitle>
                                </CardHeader>
                                <CardContent className="space-y-4">
                                    <p className="text-(--muted-foreground) text-sm">
                                        {agent.description}
                                    </p>
                                    <motion.div
                                        className="flex flex-wrap gap-2"
                                        initial="hidden"
                                        animate="visible"
                                        variants={{
                                            hidden: { opacity: 0 },
                                            visible: {
                                                opacity: 1,
                                                transition: {
                                                    staggerChildren: 0.1,
                                                    delayChildren: 0.3 + index * 0.1,
                                                },
                                            },
                                        }}
                                    >
                                        {agent.tags.map((tag, tagIndex) => (
                                            <motion.div
                                                key={tagIndex}
                                                variants={badgeVariants}
                                                whileHover={{
                                                    scale: 1.05,
                                                    transition: { type: "spring", stiffness: 300 },
                                                }}
                                            >
                                                <Badge variant="secondary">{tag}</Badge>
                                            </motion.div>
                                        ))}
                                    </motion.div>
                                </CardContent>
                            </Card>
                        </motion.div>
                    ))}
                </motion.div>
            </div>
        </motion.section>
    );
}
