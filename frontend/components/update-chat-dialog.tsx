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
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import Cookies from "js-cookie";
import { Loader2, MessageCircle } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { toast } from "sonner";

interface Agent {
    id: string;
    name: string;
    description: string;
    avatar_url: string;
    llm: {
        id: string;
        base_url: string;
        model: string;
    };
}

interface Chat {
    id: string;
    title: string;
    is_public: boolean;
    agent: {
        id: string;
        name: string;
    };
}

interface UpdateChatDialogProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    organizationId: string;
    chat: Chat;
    onSuccess: () => void;
}

export function UpdateChatDialog({
    open,
    onOpenChange,
    organizationId,
    chat,
    onSuccess,
}: UpdateChatDialogProps) {
    const [title, setTitle] = useState("");
    const [selectedAgentId, setSelectedAgentId] = useState("");
    const [isPublic, setIsPublic] = useState(false);
    const [agents, setAgents] = useState<Agent[]>([]);
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
            setAgents([]);
        } finally {
            setIsLoadingAgents(false);
        }
    }, [organizationId]);

    useEffect(() => {
        if (open) {
            setTitle(chat.title);
            setSelectedAgentId(chat.agent.id);
            setIsPublic(chat.is_public);
            fetchAgents();
        }
    }, [open, chat, organizationId, fetchAgents]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsSubmitting(true);

        try {
            const accessToken = Cookies.get("access_token");
            if (!accessToken) {
                throw new Error("Authentication token not found");
            }

            const response = await fetch(
                `${process.env.NEXT_PUBLIC_API_URL}/chats/single/${chat.id}/update/`,
                {
                    method: "PATCH",
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${accessToken}`,
                    },
                    body: JSON.stringify({
                        title,
                        agent_id: selectedAgentId,
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
                        : data.error || "Failed to update chat"
                );
            }

            toast.success("Chat updated successfully", {
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
                err instanceof Error ? err.message : "An error occurred while updating the chat";
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
                        <MessageCircle className="mr-2 h-5 w-5 text-(--primary)" />
                        Update Chat
                    </DialogTitle>
                    <DialogDescription>Update the details of your chat.</DialogDescription>
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
                                placeholder="Enter chat title"
                                required
                            />
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="agent">Agent</Label>
                            <Select
                                value={selectedAgentId}
                                onValueChange={setSelectedAgentId}
                                disabled={isLoadingAgents || agents.length === 0}
                            >
                                <SelectTrigger className="bg-(--secondary) w-full">
                                    <SelectValue placeholder="Select an agent" />
                                </SelectTrigger>
                                <SelectContent className="bg-(--background)">
                                    {isLoadingAgents ? (
                                        <div className="flex items-center justify-center p-2">
                                            <Loader2 className="h-4 w-4 animate-spin text-(--muted-foreground)" />
                                            <span className="ml-2">Loading agents...</span>
                                        </div>
                                    ) : agents.length === 0 ? (
                                        <div className="p-2 text-center text-(--muted-foreground)">
                                            No agents available
                                        </div>
                                    ) : (
                                        agents.map((agent) => (
                                            <SelectItem
                                                key={agent.id}
                                                value={agent.id}
                                                className="hover:bg-(--secondary) focus:bg-(--secondary)"
                                            >
                                                {agent.name}
                                            </SelectItem>
                                        ))
                                    )}
                                </SelectContent>
                            </Select>
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
                            disabled={isSubmitting || !title || !selectedAgentId}
                            className="font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--primary) bg-(--primary) text-(--primary-foreground) dark:bg-(--primary) dark:text-(--primary-foreground) dark:border-(--primary) h-10 cursor-pointer w-full sm:flex-1"
                        >
                            <span className="relative z-10">
                                {isSubmitting ? (
                                    <>
                                        <Loader2 className="mr-2 h-4 w-4 animate-spin inline" />
                                        Updating...
                                    </>
                                ) : (
                                    "Update Chat"
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
