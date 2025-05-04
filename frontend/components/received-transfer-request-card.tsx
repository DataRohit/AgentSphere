"use client";

import { AcceptTransferDialog } from "@/components/accept-transfer-dialog";
import { RejectTransferDialog } from "@/components/reject-transfer-dialog";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatDistanceToNow, isPast } from "date-fns";
import { Check, X } from "lucide-react";
import { useState } from "react";

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

export interface ReceivedTransferRequest {
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

interface ReceivedTransferRequestCardProps {
    transfer: ReceivedTransferRequest;
}

export function ReceivedTransferRequestCard({ transfer }: ReceivedTransferRequestCardProps) {
    const [isAcceptDialogOpen, setIsAcceptDialogOpen] = useState(false);
    const [isRejectDialogOpen, setIsRejectDialogOpen] = useState(false);

    const getInitials = (name: string) => {
        return name
            .split(" ")
            .map((part) => part[0])
            .join("")
            .toUpperCase()
            .substring(0, 2);
    };

    const currentOwnerFullName =
        transfer.current_owner.first_name && transfer.current_owner.last_name
            ? `${transfer.current_owner.first_name} ${transfer.current_owner.last_name}`
            : transfer.current_owner.username;

    const expirationDate = new Date(transfer.expiration_time);
    const isExpired = isPast(expirationDate);
    const transferStatus = isExpired ? "Expired" : "Active";
    const statusColor = isExpired ? "text-red-500" : "text-green-500";

    return (
        <>
            <Card className="h-full border border-(--border) shadow-sm hover:shadow-md transition-all duration-300 overflow-hidden flex flex-col bg-(--secondary) dark:bg-(--secondary) relative group p-0">
                <CardHeader className="pb-1 pt-4 px-4">
                    <div className="flex items-start space-x-3">
                        <Avatar className="h-10 w-10 border border-(--border) my-auto">
                            {transfer.current_owner.avatar_url ? (
                                <AvatarImage
                                    src={transfer.current_owner.avatar_url}
                                    alt={currentOwnerFullName}
                                />
                            ) : null}
                            <AvatarFallback className="bg-(--primary)/10 text-(--primary)">
                                {getInitials(currentOwnerFullName)}
                            </AvatarFallback>
                        </Avatar>
                        <div className="flex-1">
                            <div className="flex items-center justify-between">
                                <CardTitle className="text-lg font-semibold">
                                    {transfer.organization_name}
                                </CardTitle>
                                <span className={`text-xs font-medium ${statusColor}`}>
                                    {transferStatus}
                                </span>
                            </div>
                            <p className="text-sm text-(--muted-foreground) mt-0.5">
                                From: {currentOwnerFullName} (@{transfer.current_owner.username})
                            </p>
                        </div>
                    </div>
                </CardHeader>
                <CardContent className="px-4 py-2 mt-auto text-xs text-(--muted-foreground) space-y-1.5">
                    <div className="flex justify-between">
                        <span className="text-[#64748b]">Email:</span>
                        <span className="text-right text-[#64748b]">
                            {transfer.current_owner.email}
                        </span>
                    </div>
                    <div className="flex justify-between">
                        <span className="text-[#64748b]">Expires:</span>
                        <span className="text-right text-[#64748b]">
                            {formatDistanceToNow(expirationDate, { addSuffix: true })}
                        </span>
                    </div>
                    <div className="flex justify-between">
                        <span className="text-[#64748b]">Created:</span>
                        <span className="text-right text-[#64748b]">
                            {formatDistanceToNow(new Date(transfer.created_at), {
                                addSuffix: true,
                            })}
                        </span>
                    </div>
                </CardContent>
                <div className="flex w-full mt-auto border-t border-[#1e293b]">
                    <button
                        className="flex-1 h-12 bg-(--secondary) hover:bg-[#1e293b] text-green-500 text-sm flex items-center justify-center cursor-pointer transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                        onClick={() => setIsAcceptDialogOpen(true)}
                        disabled={isExpired}
                    >
                        <Check className="h-4 w-4 mr-2" />
                        <span>Accept</span>
                    </button>
                    <div className="w-px h-12 bg-[#1e293b]"></div>
                    <button
                        className="flex-1 h-12 bg-(--secondary) hover:bg-[#1e293b] text-[#ef4444] text-sm flex items-center justify-center cursor-pointer transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                        onClick={() => setIsRejectDialogOpen(true)}
                        disabled={isExpired}
                    >
                        <X className="h-4 w-4 mr-2" />
                        <span>Reject</span>
                    </button>
                </div>
            </Card>

            <AcceptTransferDialog
                open={isAcceptDialogOpen}
                onOpenChange={setIsAcceptDialogOpen}
                transferId={transfer.id}
                organizationName={transfer.organization_name}
            />

            <RejectTransferDialog
                open={isRejectDialogOpen}
                onOpenChange={setIsRejectDialogOpen}
                transferId={transfer.id}
                organizationName={transfer.organization_name}
            />
        </>
    );
}
