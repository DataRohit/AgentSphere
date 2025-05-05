"use client";

import { useAppSelector } from "@/app/store/hooks";
import { selectUser } from "@/app/store/slices/userSlice";
import { ActiveTransfersSection } from "@/components/active-transfers-section";
import { AddMemberModal } from "@/components/add-member-modal";
import { DashboardNavbar } from "@/components/dashboard-navbar";
import { DeleteOrganizationDialog } from "@/components/delete-organization-dialog";
import { ProtectedRoute } from "@/components/protected-route";
import { TransferOwnershipDialog } from "@/components/transfer-ownership-dialog";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
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
import { zodResolver } from "@hookform/resolvers/zod";
import { formatDistanceToNow } from "date-fns";
import { motion } from "framer-motion";
import Cookies from "js-cookie";
import {
    ArrowLeft,
    Bot,
    Calendar,
    ExternalLink,
    Globe,
    Loader2,
    Lock,
    Pencil,
    Trash2,
    Unlock,
    Upload,
    UserPlus,
    Users,
    X,
} from "lucide-react";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";

const organizationFormSchema = z.object({
    name: z
        .string()
        .min(2, "Name must be at least 2 characters")
        .max(100, "Name must be less than 100 characters"),
    description: z.string().max(500, "Description must be less than 500 characters").optional(),
    website: z.string().url("Please enter a valid URL").optional().or(z.literal("")),
});

type OrganizationFormValues = z.infer<typeof organizationFormSchema>;

interface OrganizationOwner {
    email: string;
    first_name: string;
    last_name: string;
    username: string;
    avatar_url: string;
    is_active: boolean;
    is_staff: boolean;
    is_superuser: boolean;
    date_joined: string;
    last_login: string;
}

interface Organization {
    id: string;
    name: string;
    description: string;
    website: string;
    logo_url: string;
    owner: OrganizationOwner;
    member_count: number;
    created_at: string;
    updated_at: string;
}

interface ApiErrorResponse {
    errors?: {
        [key: string]: string[];
    };
    error?: string;
    organization?: Organization;
}

interface OrganizationMember {
    email: string;
    first_name: string;
    last_name: string;
    username: string;
    avatar_url: string;
    is_active: boolean;
    is_staff: boolean;
    is_superuser: boolean;
    date_joined: string;
    last_login: string;
}

