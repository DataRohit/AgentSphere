"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import Cookies from "js-cookie";
import { Loader2, Mail, User } from "lucide-react";
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Organization } from "./organization-card";

const emailSchema = z.object({
    email: z.string().email("Please enter a valid email address"),
});

const usernameSchema = z.object({
    username: z.string().min(3, "Username must be at least 3 characters"),
});

type EmailFormValues = z.infer<typeof emailSchema>;
type UsernameFormValues = z.infer<typeof usernameSchema>;

interface AddMemberModalProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    organizationId: string;
    onMemberAdded: (organization: Organization) => void;
}

export function AddMemberModal({
    open,
    onOpenChange,
    organizationId,
    onMemberAdded,
}: AddMemberModalProps) {
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [activeTab, setActiveTab] = useState<"email" | "username">("email");

    const emailForm = useForm<EmailFormValues>({
        resolver: zodResolver(emailSchema),
        defaultValues: {
            email: "",
        },
    });

    const usernameForm = useForm<UsernameFormValues>({
        resolver: zodResolver(usernameSchema),
        defaultValues: {
            username: "",
        },
    });

    const onSubmitEmail = async (data: EmailFormValues) => {
        await handleSubmit(data);
    };

    const onSubmitUsername = async (data: UsernameFormValues) => {
        await handleSubmit(data);
    };

    const handleSubmit = async (data: EmailFormValues | UsernameFormValues) => {
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

            const response = await fetch(
                `http://localhost:8080/api/v1/organizations/${organizationId}/members/add/`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${accessToken}`,
                    },
                    body: JSON.stringify(data),
                }
            );

            const result = await response.json();

            if (response.ok) {
                toast.success("Member added successfully", {
                    style: {
                        backgroundColor: "oklch(0.45 0.18 142.71)",
                        color: "white",
                        border: "none",
                    },
                });

                emailForm.reset();
                usernameForm.reset();

                onOpenChange(false);

                onMemberAdded(result.organization);
            } else {
                if (result.errors) {
                    Object.entries(result.errors).forEach(([field, errors]) => {
                        if (Array.isArray(errors) && errors.length > 0) {
                            if (field === "non_field_errors") {
                                toast.error(errors[0], {
                                    style: {
                                        backgroundColor: "var(--destructive)",
                                        color: "white",
                                        border: "none",
                                    },
                                });
                            } else if (activeTab === "email" && field === "email") {
                                emailForm.setError("email", {
                                    type: "manual",
                                    message: errors[0],
                                });
                            } else if (activeTab === "username" && field === "username") {
                                usernameForm.setError("username", {
                                    type: "manual",
                                    message: errors[0],
                                });
                            } else {
                                toast.error(`${field}: ${errors[0]}`, {
                                    style: {
                                        backgroundColor: "var(--destructive)",
                                        color: "white",
                                        border: "none",
                                    },
                                });
                            }
                        }
                    });
                } else if (result.error) {
                    toast.error(result.error, {
                        style: {
                            backgroundColor: "var(--destructive)",
                            color: "white",
                            border: "none",
                        },
                    });
                } else {
                    toast.error("Failed to add member", {
                        style: {
                            backgroundColor: "var(--destructive)",
                            color: "white",
                            border: "none",
                        },
                    });
                }
            }
        } catch {
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
                    <DialogTitle className="pb-2">Add Member to Organization</DialogTitle>
                    <DialogDescription>
                        Invite a user to join your organization by email or username.
                    </DialogDescription>
                </DialogHeader>

                <Tabs
                    defaultValue="email"
                    value={activeTab}
                    onValueChange={(value) => setActiveTab(value as "email" | "username")}
                    className="w-full"
                >
                    <TabsList className="flex w-full gap-1 bg-(--card) p-0.5 rounded-lg overflow-hidden h-10">
                        <TabsTrigger
                            value="email"
                            className="flex-1 data-[state=active]:bg-(--primary) data-[state=active]:text-(--primary-foreground) data-[state=active]:shadow-sm transition-all duration-200 hover:bg-(--accent) data-[state=active]:hover:bg-(--primary) rounded-md cursor-pointer flex items-center justify-center py-1.5 px-2 m-0 h-9 w-full"
                        >
                            <div className="flex items-center">
                                <Mail className="mr-2 h-4 w-4" />
                                <span>Email</span>
                            </div>
                        </TabsTrigger>
                        <TabsTrigger
                            value="username"
                            className="flex-1 data-[state=active]:bg-(--primary) data-[state=active]:text-(--primary-foreground) data-[state=active]:shadow-sm transition-all duration-200 hover:bg-(--accent) data-[state=active]:hover:bg-(--primary) rounded-md cursor-pointer flex items-center justify-center py-1.5 px-2 m-0 h-9 w-full"
                        >
                            <div className="flex items-center">
                                <User className="mr-2 h-4 w-4" />
                                <span>Username</span>
                            </div>
                        </TabsTrigger>
                    </TabsList>

                    <TabsContent value="email" className="mt-4">
                        <Form {...emailForm}>
                            <form
                                onSubmit={emailForm.handleSubmit(onSubmitEmail)}
                                className="space-y-6"
                            >
                                <FormField
                                    control={emailForm.control}
                                    name="email"
                                    render={({ field }) => (
                                        <FormItem>
                                            <FormLabel>Email</FormLabel>
                                            <FormControl>
                                                <Input
                                                    placeholder="user@example.com"
                                                    type="email"
                                                    {...field}
                                                    className="bg-(--secondary)"
                                                />
                                            </FormControl>
                                            <FormDescription>
                                                Enter the email address of the user you want to add.
                                            </FormDescription>
                                            <FormMessage />
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
                                                    Adding...
                                                </>
                                            ) : (
                                                "Add Member"
                                            )}
                                        </span>
                                        <span className="absolute inset-0 bg-(--primary-foreground)/10 dark:bg-(--primary-foreground)/20 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                                    </Button>
                                </DialogFooter>
                            </form>
                        </Form>
                    </TabsContent>

                    <TabsContent value="username" className="mt-4">
                        <Form {...usernameForm}>
                            <form
                                onSubmit={usernameForm.handleSubmit(onSubmitUsername)}
                                className="space-y-6"
                            >
                                <FormField
                                    control={usernameForm.control}
                                    name="username"
                                    render={({ field }) => (
                                        <FormItem>
                                            <FormLabel>Username</FormLabel>
                                            <FormControl>
                                                <Input
                                                    placeholder="username"
                                                    {...field}
                                                    className="bg-(--secondary)"
                                                />
                                            </FormControl>
                                            <FormDescription>
                                                Enter the username of the user you want to add.
                                            </FormDescription>
                                            <FormMessage />
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
                                                    Adding...
                                                </>
                                            ) : (
                                                "Add Member"
                                            )}
                                        </span>
                                        <span className="absolute inset-0 bg-(--primary-foreground)/10 dark:bg-(--primary-foreground)/20 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                                    </Button>
                                </DialogFooter>
                            </form>
                        </Form>
                    </TabsContent>
                </Tabs>
            </DialogContent>
        </Dialog>
    );
}
