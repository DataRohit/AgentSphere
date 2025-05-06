"use client";

import { useAppSelector } from "@/app/store/hooks";
import { selectUser } from "@/app/store/slices/userSlice";
import { DashboardNavbar } from "@/components/dashboard-navbar";
import { DeleteAgentDialog } from "@/components/delete-agent-dialog";
import { ProtectedRoute } from "@/components/protected-route";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { UpdateAgentDialog } from "@/components/update-agent-dialog";
import { motion } from "framer-motion";
import Cookies from "js-cookie";
import {
    AlertCircle,
    ArrowLeft,
    Bot,
    Calendar,
    Cpu,
    Globe,
    Loader2,
    MessageSquare,
    Pencil,
    Server,
    Trash2,
    User,
    Wrench,
} from "lucide-react";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { toast } from "sonner";

interface Tool {
    id: string;
    name: string;
    description: string;
}

interface MCPServer {
    id: string;
    name: string;
    url: string;
    tools: Tool[];
}

interface LLM {
    id: string;
    base_url: string;
    model: string;
}

interface Agent {
    id: string;
    name: string;
    description: string;
    system_prompt: string;
    avatar_url: string;
    created_at: string;
    updated_at: string;
    organization: {
        id: string;
        name: string;
    };
    user: {
        id: string;
        username: string;
        email: string;
    };
    llm: LLM;
    mcp_servers: MCPServer[];
}

