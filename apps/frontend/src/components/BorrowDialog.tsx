"use client";

import React, { useState } from "react";
import { orchestrateBorrow } from "@/lib/api";
import { BorrowResponse } from "@/types";

interface BorrowDialogProps {
  open: boolean;
  onClose: () => void;
}

export function BorrowDialog({ open, onClose }: BorrowDialogProps) {
  const [itemName, setItemName] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<BorrowResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  if (!open) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!itemName.trim()) return;

    setLoading(true);
    setResult(null);
    setError(null);

    try {
      // Use a demo borrower ID — in production this comes from auth
      const now = new Date();
      const start = new Date(now.getTime() + 2 * 60 * 60 * 1000); // 2hrs from now
      const end = new Date(now.getTime() + 6 * 60 * 60 * 1000); // 6hrs from now

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

  const handleClose = () => {
    setItemName("");
    setResult(null);
    setError(null);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-[2000] flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={handleClose}
      />

      {/* Dialog */}
      <div className="relative bg-card border border-border rounded-2xl shadow-2xl w-full max-w-md mx-4 overflow-hidden">
        {/* Header */}
        <div className="p-6 pb-2">
          <div className="flex items-center justify-between">
            <h3 className="text-xl font-bold">🤖 Ask AI to Find an Item</h3>
            <button
              onClick={handleClose}
              className="text-muted-foreground hover:text-foreground transition-colors text-xl"
            >
              ✕
            </button>
          </div>
          <p className="text-sm text-muted-foreground mt-1">
            Describe what you need, and the AI Matchmaker will search your
            neighbourhood inventory.
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 pt-4 space-y-4">
          <div>
            <label className="text-sm font-medium mb-1.5 block">
              What do you need?
            </label>
            <input
              type="text"
              value={itemName}
              onChange={(e) => setItemName(e.target.value)}
              placeholder='e.g., "power drill", "camping tent", "projector"'
              className="w-full px-4 py-3 rounded-lg border border-input bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring text-sm"
              disabled={loading}
              autoFocus
            />
          </div>

          <button
            type="submit"
            disabled={loading || !itemName.trim()}
            className="w-full bg-primary text-primary-foreground py-3 rounded-lg font-semibold transition-all hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-foreground" />
                AI is searching...
              </>
            ) : (
              <>🔍 Search Neighbourhood</>
            )}
          </button>
        </form>

        {/* Result */}
        {result && (
          <div className="px-6 pb-6">
            <div
              className={`p-4 rounded-lg border ${
                result.success
                  ? "bg-green-500/10 border-green-500/20 text-green-700 dark:text-green-400"
                  : "bg-yellow-500/10 border-yellow-500/20 text-yellow-700 dark:text-yellow-400"
              }`}
            >
              <p className="font-semibold text-sm">
                {result.success ? "✅ Match Found!" : "🔎 No Local Match"}
              </p>
              <p className="text-sm mt-1 opacity-90">{result.message}</p>
              {result.transaction_id && (
                <p className="text-xs mt-2 font-mono opacity-70">
                  TX: {result.transaction_id}
                </p>
              )}
            </div>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="px-6 pb-6">
            <div className="p-4 rounded-lg border bg-red-500/10 border-red-500/20 text-red-700 dark:text-red-400">
              <p className="font-semibold text-sm">❌ Error</p>
              <p className="text-sm mt-1 opacity-90">{error}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
