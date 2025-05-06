"use client";

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatDistanceToNow, isPast } from "date-fns";
import Cookies from "js-cookie";
import { Loader2, X } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

interface User {
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

export interface TransferRequest {
    id: string;
    organization_id: string;
    organization_name: string;
    current_owner: User;
    new_owner: User;
    expiration_time: string;
    is_active: boolean;
    created_at: string;
    updated_at: string;
}

interface TransferRequestCardProps {
    transfer: TransferRequest;
    onCancelSuccess: () => void;
}

export function TransferRequestCard({ transfer, onCancelSuccess }: TransferRequestCardProps) {
    const [isCancelling, setIsCancelling] = useState(false);

    const getInitials = (name: string) => {
        return name
            .split(" ")
            .map((part) => part[0])
            .join("")
            .toUpperCase()
            .substring(0, 2);
    };

    const newOwnerFullName =
        transfer.new_owner.first_name && transfer.new_owner.last_name
            ? `${transfer.new_owner.first_name} ${transfer.new_owner.last_name}`
            : transfer.new_owner.username;

    const expirationDate = new Date(transfer.expiration_time);
    const isExpired = isPast(expirationDate);
    const transferStatus = isExpired ? "Expired" : "Active";
    const statusColor = isExpired ? "text-red-500" : "text-green-500";

    const handleCancelTransfer = async () => {
        setIsCancelling(true);

        try {
            const accessToken = Cookies.get("access_token");
            if (!accessToken) {
                throw new Error("Authentication token not found");
            }

            const response = await fetch(
                `http://localhost:8080/api/v1/organizations/${transfer.organization_id}/transfer/cancel/`,
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
                throw new Error(data.error || "Failed to cancel transfer request");
            }

            toast.success("Transfer request cancelled successfully", {
                style: {
                    backgroundColor: "oklch(0.45 0.18 142.71)",
                    color: "white",
                    border: "none",
                },
            });

            onCancelSuccess();
        } catch (error) {
            toast.error(
                error instanceof Error ? error.message : "Failed to cancel transfer request",
                {
                    style: {
                        backgroundColor: "var(--destructive)",
                        color: "white",
                        border: "none",
                    },
                }
            );
        } finally {
            setIsCancelling(false);
        }
    };

    return (
        <Card className="h-full border border-(--border) shadow-sm hover:shadow-md transition-all duration-300 overflow-hidden flex flex-col bg-(--secondary) dark:bg-(--secondary) relative group p-0">
            <CardHeader className="pb-1 pt-4 px-4">
                <div className="flex items-start space-x-3">
                    <Avatar className="h-10 w-10 border border-(--border) my-auto">
                        {transfer.new_owner.avatar_url ? (
                            <AvatarImage
                                src={transfer.new_owner.avatar_url}
                                alt={newOwnerFullName}
                            />
                        ) : null}
                        <AvatarFallback className="bg-(--primary)/10 text-(--primary)">
                            {getInitials(newOwnerFullName)}
                        </AvatarFallback>
                    </Avatar>
                    <div className="flex-1">
                        <div className="flex items-center justify-between">
                            <CardTitle className="text-lg font-semibold">
                                {newOwnerFullName}
                            </CardTitle>
                            <span className={`text-xs font-medium ${statusColor}`}>
                                {transferStatus}
                            </span>
                        </div>
                        <p className="text-sm text-(--muted-foreground) mt-0.5">
                            @{transfer.new_owner.username}
                        </p>
                    </div>
                </div>
            </CardHeader>
            <CardContent className="px-4 py-2 mt-auto text-xs text-(--muted-foreground) space-y-1.5">
                <div className="flex justify-between">
                    <span className="text-[#64748b]">Expires:</span>
                    <span className="text-right text-[#64748b]">
                        {formatDistanceToNow(expirationDate, { addSuffix: true })}
                    </span>
                </div>
                <div className="flex justify-between">
                    <span className="text-[#64748b]">Created:</span>
                    <span className="text-right text-[#64748b]">
                        {formatDistanceToNow(new Date(transfer.created_at), { addSuffix: true })}
                    </span>
                </div>
            </CardContent>
            <div className="flex w-full mt-auto border-t border-[#1e293b]">
                <button
                    className="flex-1 h-12 bg-(--secondary) hover:bg-[#1e293b] text-[#ef4444] text-sm flex items-center justify-center cursor-pointer transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                    onClick={handleCancelTransfer}
                    disabled={isCancelling || isExpired}
                >
                    {isCancelling ? (
                        <>
                            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                            <span>Cancelling...</span>
                        </>
                    ) : (
                        <>
                            <X className="h-4 w-4 mr-2" />
                            <span>Cancel Transfer</span>
                        </>
                    )}
                </button>
            </div>
        </Card>
    );
}
