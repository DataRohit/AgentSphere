"use client";

import { DeleteChatDialog } from "@/components/delete-chat-dialog";
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
import { UpdateChatDialog } from "@/components/update-chat-dialog";
import { format } from "date-fns";
import Cookies from "js-cookie";
import { Loader2, MessageCircle, Pencil, RefreshCw, Trash2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
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
    filterByUsername?: string;
    readOnly?: boolean;
}

export function ChatList({ organizationId, filterByUsername, readOnly = false }: ChatListProps) {
    const router = useRouter();
    const [chats, setChats] = useState<Chat[]>([]);
    const [agents, setAgents] = useState<Agent[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [selectedAgentId, setSelectedAgentId] = useState<string>("all");
    const [isPublic, setIsPublic] = useState<string>("all");
    const [sortOrder, setSortOrder] = useState<string>("newest");
    const [selectedChat, setSelectedChat] = useState<Chat | null>(null);
    const [isUpdateDialogOpen, setIsUpdateDialogOpen] = useState(false);
    const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);

    const fetchAgents = useCallback(async () => {
        try {
            const accessToken = Cookies.get("access_token");
            if (!accessToken) {
                throw new Error("Authentication token not found");
            }

            const response = await fetch(
                `${process.env.NEXT_PUBLIC_API_URL}/agents/list/me/?organization_id=${organizationId}`,
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
    }, [organizationId]);

    const fetchChats = useCallback(async () => {
        setIsLoading(true);
        try {
            const accessToken = Cookies.get("access_token");
            if (!accessToken) {
                throw new Error("Authentication token not found");
            }

            let endpoint;
            const queryParams = new URLSearchParams();
            queryParams.append("organization_id", organizationId);

            if (filterByUsername) {
                endpoint = `${process.env.NEXT_PUBLIC_API_URL}/chats/single/list`;
                queryParams.append("username", filterByUsername);
            } else {
                endpoint = `${process.env.NEXT_PUBLIC_API_URL}/chats/single/list/me`;
            }

            if (selectedAgentId && selectedAgentId !== "all") {
                queryParams.append("agent_id", selectedAgentId);
            }

            if (isPublic === "true" || isPublic === "false") {
                queryParams.append("is_public", isPublic);
            }

            const fullUrl = `${endpoint}?${queryParams.toString()}`;

            const response = await fetch(fullUrl, {
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

            const sortedChats = [...(data.chats || [])];

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
                style: {
                    backgroundColor: "#f44336",
                    color: "white",
                    border: "none",
                },
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
    }, [organizationId, selectedAgentId, isPublic, sortOrder, filterByUsername, router]);

    useEffect(() => {
        fetchAgents();
        fetchChats();
    }, [fetchAgents, fetchChats]);

    useEffect(() => {
        fetchChats();
    }, [fetchChats]);

    const formatDate = (dateString: string) => {
        try {
            return format(new Date(dateString), "MMM d, yyyy h:mm a");
        } catch {
            return dateString;
        }
    };

    const handleUpdateClick = useCallback((e: React.MouseEvent, chat: Chat) => {
        e.stopPropagation();
        setSelectedChat(chat);
        setIsUpdateDialogOpen(true);
    }, []);

    const handleDeleteClick = useCallback((e: React.MouseEvent, chat: Chat) => {
        e.stopPropagation();
        setSelectedChat(chat);
        setIsDeleteDialogOpen(true);
    }, []);

    const handleSuccess = useCallback(() => {
        fetchChats();
    }, [fetchChats]);

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
                            onClick={() => fetchChats()}
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
                                <TableHead className="font-semibold">Created</TableHead>
                                {!readOnly && (
                                    <TableHead className="font-semibold text-right pr-4">
                                        Actions
                                    </TableHead>
                                )}
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {chats.map((chat) => (
                                <TableRow
                                    key={chat.id}
                                    className="hover:bg-(--secondary) transition-colors"
                                >
                                    <TableCell
                                        className="font-medium pl-4 cursor-pointer"
                                        onClick={() =>
                                            router.push(
                                                `/chats/${chat.id}${
                                                    readOnly ? "?viewOnly=true" : ""
                                                }`
                                            )
                                        }
                                    >
                                        {chat.title}
                                    </TableCell>
                                    <TableCell
                                        className="cursor-pointer"
                                        onClick={() =>
                                            router.push(
                                                `/chats/${chat.id}${
                                                    readOnly ? "?viewOnly=true" : ""
                                                }`
                                            )
                                        }
                                    >
                                        {chat.agent.name}
                                    </TableCell>
                                    <TableCell
                                        className="cursor-pointer"
                                        onClick={() =>
                                            router.push(
                                                `/chats/${chat.id}${
                                                    readOnly ? "?viewOnly=true" : ""
                                                }`
                                            )
                                        }
                                    >
                                        <Badge
                                            variant="outline"
                                            className={`bg-(--primary)/10 border-(--primary)/20 w-20 ${
                                                chat.is_public ? "text-blue-300" : "text-green-300"
                                            }`}
                                        >
                                            {chat.is_public ? "Public" : "Private"}
                                        </Badge>
                                    </TableCell>
                                    <TableCell
                                        className="whitespace-nowrap cursor-pointer"
                                        onClick={() =>
                                            router.push(
                                                `/chats/${chat.id}${
                                                    readOnly ? "?viewOnly=true" : ""
                                                }`
                                            )
                                        }
                                    >
                                        {formatDate(chat.created_at)}
                                    </TableCell>
                                    {!readOnly && (
                                        <TableCell className="text-right pr-4">
                                            <div className="flex space-x-1 justify-end">
                                                <div className="group">
                                                    <Button
                                                        variant="ghost"
                                                        size="icon"
                                                        className="h-8 w-8 rounded-full hover:bg-(--primary)/10 hover:text-(--primary) transition-all duration-200 cursor-pointer agent-action-button"
                                                        onClick={(e) => handleUpdateClick(e, chat)}
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
                                                        onClick={(e) => handleDeleteClick(e, chat)}
                                                    >
                                                        <Trash2 className="h-4 w-4 text-(--destructive)" />
                                                        <span className="sr-only">Delete</span>
                                                    </Button>
                                                </div>
                                            </div>
                                        </TableCell>
                                    )}
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </div>
            )}

            {selectedChat && (
                <>
                    <UpdateChatDialog
                        open={isUpdateDialogOpen}
                        onOpenChange={setIsUpdateDialogOpen}
                        organizationId={organizationId}
                        chat={selectedChat}
                        onSuccess={handleSuccess}
                    />
                    <DeleteChatDialog
                        open={isDeleteDialogOpen}
                        onOpenChange={setIsDeleteDialogOpen}
                        chat={selectedChat}
                        onSuccess={handleSuccess}
                    />
                </>
            )}
        </div>
    );
}
