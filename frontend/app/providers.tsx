"use client";

import { store } from "@/app/store";
import { setUser, setUserError, setUserLoading } from "@/app/store/slices/userSlice";
import Cookies from "js-cookie";
import { ThemeProvider } from "next-themes";
import { useEffect } from "react";
import { Provider } from "react-redux";

export function Providers({ children }: { children: React.ReactNode }) {
    useEffect(() => {
        const fetchUserData = async () => {
            const accessToken = Cookies.get("access_token");
            if (!accessToken) return;

            try {
                store.dispatch(setUserLoading());
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
                    store.dispatch(setUser(data.user));
                } else {
                    const errorData = await response.json();
                    store.dispatch(setUserError(errorData.error || "Failed to fetch user data"));
                }
            } catch {
                store.dispatch(setUserError("An error occurred while fetching user data"));
            }
        };

        fetchUserData();
    }, []);

    return (
        <Provider store={store}>
            <ThemeProvider
                attribute="class"
                defaultTheme="system"
                enableSystem
                disableTransitionOnChange
            >
                {children}
            </ThemeProvider>
        </Provider>
    );
}
