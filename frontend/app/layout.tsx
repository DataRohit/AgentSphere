import type { Metadata } from "next";
import { JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";

const jetbrainsMono = JetBrains_Mono({
    variable: "--font-jetbrains-mono",
    subsets: ["latin"],
    weight: ["300", "400", "500", "600", "700"],
});

export const metadata: Metadata = {
    title: "AgentSphere",
    description:
        "A dynamic AI platform enabling users to interact with agents individually or in groups, create workflows, and integrate MCP tools for seamless task automation.",
};

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="en">
            <body className={`${jetbrainsMono.className} antialiased`}>
                <Providers>{children}</Providers>
            </body>
        </html>
    );
}
