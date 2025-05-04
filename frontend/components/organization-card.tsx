"use client";

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { formatDistanceToNow } from "date-fns";
import { motion } from "framer-motion";
import { Building2, Calendar, ExternalLink, Globe, Users } from "lucide-react";
import { useRouter } from "next/navigation";

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

export interface Organization {
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

export interface OrganizationCardProps {
    organization: Organization;
    index: number;
    disableLink?: boolean;
}

export function OrganizationCard({
    organization,
    index,
    disableLink = false,
}: OrganizationCardProps) {
    const router = useRouter();
    const formattedDate = formatDistanceToNow(new Date(organization.created_at), {
        addSuffix: true,
    });

    const getInitials = (name: string) => {
        return name
            .split(" ")
            .map((part) => part[0])
            .join("")
            .toUpperCase()
            .substring(0, 2);
    };

    const handleCardClick = (e: React.MouseEvent) => {
        if ((e.target as HTMLElement).closest("a") || disableLink) {
            return;
        }
        router.push(`/organizations/${organization.id}`);
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
            whileHover={{ y: -5, transition: { duration: 0.2 } }}
            className="h-full"
        >
            <Card
                className="p-0 pt-6 h-full  border border-(--border) shadow-sm hover:shadow-md transition-all duration-300 overflow-hidden flex flex-col cursor-pointer bg-(--secondary) dark:bg-(--secondary)"
                onClick={handleCardClick}
            >
                <CardHeader className="pb-2 ">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                            <Avatar className="h-10 w-10 border border-(--border)">
                                {organization.logo_url ? (
                                    <AvatarImage
                                        src={organization.logo_url}
                                        alt={organization.name}
                                    />
                                ) : null}
                                <AvatarFallback className="bg-(--primary)/10 text-(--primary)">
                                    {getInitials(organization.name)}
                                </AvatarFallback>
                            </Avatar>
                            <div>
                                <CardTitle className="text-lg font-semibold">
                                    {organization.name}
                                </CardTitle>
                            </div>
                        </div>
                        <Badge
                            variant="outline"
                            className={
                                disableLink
                                    ? "bg-(--secondary)/50 text-(--muted-foreground) border-(--border)"
                                    : "bg-(--primary)/10 text-(--primary) border-(--primary)/20"
                            }
                        >
                            {disableLink ? "Member" : "Owner"}
                        </Badge>
                    </div>
                </CardHeader>
                <CardContent className="flex-1">
                    <CardDescription className="line-clamp-3 mb-4 text-sm">
                        {organization.description || "No description provided"}
                    </CardDescription>

                    <div className="space-y-2">
                        {organization.website && (
                            <div className="flex items-center text-sm">
                                <Globe className="mr-2 h-4 w-4 text-(--primary)" />
                                <a
                                    href={
                                        organization.website.startsWith("http")
                                            ? organization.website
                                            : `https://${organization.website}`
                                    }
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-(--primary) hover:underline flex items-center"
                                >
                                    <span className="truncate max-w-[180px]">
                                        {organization.website.replace(/^https?:\/\//i, "")}
                                    </span>
                                    <ExternalLink className="ml-1 h-3 w-3" />
                                </a>
                            </div>
                        )}
                        <div className="flex items-center text-sm text-(--muted-foreground)">
                            <Users className="mr-2 h-4 w-4" />
                            <span>
                                {organization.member_count}{" "}
                                {organization.member_count === 1 ? "member" : "members"}
                            </span>
                        </div>
                        <div className="flex items-center text-sm text-(--muted-foreground)">
                            <Calendar className="mr-2 h-4 w-4" />
                            <span>Created {formattedDate}</span>
                        </div>
                    </div>
                </CardContent>
                <CardFooter className="pt-2 border-t bg-(--muted)/10 pb-6">
                    <div className="w-full flex justify-end">
                        <span className="text-xs text-(--muted-foreground)">
                            Last updated:{" "}
                            {formatDistanceToNow(new Date(organization.updated_at), {
                                addSuffix: true,
                            })}
                        </span>
                    </div>
                </CardFooter>
            </Card>
        </motion.div>
    );
}

export function CreateOrganizationCard({ index, onClick }: { index: number; onClick: () => void }) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
            whileHover={{ y: -5, transition: { duration: 0.2 } }}
            className="h-full"
            onClick={onClick}
        >
            <Card className="h-full border border-dashed border-(--primary) bg-(--card) hover:bg-(--primary)/5 transition-all duration-300 flex flex-col items-center justify-center p-6 cursor-pointer group">
                <div className="flex flex-col items-center text-center">
                    <div className="h-12 w-12 rounded-full bg-(--primary)/10 flex items-center justify-center mb-4 group-hover:bg-(--primary)/20 transition-colors duration-300">
                        <Building2 className="h-6 w-6 text-(--primary)" />
                    </div>
                    <h3 className="text-lg font-semibold mb-2 group-hover:text-(--primary) transition-colors duration-300">
                        Create New Organization
                    </h3>
                    <p className="text-sm text-(--muted-foreground) mb-4">
                        Start a new organization to collaborate with others
                    </p>
                    <div className="h-8 w-8 rounded-full bg-(--primary) flex items-center justify-center text-(--primary-foreground) group-hover:scale-110 transition-transform duration-300">
                        <span className="text-xl font-bold">+</span>
                    </div>
                </div>
            </Card>
        </motion.div>
    );
}

export function OrganizationCardSkeleton({ index }: { index: number }) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.05 }}
            className="h-full"
        >
            <Card className="h-full border border-(--border) shadow-sm overflow-hidden">
                <CardHeader className="pb-2">
                    <div className="flex items-center space-x-3">
                        <div className="h-10 w-10 rounded-full bg-(--muted) animate-pulse"></div>
                        <div className="h-6 w-40 bg-(--muted) animate-pulse rounded"></div>
                    </div>
                </CardHeader>
                <CardContent>
                    <div className="space-y-2">
                        <div className="h-4 w-full bg-(--muted) animate-pulse rounded"></div>
                        <div className="h-4 w-5/6 bg-(--muted) animate-pulse rounded"></div>
                        <div className="h-4 w-4/6 bg-(--muted) animate-pulse rounded"></div>
                    </div>

                    <div className="mt-6 space-y-2">
                        <div className="h-4 w-24 bg-(--muted) animate-pulse rounded"></div>
                        <div className="h-4 w-32 bg-(--muted) animate-pulse rounded"></div>
                    </div>
                </CardContent>
                <CardFooter className="pt-2 border-t">
                    <div className="w-full flex justify-end">
                        <div className="h-3 w-32 bg-(--muted) animate-pulse rounded"></div>
                    </div>
                </CardFooter>
            </Card>
        </motion.div>
    );
}
