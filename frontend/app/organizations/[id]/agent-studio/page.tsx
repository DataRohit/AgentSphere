"use client";

import { useAppSelector } from "@/app/store/hooks";
import { selectUser } from "@/app/store/slices/userSlice";
import { AgentsTab } from "@/components/agents-tab";
import { DashboardNavbar } from "@/components/dashboard-navbar";
import { LLMsTab } from "@/components/llms-tab";
import { MCPServersTab } from "@/components/mcp-servers-tab";
import { ProtectedRoute } from "@/components/protected-route";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { motion } from "framer-motion";
import Cookies from "js-cookie";
import { ArrowLeft, Bot, Cpu, MessageCircle, Server } from "lucide-react";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

interface Organization {
    id: string;
    name: string;
    owner: {
        id: string;
        username: string;
        email: string;
    };
}

export default function AgentStudioPage() {
    const router = useRouter();
    const params = useParams();
    const organizationId = params.id as string;
    const currentUser = useAppSelector(selectUser);
    const [isOwner, setIsOwner] = useState<boolean | null>(null);
    const [, setIsLoading] = useState(true);

    useEffect(() => {
        const checkOwnership = async () => {
            setIsLoading(true);
            try {
                const accessToken = Cookies.get("access_token");
                if (!accessToken) {
                    throw new Error("Authentication token not found");
                }

                const response = await fetch(
                    `${process.env.NEXT_PUBLIC_API_URL}/organizations/${organizationId}/`,
                    {
                        method: "GET",
                        headers: {
                            "Content-Type": "application/json",
                            Authorization: `Bearer ${accessToken}`,
                        },
                    }
                );

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.error || "Failed to fetch organization details");
                }

                const organization = data.organization as Organization;

                if (currentUser && organization.owner) {
                    setIsOwner(
                        currentUser.id === organization.owner.id ||
                            currentUser.email === organization.owner.email
                    );
                } else {
                    setIsOwner(false);
                }
            } catch (err) {
                console.error(err);
                setIsOwner(false);
            } finally {
                setIsLoading(false);
            }
        };

        if (currentUser) {
            checkOwnership();
        }
    }, [organizationId, currentUser]);

    const handleBackClick = () => {
        if (isOwner) {
            router.push(`/organizations/${organizationId}`);
        } else {
            router.push("/dashboard");
        }
    };

    return (
        <ProtectedRoute>
            <div className="min-h-screen flex flex-col bg-(--background)">
                <DashboardNavbar />
                <div className="flex-1 container mx-auto px-4 pt-24 pb-8">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5 }}
                        className="space-y-8"
                    >
                        <Button
                            onClick={handleBackClick}
                            variant="outline"
                            className="font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--border) bg-(--background) text-(--foreground) hover:bg-(--muted) h-10 cursor-pointer"
                        >
                            <span className="relative z-10 flex items-center">
                                <ArrowLeft className="mr-2 h-4 w-4" />
                                {isOwner ? "Back to Organization" : "Back to Dashboard"}
                            </span>
                            <span className="absolute inset-0 bg-(--muted)/50 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                        </Button>

                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.5, delay: 0.1 }}
                            className="space-y-6"
                        >
                            <div className="flex flex-col">
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center space-x-3">
                                        <Bot className="h-8 w-8 text-(--primary)" />
                                        <h1 className="text-3xl font-bold tracking-tight">
                                            Agent Studio
                                        </h1>
                                    </div>
                                    <Button
                                        onClick={() =>
                                            router.push(
                                                `/organizations/${organizationId}/conversation-manager`
                                            )
                                        }
                                        className="font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--primary) bg-(--primary) text-(--primary-foreground) dark:bg-(--primary) dark:text-(--primary-foreground) dark:border-(--primary) h-10 cursor-pointer"
                                    >
                                        <span className="relative z-10 flex items-center">
                                            <MessageCircle className="mr-2 h-4 w-4" />
                                            Conversation Manager
                                        </span>
                                        <span className="absolute inset-0 bg-(--primary-foreground)/10 dark:bg-(--primary-foreground)/20 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                                    </Button>
                                </div>
                                <p className="text-sm text-(--muted-foreground) mt-2">
                                    Create, manage, and deploy AI agents for AgentSphere
                                </p>
                            </div>

                            <Tabs defaultValue="agents" className="w-full">
                                <TabsList className="flex w-full gap-1 bg-(--card) p-0.5 rounded-lg overflow-hidden h-10">
                                    <TabsTrigger
                                        value="llms"
                                        className="flex-1 data-[state=active]:bg-(--primary) data-[state=active]:text-(--primary-foreground) data-[state=active]:shadow-sm transition-all duration-200 hover:bg-(--accent) data-[state=active]:hover:bg-(--primary) rounded-md cursor-pointer flex items-center justify-center py-1.5 px-2 m-0 h-9 w-full"
                                    >
                                        <div className="flex items-center">
                                            <Cpu className="mr-2 h-4 w-4" />
                                            <span>LLMs</span>
                                        </div>
                                    </TabsTrigger>
                                    <TabsTrigger
                                        value="mcp-servers"
                                        className="flex-1 data-[state=active]:bg-(--primary) data-[state=active]:text-(--primary-foreground) data-[state=active]:shadow-sm transition-all duration-200 hover:bg-(--accent) data-[state=active]:hover:bg-(--primary) rounded-md cursor-pointer flex items-center justify-center py-1.5 px-2 m-0 h-9 w-full"
                                    >
                                        <div className="flex items-center">
                                            <Server className="mr-2 h-4 w-4" />
                                            <span>MCP Servers</span>
                                        </div>
                                    </TabsTrigger>
                                    <TabsTrigger
                                        value="agents"
                                        className="flex-1 data-[state=active]:bg-(--primary) data-[state=active]:text-(--primary-foreground) data-[state=active]:shadow-sm transition-all duration-200 hover:bg-(--accent) data-[state=active]:hover:bg-(--primary) rounded-md cursor-pointer flex items-center justify-center py-1.5 px-2 m-0 h-9 w-full"
                                    >
                                        <div className="flex items-center">
                                            <Bot className="mr-2 h-4 w-4" />
                                            <span>Agents</span>
                                        </div>
                                    </TabsTrigger>
                                </TabsList>

                                <TabsContent
                                    value="llms"
                                    className="mt-6 data-[state=active]:animate-in data-[state=inactive]:animate-out data-[state=inactive]:fade-out-50 data-[state=active]:fade-in-50 duration-200"
                                >
                                    <motion.div
                                        initial={{ opacity: 0, y: 20 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        transition={{
                                            type: "spring",
                                            stiffness: 300,
                                            damping: 30,
                                            delay: 0.1,
                                        }}
                                    >
                                        <Card>
                                            <CardHeader>
                                                <CardTitle>Language Models</CardTitle>
                                                <p className="text-sm text-(--muted-foreground)">
                                                    Configure and manage your language models for
                                                    use with agents.
                                                </p>
                                            </CardHeader>
                                            <CardContent>
                                                <LLMsTab organizationId={organizationId} />
                                            </CardContent>
                                        </Card>
                                    </motion.div>
                                </TabsContent>

                                <TabsContent
                                    value="mcp-servers"
                                    className="mt-6 data-[state=active]:animate-in data-[state=inactive]:animate-out data-[state=inactive]:fade-out-50 data-[state=active]:fade-in-50 duration-200"
                                >
                                    <motion.div
                                        initial={{ opacity: 0, y: 20 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        transition={{
                                            type: "spring",
                                            stiffness: 300,
                                            damping: 30,
                                            delay: 0.1,
                                        }}
                                    >
                                        <Card>
                                            <CardHeader>
                                                <CardTitle>MCP Servers</CardTitle>
                                                <p className="text-sm text-(--muted-foreground)">
                                                    Connect to MCP servers to enable advanced agent
                                                    capabilities.
                                                </p>
                                            </CardHeader>
                                            <CardContent>
                                                <MCPServersTab organizationId={organizationId} />
                                            </CardContent>
                                        </Card>
                                    </motion.div>
                                </TabsContent>

                                <TabsContent
                                    value="agents"
                                    className="mt-6 data-[state=active]:animate-in data-[state=inactive]:animate-out data-[state=inactive]:fade-out-50 data-[state=active]:fade-in-50 duration-200"
                                >
                                    <motion.div
                                        initial={{ opacity: 0, y: 20 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        transition={{
                                            type: "spring",
                                            stiffness: 300,
                                            damping: 30,
                                            delay: 0.1,
                                        }}
                                    >
                                        <Card>
                                            <CardHeader>
                                                <CardTitle>AI Agents</CardTitle>
                                                <p className="text-sm text-(--muted-foreground)">
                                                    Create, manage, and deploy AI agents for your
                                                    organization.
                                                </p>
                                            </CardHeader>
                                            <CardContent>
                                                <AgentsTab organizationId={organizationId} />
                                            </CardContent>
                                        </Card>
                                    </motion.div>
                                </TabsContent>
                            </Tabs>
                        </motion.div>
                    </motion.div>
                </div>
            </div>
        </ProtectedRoute>
    );
}
