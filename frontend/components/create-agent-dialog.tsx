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
import { Bot, Check, Loader2, Server } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
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
    api_type: string;
    model: string;
}

interface ApiErrorResponse {
    status_code: number;
    errors?: {
        organization_id?: string[];
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

const createAgentSchema = z.object({
    name: z.string().min(1, "Name is required"),
    description: z.string().optional(),
    system_prompt: z.string().min(1, "System prompt is required"),
    llm_id: z.string().min(1, "LLM is required"),
    mcp_server_ids: z.array(z.string()).optional(),
});

type CreateAgentValues = z.infer<typeof createAgentSchema>;

interface CreateAgentDialogProps {
    organizationId: string;
    open: boolean;
    onOpenChange: (open: boolean) => void;
    onCreateSuccess?: () => void;
}

export function CreateAgentDialog({
    organizationId,
    open,
    onOpenChange,
    onCreateSuccess,
}: CreateAgentDialogProps) {
    const router = useRouter();
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [llms, setLLMs] = useState<LLM[]>([]);
    const [mcpServers, setMCPServers] = useState<MCPServer[]>([]);
    const [isLoadingLLMs, setIsLoadingLLMs] = useState(false);
    const [isLoadingMCPServers, setIsLoadingMCPServers] = useState(false);
    const [selectedMCPServers, setSelectedMCPServers] = useState<string[]>([]);

    const form = useForm<CreateAgentValues>({
        resolver: zodResolver(createAgentSchema),
        defaultValues: {
            name: "",
            description: "",
            system_prompt: "",
            llm_id: "",
            mcp_server_ids: [],
        },
    });

    const fetchLLMs = async () => {
        setIsLoadingLLMs(true);
        try {
            const accessToken = Cookies.get("access_token");
            if (!accessToken) {
                throw new Error("Authentication token not found");
            }

            const response = await fetch(
                `http://localhost:8080/api/v1/llms/list/me?organization_id=${organizationId}`,
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
    };

    const fetchMCPServers = async () => {
        setIsLoadingMCPServers(true);
        try {
            const accessToken = Cookies.get("access_token");
            if (!accessToken) {
                throw new Error("Authentication token not found");
            }

            const response = await fetch(
                `http://localhost:8080/api/v1/tools/mcpserver/list/me/?organization_id=${organizationId}`,
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
    };

    useEffect(() => {
        if (open) {
            fetchLLMs();
            fetchMCPServers();
        }
    }, [open, organizationId]);

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

    const onSubmit = async (values: CreateAgentValues) => {
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
                organization_id: organizationId,
                name: values.name,
                description: values.description || "",
                system_prompt: values.system_prompt,
                llm_id: values.llm_id,
                mcp_server_ids: values.mcp_server_ids || [],
            };

            const response = await fetch("http://localhost:8080/api/v1/agents/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${accessToken}`,
                },
                body: JSON.stringify(payload),
            });

            const data = await response.json();

            if (!response.ok) {
                const errorData = data as ApiErrorResponse;
                if (errorData.errors) {
                    // Handle field errors
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
                                form.setError(field as any, {
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
                    toast.error("Failed to create agent", {
                        style: {
                            backgroundColor: "var(--destructive)",
                            color: "white",
                            border: "none",
                        },
                    });
                }
                return;
            }

            toast.success("Agent created successfully", {
                style: {
                    backgroundColor: "oklch(0.45 0.18 142.71)",
                    color: "white",
                    border: "none",
                },
            });

            onOpenChange(false);
            if (onCreateSuccess) {
                onCreateSuccess();
            }

            // Redirect to the agent detail page
            if (data.agent && data.agent.id) {
                router.push(`/agents/${data.agent.id}`);
            }
        } catch (err) {
            const errorMessage =
                err instanceof Error ? err.message : "An error occurred while creating the agent";
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
                        <Bot className="mr-2 h-5 w-5 text-(--primary)" />
                        Create New Agent
                    </DialogTitle>
                    <DialogDescription>
                        Configure a new AI agent with custom capabilities.
                    </DialogDescription>
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
                                                        {llm.api_type.charAt(0).toUpperCase() +
                                                            llm.api_type.slice(1)}{" "}
                                                        / {llm.model}
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
                                            Creating...
                                        </>
                                    ) : (
                                        "Create Agent"
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
