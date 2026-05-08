"use client";

import React, { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { ItemCard } from "@/components/ItemCard";
import { BorrowDialog } from "@/components/BorrowDialog";
import { mockItems, mockUsers } from "@/lib/mockData";
import { fetchItems } from "@/lib/api";
import { Item } from "@/types";

// Dynamically import Map with SSR disabled
const Map = dynamic(() => import("@/components/Map"), { ssr: false });

export default function Home() {
  const [items, setItems] = useState<Item[]>(mockItems);
  const [loading, setLoading] = useState(true);
  const [usingLiveData, setUsingLiveData] = useState(false);
  const [borrowDialogOpen, setBorrowDialogOpen] = useState(false);

  useEffect(() => {
    fetchItems()
      .then((data) => {
        if (data && data.length > 0) {
          // Map backend items to include display-friendly fields
          const mapped = data.map((item) => ({
            ...item,
            status: item.current_status || item.status || "available",
            location_lat: item.location_lat ?? 40.7128 + Math.random() * 0.002,
            location_lng: item.location_lng ?? -74.006 + Math.random() * 0.002,
          }));
          setItems(mapped as Item[]);
          setUsingLiveData(true);
        }
      })
      .catch(() => {
        // Fallback to mock data silently
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="flex flex-col lg:flex-row h-[calc(100vh-4rem)]">
      {/* Map Section */}
      <div className="w-full lg:w-1/2 h-[40vh] lg:h-full relative border-b lg:border-b-0 lg:border-r border-border/40">
        <Map />
        {/* Floating Borrow Button */}
        <button
          onClick={() => setBorrowDialogOpen(true)}
          className="absolute bottom-6 right-6 z-[1000] bg-primary text-primary-foreground px-6 py-3 rounded-full font-semibold shadow-lg hover:opacity-90 transition-all hover:scale-105 flex items-center gap-2"
        >
          <span className="text-lg">🔍</span> Ask AI to Find
        </button>
      </div>

      {/* Catalog Grid Section */}
      <div className="w-full lg:w-1/2 h-[60vh] lg:h-full overflow-y-auto bg-background/50">
        <div className="p-6">
          <div className="mb-6 flex items-center justify-between">
            <div>
              <h2 className="text-3xl font-bold tracking-tight">Catalog</h2>
              <p className="text-muted-foreground mt-1">
                Browse items available to borrow in your neighbourhood.
              </p>
            </div>
            {usingLiveData && (
              <span className="text-xs bg-green-500/10 text-green-600 dark:text-green-400 px-3 py-1 rounded-full font-medium">
                ● Live from Supabase
              </span>
            )}
            {!usingLiveData && !loading && (
              <span className="text-xs bg-yellow-500/10 text-yellow-600 dark:text-yellow-400 px-3 py-1 rounded-full font-medium">
                ● Demo Data
              </span>
            )}
          </div>

          {loading ? (
            <div className="flex items-center justify-center h-40">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              {items.map((item) => {
                const owner = mockUsers.find((u) => u.id === item.owner_id);
                return <ItemCard key={item.id} item={item} owner={owner} />;
              })}
            </div>
          )}
        </div>
      </div>

      {/* Borrow Dialog */}
      <BorrowDialog
        open={borrowDialogOpen}
        onClose={() => setBorrowDialogOpen(false)}
      />
    </div>
  );
}
