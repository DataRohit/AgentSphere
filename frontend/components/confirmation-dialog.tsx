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
import { Loader2 } from "lucide-react";

interface ConfirmationDialogProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    title: string;
    description: string;
    confirmText: string;
    cancelText?: string;
    onConfirm: () => void;
    isLoading?: boolean;
    variant?: "default" | "destructive";
}

export function ConfirmationDialog({
    open,
    onOpenChange,
    title,
    description,
    confirmText,
    cancelText = "Cancel",
    onConfirm,
    isLoading = false,
    variant = "default",
}: ConfirmationDialogProps) {
    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:max-w-[425px] bg-(--background) border-(--border) [&_[data-slot=dialog-close]]:hover:opacity-100 [&_[data-slot=dialog-close]]:cursor-pointer [&_[data-slot=dialog-close]]:transition-opacity [&_[data-slot=dialog-close]]:duration-200">
                <DialogHeader>
                    <DialogTitle>{title}</DialogTitle>
                    <DialogDescription>{description}</DialogDescription>
                </DialogHeader>
                <DialogFooter>
                    <Button
                        type="button"
                        variant="outline"
                        onClick={() => onOpenChange(false)}
                        disabled={isLoading}
                        className="font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg border border-(--border) bg-(--background) text-(--foreground) hover:bg-(--muted) px-6 h-10 cursor-pointer"
                    >
                        <span className="relative z-10">{cancelText}</span>
                        <span className="absolute inset-0 bg-(--muted)/50 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left"></span>
                    </Button>
                    <Button
                        type="button"
                        variant={variant === "destructive" ? "destructive" : "default"}
                        onClick={onConfirm}
                        disabled={isLoading}
                        className={`font-mono relative overflow-hidden group transition-all duration-300 transform hover:shadow-lg px-6 h-10 cursor-pointer ${
                            variant === "destructive"
                                ? "border border-(--destructive) bg-(--destructive) text-(--destructive-foreground) dark:bg-(--destructive) dark:text-(--destructive-foreground) dark:border-(--destructive)"
                                : "border border-(--primary) bg-(--primary) text-(--primary-foreground) dark:bg-(--primary) dark:text-(--primary-foreground) dark:border-(--primary)"
                        }`}
                    >
                        <span className="relative z-10">
                            {isLoading ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin inline" />
                                    Processing...
                                </>
                            ) : (
                                confirmText
                            )}
                        </span>
                        <span
                            className={`absolute inset-0 ${
                                variant === "destructive"
                                    ? "bg-(--destructive-foreground)/10 dark:bg-(--destructive-foreground)/20"
                                    : "bg-(--primary-foreground)/10 dark:bg-(--primary-foreground)/20"
                            } transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left`}
                        ></span>
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}
