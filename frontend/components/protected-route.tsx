"use client";

import { useAppDispatch } from "@/app/store/hooks";
import { isAuthenticated, refreshAccessToken } from "@/lib/auth";
import { Loader2 } from "lucide-react";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

interface ProtectedRouteProps {
    children: React.ReactNode;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
    const router = useRouter();
    const pathname = usePathname();
    const dispatch = useAppDispatch();
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const checkAuth = async () => {
            setIsLoading(true);

            if (!isAuthenticated()) {
                router.push("/auth/login");
                return;
            }

            const refreshed = await refreshAccessToken(dispatch);

            if (!refreshed) {
                router.push("/auth/login");
                return;
            }

            setIsLoading(false);
        };

        checkAuth();
    }, [router, dispatch, pathname]);

    if (isLoading) {
        return (
            <div className="min-h-screen flex flex-col items-center justify-center bg-(--background)">
                <div className="flex flex-col items-center space-y-4">
                    <Loader2 className="h-12 w-12 text-(--primary) animate-spin" />
                    <p className="text-center text-(--foreground)">Verifying your session...</p>
                </div>
            </div>
        );
    }

    return <>{children}</>;
}
