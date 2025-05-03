import { Navbar } from "@/components/navbar";
import ActivationClient from "./client";

export default async function ActivatePage({
    params,
}: {
    params: Promise<{ uid: string; token: string }>;
}) {
    const { uid, token } = await params;

    return (
        <div className="min-h-screen flex flex-col bg-(--background)">
            <Navbar />
            <ActivationClient uid={uid} token={token} />
        </div>
    );
}
