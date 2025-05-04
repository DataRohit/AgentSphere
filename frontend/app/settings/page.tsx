"use client";

import { clearUser } from "@/app/store/slices/userSlice";
import { DashboardNavbar } from "@/components/dashboard-navbar";
import { ProtectedRoute } from "@/components/protected-route";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Form, FormControl, FormField, FormItem, FormLabel } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { zodResolver } from "@hookform/resolvers/zod";
import { motion } from "framer-motion";
import Cookies from "js-cookie";
import { AlertCircle, Loader2, Trash2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { useDispatch } from "react-redux";
import { toast } from "sonner";
import { z } from "zod";

const deactivateAccountSchema = z
    .object({
        current_password: z.string().min(1, "Current password is required"),
        re_password: z.string().min(1, "Confirmation password is required"),
    })
    .refine((data) => data.current_password === data.re_password, {
        message: "Passwords do not match",
        path: ["re_password"],
    });

type DeactivateAccountValues = z.infer<typeof deactivateAccountSchema>;

export default function SettingsPage() {
    const router = useRouter();
    const dispatch = useDispatch();
    const [isDeactivating, setIsDeactivating] = useState(false);
    const [isDeleting, setIsDeleting] = useState(false);

    const deactivateForm = useForm<DeactivateAccountValues>({
        resolver: zodResolver(deactivateAccountSchema),
        defaultValues: {
            current_password: "",
            re_password: "",
        },
    });

    const handleDeactivateAccount = async (data: DeactivateAccountValues) => {
        setIsDeactivating(true);
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

            const apiUrl = process.env.NEXT_PUBLIC_API_URL || "/api/v1";
            const response = await fetch(`${apiUrl}/users/deactivate/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${accessToken}`,
                },
                body: JSON.stringify(data),
            });

            const result = await response.json();

            if (response.ok) {
                dispatch(clearUser());
                Cookies.remove("access_token");
                Cookies.remove("refresh_token");

                toast.success("Account deactivated successfully", {
                    style: {
                        backgroundColor: "oklch(0.45 0.18 142.71)",
                        color: "white",
                        border: "none",
                    },
                });

                router.push("/auth/login");
            } else {
                if (result.errors) {
                    Object.entries(result.errors).forEach(([field, errors]: [string, any]) => {
                        if (Array.isArray(errors) && errors.length > 0) {
                            toast.error(`${field.replace("_", " ")}: ${errors[0]}`, {
                                style: {
                                    backgroundColor: "var(--destructive)",
                                    color: "white",
                                    border: "none",
                                },
                            });
                        }
                    });
                } else if (result.non_field_errors) {
                    toast.error(result.non_field_errors[0], {
                        style: {
                            backgroundColor: "var(--destructive)",
                            color: "white",
                            border: "none",
                        },
                    });
                } else {
                    toast.error("Failed to deactivate account", {
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
            setIsDeactivating(false);
        }
    };

    const handleDeleteAccount = async () => {
        setIsDeleting(true);
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

            const apiUrl = process.env.NEXT_PUBLIC_API_URL || "/api/v1";
            const response = await fetch(`${apiUrl}/users/delete/`, {
                method: "DELETE",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${accessToken}`,
                },
            });

            const result = await response.json();

            if (response.ok) {
                toast.success("Account deletion email sent successfully", {
                    style: {
                        backgroundColor: "oklch(0.45 0.18 142.71)",
                        color: "white",
                        border: "none",
                    },
                });
            } else {
                if (result.error) {
                    toast.error(result.error, {
                        style: {
                            backgroundColor: "var(--destructive)",
                            color: "white",
                            border: "none",
                        },
                    });
                } else {
                    toast.error("Failed to send account deletion email", {
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
            setIsDeleting(false);
        }
    };

    return (
        <ProtectedRoute>
            <div className="min-h-screen flex flex-col bg-(--background)">
                <DashboardNavbar />
                <div className="flex-1 container mx-auto px-4 pt-24 pb-8">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5 }}
                    >
                        <div className="grid gap-8">
                            <div className="flex items-center justify-between">
                                <div>
                                    <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
                                    <p className="text-(--muted-foreground)">
                                        Manage your account settings and preferences.
                                    </p>
                                </div>
                            </div>

                            <Tabs defaultValue="danger" className="w-full">
                                <TabsList className="flex w-full md:w-[600px] gap-1 bg-(--card) p-0.5 rounded-lg overflow-hidden h-10">
                                    <TabsTrigger
                                        value="danger"
                                        className="flex-1 data-[state=active]:bg-(--destructive) data-[state=active]:text-white data-[state=active]:shadow-sm transition-all duration-200 hover:bg-(--destructive)/10 hover:text-(--destructive) data-[state=active]:hover:bg-(--destructive) rounded-md cursor-pointer flex items-center justify-center py-1.5 px-2 m-0 h-9"
                                    >
                                        <div className="flex items-center">
                                            <AlertCircle className="mr-2 h-4 w-4" />
                                            <span>Danger Zone</span>
                                        </div>
                                    </TabsTrigger>
                                </TabsList>

                                <TabsContent
                                    value="danger"
                                    className="mt-6 data-[state=active]:animate-in data-[state=inactive]:animate-out data-[state=inactive]:fade-out-50 data-[state=active]:fade-in-50 duration-200"
                                >
                                    <div className="space-y-6">
                                        <motion.div
                                            initial={{ opacity: 0, y: 20 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            transition={{
                                                type: "spring",
                                                stiffness: 300,
                                                damping: 30,
                                                delay: 0.1,
                                            }}
                                        >
                                            <Card className="gap-0 overflow-hidden border border-(--destructive)/20 shadow-sm hover:shadow-md transition-shadow duration-300">
                                                <motion.div
                                                    initial={{ opacity: 0, y: 10 }}
                                                    animate={{ opacity: 1, y: 0 }}
                                                    transition={{ delay: 0.2, duration: 0.3 }}
                                                >
                                                    <CardHeader>
                                                        <CardTitle className="text-(--destructive) flex items-center">
                                                            <AlertCircle className="mr-2 h-5 w-5" />
                                                            Account Deactivation
                                                        </CardTitle>
                                                    </CardHeader>
                                                </motion.div>
                                                <motion.div
                                                    initial={{ opacity: 0 }}
                                                    animate={{ opacity: 1 }}
                                                    transition={{ delay: 0.3, duration: 0.4 }}
                                                >
                                                    <CardContent className="pt-6">
                                                        <div>
                                                            <p className="text-sm text-(--muted-foreground) mb-4">
                                                                Your account will be deactivated and
                                                                you won't be able to access the
                                                                platform. This deactivation is
                                                                temporary and your account can be
                                                                reactivated in the future.
                                                            </p>

                                                            <Form {...deactivateForm}>
                                                                <form
                                                                    onSubmit={deactivateForm.handleSubmit(
                                                                        handleDeactivateAccount
                                                                    )}
                                                                    className="space-y-4"
                                                                >
                                                                    <FormField
                                                                        control={
                                                                            deactivateForm.control
                                                                        }
                                                                        name="current_password"
                                                                        render={({ field }) => (
                                                                            <FormItem>
                                                                                <FormLabel>
                                                                                    Current Password
                                                                                </FormLabel>
                                                                                <FormControl>
                                                                                    <Input
                                                                                        placeholder="Enter your current password"
                                                                                        {...field}
                                                                                        className="border-(--border) focus-visible:ring-(--destructive)/20 bg-(--secondary)"
                                                                                    />
                                                                                </FormControl>
                                                                            </FormItem>
                                                                        )}
                                                                    />

                                                                    <FormField
                                                                        control={
                                                                            deactivateForm.control
                                                                        }
                                                                        name="re_password"
                                                                        render={({ field }) => (
                                                                            <FormItem>
                                                                                <FormLabel>
                                                                                    Confirm Password
                                                                                </FormLabel>
                                                                                <FormControl>
                                                                                    <Input
                                                                                        type="password"
                                                                                        placeholder="Confirm your password"
                                                                                        {...field}
                                                                                        className="border-(--border) focus-visible:ring-(--destructive)/20 bg-(--secondary)"
                                                                                    />
                                                                                </FormControl>
                                                                            </FormItem>
                                                                        )}
                                                                    />

                                                                    <motion.div
                                                                        initial={{
                                                                            opacity: 0,
                                                                            y: 10,
                                                                        }}
                                                                        animate={{
                                                                            opacity: 1,
                                                                            y: 0,
                                                                        }}
                                                                        transition={{
                                                                            delay: 0.6,
                                                                            duration: 0.3,
                                                                        }}
                                                                        whileHover={{ scale: 1.02 }}
                                                                        whileTap={{ scale: 0.98 }}
                                                                        className="pt-2"
                                                                    >
                                                                        <Button
                                                                            type="submit"
                                                                            disabled={
                                                                                isDeactivating
                                                                            }
                                                                            className="font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--destructive) bg-(--destructive) text-white hover:bg-(--destructive)/90 px-8 h-12 cursor-pointer w-full"
                                                                        >
                                                                            <span className="relative z-10 flex items-center justify-center">
                                                                                {isDeactivating ? (
                                                                                    <>
                                                                                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                                                                        Deactivating...
                                                                                    </>
                                                                                ) : (
                                                                                    <>
                                                                                        <AlertCircle className="mr-2 h-4 w-4" />
                                                                                        Deactivate
                                                                                        Account
                                                                                    </>
                                                                                )}
                                                                            </span>
                                                                            <span className="absolute inset-0 bg-white/10 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                                                                        </Button>
                                                                    </motion.div>
                                                                </form>
                                                            </Form>
                                                        </div>
                                                    </CardContent>
                                                </motion.div>
                                            </Card>
                                        </motion.div>

                                        <motion.div
                                            initial={{ opacity: 0, y: 20 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            transition={{
                                                type: "spring",
                                                stiffness: 300,
                                                damping: 30,
                                                delay: 0.3,
                                            }}
                                        >
                                            <Card className="gap-0 overflow-hidden border border-(--destructive)/20 shadow-sm hover:shadow-md transition-shadow duration-300">
                                                <motion.div
                                                    initial={{ opacity: 0, y: 10 }}
                                                    animate={{ opacity: 1, y: 0 }}
                                                    transition={{ delay: 0.4, duration: 0.3 }}
                                                >
                                                    <CardHeader>
                                                        <CardTitle className="text-(--destructive) flex items-center">
                                                            <Trash2 className="mr-2 h-5 w-5" />
                                                            Account Deletion
                                                        </CardTitle>
                                                    </CardHeader>
                                                </motion.div>
                                                <motion.div
                                                    initial={{ opacity: 0 }}
                                                    animate={{ opacity: 1 }}
                                                    transition={{ delay: 0.5, duration: 0.4 }}
                                                >
                                                    <CardContent className="pt-6">
                                                        <div className="space-y-4">
                                                            <p className="text-sm text-(--muted-foreground)">
                                                                This action will permanently delete
                                                                your account and all associated
                                                                data. This cannot be undone. We will
                                                                send you an email with a
                                                                confirmation link to verify this
                                                                request.
                                                            </p>

                                                            <motion.div
                                                                initial={{ opacity: 0, y: 10 }}
                                                                animate={{ opacity: 1, y: 0 }}
                                                                transition={{
                                                                    delay: 0.7,
                                                                    duration: 0.3,
                                                                }}
                                                                whileHover={{ scale: 1.02 }}
                                                                whileTap={{ scale: 0.98 }}
                                                                className="pt-2"
                                                            >
                                                                <Button
                                                                    type="button"
                                                                    onClick={handleDeleteAccount}
                                                                    disabled={isDeleting}
                                                                    className="font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--destructive) bg-(--destructive) text-white hover:bg-(--destructive)/90 px-8 h-12 cursor-pointer w-full"
                                                                >
                                                                    <span className="relative z-10 flex items-center justify-center">
                                                                        {isDeleting ? (
                                                                            <>
                                                                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                                                                Sending Request...
                                                                            </>
                                                                        ) : (
                                                                            <>
                                                                                <Trash2 className="mr-2 h-4 w-4" />
                                                                                Delete Account
                                                                            </>
                                                                        )}
                                                                    </span>
                                                                    <span className="absolute inset-0 bg-white/10 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                                                                </Button>
                                                            </motion.div>
                                                        </div>
                                                    </CardContent>
                                                </motion.div>
                                            </Card>
                                        </motion.div>
                                    </div>
                                </TabsContent>
                            </Tabs>
                        </div>
                    </motion.div>
                </div>
            </div>
        </ProtectedRoute>
    );
}
