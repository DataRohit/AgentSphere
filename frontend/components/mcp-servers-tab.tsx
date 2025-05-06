"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog";
import { Form, FormControl, FormField, FormItem, FormLabel } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { zodResolver } from "@hookform/resolvers/zod";
import { formatDistanceToNow } from "date-fns";
import { motion } from "framer-motion";
import Cookies from "js-cookie";
import {
    AlertCircle,
    Calendar,
    FileText,
    Globe,
    Loader2,
    Pencil,
    Plus,
    Server,
    Tag,
    Trash2,
    Wrench,
} from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import * as z from "zod";
import { DeleteMCPServerDialog } from "./delete-mcp-server-dialog";
import { UpdateMCPServerDialog } from "./update-mcp-server-dialog";

interface Tool {
    id: string;
    name: string;
    description: string;
}

interface MCPServer {
    id: string;
    name: string;
    description: string;
    url: string;
    tags: string;
    organization: {
        id: string;
        name: string;
    };
    user: {
        id: string;
        username: string;
        email: string;
    };
    tools: (string | Tool)[];
    created_at: string;
    updated_at: string;
}

interface ApiErrorResponse {
    status_code: number;
    errors?: {
        name?: string[];
        description?: string[];
        url?: string[];
        tags?: string[];
        organization_id?: string[];
        non_field_errors?: string[];
        [key: string]: string[] | undefined;
    };
    error?: string;
}

const createMCPServerSchema = z.object({
    name: z.string().min(1, "Name is required"),
    description: z.string().optional(),
    url: z.string().url("Must be a valid URL").min(1, "URL is required"),
    tags: z.string().optional(),
});

type CreateMCPServerValues = z.infer<typeof createMCPServerSchema>;

interface MCPServersTabProps {
    organizationId: string;
    filterByUsername?: string;
    readOnly?: boolean;
}

