"use client";

import { Navbar } from "@/components/navbar";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { motion } from "framer-motion";
import Cookies from "js-cookie";
import { AlertCircle, ArrowLeft, Loader2, Trash2 } from "lucide-react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { toast } from "sonner";

export default function AccountDeletionConfirmPage() {
    const router = useRouter();
    const params = useParams();
    const { uid, token } = params;

    const [isDeleting, setIsDeleting] = useState(false);
    const [isCancelling, setIsCancelling] = useState(false);

    useEffect(() => {
        Cookies.remove("access_token");
        Cookies.remove("refresh_token");
    }, []);

    const handleDeleteAccount = async () => {
        setIsDeleting(true);
        try {
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || "/api/v1";
            const response = await fetch(`${apiUrl}/users/delete/${uid}/${token}/`, {
                method: "DELETE",
                headers: {
                    "Content-Type": "application/json",
                },
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
                setIsDeleting(false);
                return;
            }

            if (response.ok) {
                toast.success("Account deleted successfully", {
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
                            "Invalid or expired deletion link. Please request a new one.",
                        {
                            style: {
                                backgroundColor: "var(--destructive)",
                                color: "white",
                                border: "none",
                            },
                        }
                    );
                } else {
                    toast.error("Failed to delete account. Please try again.", {
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
            setIsDeleting(false);
        }
    };

    const handleCancelDeletion = () => {
        setIsCancelling(true);
        toast.success("Account deletion cancelled", {
            style: {
                backgroundColor: "oklch(0.45 0.18 142.71)",
                color: "white",
                border: "none",
            },
        });

        setTimeout(() => {
            router.push("/auth/login");
        }, 1500);
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
        <div className="min-h-screen flex flex-col  bg-(--background)">
            <Navbar />
            <div className="flex-1 flex items-center justify-center px-4 pt-16">
                <motion.div
                    initial="hidden"
                    animate="visible"
                    variants={containerVariants}
                    className="w-full max-w-md"
                >
                    <motion.div variants={itemVariants}>
                        <Card className="gap-0 border border-(--destructive)/20 shadow-lg">
                            <CardHeader>
                                <div className="flex items-center mb-2">
                                    <Link
                                        href="/auth/login"
                                        className="text-(--muted-foreground) hover:text-(--primary) transition-colors duration-200 mr-2"
                                    >
                                        <ArrowLeft size={18} />
                                    </Link>
                                    <CardTitle className="text-2xl font-bold text-center flex-1 pr-6 text-(--destructive)">
                                        <div className="flex items-center justify-center">
                                            <AlertCircle className="mr-2 h-6 w-6" />
                                            Delete Account
                                        </div>
                                    </CardTitle>
                                </div>
                            </CardHeader>
                            <CardContent className="pt-6">
                                <motion.div variants={itemVariants}>
                                    <div className="space-y-6">
                                        <div className="bg-(--destructive)/10 p-4 rounded-md border border-(--destructive)/20">
                                            <p className="text-sm font-medium text-(--destructive)">
                                                Warning: This action cannot be undone
                                            </p>
                                            <p className="text-sm text-(--muted-foreground) mt-2">
                                                You are about to permanently delete your account and
                                                all associated data. This action is irreversible.
                                            </p>
                                        </div>

                                        <div className="flex flex-col space-y-3">
                                            <motion.div
                                                whileHover={{ scale: 1.02 }}
                                                whileTap={{ scale: 0.98 }}
                                                className="w-full"
                                            >
                                                <Button
                                                    type="button"
                                                    onClick={handleDeleteAccount}
                                                    disabled={isDeleting}
                                                    className="w-full font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--destructive) bg-(--destructive) text-white hover:bg-(--destructive)/90 px-8 h-12 cursor-pointer"
                                                >
                                                    <span className="relative z-10 flex items-center justify-center">
                                                        {isDeleting ? (
                                                            <>
                                                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                                                Deleting Account...
                                                            </>
                                                        ) : (
                                                            <>
                                                                <Trash2 className="mr-2 h-4 w-4" />
                                                                Confirm Deletion
                                                            </>
                                                        )}
                                                    </span>
                                                    <span className="absolute inset-0 bg-white/10 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                                                </Button>
                                            </motion.div>

                                            <motion.div
                                                whileHover={{ scale: 1.02 }}
                                                whileTap={{ scale: 0.98 }}
                                                className="w-full"
                                            >
                                                <Button
                                                    type="button"
                                                    onClick={handleCancelDeletion}
                                                    disabled={isCancelling || isDeleting}
                                                    variant="outline"
                                                    className="w-full font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--border) bg-(--background) hover:bg-(--accent) px-8 h-12 cursor-pointer"
                                                >
                                                    <span className="relative z-10">
                                                        {isCancelling ? "Cancelling..." : "Cancel"}
                                                    </span>
                                                </Button>
                                            </motion.div>
                                        </div>
                                    </div>
                                </motion.div>
                            </CardContent>
                        </Card>
                    </motion.div>
                </motion.div>
            </div>
        </div>
    );
}
