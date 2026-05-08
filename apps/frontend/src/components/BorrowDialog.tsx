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
import { CheckCircle2, Circle, Loader2 } from "lucide-react";

interface BorrowDialogProps {
  item: Item;
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
}

export function BorrowDialog({ item, isOpen, onOpenChange }: BorrowDialogProps) {
  // 0: Form, 1: Request sent, 2: AI Negotiating, 3: Waiting Approval, 4: Scheduled
  const [step, setStep] = useState(0);

  const handleOpenChange = (open: boolean) => {
    // Reset state when closing
    if (!open) {
      setTimeout(() => setStep(0), 300); // Wait for transition
    }
    onOpenChange(open);
  };

  const advanceState = () => {
    setStep((prev) => Math.min(prev + 1, 4));
  };

  const trackerSteps = [
    { label: "Request sent to AI Matchmaker" },
    { label: "AI negotiating with owner via Telegram" },
    { label: "Waiting for owner approval" },
    { label: "Calendar invite & handover scheduled" },
  ];

  return (
    <Dialog open={isOpen} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Request {item.name}</DialogTitle>
          <DialogDescription>
            {step === 0
              ? "Fill out the details below to request this item."
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
          </div>
        )}

        <DialogFooter className="flex-col sm:flex-row gap-2 sm:gap-0 mt-4">
          {step === 0 ? (
            <Button type="button" onClick={() => setStep(1)} className="w-full sm:w-auto">
              Confirm Request
            </Button>
          ) : step < 4 ? (
            <Button
              type="button"
              variant="outline"
              onClick={advanceState}
              className="w-full sm:w-auto border-dashed border-primary/50 text-primary/70 hover:text-primary hover:border-primary"
            >
              Dev: Advance State
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
