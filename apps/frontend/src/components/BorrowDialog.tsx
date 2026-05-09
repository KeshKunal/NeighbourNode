import React, { useState } from "react";
import { Item } from "@/types";
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
import { CheckCircle2, Circle, Loader2, AlertCircle } from "lucide-react";
import { borrowItem } from "@/lib/api";

interface BorrowDialogProps {
  item: Item;
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
}

export function BorrowDialog({ item, isOpen, onOpenChange }: BorrowDialogProps) {
  // 0: Form, 1: Sending, 2: AI Negotiating, 3: Waiting Approval, 4: Scheduled, -1: Error
  const [step, setStep] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [txId, setTxId] = useState<string | null>(null);
  const [dateValue, setDateValue] = useState("");

  const handleOpenChange = (open: boolean) => {
    if (!open) {
      setTimeout(() => {
        setStep(0);
        setError(null);
        setTxId(null);
        setDateValue("");
      }, 300);
    }
    onOpenChange(open);
  };

  const handleConfirm = async () => {
    setStep(1);
    setError(null);

    try {
      const now = new Date();
      const start = dateValue
        ? new Date(dateValue)
        : new Date(now.getTime() + 2 * 60 * 60 * 1000);
      const end = new Date(start.getTime() + 4 * 60 * 60 * 1000);

      const result = await borrowItem({
        item_id: item.id,
        borrower_id: "demo-borrower-001", // In production: from auth context
        requested_start: start.toISOString(),
        requested_end: end.toISOString(),
      });

      if (result.success) {
        setTxId(result.transaction_id || null);
        setStep(3); // Waiting for owner approval
      } else {
        setError(result.message);
        setStep(-1);
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Something went wrong");
      setStep(-1);
    }
  };

  const trackerSteps = [
    { label: "Request sent to AI Orchestrator" },
    { label: "Owner notified via Telegram" },
    { label: "Waiting for owner approval" },
    { label: "Calendar invite & handover scheduled" },
  ];

  return (
    <Dialog open={isOpen} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Request {item.title || item.name}</DialogTitle>
          <DialogDescription>
            {step === 0
              ? "Fill out the details below to request this item."
              : step === -1
              ? "Something went wrong with your request."
              : "Track the status of your request in real-time."}
          </DialogDescription>
        </DialogHeader>

        {step === 0 ? (
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <label htmlFor="date" className="text-sm font-medium leading-none">
                When do you need this?
              </label>
              <Input
                id="date"
                type="datetime-local"
                className="col-span-3"
                value={dateValue}
                onChange={(e) => setDateValue(e.target.value)}
              />
            </div>
            <div className="grid gap-2">
              <label htmlFor="message" className="text-sm font-medium leading-none">
                Message to owner (Optional)
              </label>
              <Textarea
                id="message"
                placeholder="E.g., I just need it for a couple of hours for a DIY project!"
                className="resize-none"
              />
            </div>
          </div>
        ) : step === -1 ? (
          <div className="py-6">
            <div className="p-4 rounded-lg border bg-red-500/10 border-red-500/20 flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" />
              <div>
                <p className="font-semibold text-sm">Request Failed</p>
                <p className="text-sm mt-1 opacity-80">{error}</p>
              </div>
            </div>
          </div>
        ) : (
          <div className="py-6 flex flex-col gap-4">
            {trackerSteps.map((s, index) => {
              const stepNumber = index + 1;
              const isActive = step === stepNumber;
              const isCompleted = step > stepNumber;

              return (
                <div key={stepNumber} className="flex items-center gap-3">
                  <div className="flex-shrink-0 flex items-center justify-center w-6 h-6">
                    {isCompleted ? (
                      <CheckCircle2 className="w-5 h-5 text-green-500" />
                    ) : isActive ? (
                      <Loader2 className="w-5 h-5 text-primary animate-spin" />
                    ) : (
                      <Circle className="w-5 h-5 text-muted-foreground opacity-50" />
                    )}
                  </div>
                  <span
                    className={`text-sm ${
                      isActive
                        ? "font-medium text-foreground"
                        : isCompleted
                        ? "text-muted-foreground line-through"
                        : "text-muted-foreground opacity-70"
                    }`}
                  >
                    {s.label}
                  </span>
                </div>
              );
            })}
            {txId && (
              <p className="text-xs font-mono text-muted-foreground mt-2">
                TX: {txId}
              </p>
            )}
          </div>
        )}

        <DialogFooter className="flex-col sm:flex-row gap-2 sm:gap-0 mt-4">
          {step === 0 ? (
            <Button type="button" onClick={handleConfirm} className="w-full sm:w-auto">
              Confirm Request
            </Button>
          ) : step === 1 ? (
            <Button disabled className="w-full sm:w-auto">
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Sending...
            </Button>
          ) : step === -1 ? (
            <Button type="button" variant="outline" onClick={() => setStep(0)} className="w-full sm:w-auto">
              Try Again
            </Button>
          ) : (
            <Button type="button" onClick={() => handleOpenChange(false)} className="w-full sm:w-auto">
              Done
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
