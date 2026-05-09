"use client";

import React, { useState } from "react";
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
import { orchestrateBorrow } from "@/lib/api";
import { BorrowResponse } from "@/types";
import { Loader2, CheckCircle2, AlertCircle, Search } from "lucide-react";

interface AskAIDialogProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
}

export function AskAIDialog({ isOpen, onOpenChange }: AskAIDialogProps) {
  const [itemName, setItemName] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<BorrowResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleClose = (open: boolean) => {
    if (!open) {
      setTimeout(() => {
        setItemName("");
        setResult(null);
        setError(null);
      }, 300);
    }
    onOpenChange(open);
  };

  const handleSubmit = async () => {
    if (!itemName.trim()) return;

    setLoading(true);
    setResult(null);
    setError(null);

    try {
      const now = new Date();
      const start = new Date(now.getTime() + 2 * 60 * 60 * 1000);
      const end = new Date(now.getTime() + 6 * 60 * 60 * 1000);

      const res = await orchestrateBorrow({
        item_name: itemName,
        borrower_id: "demo-borrower-001",
        requested_start: start.toISOString(),
        requested_end: end.toISOString(),
      });
      setResult(res);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>🤖 Ask AI to Find an Item</DialogTitle>
          <DialogDescription>
            Describe what you need, and the AI Matchmaker will search your
            neighbourhood inventory.
          </DialogDescription>
        </DialogHeader>

        {!result && !error && (
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <label htmlFor="item-name" className="text-sm font-medium">
                What do you need?
              </label>
              <Input
                id="item-name"
                value={itemName}
                onChange={(e) => setItemName(e.target.value)}
                placeholder='e.g., "power drill", "camping tent", "projector"'
                disabled={loading}
                onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
                autoFocus
              />
            </div>
          </div>
        )}

        {result && (
          <div className="py-4">
            <div
              className={`p-4 rounded-lg border flex items-start gap-3 ${
                result.success
                  ? "bg-green-500/10 border-green-500/20"
                  : "bg-yellow-500/10 border-yellow-500/20"
              }`}
            >
              {result.success ? (
                <CheckCircle2 className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
              ) : (
                <AlertCircle className="w-5 h-5 text-yellow-500 mt-0.5 flex-shrink-0" />
              )}
              <div>
                <p className="font-semibold text-sm">
                  {result.success ? "Match Found!" : "No Local Match"}
                </p>
                <p className="text-sm mt-1 opacity-80">{result.message}</p>
                {result.transaction_id && (
                  <p className="text-xs mt-2 font-mono opacity-60">
                    TX: {result.transaction_id}
                  </p>
                )}
              </div>
            </div>
          </div>
        )}

        {error && (
          <div className="py-4">
            <div className="p-4 rounded-lg border bg-red-500/10 border-red-500/20 flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" />
              <div>
                <p className="font-semibold text-sm">Error</p>
                <p className="text-sm mt-1 opacity-80">{error}</p>
              </div>
            </div>
          </div>
        )}

        <DialogFooter>
          {!result && !error ? (
            <Button
              onClick={handleSubmit}
              disabled={loading || !itemName.trim()}
              className="w-full sm:w-auto"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  AI is searching...
                </>
              ) : (
                <>
                  <Search className="w-4 h-4 mr-2" />
                  Search Neighbourhood
                </>
              )}
            </Button>
          ) : (
            <Button onClick={() => handleClose(false)} className="w-full sm:w-auto">
              Done
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
