"use client";

/* eslint-disable @next/next/no-img-element */

import { selectUser } from "@/app/store/slices/userSlice";
import { DashboardNavbar } from "@/components/dashboard-navbar";
import { ProtectedRoute } from "@/components/protected-route";
import { SelectLLMDialog } from "@/components/select-llm-dialog";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import Cookies from "js-cookie";
import { ArrowLeft, MessageCircle, Send } from "lucide-react";
import { useParams, useRouter } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";
import { useSelector } from "react-redux";

import dynamic from "next/dynamic";
import { toast } from "sonner";

const ReactMarkdown = dynamic(() => import("react-markdown"), { ssr: false });

interface Chat {
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
    agent: {
        id: string;
        name: string;
        avatar_url?: string;
    };
}

interface Message {
    id: string;
    content: string;
    sender: "user" | "agent";
    timestamp: Date;
}

interface ConversationSession {
    id: string;
    single_chat: {
        id: string;
        title: string;
        agent: {
            id: string;
            name: string;
            description: string;
            avatar_url?: string;
        };
    };
    is_active: boolean;
    selector_prompt: string;
    llm: {
        id: string;
        base_url: string;
        model: string;
    };
    websocket_url: string;
    created_at: string;
    updated_at: string;
}

interface WebSocketMessage {
    source: string;
    models_usage?: Record<string, unknown>;
    metadata?: {
        error?: string;
        agent?: {
            id: string;
            name: string;
            avatar_url?: string;
        };
    };
    content: string | Record<string, unknown>;
    type: string;
}

interface CustomWebSocketClient {
    emit: (event: string, data: Record<string, unknown>) => void;
    disconnect: () => void;
}

