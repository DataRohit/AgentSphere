"use client";

import { CreateOrganizationModal } from "@/components/create-organization-modal";
import { DashboardNavbar } from "@/components/dashboard-navbar";
import {
    CreateOrganizationCard,
    Organization,
    OrganizationCard,
    OrganizationCardSkeleton,
} from "@/components/organization-card";
import { ProtectedRoute } from "@/components/protected-route";
import { motion } from "framer-motion";
import Cookies from "js-cookie";
import { AlertCircle, Building2 } from "lucide-react";
import { useEffect, useState } from "react";
import { toast } from "sonner";

export default function DashboardPage() {
    const [organizations, setOrganizations] = useState<Organization[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [isModalOpen, setIsModalOpen] = useState(false);

    const fetchOrganizations = async () => {
        setIsLoading(true);
        setError(null);

        try {
            const accessToken = Cookies.get("access_token");
            if (!accessToken) {
                throw new Error("Authentication token not found");
            }

            const response = await fetch("http://localhost:8080/api/v1/organizations/owned/", {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${accessToken}`,
                },
            });

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

    useEffect(() => {
        fetchOrganizations();
    }, []);

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
                        <div className="flex items-center space-x-3">
                            <Building2 className="h-6 w-6 text-(--primary)" />
                            <h2 className="text-2xl font-bold tracking-tight">
                                Your Organizations
                            </h2>
                        </div>

                        {renderContent()}
                    </motion.div>
                </div>

                <CreateOrganizationModal
                    open={isModalOpen}
                    onOpenChange={setIsModalOpen}
                    onOrganizationCreated={handleOrganizationCreated}
                />
            </div>
        </ProtectedRoute>
    );
}
