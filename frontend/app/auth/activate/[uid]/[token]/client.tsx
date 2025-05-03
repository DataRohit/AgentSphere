"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { motion } from "framer-motion";
import { CheckCircle2, Loader2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { toast } from "sonner";

interface ActivationClientProps {
    uid: string;
    token: string;
}

export default function ActivationClient({ uid, token }: ActivationClientProps) {
    const router = useRouter();
    const [isActivating, setIsActivating] = useState(true);
    const [isActivated, setIsActivated] = useState(false);
    const [error, setError] = useState("");

    useEffect(() => {
        const activateAccount = async () => {
            try {
                const apiUrl = process.env.NEXT_PUBLIC_API_URL || "/api/v1";
                const response = await fetch(`${apiUrl}/users/activate/${uid}/${token}/`, {
                    method: "GET",
                    headers: {
                        "Content-Type": "application/json",
                    },
                });

                if (response.ok) {
                    setIsActivated(true);
                    setIsActivating(false);

                    setTimeout(() => {
                        router.push("/auth/login");
                        toast.success("Account activated successfully!", {
                            style: {
                                backgroundColor: "oklch(0.45 0.18 142.71)",
                                color: "white",
                                border: "none",
                            },
                        });
                    }, 3000);
                } else {
                    const errorData = await response.json();
                    setError(
                        errorData.detail ||
                            "Failed to activate account. The link may be invalid or expired."
                    );
                    setIsActivating(false);
                }
            } catch {
                setError(
                    "An error occurred while activating your account. Please try again later."
                );
                setIsActivating(false);
            }
        };

        activateAccount();
    }, [uid, token, router]);

    return (
        <div className="flex-1 flex items-center justify-center px-4 pt-16">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="w-full max-w-md"
            >
                <Card className="border shadow-lg">
                    <CardHeader>
                        <CardTitle className="text-2xl font-bold text-center">
                            Account Activation
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="flex flex-col items-center justify-center">
                        {isActivating && (
                            <div className="flex flex-col items-center space-y-4">
                                <Loader2 className="h-16 w-16 text-(--primary) animate-spin" />
                                <p className="text-center text-(--foreground)">
                                    Activating your account...
                                </p>
                            </div>
                        )}

                        {isActivated && (
                            <motion.div
                                initial={{ scale: 0.8, opacity: 0 }}
                                animate={{ scale: 1, opacity: 1 }}
                                transition={{ duration: 0.5 }}
                                className="flex flex-col items-center space-y-4"
                            >
                                <CheckCircle2 className="h-16 w-16 text-(--primary)" />
                                <p className="text-center text-(--foreground)">
                                    Your account has been successfully activated!
                                </p>
                                <p className="text-center text-(--muted-foreground) text-sm">
                                    Redirecting to login page...
                                </p>
                            </motion.div>
                        )}

                        {error && (
                            <div className="flex flex-col items-center space-y-4">
                                <p className="text-center text-(--destructive) font-medium">
                                    {error}
                                </p>
                                <Button
                                    onClick={() => router.push("/auth/login")}
                                    className="mt-4 font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--primary) bg-(--primary) text-(--primary-foreground) dark:bg-(--primary) dark:text-(--primary-foreground) dark:border-(--primary) px-8 h-12 cursor-pointer"
                                >
                                    <span className="relative z-10">Go to Login</span>
                                    <span className="absolute inset-0 bg-(--primary-foreground)/10 dark:bg-(--primary-foreground)/20 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                                </Button>
                            </div>
                        )}
                    </CardContent>
                </Card>
            </motion.div>
        </div>
    );
}
