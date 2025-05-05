"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
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
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { zodResolver } from "@hookform/resolvers/zod";
import { formatDistanceToNow } from "date-fns";
import { motion } from "framer-motion";
import Cookies from "js-cookie";
import {
    AlertCircle,
    Bot,
    Calendar,
    Cpu,
    Key,
    Loader2,
    Pencil,
    Plus,
    Server,
    Trash2,
} from "lucide-react";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import * as z from "zod";
import { DeleteLLMDialog } from "./delete-llm-dialog";
import { UpdateLLMDialog } from "./update-llm-dialog";

interface LLM {
    id: string;
    api_type: string;
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

interface LLMModel {
    id: string;
    name: string;
}

interface ApiErrorResponse {
    status_code: number;
    errors?: {
        api_type?: string[];
        model?: string[];
        api_key?: string[];
        max_tokens?: string[];
        non_field_errors?: string[];
        [key: string]: string[] | undefined;
    };
    error?: string;
}

const createLLMSchema = z.object({
    api_type: z.string().min(1, "API type is required"),
    model: z.string().min(1, "Model is required"),
    api_key: z.string().min(1, "API key is required"),
    max_tokens: z.number().int().positive("Max tokens must be a positive number"),
});

type CreateLLMValues = z.infer<typeof createLLMSchema>;

interface LLMsTabProps {
    organizationId: string;
}

export function LLMsTab({ organizationId }: LLMsTabProps) {
    const [llms, setLLMs] = useState<LLM[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [isDialogOpen, setIsDialogOpen] = useState(false);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [apiTypes] = useState<string[]>(["google"]);
    const [models, setModels] = useState<LLMModel[]>([]);
    const [selectedApiType, setSelectedApiType] = useState<string>("");
    const [isLoadingModels, setIsLoadingModels] = useState(false);
    const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
    const [llmToDelete, setLlmToDelete] = useState<LLM | null>(null);
    const [isUpdateDialogOpen, setIsUpdateDialogOpen] = useState(false);
    const [llmToUpdate, setLlmToUpdate] = useState<LLM | null>(null);

    const form = useForm<CreateLLMValues>({
        resolver: zodResolver(createLLMSchema),
        defaultValues: {
            api_type: "",
            model: "",
            api_key: "",
            max_tokens: 4096,
        },
    });

    const fetchLLMs = async () => {
        setIsLoading(true);
        setError(null);

        try {
            const accessToken = Cookies.get("access_token");
            if (!accessToken) {
                throw new Error("Authentication token not found");
            }

            const response = await fetch(
                `http://localhost:8080/api/v1/llms/list/me?org_id=${organizationId}`,
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
                if (response.status === 404) {
                    setLLMs([]);
                    return;
                }
                throw new Error(data.error || "Failed to fetch LLMs");
            }

            setLLMs(data.llms || []);
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
    };

    const fetchModels = async (apiType: string) => {
        setIsLoadingModels(true);
        try {
            const accessToken = Cookies.get("access_token");
            if (!accessToken) {
                throw new Error("Authentication token not found");
            }

            const response = await fetch(`http://localhost:8080/api/v1/llms/models/${apiType}/`, {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${accessToken}`,
                },
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || "Failed to fetch models");
            }

            setModels(data.models || []);
        } catch (err) {
            const errorMessage =
                err instanceof Error ? err.message : "An error occurred while fetching models";
            toast.error(errorMessage, {
                style: {
                    backgroundColor: "var(--destructive)",
                    color: "white",
                    border: "none",
                },
            });
            setModels([]);
        } finally {
            setIsLoadingModels(false);
        }
    };

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
                api_type: values.api_type,
                model: values.model,
                api_key: values.api_key,
                max_tokens: values.max_tokens,
            };

            const response = await fetch("http://localhost:8080/api/v1/llms/", {
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
    }, [organizationId]);

    // Reset form when dialog is closed
    useEffect(() => {
        if (!isDialogOpen) {
            form.reset({
                api_type: "",
                model: "",
                api_key: "",
                max_tokens: 4096,
            });
            setSelectedApiType("");
        }
    }, [isDialogOpen, form]);

    useEffect(() => {
        form.setValue("model", "");

        if (selectedApiType) {
            fetchModels(selectedApiType);
        }
    }, [selectedApiType, form]);

    const handleApiTypeChange = (value: string) => {
        setSelectedApiType(value);
        form.setValue("api_type", value);
    };

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
                        <Bot className="h-12 w-12 text-(--muted-foreground) mb-3" />
                        <h3 className="text-lg font-medium mb-1">No LLMs Configured</h3>
                        <p className="text-sm text-(--muted-foreground) mb-4">
                            Configure your first LLM to start creating AI agents.
                        </p>
                        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                            <DialogTrigger asChild>
                                <Button className="font-medium">
                                    <Plus className="mr-2 h-4 w-4" />
                                    Configure LLM
                                </Button>
                            </DialogTrigger>
                            {renderCreateLLMDialog()}
                        </Dialog>
                    </div>
                </Card>
            );
        }

        return (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {llms.map((llm, index) => (
                    <motion.div
                        key={llm.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.3, delay: index * 0.1 }}
                        whileHover={{ y: -5, transition: { duration: 0.2 } }}
                        className="h-full"
                    >
                        <Card className="h-full flex flex-col p-0 pt-6 border border-(--border) shadow-sm hover:shadow-md transition-all duration-300 overflow-hidden bg-(--secondary) dark:bg-(--secondary) relative">
                            <div className="absolute top-2 right-2 flex space-x-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                                <Button
                                    variant="ghost"
                                    size="icon"
                                    className="h-8 w-8 rounded-full hover:bg-(--primary)/10 hover:text-(--primary) transition-colors duration-200 cursor-pointer"
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        setLlmToUpdate(llm);
                                        setIsUpdateDialogOpen(true);
                                    }}
                                >
                                    <Pencil className="h-4 w-4" />
                                    <span className="sr-only">Edit</span>
                                </Button>
                                <Button
                                    variant="ghost"
                                    size="icon"
                                    className="h-8 w-8 rounded-full hover:bg-(--destructive)/10 hover:text-(--destructive) transition-colors duration-200 cursor-pointer"
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        setLlmToDelete(llm);
                                        setIsDeleteDialogOpen(true);
                                    }}
                                >
                                    <Trash2 className="h-4 w-4" />
                                    <span className="sr-only">Delete</span>
                                </Button>
                            </div>
                            <CardHeader className="pb-2">
                                <div className="flex items-center justify-between">
                                    <CardTitle className="flex items-center text-lg font-semibold">
                                        <Server className="mr-2 h-5 w-5 text-(--primary)" />
                                        {llm.api_type.charAt(0).toUpperCase() +
                                            llm.api_type.slice(1)}
                                    </CardTitle>
                                    <div className="flex items-center text-xs text-(--muted-foreground)">
                                        <Calendar className="mr-1 h-3 w-3" />
                                        <span>
                                            {formatDistanceToNow(new Date(llm.created_at), {
                                                addSuffix: true,
                                            })}
                                        </span>
                                    </div>
                                </div>
                            </CardHeader>
                            <CardContent className="flex-1 px-6">
                                <div className="space-y-3">
                                    <div className="flex items-center text-sm">
                                        <Cpu className="mr-2 h-4 w-4 text-(--primary)" />
                                        <p className="font-medium">Model:</p>
                                        <p className="ml-2 text-(--muted-foreground)">
                                            {llm.model}
                                        </p>
                                    </div>
                                    <div className="flex items-center text-sm">
                                        <Key className="mr-2 h-4 w-4 text-(--primary)" />
                                        <p className="font-medium">Max Tokens:</p>
                                        <p className="ml-2 text-(--muted-foreground)">
                                            {llm.max_tokens.toLocaleString()}
                                        </p>
                                    </div>
                                </div>
                            </CardContent>
                            <CardFooter className="pt-2 border-t bg-(--muted)/10 pb-4 mt-auto">
                                <div className="w-full flex flex-col space-y-3 xl:flex-row xl:justify-between xl:items-center xl:space-y-0">
                                    <Badge
                                        variant="outline"
                                        className="bg-(--primary)/10 text-(--primary) border-(--primary)/20 w-fit"
                                    >
                                        {llm.model}
                                    </Badge>
                                    <div className="flex space-x-2 w-full xl:w-auto">
                                        <Button
                                            variant="outline"
                                            size="sm"
                                            className="h-8 text-xs font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--border) bg-(--background) text-(--primary) hover:bg-(--primary)/10 cursor-pointer flex-1 xl:flex-initial"
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                setLlmToUpdate(llm);
                                                setIsUpdateDialogOpen(true);
                                            }}
                                        >
                                            <span className="relative z-10 flex items-center justify-center w-full">
                                                <Pencil className="mr-1 h-3 w-3" />
                                                Update
                                            </span>
                                            <span className="absolute inset-0 bg-(--primary)/10 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                                        </Button>
                                        <Button
                                            variant="outline"
                                            size="sm"
                                            className="h-8 text-xs font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--border) bg-(--background) text-(--destructive) hover:bg-(--destructive)/10 cursor-pointer flex-1 xl:flex-initial"
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                setLlmToDelete(llm);
                                                setIsDeleteDialogOpen(true);
                                            }}
                                        >
                                            <span className="relative z-10 flex items-center justify-center w-full">
                                                <Trash2 className="mr-1 h-3 w-3" />
                                                Delete
                                            </span>
                                            <span className="absolute inset-0 bg-(--destructive)/10 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                                        </Button>
                                    </div>
                                </div>
                            </CardFooter>
                        </Card>
                    </motion.div>
                ))}

                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3, delay: 0.1 * llms.length }}
                    whileHover={{ y: -5, transition: { duration: 0.2 } }}
                    className="h-full"
                >
                    <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                        <DialogTrigger asChild>
                            <Card className="h-full flex flex-col justify-center items-center p-6 cursor-pointer border border-dashed border-(--primary) bg-(--card) hover:bg-(--primary)/5 transition-all duration-300 group">
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
                            name="api_type"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>API Type</FormLabel>
                                    <Select
                                        onValueChange={(value) => handleApiTypeChange(value)}
                                        defaultValue={field.value}
                                    >
                                        <FormControl>
                                            <SelectTrigger className="bg-(--secondary) w-full">
                                                <SelectValue placeholder="Select API type" />
                                            </SelectTrigger>
                                        </FormControl>
                                        <SelectContent className="bg-(--background)">
                                            {apiTypes.map((type) => (
                                                <SelectItem
                                                    key={type}
                                                    value={type}
                                                    className="hover:bg-(--secondary) focus:bg-(--secondary)"
                                                >
                                                    {type.charAt(0).toUpperCase() + type.slice(1)}
                                                </SelectItem>
                                            ))}
                                        </SelectContent>
                                    </Select>
                                </FormItem>
                            )}
                        />

                        <FormField
                            control={form.control}
                            name="model"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Model</FormLabel>
                                    <Select
                                        onValueChange={field.onChange}
                                        defaultValue={field.value}
                                        disabled={!selectedApiType || isLoadingModels}
                                    >
                                        <FormControl>
                                            <SelectTrigger className="bg-(--secondary) w-full">
                                                <SelectValue
                                                    placeholder={
                                                        isLoadingModels
                                                            ? "Loading models..."
                                                            : "Select model"
                                                    }
                                                />
                                            </SelectTrigger>
                                        </FormControl>
                                        <SelectContent className="bg-(--background)">
                                            {models.map((model) => (
                                                <SelectItem
                                                    key={model.id}
                                                    value={model.id}
                                                    className="hover:bg-(--secondary) focus:bg-(--secondary)"
                                                >
                                                    {model.name}
                                                </SelectItem>
                                            ))}
                                        </SelectContent>
                                    </Select>
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
                            // Reset the delete state when dialog is closed
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
                            // Reset the update state when dialog is closed
                            setTimeout(() => setLlmToUpdate(null), 300);
                        }
                    }}
                    onUpdateSuccess={fetchLLMs}
                />
            )}
        </>
    );
}
