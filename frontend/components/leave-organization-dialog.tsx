"use client";

import Cookies from "js-cookie";
import { Loader2, LogOut } from "lucide-react";
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

interface LeaveOrganizationDialogProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    organizationId: string;
    organizationName: string;
    onLeaveSuccess?: () => void;
}

export function LeaveOrganizationDialog({
    open,
    onOpenChange,
    organizationId,
    organizationName,
    onLeaveSuccess,
}: LeaveOrganizationDialogProps) {
    const router = useRouter();
    const [isLeaving, setIsLeaving] = useState(false);

    const handleLeave = async () => {
        setIsLeaving(true);

        try {
            const accessToken = Cookies.get("access_token");
            if (!accessToken) {
                throw new Error("Authentication token not found");
            }

            const response = await fetch(
                `http://localhost:8080/api/v1/organizations/${organizationId}/leave/`,
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
                if (data.errors && data.errors.non_field_errors) {
                    throw new Error(data.errors.non_field_errors[0]);
                }
                throw new Error(data.error || "Failed to leave organization");
            }

            toast.success("You have successfully left the organization", {
                style: {
                    backgroundColor: "oklch(0.45 0.18 142.71)",
                    color: "white",
                    border: "none",
                },
            });

            if (onLeaveSuccess) {
                onLeaveSuccess();
            }

            router.push("/dashboard");

            setTimeout(() => {
                window.location.reload();
            }, 100);
        } catch (error) {
            toast.error(error instanceof Error ? error.message : "Failed to leave organization", {
                style: {
                    backgroundColor: "var(--destructive)",
                    color: "white",
                    border: "none",
                },
            });
        } finally {
            setIsLeaving(false);
            onOpenChange(false);
        }
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[425px] bg-(--background) border-(--border) [&_[data-slot=dialog-close]]:hover:opacity-100 [&_[data-slot=dialog-close]]:cursor-pointer [&_[data-slot=dialog-close]]:transition-opacity [&_[data-slot=dialog-close]]:duration-200">
                <DialogHeader>
                    <DialogTitle className="flex items-center text-(--foreground) pb-2">
                        <LogOut className="mr-2 h-5 w-5 text-(--destructive)" />
                        Leave Organization
                    </DialogTitle>
                    <DialogDescription>
                        Are you sure you want to leave this organization? You will lose access to
                        all organization resources.
                    </DialogDescription>
                </DialogHeader>

                <div className="py-4">
                    <p className="text-sm text-center font-medium">
                        You are about to leave{" "}
                        <span className="text-(--destructive)">{organizationName}</span>
                    </p>
                </div>

                <DialogFooter className="flex flex-col sm:flex-row sm:justify-between w-full gap-2">
                    <Button
                        type="button"
                        variant="outline"
                        onClick={() => onOpenChange(false)}
                        disabled={isLeaving}
                        className="font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--border) bg-(--background) text-(--foreground) hover:bg-(--muted) h-10 cursor-pointer w-full sm:flex-1"
                    >
                        <span className="relative z-10">Cancel</span>
                        <span className="absolute inset-0 bg-(--muted)/50 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                    </Button>
                    <Button
                        type="button"
                        variant="destructive"
                        onClick={handleLeave}
                        disabled={isLeaving}
                        className="font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--destructive) bg-(--destructive) text-(--destructive-foreground) dark:bg-(--destructive) dark:text-(--destructive-foreground) dark:border-(--destructive) h-10 cursor-pointer w-full sm:flex-1"
                    >
                        <span className="relative z-10">
                            {isLeaving ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin inline" />
                                    Leaving...
                                </>
                            ) : (
                                "Leave Organization"
                            )}
                        </span>
                        <span className="absolute inset-0 bg-(--destructive-foreground)/10 dark:bg-(--destructive-foreground)/20 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}
