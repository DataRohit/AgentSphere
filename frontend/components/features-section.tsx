"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
    ChatBubbleLeftRightIcon,
    CogIcon,
    LockClosedIcon,
    UserGroupIcon,
} from "@heroicons/react/24/outline";
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

const features = [
    {
        title: "AI Agents",
        description: "Create and manage AI agents with customizable system prompts.",
        icon: ChatBubbleLeftRightIcon,
    },
    {
        title: "Multi-User",
        description: "Collaborative environment with organizations and members",
        icon: UserGroupIcon,
    },
    {
        title: "MCP Tools",
        description: "Integrate external tools via MCP servers for task automation",
        icon: CogIcon,
    },
    {
        title: "Secure",
        description: "API keys stored securely in HashiCorp Vault for authentication",
        icon: LockClosedIcon,
    },
];

export function FeaturesSection() {
    return (
        <motion.section
            id="features"
            className="py-20 md:py-28 bg-muted/50 dark:bg-muted/10"
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
                        Key Features
                    </motion.h2>
                    <motion.p
                        className="text-(--muted-foreground) max-w-[700px] mx-auto"
                        variants={titleVariants}
                    >
                        AgentSphere provides powerful tools for AI agent interactions and workflow
                        automation
                    </motion.p>
                </motion.div>

                <motion.div
                    className="grid grid-cols-1 lg:grid-cols-2 2xl:grid-cols-4 gap-6"
                    variants={cardContainerVariants}
                >
                    {features.map((feature, index) => (
                        <motion.div
                            key={index}
                            variants={cardVariants}
                            whileHover={{
                                y: -5,
                                boxShadow: "0 10px 25px rgba(0, 0, 0, 0.1)",
                                transition: { type: "spring", stiffness: 300 },
                            }}
                        >
                            <Card className="border bg-(--background) gap-0 h-full">
                                <CardHeader className="pb-2">
                                    <motion.div
                                        variants={iconVariants}
                                        animate={{ rotate: 0 }}
                                        whileHover={{
                                            rotate: [0, -5, 5, -2, 2, 0],
                                            transition: { duration: 0.5 },
                                        }}
                                    >
                                        <feature.icon className="h-10 w-10 mb-4 text-(--primary)" />
                                    </motion.div>
                                    <CardTitle className="text-xl">{feature.title}</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <p className="text-(--muted-foreground) text-sm">
                                        {feature.description}
                                    </p>
                                </CardContent>
                            </Card>
                        </motion.div>
                    ))}
                </motion.div>

                <motion.div
                    className="mt-16 grid grid-cols-1 2xl:grid-cols-3 gap-8"
                    variants={cardContainerVariants}
                    initial="hidden"
                    whileInView="visible"
                    viewport={{ once: true, amount: 0.1 }}
                >
                    <motion.div
                        variants={cardVariants}
                        whileHover={{
                            y: -5,
                            boxShadow: "0 10px 25px rgba(0, 0, 0, 0.1)",
                            transition: { type: "spring", stiffness: 300 },
                        }}
                    >
                        <Card className="border bg-(--background) gap-0 h-full">
                            <CardHeader className="pb-2">
                                <CardTitle className="text-xl">Organization Management</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <ul className="space-y-2">
                                    <motion.li
                                        className="flex items-start"
                                        initial={{ opacity: 0, x: -10 }}
                                        whileInView={{ opacity: 1, x: 0 }}
                                        transition={{ delay: 0.1 }}
                                        viewport={{ once: true }}
                                    >
                                        <span className="mr-2">•</span>
                                        <span className="text-sm text-(--muted-foreground)">
                                            Create up to 3 organizations per user
                                        </span>
                                    </motion.li>
                                    <motion.li
                                        className="flex items-start"
                                        initial={{ opacity: 0, x: -10 }}
                                        whileInView={{ opacity: 1, x: 0 }}
                                        transition={{ delay: 0.2 }}
                                        viewport={{ once: true }}
                                    >
                                        <span className="mr-2">•</span>
                                        <span className="text-sm text-(--muted-foreground)">
                                            Add up to 8 members per organization
                                        </span>
                                    </motion.li>
                                    <motion.li
                                        className="flex items-start"
                                        initial={{ opacity: 0, x: -10 }}
                                        whileInView={{ opacity: 1, x: 0 }}
                                        transition={{ delay: 0.3 }}
                                        viewport={{ once: true }}
                                    >
                                        <span className="mr-2">•</span>
                                        <span className="text-sm text-(--muted-foreground)">
                                            Manage resource visibility (public/private)
                                        </span>
                                    </motion.li>
                                </ul>
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
                            <CardHeader className="pb-2">
                                <CardTitle className="text-xl">Agent Creation</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <ul className="space-y-2">
                                    <motion.li
                                        className="flex items-start"
                                        initial={{ opacity: 0, x: -10 }}
                                        whileInView={{ opacity: 1, x: 0 }}
                                        transition={{ delay: 0.1 }}
                                        viewport={{ once: true }}
                                    >
                                        <span className="mr-2">•</span>
                                        <span className="text-sm text-(--muted-foreground)">
                                            Create up to 5 agents per user per organization
                                        </span>
                                    </motion.li>
                                    <motion.li
                                        className="flex items-start"
                                        initial={{ opacity: 0, x: -10 }}
                                        whileInView={{ opacity: 1, x: 0 }}
                                        transition={{ delay: 0.2 }}
                                        viewport={{ once: true }}
                                    >
                                        <span className="mr-2">•</span>
                                        <span className="text-sm text-(--muted-foreground)">
                                            Customize system prompts and behaviors
                                        </span>
                                    </motion.li>
                                    <motion.li
                                        className="flex items-start"
                                        initial={{ opacity: 0, x: -10 }}
                                        whileInView={{ opacity: 1, x: 0 }}
                                        transition={{ delay: 0.3 }}
                                        viewport={{ once: true }}
                                    >
                                        <span className="mr-2">•</span>
                                        <span className="text-sm text-(--muted-foreground)">
                                            Auto-generated avatars using DiceBear
                                        </span>
                                    </motion.li>
                                </ul>
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
                            <CardHeader className="pb-2">
                                <CardTitle className="text-xl">MCP Tool Integration</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <ul className="space-y-2">
                                    <motion.li
                                        className="flex items-start"
                                        initial={{ opacity: 0, x: -10 }}
                                        whileInView={{ opacity: 1, x: 0 }}
                                        transition={{ delay: 0.1 }}
                                        viewport={{ once: true }}
                                    >
                                        <span className="mr-2">•</span>
                                        <span className="text-sm text-(--muted-foreground)">
                                            Add up to 5 MCP tools per organization
                                        </span>
                                    </motion.li>
                                    <motion.li
                                        className="flex items-start"
                                        initial={{ opacity: 0, x: -10 }}
                                        whileInView={{ opacity: 1, x: 0 }}
                                        transition={{ delay: 0.2 }}
                                        viewport={{ once: true }}
                                    >
                                        <span className="mr-2">•</span>
                                        <span className="text-sm text-(--muted-foreground)">
                                            Define tools by name, description, URL, and tags
                                        </span>
                                    </motion.li>
                                    <motion.li
                                        className="flex items-start"
                                        initial={{ opacity: 0, x: -10 }}
                                        whileInView={{ opacity: 1, x: 0 }}
                                        transition={{ delay: 0.3 }}
                                        viewport={{ once: true }}
                                    >
                                        <span className="mr-2">•</span>
                                        <span className="text-sm text-(--muted-foreground)">
                                            Secure authentication with external services
                                        </span>
                                    </motion.li>
                                </ul>
                            </CardContent>
                        </Card>
                    </motion.div>
                </motion.div>
            </div>
        </motion.section>
    );
}
