"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import { format } from "date-fns";
import Cookies from "js-cookie";
import { Loader2, MessageCircle, RefreshCw } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { toast } from "sonner";

interface Agent {
    id: string;
    name: string;
}

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
    };
}

interface ChatListProps {
    organizationId: string;
}

export function ChatList({ organizationId }: ChatListProps) {
    const router = useRouter();
    const [chats, setChats] = useState<Chat[]>([]);
    const [agents, setAgents] = useState<Agent[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [selectedAgentId, setSelectedAgentId] = useState<string>("all");
    const [isPublic, setIsPublic] = useState<string>("all");
    const [sortOrder, setSortOrder] = useState<string>("newest");

    useEffect(() => {
        fetchAgents();
        fetchChats();
    }, [organizationId]);

    useEffect(() => {
        fetchChats();
    }, [selectedAgentId, isPublic, sortOrder]);

    const fetchAgents = async () => {
        try {
            const accessToken = Cookies.get("access_token");
            if (!accessToken) {
                throw new Error("Authentication token not found");
            }

            const response = await fetch(
                `http://localhost:8080/api/v1/agents/list/me/?organization_id=${organizationId}`,
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
                throw new Error(data.error || "Failed to fetch agents");
            }

            setAgents(data.agents || []);
        } catch (err) {
            const errorMessage =
                err instanceof Error ? err.message : "An error occurred while fetching agents";
            toast.error(errorMessage, {
                className: "bg-(--destructive) text-white border-none",
            });
        }
    };

    const fetchChats = async () => {
        setIsLoading(true);
        try {
            const accessToken = Cookies.get("access_token");
            if (!accessToken) {
                throw new Error("Authentication token not found");
            }

            let url = `http://localhost:8080/api/v1/chats/single/list/me/?organization_id=${organizationId}`;

            if (selectedAgentId && selectedAgentId !== "all") {
                url += `&agent_id=${selectedAgentId}`;
            }

            if (isPublic === "true" || isPublic === "false") {
                url += `&is_public=${isPublic}`;
            }

            const response = await fetch(url, {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${accessToken}`,
                },
            });

            const data = await response.json();

            if (!response.ok) {
                if (response.status === 404) {
                    setChats([]);
                    return;
                }
                throw new Error(data.error || "Failed to fetch chats");
            }

            let sortedChats = [...(data.chats || [])];

            if (sortOrder === "newest") {
                sortedChats.sort(
                    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
                );
            } else if (sortOrder === "oldest") {
                sortedChats.sort(
                    (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
                );
            }

            setChats(sortedChats);
        } catch (err) {
            const errorMessage =
                err instanceof Error ? err.message : "An error occurred while fetching chats";
            toast.error(errorMessage, {
                className: "bg-(--destructive) text-white border-none",
            });

            if (
                err instanceof Error &&
                err.message.includes("You are not a member of this organization")
            ) {
                router.push("/dashboard");
            }
        } finally {
            setIsLoading(false);
        }
    };

    const formatDate = (dateString: string) => {
        try {
            return format(new Date(dateString), "MMM d, yyyy h:mm a");
        } catch (e) {
            return dateString;
        }
    };

    return (
        <div>
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium">Your Chats</h3>
                <div className="text-sm text-(--muted-foreground)">
                    {chats.length} {chats.length === 1 ? "chat" : "chats"} found
                </div>
            </div>
            <div className="flex flex-col sm:flex-row gap-3 sm:items-center sm:justify-between bg-(--secondary) p-3 rounded-md border border-(--border) mb-4">
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 w-full">
                    <Select value={selectedAgentId} onValueChange={setSelectedAgentId}>
                        <SelectTrigger className="w-full bg-(--background)">
                            <SelectValue placeholder="Filter by agent" />
                        </SelectTrigger>
                        <SelectContent className="bg-(--background)">
                            <SelectItem
                                value="all"
                                className="hover:bg-(--secondary) focus:bg-(--secondary)"
                            >
                                All agents
                            </SelectItem>
                            {agents.map((agent) => (
                                <SelectItem
                                    key={agent.id}
                                    value={agent.id}
                                    className="hover:bg-(--secondary) focus:bg-(--secondary)"
                                >
                                    {agent.name}
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>

                    <Select value={isPublic} onValueChange={setIsPublic}>
                        <SelectTrigger className="w-full bg-(--background)">
                            {isPublic === "all" ? (
                                <SelectValue placeholder="Filter by visibility" />
                            ) : isPublic === "true" ? (
                                <div className="flex items-center">
                                    <Badge variant="default" className="mr-2">
                                        Public
                                    </Badge>
                                    chats
                                </div>
                            ) : (
                                <div className="flex items-center">
                                    <Badge variant="outline" className="mr-2">
                                        Private
                                    </Badge>
                                    chats
                                </div>
                            )}
                        </SelectTrigger>
                        <SelectContent className="bg-(--background)">
                            <SelectItem
                                value="all"
                                className="hover:bg-(--secondary) focus:bg-(--secondary)"
                            >
                                All chats
                            </SelectItem>
                            <SelectItem
                                value="true"
                                className="hover:bg-(--secondary) focus:bg-(--secondary)"
                            >
                                <div className="flex items-center">Public chats</div>
                            </SelectItem>
                            <SelectItem
                                value="false"
                                className="hover:bg-(--secondary) focus:bg-(--secondary)"
                            >
                                <div className="flex items-center">Private chats</div>
                            </SelectItem>
                        </SelectContent>
                    </Select>

                    <div className="flex gap-2 flex-1">
                        <Select value={sortOrder} onValueChange={setSortOrder}>
                            <SelectTrigger className="w-full bg-(--background)">
                                <SelectValue placeholder="Sort by" />
                            </SelectTrigger>
                            <SelectContent className="bg-(--background)">
                                <SelectItem
                                    value="newest"
                                    className="hover:bg-(--secondary) focus:bg-(--secondary)"
                                >
                                    Newest first
                                </SelectItem>
                                <SelectItem
                                    value="oldest"
                                    className="hover:bg-(--secondary) focus:bg-(--secondary)"
                                >
                                    Oldest first
                                </SelectItem>
                            </SelectContent>
                        </Select>

                        <Button
                            variant="outline"
                            size="icon"
                            onClick={fetchChats}
                            disabled={isLoading}
                            className="bg-(--background) hover:bg-(--muted)"
                        >
                            {isLoading ? (
                                <Loader2 className="h-4 w-4 animate-spin" />
                            ) : (
                                <RefreshCw className="h-4 w-4" />
                            )}
                        </Button>
                    </div>
                </div>
            </div>

            {isLoading ? (
                <div className="flex justify-center items-center py-12 border rounded-md bg-(--secondary)">
                    <div className="flex flex-col items-center">
                        <Loader2 className="h-8 w-8 animate-spin text-(--muted-foreground) mb-2" />
                        <p className="text-sm text-(--muted-foreground)">Loading chats...</p>
                    </div>
                </div>
            ) : chats.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-12 text-center border rounded-md bg-(--secondary)">
                    <MessageCircle className="h-12 w-12 text-(--muted-foreground) mb-3" />
                    <h3 className="text-lg font-medium mb-1">No chats found</h3>
                    <p className="text-sm text-(--muted-foreground) mb-4">
                        Create a new chat using the button above
                    </p>
                </div>
            ) : (
                <div className="rounded-md border border-(--border) overflow-hidden">
                    <Table>
                        <TableHeader className="bg-(--secondary)">
                            <TableRow>
                                <TableHead className="font-semibold pl-4">Title</TableHead>
                                <TableHead className="font-semibold">Agent</TableHead>
                                <TableHead className="font-semibold">Visibility</TableHead>
                                <TableHead className="font-semibold pr-4">Created</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {chats.map((chat) => (
                                <TableRow
                                    key={chat.id}
                                    className="cursor-pointer hover:bg-(--secondary) transition-colors"
                                    onClick={() => router.push(`/chats/${chat.id}`)}
                                >
                                    <TableCell className="font-medium pl-4">{chat.title}</TableCell>
                                    <TableCell>{chat.agent.name}</TableCell>
                                    <TableCell>
                                        <Badge
                                            variant="outline"
                                            className="bg-(--primary)/10 text-(--primary) border-(--primary)/20 w-20"
                                        >
                                            {chat.is_public ? "Public" : "Private"}
                                        </Badge>
                                    </TableCell>
                                    <TableCell className="pr-4 whitespace-nowrap">
                                        {formatDate(chat.created_at)}
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </div>
            )}
        </div>
    );
}