export default function OrganizationDetailPage() {
    const router = useRouter();
    const params = useParams();
    const organizationId = params.id as string;

    const [organization, setOrganization] = useState<Organization | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [isLocked, setIsLocked] = useState(true);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [isUploadingLogo, setIsUploadingLogo] = useState(false);
    const [logoPreview, setLogoPreview] = useState<string | null>(null);
    const [members, setMembers] = useState<OrganizationMember[]>([]);
    const [isFetchingMembers, setIsFetchingMembers] = useState(false);
    const [isAddMemberModalOpen, setIsAddMemberModalOpen] = useState(false);
    const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);

    const currentUser = useAppSelector(selectUser);

    const form = useForm<OrganizationFormValues>({
        resolver: zodResolver(organizationFormSchema),
        defaultValues: {
            name: "",
            description: "",
            website: "",
        },
    });

    const fetchMembers = async () => {
        setIsFetchingMembers(true);
        try {
            const accessToken = Cookies.get("access_token");
            if (!accessToken) {
                throw new Error("Authentication token not found");
            }

            const response = await fetch(
                `http://localhost:8080/api/v1/organizations/${organizationId}/members/`,
                {
                    method: "GET",
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${accessToken}`,
                    },
                }
            );

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || "Failed to fetch organization members");
            }

            setMembers(data.members);
        } catch (error) {
            toast.error(error instanceof Error ? error.message : "Failed to fetch members", {
                style: {
                    backgroundColor: "var(--destructive)",
                    color: "white",
                    border: "none",
                },
            });
        } finally {
            setIsFetchingMembers(false);
        }
    };

    useEffect(() => {
        const fetchOrganization = async () => {
            setIsLoading(true);
            try {
                const accessToken = Cookies.get("access_token");
                if (!accessToken) {
                    throw new Error("Authentication token not found");
                }

                const response = await fetch(
                    `http://localhost:8080/api/v1/organizations/${organizationId}/`,
                    {
                        method: "GET",
                        headers: {
                            "Content-Type": "application/json",
                            Authorization: `Bearer ${accessToken}`,
                        },
                    }
                );

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.error || "Failed to fetch organization details");
                }

                setOrganization(data.organization);
                form.reset({
                    name: data.organization.name,
                    description: data.organization.description || "",
                    website: data.organization.website || "",
                });
            } catch (err) {
                const errorMessage = err instanceof Error ? err.message : "An error occurred";
                toast.error(errorMessage, {
                    style: {
                        backgroundColor: "var(--destructive)",
                        color: "white",
                        border: "none",
                    },
                });
                router.push("/dashboard");
            } finally {
                setIsLoading(false);
            }
        };

        fetchOrganization();
    }, [organizationId, router, form]);

    useEffect(() => {
        if (organization) {
            fetchMembers();
        }
    }, [organization]);

    const onSubmit = async (values: OrganizationFormValues) => {
        setIsSubmitting(true);
        try {
            const accessToken = Cookies.get("access_token");
            if (!accessToken) {
                throw new Error("Authentication token not found");
            }

            const response = await fetch(
                `http://localhost:8080/api/v1/organizations/${organizationId}/`,
                {
                    method: "PATCH",
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${accessToken}`,
                    },
                    body: JSON.stringify(values),
                }
            );

            const data = (await response.json()) as ApiErrorResponse;

            if (!response.ok) {
                if (data.errors) {
                    Object.entries(data.errors).forEach(([field, errors]) => {
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
                    });
                    throw new Error("Validation errors");
                }
                throw new Error(data.error || "Failed to update organization");
            }

            setOrganization(data.organization as Organization);
            setIsLocked(true);
            toast.success("Organization updated successfully", {
                style: {
                    backgroundColor: "oklch(0.45 0.18 142.71)",
                    color: "white",
                    border: "none",
                },
            });
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : "An error occurred";
            if (errorMessage !== "Validation errors") {
                toast.error(errorMessage, {
                    style: {
                        backgroundColor: "var(--destructive)",
                        color: "white",
                        border: "none",
                    },
                });
            }
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleLogoUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
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

        if (file.size > 2 * 1024 * 1024) {
            toast.error("Image size should be less than 2MB", {
                style: {
                    backgroundColor: "var(--destructive)",
                    color: "white",
                    border: "none",
                },
            });
            return;
        }

        const reader = new FileReader();
        reader.onload = () => {
            setLogoPreview(reader.result as string);
        };
        reader.readAsDataURL(file);
        setIsUploadingLogo(true);
        try {
            const accessToken = Cookies.get("access_token");
            if (!accessToken) {
                throw new Error("Authentication token not found");
            }

            const formData = new FormData();
            formData.append("logo", file);

            const response = await fetch(
                `http://localhost:8080/api/v1/organizations/${organizationId}/logo/`,
                {
                    method: "PUT",
                    headers: {
                        Authorization: `Bearer ${accessToken}`,
                    },
                    body: formData,
                }
            );

            const data = (await response.json()) as ApiErrorResponse;

            if (!response.ok) {
                if (data.errors) {
                    Object.entries(data.errors).forEach(([field, errors]) => {
                        toast.error(`${field}: ${errors[0]}`, {
                            style: {
                                backgroundColor: "var(--destructive)",
                                color: "white",
                                border: "none",
                            },
                        });
                    });
                    throw new Error("Validation errors");
                }
                throw new Error(data.error || "Failed to update logo");
            }

            setOrganization(data.organization as Organization);
            setLogoPreview(null);
            toast.success("Logo updated successfully", {
                style: {
                    backgroundColor: "oklch(0.45 0.18 142.71)",
                    color: "white",
                    border: "none",
                },
            });
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : "An error occurred";
            if (errorMessage !== "Validation errors") {
                toast.error(errorMessage, {
                    style: {
                        backgroundColor: "var(--destructive)",
                        color: "white",
                        border: "none",
                    },
                });
            }
        } finally {
            setIsUploadingLogo(false);
        }
    };

    const getInitials = (name: string) => {
        return name
            .split(" ")
            .map((part) => part[0])
            .join("")
            .toUpperCase()
            .substring(0, 2);
    };

    const handleAddMember = () => {
        setIsAddMemberModalOpen(true);
    };

    const handleMemberAdded = (updatedOrganization: Organization) => {
        setOrganization(updatedOrganization);
        fetchMembers();
    };

    function MemberCard({ member, index }: { member: OrganizationMember; index: number }) {
        const fullName =
            member.first_name && member.last_name
                ? `${member.first_name} ${member.last_name}`
                : member.username;

        const [isRemoveDialogOpen, setIsRemoveDialogOpen] = useState(false);
        const [isRemoving, setIsRemoving] = useState(false);
        const [isTransferDialogOpen, setIsTransferDialogOpen] = useState(false);

        const handleRemoveMember = async () => {
            setIsRemoving(true);
            try {
                const accessToken = Cookies.get("access_token");
                if (!accessToken) {
                    throw new Error("Authentication token not found");
                }

                const payload = member.email
                    ? { email: member.email }
                    : { username: member.username };

                const response = await fetch(
                    `http://localhost:8080/api/v1/organizations/${organizationId}/members/remove/`,
                    {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                            Authorization: `Bearer ${accessToken}`,
                        },
                        body: JSON.stringify(payload),
                    }
                );

                const data = await response.json();

                if (!response.ok) {
                    if (data.errors) {
                        Object.entries(data.errors).forEach(([field, errors]: [string, any]) => {
                            if (Array.isArray(errors) && errors.length > 0) {
                                toast.error(`${field}: ${errors[0]}`, {
                                    style: {
                                        backgroundColor: "var(--destructive)",
                                        color: "white",
                                        border: "none",
                                    },
                                });
                            }
                        });
                    } else if (data.error) {
                        throw new Error(data.error);
                    } else {
                        throw new Error("Failed to remove member");
                    }
                } else {
                    toast.success("Member removed successfully", {
                        style: {
                            backgroundColor: "oklch(0.45 0.18 142.71)",
                            color: "white",
                            border: "none",
                        },
                    });

                    fetchMembers();
                }
            } catch (error) {
                toast.error(error instanceof Error ? error.message : "Failed to remove member", {
                    style: {
                        backgroundColor: "var(--destructive)",
                        color: "white",
                        border: "none",
                    },
                });
            } finally {
                setIsRemoving(false);
                setIsRemoveDialogOpen(false);
            }
        };

        return (
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
                whileHover={{ y: -5, transition: { duration: 0.2 } }}
                className="h-full"
            >
                <Card className="h-full border border-(--border) shadow-sm hover:shadow-md transition-all duration-300 overflow-hidden flex flex-col bg-(--card) dark:bg-(--secondary) relative group p-0">
                    <CardHeader className="pb-1 pt-4 px-4">
                        <div className="flex items-start space-x-3">
                            <Avatar className="h-10 w-10 border border-(--border) my-auto">
                                {member.avatar_url ? (
                                    <AvatarImage src={member.avatar_url} alt={fullName} />
                                ) : null}
                                <AvatarFallback className="bg-(--primary)/10 text-(--primary)">
                                    {getInitials(fullName)}
                                </AvatarFallback>
                            </Avatar>
                            <div className="flex-1">
                                <div className="flex items-center justify-between">
                                    <CardTitle className="text-lg font-semibold">
                                        {fullName}
                                    </CardTitle>
                                    {member.is_active ? (
                                        <span className="text-xs font-medium text-green-500">
                                            Active
                                        </span>
                                    ) : (
                                        <span className="text-xs font-medium text-red-500">
                                            Inactive
                                        </span>
                                    )}
                                </div>
                                <p className="text-sm text-(--muted-foreground) mt-0.5">
                                    {member.email}
                                </p>
                            </div>
                        </div>
                    </CardHeader>
                    <CardContent className="px-4 py-2 mt-auto text-xs text-(--muted-foreground) space-y-1.5">
                        <div className="flex justify-between">
                            <span className="text-[#64748b]">Joined:</span>
                            <span className="text-right text-[#64748b]">
                                {formatDistanceToNow(new Date(member.date_joined), {
                                    addSuffix: true,
                                })}
                            </span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-[#64748b]">Last login:</span>
                            <span className="text-right text-[#64748b]">
                                {member.last_login
                                    ? formatDistanceToNow(new Date(member.last_login), {
                                          addSuffix: true,
                                      })
                                    : "Never"}
                            </span>
                        </div>
                    </CardContent>
                    <div className="flex w-full mt-auto border-t border-[#1e293b]">
                        <button
                            className="flex-1 h-12 bg-(--secondary) hover:bg-[#1e293b] text-[#3b82f6] text-sm flex items-center justify-center cursor-pointer transition-colors duration-200"
                            onClick={(e) => {
                                e.stopPropagation();
                                setIsTransferDialogOpen(true);
                            }}
                        >
                            <Users className="h-4 w-4 mr-2" />
                            <span>Transfer</span>
                        </button>
                        <div className="w-px h-12 bg-[#1e293b]"></div>
                        <button
                            className="flex-1 h-12 bg-(--secondary) hover:bg-[#1e293b] text-[#ef4444] text-sm flex items-center justify-center cursor-pointer transition-colors duration-200"
                            onClick={(e) => {
                                e.stopPropagation();
                                setIsRemoveDialogOpen(true);
                            }}
                        >
                            <Trash2 className="h-4 w-4 mr-2" />
                            <span>Remove</span>
                        </button>
                    </div>
                </Card>

                <Dialog open={isRemoveDialogOpen} onOpenChange={setIsRemoveDialogOpen}>
                    <DialogContent className="sm:max-w-[425px] bg-(--background) border-(--border) [&_[data-slot=dialog-close]]:hover:opacity-100 [&_[data-slot=dialog-close]]:cursor-pointer [&_[data-slot=dialog-close]]:transition-opacity [&_[data-slot=dialog-close]]:duration-200">
                        <DialogHeader>
                            <DialogTitle className="flex items-center text-(--foreground) pb-2">
                                <Trash2 className="mr-2 h-5 w-5 text-(--destructive)" />
                                Remove Member
                            </DialogTitle>
                            <DialogDescription>
                                Are you sure you want to remove this member from the organization?
                            </DialogDescription>
                        </DialogHeader>

                        <div className="py-4">
                            <p className="text-sm text-center">
                                You are about to remove{" "}
                                <span className="font-medium">{fullName}</span> from the
                                organization.
                            </p>
                        </div>

                        <DialogFooter className="flex flex-col sm:flex-row sm:justify-between w-full gap-2">
                            <Button
                                type="button"
                                variant="outline"
                                onClick={() => setIsRemoveDialogOpen(false)}
                                disabled={isRemoving}
                                className="font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--border) bg-(--background) text-(--foreground) hover:bg-(--muted) h-10 cursor-pointer w-full sm:flex-1"
                            >
                                <span className="relative z-10">Cancel</span>
                                <span className="absolute inset-0 bg-(--muted)/50 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                            </Button>
                            <Button
                                type="button"
                                variant="destructive"
                                onClick={handleRemoveMember}
                                disabled={isRemoving}
                                className="font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--destructive) bg-(--destructive) text-(--destructive-foreground) dark:bg-(--destructive) dark:text-(--destructive-foreground) dark:border-(--destructive) h-10 cursor-pointer w-full sm:flex-1"
                            >
                                <span className="relative z-10">
                                    {isRemoving ? (
                                        <>
                                            <Loader2 className="mr-2 h-4 w-4 animate-spin inline" />
                                            Removing...
                                        </>
                                    ) : (
                                        "Remove"
                                    )}
                                </span>
                                <span className="absolute inset-0 bg-(--destructive-foreground)/10 dark:bg-(--destructive-foreground)/20 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                            </Button>
                        </DialogFooter>
                    </DialogContent>
                </Dialog>

                <TransferOwnershipDialog
                    open={isTransferDialogOpen}
                    onOpenChange={setIsTransferDialogOpen}
                    organizationId={organizationId}
                    organizationName={organization?.name || ""}
                    member={member}
                />
            </motion.div>
        );
    }

    function AddMemberCard({ index, onClick }: { index: number; onClick: () => void }) {
        return (
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
                whileHover={{ y: -5, transition: { duration: 0.2 } }}
                className="h-full"
                onClick={onClick}
            >
                <Card className="h-full border border-dashed border-(--primary) bg-(--card) dark:bg-slate-900 hover:bg-(--primary)/5 transition-all duration-300 flex flex-col items-center justify-center p-6 cursor-pointer group">
                    <div className="flex flex-col items-center text-center">
                        <div className="h-12 w-12 rounded-full bg-(--primary)/10 flex items-center justify-center mb-4 group-hover:bg-(--primary)/20 transition-colors duration-300">
                            <UserPlus className="h-6 w-6 text-(--primary)" />
                        </div>
                        <h3 className="font-medium mb-1">Add Member</h3>
                        <p className="text-sm text-(--muted-foreground)">
                            Invite a new member to join
                        </p>
                    </div>
                </Card>
            </motion.div>
        );
    }

    const toggleLock = () => {
        if (!isLocked) {
            form.reset({
                name: organization?.name || "",
                description: organization?.description || "",
                website: organization?.website || "",
            });
        }
        setIsLocked(!isLocked);
    };

    const handleCancel = () => {
        form.reset({
            name: organization?.name || "",
            description: organization?.description || "",
            website: organization?.website || "",
        });
        setIsLocked(true);
    };

    if (isLoading) {
        return (
            <ProtectedRoute>
                <div className="min-h-screen flex flex-col bg-(--background)">
                    <DashboardNavbar />
                    <div className="flex-1 container mx-auto px-4 pt-24 pb-8">
                        <div className="flex justify-center items-center h-full">
                            <div className="flex flex-col items-center">
                                <Loader2 className="h-8 w-8 animate-spin text-(--primary)" />
                                <p className="mt-4 text-lg">Loading organization details...</p>
                            </div>
                        </div>
                    </div>
                </div>
            </ProtectedRoute>
        );
    }

    if (!organization) {
        return (
            <ProtectedRoute>
                <div className="min-h-screen flex flex-col bg-(--background)">
                    <DashboardNavbar />
                    <div className="flex-1 container mx-auto px-4 pt-24 pb-8">
                        <div className="flex justify-center items-center h-full">
                            <div className="flex flex-col items-center">
                                <X className="h-8 w-8 text-(--destructive)" />
                                <p className="mt-4 text-lg">Organization not found</p>
                                <Button className="mt-4" onClick={() => router.push("/dashboard")}>
                                    Return to Dashboard
                                </Button>
                            </div>
                        </div>
                    </div>
                </div>
            </ProtectedRoute>
        );
    }

    return (
        <ProtectedRoute>
            <div className="min-h-screen flex flex-col bg-(--background)">
                <DashboardNavbar />
                <div className="flex-1 container mx-auto px-4 pt-24 pb-8">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5 }}
                        className="space-y-8"
                    >
                        <Button
                            variant="ghost"
                            className="flex items-center text-(--muted-foreground) hover:text-(--foreground)"
                            onClick={() => router.push("/dashboard")}
                        >
                            <ArrowLeft className="mr-2 h-4 w-4" />
                            Back to Dashboard
                        </Button>

                        <Card className="border border-(--border) shadow-sm overflow-hidden p-0 pt-6">
                            <CardHeader className="pb-4 relative flex justify-between items-start bg-(--background)">
                                <div className="flex items-center gap-4">
                                    <div className="relative">
                                        <Avatar className="h-16 w-16 border border-(--border)">
                                            {organization.logo_url || logoPreview ? (
                                                <AvatarImage
                                                    src={logoPreview || organization.logo_url}
                                                    alt={organization.name}
                                                />
                                            ) : null}
                                            <AvatarFallback className="bg-(--primary)/10 text-(--primary) text-xl">
                                                {getInitials(organization.name)}
                                            </AvatarFallback>
                                        </Avatar>
                                        {!isLocked && (
                                            <div className="absolute inset-0 flex items-center justify-center">
                                                <label
                                                    htmlFor="logo-upload"
                                                    className="h-full w-full flex items-center justify-center bg-black/50 rounded-full cursor-pointer opacity-0 hover:opacity-100 transition-opacity duration-200"
                                                >
                                                    {isUploadingLogo ? (
                                                        <Loader2 className="h-5 w-5 animate-spin text-white" />
                                                    ) : (
                                                        <Upload className="h-5 w-5 text-white" />
                                                    )}
                                                    <span className="sr-only">Upload Logo</span>
                                                </label>
                                                <input
                                                    id="logo-upload"
                                                    type="file"
                                                    accept="image/*"
                                                    className="hidden bg-(--secondary)"
                                                    onChange={handleLogoUpload}
                                                    disabled={isUploadingLogo}
                                                />
                                            </div>
                                        )}
                                    </div>
                                    <div>
                                        <CardTitle className="text-xl font-bold">
                                            {organization.name}
                                        </CardTitle>
                                        <CardDescription className="mt-1 text-sm">
                                            Owned by {organization.owner.first_name}{" "}
                                            {organization.owner.last_name}
                                        </CardDescription>
                                    </div>
                                </div>

                                <Button
                                    variant="ghost"
                                    size="icon"
                                    className="h-8 w-8 rounded-full bg-(--muted) hover:bg-(--muted-foreground)/20 transition-colors duration-200 cursor-pointer"
                                    onClick={toggleLock}
                                    disabled={isSubmitting || isUploadingLogo}
                                >
                                    {isLocked ? (
                                        <Lock className="h-4 w-4 text-(--foreground)" />
                                    ) : (
                                        <Unlock className="h-4 w-4 text-(--foreground)" />
                                    )}
                                    <span className="sr-only">{isLocked ? "Unlock" : "Lock"}</span>
                                </Button>
                            </CardHeader>

                            <CardContent className="px-6 py-4 space-y-6 bg-(--background)">
                                <Form {...form}>
                                    <form
                                        onSubmit={form.handleSubmit(onSubmit)}
                                        className="space-y-6"
                                    >
                                        <FormField
                                            control={form.control}
                                            name="name"
                                            render={({ field }) => (
                                                <FormItem className="space-y-2">
                                                    <FormLabel className="flex items-center text-sm font-medium">
                                                        <span>Name</span>
                                                        {!isLocked && (
                                                            <Pencil className="ml-2 h-3 w-3 text-(--muted-foreground)" />
                                                        )}
                                                    </FormLabel>
                                                    {isLocked ? (
                                                        <div className="p-2 rounded-md bg-(--secondary) text-sm">
                                                            {field.value}
                                                        </div>
                                                    ) : (
                                                        <FormControl>
                                                            <Input
                                                                {...field}
                                                                className="bg-(--secondary) border-(--border) focus:border-(--primary) focus:ring-1 focus:ring-(--primary)"
                                                            />
                                                        </FormControl>
                                                    )}
                                                    <FormMessage />
                                                </FormItem>
                                            )}
                                        />

                                        <FormField
                                            control={form.control}
                                            name="description"
                                            render={({ field }) => (
                                                <FormItem className="space-y-2">
                                                    <FormLabel className="flex items-center text-sm font-medium">
                                                        <span>Description</span>
                                                        {!isLocked && (
                                                            <Pencil className="ml-2 h-3 w-3 text-(--muted-foreground)" />
                                                        )}
                                                    </FormLabel>
                                                    {isLocked ? (
                                                        <div className="p-2 rounded-md bg-(--secondary) min-h-[80px] text-sm">
                                                            {field.value ||
                                                                "No description provided"}
                                                        </div>
                                                    ) : (
                                                        <FormControl>
                                                            <Textarea
                                                                {...field}
                                                                className="min-h-[120px] resize-none bg-(--secondary) border-(--border) focus:border-(--primary) focus:ring-1 focus:ring-(--primary)"
                                                                placeholder="Describe your organization..."
                                                            />
                                                        </FormControl>
                                                    )}
                                                    <FormMessage />
                                                </FormItem>
                                            )}
                                        />

                                        <FormField
                                            control={form.control}
                                            name="website"
                                            render={({ field }) => (
                                                <FormItem className="space-y-2">
                                                    <FormLabel className="flex items-center text-sm font-medium">
                                                        <span>Website</span>
                                                        {!isLocked && (
                                                            <Pencil className="ml-2 h-3 w-3 text-(--muted-foreground)" />
                                                        )}
                                                    </FormLabel>
                                                    {isLocked ? (
                                                        <div className="p-2 rounded-md bg-(--secondary) text-sm">
                                                            {field.value ? (
                                                                <a
                                                                    href={
                                                                        field.value.startsWith(
                                                                            "http"
                                                                        )
                                                                            ? field.value
                                                                            : `https://${field.value}`
                                                                    }
                                                                    target="_blank"
                                                                    rel="noopener noreferrer"
                                                                    className="text-(--primary) hover:underline flex items-center"
                                                                >
                                                                    <Globe className="mr-2 h-4 w-4" />
                                                                    <span>
                                                                        {field.value.replace(
                                                                            /^https?:\/\//i,
                                                                            ""
                                                                        )}
                                                                    </span>
                                                                    <ExternalLink className="ml-1 h-3 w-3" />
                                                                </a>
                                                            ) : (
                                                                "No website provided"
                                                            )}
                                                        </div>
                                                    ) : (
                                                        <FormControl>
                                                            <Input
                                                                {...field}
                                                                placeholder="https://example.com"
                                                                className="bg-(--secondary) border-(--border) focus:border-(--primary) focus:ring-1 focus:ring-(--primary)"
                                                            />
                                                        </FormControl>
                                                    )}
                                                    <FormDescription className="text-xs">
                                                        Your organization's website (optional)
                                                    </FormDescription>
                                                    <FormMessage />
                                                </FormItem>
                                            )}
                                        />

                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4">
                                            <div className="flex items-center text-xs text-(--muted-foreground)">
                                                <Users className="mr-2 h-3 w-3" />
                                                <span>
                                                    {organization.member_count}{" "}
                                                    {organization.member_count === 1
                                                        ? "member"
                                                        : "members"}
                                                </span>
                                            </div>
                                            <div className="flex items-center text-xs text-(--muted-foreground)">
                                                <Calendar className="mr-2 h-3 w-3" />
                                                <span>
                                                    Created{" "}
                                                    {formatDistanceToNow(
                                                        new Date(organization.created_at),
                                                        { addSuffix: true }
                                                    )}
                                                </span>
                                            </div>
                                        </div>
                                    </form>
                                </Form>
                            </CardContent>

                            <CardFooter className="[.border-t]:py-4 px-6 border-t bg-(--background) flex flex-col gap-6 md:flex-row md:gap-0 justify-between items-center">
                                <div className="flex items-center">
                                    <span className="text-xs text-(--muted-foreground)">
                                        Last updated:{" "}
                                        {formatDistanceToNow(new Date(organization.updated_at), {
                                            addSuffix: true,
                                        })}
                                    </span>
                                </div>

                                {!isLocked ? (
                                    <div className="flex space-x-3">
                                        <Button
                                            type="button"
                                            variant="outline"
                                            onClick={handleCancel}
                                            disabled={isSubmitting}
                                            className="h-9 px-4 text-sm font-medium border border-(--border) bg-(--secondary) text-(--foreground) hover:bg-(--muted) cursor-pointer"
                                        >
                                            Cancel
                                        </Button>
                                        <Button
                                            type="submit"
                                            onClick={form.handleSubmit(onSubmit)}
                                            disabled={isSubmitting}
                                            className="h-9 px-4 text-sm font-medium border border-(--primary) bg-(--secondary) text-(--primary-foreground) hover:bg-(--primary)/90 cursor-pointer"
                                        >
                                            {isSubmitting ? (
                                                <>
                                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                                    Saving...
                                                </>
                                            ) : (
                                                "Save Changes"
                                            )}
                                        </Button>
                                    </div>
                                ) : (
                                    <div className="flex space-x-3">
                                        <Button
                                            type="button"
                                            variant="outline"
                                            onClick={() =>
                                                router.push(
                                                    `/organizations/${organizationId}/agent-studio`
                                                )
                                            }
                                            className="h-9 px-4 text-sm font-medium flex items-center cursor-pointer text-(--primary) border-(--border) hover:bg-(--primary)/10"
                                        >
                                            <Bot className="mr-2 h-4 w-4" />
                                            Agent Studio
                                        </Button>
                                        <Button
                                            type="button"
                                            variant="outline"
                                            onClick={() => setIsDeleteDialogOpen(true)}
                                            className="h-9 px-4 text-sm font-medium flex items-center cursor-pointer text-(--destructive) border-(--border) hover:bg-(--destructive)/10"
                                        >
                                            <Trash2 className="mr-2 h-4 w-4" />
                                            Delete Organization
                                        </Button>
                                    </div>
                                )}
                            </CardFooter>
                        </Card>

                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.5, delay: 0.2 }}
                            className="mt-8"
                        >
                            <ActiveTransfersSection organizationId={organizationId} />
                        </motion.div>

                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.5, delay: 0.3 }}
                            className="mt-8"
                        >
                            <div className="flex items-center justify-between mb-4">
                                <h2 className="text-2xl font-bold">Members</h2>
                            </div>

                            {isFetchingMembers ? (
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                    {[...Array(3)].map((_, index) => (
                                        <Card
                                            key={index}
                                            className="h-24 border border-(--border) shadow-sm animate-pulse"
                                        >
                                            <div className="flex items-center p-4 space-x-4">
                                                <div className="h-10 w-10 rounded-full bg-(--muted)" />
                                                <div className="space-y-2">
                                                    <div className="h-4 w-24 bg-(--muted) rounded" />
                                                    <div className="h-3 w-32 bg-(--muted) rounded" />
                                                </div>
                                            </div>
                                        </Card>
                                    ))}
                                </div>
                            ) : (
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                    {members
                                        .filter(
                                            (member) =>
                                                !currentUser ||
                                                (member.email !== currentUser.email &&
                                                    member.username !== currentUser.username)
                                        )
                                        .map((member, index) => (
                                            <MemberCard
                                                key={member.email}
                                                member={member}
                                                index={index}
                                            />
                                        ))}
                                    <AddMemberCard
                                        index={members.length}
                                        onClick={handleAddMember}
                                    />
                                </div>
                            )}
                        </motion.div>
                    </motion.div>
                </div>
            </div>

            <AddMemberModal
                open={isAddMemberModalOpen}
                onOpenChange={setIsAddMemberModalOpen}
                organizationId={organizationId}
                onMemberAdded={handleMemberAdded}
            />

            <DeleteOrganizationDialog
                open={isDeleteDialogOpen}
                onOpenChange={setIsDeleteDialogOpen}
                organizationId={organizationId}
                organizationName={organization.name}
            />
        </ProtectedRoute>
    );
}
