"use client";

import React, { useState, useEffect } from "react";
import { Search, X, Loader2, Filter, Sparkles, SlidersHorizontal } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ItemCard } from "@/components/ItemCard";
import { resourcesApi } from "@/lib/api";
import { Resource } from "@/types";
import { motion } from "framer-motion";

const CATEGORIES = [
  "All",
  "Tools and equipment",
  "Electronics",
  "Books and study material",
  "Travel and camping",
  "Sports equipment",
  "Kitchen equipment",
  "Household items",
];

export function SmartSearch() {
  const [searchQuery, setSearchQuery] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [results, setResults] = useState<Resource[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Debounce logic (300ms)
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(searchQuery);
    }, 300);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Fetch logic from MongoDB
  useEffect(() => {
    async function fetchItems() {
      setIsLoading(true);
      setError(null);
      try {
        const data = await resourcesApi.list({
          search: debouncedQuery.trim() || undefined,
          category: selectedCategory === "All" ? undefined : selectedCategory,
        });
        setResults(data || []);
      } catch (err: any) {
        console.error("MongoDB resource search error:", err);
        setError("Failed to fetch community resources from MongoDB.");
      } finally {
        setIsLoading(false);
      }
    }
    fetchItems();
  }, [debouncedQuery, selectedCategory]);

  return (
    <div className="w-full space-y-6">
      {/* Search Input & Category Bar */}
      <div className="space-y-4">
        <div className="relative max-w-2xl">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            type="text"
            placeholder="Search power drill, tent, monitor, books, badminton..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-11 pr-10 h-12 text-sm rounded-2xl shadow-sm border-border/70 focus-visible:ring-1"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery("")}
              className="absolute right-3.5 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground p-1"
              aria-label="Clear search"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Categories */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-2 scrollbar-none">
          {CATEGORIES.map((cat) => {
            const isSelected = selectedCategory === cat;
            return (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-3.5 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-all ${
                  isSelected
                    ? "bg-primary text-primary-foreground shadow-sm"
                    : "bg-muted/60 text-muted-foreground hover:bg-muted hover:text-foreground border border-border/40"
                }`}
              >
                {cat}
              </button>
            );
          })}
        </div>
      </div>

      {/* Error State */}
      {error && (
        <div className="p-4 bg-destructive/10 text-destructive rounded-xl border border-destructive/20 text-xs">
          {error}
        </div>
      )}

      {/* Results Header */}
      <div className="flex items-center justify-between text-xs text-muted-foreground pt-1">
        <span>
          Showing <strong className="text-foreground">{results.length}</strong> available item(s)
          {selectedCategory !== "All" && ` in ${selectedCategory}`}
        </span>
      </div>

      {/* Loading Skeleton */}
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-5">
          {[1, 2, 3, 4, 5, 6].map((n) => (
            <div key={n} className="rounded-2xl border border-border/40 bg-card h-80 animate-pulse p-4 space-y-3">
              <div className="h-44 bg-muted rounded-xl" />
              <div className="h-4 bg-muted rounded w-3/4" />
              <div className="h-3 bg-muted rounded w-1/2" />
            </div>
          ))}
        </div>
      ) : results.length > 0 ? (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-5"
        >
          {results.map((item) => (
            <ItemCard key={item.id} item={item} />
          ))}
        </motion.div>
      ) : (
        /* Empty State */
        <div className="py-16 text-center space-y-3 border border-dashed border-border/70 rounded-2xl p-8 bg-muted/20">
          <div className="w-12 h-12 rounded-full bg-muted flex items-center justify-center mx-auto text-muted-foreground">
            <Search className="w-6 h-6" />
          </div>
          <h3 className="font-semibold text-base">No items found</h3>
          <p className="text-xs text-muted-foreground max-w-sm mx-auto">
            Try adjusting your search terms or filter categories to discover items in your neighbourhood.
          </p>
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              setSearchQuery("");
              setSelectedCategory("All");
            }}
            className="text-xs mt-2"
          >
            Reset Filters
          </Button>
        </div>
      )}
    </div>
  );
}
