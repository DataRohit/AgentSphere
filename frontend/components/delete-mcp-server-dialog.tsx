"use client";

import { Button } from "@/components/ui/button";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
import Cookies from "js-cookie";
import { AlertCircle, Loader2, Trash2 } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

interface Tool {
    id: string;
    name: string;
    description: string;
}

interface MCPServer {
    id: string;
    name: string;
    description: string;
    url: string;
    tags: string;
    tools: (string | Tool)[];
    created_at: string;
    updated_at: string;
}

interface DeleteMCPServerDialogProps {
    mcpServer: MCPServer;
    open: boolean;
    onOpenChange: (open: boolean) => void;
    onDeleteSuccess: () => void;
}

export function DeleteMCPServerDialog({
    mcpServer,
    open,
    onOpenChange,
    onDeleteSuccess,
}: DeleteMCPServerDialogProps) {
    const [isDeleting, setIsDeleting] = useState(false);

    const handleDelete = async () => {
        setIsDeleting(true);

        try {
            const accessToken = Cookies.get("access_token");

            if (!accessToken) {
                toast.error("Authentication error. Please log in again.", {
                    style: {
                        backgroundColor: "var(--destructive)",
                        color: "white",
                        border: "none",
                    },
                });
                onOpenChange(false);
                return;
            }

            const response = await fetch(
                `${process.env.NEXT_PUBLIC_API_URL}/tools/mcpserver/${mcpServer.id}/delete/`,
                {
                    method: "DELETE",
                    headers: {
                        Authorization: `Bearer ${accessToken}`,
                    },
                }
            );

            const data = await response.json();

            if (response.ok) {
                toast.success("MCP server deleted successfully", {
                    style: {
                        backgroundColor: "oklch(0.45 0.18 142.71)",
                        color: "white",
                        border: "none",
                    },
                });
                onDeleteSuccess();
                onOpenChange(false);
            } else {
                switch (response.status) {
                    case 401:
                        toast.error(
                            data.error ||
                                "Authentication credentials were not provided or are invalid."
                        );
                        break;
                    case 403:
                        toast.error(
                            data.error || "You do not have permission to delete this MCP server."
                        );
                        break;
                    case 404:
                        toast.error(data.error || "MCP server not found.");
                        break;
                    default:
                        toast.error(
                            data.error || "An error occurred while deleting the MCP server."
                        );
                }
            }
        } catch (err) {
            const errorMessage =
                err instanceof Error
                    ? err.message
                    : "An error occurred while deleting the MCP server";
            toast.error(errorMessage, {
                style: {
                    backgroundColor: "var(--destructive)",
                    color: "white",
                    border: "none",
                },
            });
        } finally {
            setIsDeleting(false);
        }
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[425px] bg-(--background) border-(--border) [&_[data-slot=dialog-close]]:hover:opacity-100 [&_[data-slot=dialog-close]]:cursor-pointer [&_[data-slot=dialog-close]]:transition-opacity [&_[data-slot=dialog-close]]:duration-200">
                <DialogHeader className="text-left">
                    <DialogTitle className="flex items-center text-destructive">
                        <AlertCircle className="mr-2 h-5 w-5" />
                        Delete MCP Server
                    </DialogTitle>
                    <DialogDescription>
                        Are you sure you want to delete this MCP server? This action cannot be
                        undone.
                    </DialogDescription>
                </DialogHeader>

                <div className="py-4">
                    <div className="rounded-md bg-(--destructive)/10 p-4 mb-4">
                        <div className="flex flex-col">
                            <div className="flex items-center mb-2">
                                <AlertCircle className="h-5 w-5 text-(--destructive) mr-2" />
                                <h3 className="text-sm font-medium text-(--destructive)">
                                    Warning
                                </h3>
                            </div>
                            <p className="text-sm text-(--destructive)/80 ml-7">
                                Deleting this MCP server will permanently remove it from your
                                account. Any agents using this server may stop functioning properly.
                            </p>
                        </div>
                    </div>

                    <div className="space-y-4">
                        <div className="space-y-2">
                            <h3 className="text-sm font-medium">MCP Server Details</h3>
                            <div className="p-3 rounded-md bg-(--secondary) space-y-2">
                                <div className="flex items-center text-sm">
                                    <span className="font-medium">Name:</span>
                                    <span className="ml-2 text-(--muted-foreground)">
                                        {mcpServer.name}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <DialogFooter className="flex flex-col sm:flex-row sm:justify-between w-full gap-2">
                    <Button
                        type="button"
                        variant="outline"
                        onClick={() => onOpenChange(false)}
                        disabled={isDeleting}
                        className="font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--border) bg-(--background) text-(--foreground) hover:bg-(--muted) h-10 cursor-pointer w-full sm:flex-1"
                    >
                        <span className="relative z-10">Cancel</span>
                        <span className="absolute inset-0 bg-(--muted)/50 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                    </Button>
                    <Button
                        type="button"
                        variant="destructive"
                        onClick={handleDelete}
                        disabled={isDeleting}
                        className="font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--border) bg-(--destructive) text-(--destructive-foreground) dark:bg-(--destructive) dark:text-(--destructive-foreground) dark:border-(--destructive) h-10 cursor-pointer w-full sm:flex-1"
                    >
                        <span className="relative z-10 flex items-center justify-center">
                            {isDeleting ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Deleting...
                                </>
                            ) : (
                                <>
                                    <Trash2 className="mr-2 h-4 w-4" />
                                    Delete Server
                                </>
                            )}
                        </span>
                        <span className="absolute inset-0 bg-(--destructive-foreground)/10 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}
