"use client";

import { DashboardNavbar } from "@/components/dashboard-navbar";
import { ProtectedRoute } from "@/components/protected-route";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import Cookies from "js-cookie";
import { ArrowLeft, Loader2, MessageCircle } from "lucide-react";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { toast } from "sonner";

interface Agent {
    id: string;
    name: string;
}

interface GroupChat {
    id: string;
    title: string;
    is_public: boolean;
    created_at: string;
    updated_at: string;
    summary: string;
    organization: {
        id: string;
        name: string;
    };
    user: {
        id: string;
        username: string;
        email: string;
    };
    agents: Agent[];
}

export default function GroupChatConversationPage() {
    const router = useRouter();
    const params = useParams();
    const chatId = params.id as string;
    const [chat, setChat] = useState<GroupChat | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        fetchChat();
    }, [chatId]);

    const fetchChat = async () => {
        setIsLoading(true);
        try {
            const accessToken = Cookies.get("access_token");
            if (!accessToken) {
                throw new Error("Authentication token not found");
            }

            const response = await fetch(`http://localhost:8080/api/v1/chats/group/${chatId}/`, {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${accessToken}`,
                },
            });

            const data = await response.json();

            if (!response.ok) {
                if (response.status === 404) {
                    router.push("/dashboard");
                    return;
                }
                throw new Error(data.error || "Failed to fetch group chat");
            }

            setChat(data.chat);
        } catch (err) {
            const errorMessage =
                err instanceof Error
                    ? err.message
                    : "An error occurred while fetching the group chat";
            toast.error(errorMessage, {
                className: "bg-(--destructive) text-white border-none",
            });

            if (
                err instanceof Error &&
                (err.message.includes("You do not have permission to view this chat") ||
                    err.message.includes("Group chat not found"))
            ) {
                router.push("/dashboard");
            }
        } finally {
            setIsLoading(false);
        }
    };

    const formatAgentNames = (agents: Agent[]) => {
        return agents.map((agent) => agent.name).join(", ");
    };

    const handleBackClick = () => {
        router.push(`/group-chats/${chatId}`);
    };

    return (
        <ProtectedRoute>
            <div className="min-h-screen flex flex-col bg-(--background)">
                <DashboardNavbar />
                <div className="flex-1 container mx-auto px-4 pt-24 pb-8">
                    <Button
                        onClick={handleBackClick}
                        variant="outline"
                        className="font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--border) bg-(--background) text-(--foreground) hover:bg-(--muted) h-10 cursor-pointer mb-6"
                    >
                        <span className="relative z-10 flex items-center">
                            <ArrowLeft className="mr-2 h-4 w-4" />
                            Back to Chat Details
                        </span>
                        <span className="absolute inset-0 bg-(--muted)/50 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                    </Button>

                    {isLoading ? (
                        <div className="space-y-4">
                            <div className="flex justify-center items-center py-12">
                                <Loader2 className="h-8 w-8 animate-spin text-(--muted-foreground)" />
                            </div>
                        </div>
                    ) : chat ? (
                        <div className="flex flex-col h-[calc(100vh-180px)]">
                            <div className="flex items-center space-x-2 mb-4">
                                <h1 className="text-2xl font-bold tracking-tight">{chat.title}</h1>
                                <Badge
                                    variant="outline"
                                    className={`bg-(--primary)/10 text-(--primary) border-(--primary)/20 w-20 ml-2 ${
                                        chat.is_public ? "text-blue-300" : "text-green-300"
                                    }`}
                                >
                                    {chat.is_public ? "Public" : "Private"}
                                </Badge>
                            </div>
                            <p className="text-sm text-(--muted-foreground) mb-4">
                                Group conversation with {formatAgentNames(chat.agents)}
                            </p>

                            {/* Messages Container */}
                            <div className="flex-1 overflow-y-auto mb-4 border border-(--border) rounded-md p-4 bg-(--secondary)/30">
                                <div className="space-y-4">
                                    {/* Agent 1 Message */}
                                    <div className="flex items-start gap-2 max-w-[80%]">
                                        <div className="w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-700 overflow-hidden flex-shrink-0">
                                            {chat.agents[0] && chat.agents[0].id ? (
                                                <img
                                                    src={`https://api.dicebear.com/7.x/bottts/svg?seed=${chat.agents[0].id}`}
                                                    alt={chat.agents[0].name}
                                                    className="w-full h-full object-cover"
                                                />
                                            ) : (
                                                <div className="w-full h-full flex items-center justify-center text-gray-500">
                                                    <svg
                                                        xmlns="http://www.w3.org/2000/svg"
                                                        width="16"
                                                        height="16"
                                                        viewBox="0 0 24 24"
                                                        fill="none"
                                                        stroke="currentColor"
                                                        strokeWidth="2"
                                                        strokeLinecap="round"
                                                        strokeLinejoin="round"
                                                    >
                                                        <path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20z"></path>
                                                        <path d="M12 8a2 2 0 1 0 0 4 2 2 0 0 0 0-4z"></path>
                                                        <path d="M12 14a4 4 0 0 0-4 4"></path>
                                                    </svg>
                                                </div>
                                            )}
                                        </div>
                                        <div>
                                            <p className="text-xs font-medium text-(--primary) mb-1">
                                                {chat.agents[0]?.name || "Agent 1"}
                                            </p>
                                            <div className="bg-gray-100 dark:bg-gray-800 p-3 rounded-lg">
                                                <p className="text-sm">
                                                    Hello! I'm here to help with any questions about
                                                    the project architecture.
                                                </p>
                                            </div>
                                        </div>
                                    </div>

                                    {/* User Message */}
                                    <div className="flex items-start justify-end w-full">
                                        <div className="flex items-start gap-2 max-w-[80%] ml-auto">
                                            <div className="flex flex-col items-end">
                                                <p className="text-xs font-medium text-right text-(--primary) mb-1">
                                                    {chat.user.username}
                                                </p>
                                                <div className="bg-(--primary) text-(--primary-foreground) p-3 rounded-lg">
                                                    <p className="text-sm">
                                                        Hi team! I'd like to discuss the database
                                                        schema for our new feature.
                                                    </p>
                                                </div>
                                            </div>
                                            <div className="w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-700 overflow-hidden flex-shrink-0">
                                                <img
                                                    src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${chat.user.username}`}
                                                    alt={chat.user.username}
                                                    className="w-full h-full object-cover"
                                                />
                                            </div>
                                        </div>
                                    </div>

                                    {/* Agent 2 Message */}
                                    <div className="flex items-start gap-2 max-w-[80%]">
                                        <div className="w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-700 overflow-hidden flex-shrink-0">
                                            {chat.agents[1] && chat.agents[1].id ? (
                                                <img
                                                    src={`https://api.dicebear.com/7.x/bottts/svg?seed=${chat.agents[1].id}`}
                                                    alt={chat.agents[1].name}
                                                    className="w-full h-full object-cover"
                                                />
                                            ) : (
                                                <div className="w-full h-full flex items-center justify-center text-gray-500">
                                                    <svg
                                                        xmlns="http://www.w3.org/2000/svg"
                                                        width="16"
                                                        height="16"
                                                        viewBox="0 0 24 24"
                                                        fill="none"
                                                        stroke="currentColor"
                                                        strokeWidth="2"
                                                        strokeLinecap="round"
                                                        strokeLinejoin="round"
                                                    >
                                                        <path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20z"></path>
                                                        <path d="M12 8a2 2 0 1 0 0 4 2 2 0 0 0 0-4z"></path>
                                                        <path d="M12 14a4 4 0 0 0-4 4"></path>
                                                    </svg>
                                                </div>
                                            )}
                                        </div>
                                        <div>
                                            <p className="text-xs font-medium text-(--primary) mb-1">
                                                {chat.agents[1]?.name || "Agent 2"}
                                            </p>
                                            <div className="bg-gray-100 dark:bg-gray-800 p-3 rounded-lg">
                                                <p className="text-sm">
                                                    Great! I can help with database-related
                                                    questions. What specific aspects of the schema
                                                    are you interested in?
                                                </p>
                                            </div>
                                        </div>
                                    </div>

                                    {/* User Message */}
                                    <div className="flex items-start justify-end w-full">
                                        <div className="flex items-start gap-2 max-w-[80%] ml-auto">
                                            <div className="flex flex-col items-end">
                                                <p className="text-xs font-medium text-right text-(--primary) mb-1">
                                                    {chat.user.username}
                                                </p>
                                                <div className="bg-(--primary) text-(--primary-foreground) p-3 rounded-lg">
                                                    <p className="text-sm">
                                                        I'm wondering if we should use a relational
                                                        database or a NoSQL solution for storing
                                                        user activity logs.
                                                    </p>
                                                </div>
                                            </div>
                                            <div className="w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-700 overflow-hidden flex-shrink-0">
                                                <img
                                                    src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${chat.user.username}`}
                                                    alt={chat.user.username}
                                                    className="w-full h-full object-cover"
                                                />
                                            </div>
                                        </div>
                                    </div>

                                    {/* Agent 1 Message */}
                                    <div className="flex items-start gap-2 max-w-[80%]">
                                        <div className="w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-700 overflow-hidden flex-shrink-0">
                                            {chat.agents[0] && chat.agents[0].id ? (
                                                <img
                                                    src={`https://api.dicebear.com/7.x/bottts/svg?seed=${chat.agents[0].id}`}
                                                    alt={chat.agents[0].name}
                                                    className="w-full h-full object-cover"
                                                />
                                            ) : (
                                                <div className="w-full h-full flex items-center justify-center text-gray-500">
                                                    <svg
                                                        xmlns="http://www.w3.org/2000/svg"
                                                        width="16"
                                                        height="16"
                                                        viewBox="0 0 24 24"
                                                        fill="none"
                                                        stroke="currentColor"
                                                        strokeWidth="2"
                                                        strokeLinecap="round"
                                                        strokeLinejoin="round"
                                                    >
                                                        <path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20z"></path>
                                                        <path d="M12 8a2 2 0 1 0 0 4 2 2 0 0 0 0-4z"></path>
                                                        <path d="M12 14a4 4 0 0 0-4 4"></path>
                                                    </svg>
                                                </div>
                                            )}
                                        </div>
                                        <div>
                                            <p className="text-xs font-medium text-(--primary) mb-1">
                                                {chat.agents[0]?.name || "Agent 1"}
                                            </p>
                                            <div className="bg-gray-100 dark:bg-gray-800 p-3 rounded-lg">
                                                <p className="text-sm">
                                                    From an architectural perspective, it depends on
                                                    your query patterns. If you need complex queries
                                                    and transactions, a relational DB might be
                                                    better.
                                                </p>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Agent 2 Message */}
                                    <div className="flex items-start gap-2 max-w-[80%]">
                                        <div className="w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-700 overflow-hidden flex-shrink-0">
                                            {chat.agents[1] && chat.agents[1].id ? (
                                                <img
                                                    src={`https://api.dicebear.com/7.x/bottts/svg?seed=${chat.agents[1].id}`}
                                                    alt={chat.agents[1].name}
                                                    className="w-full h-full object-cover"
                                                />
                                            ) : (
                                                <div className="w-full h-full flex items-center justify-center text-gray-500">
                                                    <svg
                                                        xmlns="http://www.w3.org/2000/svg"
                                                        width="16"
                                                        height="16"
                                                        viewBox="0 0 24 24"
                                                        fill="none"
                                                        stroke="currentColor"
                                                        strokeWidth="2"
                                                        strokeLinecap="round"
                                                        strokeLinejoin="round"
                                                    >
                                                        <path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20z"></path>
                                                        <path d="M12 8a2 2 0 1 0 0 4 2 2 0 0 0 0-4z"></path>
                                                        <path d="M12 14a4 4 0 0 0-4 4"></path>
                                                    </svg>
                                                </div>
                                            )}
                                        </div>
                                        <div>
                                            <p className="text-xs font-medium text-(--primary) mb-1">
                                                {chat.agents[1]?.name || "Agent 2"}
                                            </p>
                                            <div className="bg-gray-100 dark:bg-gray-800 p-3 rounded-lg">
                                                <p className="text-sm">
                                                    I agree with that assessment. For high-volume
                                                    activity logs, NoSQL can offer better write
                                                    performance and scalability. MongoDB or
                                                    Cassandra might be good options if your primary
                                                    concern is ingestion speed and you don't need
                                                    complex joins.
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Input Box */}
                            <div className="flex items-center space-x-2">
                                <div className="flex-1">
                                    <input
                                        type="text"
                                        placeholder="Type your message..."
                                        className="w-full p-3 rounded-md border border-(--border) bg-(--background) focus:outline-none focus:ring-2 focus:ring-(--primary) focus:border-transparent"
                                    />
                                </div>
                                <Button className="h-12 w-12 p-0 rounded-md font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--border) bg-(--background) text-(--foreground) hover:bg-(--muted) cursor-pointer">
                                    <span className="relative z-10">
                                        <svg
                                            xmlns="http://www.w3.org/2000/svg"
                                            viewBox="0 0 24 24"
                                            fill="none"
                                            stroke="currentColor"
                                            strokeWidth="2"
                                            strokeLinecap="round"
                                            strokeLinejoin="round"
                                            className="h-5 w-5 text-(--foreground)"
                                        >
                                            <path d="m22 2-7 20-4-9-9-4Z" />
                                            <path d="M22 2 11 13" />
                                        </svg>
                                    </span>
                                    <span className="absolute inset-0 bg-(--muted)/50 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                                    <span className="sr-only">Send message</span>
                                </Button>
                            </div>
                        </div>
                    ) : (
                        <div className="flex flex-col items-center justify-center py-12 text-center border rounded-md bg-(--secondary)">
                            <MessageCircle className="h-12 w-12 text-(--muted-foreground) mb-3" />
                            <h3 className="text-lg font-medium mb-1">Chat not found</h3>
                            <p className="text-sm text-(--muted-foreground) mb-4">
                                The chat you're looking for doesn't exist or you don't have
                                permission to view it.
                            </p>
                            <Button
                                onClick={() => router.push("/dashboard")}
                                className="font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--primary) bg-(--primary) text-(--primary-foreground) dark:bg-(--primary) dark:text-(--primary-foreground) dark:border-(--primary) h-10 cursor-pointer"
                            >
                                <span className="relative z-10">Go to Dashboard</span>
                                <span className="absolute inset-0 bg-(--primary-foreground)/10 dark:bg-(--primary-foreground)/20 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                            </Button>
                        </div>
                    )}
                </div>
            </div>
        </ProtectedRoute>
    );
}
