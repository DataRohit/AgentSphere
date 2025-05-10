"use client";

import { Button } from "@/components/ui/button";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
import Cookies from "js-cookie";
import { Check, Cpu, Loader2 } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { toast } from "sonner";

interface LLM {
    id: string;
    base_url: string;
    model: string;
    max_tokens: number;
    organization: {
        id: string;
        name: string;
    };
    user: {
        id: string;
        username: string;
        email: string;
    };
    created_at: string;
    updated_at: string;
}

interface SelectLLMDialogProps {
    open: boolean;
    onOpenChange: (open: boolean, selectedLLMId?: string) => void;
    organizationId: string;
    chatId?: string;
    chatType?: "single" | "group";
}

export function SelectLLMDialog(props: SelectLLMDialogProps) {
    const { open, onOpenChange, organizationId } = props;
    const [llms, setLLMs] = useState<LLM[]>([]);
    const [isLoadingLLMs, setIsLoadingLLMs] = useState(false);
    const [selectedLLMId, setSelectedLLMId] = useState<string | null>(null);
    const [isSubmitting, setIsSubmitting] = useState(false);

    const fetchLLMs = useCallback(async () => {
        setIsLoadingLLMs(true);
        try {
            const accessToken = Cookies.get("access_token");
            if (!accessToken) {
                throw new Error("Authentication token not found");
            }

            const response = await fetch(
                `${process.env.NEXT_PUBLIC_API_URL}/llms/list/me?organization_id=${organizationId}`,
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
                throw new Error(data.error || "Failed to fetch LLMs");
            }

            setLLMs(data.llms || []);
            if (data.llms && data.llms.length > 0) {
                setSelectedLLMId(data.llms[0].id);
            }
        } catch (err) {
            const errorMessage =
                err instanceof Error ? err.message : "An error occurred while fetching LLMs";
            toast.error(errorMessage, {
                style: {
                    backgroundColor: "var(--destructive)",
                    color: "white",
                    border: "none",
                },
            });
        } finally {
            setIsLoadingLLMs(false);
        }
    }, [organizationId]);

    useEffect(() => {
        if (open) {
            fetchLLMs();
            setSelectedLLMId(null);
        }
    }, [open, organizationId, fetchLLMs]);

    const handleLLMSelection = (llmId: string) => {
        setSelectedLLMId(llmId);
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!selectedLLMId) {
            toast.error("Please select an LLM", {
                style: {
                    backgroundColor: "var(--destructive)",
                    color: "white",
                    border: "none",
                },
            });
            return;
        }

        setIsSubmitting(true);
        try {
            onOpenChange(false, selectedLLMId);
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <Dialog open={open} onOpenChange={(open) => onOpenChange(open, undefined)}>
            <DialogContent className="sm:max-w-[500px] bg-(--background) border-(--border) [&_[data-slot=dialog-close]]:hover:opacity-100 [&_[data-slot=dialog-close]]:cursor-pointer [&_[data-slot=dialog-close]]:transition-opacity [&_[data-slot=dialog-close]]:duration-200">
                <DialogHeader>
                    <DialogTitle className="flex items-center pb-2 text-left">
                        <Cpu className="mr-2 h-5 w-5 text-(--primary)" />
                        Select Language Model
                    </DialogTitle>
                    <DialogDescription className="text-left">
                        Select a language model for conversation summary generation.
                    </DialogDescription>
                </DialogHeader>
                <form onSubmit={handleSubmit} className="space-y-6">
                    <div className="space-y-4">
                        {isLoadingLLMs ? (
                            <div className="flex items-center justify-center p-4 bg-(--secondary) rounded-md">
                                <Loader2 className="h-4 w-4 animate-spin text-(--muted-foreground)" />
                                <span className="ml-2">Loading language models...</span>
                            </div>
                        ) : llms.length === 0 ? (
                            <div className="p-4 text-center text-(--muted-foreground) bg-(--secondary) rounded-md">
                                No language models available
                            </div>
                        ) : (
                            <div className="max-h-[300px] overflow-y-auto custom-scrollbar">
                                <div className="grid grid-cols-1 gap-2">
                                    {llms.map((llm) => (
                                        <div
                                            key={llm.id}
                                            className={`p-3 rounded-md border cursor-pointer transition-all duration-200 ${
                                                selectedLLMId === llm.id
                                                    ? "border-(--primary) bg-(--primary)/10"
                                                    : "border-(--border) bg-(--secondary) hover:border-(--primary)/50"
                                            }`}
                                            onClick={() => handleLLMSelection(llm.id)}
                                        >
                                            <div className="flex items-center justify-between">
                                                <div className="flex items-center">
                                                    <Cpu className="mr-2 h-4 w-4 text-(--primary)" />
                                                    <span className="font-medium text-sm truncate w-64">
                                                        {llm.model}
                                                    </span>
                                                </div>
                                                {selectedLLMId === llm.id && (
                                                    <Check className="h-4 w-4 text-(--primary)" />
                                                )}
                                            </div>
                                            <div className="text-xs text-(--muted-foreground) mt-1 truncate">
                                                {llm.base_url}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                    <DialogFooter className="flex flex-col sm:flex-row sm:justify-between w-full gap-2">
                        <Button
                            type="button"
                            variant="outline"
                            onClick={() => onOpenChange(false, undefined)}
                            disabled={isSubmitting}
                            className="font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--border) bg-(--background) text-(--foreground) hover:bg-(--muted) h-10 cursor-pointer w-full sm:flex-1"
                        >
                            <span className="relative z-10">Cancel</span>
                            <span className="absolute inset-0 bg-(--muted)/50 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                        </Button>
                        <Button
                            type="submit"
                            disabled={isSubmitting || !selectedLLMId}
                            className="font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--primary) bg-(--primary) text-(--primary-foreground) dark:bg-(--primary) dark:text-(--primary-foreground) dark:border-(--primary) h-10 cursor-pointer w-full sm:flex-1"
                        >
                            <span className="relative z-10">
                                {isSubmitting ? (
                                    <>
                                        <Loader2 className="mr-2 h-4 w-4 animate-spin inline" />
                                        Continuing...
                                    </>
                                ) : (
                                    "Continue Chat"
                                )}
                            </span>
                            <span className="absolute inset-0 bg-(--primary-foreground)/10 dark:bg-(--primary-foreground)/20 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                        </Button>
                    </DialogFooter>
                </form>
            </DialogContent>
        </Dialog>
    );
}
