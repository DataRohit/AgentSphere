"use client";

import { AgentsTab } from "@/components/agents-tab";
import { DashboardNavbar } from "@/components/dashboard-navbar";
import { LLMsTab } from "@/components/llms-tab";
import { MCPServersTab } from "@/components/mcp-servers-tab";
import { ProtectedRoute } from "@/components/protected-route";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { motion } from "framer-motion";
import { ArrowLeft, Bot, Cpu, Server } from "lucide-react";
import { useParams, useRouter } from "next/navigation";

export default function AgentStudioPage() {
    const router = useRouter();
    const params = useParams();
    const organizationId = params.id as string;

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
                            variant="ghost"
                            className="flex items-center text-(--muted-foreground) hover:text-(--foreground)"
                            onClick={() => router.push(`/organizations/${organizationId}`)}
                        >
                            <ArrowLeft className="mr-2 h-4 w-4" />
                            Back to Organization
                        </Button>

                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.5, delay: 0.1 }}
                            className="space-y-6"
                        >
                            <div className="flex items-center space-x-3">
                                <Bot className="h-8 w-8 text-(--primary)" />
                                <h1 className="text-3xl font-bold tracking-tight">Agent Studio</h1>
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
                                                <p className="text-(--muted-foreground)">
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
                                                <p className="text-(--muted-foreground)">
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
                                                <p className="text-(--muted-foreground)">
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
