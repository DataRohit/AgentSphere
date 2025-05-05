"use client";

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
import { ScrollArea } from "@/components/ui/scroll-area";
import { formatDistanceToNow } from "date-fns";
import Cookies from "js-cookie";
import { AlertCircle, Calendar, Cpu, Key, Loader2, Server, User } from "lucide-react";
import { useEffect, useState } from "react";
import { toast } from "sonner";

interface OrganizationMember {
    email: string;
    first_name: string;
    last_name: string;
    username: string;
    avatar_url: string;
    is_active: boolean;
    is_staff: boolean;
    is_superuser: boolean;
    date_joined: string;
    last_login: string;
}

interface LLM {
    id: string;
    api_type: string;
    model: string;
    max_tokens: number;
    organization: {
        id: string;
        name: string;
    };
    user: {
        id: string;
        username: string;
        email: string;
    };
    created_at: string;
    updated_at: string;
}

interface MemberDetailsDialogProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    member: OrganizationMember | null;
    organizationId: string;
}

export function MemberDetailsDialog({
    open,
    onOpenChange,
    member,
    organizationId,
}: MemberDetailsDialogProps) {
    const [llms, setLLMs] = useState<LLM[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const fetchMemberLLMs = async () => {
        if (!member || !organizationId) return;

        setIsLoading(true);
        setError(null);

        try {
            const accessToken = Cookies.get("access_token");
            if (!accessToken) {
                throw new Error("Authentication token not found");
            }

            const response = await fetch(
                `http://localhost:8080/api/v1/llms/list/?organization_id=${organizationId}`,
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
                    setLLMs([]);
                    return;
                }
                throw new Error(data.error || "Failed to fetch LLMs");
            }

            const memberLLMs = data.llms.filter(
                (llm: LLM) =>
                    llm.user.email === member.email || llm.user.username === member.username
            );

            setLLMs(memberLLMs || []);
        } catch (err) {
            const errorMessage =
                err instanceof Error ? err.message : "An error occurred while fetching LLMs";
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
    };

    useEffect(() => {
        if (open && member) {
            fetchMemberLLMs();
        }
    }, [open, member, organizationId]);

    if (!member) return null;

    const getInitials = (name: string) => {
        return name
            .split(" ")
            .map((part) => part[0])
            .join("")
            .toUpperCase()
            .substring(0, 2);
    };

    const fullName =
        member.first_name && member.last_name
            ? `${member.first_name} ${member.last_name}`
            : member.username;

    const renderLLMsList = () => {
        if (isLoading) {
            return (
                <div className="flex justify-center items-center p-8">
                    <Loader2 className="h-8 w-8 animate-spin text-(--muted-foreground)" />
                </div>
            );
        }

        if (error) {
            return (
                <div className="flex flex-col items-center justify-center p-4 text-center">
                    <div className="h-10 w-10 rounded-full bg-(--destructive)/10 flex items-center justify-center mb-3">
                        <AlertCircle className="h-5 w-5 text-(--destructive)" />
                    </div>
                    <h3 className="text-sm font-medium mb-1">Failed to load LLMs</h3>
                    <p className="text-xs text-(--muted-foreground) mb-3">{error}</p>
                    <Button
                        onClick={fetchMemberLLMs}
                        variant="outline"
                        size="sm"
                        className="h-8 text-xs"
                    >
                        Retry
                    </Button>
                </div>
            );
        }

        if (llms.length === 0) {
            return (
                <div className="flex flex-col items-center justify-center p-4 text-center">
                    <p className="text-sm text-(--muted-foreground)">
                        No LLMs created by this member.
                    </p>
                </div>
            );
        }

        return (
            <div className="space-y-4">
                {llms.map((llm) => (
                    <div
                        key={llm.id}
                        className="p-4 rounded-md border border-(--border) bg-(--secondary) hover:bg-(--muted) transition-colors duration-200"
                    >
                        <div className="flex justify-between items-start mb-4">
                            <div className="flex items-center">
                                <Server className="h-4 w-4 text-(--primary) mr-2" />
                                <h3 className="font-medium">
                                    {llm.api_type.charAt(0).toUpperCase() + llm.api_type.slice(1)}
                                </h3>
                            </div>
                            <Badge
                                variant="outline"
                                className="bg-(--primary)/10 text-(--primary) border-(--primary)/20"
                            >
                                {llm.model}
                            </Badge>
                        </div>
                        <div className="flex flex-col space-y-2 text-sm">
                            <div className="flex items-center text-xs text-(--muted-foreground)">
                                <Cpu className="mr-1 h-3 w-3" />
                                <span>Model: {llm.model}</span>
                            </div>
                            <div className="flex items-center text-xs text-(--muted-foreground)">
                                <Key className="mr-1 h-3 w-3" />
                                <span>Max Tokens: {llm.max_tokens.toLocaleString()}</span>
                            </div>
                            <div className="flex items-center text-xs text-(--muted-foreground)">
                                <Calendar className="mr-1 h-3 w-3" />
                                <span>
                                    Created{" "}
                                    {formatDistanceToNow(new Date(llm.created_at), {
                                        addSuffix: true,
                                    })}
                                </span>
                            </div>
                            <div className="flex items-center text-xs text-(--muted-foreground)">
                                <Calendar className="mr-1 h-3 w-3" />
                                <span>
                                    Updated{" "}
                                    {formatDistanceToNow(new Date(llm.updated_at), {
                                        addSuffix: true,
                                    })}
                                </span>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        );
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[500px] bg-(--background) border-(--border) [&_[data-slot=dialog-close]]:hover:opacity-100 [&_[data-slot=dialog-close]]:cursor-pointer [&_[data-slot=dialog-close]]:transition-opacity [&_[data-slot=dialog-close]]:duration-200">
                <DialogHeader>
                    <div className="flex items-center gap-4">
                        <Avatar className="h-12 w-12 border border-(--border)">
                            {member.avatar_url ? (
                                <AvatarImage src={member.avatar_url} alt={fullName} />
                            ) : null}
                            <AvatarFallback className="bg-(--primary)/10 text-(--primary) text-lg">
                                {getInitials(fullName)}
                            </AvatarFallback>
                        </Avatar>
                        <div>
                            <DialogTitle className="text-xl">{fullName}</DialogTitle>
                            <DialogDescription>Member Details</DialogDescription>
                        </div>
                    </div>
                </DialogHeader>

                <div className="space-y-6 py-4">
                    <div className="space-y-2">
                        <h3 className="text-sm font-medium">User Information</h3>
                        <div className="p-3 rounded-md bg-(--secondary) space-y-2">
                            <div className="flex items-center text-sm">
                                <User className="mr-2 h-4 w-4 text-(--muted-foreground)" />
                                <span className="font-medium">Username:</span>
                                <span className="ml-2 text-(--muted-foreground)">
                                    {member.username}
                                </span>
                            </div>
                            <div className="flex items-center text-sm">
                                <svg
                                    xmlns="http://www.w3.org/2000/svg"
                                    viewBox="0 0 24 24"
                                    fill="none"
                                    stroke="currentColor"
                                    strokeWidth="2"
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    className="mr-2 h-4 w-4 text-(--muted-foreground)"
                                >
                                    <path d="M22 17.5l-9.9 1.16-9.9-1.16a1 1 0 0 0-1.1.87v3.38a1 1 0 0 0 .9.95l10 1.15 10-1.15a1 1 0 0 0 .9-.95v-3.38a1 1 0 0 0-1.1-.87z" />
                                    <path d="M6.89 6.89A3.13 3.13 0 0 1 8 2a3.13 3.13 0 0 1 3 3.13V18.5" />
                                    <path d="M15.89 6.89A3.13 3.13 0 0 0 16 2a3.13 3.13 0 0 0-3 3.13V18.5" />
                                </svg>
                                <span className="font-medium">Status:</span>
                                <span
                                    className={`ml-2 ${
                                        member.is_active ? "text-green-500" : "text-red-500"
                                    }`}
                                >
                                    {member.is_active ? "Active" : "Inactive"}
                                </span>
                            </div>
                            <div className="flex items-center text-sm">
                                <svg
                                    xmlns="http://www.w3.org/2000/svg"
                                    viewBox="0 0 24 24"
                                    fill="none"
                                    stroke="currentColor"
                                    strokeWidth="2"
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    className="mr-2 h-4 w-4 text-(--muted-foreground)"
                                >
                                    <rect width="20" height="16" x="2" y="4" rx="2" />
                                    <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7" />
                                </svg>
                                <span className="font-medium">Email:</span>
                                <span className="ml-2 text-(--muted-foreground)">
                                    {member.email}
                                </span>
                            </div>
                            <div className="flex items-center text-sm">
                                <Calendar className="mr-2 h-4 w-4 text-(--muted-foreground)" />
                                <span className="font-medium">Joined:</span>
                                <span className="ml-2 text-(--muted-foreground)">
                                    {formatDistanceToNow(new Date(member.date_joined), {
                                        addSuffix: true,
                                    })}
                                </span>
                            </div>
                            <div className="flex items-center text-sm">
                                <Calendar className="mr-2 h-4 w-4 text-(--muted-foreground)" />
                                <span className="font-medium">Last Login:</span>
                                <span className="ml-2 text-(--muted-foreground)">
                                    {member.last_login
                                        ? formatDistanceToNow(new Date(member.last_login), {
                                              addSuffix: true,
                                          })
                                        : "Never"}
                                </span>
                            </div>
                        </div>
                    </div>

                    <div className="space-y-2">
                        <div className="flex items-center justify-between">
                            <h3 className="text-sm font-medium">LLMs Created by {fullName}</h3>
                            {isLoading && (
                                <div className="flex items-center text-xs text-(--muted-foreground)">
                                    <Loader2 className="h-3 w-3 animate-spin mr-1" />
                                    Loading...
                                </div>
                            )}
                        </div>
                        <ScrollArea className="h-[250px] rounded-md border border-(--border) p-4">
                            {renderLLMsList()}
                        </ScrollArea>
                    </div>
                </div>

                <DialogFooter>
                    <Button
                        type="button"
                        variant="outline"
                        onClick={() => onOpenChange(false)}
                        className="font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--border) bg-(--background) text-(--foreground) hover:bg-(--muted) h-10 cursor-pointer"
                    >
                        <span className="relative z-10">Close</span>
                        <span className="absolute inset-0 bg-(--muted)/50 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}
