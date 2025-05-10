"use client";

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
import { zodResolver } from "@hookform/resolvers/zod";
import { formatDistanceToNow } from "date-fns";
import { motion } from "framer-motion";
import Cookies from "js-cookie";
import {
    AlertCircle,
    Calendar,
    Cpu,
    Globe,
    Key,
    Loader2,
    Pencil,
    Plus,
    Server,
    Trash2,
} from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import * as z from "zod";
import { DeleteLLMDialog } from "./delete-llm-dialog";
import { UpdateLLMDialog } from "./update-llm-dialog";

interface LLM {
    id: string;
    base_url: string;
    model: string;
    max_tokens: number;
    organization: {
        id: string;
        name: string;
    };
    user: {
        id: string;
        username: string;
        email: string;
    };
    created_at: string;
    updated_at: string;
}

interface ApiErrorResponse {
    status_code: number;
    errors?: {
        base_url?: string[];
        model?: string[];
        api_key?: string[];
        max_tokens?: string[];
        non_field_errors?: string[];
        [key: string]: string[] | undefined;
    };
    error?: string;
}

const createLLMSchema = z.object({
    base_url: z.string().url("Base URL must be a valid URL").min(1, "Base URL is required"),
    model: z.string().min(1, "Model is required"),
    api_key: z.string().min(1, "API key is required"),
    max_tokens: z.number().int().positive("Max tokens must be a positive number"),
});

type CreateLLMValues = z.infer<typeof createLLMSchema>;

interface LLMsTabProps {
    organizationId: string;
    filterByUsername?: string;
    readOnly?: boolean;
}

