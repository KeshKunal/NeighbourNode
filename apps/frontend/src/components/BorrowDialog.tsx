"use client";

import React, { useState } from "react";
import { Resource } from "@/types";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { CheckCircle2, Circle, Loader2, AlertCircle, Calendar, MessageSquare } from "lucide-react";
import { borrowApi } from "@/lib/api";
import { useAuth } from "@/lib/authContext";
import { toast } from "sonner";
import Link from "next/link";

interface BorrowDialogProps {
  item: Resource;
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
}

export function BorrowDialog({ item, isOpen, onOpenChange }: BorrowDialogProps) {
  const { user, loginDemo } = useAuth();
  // 0: Form, 1: Submitting, 2: Waiting Approval / Success, -1: Error
  const [step, setStep] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [startDate, setStartDate] = useState(() => {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    tomorrow.setHours(10, 0, 0, 0);
    return tomorrow.toISOString().slice(0, 16);
  });
  const [endDate, setEndDate] = useState(() => {
    const dayAfter = new Date();
    dayAfter.setDate(dayAfter.getDate() + 3);
    dayAfter.setHours(18, 0, 0, 0);
    return dayAfter.toISOString().slice(0, 16);
  });
  const [message, setMessage] = useState("Hi! I would like to borrow this item for a few days. Happy to coordinate pickup.");

  const handleOpenChange = (open: boolean) => {
    if (!open) {
      setTimeout(() => {
        setStep(0);
        setError(null);
      }, 300);
    }
    onOpenChange(open);
  };

  const handleConfirm = async () => {
    if (!user) {
      toast.error("Please sign in or use a demo account to borrow items.");
      return;
    }

    if (user.id === item.owner_id) {
      setError("You cannot borrow your own listing.");
      setStep(-1);
      return;
    }

    setStep(1);
    setError(null);

    try {
      const start = new Date(startDate);
      const end = new Date(endDate);

      if (end <= start) {
        throw new Error("Return date must be after the start date.");
      }

      await borrowApi.createRequest({
        resource_id: item.id,
        requested_start: start.toISOString(),
        requested_end: end.toISOString(),
        message: message.trim(),
      });

      setStep(2);
      toast.success("Borrow request submitted to owner!");
    } catch (err: any) {
      setError(err.message || "Failed to submit request.");
      setStep(-1);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-[480px] rounded-2xl">
        <DialogHeader>
          <DialogTitle className="text-xl font-bold">Request to Borrow</DialogTitle>
          <DialogDescription>
            {item.title || item.name} • {item.locality?.split(",")[0] || "Bengaluru"}
          </DialogDescription>
        </DialogHeader>

        {/* STEP 0: FORM */}
        {step === 0 && (
          <div className="space-y-4 py-2">
            {!user && (
              <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-xs text-amber-700 dark:text-amber-300 flex flex-col gap-2">
                <span>You are currently not signed in. Sign in or continue as Demo Borrower:</span>
                <Button
                  size="sm"
                  variant="outline"
                  className="w-full text-xs h-7"
                  onClick={() => loginDemo("borrower")}
                >
                  ⚡ One-Click Demo Borrower Sign-in
                </Button>
              </div>
            )}

            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-muted-foreground flex items-center gap-1.5">
                  <Calendar className="w-3.5 h-3.5 text-primary" /> Start Date & Time
                </label>
                <Input
                  type="datetime-local"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  className="text-xs"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-muted-foreground flex items-center gap-1.5">
                  <Calendar className="w-3.5 h-3.5 text-primary" /> Return Date & Time
                </label>
                <Input
                  type="datetime-local"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  className="text-xs"
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-muted-foreground flex items-center gap-1.5">
                <MessageSquare className="w-3.5 h-3.5 text-primary" /> Note to Owner
              </label>
              <Textarea
                rows={3}
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Mention how you plan to use it and your preferred pickup time..."
                className="text-xs resize-none"
              />
            </div>

            {item.lending_rules && (
              <div className="p-3 rounded-xl bg-muted/50 border border-border/40 text-[11px] text-muted-foreground space-y-1">
                <span className="font-semibold text-foreground">Owner's Lending Rules:</span>
                <p>{item.lending_rules}</p>
              </div>
            )}
          </div>
        )}

        {/* STEP 1: SUBMITTING */}
        {step === 1 && (
          <div className="py-8 flex flex-col items-center justify-center space-y-3 text-center">
            <Loader2 className="w-8 h-8 text-primary animate-spin" />
            <p className="text-sm font-semibold">Submitting Borrow Request...</p>
            <p className="text-xs text-muted-foreground">Checking MongoDB reservation locks & notifying owner.</p>
          </div>
        )}

        {/* STEP 2: SUCCESS */}
        {step === 2 && (
          <div className="py-6 space-y-4 text-center">
            <div className="w-12 h-12 rounded-full bg-emerald-500/10 text-emerald-600 flex items-center justify-center mx-auto">
              <CheckCircle2 className="w-7 h-7" />
            </div>
            <div>
              <h3 className="font-bold text-lg">Request Sent to Owner!</h3>
              <p className="text-xs text-muted-foreground mt-1 max-w-sm mx-auto">
                The owner has been notified via the community network. You can track this in your dashboard.
              </p>
            </div>
            <div className="p-3 rounded-xl bg-muted text-xs text-left space-y-1">
              <div className="flex justify-between text-muted-foreground">
                <span>Resource:</span> <span className="font-medium text-foreground">{item.title || item.name}</span>
              </div>
              <div className="flex justify-between text-muted-foreground">
                <span>Status:</span> <span className="font-semibold text-amber-600">Pending Approval</span>
              </div>
            </div>
          </div>
        )}

        {/* STEP -1: ERROR */}
        {step === -1 && (
          <div className="py-6 space-y-4 text-center">
            <div className="w-12 h-12 rounded-full bg-destructive/10 text-destructive flex items-center justify-center mx-auto">
              <AlertCircle className="w-7 h-7" />
            </div>
            <div>
              <h3 className="font-bold text-lg text-destructive">Could Not Complete Request</h3>
              <p className="text-xs text-muted-foreground mt-1">{error || "An unexpected error occurred."}</p>
            </div>
          </div>
        )}

        <DialogFooter className="gap-2 sm:gap-0">
          {step === 0 && (
            <>
              <Button variant="outline" size="sm" onClick={() => handleOpenChange(false)}>
                Cancel
              </Button>
              <Button size="sm" onClick={handleConfirm}>
                Submit Request
              </Button>
            </>
          )}

          {step === 2 && (
            <div className="flex w-full gap-2">
              <Button variant="outline" size="sm" className="flex-1" onClick={() => handleOpenChange(false)}>
                Close
              </Button>
              <Link href="/dashboard" className="flex-1">
                <Button size="sm" className="w-full">
                  Go to Dashboard
                </Button>
              </Link>
            </div>
          )}

          {step === -1 && (
            <Button size="sm" onClick={() => setStep(0)} className="w-full">
              Try Again
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
