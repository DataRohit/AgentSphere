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
import { zodResolver } from "@hookform/resolvers/zod";
import Cookies from "js-cookie";
import { Cpu, Globe, Key, Loader2, Pencil } from "lucide-react";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";

interface LLM {
    id: string;
    base_url: string;
    model: string;
    max_tokens: number;
    created_at: string;
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

const updateLLMSchema = z.object({
    base_url: z.string().url("Base URL must be a valid URL").min(1, "Base URL is required"),
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

    const form = useForm<UpdateLLMValues>({
        resolver: zodResolver(updateLLMSchema),
        defaultValues: {
            base_url: llm.base_url,
            model: llm.model,
            api_key: "",
            max_tokens: llm.max_tokens,
        },
    });

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
                base_url: values.base_url,
                model: values.model,
                api_key: values.api_key,
                max_tokens: values.max_tokens,
            };

            const response = await fetch(
                `${process.env.NEXT_PUBLIC_API_URL}/llms/${llm.id}/update/`,
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
                base_url: llm.base_url,
                model: llm.model,
                api_key: "",
                max_tokens: llm.max_tokens,
            });
        }
    }, [open, llm, form]);

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
