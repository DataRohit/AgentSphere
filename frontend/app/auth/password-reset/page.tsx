"use client";

import { Navbar } from "@/components/navbar";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Form, FormControl, FormItem, FormLabel } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import { motion } from "framer-motion";
import Cookies from "js-cookie";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";

interface PasswordResetFormValues {
    email: string;
}

export default function PasswordResetPage() {
    const router = useRouter();
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [progress, setProgress] = useState(0);

    // Check if user is already logged in
    useEffect(() => {
        const accessToken = Cookies.get("access_token");
        if (accessToken) {
            // User is already logged in, redirect to dashboard
            router.push("/dashboard");
        }
    }, [router]);

    // Reset progress when not submitting
    useEffect(() => {
        if (!isSubmitting) {
            setProgress(0);
        }
    }, [isSubmitting]);

    // Simulate progress when submitting
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

    const form = useForm<PasswordResetFormValues>({
        mode: "onTouched",
        defaultValues: {
            email: "",
        },
    });

    const onSubmit = async (data: PasswordResetFormValues) => {
        setIsSubmitting(true);
        try {
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || "/api/v1";
            const response = await fetch(`${apiUrl}/users/password-reset/`, {
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
                // Set progress to 100% on success
                setProgress(100);

                toast.success("Password reset email sent successfully!", {
                    style: {
                        backgroundColor: "oklch(0.45 0.18 142.71)",
                        color: "white",
                        border: "none",
                    },
                });

                // Redirect to login page after a short delay
                setTimeout(() => {
                    router.push("/auth/login");
                }, 2000);
            } else {
                if (result.errors) {
                    // Handle field errors
                    if (result.errors.email && result.errors.email.length > 0) {
                        toast.error(`Email: ${result.errors.email[0]}`, {
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
                        toast.error("Failed to send password reset email. Please try again.", {
                            style: {
                                backgroundColor: "var(--destructive)",
                                color: "white",
                                border: "none",
                            },
                        });
                    }
                } else {
                    toast.error("Failed to send password reset email. Please try again.", {
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
                                <div className="flex items-center mb-2">
                                    <Link
                                        href="/auth/login"
                                        className="text-(--muted-foreground) hover:text-(--primary) transition-colors duration-200 mr-2"
                                    >
                                        <ArrowLeft size={18} />
                                    </Link>
                                    <CardTitle className="text-2xl font-bold text-center flex-1 pr-6">
                                        Reset Password
                                    </CardTitle>
                                </div>
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
                                        onSubmit={form.handleSubmit(onSubmit)}
                                        className="space-y-4"
                                    >
                                        <motion.div variants={itemVariants}>
                                            <p className="text-sm text-(--muted-foreground) mb-4">
                                                Enter your email address below and we'll send you a
                                                link to reset your password.
                                            </p>
                                            <FormItem>
                                                <FormLabel>Email</FormLabel>
                                                <FormControl>
                                                    <Input
                                                        className="bg-(--secondary)"
                                                        type="email"
                                                        placeholder="Email"
                                                        {...form.register("email", {
                                                            required: true,
                                                            pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                                                        })}
                                                    />
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
                                                            ? "Sending..."
                                                            : "Send Reset Link"}
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
