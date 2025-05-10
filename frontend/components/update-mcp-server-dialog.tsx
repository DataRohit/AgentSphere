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
import { Textarea } from "@/components/ui/textarea";
import { zodResolver } from "@hookform/resolvers/zod";
import Cookies from "js-cookie";
import { Loader2, Pencil } from "lucide-react";
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
    description: string;
    url: string;
    tags: string;
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
        non_field_errors?: string[];
        [key: string]: string[] | undefined;
    };
    error?: string;
}

const updateMCPServerSchema = z.object({
    name: z.string().min(1, "Name is required"),
    description: z.string().optional(),
    url: z.string().url("Must be a valid URL").min(1, "URL is required"),
    tags: z.string().optional(),
});

type UpdateMCPServerValues = z.infer<typeof updateMCPServerSchema>;

interface UpdateMCPServerDialogProps {
    mcpServer: MCPServer;
    open: boolean;
    onOpenChange: (open: boolean) => void;
    onUpdateSuccess: () => void;
}

export function UpdateMCPServerDialog({
    mcpServer,
    open,
    onOpenChange,
    onUpdateSuccess,
}: UpdateMCPServerDialogProps) {
    const [isSubmitting, setIsSubmitting] = useState(false);

    const form = useForm<UpdateMCPServerValues>({
        resolver: zodResolver(updateMCPServerSchema),
        defaultValues: {
            name: mcpServer.name,
            description: mcpServer.description || "",
            url: mcpServer.url,
            tags: mcpServer.tags || "",
        },
    });

    const onSubmit = async (values: UpdateMCPServerValues) => {
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
                description: values.description,
                url: values.url,
                tags: values.tags,
            };

            const response = await fetch(
                `${process.env.NEXT_PUBLIC_API_URL}/tools/mcpserver/${mcpServer.id}/update/`,
                {
                    method: "PATCH",
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${accessToken}`,
                    },
                    body: JSON.stringify(payload),
                }
            );

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
                } else if (response.status === 403) {
                    toast.error("You do not have permission to update this MCP server.", {
                        style: {
                            backgroundColor: "var(--destructive)",
                            color: "white",
                            border: "none",
                        },
                    });
                } else if (response.status === 404) {
                    toast.error("MCP server not found.", {
                        style: {
                            backgroundColor: "var(--destructive)",
                            color: "white",
                            border: "none",
                        },
                    });
                } else {
                    throw new Error(data.error || "Failed to update MCP server");
                }
                return;
            }

            toast.success("MCP server updated successfully", {
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
                err instanceof Error ? err.message : "An error occurred while updating MCP server";
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
        if (open) {
            form.reset({
                name: mcpServer.name,
                description: mcpServer.description || "",
                url: mcpServer.url,
                tags: mcpServer.tags || "",
            });
        }
    }, [open, mcpServer, form]);

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[500px] bg-(--background) border-(--border) [&_[data-slot=dialog-close]]:hover:opacity-100 [&_[data-slot=dialog-close]]:cursor-pointer [&_[data-slot=dialog-close]]:transition-opacity [&_[data-slot=dialog-close]]:duration-200">
                <DialogHeader>
                    <DialogTitle className="flex items-center pb-2">
                        <Pencil className="mr-2 h-5 w-5 text-(--primary)" />
                        Update MCP Server
                    </DialogTitle>
                    <DialogDescription>Update your MCP server configuration.</DialogDescription>
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
                                        "Update"
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
