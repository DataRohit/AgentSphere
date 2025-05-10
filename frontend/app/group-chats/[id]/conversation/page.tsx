"use client";

/* eslint-disable @next/next/no-img-element */

import { selectUser } from "@/app/store/slices/userSlice";
import { DashboardNavbar } from "@/components/dashboard-navbar";
import { ProtectedRoute } from "@/components/protected-route";
import { SelectLLMDialog } from "@/components/select-llm-dialog";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import Cookies from "js-cookie";
import { ArrowLeft, Loader2, MessageCircle, Send } from "lucide-react";
import dynamic from "next/dynamic";
import { useParams, useRouter } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";
import { useSelector } from "react-redux";
import { toast } from "sonner";

const ReactMarkdown = dynamic(() => import("react-markdown"), { ssr: false });

interface Agent {
    id: string;
    name: string;
    description?: string;
    avatar_url?: string;
}

interface Message {
    id: string;
    content: string;
    sender: "user" | "agent";
    agentId?: string;
    agentName?: string;
    agentAvatarUrl?: string;
    timestamp: Date;
}

interface ConversationSession {
    id: string;
    group_chat: {
        id: string;
        title: string;
        agents: Agent[];
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

interface ModelsUsage {
    [key: string]: {
        input_tokens: number;
        output_tokens: number;
        total_tokens: number;
    };
}

interface WebSocketMessage {
    source: string;
    models_usage: ModelsUsage;
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
    const [isSelectLLMDialogOpen, setIsSelectLLMDialogOpen] = useState(false);
    const [messages, setMessages] = useState<Message[]>([]);
    const [inputText, setInputText] = useState("");
    const [isAgentTyping, setIsAgentTyping] = useState(false);
    const [sessionData, setSessionData] = useState<ConversationSession | null>(null);
    const socketRef = useRef<CustomWebSocketClient | null>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const currentUser = useSelector(selectUser);

    const fetchChat = useCallback(async () => {
        setIsLoading(true);
        try {
            const accessToken = Cookies.get("access_token");
            if (!accessToken) {
                throw new Error("Authentication token not found");
            }

            const response = await fetch(
                `${process.env.NEXT_PUBLIC_API_URL}/chats/group/${chatId}/`,
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
    }, [chatId, router]);

    useEffect(() => {
        fetchChat();
    }, [fetchChat]);

    useEffect(() => {
        if (chat) {
            setIsSelectLLMDialogOpen(true);
        }
    }, [chat]);

    const formatAgentNames = (agents: Agent[]) => {
        return agents.map((agent) => agent.name).join(", ");
    };

    const handleBackClick = () => {
        if (socketRef.current) {
            socketRef.current.disconnect();
        }
        router.push(`/group-chats/${chatId}`);
    };

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

    useEffect(() => {
        if (messagesEndRef.current) {
            messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
        }
    }, [messages, isAgentTyping]);

    const fetchPreviousMessages = async (groupChatId: string) => {
        try {
            const accessToken = Cookies.get("access_token");
            if (!accessToken) {
                throw new Error("Authentication token not found");
            }

            const response = await fetch(
                `${process.env.NEXT_PUBLIC_API_URL}/chats/group/${groupChatId}/messages/`,
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
                    if (messages.length === 0 && sessionData?.group_chat?.agents) {
                        const initialMessage: Message = {
                            id: "initial-message",
                            content: `Hello! Welcome to the group chat with ${sessionData.group_chat.agents
                                .map((agent) => agent.name)
                                .join(", ")}. How can we help you today?`,
                            sender: "agent",
                            agentId: sessionData.group_chat.agents[0].id,
                            agentName: sessionData.group_chat.agents[0].name,
                            agentAvatarUrl: sessionData.group_chat.agents[0].avatar_url,
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
                        agent?: {
                            id: string;
                            name: string;
                            avatar_url?: string;
                        };
                        created_at: string;
                    }) => {
                        if (msg.sender === "agent") {
                            return {
                                id: msg.id,
                                content: msg.content,
                                sender: msg.sender,
                                agentId: msg.agent?.id,
                                agentName: msg.agent?.name,
                                agentAvatarUrl: msg.agent?.avatar_url,
                                timestamp: new Date(msg.created_at),
                            };
                        } else {
                            return {
                                id: msg.id,
                                content: msg.content,
                                sender: msg.sender,
                                timestamp: new Date(msg.created_at),
                            };
                        }
                    }
                );

                setMessages(formattedMessages);
            } else {
                if (messages.length === 0 && sessionData?.group_chat?.agents) {
                    const initialMessage: Message = {
                        id: "initial-message",
                        content: `Hello! Welcome to the group chat with ${sessionData.group_chat.agents
                            .map((agent) => agent.name)
                            .join(", ")}. How can we help you today?`,
                        sender: "agent",
                        agentId: sessionData.group_chat.agents[0].id,
                        agentName: sessionData.group_chat.agents[0].name,
                        agentAvatarUrl: sessionData.group_chat.agents[0].avatar_url,
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

            if (sessionData?.group_chat?.agents) {
                const initialMessage: Message = {
                    id: "initial-message",
                    content: `Hello! Welcome to the group chat with ${sessionData.group_chat.agents
                        .map((agent) => agent.name)
                        .join(", ")}. How can we help you today?`,
                    sender: "agent",
                    agentId: sessionData.group_chat.agents[0].id,
                    agentName: sessionData.group_chat.agents[0].name,
                    agentAvatarUrl: sessionData.group_chat.agents[0].avatar_url,
                    timestamp: new Date(),
                };
                setMessages([initialMessage]);
            }
        }
    };

    const createConversationSession = async (llmId: string) => {
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
                throw new Error(data.error || "Failed to create conversation session");
            }

            setSessionData(data.session);

            if (data.session.group_chat?.agents && data.session.group_chat.agents.length > 0) {
                const welcomeMessage: Message = {
                    id: "welcome-message",
                    content: `Hello! Welcome to the group chat with ${data.session.group_chat.agents
                        .map((agent: Agent) => agent.name)
                        .join(", ")}. How can we help you today?`,
                    sender: "agent",
                    agentId: data.session.group_chat.agents[0].id,
                    agentName: data.session.group_chat.agents[0].name,
                    agentAvatarUrl: data.session.group_chat.agents[0].avatar_url,
                    timestamp: new Date(),
                };
                setMessages([welcomeMessage]);
            }

            await fetchPreviousMessages(data.session.group_chat.id);

            connectToWebSocket(data.session.websocket_url);
        } catch (err) {
            const errorMessage =
                err instanceof Error
                    ? err.message
                    : "An error occurred while creating the conversation session";
            toast.error(errorMessage, {
                className: "bg-(--destructive) text-white border-none",
            });
        }
    };

    const connectToWebSocket = (websocketUrl: string) => {
        const accessToken = Cookies.get("access_token");
        if (!accessToken) {
            toast.error("Authentication token not found", {
                className: "bg-(--destructive) text-white border-none",
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
                    if (message.source === "server" && message.content === "connected") {
                        setIsAgentTyping(false);
                        return;
                    }

                    if (message.source !== "user") {
                        setIsAgentTyping(false);

                        let agentId = undefined;
                        let agentName = undefined;
                        let agentAvatarUrl = undefined;

                        if (message.metadata && message.metadata.agent) {
                            agentId = message.metadata.agent.id;
                            agentName = message.metadata.agent.name;
                            agentAvatarUrl = message.metadata.agent.avatar_url;
                        } else if (sessionData?.group_chat?.agents) {
                            let agent = null;

                            const normalizedSource = message.source
                                .toLowerCase()
                                .replace(/[^a-z0-9]/g, "");

                            for (const a of sessionData.group_chat.agents) {
                                if (a.name === message.source) {
                                    agent = a;
                                    break;
                                }

                                if (a.name.toLowerCase() === message.source.toLowerCase()) {
                                    agent = a;
                                    break;
                                }

                                const normalizedAgentName = a.name
                                    .toLowerCase()
                                    .replace(/[^a-z0-9]/g, "");
                                if (normalizedAgentName === normalizedSource) {
                                    agent = a;
                                    break;
                                }

                                if (
                                    normalizedAgentName.includes(normalizedSource) ||
                                    normalizedSource.includes(normalizedAgentName)
                                ) {
                                    agent = a;
                                    break;
                                }
                            }

                            if (agent) {
                                agentId = agent.id;
                                agentName = agent.name;
                                agentAvatarUrl = agent.avatar_url;
                            } else {
                                const readableName = message.source
                                    .replace(/([A-Z])/g, " $1")
                                    .replace(/\b\w/g, (c) => c.toUpperCase())
                                    .trim();

                                agentName = readableName;

                                if (sessionData.group_chat.agents.length > 0) {
                                    agentId = sessionData.group_chat.agents[0].id;
                                    agentAvatarUrl = sessionData.group_chat.agents[0].avatar_url;
                                }
                            }
                        }

                        const content =
                            typeof message.content === "string"
                                ? message.content
                                : JSON.stringify(message.content);

                        const newMessage: Message = {
                            id: Date.now().toString(),
                            content: content,
                            sender: "agent",
                            agentId,
                            agentName,
                            agentAvatarUrl,
                            timestamp: new Date(),
                        };

                        setMessages((prevMessages) => [...prevMessages, newMessage]);
                    }
                } else if (message.type === "TypingMessage" && message.source !== "user") {
                    setIsAgentTyping(true);
                }
            } catch {}
        };

        socket.onclose = () => {};

        socket.onerror = () => {
            toast.error("Error connecting to chat server", {
                className: "bg-(--destructive) text-white border-none",
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

        const newMessage: Message = {
            id: Date.now().toString(),
            content: inputText,
            sender: "user",
            timestamp: new Date(),
        };

        setMessages((prevMessages) => [...prevMessages, newMessage]);

        socketRef.current.emit("message", {
            source: "user",
            content: inputText,
        });

        setInputText("");
        setIsAgentTyping(true);
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
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
                router.push(`/group-chats/${chatId}`);
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

                            <div className="flex-1 overflow-y-auto mb-4 border border-(--border) rounded-md p-4 bg-(--secondary)/30">
                                <div className="space-y-4">
                                    {messages.map((message) => {
                                        return (
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
                                                        {message.agentAvatarUrl ? (
                                                            <img
                                                                src={message.agentAvatarUrl}
                                                                alt={message.agentName || "Agent"}
                                                                className="w-full h-full object-cover"
                                                            />
                                                        ) : message.agentId ? (
                                                            <img
                                                                src={`https://api.dicebear.com/7.x/bottts/svg?seed=${message.agentId}`}
                                                                alt={message.agentName || "Agent"}
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
                                                            {message.agentName || "Agent"}
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
                                                                    chat?.user?.username ||
                                                                    "You"}
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
                                                                    alt={
                                                                        currentUser.username ||
                                                                        "You"
                                                                    }
                                                                    className="w-full h-full object-cover"
                                                                />
                                                            ) : (
                                                                <img
                                                                    src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${
                                                                        currentUser?.username ||
                                                                        chat?.user?.username ||
                                                                        "user"
                                                                    }`}
                                                                    alt={
                                                                        currentUser?.username ||
                                                                        chat?.user?.username ||
                                                                        "You"
                                                                    }
                                                                    className="w-full h-full object-cover"
                                                                />
                                                            )}
                                                        </div>
                                                    </div>
                                                )}
                                            </div>
                                        );
                                    })}

                                    {isAgentTyping && (
                                        <div className="flex items-start gap-2 max-w-[80%]">
                                            <div className="w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-700 overflow-hidden flex-shrink-0">
                                                {sessionData?.group_chat?.agents &&
                                                sessionData.group_chat.agents[0]?.avatar_url ? (
                                                    <img
                                                        src={
                                                            sessionData.group_chat.agents[0]
                                                                .avatar_url
                                                        }
                                                        alt={sessionData.group_chat.agents[0].name}
                                                        className="w-full h-full object-cover"
                                                    />
                                                ) : sessionData?.group_chat?.agents &&
                                                  sessionData.group_chat.agents[0]?.id ? (
                                                    <img
                                                        src={`https://api.dicebear.com/7.x/bottts/svg?seed=${sessionData.group_chat.agents[0].id}`}
                                                        alt={sessionData.group_chat.agents[0].name}
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
                                                    {(sessionData?.group_chat?.agents &&
                                                        sessionData.group_chat.agents[0]?.name) ||
                                                        "Agent"}
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
                                        className="w-full p-3 rounded-md border border-(--border) bg-(--background) focus:outline-none focus:ring-2 focus:ring-(--primary) focus:border-transparent"
                                        value={inputText}
                                        onChange={(e) => setInputText(e.target.value)}
                                        onKeyDown={handleKeyDown}
                                        disabled={!socketRef.current}
                                    />
                                </div>
                                <Button
                                    className="h-12 w-12 p-0 rounded-md font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--border) bg-(--background) text-(--foreground) hover:bg-(--muted) cursor-pointer"
                                    onClick={handleSendMessage}
                                    disabled={!socketRef.current || !inputText.trim()}
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
                    chatType="group"
                    organizationId={chat.organization.id}
                />
            )}
        </ProtectedRoute>
    );
}
