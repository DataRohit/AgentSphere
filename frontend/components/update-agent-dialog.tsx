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
import { Form, FormControl, FormField, FormItem, FormLabel } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { zodResolver } from "@hookform/resolvers/zod";
import Cookies from "js-cookie";
import { Check, Loader2, Pencil, Server } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";

interface Tool {
    id: string;
    name: string;
    description: string;
}

interface MCPServer {
    id: string;
    name: string;
    url: string;
    tools: Tool[];
}

interface LLM {
    id: string;
    base_url: string;
    model: string;
}

interface Agent {
    id: string;
    name: string;
    description: string;
    system_prompt: string;
    avatar_url: string;
    organization: {
        id: string;
        name: string;
    };
    user: {
        id: string;
        username: string;
        email: string;
    };
    llm: LLM;
    mcp_servers: MCPServer[];
    created_at: string;
    updated_at: string;
}

interface ApiErrorResponse {
    status_code: number;
    errors?: {
        name?: string[];
        description?: string[];
        system_prompt?: string[];
        llm_id?: string[];
        mcp_server_ids?: string[];
        non_field_errors?: string[];
        [key: string]: string[] | undefined;
    };
    error?: string;
}

const updateAgentSchema = z.object({
    name: z.string().min(1, "Name is required"),
    description: z.string().optional(),
    system_prompt: z.string().min(1, "System prompt is required"),
    llm_id: z.string().min(1, "LLM is required"),
    mcp_server_ids: z.array(z.string()).optional(),
});

type UpdateAgentValues = z.infer<typeof updateAgentSchema>;

interface UpdateAgentDialogProps {
    agent: Agent;
    open: boolean;
    onOpenChange: (open: boolean) => void;
    onUpdateSuccess: () => void;
}

