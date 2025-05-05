"use client";

import { Card } from "@/components/ui/card";
import { Server } from "lucide-react";

interface MCPServersTabProps {
    organizationId: string;
}

export function MCPServersTab({ organizationId }: MCPServersTabProps) {
    return (
        <Card className="p-6 border border-dashed border-(--border)">
            <div className="flex flex-col items-center justify-center p-4 text-center">
                <Server className="h-12 w-12 text-(--muted-foreground) mb-3" />
                <h3 className="text-lg font-medium mb-1">No MCP Servers Connected</h3>
                <p className="text-sm text-(--muted-foreground)">
                    Connect to MCP servers to enable advanced agent capabilities.
                </p>
            </div>
        </Card>
    );
}
