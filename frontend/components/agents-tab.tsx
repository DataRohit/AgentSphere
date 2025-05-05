"use client";

import { Card } from "@/components/ui/card";
import { Bot } from "lucide-react";

interface AgentsTabProps {
    organizationId: string;
}

export function AgentsTab({ organizationId }: AgentsTabProps) {
    return (
        <Card className="p-6 border border-dashed border-(--border)">
            <div className="flex flex-col items-center justify-center p-4 text-center">
                <Bot className="h-12 w-12 text-(--muted-foreground) mb-3" />
                <h3 className="text-lg font-medium mb-1">No Agents Created</h3>
                <p className="text-sm text-(--muted-foreground)">
                    Create AI agents to automate tasks and workflows.
                </p>
            </div>
        </Card>
    );
}
