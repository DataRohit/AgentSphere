"use client";

import Cookies from "js-cookie";
import { Check, Loader2 } from "lucide-react";
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

interface AcceptTransferDialogProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    transferId: string;
    organizationName: string;
    onAcceptSuccess?: () => void;
}

export function AcceptTransferDialog({
    open,
    onOpenChange,
    transferId,
    organizationName,
    onAcceptSuccess,
}: AcceptTransferDialogProps) {
    const [isAccepting, setIsAccepting] = useState(false);

    const handleAccept = async () => {
        setIsAccepting(true);

        try {
            const accessToken = Cookies.get("access_token");
            if (!accessToken) {
                throw new Error("Authentication token not found");
            }

            const response = await fetch(
                `${process.env.NEXT_PUBLIC_API_URL}/organizations/transfer/${transferId}/accept/`,
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
                throw new Error(data.error || "Failed to accept transfer request");
            }

            toast.success("Transfer request accepted successfully", {
                style: {
                    backgroundColor: "oklch(0.45 0.18 142.71)",
                    color: "white",
                    border: "none",
                },
            });

            if (onAcceptSuccess) {
                onAcceptSuccess();
            }

            setTimeout(() => {
                window.location.reload();
            }, 100);
        } catch (error) {
            toast.error(
                error instanceof Error ? error.message : "Failed to accept transfer request",
                {
                    style: {
                        backgroundColor: "var(--destructive)",
                        color: "white",
                        border: "none",
                    },
                }
            );
        } finally {
            setIsAccepting(false);
            onOpenChange(false);
        }
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[425px] bg-(--background) border-(--border) [&_[data-slot=dialog-close]]:hover:opacity-100 [&_[data-slot=dialog-close]]:cursor-pointer [&_[data-slot=dialog-close]]:transition-opacity [&_[data-slot=dialog-close]]:duration-200">
                <DialogHeader>
                    <DialogTitle className="flex items-center text-(--foreground) pb-2">
                        <Check className="mr-2 h-5 w-5 text-green-500" />
                        Accept Ownership Transfer
                    </DialogTitle>
                    <DialogDescription>
                        Are you sure you want to accept ownership of this organization? You will
                        become the new owner.
                    </DialogDescription>
                </DialogHeader>

                <div className="py-4">
                    <p className="text-sm text-center font-medium">
                        You are about to become the owner of{" "}
                        <span className="text-green-500">{organizationName}</span>
                    </p>
                </div>

                <DialogFooter className="flex flex-col sm:flex-row sm:justify-between w-full gap-2">
                    <Button
                        type="button"
                        variant="outline"
                        onClick={() => onOpenChange(false)}
                        disabled={isAccepting}
                        className="font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--border) bg-(--background) text-(--foreground) hover:bg-(--muted) h-10 cursor-pointer w-full sm:flex-1"
                    >
                        <span className="relative z-10">Cancel</span>
                        <span className="absolute inset-0 bg-(--muted)/50 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                    </Button>
                    <Button
                        type="button"
                        variant="default"
                        onClick={handleAccept}
                        disabled={isAccepting}
                        className="font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-green-500 bg-green-500 text-white dark:bg-green-500 dark:text-white dark:border-green-500 h-10 cursor-pointer w-full sm:flex-1"
                    >
                        <span className="relative z-10">
                            {isAccepting ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin inline" />
                                    Accepting...
                                </>
                            ) : (
                                "Accept"
                            )}
                        </span>
                        <span className="absolute inset-0 bg-white/10 dark:bg-white/20 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}