export default function AgentDetailPage() {
    const router = useRouter();
    const params = useParams();
    const agentId = params.id as string;
    const currentUser = useAppSelector(selectUser);

    const [agent, setAgent] = useState<Agent | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [referrer, setReferrer] = useState<string | null>(null);
    const [isUpdateDialogOpen, setIsUpdateDialogOpen] = useState(false);
    const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);

    useEffect(() => {
        if (typeof window !== "undefined") {
            const urlParams = new URLSearchParams(window.location.search);
            const referrerParam = urlParams.get("referrer");

            if (referrerParam === "member-detail") {
                setReferrer("member-detail");
            } else if (referrerParam === "agent-studio") {
                setReferrer("agent-studio");
            } else {
                const prevPath = document.referrer;
                if (prevPath.includes("/agent-studio")) {
                    setReferrer("agent-studio");
                } else if (prevPath.includes("/organizations/")) {
                    setReferrer("organization");
                }
            }
        }

        const fetchAgentDetails = async () => {
            setIsLoading(true);
            setError(null);

            try {
                const accessToken = Cookies.get("access_token");
                if (!accessToken) {
                    throw new Error("Authentication token not found");
                }

                const response = await fetch(`http://localhost:8080/api/v1/agents/${agentId}/`, {
                    method: "GET",
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${accessToken}`,
                    },
                });

                const data = await response.json();

                if (!response.ok) {
                    if (response.status === 401) {
                        throw new Error("Authentication credentials were not provided.");
                    } else if (response.status === 403) {
                        throw new Error("You do not have permission to view this agent.");
                    } else if (response.status === 404) {
                        throw new Error("Agent not found.");
                    } else {
                        throw new Error(data.error || "Failed to fetch agent details");
                    }
                }

                setAgent(data.agent);
            } catch (err) {
                const errorMessage =
                    err instanceof Error
                        ? err.message
                        : "An error occurred while fetching agent details";
                setError(errorMessage);
                toast.error(errorMessage, {
                    style: {
                        backgroundColor: "var(--destructive)",
                        color: "white",
                        border: "none",
                    },
                });

                router.push("/dashboard");
            } finally {
                setIsLoading(false);
            }
        };

        if (agentId) {
            fetchAgentDetails();
        }
    }, [agentId, router]);

    const handleBackClick = () => {
        if (agent) {
            if (referrer === "agent-studio") {
                router.push(`/organizations/${agent.organization.id}/agent-studio`);
            } else if (referrer === "member-detail" || referrer === "organization") {
                if (agent.user.username) {
                    router.push(
                        `/organizations/${agent.organization.id}/members/${agent.user.username}`
                    );
                } else {
                    router.push(`/organizations/${agent.organization.id}`);
                }
            } else if (
                currentUser &&
                (agent.user.id === currentUser.id || agent.user.username === currentUser.username)
            ) {
                router.push(`/organizations/${agent.organization.id}/agent-studio`);
            } else {
                router.push(`/organizations/${agent.organization.id}`);
            }
        } else {
            router.push("/dashboard");
        }
    };

    const handleUpdateClick = () => {
        setIsUpdateDialogOpen(true);
    };

    const handleDeleteClick = () => {
        setIsDeleteDialogOpen(true);
    };

    if (isLoading) {
        return (
            <ProtectedRoute>
                <div className="min-h-screen flex flex-col bg-(--background)">
                    <DashboardNavbar />
                    <div className="flex-1 container mx-auto px-4 pt-24 pb-8">
                        <div className="flex justify-center items-center h-full">
                            <Loader2 className="h-8 w-8 animate-spin text-(--muted-foreground)" />
                        </div>
                    </div>
                </div>
            </ProtectedRoute>
        );
    }

    if (error || !agent) {
        return (
            <ProtectedRoute>
                <div className="min-h-screen flex flex-col bg-(--background)">
                    <DashboardNavbar />
                    <div className="flex-1 container mx-auto px-4 pt-24 pb-8">
                        <div className="flex justify-center items-center h-full">
                            <div className="flex flex-col items-center">
                                <AlertCircle className="h-8 w-8 text-(--destructive)" />
                                <p className="mt-4 text-lg">{error || "Agent not found"}</p>
                                <Button className="mt-4" onClick={() => router.push("/dashboard")}>
                                    Return to Dashboard
                                </Button>
                            </div>
                        </div>
                    </div>
                </div>
            </ProtectedRoute>
        );
    }

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
                                Back to{" "}
                                {referrer === "agent-studio"
                                    ? "Agent Studio"
                                    : referrer === "member-detail" || referrer === "organization"
                                    ? "User Details"
                                    : currentUser &&
                                      (agent.user.id === currentUser.id ||
                                          agent.user.username === currentUser.username)
                                    ? "Agent Studio"
                                    : "Organization"}
                            </span>
                            <span className="absolute inset-0 bg-(--muted)/50 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                        </Button>

                        <Card className="border border-(--border)">
                            <CardHeader className="pb-4">
                                <div className="flex items-center justify-between w-full">
                                    <div className="flex items-center gap-4">
                                        <Avatar className="h-16 w-16 border border-(--border)">
                                            {agent.avatar_url ? (
                                                <AvatarImage
                                                    src={agent.avatar_url}
                                                    alt={agent.name}
                                                />
                                            ) : (
                                                <AvatarFallback className="bg-(--primary)/10 text-(--primary) text-xl">
                                                    <Bot className="h-8 w-8" />
                                                </AvatarFallback>
                                            )}
                                        </Avatar>
                                        <div>
                                            <CardTitle className="text-xl md:text-2xl font-bold">
                                                {agent.name}
                                            </CardTitle>
                                            <div className="flex items-center text-xs md:text-sm text-(--muted-foreground)">
                                                <User className="mr-1 h-3 md:h-4 w-3 md:w-4" />
                                                <span>Created by {agent.user.username}</span>
                                            </div>
                                        </div>
                                    </div>

                                    {currentUser &&
                                        agent &&
                                        currentUser.username === agent.user.username && (
                                            <div className="flex flex-col space-y-2 sm:flex-row sm:space-y-0 sm:space-x-2">
                                                <Button
                                                    variant="ghost"
                                                    size="icon"
                                                    className="h-10 w-10 rounded-full hover:bg-(--primary)/10 hover:text-(--primary) transition-all duration-200 cursor-pointer"
                                                    onClick={handleUpdateClick}
                                                >
                                                    <Pencil className="h-5 w-5" />
                                                    <span className="sr-only">Edit</span>
                                                </Button>
                                                <Button
                                                    variant="ghost"
                                                    size="icon"
                                                    className="h-10 w-10 rounded-full hover:bg-(--destructive)/10 hover:text-(--destructive) transition-all duration-200 cursor-pointer"
                                                    onClick={handleDeleteClick}
                                                >
                                                    <Trash2 className="h-5 w-5 text-(--destructive)" />
                                                    <span className="sr-only">Delete</span>
                                                </Button>
                                            </div>
                                        )}
                                </div>
                            </CardHeader>
                            <CardContent className="space-y-6">
                                {agent.description && (
                                    <div className="space-y-2">
                                        <h3 className="text-base md:text-lg font-semibold">
                                            Description
                                        </h3>
                                        <div className="p-4 rounded-md bg-(--secondary)">
                                            <p className="text-xs md:text-sm text-(--muted-foreground)">
                                                {agent.description}
                                            </p>
                                        </div>
                                    </div>
                                )}

                                <div className="space-y-2">
                                    <h3 className="text-base md:text-lg font-semibold flex items-center">
                                        <MessageSquare className="mr-2 h-4 md:h-5 w-4 md:w-5 text-(--primary)" />
                                        System Prompt
                                    </h3>
                                    <div className="p-4 rounded-md bg-(--secondary) text-xs md:text-sm text-(--muted-foreground) whitespace-pre-wrap">
                                        {agent.system_prompt}
                                    </div>
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    <div className="space-y-4">
                                        <h3 className="text-base md:text-lg font-semibold flex items-center">
                                            <Cpu className="mr-2 h-4 md:h-5 w-4 md:w-5 text-(--primary)" />
                                            Language Model
                                        </h3>
                                        <div className="p-4 rounded-md bg-(--secondary)">
                                            <div className="flex flex-col mb-2">
                                                <span className="text-xs md:text-sm font-medium mb-1">
                                                    Base URL:
                                                </span>
                                                <span className="text-xs md:text-sm text-(--muted-foreground) truncate md:normal-case">
                                                    {agent.llm.base_url}
                                                </span>
                                            </div>
                                            <div className="flex flex-col">
                                                <span className="text-xs md:text-sm font-medium mb-1">
                                                    Model:
                                                </span>
                                                <span className="text-xs md:text-sm text-(--muted-foreground)">
                                                    {agent.llm.model}
                                                </span>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="space-y-4">
                                        <h3 className="text-base md:text-lg font-semibold flex items-center">
                                            <Calendar className="mr-2 h-4 md:h-5 w-4 md:w-5 text-(--primary)" />
                                            Timestamps
                                        </h3>
                                        <div className="p-4 rounded-md bg-(--secondary)">
                                            <div className="flex flex-col mb-2">
                                                <span className="text-xs md:text-sm font-medium mb-1">
                                                    Created:
                                                </span>
                                                <span className="text-xs md:text-sm text-(--muted-foreground)">
                                                    {new Date(agent.created_at).toLocaleString()}
                                                </span>
                                            </div>
                                            <div className="flex flex-col">
                                                <span className="text-xs md:text-sm font-medium mb-1">
                                                    Updated:
                                                </span>
                                                <span className="text-xs md:text-sm text-(--muted-foreground)">
                                                    {new Date(agent.updated_at).toLocaleString()}
                                                </span>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                {agent.mcp_servers.length > 0 && (
                                    <div className="space-y-4">
                                        <h3 className="text-base md:text-lg font-semibold flex items-center">
                                            <Server className="mr-2 h-4 md:h-5 w-4 md:w-5 text-(--primary)" />
                                            MCP Servers ({agent.mcp_servers.length})
                                        </h3>
                                        <div className="space-y-4">
                                            {agent.mcp_servers.map((server) => (
                                                <div
                                                    key={server.id}
                                                    className="p-4 rounded-md bg-(--secondary)"
                                                >
                                                    <div className="flex items-center mb-2">
                                                        <h4 className="text-sm md:text-base font-semibold">
                                                            {server.name}
                                                        </h4>
                                                    </div>
                                                    <div className="flex items-center text-xs md:text-sm mb-2">
                                                        <Globe className="mr-2 h-3 md:h-4 w-3 md:w-4 text-(--primary)" />
                                                        <span className="font-medium">URL:</span>
                                                        <span className="ml-2 text-(--muted-foreground) truncate">
                                                            {server.url}
                                                        </span>
                                                    </div>
                                                    {server.tools.length > 0 && (
                                                        <div className="mt-2">
                                                            <div className="flex items-center text-xs md:text-sm mb-2">
                                                                <Wrench className="mr-2 h-3 md:h-4 w-3 md:w-4 text-(--primary)" />
                                                                <span className="font-medium">
                                                                    Tools ({server.tools.length}):
                                                                </span>
                                                            </div>
                                                            <div className="max-h-[200px] overflow-y-auto pr-2 border border-(--border) rounded-md p-2">
                                                                <div className="space-y-2">
                                                                    {server.tools.map((tool) => (
                                                                        <div
                                                                            key={tool.id}
                                                                            className="px-4 py-3 bg-(--primary)/10 rounded-md"
                                                                        >
                                                                            <p className="text-xs md:text-sm font-medium">
                                                                                {tool.name}
                                                                            </p>
                                                                            {tool.description && (
                                                                                <p className="text-[10px] md:text-xs text-(--muted-foreground) mt-1">
                                                                                    {
                                                                                        tool.description
                                                                                    }
                                                                                </p>
                                                                            )}
                                                                        </div>
                                                                    ))}
                                                                </div>
                                                            </div>
                                                        </div>
                                                    )}
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </CardContent>
                        </Card>
                    </motion.div>

                    {agent &&
                        currentUser &&
                        (agent.user.id === currentUser.id ||
                            agent.user.username === currentUser.username) && (
                            <>
                                <UpdateAgentDialog
                                    agent={agent}
                                    open={isUpdateDialogOpen}
                                    onOpenChange={(open) => {
                                        setIsUpdateDialogOpen(open);
                                        if (!open) {
                                            const fetchAgentDetails = async () => {
                                                try {
                                                    const accessToken = Cookies.get("access_token");
                                                    if (!accessToken) {
                                                        throw new Error(
                                                            "Authentication token not found"
                                                        );
                                                    }

                                                    const response = await fetch(
                                                        `http://localhost:8080/api/v1/agents/${agentId}/`,
                                                        {
                                                            method: "GET",
                                                            headers: {
                                                                "Content-Type": "application/json",
                                                                Authorization: `Bearer ${accessToken}`,
                                                            },
                                                        }
                                                    );

                                                    const data = await response.json();

                                                    if (response.ok) {
                                                        setAgent(data.agent);
                                                    }
                                                } catch (err) {
                                                    console.error(
                                                        "Failed to refresh agent details:",
                                                        err
                                                    );
                                                }
                                            };
                                            fetchAgentDetails();
                                        }
                                    }}
                                    onUpdateSuccess={() => {
                                        const fetchAgentDetails = async () => {
                                            try {
                                                const accessToken = Cookies.get("access_token");
                                                if (!accessToken) {
                                                    throw new Error(
                                                        "Authentication token not found"
                                                    );
                                                }

                                                const response = await fetch(
                                                    `http://localhost:8080/api/v1/agents/${agentId}/`,
                                                    {
                                                        method: "GET",
                                                        headers: {
                                                            "Content-Type": "application/json",
                                                            Authorization: `Bearer ${accessToken}`,
                                                        },
                                                    }
                                                );

                                                const data = await response.json();

                                                if (response.ok) {
                                                    setAgent(data.agent);
                                                }
                                            } catch (err) {
                                                console.error(
                                                    "Failed to refresh agent details:",
                                                    err
                                                );
                                            }
                                        };
                                        fetchAgentDetails();
                                    }}
                                />
                                <DeleteAgentDialog
                                    agent={agent}
                                    open={isDeleteDialogOpen}
                                    onOpenChange={setIsDeleteDialogOpen}
                                    onDeleteSuccess={() => {
                                        handleBackClick();
                                    }}
                                />
                            </>
                        )}
                </div>
            </div>
        </ProtectedRoute>
    );
}
