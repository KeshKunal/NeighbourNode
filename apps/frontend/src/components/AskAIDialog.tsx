"use client";

import React, { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { aiApi } from "@/lib/api";
import { AIAskResponse, Resource, Skill } from "@/types";
import { Loader2, Sparkles, MapPin, Search, ArrowRight, BookOpen, Tool } from "lucide-react";
import { BorrowDialog } from "@/components/BorrowDialog";
import Link from "next/link";

interface AskAIDialogProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
}

export function AskAIDialog({ isOpen, onOpenChange }: AskAIDialogProps) {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<AIAskResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [borrowItem, setBorrowItem] = useState<Resource | null>(null);

  const handleClose = (open: boolean) => {
    if (!open) {
      setTimeout(() => {
        setQuery("");
        setResponse(null);
        setError(null);
      }, 300);
    }
    onOpenChange(open);
  };

  const handleSearch = async (overrideQuery?: string) => {
    const q = overrideQuery || query;
    if (!q.trim()) return;

    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      const res = await aiApi.ask(q.trim());
      setResponse(res);
    } catch (err: any) {
      setError(err.message || "Failed to process query.");
    } finally {
      setLoading(false);
    }
  };

  const samplePrompts = [
    "I need a drill for tomorrow evening",
    "Someone who can teach Python near my apartment",
    "Find a projector available this weekend",
    "Looking for a camping tent for 3 people",
  ];

  return (
    <>
      <Dialog open={isOpen} onOpenChange={handleClose}>
        <DialogContent className="sm:max-w-[580px] max-h-[85vh] overflow-y-auto rounded-2xl p-6">
          <DialogHeader>
            <div className="flex items-center gap-2 mb-1">
              <div className="w-8 h-8 rounded-lg bg-primary/10 text-primary flex items-center justify-center">
                <Sparkles className="w-4 h-4" />
              </div>
              <DialogTitle className="text-xl font-bold">Ask AI Matchmaker</DialogTitle>
            </div>
            <DialogDescription className="text-xs">
              Natural language search across MongoDB community resources and skills in Bengaluru.
            </DialogDescription>
          </DialogHeader>

          {/* Search Box */}
          <div className="space-y-3 pt-2">
            <div className="flex gap-2">
              <Input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder='e.g., "I need a power drill for Saturday morning"'
                onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                disabled={loading}
                className="rounded-xl text-sm h-11"
                autoFocus
              />
              <Button
                onClick={() => handleSearch()}
                disabled={loading || !query.trim()}
                className="h-11 px-5 rounded-xl font-semibold"
              >
                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : "Find"}
              </Button>
            </div>

            {/* Quick Prompts */}
            {!response && !loading && (
              <div className="space-y-1.5 pt-1">
                <span className="text-[11px] text-muted-foreground font-medium">Try asking:</span>
                <div className="flex flex-wrap gap-1.5">
                  {samplePrompts.map((p, idx) => (
                    <button
                      key={idx}
                      onClick={() => {
                        setQuery(p);
                        handleSearch(p);
                      }}
                      className="text-[11px] px-2.5 py-1 rounded-full bg-muted/60 hover:bg-muted text-muted-foreground hover:text-foreground border border-border/50 transition-colors text-left"
                    >
                      "{p}"
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Loading */}
          {loading && (
            <div className="py-12 flex flex-col items-center justify-center space-y-3 text-center">
              <Loader2 className="w-7 h-7 text-primary animate-spin" />
              <p className="text-xs text-muted-foreground">
                Analyzing request intent, searching MongoDB collections & scoring nearby candidates...
              </p>
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="p-3.5 rounded-xl bg-destructive/10 text-destructive text-xs border border-destructive/20 mt-3">
              {error}
            </div>
          )}

          {/* Results */}
          {response && !loading && (
            <div className="space-y-4 pt-3 border-t border-border/40 mt-3">
              {/* Intent & keywords badge */}
              <div className="flex items-center gap-2 flex-wrap">
                <Badge variant="outline" className="text-[11px] font-semibold uppercase">
                  Intent: {response.intent}
                </Badge>
                {response.keywords.map((kw, i) => (
                  <Badge key={i} variant="secondary" className="text-[10px]">
                    #{kw}
                  </Badge>
                ))}
              </div>

              {/* Natural Language Answer */}
              <div className="p-4 rounded-xl bg-muted/60 border border-border/40 text-xs leading-relaxed text-foreground">
                {response.natural_language_answer}
              </div>

              {/* Matched Resources */}
              {response.matched_resources && response.matched_resources.length > 0 && (
                <div className="space-y-2">
                  <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                    Available Community Resources ({response.matched_resources.length})
                  </span>
                  <div className="space-y-2">
                    {response.matched_resources.map((item) => (
                      <div
                        key={item.id}
                        className="p-3.5 rounded-xl border border-border/60 bg-card hover:border-primary/40 transition-colors flex items-center justify-between gap-3"
                      >
                        <div className="min-w-0 flex-1">
                          <h4 className="font-semibold text-sm truncate">{item.title}</h4>
                          <div className="flex items-center gap-2 text-[11px] text-muted-foreground mt-0.5">
                            <span className="font-medium text-foreground">{item.category}</span>
                            <span>•</span>
                            <span className="flex items-center gap-0.5">
                              <MapPin className="w-3 h-3 text-primary" /> {item.locality?.split(",")[0]}
                            </span>
                          </div>
                        </div>

                        <Button
                          size="sm"
                          className="text-xs rounded-lg h-8 px-3.5 font-semibold"
                          onClick={() => {
                            setBorrowItem(item);
                          }}
                        >
                          Borrow
                        </Button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Matched Skills */}
              {response.matched_skills && response.matched_skills.length > 0 && (
                <div className="space-y-2">
                  <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                    Matched Community Skills ({response.matched_skills.length})
                  </span>
                  <div className="space-y-2">
                    {response.matched_skills.map((skill) => (
                      <div
                        key={skill.id}
                        className="p-3.5 rounded-xl border border-border/60 bg-card flex items-center justify-between gap-3"
                      >
                        <div className="min-w-0 flex-1">
                          <h4 className="font-semibold text-sm truncate">{skill.title}</h4>
                          <p className="text-xs text-muted-foreground line-clamp-1 mt-0.5">
                            {skill.description}
                          </p>
                          <div className="flex items-center gap-2 text-[11px] text-muted-foreground mt-1">
                            <Badge variant="outline" className="text-[10px]">
                              {skill.experience_level}
                            </Badge>
                            <span>•</span>
                            <span>{skill.provider?.full_name || "Neighbour"}</span>
                          </div>
                        </div>

                        <Link href="/skills">
                          <Button size="sm" variant="outline" className="text-xs h-8">
                            View Skills
                          </Button>
                        </Link>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Embedded Borrow Modal when user taps Borrow from AI search */}
      {borrowItem && (
        <BorrowDialog
          item={borrowItem}
          isOpen={!!borrowItem}
          onOpenChange={(open) => !open && setBorrowItem(null)}
        />
      )}
    </>
  );
}
