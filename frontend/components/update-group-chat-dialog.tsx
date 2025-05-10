"use client";

import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import Cookies from "js-cookie";
import { Check, Loader2, Users } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { toast } from "sonner";

interface Agent {
    id: string;
    name: string;
    description?: string;
    avatar_url?: string;
    llm?: {
        id: string;
        base_url: string;
        model: string;
    };
}

interface GroupChat {
    id: string;
    title: string;
    is_public: boolean;
    agents: Agent[];
}

interface UpdateGroupChatDialogProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    organizationId: string;
    chat: GroupChat;
    onSuccess: () => void;
}

export function UpdateGroupChatDialog({
    open,
    onOpenChange,
    organizationId,
    chat,
    onSuccess,
}: UpdateGroupChatDialogProps) {
    const [title, setTitle] = useState("");
    const [isPublic, setIsPublic] = useState(false);
    const [agents, setAgents] = useState<Agent[]>([]);
    const [selectedAgentIds, setSelectedAgentIds] = useState<string[]>([]);
    const [isLoadingAgents, setIsLoadingAgents] = useState(false);
    const [isSubmitting, setIsSubmitting] = useState(false);

    const fetchAgents = useCallback(async () => {
        setIsLoadingAgents(true);
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
        } finally {
            setIsLoadingAgents(false);
        }
    }, [organizationId]);

    useEffect(() => {
        if (open) {
            setTitle(chat.title);
            setIsPublic(chat.is_public);
            setSelectedAgentIds(chat.agents.map((agent) => agent.id));
            fetchAgents();
        }
    }, [open, chat, organizationId, fetchAgents]);

    const toggleAgent = (agentId: string) => {
        setSelectedAgentIds((prev) => {
            if (prev.includes(agentId)) {
                return prev.filter((id) => id !== agentId);
            } else {
                return [...prev, agentId];
            }
        });
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!title || selectedAgentIds.length === 0) {
            toast.error("Please fill in all required fields", {
                className: "bg-(--destructive) text-white border-none",
            });
            return;
        }

        setIsSubmitting(true);

        try {
            const accessToken = Cookies.get("access_token");
            if (!accessToken) {
                throw new Error("Authentication token not found");
            }

            const response = await fetch(
                `${process.env.NEXT_PUBLIC_API_URL}/chats/group/${chat.id}/update/`,
                {
                    method: "PATCH",
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${accessToken}`,
                    },
                    body: JSON.stringify({
                        title,
                        agent_ids: selectedAgentIds,
                        is_public: isPublic,
                    }),
                }
            );

            const data = await response.json();

            if (!response.ok) {
                const errorMessages = [];
                if (data.errors) {
                    for (const field in data.errors) {
                        errorMessages.push(...data.errors[field]);
                    }
                }
                throw new Error(
                    errorMessages.length > 0
                        ? errorMessages.join(", ")
                        : data.error || "Failed to update group chat"
                );
            }

            toast.success("Group chat updated successfully", {
                style: {
                    backgroundColor: "oklch(0.45 0.18 142.71)",
                    color: "white",
                    border: "none",
                },
            });

            onOpenChange(false);
            onSuccess();
        } catch (err) {
            const errorMessage =
                err instanceof Error
                    ? err.message
                    : "An error occurred while updating the group chat";
            toast.error(errorMessage, {
                className: "bg-(--destructive) text-white border-none",
            });
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[500px] bg-(--background) border-(--border) [&_[data-slot=dialog-close]]:hover:opacity-100 [&_[data-slot=dialog-close]]:cursor-pointer [&_[data-slot=dialog-close]]:transition-opacity [&_[data-slot=dialog-close]]:duration-200">
                <DialogHeader>
                    <DialogTitle className="flex items-center pb-2">
                        <Users className="mr-2 h-5 w-5 text-(--primary)" />
                        Update Group Chat
                    </DialogTitle>
                    <DialogDescription>Update the details of your group chat.</DialogDescription>
                </DialogHeader>
                <form onSubmit={handleSubmit} className="space-y-6">
                    <div className="space-y-4">
                        <div className="space-y-2">
                            <Label htmlFor="title">Title</Label>
                            <Input
                                id="title"
                                value={title}
                                onChange={(e) => setTitle(e.target.value)}
                                className="bg-(--secondary)"
                                placeholder="Enter group chat title"
                                required
                            />
                        </div>
                        <div className="space-y-2">
                            <Label>Agents (Select at least one)</Label>
                            <div className="space-y-2">
                                {isLoadingAgents ? (
                                    <div className="flex items-center justify-center p-4 bg-(--secondary) rounded-md">
                                        <Loader2 className="h-4 w-4 animate-spin text-(--muted-foreground)" />
                                        <span className="ml-2 text-sm text-(--muted-foreground)">
                                            Loading agents...
                                        </span>
                                    </div>
                                ) : agents.length === 0 ? (
                                    <div className="p-4 text-center text-(--muted-foreground) bg-(--secondary) rounded-md">
                                        No agents available. Please create an agent first.
                                    </div>
                                ) : (
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2 max-h-[200px] overflow-y-auto p-1">
                                        {agents.map((agent) => (
                                            <div
                                                key={agent.id}
                                                className={`p-3 rounded-md border cursor-pointer transition-all duration-200 ${
                                                    selectedAgentIds.includes(agent.id)
                                                        ? "border-(--primary) bg-(--primary)/10"
                                                        : "border-(--border) bg-(--secondary) hover:border-(--primary)/50"
                                                }`}
                                                onClick={() => toggleAgent(agent.id)}
                                            >
                                                <div className="flex items-center justify-between">
                                                    <div className="flex items-center">
                                                        <span className="font-medium text-sm">
                                                            {agent.name}
                                                        </span>
                                                    </div>
                                                    {selectedAgentIds.includes(agent.id) && (
                                                        <Check className="h-4 w-4 text-(--primary)" />
                                                    )}
                                                </div>
                                                {agent.description && (
                                                    <div className="text-xs text-(--muted-foreground) mt-1 truncate">
                                                        {agent.description}
                                                    </div>
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="is-public">Visibility</Label>
                            <div className="flex items-center space-x-2 p-3 rounded-md bg-(--secondary)">
                                <Checkbox
                                    id="is-public"
                                    checked={isPublic}
                                    onCheckedChange={(checked) => setIsPublic(checked === true)}
                                />
                                <label
                                    htmlFor="is-public"
                                    className="text-xs text-(--muted-foreground) ml-3 peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                                >
                                    Public to organization
                                </label>
                            </div>
                        </div>
                    </div>
                    <DialogFooter className="flex flex-col sm:flex-row sm:justify-between w-full gap-2">
                        <Button
                            type="button"
                            variant="outline"
                            onClick={() => onOpenChange(false)}
                            disabled={isSubmitting}
                            className="font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--border) bg-(--background) text-(--foreground) hover:bg-(--muted) h-10 cursor-pointer w-full sm:flex-1"
                        >
                            <span className="relative z-10">Cancel</span>
                            <span className="absolute inset-0 bg-(--muted)/50 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                        </Button>
                        <Button
                            type="submit"
                            disabled={isSubmitting || !title || selectedAgentIds.length === 0}
                            className="font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--primary) bg-(--primary) text-(--primary-foreground) dark:bg-(--primary) dark:text-(--primary-foreground) dark:border-(--primary) h-10 cursor-pointer w-full sm:flex-1"
                        >
                            <span className="relative z-10">
                                {isSubmitting ? (
                                    <>
                                        <Loader2 className="mr-2 h-4 w-4 animate-spin inline" />
                                        Updating...
                                    </>
                                ) : (
                                    "Update Group Chat"
                                )}
                            </span>
                            <span className="absolute inset-0 bg-(--primary-foreground)/10 dark:bg-(--primary-foreground)/20 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                        </Button>
                    </DialogFooter>
                </form>
            </DialogContent>
        </Dialog>
    );
}
