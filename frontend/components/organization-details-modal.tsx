"use client";

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
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
import { Skeleton } from "@/components/ui/skeleton";
import { formatDistanceToNow } from "date-fns";
import Cookies from "js-cookie";
import {
    AlertCircle,
    Bot,
    Calendar,
    ExternalLink,
    Globe,
    Loader2,
    LogOut,
    Users,
} from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { toast } from "sonner";
import { LeaveOrganizationDialog } from "./leave-organization-dialog";
import { Organization } from "./organization-card";

interface Member {
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

interface OrganizationDetailsModalProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    organization: Organization | null;
}

export function OrganizationDetailsModal({
    open,
    onOpenChange,
    organization,
}: OrganizationDetailsModalProps) {
    const router = useRouter();
    const [members, setMembers] = useState<Member[]>([]);
    const [isLoadingMembers, setIsLoadingMembers] = useState(false);
    const [membersError, setMembersError] = useState<string | null>(null);
    const [isLeaveDialogOpen, setIsLeaveDialogOpen] = useState(false);

    const fetchMembers = async () => {
        if (!organization) return;

        setIsLoadingMembers(true);
        setMembersError(null);

        try {
            const accessToken = Cookies.get("access_token");
            if (!accessToken) {
                throw new Error("Authentication token not found");
            }

            const response = await fetch(
                `http://localhost:8080/api/v1/organizations/${organization.id}/members/`,
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
                throw new Error(data.error || "Failed to fetch organization members");
            }

            setMembers(data.members || []);
        } catch (err) {
            const errorMessage =
                err instanceof Error ? err.message : "An error occurred while fetching members";
            setMembersError(errorMessage);
            toast.error(errorMessage, {
                style: {
                    backgroundColor: "var(--destructive)",
                    color: "white",
                    border: "none",
                },
            });
        } finally {
            setIsLoadingMembers(false);
        }
    };

    useEffect(() => {
        if (open && organization) {
            fetchMembers();
        }
    }, [open, organization]);

    if (!organization) return null;

    const getInitials = (name: string) => {
        return name
            .split(" ")
            .map((part) => part[0])
            .join("")
            .toUpperCase()
            .substring(0, 2);
    };

    const ownerFullName =
        organization.owner.first_name && organization.owner.last_name
            ? `${organization.owner.first_name} ${organization.owner.last_name}`
            : organization.owner.username;

    const handleLeaveSuccess = () => {
        onOpenChange(false);
    };

    const handleAgentStudioClick = () => {
        onOpenChange(false);
        router.push(`/organizations/${organization.id}/agent-studio`);
    };

    const renderMembersList = () => {
        if (isLoadingMembers) {
            return (
                <div className="space-y-4">
                    {[...Array(3)].map((_, index) => (
                        <div key={`skeleton-${index}`} className="flex items-center gap-3">
                            <Skeleton className="h-10 w-10 rounded-full" />
                            <div className="space-y-2">
                                <Skeleton className="h-4 w-40" />
                                <Skeleton className="h-3 w-32" />
                            </div>
                        </div>
                    ))}
                </div>
            );
        }

        if (membersError) {
            return (
                <div className="flex flex-col items-center justify-center p-4 text-center">
                    <div className="h-10 w-10 rounded-full bg-(--destructive)/10 flex items-center justify-center mb-3">
                        <AlertCircle className="h-5 w-5 text-(--destructive)" />
                    </div>
                    <h3 className="text-sm font-medium mb-1">Failed to load members</h3>
                    <p className="text-xs text-(--muted-foreground) mb-3">{membersError}</p>
                    <Button
                        onClick={fetchMembers}
                        variant="outline"
                        size="sm"
                        className="h-8 text-xs"
                    >
                        Retry
                    </Button>
                </div>
            );
        }

        if (members.length === 0) {
            return (
                <div className="flex flex-col items-center justify-center p-4 text-center">
                    <p className="text-sm text-(--muted-foreground)">
                        No members found in this organization.
                    </p>
                </div>
            );
        }

        return (
            <div className="space-y-3">
                {members.map((member) => {
                    const fullName =
                        member.first_name && member.last_name
                            ? `${member.first_name} ${member.last_name}`
                            : member.username;

                    return (
                        <div
                            key={member.username}
                            className="flex items-center gap-3 p-2 rounded-md"
                        >
                            <Avatar className="h-10 w-10 border border-(--border)">
                                {member.avatar_url ? (
                                    <AvatarImage src={member.avatar_url} alt={fullName} />
                                ) : null}
                                <AvatarFallback className="bg-(--secondary) text-(--foreground) text-sm">
                                    {getInitials(fullName)}
                                </AvatarFallback>
                            </Avatar>
                            <div className="flex flex-col">
                                <div className="flex items-center">
                                    <span className="font-medium text-sm">{fullName}</span>
                                    {!member.is_active && (
                                        <span className="ml-2 text-xs px-1.5 py-0.5 rounded-full bg-(--muted) text-(--muted-foreground)">
                                            Inactive
                                        </span>
                                    )}
                                </div>
                                <div className="flex flex-col sm:flex-row sm:gap-3">
                                    <span className="text-xs text-(--muted-foreground)">
                                        @{member.username}
                                    </span>
                                    <span className="text-xs text-(--muted-foreground)">
                                        {member.email}
                                    </span>
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>
        );
    };

    return (
        <>
            <Dialog open={open} onOpenChange={onOpenChange}>
                <DialogContent className="sm:max-w-[500px] bg-(--background) border-(--border) [&_[data-slot=dialog-close]]:hover:opacity-100 [&_[data-slot=dialog-close]]:cursor-pointer [&_[data-slot=dialog-close]]:transition-opacity [&_[data-slot=dialog-close]]:duration-200">
                    <DialogHeader>
                        <div className="flex items-center gap-4">
                            <Avatar className="h-12 w-12 border border-(--border)">
                                {organization.logo_url ? (
                                    <AvatarImage
                                        src={organization.logo_url}
                                        alt={organization.name}
                                    />
                                ) : null}
                                <AvatarFallback className="bg-(--primary)/10 text-(--primary) text-lg">
                                    {getInitials(organization.name)}
                                </AvatarFallback>
                            </Avatar>
                            <div>
                                <DialogTitle className="text-xl">{organization.name}</DialogTitle>
                                <DialogDescription>Owned by {ownerFullName}</DialogDescription>
                            </div>
                        </div>
                    </DialogHeader>

                    <div className="space-y-6 py-4">
                        {organization.description && (
                            <div className="space-y-2">
                                <h3 className="text-sm font-medium">Description</h3>
                                <div className="p-3 rounded-md bg-(--secondary) text-sm">
                                    {organization.description}
                                </div>
                            </div>
                        )}

                        {organization.website && (
                            <div className="space-y-2">
                                <h3 className="text-sm font-medium">Website</h3>
                                <div className="p-3 rounded-md bg-(--secondary) text-sm">
                                    <a
                                        href={
                                            organization.website.startsWith("http")
                                                ? organization.website
                                                : `https://${organization.website}`
                                        }
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="text-(--primary) hover:underline flex items-center"
                                    >
                                        <Globe className="mr-2 h-4 w-4" />
                                        <span>
                                            {organization.website.replace(/^https?:\/\//i, "")}
                                        </span>
                                        <ExternalLink className="ml-1 h-3 w-3" />
                                    </a>
                                </div>
                            </div>
                        )}

                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <h3 className="text-sm font-medium">Members</h3>
                                <div className="p-3 rounded-md bg-(--secondary) text-sm flex items-center">
                                    <Users className="mr-2 h-4 w-4 text-(--muted-foreground)" />
                                    <span>
                                        {organization.member_count}{" "}
                                        {organization.member_count === 1 ? "member" : "members"}
                                    </span>
                                </div>
                            </div>
                            <div className="space-y-2">
                                <h3 className="text-sm font-medium">Created</h3>
                                <div className="p-3 rounded-md bg-(--secondary) text-sm flex items-center">
                                    <Calendar className="mr-2 h-4 w-4 text-(--muted-foreground)" />
                                    <span>
                                        {formatDistanceToNow(new Date(organization.created_at), {
                                            addSuffix: true,
                                        })}
                                    </span>
                                </div>
                            </div>
                        </div>

                        <div className="space-y-2">
                            <div className="flex items-center justify-between">
                                <h3 className="text-sm font-medium">Member List</h3>
                                {isLoadingMembers && (
                                    <div className="flex items-center text-xs text-(--muted-foreground)">
                                        <Loader2 className="h-3 w-3 animate-spin mr-1" />
                                        Loading...
                                    </div>
                                )}
                            </div>
                            <ScrollArea className="h-[200px] rounded-md border border-(--border) p-4">
                                {renderMembersList()}
                            </ScrollArea>
                        </div>
                    </div>

                    <DialogFooter className="flex flex-col sm:flex-row sm:justify-between w-full gap-2">
                        <div className="flex flex-col sm:flex-row gap-2 w-full">
                            <Button
                                type="button"
                                variant="outline"
                                onClick={handleAgentStudioClick}
                                className="font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--primary) bg-(--background) text-(--primary) hover:bg-(--primary)/10 h-10 cursor-pointer w-full sm:flex-1"
                            >
                                <span className="relative z-10 flex items-center justify-center">
                                    <Bot className="mr-2 h-4 w-4" />
                                    Agent Studio
                                </span>
                                <span className="absolute inset-0 bg-(--primary)/10 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                            </Button>
                            <Button
                                type="button"
                                variant="destructive"
                                onClick={() => setIsLeaveDialogOpen(true)}
                                className="font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--destructive) bg-(--destructive) text-(--destructive-foreground) dark:bg-(--destructive) dark:text-(--destructive-foreground) dark:border-(--destructive) h-10 cursor-pointer w-full sm:flex-1"
                            >
                                <span className="relative z-10 flex items-center justify-center">
                                    <LogOut className="mr-2 h-4 w-4" />
                                    Leave Organization
                                </span>
                                <span className="absolute inset-0 bg-(--destructive-foreground)/10 dark:bg-(--destructive-foreground)/20 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                            </Button>
                        </div>
                    </DialogFooter>
                </DialogContent>
            </Dialog>

            <LeaveOrganizationDialog
                open={isLeaveDialogOpen}
                onOpenChange={setIsLeaveDialogOpen}
                organizationId={organization.id}
                organizationName={organization.name}
                onLeaveSuccess={handleLeaveSuccess}
            />
        </>
    );
}
