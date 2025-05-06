"use client";

import { useAppSelector } from "@/app/store/hooks";
import { selectUser } from "@/app/store/slices/userSlice";
import { AgentsTab } from "@/components/agents-tab";
import { DashboardNavbar } from "@/components/dashboard-navbar";
import { LLMsTab } from "@/components/llms-tab";
import { MCPServersTab } from "@/components/mcp-servers-tab";
import { ProtectedRoute } from "@/components/protected-route";
import { TransferOwnershipDialog } from "@/components/transfer-ownership-dialog";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { formatDistanceToNow } from "date-fns";
import { motion } from "framer-motion";
import Cookies from "js-cookie";
import { ArrowLeft, Bot, Calendar, Cpu, Loader2, Server, Trash2, User, Users } from "lucide-react";
import { useParams, useRouter } from "next/navigation";
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

interface Organization {
    id: string;
    name: string;
    description: string;
    website: string;
    logo_url: string;
    owner: {
        id: string;
        username: string;
        email: string;
        first_name: string;
        last_name: string;
    };
    member_count: number;
    created_at: string;
    updated_at: string;
}

export default function MemberDetailsPage() {
    const router = useRouter();
    const params = useParams();
    const organizationId = params.id as string;
    const username = params.username as string;
    const currentUser = useAppSelector(selectUser);

    const [member, setMember] = useState<OrganizationMember | null>(null);
    const [organization, setOrganization] = useState<Organization | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [isOwner, setIsOwner] = useState(false);

    const [isRemoveDialogOpen, setIsRemoveDialogOpen] = useState(false);
    const [isRemoving, setIsRemoving] = useState(false);
    const [isTransferDialogOpen, setIsTransferDialogOpen] = useState(false);

    const fetchOrganization = async () => {
        try {
            const accessToken = Cookies.get("access_token");
            if (!accessToken) {
                throw new Error("Authentication token not found");
            }

            const response = await fetch(
                `http://localhost:8080/api/v1/organizations/${organizationId}/`,
                {
                    method: "GET",
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${accessToken}`,
                    },
                }
            );

            if (!response.ok) {
                throw new Error("Failed to fetch organization details");
            }

            const data = await response.json();
            setOrganization(data.organization);

            if (currentUser && data.organization.owner.username === currentUser.username) {
                setIsOwner(true);
            }
        } catch (err) {
            const errorMessage =
                err instanceof Error
                    ? err.message
                    : "An error occurred while fetching organization details";
            setError(errorMessage);
            toast.error(errorMessage, {
                style: {
                    backgroundColor: "var(--destructive)",
                    color: "white",
                    border: "none",
                },
            });
        }
    };

    const fetchMember = async () => {
        setIsLoading(true);
        setError(null);

        try {
            const accessToken = Cookies.get("access_token");
            if (!accessToken) {
                throw new Error("Authentication token not found");
            }

            const response = await fetch(
                `http://localhost:8080/api/v1/organizations/${organizationId}/members/`,
                {
                    method: "GET",
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${accessToken}`,
                    },
                }
            );

            if (!response.ok) {
                throw new Error("Failed to fetch members");
            }

            const data = await response.json();
            const foundMember = data.members.find(
                (m: OrganizationMember) => m.username === username
            );

            if (!foundMember) {
                throw new Error("Member not found");
            }

            setMember(foundMember);
        } catch (err) {
            const errorMessage =
                err instanceof Error
                    ? err.message
                    : "An error occurred while fetching member details";
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
        fetchOrganization();
        fetchMember();
    }, [organizationId, username]);

    const handleRemoveMember = async () => {
        if (!member) return;

        setIsRemoving(true);
        try {
            const accessToken = Cookies.get("access_token");
            if (!accessToken) {
                throw new Error("Authentication token not found");
            }

            const payload = member.email ? { email: member.email } : { username: member.username };

            const response = await fetch(
                `http://localhost:8080/api/v1/organizations/${organizationId}/members/remove/`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${accessToken}`,
                    },
                    body: JSON.stringify(payload),
                }
            );

            const data = await response.json();

            if (!response.ok) {
                if (data.errors) {
                    Object.entries(data.errors).forEach(([field, errors]: [string, any]) => {
                        if (Array.isArray(errors) && errors.length > 0) {
                            toast.error(`${field}: ${errors[0]}`, {
                                style: {
                                    backgroundColor: "var(--destructive)",
                                    color: "white",
                                    border: "none",
                                },
                            });
                        }
                    });
                } else if (data.error) {
                    throw new Error(data.error);
                } else {
                    throw new Error("Failed to remove member");
                }
            } else {
                toast.success("Member removed successfully", {
                    style: {
                        backgroundColor: "oklch(0.45 0.18 142.71)",
                        color: "white",
                        border: "none",
                    },
                });

                router.push(`/organizations/${organizationId}`);
            }
        } catch (err) {
            const errorMessage =
                err instanceof Error ? err.message : "An error occurred while removing member";
            toast.error(errorMessage, {
                style: {
                    backgroundColor: "var(--destructive)",
                    color: "white",
                    border: "none",
                },
            });
        } finally {
            setIsRemoving(false);
            setIsRemoveDialogOpen(false);
        }
    };

    const getInitials = (name: string) => {
        return name
            .split(" ")
            .map((part) => part[0])
            .join("")
            .toUpperCase()
            .substring(0, 2);
    };

    useEffect(() => {
        if (!isOwner && !isLoading) {
            router.push(`/organizations/${organizationId}`);
        }
    }, [isOwner, isLoading, organizationId, router]);

    if (!isOwner && !isLoading) {
        return null;
    }

    const fullName =
        member?.first_name && member?.last_name
            ? `${member.first_name} ${member.last_name}`
            : member?.username || "";

    return (
        <ProtectedRoute>
            <div className="min-h-screen flex flex-col bg-(--background)">
                <DashboardNavbar />
                <div className="flex-1 container mx-auto px-4 pt-24 pb-8">
                    {isLoading ? (
                        <div className="flex justify-center items-center h-64">
                            <Loader2 className="h-8 w-8 animate-spin text-(--muted-foreground)" />
                        </div>
                    ) : error ? (
                        <div className="flex flex-col items-center justify-center h-64 text-center">
                            <p className="text-lg text-(--destructive) mb-4">{error}</p>
                            <Button
                                onClick={(e) => {
                                    e.preventDefault();
                                    router.push(`/organizations/${organizationId}`);
                                }}
                                className="font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--border) bg-(--background) text-(--foreground) hover:bg-(--muted) h-10 cursor-pointer"
                            >
                                <span className="relative z-10 flex items-center">
                                    <ArrowLeft className="mr-2 h-4 w-4" />
                                    Back to Organization
                                </span>
                                <span className="absolute inset-0 bg-(--muted)/50 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                            </Button>
                        </div>
                    ) : (
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.5 }}
                        >
                            <div className="hidden md:flex md:items-center md:justify-between gap-4 mb-6">
                                <Button
                                    onClick={(e) => {
                                        e.preventDefault();
                                        router.push(`/organizations/${organizationId}`);
                                    }}
                                    variant="outline"
                                    className="font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--border) bg-(--background) text-(--foreground) hover:bg-(--muted) h-10 cursor-pointer"
                                >
                                    <span className="relative z-10 flex items-center">
                                        <ArrowLeft className="mr-2 h-4 w-4" />
                                        Back to Organization
                                    </span>
                                    <span className="absolute inset-0 bg-(--muted)/50 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                                </Button>

                                <div className="flex space-x-3">
                                    <Button
                                        onClick={() => setIsTransferDialogOpen(true)}
                                        variant="outline"
                                        className="font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--border) bg-(--background) text-(--primary) hover:bg-(--primary)/10 cursor-pointer h-10 w-[250px]"
                                    >
                                        <span className="relative z-10 flex items-center justify-center">
                                            <Users className="mr-2 h-4 w-4" />
                                            <span className="whitespace-nowrap">Transfer</span>
                                        </span>
                                        <span className="absolute inset-0 bg-(--primary)/10 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                                    </Button>

                                    <Button
                                        onClick={() => setIsRemoveDialogOpen(true)}
                                        variant="outline"
                                        className="font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--border) bg-(--background) text-(--destructive) hover:bg-(--destructive)/10 cursor-pointer h-10 w-[250px]"
                                    >
                                        <span className="relative z-10 flex items-center justify-center">
                                            <Trash2 className="mr-2 h-4 w-4" />
                                            <span className="whitespace-nowrap">Remove</span>
                                        </span>
                                        <span className="absolute inset-0 bg-(--destructive)/10 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                                    </Button>
                                </div>
                            </div>

                            <div className="flex md:hidden mb-6">
                                <Button
                                    onClick={(e) => {
                                        e.preventDefault();
                                        router.push(`/organizations/${organizationId}`);
                                    }}
                                    variant="outline"
                                    className="font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--border) bg-(--background) text-(--foreground) hover:bg-(--muted) h-10 cursor-pointer w-full"
                                >
                                    <span className="relative z-10 flex items-center">
                                        <ArrowLeft className="mr-2 h-4 w-4" />
                                        Back to Organization
                                    </span>
                                    <span className="absolute inset-0 bg-(--muted)/50 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                                </Button>
                            </div>

                            <Card className="mb-6">
                                <CardHeader>
                                    <div className="flex items-center gap-4">
                                        <Avatar className="h-16 w-16 border border-(--border)">
                                            {member?.avatar_url ? (
                                                <AvatarImage
                                                    src={member.avatar_url}
                                                    alt={fullName}
                                                />
                                            ) : null}
                                            <AvatarFallback className="bg-(--primary)/10 text-(--primary) text-xl">
                                                {getInitials(fullName)}
                                            </AvatarFallback>
                                        </Avatar>
                                        <div>
                                            <h1 className="text-2xl font-bold">{fullName}</h1>
                                            <p className="text-(--muted-foreground)">
                                                Member Details
                                            </p>
                                        </div>
                                    </div>
                                </CardHeader>
                                <CardContent>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <div className="space-y-2">
                                            <div className="flex items-center text-sm">
                                                <User className="mr-2 h-4 w-4 text-(--muted-foreground)" />
                                                <span className="font-medium">Username:</span>
                                                <span className="ml-2 text-(--muted-foreground)">
                                                    {member?.username}
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
                                                    <rect
                                                        width="20"
                                                        height="16"
                                                        x="2"
                                                        y="4"
                                                        rx="2"
                                                    />
                                                    <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7" />
                                                </svg>
                                                <span className="font-medium">Email:</span>
                                                <span className="ml-2 text-(--muted-foreground)">
                                                    {member?.email}
                                                </span>
                                            </div>
                                        </div>
                                        <div className="space-y-2">
                                            <div className="flex items-center text-sm">
                                                <Calendar className="mr-2 h-4 w-4 text-(--muted-foreground)" />
                                                <span className="font-medium">Joined:</span>
                                                <span className="ml-2 text-(--muted-foreground)">
                                                    {member?.date_joined
                                                        ? formatDistanceToNow(
                                                              new Date(member.date_joined),
                                                              {
                                                                  addSuffix: true,
                                                              }
                                                          )
                                                        : "Unknown"}
                                                </span>
                                            </div>
                                            <div className="flex items-center text-sm">
                                                <Calendar className="mr-2 h-4 w-4 text-(--muted-foreground)" />
                                                <span className="font-medium">Last Login:</span>
                                                <span className="ml-2 text-(--muted-foreground)">
                                                    {member?.last_login
                                                        ? formatDistanceToNow(
                                                              new Date(member.last_login),
                                                              {
                                                                  addSuffix: true,
                                                              }
                                                          )
                                                        : "Never"}
                                                </span>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="md:hidden mt-6 grid grid-cols-2 gap-3">
                                        <Button
                                            onClick={() => setIsTransferDialogOpen(true)}
                                            variant="outline"
                                            className="font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--border) bg-(--background) text-(--primary) hover:bg-(--primary)/10 cursor-pointer h-10 w-full"
                                        >
                                            <span className="relative z-10 flex items-center justify-center">
                                                <Users className="mr-2 h-4 w-4" />
                                                <span className="whitespace-nowrap">Transfer</span>
                                            </span>
                                            <span className="absolute inset-0 bg-(--primary)/10 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                                        </Button>

                                        <Button
                                            onClick={() => setIsRemoveDialogOpen(true)}
                                            variant="outline"
                                            className="font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--border) bg-(--background) text-(--destructive) hover:bg-(--destructive)/10 cursor-pointer h-10 w-full"
                                        >
                                            <span className="relative z-10 flex items-center justify-center">
                                                <Trash2 className="mr-2 h-4 w-4" />
                                                <span className="whitespace-nowrap">Remove</span>
                                            </span>
                                            <span className="absolute inset-0 bg-(--destructive)/10 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                                        </Button>
                                    </div>
                                </CardContent>
                            </Card>

                            <Tabs defaultValue="llms" className="w-full">
                                <TabsList className="flex w-full gap-1 bg-(--card) p-0.5 rounded-lg overflow-hidden h-10">
                                    <TabsTrigger
                                        value="llms"
                                        className="flex-1 data-[state=active]:bg-(--primary) data-[state=active]:text-(--primary-foreground) data-[state=active]:shadow-sm transition-all duration-200 hover:bg-(--accent) data-[state=active]:hover:bg-(--primary) rounded-md cursor-pointer flex items-center justify-center py-1.5 px-2 m-0 h-9 w-full"
                                    >
                                        <div className="flex items-center">
                                            <Cpu className="mr-2 h-4 w-4" />
                                            <span>LLMs</span>
                                        </div>
                                    </TabsTrigger>
                                    <TabsTrigger
                                        value="mcp-servers"
                                        className="flex-1 data-[state=active]:bg-(--primary) data-[state=active]:text-(--primary-foreground) data-[state=active]:shadow-sm transition-all duration-200 hover:bg-(--accent) data-[state=active]:hover:bg-(--primary) rounded-md cursor-pointer flex items-center justify-center py-1.5 px-2 m-0 h-9 w-full"
                                    >
                                        <div className="flex items-center">
                                            <Server className="mr-2 h-4 w-4" />
                                            <span>MCP Servers</span>
                                        </div>
                                    </TabsTrigger>
                                    <TabsTrigger
                                        value="agents"
                                        className="flex-1 data-[state=active]:bg-(--primary) data-[state=active]:text-(--primary-foreground) data-[state=active]:shadow-sm transition-all duration-200 hover:bg-(--accent) data-[state=active]:hover:bg-(--primary) rounded-md cursor-pointer flex items-center justify-center py-1.5 px-2 m-0 h-9 w-full"
                                    >
                                        <div className="flex items-center">
                                            <Bot className="mr-2 h-4 w-4" />
                                            <span>Agents</span>
                                        </div>
                                    </TabsTrigger>
                                </TabsList>

                                <TabsContent
                                    value="llms"
                                    className="mt-6 data-[state=active]:animate-in data-[state=inactive]:animate-out data-[state=inactive]:fade-out-50 data-[state=active]:fade-in-50 duration-200"
                                >
                                    <motion.div
                                        initial={{ opacity: 0, y: 20 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        transition={{
                                            type: "spring",
                                            stiffness: 300,
                                            damping: 30,
                                            delay: 0.1,
                                        }}
                                    >
                                        <Card>
                                            <CardHeader>
                                                <h2 className="text-xl font-bold">
                                                    Language Models
                                                </h2>
                                                <p className="text-(--muted-foreground)">
                                                    LLMs created by {fullName}
                                                </p>
                                            </CardHeader>
                                            <CardContent>
                                                <LLMsTab
                                                    organizationId={organizationId}
                                                    filterByUsername={member?.username}
                                                    readOnly={true}
                                                />
                                            </CardContent>
                                        </Card>
                                    </motion.div>
                                </TabsContent>

                                <TabsContent
                                    value="mcp-servers"
                                    className="mt-6 data-[state=active]:animate-in data-[state=inactive]:animate-out data-[state=inactive]:fade-out-50 data-[state=active]:fade-in-50 duration-200"
                                >
                                    <motion.div
                                        initial={{ opacity: 0, y: 20 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        transition={{
                                            type: "spring",
                                            stiffness: 300,
                                            damping: 30,
                                            delay: 0.1,
                                        }}
                                    >
                                        <Card>
                                            <CardHeader>
                                                <h2 className="text-xl font-bold">MCP Servers</h2>
                                                <p className="text-(--muted-foreground)">
                                                    MCP Servers created by {fullName}
                                                </p>
                                            </CardHeader>
                                            <CardContent>
                                                <MCPServersTab
                                                    organizationId={organizationId}
                                                    filterByUsername={member?.username}
                                                    readOnly={true}
                                                />
                                            </CardContent>
                                        </Card>
                                    </motion.div>
                                </TabsContent>

                                <TabsContent
                                    value="agents"
                                    className="mt-6 data-[state=active]:animate-in data-[state=inactive]:animate-out data-[state=inactive]:fade-out-50 data-[state=active]:fade-in-50 duration-200"
                                >
                                    <motion.div
                                        initial={{ opacity: 0, y: 20 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        transition={{
                                            type: "spring",
                                            stiffness: 300,
                                            damping: 30,
                                            delay: 0.1,
                                        }}
                                    >
                                        <Card>
                                            <CardHeader>
                                                <h2 className="text-xl font-bold">Agents</h2>
                                                <p className="text-(--muted-foreground)">
                                                    Agents created by {fullName}
                                                </p>
                                            </CardHeader>
                                            <CardContent>
                                                <AgentsTab organizationId={organizationId} />
                                            </CardContent>
                                        </Card>
                                    </motion.div>
                                </TabsContent>
                            </Tabs>

                            {/* Remove Member Dialog */}
                            {isRemoveDialogOpen && (
                                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                                    <div className="bg-(--background) rounded-lg p-6 max-w-md w-full">
                                        <h2 className="text-xl font-bold mb-4">Remove Member</h2>
                                        <p className="mb-6">
                                            Are you sure you want to remove{" "}
                                            <span className="font-semibold">{fullName}</span> from
                                            this organization? This action cannot be undone.
                                        </p>
                                        <div className="grid grid-cols-2 gap-3 w-full">
                                            <Button
                                                type="button"
                                                variant="outline"
                                                onClick={() => setIsRemoveDialogOpen(false)}
                                                disabled={isRemoving}
                                                className="font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--border) bg-(--background) text-(--foreground) hover:bg-(--muted) h-10 cursor-pointer w-full"
                                            >
                                                <span className="relative z-10 flex items-center justify-center">
                                                    <span>Cancel</span>
                                                </span>
                                                <span className="absolute inset-0 bg-(--muted)/50 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                                            </Button>
                                            <Button
                                                type="button"
                                                variant="destructive"
                                                onClick={handleRemoveMember}
                                                disabled={isRemoving}
                                                className="font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--destructive) bg-(--destructive) text-white hover:bg-(--destructive)/90 h-10 cursor-pointer w-full"
                                            >
                                                {isRemoving ? (
                                                    <Loader2 className="h-4 w-4 animate-spin" />
                                                ) : (
                                                    <span className="relative z-10 flex items-center justify-center">
                                                        <Trash2 className="mr-2 h-4 w-4" />
                                                        <span>Remove</span>
                                                    </span>
                                                )}
                                                <span className="absolute inset-0 bg-(--destructive)/90 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                                            </Button>
                                        </div>
                                    </div>
                                </div>
                            )}

                            {/* Transfer Ownership Dialog */}
                            {member && (
                                <TransferOwnershipDialog
                                    open={isTransferDialogOpen}
                                    onOpenChange={setIsTransferDialogOpen}
                                    organizationId={organizationId}
                                    organizationName={organization?.name || ""}
                                    member={member}
                                />
                            )}
                        </motion.div>
                    )}
                </div>
            </div>
        </ProtectedRoute>
    );
}
