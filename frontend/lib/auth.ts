"use server";

import Cookies from "js-cookie";

export async function isAuthenticated(): Promise<boolean> {
    try {
        const accessToken = Cookies.get("access_token");
        if (!accessToken) return false;

        const apiUrl = process.env.NEXT_PUBLIC_API_URL || "/api/v1";
        const response = await fetch(`${apiUrl}/users/me/`, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${accessToken}`,
            },
        });

        if (!response.ok) return false;

        const data = await response.json();
        return !!data.user;
    } catch (error) {
        return false;
    }
}

export async function refreshAccessToken(dispatch: any): Promise<boolean> {
    try {
        const refreshToken = Cookies.get("refresh_token");
        if (!refreshToken) return false;

        const apiUrl = process.env.NEXT_PUBLIC_API_URL || "/api/v1";
        const response = await fetch(`${apiUrl}/users/relogin/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ refresh: refreshToken }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || "Failed to refresh token");
        }

        const data = await response.json();
        Cookies.set("access_token", data.access);

        if (data.refresh) {
            Cookies.set("refresh_token", data.refresh);
        }

        return true;
    } catch (error) {
        // Clear tokens if refresh fails
        Cookies.remove("access_token");
        Cookies.remove("refresh_token");
        return false;
    }
}
