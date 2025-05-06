"use client";

import { CreateAgentDialog } from "@/components/create-agent-dialog";
import { DeleteAgentDialog } from "@/components/delete-agent-dialog";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { UpdateAgentDialog } from "@/components/update-agent-dialog";
import { formatDistanceToNow } from "date-fns";
import { motion } from "framer-motion";
import Cookies from "js-cookie";
import {
    AlertCircle,
    Bot,
    Calendar,
    Cpu,
    FileText,
    Loader2,
    MessageSquare,
    Pencil,
    Plus,
    Server,
    Trash2,
} from "lucide-react";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
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
    created_at: string;
    updated_at: string;
}

interface AgentsTabProps {
    organizationId: string;
    filterByUsername?: string;
    readOnly?: boolean;
}

export function AgentsTab({ organizationId, filterByUsername, readOnly = false }: AgentsTabProps) {
    const [agents, setAgents] = useState<Agent[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
    const [isUpdateDialogOpen, setIsUpdateDialogOpen] = useState(false);
    const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
    const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
    const router = useRouter();

    const fetchAgents = useCallback(async () => {
        setIsLoading(true);
        setError(null);

        try {
            const accessToken = Cookies.get("access_token");
            if (!accessToken) {
                throw new Error("Authentication token not found");
            }

            let endpoint;
            const queryParams = new URLSearchParams();

            if (filterByUsername) {
                endpoint = "http://localhost:8080/api/v1/agents/list/";
                queryParams.append("organization_id", organizationId);
                queryParams.append("username", filterByUsername);
            } else {
                endpoint = "http://localhost:8080/api/v1/agents/list/me/";
                queryParams.append("organization_id", organizationId);
            }

            const response = await fetch(`${endpoint}?${queryParams.toString()}`, {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${accessToken}`,
                },
            });

            const data = await response.json();

            if (!response.ok) {
                if (response.status === 404) {
                    setAgents([]);
                    return;
                }
                throw new Error(data.error || "Failed to fetch agents");
            }

            const agentsData = data.agents || [];
            setAgents(agentsData);
        } catch (err) {
            const errorMessage =
                err instanceof Error ? err.message : "An error occurred while fetching agents";
            setError(errorMessage);
            toast.error(errorMessage, {
                style: {
                    backgroundColor: "var(--destructive)",
                    color: "white",
                    border: "none",
                },
            });
        } finally {
            setIsLoading(false);
        }
    }, [organizationId, filterByUsername]);

    useEffect(() => {
        if (organizationId) {
            fetchAgents();
        }
    }, [organizationId, fetchAgents]);

    const handleAgentClick = (agentId: string, e: React.MouseEvent) => {
        if ((e.target as HTMLElement).closest(".agent-action-button")) {
            e.stopPropagation();
            return;
        }

        if (filterByUsername) {
            router.push(`/agents/${agentId}?referrer=member-detail&username=${filterByUsername}`);
        } else {
            router.push(`/agents/${agentId}`);
        }
    };

    const handleUpdateClick = (agent: Agent, e: React.MouseEvent) => {
        e.stopPropagation();
        setSelectedAgent(agent);
        setIsUpdateDialogOpen(true);
    };

    const handleDeleteClick = (agent: Agent, e: React.MouseEvent) => {
        e.stopPropagation();
        setSelectedAgent(agent);
        setIsDeleteDialogOpen(true);
    };

    const renderAgentCards = () => {
        if (isLoading) {
            return (
                <div className="flex justify-center items-center p-8">
                    <Loader2 className="h-8 w-8 animate-spin text-(--muted-foreground)" />
                </div>
            );
        }

        if (error) {
            return (
                <Card className="p-6 bg-(--destructive)/10 border-none">
                    <div className="flex flex-col items-center justify-center p-4 text-center">
                        <div className="h-10 w-10 rounded-full bg-(--destructive)/10 flex items-center justify-center mb-3">
                            <AlertCircle className="h-5 w-5 text-(--destructive)" />
                        </div>
                        <h3 className="text-sm font-medium mb-1">Failed to load agents</h3>
                        <p className="text-xs text-(--muted-foreground) mb-3">{error}</p>
                        <Button
                            onClick={fetchAgents}
                            variant="outline"
                            size="sm"
                            className="h-8 text-xs"
                        >
                            Retry
                        </Button>
                    </div>
                </Card>
            );
        }

        if (agents.length === 0) {
            return (
                <Card className="p-6 border border-dashed border-(--border)">
                    <div className="flex flex-col items-center justify-center p-4 text-center">
                        <Bot className="h-12 w-12 text-(--muted-foreground) mb-3" />
                        <h3 className="text-lg font-medium mb-1">No Agents Created</h3>
                        <p className="text-sm text-(--muted-foreground) mb-4">
                            {readOnly
                                ? "This user has not created any agents yet."
                                : "Create your first agent to start interacting with AI."}
                        </p>
                        {!readOnly && (
                            <Button
                                className="font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--primary) bg-(--primary) text-(--primary-foreground) dark:bg-(--primary) dark:text-(--primary-foreground) dark:border-(--primary) h-10 cursor-pointer"
                                onClick={() => setIsCreateDialogOpen(true)}
                            >
                                <span className="relative z-10">Create Agent</span>
                                <span className="absolute inset-0 bg-(--primary-foreground)/10 dark:bg-(--primary-foreground)/20 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                            </Button>
                        )}
                    </div>
                </Card>
            );
        }

        return (
            <div className="flex flex-col space-y-4">
                {agents.map((agent, index) => (
                    <motion.div
                        key={agent.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.3, delay: index * 0.1 }}
                        whileHover={{ y: -5, transition: { duration: 0.2 } }}
                        className="h-full cursor-pointer"
                        onClick={(e) => handleAgentClick(agent.id, e)}
                    >
                        <Card className="h-full flex flex-col p-0 pt-6 border border-(--border) shadow-sm hover:shadow-md transition-all duration-300 overflow-hidden bg-(--secondary) dark:bg-(--secondary) relative gap-2">
                            <CardHeader className="pb-2">
                                <div className="flex items-center justify-between w-full">
                                    <div className="flex items-center">
                                        <div className="mr-3">
                                            <Avatar className="h-10 w-10 border border-(--border)">
                                                {agent.avatar_url ? (
                                                    <AvatarImage
                                                        src={agent.avatar_url}
                                                        alt={agent.name}
                                                    />
                                                ) : (
                                                    <AvatarFallback className="bg-(--muted) text-(--muted-foreground)">
                                                        <Bot className="h-5 w-5" />
                                                    </AvatarFallback>
                                                )}
                                            </Avatar>
                                        </div>
                                        <CardTitle className="flex items-center text-lg font-semibold">
                                            {agent.name}
                                        </CardTitle>
                                    </div>
                                    {!readOnly && !filterByUsername && (
                                        <div className="absolute top-2 right-2 flex space-x-1">
                                            <div className="group">
                                                <Button
                                                    variant="ghost"
                                                    size="icon"
                                                    className="h-8 w-8 rounded-full hover:bg-(--primary)/10 hover:text-(--primary) transition-all duration-200 cursor-pointer agent-action-button"
                                                    onClick={(e) => handleUpdateClick(agent, e)}
                                                >
                                                    <Pencil className="h-4 w-4" />
                                                    <span className="sr-only">Edit</span>
                                                </Button>
                                            </div>
                                            <div className="group">
                                                <Button
                                                    variant="ghost"
                                                    size="icon"
                                                    className="h-8 w-8 rounded-full hover:bg-(--destructive)/10 hover:text-(--destructive) transition-all duration-200 cursor-pointer agent-action-button"
                                                    onClick={(e) => handleDeleteClick(agent, e)}
                                                >
                                                    <Trash2 className="h-4 w-4 text-(--destructive)" />
                                                    <span className="sr-only">Delete</span>
                                                </Button>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </CardHeader>
                            <CardContent className="px-6 pb-6">
                                <div className="space-y-3">
                                    {agent.description && (
                                        <div>
                                            <div className="flex items-center text-sm">
                                                <FileText className="mr-2 h-4 w-4 text-(--primary)" />
                                                <p className="font-medium">Details:</p>
                                            </div>
                                            <div className="mt-1 text-sm text-(--muted-foreground) line-clamp-2">
                                                {agent.description}
                                            </div>
                                        </div>
                                    )}

                                    <div>
                                        <div className="flex items-center text-sm">
                                            <MessageSquare className="mr-2 h-4 w-4 text-(--primary)" />
                                            <p className="font-medium">System Prompt:</p>
                                        </div>
                                        <div className="mt-1 text-sm text-(--muted-foreground) line-clamp-2">
                                            {agent.system_prompt}
                                        </div>
                                    </div>
                                    <div className="flex items-center text-sm">
                                        <Cpu className="mr-2 h-4 w-4 text-(--primary)" />
                                        <p className="font-medium">LLM:</p>
                                        <p className="ml-2 text-(--muted-foreground) truncate">
                                            {agent.llm.model}
                                        </p>
                                    </div>
                                    {agent.mcp_servers.length > 0 && (
                                        <div className="flex items-center text-sm">
                                            <Server className="mr-2 h-4 w-4 text-(--primary)" />
                                            <p className="font-medium">MCP Servers:</p>
                                            <p className="ml-2 text-(--muted-foreground)">
                                                {agent.mcp_servers.length}
                                            </p>
                                        </div>
                                    )}
                                </div>
                            </CardContent>
                            <div className="mt-auto border-t bg-(--muted)/10 px-6 py-3">
                                <div className="w-full flex flex-col space-y-1">
                                    <div className="flex items-center text-xs text-(--muted-foreground)">
                                        <Calendar className="mr-1 h-3 w-3" />
                                        <span>
                                            Created{" "}
                                            {formatDistanceToNow(new Date(agent.created_at), {
                                                addSuffix: true,
                                            })}
                                        </span>
                                    </div>
                                    <div className="flex items-center text-xs text-(--muted-foreground)">
                                        <Calendar className="mr-1 h-3 w-3" />
                                        <span>
                                            Updated{" "}
                                            {formatDistanceToNow(new Date(agent.updated_at), {
                                                addSuffix: true,
                                            })}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </Card>
                    </motion.div>
                ))}

                {!readOnly && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.3, delay: 0.1 * agents.length }}
                        whileHover={{ y: -5, transition: { duration: 0.2 } }}
                        className="w-full"
                    >
                        <Card
                            className="h-full flex flex-col justify-center items-center p-6 cursor-pointer border border-dashed border-(--primary) bg-(--card) hover:bg-(--primary)/5 transition-all duration-300 group gap-2"
                            onClick={() => setIsCreateDialogOpen(true)}
                        >
                            <div className="flex flex-col items-center text-center">
                                <div className="h-12 w-12 rounded-full bg-(--primary)/10 flex items-center justify-center mb-4 group-hover:bg-(--primary)/20 transition-colors duration-300">
                                    <Plus className="h-6 w-6 text-(--primary)" />
                                </div>
                                <h3 className="text-lg font-semibold mb-2 group-hover:text-(--primary) transition-colors duration-300">
                                    Create New Agent
                                </h3>
                                <p className="text-sm text-(--muted-foreground)">
                                    Build a new AI agent with custom capabilities
                                </p>
                            </div>
                        </Card>
                    </motion.div>
                )}
            </div>
        );
    };

    return (
        <>
            <div className="space-y-6">{renderAgentCards()}</div>

            <CreateAgentDialog
                organizationId={organizationId}
                open={isCreateDialogOpen}
                onOpenChange={setIsCreateDialogOpen}
                onCreateSuccess={fetchAgents}
            />

            {selectedAgent && (
                <>
                    <UpdateAgentDialog
                        agent={selectedAgent}
                        open={isUpdateDialogOpen}
                        onOpenChange={(open) => {
                            setIsUpdateDialogOpen(open);
                            if (!open) {
                                setTimeout(() => setSelectedAgent(null), 300);
                            }
                        }}
                        onUpdateSuccess={fetchAgents}
                    />
                    <DeleteAgentDialog
                        agent={selectedAgent}
                        open={isDeleteDialogOpen}
                        onOpenChange={(open) => {
                            setIsDeleteDialogOpen(open);
                            if (!open) {
                                setTimeout(() => setSelectedAgent(null), 300);
                            }
                        }}
                        onDeleteSuccess={fetchAgents}
                    />
                </>
            )}
        </>
    );
}
