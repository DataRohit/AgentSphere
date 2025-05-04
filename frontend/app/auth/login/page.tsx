"use client";

import { useAppDispatch } from "@/app/store/hooks";
import { setUser, setUserError, setUserLoading } from "@/app/store/slices/userSlice";
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
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";

interface LoginFormValues {
    email: string;
    password: string;
}

export default function LoginPage() {
    const router = useRouter();
    const dispatch = useAppDispatch();
    const [showPassword, setShowPassword] = useState(false);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [progress, setProgress] = useState(0);

    useEffect(() => {
        const accessToken = Cookies.get("access_token");
        if (accessToken) {
            router.push("/dashboard");
        }
    }, [router]);

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

    const form = useForm<LoginFormValues>({
        mode: "onTouched",
        defaultValues: {
            email: "",
            password: "",
        },
    });

    const fetchUserData = async (accessToken: string) => {
        dispatch(setUserLoading());
        try {
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || "/api/v1";
            const response = await fetch(`${apiUrl}/users/me/`, {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${accessToken}`,
                },
            });

            if (response.ok) {
                const data = await response.json();
                dispatch(setUser(data.user));
            } else {
                const errorData = await response.json();
                dispatch(setUserError(errorData.error || "Failed to fetch user data"));
            }
        } catch (error) {
            dispatch(setUserError("An error occurred while fetching user data"));
        }
    };

    const onSubmit = async (data: LoginFormValues) => {
        setIsSubmitting(true);
        try {
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || "/api/v1";
            const response = await fetch(`${apiUrl}/users/login/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(data),
                credentials: "include",
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
                return;
            }

            if (response.ok) {
                setProgress(100);

                Cookies.set("access_token", result.access, { expires: 0.25 });
                Cookies.set("refresh_token", result.refresh, { expires: 1 });

                await fetchUserData(result.access);

                toast.success("Login successful!", {
                    style: {
                        backgroundColor: "oklch(0.45 0.18 142.71)",
                        color: "white",
                        border: "none",
                    },
                });

                setTimeout(() => {
                    router.push("/dashboard");
                }, 1000);
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
                    toast.error("Invalid email or password. Please try again.", {
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
                                    Log In
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
                                        onSubmit={form.handleSubmit(onSubmit)}
                                        className="space-y-4"
                                    >
                                        <motion.div variants={itemVariants}>
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

                                        <motion.div variants={itemVariants}>
                                            <FormItem>
                                                <FormLabel>Password</FormLabel>
                                                <FormControl>
                                                    <div className="relative">
                                                        <Input
                                                            className="bg-(--secondary)"
                                                            type={
                                                                showPassword ? "text" : "password"
                                                            }
                                                            placeholder="Password"
                                                            {...form.register("password", {
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

                                        <motion.div
                                            variants={itemVariants}
                                            className="flex justify-end"
                                        >
                                            <Link
                                                href="/auth/password-reset"
                                                className="text-sm text-(--muted-foreground) hover:text-(--primary) transition-colors duration-200"
                                            >
                                                Forgot Password?
                                            </Link>
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
                                                        {isSubmitting ? "Logging in..." : "Log In"}
                                                    </span>
                                                    <span className="absolute inset-0 bg-(--primary-foreground)/10 dark:bg-(--primary-foreground)/20 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                                                </Button>
                                            </motion.div>
                                        </motion.div>

                                        <motion.div
                                            variants={itemVariants}
                                            className="text-center text-sm text-(--muted-foreground) mt-4"
                                        >
                                            Don&apos;t have an account?{" "}
                                            <Link
                                                href="/auth/signup"
                                                className="text-(--primary) hover:underline"
                                            >
                                                Sign Up
                                            </Link>
                                        </motion.div>

                                        <motion.div
                                            variants={itemVariants}
                                            className="text-center text-sm text-(--muted-foreground) mt-2"
                                        >
                                            Account deactivated?{" "}
                                            <Link
                                                href="/auth/reactivate-request"
                                                className="text-(--primary) hover:underline"
                                            >
                                                Reactivate Account
                                            </Link>
                                        </motion.div>

                                        <motion.div
                                            variants={itemVariants}
                                            className="text-center text-sm text-(--muted-foreground) mt-2"
                                        >
                                            Need activation link?{" "}
                                            <Link
                                                href="/auth/resend-activation"
                                                className="text-(--primary) hover:underline"
                                            >
                                                Resend Activation
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