export function UpdateAgentDialog({
    agent,
    open,
    onOpenChange,
    onUpdateSuccess,
}: UpdateAgentDialogProps) {
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [llms, setLLMs] = useState<LLM[]>([]);
    const [mcpServers, setMCPServers] = useState<MCPServer[]>([]);
    const [isLoadingLLMs, setIsLoadingLLMs] = useState(false);
    const [isLoadingMCPServers, setIsLoadingMCPServers] = useState(false);
    const [selectedMCPServers, setSelectedMCPServers] = useState<string[]>([]);

    const form = useForm<UpdateAgentValues>({
        resolver: zodResolver(updateAgentSchema),
        defaultValues: {
            name: agent.name,
            description: agent.description || "",
            system_prompt: agent.system_prompt,
            llm_id: agent.llm.id,
            mcp_server_ids: agent.mcp_servers.map((server) => server.id),
        },
    });

    const fetchLLMs = useCallback(async () => {
        setIsLoadingLLMs(true);
        try {
            const accessToken = Cookies.get("access_token");
            if (!accessToken) {
                throw new Error("Authentication token not found");
            }

            const response = await fetch(
                `${process.env.NEXT_PUBLIC_API_URL}/llms/list/me?organization_id=${agent.organization.id}`,
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
                throw new Error(data.error || "Failed to fetch LLMs");
            }

            setLLMs(data.llms || []);
        } catch (err) {
            const errorMessage =
                err instanceof Error ? err.message : "An error occurred while fetching LLMs";
            toast.error(errorMessage, {
                style: {
                    backgroundColor: "var(--destructive)",
                    color: "white",
                    border: "none",
                },
            });
        } finally {
            setIsLoadingLLMs(false);
        }
    }, [agent.organization.id]);

    const fetchMCPServers = useCallback(async () => {
        setIsLoadingMCPServers(true);
        try {
            const accessToken = Cookies.get("access_token");
            if (!accessToken) {
                throw new Error("Authentication token not found");
            }

            const response = await fetch(
                `${process.env.NEXT_PUBLIC_API_URL}/tools/mcpserver/list/me/?organization_id=${agent.organization.id}`,
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
                throw new Error(data.error || "Failed to fetch MCP servers");
            }

            setMCPServers(data.mcpservers || []);
        } catch (err) {
            const errorMessage =
                err instanceof Error ? err.message : "An error occurred while fetching MCP servers";
            toast.error(errorMessage, {
                style: {
                    backgroundColor: "var(--destructive)",
                    color: "white",
                    border: "none",
                },
            });
        } finally {
            setIsLoadingMCPServers(false);
        }
    }, [agent.organization.id]);

    useEffect(() => {
        if (open) {
            fetchLLMs();
            fetchMCPServers();
            setSelectedMCPServers(agent.mcp_servers.map((server) => server.id));
            form.reset({
                name: agent.name,
                description: agent.description || "",
                system_prompt: agent.system_prompt,
                llm_id: agent.llm.id,
                mcp_server_ids: agent.mcp_servers.map((server) => server.id),
            });
        }
    }, [open, agent, form, fetchLLMs, fetchMCPServers]);

    const toggleMCPServer = (serverId: string) => {
        setSelectedMCPServers((prev) => {
            if (prev.includes(serverId)) {
                return prev.filter((id) => id !== serverId);
            } else {
                return [...prev, serverId];
            }
        });
    };

    useEffect(() => {
        form.setValue("mcp_server_ids", selectedMCPServers);
    }, [selectedMCPServers, form]);

    const onSubmit = async (values: UpdateAgentValues) => {
        setIsSubmitting(true);
        try {
            const accessToken = Cookies.get("access_token");
            if (!accessToken) {
                toast.error("Authentication token not found", {
                    style: {
                        backgroundColor: "var(--destructive)",
                        color: "white",
                        border: "none",
                    },
                });
                return;
            }

            const payload = {
                name: values.name,
                description: values.description || "",
                system_prompt: values.system_prompt,
                llm_id: values.llm_id,
                mcp_server_ids: values.mcp_server_ids || [],
            };

            const response = await fetch(
                `${process.env.NEXT_PUBLIC_API_URL}/agents/${agent.id}/update/`,
                {
                    method: "PATCH",
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${accessToken}`,
                    },
                    body: JSON.stringify(payload),
                }
            );

            const data = await response.json();

            if (!response.ok) {
                const errorData = data as ApiErrorResponse;
                if (errorData.errors) {
                    Object.entries(errorData.errors).forEach(([field, errors]) => {
                        if (errors && errors.length > 0) {
                            if (field === "non_field_errors") {
                                toast.error(errors[0], {
                                    style: {
                                        backgroundColor: "var(--destructive)",
                                        color: "white",
                                        border: "none",
                                    },
                                });
                            } else {
                                form.setError(field as keyof UpdateAgentValues, {
                                    type: "manual",
                                    message: errors[0],
                                });
                            }
                        }
                    });
                } else if (errorData.error) {
                    toast.error(errorData.error, {
                        style: {
                            backgroundColor: "var(--destructive)",
                            color: "white",
                            border: "none",
                        },
                    });
                } else {
                    toast.error("Failed to update agent", {
                        style: {
                            backgroundColor: "var(--destructive)",
                            color: "white",
                            border: "none",
                        },
                    });
                }
                return;
            }

            toast.success("Agent updated successfully", {
                style: {
                    backgroundColor: "oklch(0.45 0.18 142.71)",
                    color: "white",
                    border: "none",
                },
            });

            onOpenChange(false);
            onUpdateSuccess();
        } catch (err) {
            const errorMessage =
                err instanceof Error ? err.message : "An error occurred while updating the agent";
            toast.error(errorMessage, {
                style: {
                    backgroundColor: "var(--destructive)",
                    color: "white",
                    border: "none",
                },
            });
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[600px] bg-(--background) border-(--border) [&_[data-slot=dialog-close]]:hover:opacity-100 [&_[data-slot=dialog-close]]:cursor-pointer [&_[data-slot=dialog-close]]:transition-opacity [&_[data-slot=dialog-close]]:duration-200">
                <DialogHeader>
                    <DialogTitle className="flex items-center pb-2">
                        <Pencil className="mr-2 h-5 w-5 text-(--primary)" />
                        Update Agent
                    </DialogTitle>
                    <DialogDescription>Update your agent configuration.</DialogDescription>
                </DialogHeader>

                <Form {...form}>
                    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                        <FormField
                            control={form.control}
                            name="name"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Name</FormLabel>
                                    <FormControl>
                                        <Input
                                            placeholder="Enter agent name"
                                            className="bg-(--secondary)"
                                            {...field}
                                        />
                                    </FormControl>
                                </FormItem>
                            )}
                        />

                        <FormField
                            control={form.control}
                            name="description"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Description (Optional)</FormLabel>
                                    <FormControl>
                                        <Textarea
                                            placeholder="Enter agent description"
                                            className="bg-(--secondary) resize-none min-h-[80px]"
                                            {...field}
                                        />
                                    </FormControl>
                                </FormItem>
                            )}
                        />

                        <FormField
                            control={form.control}
                            name="system_prompt"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>System Prompt</FormLabel>
                                    <FormControl>
                                        <Textarea
                                            placeholder="Enter system prompt for the agent"
                                            className="bg-(--secondary) resize-none min-h-[120px]"
                                            {...field}
                                        />
                                    </FormControl>
                                </FormItem>
                            )}
                        />

                        <FormField
                            control={form.control}
                            name="llm_id"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Language Model</FormLabel>
                                    <Select
                                        onValueChange={field.onChange}
                                        defaultValue={field.value}
                                    >
                                        <FormControl>
                                            <SelectTrigger className="bg-(--secondary) w-full">
                                                <SelectValue placeholder="Select a language model" />
                                            </SelectTrigger>
                                        </FormControl>
                                        <SelectContent className="bg-(--background)">
                                            {isLoadingLLMs ? (
                                                <div className="flex items-center justify-center p-2">
                                                    <Loader2 className="h-4 w-4 animate-spin text-(--muted-foreground)" />
                                                </div>
                                            ) : llms.length === 0 ? (
                                                <div className="p-2 text-center text-(--muted-foreground)">
                                                    No LLMs available
                                                </div>
                                            ) : (
                                                llms.map((llm) => (
                                                    <SelectItem
                                                        key={llm.id}
                                                        value={llm.id}
                                                        className="hover:bg-(--secondary) focus:bg-(--secondary)"
                                                    >
                                                        {llm.model}
                                                    </SelectItem>
                                                ))
                                            )}
                                        </SelectContent>
                                    </Select>
                                </FormItem>
                            )}
                        />

                        <FormField
                            control={form.control}
                            name="mcp_server_ids"
                            render={() => (
                                <FormItem>
                                    <FormLabel>MCP Servers (Optional)</FormLabel>
                                    <div className="space-y-2">
                                        {isLoadingMCPServers ? (
                                            <div className="flex items-center justify-center p-4 bg-(--secondary) rounded-md">
                                                <Loader2 className="h-4 w-4 animate-spin text-(--muted-foreground)" />
                                            </div>
                                        ) : mcpServers.length === 0 ? (
                                            <div className="p-4 text-center text-(--muted-foreground) bg-(--secondary) rounded-md">
                                                No MCP servers available
                                            </div>
                                        ) : (
                                            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                                                {mcpServers.map((server) => (
                                                    <div
                                                        key={server.id}
                                                        className={`p-3 rounded-md border cursor-pointer transition-all duration-200 ${
                                                            selectedMCPServers.includes(server.id)
                                                                ? "border-(--primary) bg-(--primary)/10"
                                                                : "border-(--border) bg-(--secondary) hover:border-(--primary)/50"
                                                        }`}
                                                        onClick={() => toggleMCPServer(server.id)}
                                                    >
                                                        <div className="flex items-center justify-between">
                                                            <div className="flex items-center">
                                                                <Server className="mr-2 h-4 w-4 text-(--primary)" />
                                                                <span className="font-medium text-sm">
                                                                    {server.name}
                                                                </span>
                                                            </div>
                                                            {selectedMCPServers.includes(
                                                                server.id
                                                            ) && (
                                                                <Check className="h-4 w-4 text-(--primary)" />
                                                            )}
                                                        </div>
                                                        <div className="text-xs text-(--muted-foreground) mt-1 truncate">
                                                            {server.url}
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                </FormItem>
                            )}
                        />

                        <DialogFooter className="flex flex-col sm:flex-row sm:justify-between w-full gap-2">
                            <Button
                                type="button"
                                variant="outline"
                                onClick={() => onOpenChange(false)}
                                disabled={isSubmitting}
                                className="font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--border) bg-(--background) text-(--foreground) hover:bg-(--muted) h-10 cursor-pointer w-full sm:flex-1"
                            >
                                <span className="relative z-10">Cancel</span>
                                <span className="absolute inset-0 bg-(--muted)/50 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                            </Button>
                            <Button
                                type="submit"
                                disabled={isSubmitting}
                                className="font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--primary) bg-(--primary) text-(--primary-foreground) dark:bg-(--primary) dark:text-(--primary-foreground) dark:border-(--primary) h-10 cursor-pointer w-full sm:flex-1"
                            >
                                <span className="relative z-10">
                                    {isSubmitting ? (
                                        <>
                                            <Loader2 className="mr-2 h-4 w-4 animate-spin inline" />
                                            Updating...
                                        </>
                                    ) : (
                                        "Update Agent"
                                    )}
                                </span>
                                <span className="absolute inset-0 bg-(--primary-foreground)/10 dark:bg-(--primary-foreground)/20 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                            </Button>
                        </DialogFooter>
                    </form>
                </Form>
            </DialogContent>
        </Dialog>
    );
}
