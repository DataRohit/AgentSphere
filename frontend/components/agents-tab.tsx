"use client";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Bot, Loader2 } from "lucide-react";
import { useEffect, useState } from "react";

interface AgentsTabProps {
    organizationId: string;
    filterByUsername?: string;
    readOnly?: boolean;
}

export function AgentsTab({
    organizationId: _organizationId,
    filterByUsername,
    readOnly = false,
}: AgentsTabProps) {
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const timer = setTimeout(() => {
            setIsLoading(false);
        }, 1000);

        return () => clearTimeout(timer);
    }, []);

    if (isLoading) {
        return (
            <div className="flex justify-center items-center p-8">
                <Loader2 className="h-8 w-8 animate-spin text-(--muted-foreground)" />
            </div>
        );
    }

    return (
        <Card className="p-6 border border-dashed border-(--border)">
            <div className="flex flex-col items-center justify-center p-4 text-center">
                <Bot className="h-12 w-12 text-(--muted-foreground) mb-3" />
                <h3 className="text-lg font-medium mb-1">Agents Coming Soon</h3>
                <p className="text-sm text-(--muted-foreground) mb-4">
                    {filterByUsername
                        ? "This user has not created any agents yet."
                        : "The Agents feature is currently under development and will be available soon."}
                </p>
                {!readOnly && (
                    <Button
                        variant="outline"
                        className="font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--border) bg-(--background) text-(--foreground) hover:bg-(--muted) h-10 cursor-pointer"
                        disabled
                    >
                        <span className="relative z-10">Coming Soon</span>
                    </Button>
                )}
            </div>
        </Card>
    );
}
