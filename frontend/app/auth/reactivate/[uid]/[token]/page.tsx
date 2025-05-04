"use client";

import { Navbar } from "@/components/navbar";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Form, FormControl, FormItem, FormLabel } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import { motion } from "framer-motion";
import Cookies from "js-cookie";
import { Eye, EyeOff } from "lucide-react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";

interface ReactivateAccountConfirmFormValues {
    new_password: string;
    re_new_password: string;
}

export default function ReactivateAccountConfirmPage() {
    const router = useRouter();
    const params = useParams();
    const { uid, token } = params;

    const [showPassword, setShowPassword] = useState(false);
    const [showRePassword, setShowRePassword] = useState(false);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [progress, setProgress] = useState(0);

    useEffect(() => {
        Cookies.remove("access_token");
        Cookies.remove("refresh_token");
    }, []);

    useEffect(() => {
        if (!isSubmitting) {
            setProgress(0);
        }
    }, [isSubmitting]);

    useEffect(() => {
        if (isSubmitting) {
            const timer = setTimeout(() => {
                setProgress((oldProgress) => {
                    if (oldProgress < 95) {
                        return Math.min(oldProgress + 5, 95);
                    }
                    return oldProgress;
                });
            }, 100);

            return () => {
                clearTimeout(timer);
            };
        }
    }, [isSubmitting, progress]);

    const form = useForm<ReactivateAccountConfirmFormValues>({
        mode: "onTouched",
        defaultValues: {
            new_password: "",
            re_new_password: "",
        },
    });

    const onSubmit = async (data: ReactivateAccountConfirmFormValues) => {
        if (data.new_password !== data.re_new_password) {
            toast.error("Passwords do not match", {
                style: {
                    backgroundColor: "var(--destructive)",
                    color: "white",
                    border: "none",
                },
            });
            return;
        }

        if (data.new_password.length < 8) {
            toast.error("Password must be at least 8 characters", {
                style: {
                    backgroundColor: "var(--destructive)",
                    color: "white",
                    border: "none",
                },
            });
            return;
        }

        setIsSubmitting(true);
        try {
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || "/api/v1";
            const response = await fetch(`${apiUrl}/users/reactivate/${uid}/${token}/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(data),
            });

            let result;
            try {
                result = await response.json();
            } catch {
                toast.error("Unable to process server response. Please try again later.", {
                    style: {
                        backgroundColor: "var(--destructive)",
                        color: "white",
                        border: "none",
                    },
                });
                setIsSubmitting(false);
                return;
            }

            if (response.ok) {
                setProgress(100);

                toast.success("Account reactivated successfully!", {
                    style: {
                        backgroundColor: "oklch(0.45 0.18 142.71)",
                        color: "white",
                        border: "none",
                    },
                });

                setTimeout(() => {
                    router.push("/auth/login");
                }, 2000);
            } else {
                if (response.status === 403) {
                    toast.error(
                        result.error ||
                            "Invalid or expired reactivation link. Please request a new one.",
                        {
                            style: {
                                backgroundColor: "var(--destructive)",
                                color: "white",
                                border: "none",
                            },
                        }
                    );
                } else if (result.errors) {
                    if (result.errors.new_password && result.errors.new_password.length > 0) {
                        toast.error(`New password: ${result.errors.new_password[0]}`, {
                            style: {
                                backgroundColor: "var(--destructive)",
                                color: "white",
                                border: "none",
                            },
                        });
                    } else if (
                        result.errors.re_new_password &&
                        result.errors.re_new_password.length > 0
                    ) {
                        toast.error(`Confirm password: ${result.errors.re_new_password[0]}`, {
                            style: {
                                backgroundColor: "var(--destructive)",
                                color: "white",
                                border: "none",
                            },
                        });
                    } else if (
                        result.errors.non_field_errors &&
                        result.errors.non_field_errors.length > 0
                    ) {
                        toast.error(result.errors.non_field_errors[0], {
                            style: {
                                backgroundColor: "var(--destructive)",
                                color: "white",
                                border: "none",
                            },
                        });
                    } else {
                        toast.error("Failed to reactivate account. Please try again.", {
                            style: {
                                backgroundColor: "var(--destructive)",
                                color: "white",
                                border: "none",
                            },
                        });
                    }
                } else {
                    toast.error("Failed to reactivate account. Please try again.", {
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

    const containerVariants = {
        hidden: { opacity: 0 },
        visible: {
            opacity: 1,
            transition: {
                staggerChildren: 0.1,
            },
        },
    };

    const itemVariants = {
        hidden: { y: 20, opacity: 0 },
        visible: {
            y: 0,
            opacity: 1,
            transition: {
                type: "spring",
                stiffness: 100,
            },
        },
    };

    return (
        <div className="min-h-screen flex flex-col bg-(--background)">
            <Navbar />
            <div className="flex-1 flex items-center justify-center px-4 pt-16">
                <motion.div
                    initial="hidden"
                    animate="visible"
                    variants={containerVariants}
                    className="w-full max-w-md"
                >
                    <motion.div variants={itemVariants}>
                        <Card className="border shadow-lg">
                            <CardHeader>
                                <CardTitle className="text-2xl font-bold text-center">
                                    Reactivate Your Account
                                </CardTitle>
                                {isSubmitting && (
                                    <div className="mt-2">
                                        <Progress
                                            value={progress}
                                            className="h-1 bg-(--primary-foreground)/20"
                                        />
                                    </div>
                                )}
                            </CardHeader>
                            <CardContent>
                                <Form {...form}>
                                    <form
                                        onSubmit={(e) => {
                                            const data = form.getValues();
                                            if (data.new_password !== data.re_new_password) {
                                                e.preventDefault();
                                                toast.error("Passwords do not match", {
                                                    style: {
                                                        backgroundColor: "var(--destructive)",
                                                        color: "white",
                                                        border: "none",
                                                    },
                                                });
                                                return;
                                            }

                                            if (data.new_password.length < 8) {
                                                e.preventDefault();
                                                toast.error(
                                                    "Password must be at least 8 characters",
                                                    {
                                                        style: {
                                                            backgroundColor: "var(--destructive)",
                                                            color: "white",
                                                            border: "none",
                                                        },
                                                    }
                                                );
                                                return;
                                            }

                                            form.handleSubmit(onSubmit)(e);
                                        }}
                                        className="space-y-4"
                                    >
                                        <motion.div variants={itemVariants}>
                                            <p className="text-sm text-(--muted-foreground) mb-4">
                                                Please set a new password to reactivate your
                                                account.
                                            </p>
                                        </motion.div>

                                        <motion.div variants={itemVariants}>
                                            <FormItem>
                                                <FormLabel>New Password</FormLabel>
                                                <FormControl>
                                                    <div className="relative">
                                                        <Input
                                                            className="bg-(--secondary)"
                                                            type={
                                                                showPassword ? "text" : "password"
                                                            }
                                                            placeholder="New Password"
                                                            {...form.register("new_password", {
                                                                required: true,
                                                            })}
                                                        />
                                                        <button
                                                            type="button"
                                                            className="absolute right-2 top-1/2 -translate-y-1/2 text-(--muted-foreground) hover:text-(--primary) focus:text-(--primary) p-1.5 rounded-full hover:bg-(--accent) focus:bg-(--accent) transition-all duration-200 cursor-pointer"
                                                            tabIndex={-1}
                                                            onClick={() =>
                                                                setShowPassword((v) => !v)
                                                            }
                                                        >
                                                            {showPassword ? (
                                                                <EyeOff size={18} />
                                                            ) : (
                                                                <Eye size={18} />
                                                            )}
                                                        </button>
                                                    </div>
                                                </FormControl>
                                            </FormItem>
                                        </motion.div>

                                        <motion.div variants={itemVariants}>
                                            <FormItem>
                                                <FormLabel>Confirm New Password</FormLabel>
                                                <FormControl>
                                                    <div className="relative">
                                                        <Input
                                                            className="bg-(--secondary)"
                                                            type={
                                                                showRePassword ? "text" : "password"
                                                            }
                                                            placeholder="Confirm New Password"
                                                            {...form.register("re_new_password", {
                                                                required: true,
                                                            })}
                                                        />
                                                        <button
                                                            type="button"
                                                            className="absolute right-2 top-1/2 -translate-y-1/2 text-(--muted-foreground) hover:text-(--primary) focus:text-(--primary) p-1.5 rounded-full hover:bg-(--accent) focus:bg-(--accent) transition-all duration-200 cursor-pointer"
                                                            tabIndex={-1}
                                                            onClick={() =>
                                                                setShowRePassword((v) => !v)
                                                            }
                                                        >
                                                            {showRePassword ? (
                                                                <EyeOff size={18} />
                                                            ) : (
                                                                <Eye size={18} />
                                                            )}
                                                        </button>
                                                    </div>
                                                </FormControl>
                                            </FormItem>
                                        </motion.div>

                                        <motion.div variants={itemVariants} className="pt-2">
                                            <motion.div
                                                whileHover={{ scale: 1.02 }}
                                                whileTap={{ scale: 0.98 }}
                                                className="w-full"
                                            >
                                                <Button
                                                    type="submit"
                                                    size="lg"
                                                    className="w-full font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--primary) bg-(--primary) text-(--primary-foreground) dark:bg-(--primary) dark:text-(--primary-foreground) dark:border-(--primary) px-8 h-12 cursor-pointer"
                                                    disabled={isSubmitting}
                                                >
                                                    <span className="relative z-10">
                                                        {isSubmitting
                                                            ? "Reactivating Account..."
                                                            : "Reactivate Account"}
                                                    </span>
                                                    <span className="absolute inset-0 bg-(--primary-foreground)/10 dark:bg-(--primary-foreground)/20 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                                                </Button>
                                            </motion.div>
                                        </motion.div>

                                        <motion.div
                                            variants={itemVariants}
                                            className="text-center text-sm text-(--muted-foreground) mt-4"
                                        >
                                            Remember your password?{" "}
                                            <Link
                                                href="/auth/login"
                                                className="text-(--primary) hover:underline"
                                            >
                                                Log In
                                            </Link>
                                        </motion.div>
                                    </form>
                                </Form>
                            </CardContent>
                        </Card>
                    </motion.div>
                </motion.div>
            </div>
        </div>
    );
}
