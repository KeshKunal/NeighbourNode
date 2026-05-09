"use client";

import React, { useState, useEffect, useCallback } from "react";
import { Search, X, Loader2 } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { supabase } from "@/lib/supabase";
import { ItemCard } from "@/components/ItemCard";
import { motion } from "framer-motion";

export function SmartSearch() {
  const [searchQuery, setSearchQuery] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");
  const [results, setResults] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Debounce logic
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(searchQuery);
    }, 400); // 400ms delay

    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Fetch logic
  useEffect(() => {
    async function fetchItems() {
      setIsLoading(true);
      setError(null);
      try {
        if (!debouncedQuery.trim()) {
          // If empty, fetch default catalog items with owner info
          const { data, error: err } = await supabase
            .from("items")
            .select("*, owner:users(*)")
            .eq("current_status", "available")
            .order("created_at", { ascending: false });

          if (err) throw err;
          setResults(data || []);
        } else {
          // If query exists, call custom RPC
          const { data, error: err } = await supabase.rpc("search_items", {
            search_term: debouncedQuery,
          });

          if (err) throw err;
          setResults(data || []);
        }
      } catch (err: any) {
        console.error("Search error:", err);
        setError("Failed to fetch items. Please try again.");
      } finally {
        setIsLoading(false);
      }
    }

    fetchItems();
  }, [debouncedQuery]);

  const clearSearch = () => {
    setSearchQuery("");
  };

  return (
    <div className="w-full space-y-6">
      {/* Search Input */}
      <div className="relative max-w-xl">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
          <Input
            type="text"
            placeholder="Search for items... (e.g. Drill, Ladder)"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10 pr-10 h-12 text-lg rounded-full shadow-sm"
          />
          {searchQuery && (
            <button
              onClick={clearSearch}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          )}
        </div>
      </div>

      {/* Error State */}
      {error && (
        <div className="p-4 bg-destructive/10 text-destructive rounded-lg border border-destructive/20">
          {error}
        </div>
      )}

      {/* Loading State */}
      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
          <span className="ml-3 text-muted-foreground">Searching catalog...</span>
        </div>
      ) : (
        /* Results Grid */
        <div>
          {results.length === 0 ? (
            <div className="text-center py-12 border rounded-xl bg-muted/20">
              <h3 className="text-xl font-semibold mb-2">No items found</h3>
              <p className="text-muted-foreground">
                We couldn't find any items matching "{searchQuery}". Try a different keyword.
              </p>
            </div>
          ) : (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ staggerChildren: 0.1 }}
              className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4"
            >
              {results.map((item) => (
                <ItemCard key={item.id} item={item} owner={item.owner} />
              ))}
            </motion.div>
          )}
        </div>
      )}
    </div>
  );
}
