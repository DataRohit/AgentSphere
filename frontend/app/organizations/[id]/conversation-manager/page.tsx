"use client";

import { ChatList } from "@/components/chat-list";
import { CreateChatDialog } from "@/components/create-chat-dialog";
import { DashboardNavbar } from "@/components/dashboard-navbar";
import { ProtectedRoute } from "@/components/protected-route";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { motion } from "framer-motion";
import { ArrowLeft, MessageCircle, Plus, Users } from "lucide-react";
import { useParams, useRouter } from "next/navigation";
import { useState } from "react";

export default function ConversationManagerPage() {
    const router = useRouter();
    const params = useParams();
    const organizationId = params.id as string;
    const [isCreateChatDialogOpen, setIsCreateChatDialogOpen] = useState(false);

    const handleBackClick = () => {
        router.push(`/organizations/${organizationId}/agent-studio`);
    };

    const handleCreateChatSuccess = () => {
        window.location.reload();
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
                                Back to Agent Studio
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
                                <div className="flex items-center space-x-3">
                                    <MessageCircle className="h-8 w-8 text-(--primary)" />
                                    <h1 className="text-3xl font-bold tracking-tight">
                                        Conversation Manager
                                    </h1>
                                </div>
                                <p className="text-sm text-(--muted-foreground) mt-2">
                                    Manage your conversations with AI agents
                                </p>
                            </div>

                            <Tabs defaultValue="direct-chat" className="w-full">
                                <TabsList className="flex w-full gap-1 bg-(--card) p-0.5 rounded-lg overflow-hidden h-10">
                                    <TabsTrigger
                                        value="direct-chat"
                                        className="flex-1 data-[state=active]:bg-(--primary) data-[state=active]:text-(--primary-foreground) data-[state=active]:shadow-sm transition-all duration-200 hover:bg-(--accent) data-[state=active]:hover:bg-(--primary) rounded-md cursor-pointer flex items-center justify-center py-1.5 px-2 m-0 h-9 w-full"
                                    >
                                        <div className="flex items-center">
                                            <MessageCircle className="mr-2 h-4 w-4" />
                                            <span>One-on-One Direct Chat</span>
                                        </div>
                                    </TabsTrigger>
                                    <TabsTrigger
                                        value="group-chat"
                                        className="flex-1 data-[state=active]:bg-(--primary) data-[state=active]:text-(--primary-foreground) data-[state=active]:shadow-sm transition-all duration-200 hover:bg-(--accent) data-[state=active]:hover:bg-(--primary) rounded-md cursor-pointer flex items-center justify-center py-1.5 px-2 m-0 h-9 w-full"
                                    >
                                        <div className="flex items-center">
                                            <Users className="mr-2 h-4 w-4" />
                                            <span>Group Chat</span>
                                        </div>
                                    </TabsTrigger>
                                </TabsList>

                                <TabsContent
                                    value="direct-chat"
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
                                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                                <div>
                                                    <CardTitle>One-on-One Direct Chat</CardTitle>
                                                    <p className="text-sm text-(--muted-foreground) mt-2">
                                                        Chat directly with individual AI agents
                                                    </p>
                                                </div>
                                                <Button
                                                    onClick={() => setIsCreateChatDialogOpen(true)}
                                                    className="font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--primary) bg-(--primary) text-(--primary-foreground) dark:bg-(--primary) dark:text-(--primary-foreground) dark:border-(--primary) h-10 cursor-pointer"
                                                >
                                                    <span className="relative z-10 flex items-center">
                                                        <Plus className="mr-2 h-4 w-4" />
                                                        New Chat
                                                    </span>
                                                    <span className="absolute inset-0 bg-(--primary-foreground)/10 dark:bg-(--primary-foreground)/20 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                                                </Button>
                                            </CardHeader>
                                            <CardContent>
                                                <ChatList organizationId={organizationId} />
                                            </CardContent>
                                        </Card>
                                    </motion.div>
                                </TabsContent>

                                <TabsContent
                                    value="group-chat"
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
                                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                                <div>
                                                    <CardTitle>Group Chat</CardTitle>
                                                    <p className="text-sm text-(--muted-foreground) mt-2">
                                                        Chat with multiple AI agents in a group
                                                        conversation
                                                    </p>
                                                </div>
                                                <Button className="font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--primary) bg-(--primary) text-(--primary-foreground) dark:bg-(--primary) dark:text-(--primary-foreground) dark:border-(--primary) h-10 cursor-pointer">
                                                    <span className="relative z-10 flex items-center">
                                                        <Plus className="mr-2 h-4 w-4" />
                                                        New Group
                                                    </span>
                                                    <span className="absolute inset-0 bg-(--primary-foreground)/10 dark:bg-(--primary-foreground)/20 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                                                </Button>
                                            </CardHeader>
                                            <CardContent>
                                                <div className="flex flex-col items-center justify-center p-8 text-center">
                                                    <Users className="h-12 w-12 text-(--muted-foreground) mb-3" />
                                                    <h3 className="text-lg font-medium mb-1">
                                                        Group Chat Placeholder
                                                    </h3>
                                                    <p className="text-sm text-(--muted-foreground) mb-4">
                                                        This is a placeholder for the group chat
                                                        functionality.
                                                    </p>
                                                </div>
                                            </CardContent>
                                        </Card>
                                    </motion.div>
                                </TabsContent>
                            </Tabs>
                        </motion.div>
                    </motion.div>
                </div>
            </div>

            <CreateChatDialog
                open={isCreateChatDialogOpen}
                onOpenChange={setIsCreateChatDialogOpen}
                organizationId={organizationId}
                onSuccess={handleCreateChatSuccess}
            />
        </ProtectedRoute>
    );
}
