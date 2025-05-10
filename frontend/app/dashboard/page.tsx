"use client";

import { useAppSelector } from "@/app/store/hooks";
import { selectUser } from "@/app/store/slices/userSlice";
import { CreateOrganizationModal } from "@/components/create-organization-modal";
import { DashboardNavbar } from "@/components/dashboard-navbar";
import {
    CreateOrganizationCard,
    Organization,
    OrganizationCard,
    OrganizationCardSkeleton,
} from "@/components/organization-card";
import { OrganizationDetailsModal } from "@/components/organization-details-modal";
import { ProtectedRoute } from "@/components/protected-route";
import { ReceivedTransfersSection } from "@/components/received-transfers-section";
import { motion } from "framer-motion";
import Cookies from "js-cookie";
import { AlertCircle, Building2, MailQuestion, Users } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { toast } from "sonner";

export default function DashboardPage() {
    const user = useAppSelector(selectUser);
    const [organizations, setOrganizations] = useState<Organization[]>([]);
    const [memberOrganizations, setMemberOrganizations] = useState<Organization[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isMembershipsLoading, setIsMembershipsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [membershipError, setMembershipError] = useState<string | null>(null);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [isDetailsModalOpen, setIsDetailsModalOpen] = useState(false);
    const [selectedOrganization, setSelectedOrganization] = useState<Organization | null>(null);

    const fetchOrganizations = async () => {
        setIsLoading(true);
        setError(null);

        try {
            const accessToken = Cookies.get("access_token");
            if (!accessToken) {
                throw new Error("Authentication token not found");
            }

            const response = await fetch(
                `${process.env.NEXT_PUBLIC_API_URL}/organizations/owned/`,
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
                throw new Error(data.error || "Failed to fetch organizations");
            }

            setOrganizations(data.organizations || []);
        } catch (err) {
            const errorMessage =
                err instanceof Error
                    ? err.message
                    : "An error occurred while fetching organizations";
            setError(errorMessage);
            toast.error(errorMessage, {
                style: {
                    backgroundColor: "var(--destructive)",
                    color: "white",
                    border: "none",
                },
            });
        } finally {
            setIsLoading(false);
        }
    };

    const fetchMemberships = useCallback(async () => {
        setIsMembershipsLoading(true);
        setMembershipError(null);

        try {
            const accessToken = Cookies.get("access_token");
            if (!accessToken) {
                throw new Error("Authentication token not found");
            }

            const response = await fetch(
                `${process.env.NEXT_PUBLIC_API_URL}/organizations/memberships/`,
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
                throw new Error(data.error || "Failed to fetch memberships");
            }

            const ownedOrgIds = organizations.map((org) => org.id);
            const memberOnlyOrgs = (data.organizations || []).filter(
                (org: Organization) => !ownedOrgIds.includes(org.id)
            );

            setMemberOrganizations(memberOnlyOrgs);
        } catch (err) {
            const errorMessage =
                err instanceof Error ? err.message : "An error occurred while fetching memberships";
            setMembershipError(errorMessage);
            toast.error(errorMessage, {
                style: {
                    backgroundColor: "var(--destructive)",
                    color: "white",
                    border: "none",
                },
            });
        } finally {
            setIsMembershipsLoading(false);
        }
    }, [organizations]);

    useEffect(() => {
        fetchOrganizations();
    }, []);

    useEffect(() => {
        if (!isLoading) {
            fetchMemberships();
        }
    }, [isLoading, organizations, fetchMemberships]);

    const handleOrganizationCreated = (newOrganization: Organization) => {
        setOrganizations((prevOrganizations) => [newOrganization, ...prevOrganizations]);
    };

    const handleCreateOrganizationClick = () => {
        setIsModalOpen(true);
    };

    const renderContent = () => {
        if (isLoading) {
            return (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {[...Array(3)].map((_, index) => (
                        <OrganizationCardSkeleton key={`skeleton-${index}`} index={index} />
                    ))}
                </div>
            );
        }

        if (error) {
            return (
                <div className="flex flex-col items-center justify-center p-8 text-center">
                    <div className="h-12 w-12 rounded-full bg-(--destructive)/10 flex items-center justify-center mb-4">
                        <AlertCircle className="h-6 w-6 text-(--destructive)" />
                    </div>
                    <h3 className="text-lg font-semibold mb-2">Failed to load organizations</h3>
                    <p className="text-sm text-(--muted-foreground) mb-4 max-w-md">{error}</p>
                    <button
                        onClick={() => fetchOrganizations()}
                        className="px-4 py-2 rounded-md bg-(--primary) text-(--primary-foreground) hover:bg-(--primary)/90 transition-colors"
                    >
                        Retry
                    </button>
                </div>
            );
        }

        if (organizations.length === 0) {
            return (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    <CreateOrganizationCard index={0} onClick={handleCreateOrganizationClick} />
                </div>
            );
        }

        return (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {organizations.map((org, index) => (
                    <OrganizationCard key={org.id} organization={org} index={index} />
                ))}
                <CreateOrganizationCard
                    index={organizations.length}
                    onClick={handleCreateOrganizationClick}
                />
            </div>
        );
    };

    const renderMemberships = () => {
        if (isMembershipsLoading && !memberOrganizations.length) {
            return (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {[...Array(2)].map((_, index) => (
                        <OrganizationCardSkeleton key={`member-skeleton-${index}`} index={index} />
                    ))}
                </div>
            );
        }

        if (membershipError) {
            return (
                <div className="flex flex-col items-center justify-center p-8 text-center">
                    <div className="h-12 w-12 rounded-full bg-(--destructive)/10 flex items-center justify-center mb-4">
                        <AlertCircle className="h-6 w-6 text-(--destructive)" />
                    </div>
                    <h3 className="text-lg font-semibold mb-2">Failed to load memberships</h3>
                    <p className="text-sm text-(--muted-foreground) mb-4 max-w-md">
                        {membershipError}
                    </p>
                    <button
                        onClick={() => fetchMemberships()}
                        className="px-4 py-2 rounded-md bg-(--primary) text-(--primary-foreground) hover:bg-(--primary)/90 transition-colors"
                    >
                        Retry
                    </button>
                </div>
            );
        }

        if (memberOrganizations.length === 0) {
            return (
                <div className="flex flex-col items-center justify-center p-8 text-center">
                    <p className="text-sm text-(--muted-foreground)">
                        You are not a member of any organizations yet.
                    </p>
                </div>
            );
        }

        const handleOrganizationClick = (org: Organization) => {
            setSelectedOrganization(org);
            setIsDetailsModalOpen(true);
        };

        return (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {memberOrganizations.map((org, index) => (
                    <div
                        key={org.id}
                        onClick={() => handleOrganizationClick(org)}
                        className="cursor-pointer"
                    >
                        <OrganizationCard organization={org} index={index} disableLink={true} />
                    </div>
                ))}
            </div>
        );
    };

    const shouldShowMembershipsSection =
        !isLoading && (memberOrganizations.length > 0 || membershipError || isMembershipsLoading);

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
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.5, delay: 0.1 }}
                            className="space-y-6"
                        >
                            <div className="flex items-center space-x-3">
                                <Building2 className="h-6 w-6 text-(--primary)" />
                                <h2 className="text-2xl font-bold tracking-tight">
                                    Your Organizations
                                </h2>
                            </div>

                            {renderContent()}
                        </motion.div>

                        {shouldShowMembershipsSection && (
                            <motion.div
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ duration: 0.5, delay: 0.2 }}
                                className="space-y-6"
                            >
                                <div className="flex items-center space-x-3">
                                    <Users className="h-6 w-6 text-(--primary)" />
                                    <h2 className="text-2xl font-bold tracking-tight">
                                        Member Organizations
                                    </h2>
                                </div>

                                {renderMemberships()}
                            </motion.div>
                        )}

                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.5, delay: 0.3 }}
                            className="space-y-6"
                        >
                            <div className="flex items-center space-x-3">
                                <MailQuestion className="h-6 w-6 text-(--primary)" />
                                <h2 className="text-2xl font-bold tracking-tight">
                                    Pending Ownership Transfers
                                </h2>
                            </div>

                            <ReceivedTransfersSection userId={user?.id || ""} />
                        </motion.div>
                    </motion.div>
                </div>

                <CreateOrganizationModal
                    open={isModalOpen}
                    onOpenChange={setIsModalOpen}
                    onOrganizationCreated={handleOrganizationCreated}
                />

                <OrganizationDetailsModal
                    open={isDetailsModalOpen}
                    onOpenChange={setIsDetailsModalOpen}
                    organization={selectedOrganization}
                />
            </div>
        </ProtectedRoute>
    );
}
