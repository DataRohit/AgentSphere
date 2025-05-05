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
import { Loader2, Users } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

interface OrganizationMember {
    email: string;
    first_name: string;
    last_name: string;
    username: string;
    avatar_url?: string;
    is_active?: boolean;
    is_staff?: boolean;
    is_superuser?: boolean;
    date_joined?: string;
    last_login?: string;
}

interface TransferOwnershipDialogProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    organizationId: string;
    organizationName: string;
    member: OrganizationMember;
    onTransferSuccess?: () => void;
}

export function TransferOwnershipDialog({
    open,
    onOpenChange,
    organizationId,
    organizationName,
    member,
    onTransferSuccess,
}: TransferOwnershipDialogProps) {
    const [isTransferring, setIsTransferring] = useState(false);

    const handleTransfer = async () => {
        setIsTransferring(true);

        try {
            const accessToken = Cookies.get("access_token");
            if (!accessToken) {
                throw new Error("Authentication token not found");
            }

            const payload = member.email ? { email: member.email } : { username: member.username };

            const response = await fetch(
                `http://localhost:8080/api/v1/organizations/${organizationId}/transfer/`,
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
                if (data.errors && data.errors.non_field_errors) {
                    throw new Error(data.errors.non_field_errors[0]);
                } else if (data.errors && data.errors.username) {
                    throw new Error(data.errors.username[0]);
                } else if (data.errors && data.errors.email) {
                    throw new Error(data.errors.email[0]);
                } else if (data.errors && data.errors.user_id) {
                    throw new Error(data.errors.user_id[0]);
                }
                throw new Error(data.error || "Failed to transfer ownership");
            }

            toast.success("Ownership transferred successfully", {
                style: {
                    backgroundColor: "oklch(0.45 0.18 142.71)",
                    color: "white",
                    border: "none",
                },
            });

            if (onTransferSuccess) {
                onTransferSuccess();
            }

            setTimeout(() => {
                window.location.reload();
            }, 100);
        } catch (error) {
            toast.error(error instanceof Error ? error.message : "Failed to transfer ownership", {
                style: {
                    backgroundColor: "var(--destructive)",
                    color: "white",
                    border: "none",
                },
            });
        } finally {
            setIsTransferring(false);
            onOpenChange(false);
        }
    };

    const fullName =
        member.first_name && member.last_name
            ? `${member.first_name} ${member.last_name}`
            : member.username;

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[425px] bg-(--background) border-(--border) [&_[data-slot=dialog-close]]:hover:opacity-100 [&_[data-slot=dialog-close]]:cursor-pointer [&_[data-slot=dialog-close]]:transition-opacity [&_[data-slot=dialog-close]]:duration-200">
                <DialogHeader>
                    <DialogTitle className="flex items-center text-(--foreground) pb-2">
                        <Users className="mr-2 h-5 w-5 text-(--primary)" />
                        Transfer Ownership
                    </DialogTitle>
                    <DialogDescription>
                        Are you sure you want to transfer ownership of this organization? You will
                        no longer be the owner and will become a regular member.
                    </DialogDescription>
                </DialogHeader>

                <div className="py-4">
                    <p className="text-sm text-center">
                        You are about to transfer ownership of{" "}
                        <span className="font-medium">{organizationName}</span> to{" "}
                        <span className="font-medium text-(--primary)">{fullName}</span>
                    </p>
                </div>

                <DialogFooter className="flex flex-col sm:flex-row sm:justify-between w-full gap-2">
                    <Button
                        type="button"
                        variant="outline"
                        onClick={() => onOpenChange(false)}
                        disabled={isTransferring}
                        className="font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--border) bg-(--background) text-(--foreground) hover:bg-(--muted) h-10 cursor-pointer w-full sm:flex-1"
                    >
                        <span className="relative z-10">Cancel</span>
                        <span className="absolute inset-0 bg-(--muted)/50 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                    </Button>
                    <Button
                        type="button"
                        variant="default"
                        onClick={handleTransfer}
                        disabled={isTransferring}
                        className="font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--primary) bg-(--primary) text-(--primary-foreground) dark:bg-(--primary) dark:text-(--primary-foreground) dark:border-(--primary) h-10 cursor-pointer w-full sm:flex-1"
                    >
                        <span className="relative z-10">
                            {isTransferring ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin inline" />
                                    Transferring...
                                </>
                            ) : (
                                "Initiate Transfer"
                            )}
                        </span>
                        <span className="absolute inset-0 bg-(--primary-foreground)/10 dark:bg-(--primary-foreground)/20 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}
