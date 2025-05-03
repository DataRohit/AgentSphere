"use client";

import { useAppDispatch, useAppSelector } from "@/app/store/hooks";
import { selectUser, setUser } from "@/app/store/slices/userSlice";
import { DashboardNavbar } from "@/components/dashboard-navbar";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
    Form,
    FormControl,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { zodResolver } from "@hookform/resolvers/zod";
import { motion } from "framer-motion";
import Cookies from "js-cookie";
import { Loader2, Upload, User } from "lucide-react";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";

const userInfoSchema = z.object({
    username: z.string().min(3, "Username must be at least 3 characters"),
    first_name: z.string().min(1, "First name is required"),
    last_name: z.string().min(1, "Last name is required"),
});

type UserInfoValues = z.infer<typeof userInfoSchema>;

export default function ProfilePage() {
    const router = useRouter();
    const dispatch = useAppDispatch();
    const user = useAppSelector(selectUser);
    const [isLoading, setIsLoading] = useState(true);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [isUploading, setIsUploading] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const form = useForm<UserInfoValues>({
        resolver: zodResolver(userInfoSchema),
        defaultValues: {
            username: "",
            first_name: "",
            last_name: "",
        },
    });

    useEffect(() => {
        const accessToken = Cookies.get("access_token");
        if (!accessToken) {
            toast.error("Please log in to access your profile", {
                style: {
                    backgroundColor: "var(--destructive)",
                    color: "white",
                    border: "none",
                },
            });
            router.push("/auth/login");
            return;
        }

        setIsLoading(false);
    }, [router]);

    useEffect(() => {
        if (user) {
            form.reset({
                username: user.username || "",
                first_name: user.first_name || "",
                last_name: user.last_name || "",
            });
        }
    }, [user, form]);

    const onSubmit = async (data: UserInfoValues) => {
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

            const apiUrl = process.env.NEXT_PUBLIC_API_URL || "/api/v1";
            const response = await fetch(`${apiUrl}/users/me/`, {
                method: "PATCH",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${accessToken}`,
                },
                body: JSON.stringify(data),
            });

            const result = await response.json();

            if (response.ok) {
                dispatch(setUser(result.user));

                toast.success("Profile updated successfully", {
                    style: {
                        backgroundColor: "oklch(0.45 0.18 142.71)",
                        color: "white",
                        border: "none",
                    },
                });
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
                } else {
                    toast.error("Failed to update profile", {
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

    const handleAvatarUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (!file) return;

        if (!file.type.startsWith("image/")) {
            toast.error("Please upload an image file", {
                style: {
                    backgroundColor: "var(--destructive)",
                    color: "white",
                    border: "none",
                },
            });
            return;
        }

        if (file.size > 5 * 1024 * 1024) {
            toast.error("Image size should be less than 5MB", {
                style: {
                    backgroundColor: "var(--destructive)",
                    color: "white",
                    border: "none",
                },
            });
            return;
        }

        setIsUploading(true);
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

            const formData = new FormData();
            formData.append("avatar", file);

            const apiUrl = process.env.NEXT_PUBLIC_API_URL || "/api/v1";
            const response = await fetch(`${apiUrl}/users/me/avatar/`, {
                method: "PUT",
                headers: {
                    Authorization: `Bearer ${accessToken}`,
                },
                body: formData,
            });

            const result = await response.json();

            if (response.ok) {
                dispatch(setUser(result.user));

                toast.success("Avatar updated successfully", {
                    style: {
                        backgroundColor: "oklch(0.45 0.18 142.71)",
                        color: "white",
                        border: "none",
                    },
                });

                window.location.reload();
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
                } else {
                    toast.error("Failed to update avatar", {
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
            setIsUploading(false);
            if (fileInputRef.current) {
                fileInputRef.current.value = "";
            }
        }
    };

    const triggerFileInput = () => {
        fileInputRef.current?.click();
    };

    if (isLoading) {
        return (
            <div className="min-h-screen flex flex-col bg-(--background)">
                <DashboardNavbar />
                <div className="flex-1 flex items-center justify-center pt-16">
                    <div className="flex flex-col items-center space-y-4">
                        <Loader2 className="h-12 w-12 text-(--primary) animate-spin" />
                        <p className="text-center text-(--foreground)">Loading your profile...</p>
                    </div>
                </div>
            </div>
        );
    }

    return (
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
                                <h1 className="text-3xl font-bold tracking-tight">Profile</h1>
                                <p className="text-(--muted-foreground)">
                                    Manage your account settings and profile information.
                                </p>
                            </div>
                        </div>

                        <Tabs defaultValue="info" className="w-full">
                            <TabsList className="flex w-full md:w-[400px] gap-1 bg-(--card) p-0.5 rounded-lg overflow-hidden h-10">
                                <TabsTrigger
                                    value="info"
                                    className="flex-1 data-[state=active]:bg-(--primary) data-[state=active]:text-(--primary-foreground) data-[state=active]:shadow-sm transition-all duration-200 hover:bg-(--accent) data-[state=active]:hover:bg-(--primary) rounded-md cursor-pointer flex items-center justify-center py-1.5 px-2 m-0 h-9"
                                >
                                    <div className="flex items-center">
                                        <User className="mr-2 h-4 w-4" />
                                        <span>User Information</span>
                                    </div>
                                </TabsTrigger>
                                <TabsTrigger
                                    value="avatar"
                                    className="flex-1 data-[state=active]:bg-(--primary) data-[state=active]:text-(--primary-foreground) data-[state=active]:shadow-sm transition-all duration-200 hover:bg-(--accent) data-[state=active]:hover:bg-(--primary) rounded-md cursor-pointer flex items-center justify-center py-1.5 px-2 m-0 h-9"
                                >
                                    <div className="flex items-center">
                                        <Upload className="mr-2 h-4 w-4" />
                                        <span>Avatar</span>
                                    </div>
                                </TabsTrigger>
                            </TabsList>

                            <TabsContent
                                value="info"
                                className="mt-6 data-[state=active]:animate-in data-[state=inactive]:animate-out data-[state=inactive]:fade-out-50 data-[state=active]:fade-in-50 duration-200"
                            >
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
                                    <Card className="overflow-hidden border border-(--border) shadow-sm hover:shadow-md transition-shadow duration-300">
                                        <motion.div
                                            initial={{ opacity: 0, y: 10 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            transition={{ delay: 0.2, duration: 0.3 }}
                                        >
                                            <CardHeader>
                                                <CardTitle>User Information</CardTitle>
                                                <CardDescription>
                                                    Update your personal information.
                                                </CardDescription>
                                            </CardHeader>
                                        </motion.div>
                                        <motion.div
                                            initial={{ opacity: 0 }}
                                            animate={{ opacity: 1 }}
                                            transition={{ delay: 0.3, duration: 0.4 }}
                                        >
                                            <CardContent>
                                                <Form {...form}>
                                                    <form
                                                        onSubmit={form.handleSubmit(onSubmit)}
                                                        className="space-y-6"
                                                    >
                                                        <FormField
                                                            control={form.control}
                                                            name="username"
                                                            render={({ field }) => (
                                                                <FormItem>
                                                                    <FormLabel>Username</FormLabel>
                                                                    <FormControl>
                                                                        <Input
                                                                            placeholder="Username"
                                                                            {...field}
                                                                        />
                                                                    </FormControl>
                                                                    <FormMessage />
                                                                </FormItem>
                                                            )}
                                                        />

                                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                                            <FormField
                                                                control={form.control}
                                                                name="first_name"
                                                                render={({ field }) => (
                                                                    <FormItem>
                                                                        <FormLabel>
                                                                            First Name
                                                                        </FormLabel>
                                                                        <FormControl>
                                                                            <Input
                                                                                placeholder="First Name"
                                                                                {...field}
                                                                            />
                                                                        </FormControl>
                                                                        <FormMessage />
                                                                    </FormItem>
                                                                )}
                                                            />

                                                            <FormField
                                                                control={form.control}
                                                                name="last_name"
                                                                render={({ field }) => (
                                                                    <FormItem>
                                                                        <FormLabel>
                                                                            Last Name
                                                                        </FormLabel>
                                                                        <FormControl>
                                                                            <Input
                                                                                placeholder="Last Name"
                                                                                {...field}
                                                                            />
                                                                        </FormControl>
                                                                        <FormMessage />
                                                                    </FormItem>
                                                                )}
                                                            />
                                                        </div>

                                                        <motion.div
                                                            initial={{ opacity: 0, y: 10 }}
                                                            animate={{ opacity: 1, y: 0 }}
                                                            transition={{
                                                                delay: 0.6,
                                                                duration: 0.3,
                                                            }}
                                                            whileHover={{ scale: 1.02 }}
                                                            whileTap={{ scale: 0.98 }}
                                                        >
                                                            <Button
                                                                type="submit"
                                                                disabled={isSubmitting}
                                                                className="font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--primary) bg-(--primary) text-(--primary-foreground) dark:bg-(--primary) dark:text-(--primary-foreground) dark:border-(--primary) px-8 h-12 cursor-pointer w-full"
                                                            >
                                                                <span className="relative z-10">
                                                                    {isSubmitting
                                                                        ? "Updating..."
                                                                        : "Update Profile"}
                                                                </span>
                                                                <span className="absolute inset-0 bg-(--primary-foreground)/10 dark:bg-(--primary-foreground)/20 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                                                            </Button>
                                                        </motion.div>
                                                    </form>
                                                </Form>
                                            </CardContent>
                                        </motion.div>
                                    </Card>
                                </motion.div>
                            </TabsContent>

                            <TabsContent
                                value="avatar"
                                className="mt-6 data-[state=active]:animate-in data-[state=inactive]:animate-out data-[state=inactive]:fade-out-50 data-[state=active]:fade-in-50 duration-200"
                            >
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
                                    <Card className="overflow-hidden border border-(--border) shadow-sm hover:shadow-md transition-shadow duration-300">
                                        <motion.div
                                            initial={{ opacity: 0, y: 10 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            transition={{ delay: 0.2, duration: 0.3 }}
                                        >
                                            <CardHeader>
                                                <CardTitle>Avatar</CardTitle>
                                                <CardDescription>
                                                    Update your profile picture.
                                                </CardDescription>
                                            </CardHeader>
                                        </motion.div>
                                        <motion.div
                                            initial={{ opacity: 0 }}
                                            animate={{ opacity: 1 }}
                                            transition={{ delay: 0.3, duration: 0.4 }}
                                        >
                                            <CardContent>
                                                <div className="space-y-6">
                                                    <div className="flex flex-col items-center space-y-4">
                                                        <motion.div
                                                            className="relative h-32 w-32 rounded-full overflow-hidden border-4 border-(--border)"
                                                            initial={{ scale: 0.8, opacity: 0 }}
                                                            animate={{ scale: 1, opacity: 1 }}
                                                            transition={{
                                                                type: "spring",
                                                                stiffness: 300,
                                                                damping: 20,
                                                                delay: 0.4,
                                                            }}
                                                            whileHover={{
                                                                scale: 1.05,
                                                                borderColor: "var(--primary)",
                                                            }}
                                                        >
                                                            {user?.avatar_url ? (
                                                                <Image
                                                                    src={user.avatar_url}
                                                                    alt={user.username}
                                                                    fill
                                                                    className="object-cover"
                                                                />
                                                            ) : (
                                                                <div className="h-full w-full flex items-center justify-center bg-(--primary)/10 text-(--primary)">
                                                                    <User size={48} />
                                                                </div>
                                                            )}
                                                        </motion.div>

                                                        <div className="text-center">
                                                            <h3 className="font-medium">
                                                                {user?.full_name || user?.username}
                                                            </h3>
                                                            <p className="text-sm text-(--muted-foreground)">
                                                                {user?.email}
                                                            </p>
                                                        </div>
                                                    </div>

                                                    <Separator />

                                                    <div className="space-y-4">
                                                        <div className="space-y-2">
                                                            <Label htmlFor="avatar">
                                                                Upload new avatar
                                                            </Label>
                                                            <p className="text-sm text-(--muted-foreground)">
                                                                Supported formats: JPEG, PNG, GIF.
                                                                Max size: 5MB.
                                                            </p>
                                                        </div>

                                                        <input
                                                            type="file"
                                                            id="avatar"
                                                            ref={fileInputRef}
                                                            accept="image/*"
                                                            onChange={handleAvatarUpload}
                                                            className="hidden"
                                                        />

                                                        <motion.div
                                                            initial={{ opacity: 0, y: 10 }}
                                                            animate={{ opacity: 1, y: 0 }}
                                                            transition={{
                                                                delay: 0.6,
                                                                duration: 0.3,
                                                            }}
                                                            whileHover={{ scale: 1.02 }}
                                                            whileTap={{ scale: 0.98 }}
                                                        >
                                                            <Button
                                                                type="button"
                                                                onClick={triggerFileInput}
                                                                disabled={isUploading}
                                                                className="font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--primary) bg-(--primary) text-(--primary-foreground) dark:bg-(--primary) dark:text-(--primary-foreground) dark:border-(--primary) px-8 h-12 cursor-pointer w-full"
                                                            >
                                                                <span className="relative z-10 flex items-center">
                                                                    {isUploading ? (
                                                                        <>
                                                                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                                                            Uploading...
                                                                        </>
                                                                    ) : (
                                                                        <>
                                                                            <Upload className="mr-2 h-4 w-4" />
                                                                            Upload Avatar
                                                                        </>
                                                                    )}
                                                                </span>
                                                                <span className="absolute inset-0 bg-(--primary-foreground)/10 dark:bg-(--primary-foreground)/20 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                                                            </Button>
                                                        </motion.div>
                                                    </div>
                                                </div>
                                            </CardContent>
                                        </motion.div>
                                    </Card>
                                </motion.div>
                            </TabsContent>
                        </Tabs>
                    </div>
                </motion.div>
            </div>
        </div>
    );
}
