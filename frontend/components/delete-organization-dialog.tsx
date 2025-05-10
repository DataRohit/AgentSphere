"use client";

import Cookies from "js-cookie";
import { Loader2, Trash2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
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

interface DeleteOrganizationDialogProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    organizationId: string;
    organizationName: string;
}

export function DeleteOrganizationDialog({
    open,
    onOpenChange,
    organizationId,
    organizationName,
}: DeleteOrganizationDialogProps) {
    const router = useRouter();
    const [confirmationText, setConfirmationText] = useState("");
    const [isDeleting, setIsDeleting] = useState(false);

    const handleDelete = async () => {
        if (confirmationText !== organizationName) {
            toast.error("Organization name doesn't match", {
                style: {
                    backgroundColor: "var(--destructive)",
                    color: "white",
                    border: "none",
                },
            });
            return;
        }

        setIsDeleting(true);

        try {
            const accessToken = Cookies.get("access_token");
            if (!accessToken) {
                throw new Error("Authentication token not found");
            }

            const response = await fetch(
                `${process.env.NEXT_PUBLIC_API_URL}/organizations/${organizationId}/`,
                {
                    method: "DELETE",
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${accessToken}`,
                    },
                }
            );

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || "Failed to delete organization");
            }

            toast.success("Organization deleted successfully", {
                style: {
                    backgroundColor: "oklch(0.45 0.18 142.71)",
                    color: "white",
                    border: "none",
                },
            });

            router.push("/dashboard");
        } catch (error) {
            toast.error(error instanceof Error ? error.message : "Failed to delete organization", {
                style: {
                    backgroundColor: "var(--destructive)",
                    color: "white",
                    border: "none",
                },
            });
        } finally {
            setIsDeleting(false);
            onOpenChange(false);
        }
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[425px] bg-(--background) border-(--border) [&_[data-slot=dialog-close]]:hover:opacity-100 [&_[data-slot=dialog-close]]:cursor-pointer [&_[data-slot=dialog-close]]:transition-opacity [&_[data-slot=dialog-close]]:duration-200">
                <DialogHeader>
                    <DialogTitle className="flex items-center text-(--foreground) pb-2">
                        <Trash2 className="mr-2 h-5 w-5 text-(--destructive)" />
                        Delete Organization
                    </DialogTitle>
                    <DialogDescription>
                        This action cannot be undone. This will permanently delete the organization
                        and remove all associated data.
                    </DialogDescription>
                </DialogHeader>

                <div className="space-y-4 py-2">
                    <div className="space-y-2">
                        <Label htmlFor="confirmation" className="text-(--foreground) mb-4">
                            To confirm, type the organization name
                        </Label>
                        <div className="flex items-center justify-center h-10 px-3 py-2 rounded-md border border-(--border) bg-(--background) text-(--foreground) mb-4">
                            <p className="text-sm font-medium text-center">{organizationName}</p>
                        </div>
                        <Input
                            id="confirmation"
                            value={confirmationText}
                            onChange={(e) => setConfirmationText(e.target.value)}
                            placeholder="Enter organization name"
                            className="bg-(--secondary) h-10 border-(--border) focus:border-(--destructive) focus:ring-1 focus:ring-(--destructive) text-center"
                        />
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
                        disabled={isDeleting || confirmationText !== organizationName}
                        className="font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--destructive) bg-(--destructive) text-(--destructive-foreground) dark:bg-(--destructive) dark:text-(--destructive-foreground) dark:border-(--destructive) h-10 cursor-pointer w-full sm:flex-1"
                    >
                        <span className="relative z-10">
                            {isDeleting ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin inline" />
                                    Deleting...
                                </>
                            ) : (
                                "Delete"
                            )}
                        </span>
                        <span className="absolute inset-0 bg-(--destructive-foreground)/10 dark:bg-(--destructive-foreground)/20 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}
