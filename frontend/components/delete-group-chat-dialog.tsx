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
import { Loader2, Trash2 } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

interface GroupChat {
    id: string;
    title: string;
}

interface DeleteGroupChatDialogProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    chat: GroupChat;
    onSuccess: () => void;
}

export function DeleteGroupChatDialog({
    open,
    onOpenChange,
    chat,
    onSuccess,
}: DeleteGroupChatDialogProps) {
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleDelete = async () => {
        setIsSubmitting(true);
        try {
            const accessToken = Cookies.get("access_token");
            if (!accessToken) {
                throw new Error("Authentication token not found");
            }

            const response = await fetch(`http://localhost:8080/api/v1/chats/group/${chat.id}/delete/`, {
                method: "DELETE",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${accessToken}`,
                },
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || "Failed to delete group chat");
            }

            toast.success("Group chat deleted successfully", {
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
                err instanceof Error ? err.message : "An error occurred while deleting the group chat";
            toast.error(errorMessage, {
                className: "bg-(--destructive) text-white border-none",
            });
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[425px] bg-(--background) border-(--border) [&_[data-slot=dialog-close]]:hover:opacity-100 [&_[data-slot=dialog-close]]:cursor-pointer [&_[data-slot=dialog-close]]:transition-opacity [&_[data-slot=dialog-close]]:duration-200">
                <DialogHeader>
                    <DialogTitle className="flex items-center pb-2">
                        <Trash2 className="mr-2 h-5 w-5 text-(--destructive)" />
                        Delete Group Chat
                    </DialogTitle>
                    <DialogDescription>
                        Are you sure you want to delete this group chat? This action cannot be undone.
                    </DialogDescription>
                </DialogHeader>
                <div className="py-4">
                    <p className="text-sm font-medium mb-2">You are about to delete the group chat:</p>
                    <div className="p-3 bg-(--secondary) rounded-md">
                        <p className="font-medium">{chat.title}</p>
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
                        type="button"
                        variant="destructive"
                        onClick={handleDelete}
                        disabled={isSubmitting}
                        className="font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--destructive) bg-(--destructive) text-white dark:bg-(--destructive) dark:text-white dark:border-(--destructive) h-10 cursor-pointer w-full sm:flex-1"
                    >
                        <span className="relative z-10">
                            {isSubmitting ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin inline" />
                                    Deleting...
                                </>
                            ) : (
                                "Delete Group Chat"
                            )}
                        </span>
                        <span className="absolute inset-0 bg-white/10 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}
