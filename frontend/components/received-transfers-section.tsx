"use client";

import {
    ReceivedTransferRequest,
    ReceivedTransferRequestCard,
} from "@/components/received-transfer-request-card";
import { Card } from "@/components/ui/card";
import { motion } from "framer-motion";
import Cookies from "js-cookie";
import { AlertCircle } from "lucide-react";
import { useEffect, useState } from "react";

interface ReceivedTransfersSectionProps {
    userId: string;
}

export function ReceivedTransfersSection({ userId }: ReceivedTransfersSectionProps) {
    const [transfers, setTransfers] = useState<ReceivedTransferRequest[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchTransfers = async () => {
        setIsLoading(true);
        setError(null);

        try {
            const accessToken = Cookies.get("access_token");
            if (!accessToken) {
                throw new Error("Authentication token not found");
            }

            const response = await fetch(
                `${process.env.NEXT_PUBLIC_API_URL}/organizations/transfers/received/`,
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
                throw new Error(data.error || "Failed to fetch received transfer requests");
            }

            setTransfers(data.transfers || []);
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : "An error occurred";
            setError(errorMessage);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchTransfers();
    }, [userId]);

    if (isLoading) {
        return (
            <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {[...Array(3)].map((_, index) => (
                        <Card
                            key={index}
                            className="h-40 border border-(--border) shadow-sm animate-pulse"
                        >
                            <div className="flex items-center p-4 space-x-4">
                                <div className="h-10 w-10 rounded-full bg-(--muted)" />
                                <div className="space-y-2">
                                    <div className="h-4 w-24 bg-(--muted) rounded" />
                                    <div className="h-3 w-32 bg-(--muted) rounded" />
                                </div>
                            </div>
                        </Card>
                    ))}
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="space-y-4">
                <Card className="border border-(--border) shadow-sm p-6">
                    <div className="flex flex-col items-center justify-center text-center">
                        <div className="h-10 w-10 rounded-full bg-(--destructive)/10 flex items-center justify-center mb-3">
                            <AlertCircle className="h-5 w-5 text-(--destructive)" />
                        </div>
                        <h3 className="text-sm font-medium mb-1">Failed to load transfers</h3>
                        <p className="text-xs text-(--muted-foreground) mb-3">{error}</p>
                    </div>
                </Card>
            </div>
        );
    }

    if (transfers.length === 0) {
        return (
            <div className="space-y-4">
                <Card className="border border-(--border) shadow-sm p-6">
                    <div className="flex flex-col items-center justify-center text-center">
                        <p className="text-sm text-(--muted-foreground)">
                            No pending ownership transfers found.
                        </p>
                    </div>
                </Card>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {transfers.map((transfer, index) => (
                    <motion.div
                        key={transfer.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.3, delay: index * 0.1 }}
                        whileHover={{ y: -5, transition: { duration: 0.2 } }}
                        className="h-full"
                    >
                        <ReceivedTransferRequestCard transfer={transfer} />
                    </motion.div>
                ))}
            </div>
        </div>
    );
}