export function LLMsTab({ organizationId, filterByUsername, readOnly = false }: LLMsTabProps) {
    const [llms, setLLMs] = useState<LLM[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [isDialogOpen, setIsDialogOpen] = useState(false);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
    const [llmToDelete, setLlmToDelete] = useState<LLM | null>(null);
    const [isUpdateDialogOpen, setIsUpdateDialogOpen] = useState(false);
    const [llmToUpdate, setLlmToUpdate] = useState<LLM | null>(null);

    const form = useForm<CreateLLMValues>({
        resolver: zodResolver(createLLMSchema),
        defaultValues: {
            base_url: "",
            model: "",
            api_key: "",
            max_tokens: 4096,
        },
    });

    const fetchLLMs = useCallback(async () => {
        setIsLoading(true);
        setError(null);

        try {
            const accessToken = Cookies.get("access_token");
            if (!accessToken) {
                throw new Error("Authentication token not found");
            }

            let endpoint;
            const queryParams = new URLSearchParams();

            if (filterByUsername) {
                endpoint = `${process.env.NEXT_PUBLIC_API_URL}/llms/list/`;
                queryParams.append("organization_id", organizationId);
                queryParams.append("username", filterByUsername);
            } else {
                endpoint = `${process.env.NEXT_PUBLIC_API_URL}/llms/list/me`;
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
                    setLLMs([]);
                    return;
                }
                throw new Error(data.error || "Failed to fetch LLMs");
            }

            const llmsData = data.llms || [];

            setLLMs(llmsData);
        } catch (err) {
            const errorMessage =
                err instanceof Error ? err.message : "An error occurred while fetching LLMs";
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
    }, [organizationId, filterByUsername]);

    const onSubmit = async (values: CreateLLMValues) => {
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
                base_url: values.base_url,
                model: values.model,
                api_key: values.api_key,
                max_tokens: values.max_tokens,
            };

            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/llms/`, {
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
                } else if (response.status === 403) {
                    toast.error("You do not have permission to create this LLM configuration.", {
                        style: {
                            backgroundColor: "var(--destructive)",
                            color: "white",
                            border: "none",
                        },
                    });
                } else {
                    throw new Error(data.error || "Failed to create LLM configuration");
                }
                return;
            }

            toast.success("LLM configuration created successfully", {
                style: {
                    backgroundColor: "oklch(0.45 0.18 142.71)",
                    color: "white",
                    border: "none",
                },
            });

            form.reset();
            setIsDialogOpen(false);

            fetchLLMs();
        } catch (err) {
            const errorMessage =
                err instanceof Error
                    ? err.message
                    : "An error occurred while creating LLM configuration";
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
            fetchLLMs();
        }
    }, [organizationId, fetchLLMs]);

    useEffect(() => {
        if (!isDialogOpen) {
            form.reset({
                base_url: "",
                model: "",
                api_key: "",
                max_tokens: 4096,
            });
        }
    }, [isDialogOpen, form]);

    const renderLLMCards = () => {
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
                        <h3 className="text-sm font-medium mb-1">Failed to load LLMs</h3>
                        <p className="text-xs text-(--muted-foreground) mb-3">{error}</p>
                        <Button
                            onClick={fetchLLMs}
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

        if (llms.length === 0) {
            return (
                <Card className="p-6 border border-dashed border-(--border)">
                    <div className="flex flex-col items-center justify-center p-4 text-center">
                        <Cpu className="h-12 w-12 text-(--muted-foreground) mb-3" />
                        <h3 className="text-lg font-medium mb-1">No LLMs Configured</h3>
                        <p className="text-sm text-(--muted-foreground) mb-4">
                            {readOnly
                                ? "This user has not configured any LLMs yet."
                                : "Configure your first LLM to start creating AI agents."}
                        </p>
                        {!readOnly && (
                            <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                                <DialogTrigger asChild>
                                    <Button className="font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--primary) bg-(--primary) text-(--primary-foreground) dark:bg-(--primary) dark:text-(--primary-foreground) dark:border-(--primary) h-10 cursor-pointer">
                                        <span className="relative z-10 flex items-center">
                                            <Plus className="mr-2 h-4 w-4" />
                                            Configure LLM
                                        </span>
                                        <span className="absolute inset-0 bg-(--primary-foreground)/10 dark:bg-(--primary-foreground)/20 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                                    </Button>
                                </DialogTrigger>
                                {renderCreateLLMDialog()}
                            </Dialog>
                        )}
                    </div>
                </Card>
            );
        }

        return (
            <div className="flex flex-col space-y-4">
                {llms.map((llm, index) => (
                    <motion.div
                        key={llm.id}
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
                                                setLlmToUpdate(llm);
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
                                                setLlmToDelete(llm);
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
                                        LLM Configuration
                                    </CardTitle>
                                </div>
                            </CardHeader>
                            <CardContent className="px-6 pb-4">
                                <div className="space-y-3">
                                    <div>
                                        <div className="flex items-center text-sm">
                                            <Globe className="mr-2 h-4 w-4 text-(--primary)" />
                                            <p className="font-medium">Base URL:</p>
                                        </div>
                                        <div className="mt-1 text-sm text-(--muted-foreground) truncate">
                                            {llm.base_url}
                                        </div>
                                    </div>
                                    <div>
                                        <div className="flex items-center text-sm">
                                            <Cpu className="mr-2 h-4 w-4 text-(--primary)" />
                                            <p className="font-medium">Model:</p>
                                        </div>
                                        <div className="mt-1 text-sm text-(--muted-foreground)">
                                            {llm.model}
                                        </div>
                                    </div>
                                    <div>
                                        <div className="flex items-center text-sm">
                                            <Key className="mr-2 h-4 w-4 text-(--primary)" />
                                            <p className="font-medium">Max Tokens:</p>
                                        </div>
                                        <div className="mt-1 text-sm text-(--muted-foreground)">
                                            {llm.max_tokens.toLocaleString()}
                                        </div>
                                    </div>
                                </div>
                            </CardContent>
                            <div className="mt-auto border-t bg-(--muted)/10 px-6 py-3">
                                <div className="w-full flex flex-col space-y-1">
                                    <div className="flex items-center text-xs text-(--muted-foreground)">
                                        <Calendar className="mr-1 h-3 w-3" />
                                        <span>
                                            Created{" "}
                                            {formatDistanceToNow(new Date(llm.created_at), {
                                                addSuffix: true,
                                            })}
                                        </span>
                                    </div>
                                    <div className="flex items-center text-xs text-(--muted-foreground)">
                                        <Calendar className="mr-1 h-3 w-3" />
                                        <span>
                                            Updated{" "}
                                            {formatDistanceToNow(new Date(llm.updated_at), {
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
                        transition={{ duration: 0.3, delay: 0.1 * llms.length }}
                        whileHover={{ y: -5, transition: { duration: 0.2 } }}
                        className="w-full"
                    >
                        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                            <DialogTrigger asChild>
                                <Card className="h-full flex flex-col justify-center items-center p-6 cursor-pointer border border-dashed border-(--primary) bg-(--card) hover:bg-(--primary)/5 transition-all duration-300 group gap-2">
                                    <div className="flex flex-col items-center text-center">
                                        <div className="h-12 w-12 rounded-full bg-(--primary)/10 flex items-center justify-center mb-4 group-hover:bg-(--primary)/20 transition-colors duration-300">
                                            <Plus className="h-6 w-6 text-(--primary)" />
                                        </div>
                                        <h3 className="text-lg font-semibold mb-2 group-hover:text-(--primary) transition-colors duration-300">
                                            Add New LLM
                                        </h3>
                                        <p className="text-sm text-(--muted-foreground)">
                                            Configure a new language model for your agents
                                        </p>
                                    </div>
                                </Card>
                            </DialogTrigger>
                            {renderCreateLLMDialog()}
                        </Dialog>
                    </motion.div>
                )}
            </div>
        );
    };

    const renderCreateLLMDialog = () => {
        return (
            <DialogContent className="sm:max-w-[500px] bg-(--background) border-(--border) [&_[data-slot=dialog-close]]:hover:opacity-100 [&_[data-slot=dialog-close]]:cursor-pointer [&_[data-slot=dialog-close]]:transition-opacity [&_[data-slot=dialog-close]]:duration-200">
                <DialogHeader>
                    <DialogTitle className="pb-2">Configure New LLM</DialogTitle>
                    <DialogDescription>
                        Add a new language model configuration to use with your agents.
                    </DialogDescription>
                </DialogHeader>

                <Form {...form}>
                    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                        <FormField
                            control={form.control}
                            name="base_url"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Base URL</FormLabel>
                                    <FormControl>
                                        <div className="relative">
                                            <Input
                                                type="url"
                                                placeholder="https://api.example.com"
                                                className="bg-(--secondary) pr-10"
                                                {...field}
                                            />
                                            <Globe className="absolute right-3 top-2.5 h-4 w-4 text-(--muted-foreground) pointer-events-none" />
                                        </div>
                                    </FormControl>
                                </FormItem>
                            )}
                        />

                        <FormField
                            control={form.control}
                            name="model"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Model</FormLabel>
                                    <FormControl>
                                        <div className="relative">
                                            <Input
                                                type="text"
                                                placeholder="e.g., gpt-4, gemini-pro"
                                                className="bg-(--secondary) pr-10"
                                                {...field}
                                            />
                                            <Cpu className="absolute right-3 top-2.5 h-4 w-4 text-(--muted-foreground) pointer-events-none" />
                                        </div>
                                    </FormControl>
                                </FormItem>
                            )}
                        />

                        <FormField
                            control={form.control}
                            name="api_key"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>API Key</FormLabel>
                                    <FormControl>
                                        <div className="relative">
                                            <Input
                                                type="password"
                                                placeholder="Enter your API key"
                                                className="bg-(--secondary) pr-10"
                                                {...field}
                                            />
                                            <Key className="absolute right-3 top-2.5 h-4 w-4 text-(--muted-foreground) pointer-events-none" />
                                        </div>
                                    </FormControl>
                                </FormItem>
                            )}
                        />

                        <FormField
                            control={form.control}
                            name="max_tokens"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Max Tokens</FormLabel>
                                    <FormControl>
                                        <Input
                                            type="number"
                                            placeholder="4096"
                                            className="bg-(--secondary)"
                                            {...field}
                                            onChange={(e) =>
                                                field.onChange(parseInt(e.target.value) || 0)
                                            }
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
                                        "Create LLM"
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
            <div className="space-y-6">{renderLLMCards()}</div>

            {llmToDelete && (
                <DeleteLLMDialog
                    llm={llmToDelete}
                    open={isDeleteDialogOpen}
                    onOpenChange={(open) => {
                        setIsDeleteDialogOpen(open);
                        if (!open) {
                            setTimeout(() => setLlmToDelete(null), 300);
                        }
                    }}
                    onDeleteSuccess={fetchLLMs}
                />
            )}

            {llmToUpdate && (
                <UpdateLLMDialog
                    llm={llmToUpdate}
                    open={isUpdateDialogOpen}
                    onOpenChange={(open) => {
                        setIsUpdateDialogOpen(open);
                        if (!open) {
                            setTimeout(() => setLlmToUpdate(null), 300);
                        }
                    }}
                    onUpdateSuccess={fetchLLMs}
                />
            )}
        </>
    );
}
