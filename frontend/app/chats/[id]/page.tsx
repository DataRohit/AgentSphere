"use client";

import { DashboardNavbar } from "@/components/dashboard-navbar";
import { DeleteChatDialog } from "@/components/delete-chat-dialog";
import { ProtectedRoute } from "@/components/protected-route";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { UpdateChatDialog } from "@/components/update-chat-dialog";
import { format } from "date-fns";
import Cookies from "js-cookie";
import { ArrowLeft, Calendar, MessageCircle, Pencil, Trash2, User } from "lucide-react";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { toast } from "sonner";

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

export default function ChatDetailPage() {
    const router = useRouter();
    const params = useParams();
    const chatId = params.id as string;
    const [chat, setChat] = useState<Chat | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [isUpdateDialogOpen, setIsUpdateDialogOpen] = useState(false);
    const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
    const [isViewOnly, setIsViewOnly] = useState(false);

    useEffect(() => {
        fetchChatDetails();

        const searchParams = new URLSearchParams(window.location.search);
        const viewOnly = searchParams.get("viewOnly") === "true";
        setIsViewOnly(viewOnly);
    }, [chatId]);

    const fetchChatDetails = async () => {
        setIsLoading(true);
        try {
            const accessToken = Cookies.get("access_token");
            if (!accessToken) {
                throw new Error("Authentication token not found");
            }

            const response = await fetch(`http://localhost:8080/api/v1/chats/single/${chatId}/`, {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${accessToken}`,
                },
            });

            const data = await response.json();

            if (!response.ok) {
                if (response.status === 404) {
                    toast.error("Chat not found", {
                        className: "bg-(--destructive) text-white border-none",
                    });
                    router.push("/dashboard");
                    return;
                } else if (response.status === 403) {
                    toast.error("You do not have permission to view this chat", {
                        className: "bg-(--destructive) text-white border-none",
                    });
                    router.push("/dashboard");
                    return;
                } else {
                    throw new Error(data.error || "Failed to fetch chat details");
                }
            }

            setChat(data.chat);
        } catch (err) {
            const errorMessage =
                err instanceof Error
                    ? err.message
                    : "An error occurred while fetching chat details";
            toast.error(errorMessage, {
                className: "bg-(--destructive) text-white border-none",
            });
            router.push("/dashboard");
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

    const handleBackClick = () => {
        router.back();
    };

    const handleUpdateClick = () => {
        setIsUpdateDialogOpen(true);
    };

    const handleDeleteClick = () => {
        setIsDeleteDialogOpen(true);
    };

    const handleSuccess = () => {
        fetchChatDetails();
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
                            Back to Conversation Manager
                        </span>
                        <span className="absolute inset-0 bg-(--muted)/50 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                    </Button>

                    {isLoading ? (
                        <div className="space-y-4">
                            <Skeleton className="h-12 w-3/4" />
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <Skeleton className="h-32" />
                                <Skeleton className="h-32" />
                            </div>
                            <Skeleton className="h-64" />
                        </div>
                    ) : chat ? (
                        <div className="space-y-6">
                            <div className="flex flex-col space-y-4">
                                <div>
                                    <div className="flex items-center space-x-2">
                                        <h1 className="text-3xl font-bold tracking-tight">
                                            {chat.title}
                                        </h1>
                                        <Badge
                                            variant="outline"
                                            className={`bg-(--primary)/10 text-(--primary) border-(--primary)/20 w-20 ml-2 ${
                                                chat.is_public ? "text-blue-300" : "text-green-300"
                                            }`}
                                        >
                                            {chat.is_public ? "Public" : "Private"}
                                        </Badge>
                                    </div>
                                    <p className="text-sm text-(--muted-foreground) mt-1">
                                        Conversation with {chat.agent.name}
                                    </p>
                                </div>

                                <div className="flex flex-col space-y-2">
                                    {!isViewOnly && (
                                        <>
                                            <div className="w-full">
                                                <Button
                                                    className="font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--primary) bg-(--primary) text-(--primary-foreground) dark:bg-(--primary) dark:text-(--primary-foreground) dark:border-(--primary) h-10 cursor-pointer w-full"
                                                    onClick={() =>
                                                        router.push(`/conversations/${chat.id}`)
                                                    }
                                                >
                                                    <span className="relative z-10 flex items-center">
                                                        <MessageCircle className="mr-2 h-4 w-4" />
                                                        Continue Chat
                                                    </span>
                                                    <span className="absolute inset-0 bg-(--primary-foreground)/10 dark:bg-(--primary-foreground)/20 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                                                </Button>
                                            </div>
                                            <div className="flex space-x-2 w-full">
                                                <Button
                                                    className="font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--border) bg-(--background) text-(--foreground) hover:bg-(--muted) h-10 cursor-pointer w-1/2"
                                                    variant="outline"
                                                    onClick={handleUpdateClick}
                                                >
                                                    <span className="relative z-10 flex items-center">
                                                        <Pencil className="mr-2 h-4 w-4" />
                                                        Update
                                                    </span>
                                                    <span className="absolute inset-0 bg-(--muted)/50 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                                                </Button>
                                                <Button
                                                    className="font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--destructive) bg-(--destructive) text-white dark:bg-(--destructive) dark:text-white dark:border-(--destructive) h-10 cursor-pointer w-1/2"
                                                    variant="destructive"
                                                    onClick={handleDeleteClick}
                                                >
                                                    <span className="relative z-10 flex items-center">
                                                        <Trash2 className="mr-2 h-4 w-4" />
                                                        Delete
                                                    </span>
                                                    <span className="absolute inset-0 bg-white/10 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                                                </Button>
                                            </div>
                                        </>
                                    )}
                                </div>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <Card>
                                    <CardHeader>
                                        <CardTitle className="flex items-center text-lg">
                                            <Calendar className="mr-2 h-5 w-5 text-(--primary)" />
                                            Timestamps
                                        </CardTitle>
                                    </CardHeader>
                                    <CardContent className="space-y-2">
                                        <div>
                                            <p className="text-sm font-medium text-(--muted-foreground)">
                                                Created
                                            </p>
                                            <p>{formatDate(chat.created_at)}</p>
                                        </div>
                                        <div>
                                            <p className="text-sm font-medium text-(--muted-foreground)">
                                                Last Updated
                                            </p>
                                            <p>{formatDate(chat.updated_at)}</p>
                                        </div>
                                    </CardContent>
                                </Card>

                                <Card>
                                    <CardHeader>
                                        <CardTitle className="flex items-center text-lg">
                                            <User className="mr-2 h-5 w-5 text-(--primary)" />
                                            Details
                                        </CardTitle>
                                    </CardHeader>
                                    <CardContent className="space-y-2">
                                        <div>
                                            <p className="text-sm font-medium text-(--muted-foreground)">
                                                Organization
                                            </p>
                                            <p>{chat.organization.name}</p>
                                        </div>
                                        <div>
                                            <p className="text-sm font-medium text-(--muted-foreground)">
                                                Agent
                                            </p>
                                            <p>{chat.agent.name}</p>
                                        </div>
                                    </CardContent>
                                </Card>
                            </div>

                            <Card>
                                <CardHeader>
                                    <CardTitle className="flex items-center text-lg">
                                        <MessageCircle className="mr-2 h-5 w-5 text-(--primary)" />
                                        Summary
                                    </CardTitle>
                                </CardHeader>
                                <CardContent>
                                    {chat.summary ? (
                                        <div className="p-4 rounded-md bg-(--secondary) text-xs md:text-sm text-(--muted-foreground) whitespace-pre-wrap">
                                            {chat.summary}
                                        </div>
                                    ) : (
                                        <div className="flex flex-col items-center justify-center p-4 rounded-md bg-(--secondary) text-center">
                                            <MessageCircle className="h-8 w-8 text-(--muted-foreground) mb-2" />
                                            <p className="text-sm text-(--muted-foreground)">
                                                No summary available for this chat yet.
                                            </p>
                                        </div>
                                    )}
                                </CardContent>
                            </Card>
                        </div>
                    ) : (
                        <div className="flex flex-col items-center justify-center py-12 text-center border rounded-md bg-(--secondary)">
                            <MessageCircle className="h-12 w-12 text-(--muted-foreground) mb-3" />
                            <h3 className="text-lg font-medium mb-1">Chat not found</h3>
                            <p className="text-sm text-(--muted-foreground) mb-4">
                                The chat you're looking for doesn't exist or you don't have
                                permission to view it.
                            </p>
                        </div>
                    )}
                </div>
            </div>

            {chat && (
                <>
                    <UpdateChatDialog
                        open={isUpdateDialogOpen}
                        onOpenChange={setIsUpdateDialogOpen}
                        organizationId={chat.organization.id}
                        chat={chat}
                        onSuccess={handleSuccess}
                    />
                    <DeleteChatDialog
                        open={isDeleteDialogOpen}
                        onOpenChange={setIsDeleteDialogOpen}
                        chat={chat}
                        onSuccess={handleSuccess}
                    />
                </>
            )}
        </ProtectedRoute>
    );
}