export default function ChatConversationPage() {
    const router = useRouter();
    const params = useParams();
    const chatId = params.id as string;
    const [chat, setChat] = useState<Chat | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [isSelectLLMDialogOpen, setIsSelectLLMDialogOpen] = useState(false);
    const [messages, setMessages] = useState<Message[]>([]);
    const [inputText, setInputText] = useState("");
    const [isAgentTyping, setIsAgentTyping] = useState(false);
    const [sessionData, setSessionData] = useState<ConversationSession | null>(null);
    const socketRef = useRef<CustomWebSocketClient | null>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const currentUser = useSelector(selectUser);

    const fetchChatDetails = useCallback(async () => {
        setIsLoading(true);
        try {
            const accessToken = Cookies.get("access_token");
            if (!accessToken) {
                throw new Error("Authentication token not found");
            }

            const response = await fetch(
                `${process.env.NEXT_PUBLIC_API_URL}/chats/single/${chatId}/`,
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
                if (response.status === 404) {
                    toast.error("Chat not found", {
                        className: "bg-(--destructive) text-white border-none",
                    });
                    router.push("/dashboard");
                    return;
                } else if (response.status === 403) {
                    toast.error("You do not have permission to view this chat", {
                        className: "bg-(--destructive) text-white border-none",
                    });
                    router.push("/dashboard");
                    return;
                } else {
                    throw new Error(data.error || "Failed to fetch chat details");
                }
            }

            setChat(data.chat);
        } catch (err) {
            const errorMessage =
                err instanceof Error
                    ? err.message
                    : "An error occurred while fetching chat details";
            toast.error(errorMessage, {
                className: "bg-(--destructive) text-white border-none",
            });
            router.push("/dashboard");
        } finally {
            setIsLoading(false);
        }
    }, [chatId, router]);

    useEffect(() => {
        fetchChatDetails();
    }, [fetchChatDetails]);

    useEffect(() => {
        if (chat) {
            setIsSelectLLMDialogOpen(true);
        }
    }, [chat]);

    useEffect(() => {
        if (messagesEndRef.current) {
            messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
        }
    }, [messages, isAgentTyping]);

    useEffect(() => {
        const handleBeforeUnload = () => {
            if (socketRef.current) {
                socketRef.current.disconnect();
            }
        };

        const handlePopState = () => {
            if (socketRef.current) {
                socketRef.current.disconnect();
            }
        };

        window.addEventListener("beforeunload", handleBeforeUnload);
        window.addEventListener("popstate", handlePopState);

        return () => {
            window.removeEventListener("beforeunload", handleBeforeUnload);
            window.removeEventListener("popstate", handlePopState);

            if (socketRef.current) {
                socketRef.current.disconnect();
            }
        };
    }, []);

    const fetchPreviousMessages = async (singleChatId: string) => {
        try {
            const accessToken = Cookies.get("access_token");
            if (!accessToken) {
                throw new Error("Authentication token not found");
            }

            const response = await fetch(
                `${process.env.NEXT_PUBLIC_API_URL}/chats/single/${singleChatId}/messages/`,
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
                if (response.status === 404 && data.error === "No messages found in this chat.") {
                    if (messages.length === 0 && sessionData?.single_chat?.agent) {
                        const initialMessage: Message = {
                            id: "initial-message",
                            content: `Hello! I&apos;m ${sessionData.single_chat.agent.name}. How can I help you today?`,
                            sender: "agent",
                            timestamp: new Date(),
                        };
                        setMessages([initialMessage]);
                    }
                    return;
                } else {
                    throw new Error(data.error || "Failed to fetch previous messages");
                }
            }

            if (data.messages && data.messages.length > 0) {
                const formattedMessages: Message[] = data.messages.map(
                    (msg: {
                        id: string;
                        content: string;
                        sender: "user" | "agent";
                        created_at: string;
                    }) => ({
                        id: msg.id,
                        content: msg.content,
                        sender: msg.sender,
                        timestamp: new Date(msg.created_at),
                    })
                );

                setMessages(formattedMessages);
            } else {
                if (messages.length === 0 && sessionData?.single_chat?.agent) {
                    const initialMessage: Message = {
                        id: "initial-message",
                        content: `Hello! I&apos;m ${sessionData.single_chat.agent.name}. How can I help you today?`,
                        sender: "agent",
                        timestamp: new Date(),
                    };
                    setMessages([initialMessage]);
                }
            }
        } catch (err) {
            console.error("Error fetching previous messages:", err);
            if (messages.length > 0) {
                return;
            }

            const errorMessage = err instanceof Error ? err.message : "";
            if (errorMessage.includes("No messages found")) {
                if (sessionData?.single_chat?.agent) {
                    const initialMessage: Message = {
                        id: "initial-message",
                        content: `Hello! I&apos;m ${sessionData.single_chat.agent.name}. How can I help you today?`,
                        sender: "agent",
                        timestamp: new Date(),
                    };
                    setMessages([initialMessage]);
                }
            } else {
                if (sessionData?.single_chat?.agent) {
                    const initialMessage: Message = {
                        id: "initial-message",
                        content: `Hello! I&apos;m ${sessionData.single_chat.agent.name}. How can I help you today?`,
                        sender: "agent",
                        timestamp: new Date(),
                    };
                    setMessages([initialMessage]);
                }
            }
        }
    };

    const createConversationSession = async (llmId: string) => {
        if (!chat) return;

        try {
            const accessToken = Cookies.get("access_token");
            if (!accessToken) {
                throw new Error("Authentication token not found");
            }

            const response = await fetch(
                `${process.env.NEXT_PUBLIC_API_URL}/conversation/session/`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${accessToken}`,
                    },
                    body: JSON.stringify({
                        chat_id: chatId,
                        llm_id: llmId,
                    }),
                }
            );

            const data = await response.json();

            if (!response.ok) {
                const errorMessages = [];
                if (data.error && typeof data.error === "object") {
                    for (const field in data.error) {
                        errorMessages.push(...data.error[field]);
                    }
                }
                throw new Error(
                    errorMessages.length > 0
                        ? errorMessages.join(", ")
                        : data.error || "Failed to create conversation session"
                );
            }

            setSessionData(data.session);

            const welcomeMessage: Message = {
                id: "welcome-message",
                content: `Hello! I&apos;m ${data.session.single_chat.agent.name}. How can I help you today?`,
                sender: "agent",
                timestamp: new Date(),
            };
            setMessages([welcomeMessage]);

            await fetchPreviousMessages(data.session.single_chat.id);

            connectToWebSocket(data.session.websocket_url);
        } catch (err) {
            const errorMessage =
                err instanceof Error
                    ? err.message
                    : "An error occurred while creating conversation session";
            toast.error(errorMessage, {
                style: {
                    backgroundColor: "var(--destructive)",
                    color: "white",
                    border: "none",
                },
            });
            router.push(`/chats/${chatId}`);
        }
    };
    const connectToWebSocket = (websocketUrl: string) => {
        const accessToken = Cookies.get("access_token");
        if (!accessToken) {
            toast.error("Authentication token not found", {
                style: {
                    backgroundColor: "var(--destructive)",
                    color: "white",
                    border: "none",
                },
            });
            return;
        }

        const wsUrlWithToken = `${websocketUrl}${
            websocketUrl.includes("?") ? "&" : "?"
        }token=${accessToken}`;
        const socket = new WebSocket(wsUrlWithToken);

        socket.onopen = () => {};

        socket.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data) as WebSocketMessage;

                if (message.type === "TextMessage") {
                    if (message.content === "connected") {
                    } else {
                        setIsAgentTyping(false);
                        const content =
                            typeof message.content === "string"
                                ? message.content
                                : JSON.stringify(message.content);

                        const agentMessage: Message = {
                            id: `agent-${Date.now()}`,
                            content: content,
                            sender: "agent",
                            timestamp: new Date(),
                        };
                        setMessages((prevMessages) => [...prevMessages, agentMessage]);
                    }
                } else if (message.type === "ToolCallRequestEvent") {
                    setIsAgentTyping(true);
                } else if (message.type === "ToolCallExecutionEvent") {
                    setIsAgentTyping(true);
                }
            } catch {}
        };

        socket.onclose = () => {};

        socket.onerror = () => {
            toast.error("Error connecting to conversation session", {
                style: {
                    backgroundColor: "var(--destructive)",
                    color: "white",
                    border: "none",
                },
            });
        };

        const socketIOLike: CustomWebSocketClient = {
            emit: (_event: string, data: Record<string, unknown>) => {
                if (socket.readyState === socket.OPEN) {
                    socket.send(JSON.stringify(data));
                }
            },
            disconnect: () => {
                socket.close();
            },
        };

        socketRef.current = socketIOLike;
    };

    const handleSendMessage = () => {
        if (!inputText.trim() || !socketRef.current) return;

        const userMessage: Message = {
            id: `user-${Date.now()}`,
            content: inputText,
            sender: "user",
            timestamp: new Date(),
        };
        setMessages((prevMessages) => [...prevMessages, userMessage]);

        socketRef.current.emit("message", {
            source: "user",
            content: inputText,
        });

        setInputText("");
        setIsAgentTyping(true);
    };

    const handleInputKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    };

    const handleBackClick = () => {
        if (socketRef.current) {
            socketRef.current.disconnect();
        }
        router.push(`/chats/${chatId}`);
    };

    const handleLLMDialogOpenChange = async (open: boolean, selectedLLMId?: string) => {
        if (!open) {
            if (selectedLLMId) {
                try {
                    if (socketRef.current) {
                        socketRef.current.disconnect();
                    }
                    await createConversationSession(selectedLLMId);
                } catch {}
            } else {
                if (socketRef.current) {
                    socketRef.current.disconnect();
                }
                router.push(`/chats/${chatId}`);
            }
        }
        setIsSelectLLMDialogOpen(open);
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
                            <Skeleton className="h-12 w-3/4" />
                            <Skeleton className="h-8 w-1/2" />
                            <div className="mt-8">
                                <Skeleton className="h-64 w-full" />
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
                                Conversation with {chat.agent.name}
                            </p>

                            <div className="flex-1 overflow-y-auto mb-4 border border-(--border) rounded-md p-4 bg-(--secondary)/30">
                                <div className="space-y-4">
                                    {messages.map((message) => (
                                        <div
                                            key={message.id}
                                            className={`flex items-start ${
                                                message.sender === "user"
                                                    ? "justify-end w-full"
                                                    : "gap-2 max-w-[80%]"
                                            }`}
                                        >
                                            {message.sender === "agent" && (
                                                <div className="w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-700 overflow-hidden flex-shrink-0">
                                                    {sessionData?.single_chat?.agent?.avatar_url ? (
                                                        <img
                                                            src={
                                                                sessionData.single_chat.agent
                                                                    .avatar_url
                                                            }
                                                            alt={chat.agent.name}
                                                            className="w-full h-full object-cover"
                                                        />
                                                    ) : chat.agent && chat.agent.id ? (
                                                        <img
                                                            src={`https://api.dicebear.com/7.x/bottts/svg?seed=${chat.agent.id}`}
                                                            alt={chat.agent.name}
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
                                            )}

                                            {message.sender === "agent" ? (
                                                <div>
                                                    <p className="text-xs font-medium text-(--primary) mb-1">
                                                        {chat.agent.name}
                                                    </p>
                                                    <div className="bg-gray-100 dark:bg-gray-800 p-3 rounded-lg">
                                                        <div className="text-sm markdown-content">
                                                            <ReactMarkdown
                                                                components={{
                                                                    strong: (props) => (
                                                                        <span
                                                                            className="font-bold"
                                                                            {...props}
                                                                        />
                                                                    ),
                                                                    em: (props) => (
                                                                        <span
                                                                            className="italic"
                                                                            {...props}
                                                                        />
                                                                    ),
                                                                    ul: (props) => (
                                                                        <ul
                                                                            className="list-disc pl-5 my-2"
                                                                            {...props}
                                                                        />
                                                                    ),
                                                                    ol: (props) => (
                                                                        <ol
                                                                            className="list-decimal pl-5 my-2"
                                                                            {...props}
                                                                        />
                                                                    ),
                                                                    li: (props) => (
                                                                        <li
                                                                            className="my-1"
                                                                            {...props}
                                                                        />
                                                                    ),
                                                                    p: (props) => (
                                                                        <p
                                                                            className="my-2"
                                                                            {...props}
                                                                        />
                                                                    ),
                                                                }}
                                                            >
                                                                {message.content}
                                                            </ReactMarkdown>
                                                        </div>
                                                    </div>
                                                </div>
                                            ) : (
                                                <div className="flex items-start gap-2 max-w-[80%] ml-auto">
                                                    <div className="flex flex-col items-end">
                                                        <p className="text-xs font-medium text-right text-(--primary) mb-1">
                                                            {currentUser?.full_name ||
                                                                chat.user.username}
                                                        </p>
                                                        <div className="bg-(--primary) text-(--primary-foreground) p-3 rounded-lg">
                                                            <p className="text-sm">
                                                                {message.content}
                                                            </p>
                                                        </div>
                                                    </div>
                                                    <div className="w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-700 overflow-hidden flex-shrink-0">
                                                        {currentUser?.avatar_url ? (
                                                            <img
                                                                src={currentUser.avatar_url}
                                                                alt={currentUser.username || "You"}
                                                                className="w-full h-full object-cover"
                                                            />
                                                        ) : (
                                                            <img
                                                                src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${
                                                                    currentUser?.username ||
                                                                    chat.user.username
                                                                }`}
                                                                alt={
                                                                    currentUser?.username ||
                                                                    chat.user.username
                                                                }
                                                                className="w-full h-full object-cover"
                                                            />
                                                        )}
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                    ))}

                                    {isAgentTyping && (
                                        <div className="flex items-start gap-2 max-w-[80%]">
                                            <div className="w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-700 overflow-hidden flex-shrink-0">
                                                {sessionData?.single_chat?.agent?.avatar_url ? (
                                                    <img
                                                        src={
                                                            sessionData.single_chat.agent.avatar_url
                                                        }
                                                        alt={chat.agent.name}
                                                        className="w-full h-full object-cover"
                                                    />
                                                ) : chat.agent && chat.agent.id ? (
                                                    <img
                                                        src={`https://api.dicebear.com/7.x/bottts/svg?seed=${chat.agent.id}`}
                                                        alt={chat.agent.name}
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
                                                    {chat.agent.name}
                                                </p>
                                                <div className="bg-gray-100 dark:bg-gray-800 p-3 rounded-lg">
                                                    <div className="flex space-x-1">
                                                        <div
                                                            className="w-2 h-2 bg-(--primary) rounded-full animate-bounce"
                                                            style={{ animationDelay: "0ms" }}
                                                        ></div>
                                                        <div
                                                            className="w-2 h-2 bg-(--primary) rounded-full animate-bounce"
                                                            style={{ animationDelay: "300ms" }}
                                                        ></div>
                                                        <div
                                                            className="w-2 h-2 bg-(--primary) rounded-full animate-bounce"
                                                            style={{ animationDelay: "600ms" }}
                                                        ></div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    )}

                                    <div ref={messagesEndRef} />
                                </div>
                            </div>

                            <div className="flex items-center space-x-2">
                                <div className="flex-1">
                                    <input
                                        type="text"
                                        placeholder="Type your message..."
                                        value={inputText}
                                        onChange={(e) => setInputText(e.target.value)}
                                        onKeyDown={handleInputKeyDown}
                                        disabled={isAgentTyping || !socketRef.current}
                                        className="w-full p-3 rounded-md border border-(--border) bg-(--background) focus:outline-none focus:ring-2 focus:ring-(--primary) focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
                                    />
                                </div>
                                <Button
                                    onClick={handleSendMessage}
                                    disabled={
                                        !inputText.trim() || isAgentTyping || !socketRef.current
                                    }
                                    className="h-12 w-12 p-0 rounded-md font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--border) bg-(--background) text-(--foreground) hover:bg-(--muted) cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    <span className="relative z-10">
                                        <Send className="h-5 w-5 text-(--foreground)" />
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
                                The chat you&apos;re looking for doesn&apos;t exist or you
                                don&apos;t have permission to view it.
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

            {chat && (
                <SelectLLMDialog
                    open={isSelectLLMDialogOpen}
                    onOpenChange={handleLLMDialogOpenChange}
                    chatId={chatId}
                    chatType="single"
                    organizationId={chat.organization.id}
                />
            )}
        </ProtectedRoute>
    );
}
