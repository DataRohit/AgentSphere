"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import Cookies from "js-cookie";
import { Loader2 } from "lucide-react";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";

import { Button } from "@/components/ui/button";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
import {
    Form,
    FormControl,
    FormDescription,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Organization } from "./organization-card";

const organizationFormSchema = z.object({
    name: z
        .string()
        .min(3, "Name must be at least 3 characters")
        .max(100, "Name must be less than 100 characters"),
    description: z.string().max(500, "Description must be less than 500 characters").optional(),
    website: z
        .string()
        .url("Please enter a valid URL")
        .max(200, "Website URL must be less than 200 characters")
        .optional()
        .or(z.literal("")),
});

type OrganizationFormValues = z.infer<typeof organizationFormSchema>;

interface CreateOrganizationModalProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    onOrganizationCreated: (organization: Organization) => void;
}

export function CreateOrganizationModal({
    open,
    onOpenChange,
    onOrganizationCreated,
}: CreateOrganizationModalProps) {
    const [isSubmitting, setIsSubmitting] = useState(false);

    const form = useForm<OrganizationFormValues>({
        resolver: zodResolver(organizationFormSchema),
        defaultValues: {
            name: "",
            description: "",
            website: "",
        },
    });

    const onSubmit = async (data: OrganizationFormValues) => {
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
                name: data.name,
                description: data.description || undefined,
                website: data.website || undefined,
            };

            const response = await fetch("http://localhost:8080/api/v1/organizations/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${accessToken}`,
                },
                body: JSON.stringify(payload),
            });

            const result = await response.json();

            if (response.ok) {
                toast.success("Organization created successfully", {
                    style: {
                        backgroundColor: "oklch(0.45 0.18 142.71)",
                        color: "white",
                        border: "none",
                    },
                });

                form.reset();

                onOpenChange(false);

                onOrganizationCreated(result.organization);
            } else {
                if (result.errors) {
                    Object.entries(result.errors).forEach(([field, errors]: [string, any]) => {
                        if (Array.isArray(errors) && errors.length > 0) {
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
                } else {
                    toast.error("Failed to create organization", {
                        style: {
                            backgroundColor: "var(--destructive)",
                            color: "white",
                            border: "none",
                        },
                    });
                }
            }
        } catch (error) {
            toast.error("An error occurred. Please try again later.", {
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
            <DialogContent className="sm:max-w-[500px] bg-(--background) border-(--border) [&_[data-slot=dialog-close]]:hover:opacity-100 [&_[data-slot=dialog-close]]:cursor-pointer [&_[data-slot=dialog-close]]:transition-opacity [&_[data-slot=dialog-close]]:duration-200">
                <DialogHeader>
                    <DialogTitle>Create New Organization</DialogTitle>
                    <DialogDescription>
                        Create an organization to collaborate with others on projects.
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
                                        <Input placeholder="My Organization" {...field} />
                                    </FormControl>
                                    <FormDescription>
                                        This is your organization's display name.
                                    </FormDescription>
                                    <FormMessage />
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
                                            placeholder="Describe your organization..."
                                            className="resize-none"
                                            {...field}
                                        />
                                    </FormControl>
                                    <FormDescription>
                                        A brief description of your organization.
                                    </FormDescription>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <FormField
                            control={form.control}
                            name="website"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Website</FormLabel>
                                    <FormControl>
                                        <Input placeholder="https://example.com" {...field} />
                                    </FormControl>
                                    <FormDescription>
                                        Your organization's website (optional).
                                    </FormDescription>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <DialogFooter>
                            <Button
                                type="button"
                                variant="outline"
                                onClick={() => onOpenChange(false)}
                                disabled={isSubmitting}
                                className="font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--border) bg-(--background) text-(--foreground) hover:bg-(--muted) px-6 h-10 cursor-pointer"
                            >
                                <span className="relative z-10">Cancel</span>
                                <span className="absolute inset-0 bg-(--muted)/50 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                            </Button>
                            <Button
                                type="submit"
                                disabled={isSubmitting}
                                className="font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--primary) bg-(--primary) text-(--primary-foreground) dark:bg-(--primary) dark:text-(--primary-foreground) dark:border-(--primary) px-6 h-10 cursor-pointer"
                            >
                                <span className="relative z-10">
                                    {isSubmitting ? (
                                        <>
                                            <Loader2 className="mr-2 h-4 w-4 animate-spin inline" />
                                            Creating...
                                        </>
                                    ) : (
                                        "Create Organization"
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