export function MCPServersTab({
    organizationId,
    filterByUsername,
    readOnly = false,
}: MCPServersTabProps) {
    const [mcpServers, setMCPServers] = useState<MCPServer[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [isDialogOpen, setIsDialogOpen] = useState(false);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
    const [mcpServerToDelete, setMcpServerToDelete] = useState<MCPServer | null>(null);
    const [isUpdateDialogOpen, setIsUpdateDialogOpen] = useState(false);
    const [mcpServerToUpdate, setMcpServerToUpdate] = useState<MCPServer | null>(null);

    const form = useForm<CreateMCPServerValues>({
        resolver: zodResolver(createMCPServerSchema),
        defaultValues: {
            name: "",
            description: "",
            url: "",
            tags: "",
        },
    });

    const fetchMCPServers = useCallback(async () => {
        setIsLoading(true);
        setError(null);

        try {
            const accessToken = Cookies.get("access_token");
            if (!accessToken) {
                throw new Error("Authentication token not found");
            }

            const queryParams = new URLSearchParams();
            let endpoint;

            if (filterByUsername) {
                endpoint = "http://localhost:8080/api/v1/tools/mcpserver/list/";
                queryParams.append("organization_id", organizationId);
                queryParams.append("username", filterByUsername);
            } else {
                endpoint = "http://localhost:8080/api/v1/tools/mcpserver/list/me/";
                queryParams.append("organization_id", organizationId);
            }

            const response = await fetch(`${endpoint}?${queryParams.toString()}`, {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${accessToken}`,
                },
            });

            const data = await response.json();

            if (!response.ok) {
                if (response.status === 404) {
                    setMCPServers([]);
                    return;
                }
                throw new Error(data.error || "Failed to fetch MCP servers");
            }

            const serversData = data.mcpservers || [];

            setMCPServers(serversData);
        } catch (err) {
            const errorMessage =
                err instanceof Error ? err.message : "An error occurred while fetching MCP servers";
            setError(errorMessage);
            toast.error(errorMessage, {
                style: {
                    backgroundColor: "var(--destructive)",
                    color: "white",
                    border: "none",
                },
            });
        } finally {
            setIsLoading(false);
        }
    }, [filterByUsername, organizationId]);

    const onSubmit = async (values: CreateMCPServerValues) => {
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
                description: values.description,
                url: values.url,
                tags: values.tags,
            };

            const response = await fetch("http://localhost:8080/api/v1/tools/mcpserver/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${accessToken}`,
                },
                body: JSON.stringify(payload),
            });

            const data = (await response.json()) as ApiErrorResponse;

            if (!response.ok) {
                if (response.status === 400 && data.errors) {
                    Object.entries(data.errors).forEach(([field, fieldErrors]) => {
                        if (fieldErrors && fieldErrors.length > 0) {
                            if (field === "non_field_errors") {
                                toast.error(fieldErrors[0], {
                                    style: {
                                        backgroundColor: "var(--destructive)",
                                        color: "white",
                                        border: "none",
                                    },
                                });
                            } else {
                                toast.error(
                                    `${
                                        field.charAt(0).toUpperCase() +
                                        field.slice(1).replace(/_/g, " ")
                                    }: ${fieldErrors[0]}`,
                                    {
                                        style: {
                                            backgroundColor: "var(--destructive)",
                                            color: "white",
                                            border: "none",
                                        },
                                    }
                                );
                            }
                        }
                    });
                } else if (response.status === 401) {
                    toast.error("Authentication credentials were not provided or are invalid.", {
                        style: {
                            backgroundColor: "var(--destructive)",
                            color: "white",
                            border: "none",
                        },
                    });
                } else {
                    throw new Error(data.error || "Failed to create MCP server");
                }
                return;
            }

            toast.success("MCP server created successfully", {
                style: {
                    backgroundColor: "oklch(0.45 0.18 142.71)",
                    color: "white",
                    border: "none",
                },
            });

            form.reset();
            setIsDialogOpen(false);

            fetchMCPServers();
        } catch (err) {
            const errorMessage =
                err instanceof Error ? err.message : "An error occurred while creating MCP server";
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

    useEffect(() => {
        if (organizationId) {
            fetchMCPServers();
        }
    }, [organizationId, fetchMCPServers]);

    useEffect(() => {
        if (!isDialogOpen) {
            form.reset({
                name: "",
                description: "",
                url: "",
                tags: "",
            });
        }
    }, [isDialogOpen, form]);

    const renderMCPServerCards = () => {
        if (isLoading) {
            return (
                <div className="flex justify-center items-center p-8">
                    <Loader2 className="h-8 w-8 animate-spin text-(--muted-foreground)" />
                </div>
            );
        }

        if (error) {
            return (
                <Card className="p-6 bg-(--destructive)/10 border-none">
                    <div className="flex flex-col items-center justify-center p-4 text-center">
                        <div className="h-10 w-10 rounded-full bg-(--destructive)/10 flex items-center justify-center mb-3">
                            <AlertCircle className="h-5 w-5 text-(--destructive)" />
                        </div>
                        <h3 className="text-sm font-medium mb-1">Failed to load MCP servers</h3>
                        <p className="text-xs text-(--muted-foreground) mb-3">{error}</p>
                        <Button
                            onClick={fetchMCPServers}
                            variant="outline"
                            size="sm"
                            className="h-8 text-xs"
                        >
                            Retry
                        </Button>
                    </div>
                </Card>
            );
        }

        if (mcpServers.length === 0) {
            return (
                <Card className="p-6 border border-dashed border-(--border)">
                    <div className="flex flex-col items-center justify-center p-4 text-center">
                        <Server className="h-12 w-12 text-(--muted-foreground) mb-3" />
                        <h3 className="text-lg font-medium mb-1">No MCP Servers Connected</h3>
                        <p className="text-sm text-(--muted-foreground) mb-4">
                            {readOnly
                                ? "This user has not created any MCP servers yet."
                                : "Connect to MCP servers to enable advanced agent capabilities."}
                        </p>
                        {!readOnly && (
                            <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                                <DialogTrigger asChild>
                                    <Button className="font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--primary) bg-(--primary) text-(--primary-foreground) dark:bg-(--primary) dark:text-(--primary-foreground) dark:border-(--primary) h-10 cursor-pointer">
                                        <span className="relative z-10 flex items-center">
                                            <Plus className="mr-2 h-4 w-4" />
                                            Add MCP Server
                                        </span>
                                        <span className="absolute inset-0 bg-(--primary-foreground)/10 dark:bg-(--primary-foreground)/20 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                                    </Button>
                                </DialogTrigger>
                                {renderCreateMCPServerDialog()}
                            </Dialog>
                        )}
                    </div>
                </Card>
            );
        }

        return (
            <div className="grid grid-cols-1 gap-4">
                {mcpServers.map((server, index) => (
                    <motion.div
                        key={server.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.3, delay: index * 0.1 }}
                        whileHover={{ y: -5, transition: { duration: 0.2 } }}
                        className="h-full"
                    >
                        <Card className="h-full flex flex-col p-0 pt-6 border border-(--border) shadow-sm hover:shadow-md transition-all duration-300 overflow-hidden bg-(--secondary) dark:bg-(--secondary) relative gap-2">
                            {!readOnly && (
                                <div className="absolute top-2 right-2 flex space-x-1">
                                    <div className="group">
                                        <Button
                                            variant="ghost"
                                            size="icon"
                                            className="h-8 w-8 rounded-full hover:bg-(--primary)/10 hover:text-(--primary) transition-all duration-200 cursor-pointer"
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                setMcpServerToUpdate(server);
                                                setIsUpdateDialogOpen(true);
                                            }}
                                        >
                                            <Pencil className="h-4 w-4" />
                                            <span className="sr-only">Edit</span>
                                        </Button>
                                    </div>
                                    <div className="group">
                                        <Button
                                            variant="ghost"
                                            size="icon"
                                            className="h-8 w-8 rounded-full hover:bg-(--destructive)/10 hover:text-(--destructive) transition-all duration-200 cursor-pointer"
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                setMcpServerToDelete(server);
                                                setIsDeleteDialogOpen(true);
                                            }}
                                        >
                                            <Trash2 className="h-4 w-4 text-(--destructive)" />
                                            <span className="sr-only">Delete</span>
                                        </Button>
                                    </div>
                                </div>
                            )}
                            <CardHeader className="pb-2">
                                <div className="flex items-center">
                                    <CardTitle className="flex items-center text-lg font-semibold">
                                        <Server className="mr-2 h-5 w-5 text-(--primary)" />
                                        {server.name}
                                    </CardTitle>
                                </div>
                            </CardHeader>
                            <CardContent className="px-6 pb-6">
                                <div className="space-y-3">
                                    {server.description && (
                                        <div>
                                            <div className="flex items-center text-sm">
                                                <FileText className="mr-2 h-4 w-4 text-(--primary)" />
                                                <p className="font-medium">Details:</p>
                                            </div>
                                            <div className="mt-1 text-sm text-(--muted-foreground)">
                                                {server.description}
                                            </div>
                                        </div>
                                    )}

                                    <div className="flex items-center text-sm">
                                        <Globe className="mr-2 h-4 w-4 text-(--primary)" />
                                        <p className="font-medium">URL:</p>
                                        <p className="ml-2 text-(--muted-foreground) truncate">
                                            {server.url}
                                        </p>
                                    </div>
                                    <div className="flex items-center text-sm">
                                        <Tag className="mr-2 h-4 w-4 text-(--primary)" />
                                        <p className="font-medium mr-2">Tags:</p>
                                        <div className="flex flex-wrap gap-1">
                                            {server.tags.split(",").map((tag, tagIndex) => (
                                                <Badge
                                                    key={`${
                                                        server.id
                                                    }-tag-${tagIndex}-${tag.trim()}`}
                                                    variant="outline"
                                                    className="bg-(--primary)/10 text-(--primary) border-(--primary)/20"
                                                >
                                                    {tag.trim()}
                                                </Badge>
                                            ))}
                                        </div>
                                    </div>
                                    <div className="flex flex-col space-y-2">
                                        <div className="flex items-center text-sm">
                                            <Wrench className="mr-2 h-4 w-4 text-(--primary)" />
                                            <p className="font-medium">Tools:</p>
                                        </div>
                                        <div className="max-h-[200px] overflow-y-auto pr-2 border border-(--border) rounded-md p-2">
                                            {server.tools.length > 0 ? (
                                                <div className="space-y-2">
                                                    {server.tools.map((tool, toolIndex) => {
                                                        const toolObj =
                                                            typeof tool === "object"
                                                                ? (tool as Tool)
                                                                : {
                                                                      id: `unknown-${toolIndex}`,
                                                                      name: "Unknown",
                                                                      description: "",
                                                                  };
                                                        return (
                                                            <div
                                                                key={`${
                                                                    server.id
                                                                }-tool-${toolIndex}-${
                                                                    toolObj.id || toolIndex
                                                                }`}
                                                                className="px-4 py-3 bg-(--primary)/10 rounded-md"
                                                            >
                                                                <p className="text-sm font-medium">
                                                                    {toolObj.name}
                                                                </p>
                                                                {toolObj.description && (
                                                                    <p className="text-xs text-(--muted-foreground) mt-1">
                                                                        {toolObj.description}
                                                                    </p>
                                                                )}
                                                            </div>
                                                        );
                                                    })}
                                                </div>
                                            ) : (
                                                <span className="text-xs text-(--muted-foreground) block py-2">
                                                    No tools available
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            </CardContent>
                            <div className="mt-auto border-t bg-(--muted)/10 px-6 py-3">
                                <div className="w-full flex flex-col sm:flex-row sm:justify-between space-y-1 sm:space-y-0">
                                    <div className="flex items-center text-xs text-(--muted-foreground)">
                                        <Calendar className="mr-1 h-3 w-3" />
                                        <span>
                                            Created{" "}
                                            {formatDistanceToNow(new Date(server.created_at), {
                                                addSuffix: true,
                                            })}
                                        </span>
                                    </div>
                                    <div className="flex items-center text-xs text-(--muted-foreground)">
                                        <Calendar className="mr-1 h-3 w-3" />
                                        <span>
                                            Updated{" "}
                                            {formatDistanceToNow(new Date(server.updated_at), {
                                                addSuffix: true,
                                            })}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </Card>
                    </motion.div>
                ))}

                {!readOnly && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.3, delay: 0.1 * mcpServers.length }}
                        whileHover={{ y: -5, transition: { duration: 0.2 } }}
                        className="h-full"
                    >
                        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                            <DialogTrigger asChild>
                                <Card className="h-full flex flex-col justify-center items-center p-6 cursor-pointer border border-dashed border-(--primary) bg-(--card) hover:bg-(--primary)/5 transition-all duration-300 group gap-2">
                                    <div className="flex flex-col items-center text-center">
                                        <div className="h-12 w-12 rounded-full bg-(--primary)/10 flex items-center justify-center mb-4 group-hover:bg-(--primary)/20 transition-colors duration-300">
                                            <Plus className="h-6 w-6 text-(--primary)" />
                                        </div>
                                        <h3 className="text-lg font-semibold mb-2 group-hover:text-(--primary) transition-colors duration-300">
                                            Add New Server
                                        </h3>
                                        <p className="text-sm text-(--muted-foreground)">
                                            Connect to a new MCP server for your agents
                                        </p>
                                    </div>
                                </Card>
                            </DialogTrigger>
                            {renderCreateMCPServerDialog()}
                        </Dialog>
                    </motion.div>
                )}
            </div>
        );
    };

    const renderCreateMCPServerDialog = () => {
        return (
            <DialogContent className="sm:max-w-[500px] bg-(--background) border-(--border) [&_[data-slot=dialog-close]]:hover:opacity-100 [&_[data-slot=dialog-close]]:cursor-pointer [&_[data-slot=dialog-close]]:transition-opacity [&_[data-slot=dialog-close]]:duration-200">
                <DialogHeader>
                    <DialogTitle className="pb-2">Add New MCP Server</DialogTitle>
                    <DialogDescription>
                        Connect to a new MCP server to enable advanced agent capabilities.
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
                                            placeholder="Enter server name"
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
                                    <FormLabel>Description</FormLabel>
                                    <FormControl>
                                        <Textarea
                                            placeholder="Enter server description"
                                            className="bg-(--secondary) resize-none min-h-[80px]"
                                            {...field}
                                        />
                                    </FormControl>
                                </FormItem>
                            )}
                        />

                        <FormField
                            control={form.control}
                            name="url"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>URL</FormLabel>
                                    <FormControl>
                                        <Input
                                            placeholder="https://example.com/api"
                                            className="bg-(--secondary)"
                                            {...field}
                                        />
                                    </FormControl>
                                </FormItem>
                            )}
                        />

                        <FormField
                            control={form.control}
                            name="tags"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Tags</FormLabel>
                                    <FormControl>
                                        <Input
                                            placeholder="finance,flights,hotels"
                                            className="bg-(--secondary)"
                                            {...field}
                                        />
                                    </FormControl>
                                </FormItem>
                            )}
                        />

                        <DialogFooter className="flex flex-col sm:flex-row sm:justify-between w-full gap-2">
                            <Button
                                type="button"
                                variant="outline"
                                onClick={() => setIsDialogOpen(false)}
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
                                        "Create Server"
                                    )}
                                </span>
                                <span className="absolute inset-0 bg-(--primary-foreground)/10 dark:bg-(--primary-foreground)/20 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                            </Button>
                        </DialogFooter>
                    </form>
                </Form>
            </DialogContent>
        );
    };

    return (
        <>
            <div className="space-y-6">{renderMCPServerCards()}</div>

            {mcpServerToDelete && (
                <DeleteMCPServerDialog
                    mcpServer={mcpServerToDelete}
                    open={isDeleteDialogOpen}
                    onOpenChange={(open) => {
                        setIsDeleteDialogOpen(open);
                        if (!open) {
                            setTimeout(() => setMcpServerToDelete(null), 300);
                        }
                    }}
                    onDeleteSuccess={fetchMCPServers}
                />
            )}

            {mcpServerToUpdate && (
                <UpdateMCPServerDialog
                    mcpServer={mcpServerToUpdate}
                    open={isUpdateDialogOpen}
                    onOpenChange={(open) => {
                        setIsUpdateDialogOpen(open);
                        if (!open) {
                            setTimeout(() => setMcpServerToUpdate(null), 300);
                        }
                    }}
                    onUpdateSuccess={fetchMCPServers}
                />
            )}
        </>
    );
}
