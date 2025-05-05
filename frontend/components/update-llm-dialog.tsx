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
import { zodResolver } from "@hookform/resolvers/zod";
import Cookies from "js-cookie";
import { Key, Loader2, Pencil } from "lucide-react";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";

interface LLM {
    id: string;
    api_type: string;
    model: string;
    max_tokens: number;
    created_at: string;
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

const updateLLMSchema = z.object({
    api_type: z.string().min(1, "API type is required"),
    model: z.string().min(1, "Model is required"),
    api_key: z.string().min(1, "API key is required"),
    max_tokens: z.number().int().positive("Max tokens must be a positive number"),
});

type UpdateLLMValues = z.infer<typeof updateLLMSchema>;

interface UpdateLLMDialogProps {
    llm: LLM;
    open: boolean;
    onOpenChange: (open: boolean) => void;
    onUpdateSuccess: () => void;
}

export function UpdateLLMDialog({
    llm,
    open,
    onOpenChange,
    onUpdateSuccess,
}: UpdateLLMDialogProps) {
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [apiTypes] = useState<string[]>(["google"]);
    const [models, setModels] = useState<LLMModel[]>([]);
    const [selectedApiType, setSelectedApiType] = useState<string>(llm.api_type);
    const [isLoadingModels, setIsLoadingModels] = useState(false);

    const form = useForm<UpdateLLMValues>({
        resolver: zodResolver(updateLLMSchema),
        defaultValues: {
            api_type: llm.api_type,
            model: llm.model,
            api_key: "",
            max_tokens: llm.max_tokens,
        },
    });

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

    const onSubmit = async (values: UpdateLLMValues) => {
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
                api_type: values.api_type,
                model: values.model,
                api_key: values.api_key,
                max_tokens: values.max_tokens,
            };

            const response = await fetch(`http://localhost:8080/api/v1/llms/${llm.id}/update/`, {
                method: "PATCH",
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
                    toast.error("You do not have permission to update this LLM configuration.", {
                        style: {
                            backgroundColor: "var(--destructive)",
                            color: "white",
                            border: "none",
                        },
                    });
                } else if (response.status === 404) {
                    toast.error("LLM configuration not found.", {
                        style: {
                            backgroundColor: "var(--destructive)",
                            color: "white",
                            border: "none",
                        },
                    });
                } else {
                    throw new Error(data.error || "Failed to update LLM configuration");
                }
                return;
            }

            toast.success("LLM configuration updated successfully", {
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
                err instanceof Error
                    ? err.message
                    : "An error occurred while updating LLM configuration";
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
                api_type: llm.api_type,
                model: llm.model,
                api_key: "",
                max_tokens: llm.max_tokens,
            });
            setSelectedApiType(llm.api_type);
        }
    }, [open, llm, form]);

    useEffect(() => {
        if (open && selectedApiType) {
            fetchModels(selectedApiType);
        }
    }, [open, selectedApiType]);

    const handleApiTypeChange = (value: string) => {
        setSelectedApiType(value);
        form.setValue("api_type", value);
        form.setValue("model", "");
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[500px] bg-(--background) border-(--border) [&_[data-slot=dialog-close]]:hover:opacity-100 [&_[data-slot=dialog-close]]:cursor-pointer [&_[data-slot=dialog-close]]:transition-opacity [&_[data-slot=dialog-close]]:duration-200">
                <DialogHeader>
                    <DialogTitle className="flex items-center pb-2">
                        <Pencil className="mr-2 h-5 w-5 text-(--primary)" />
                        Update LLM Configuration
                    </DialogTitle>
                    <DialogDescription>Update your language model configuration.</DialogDescription>
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
