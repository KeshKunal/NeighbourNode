"use client";

import React from "react";
import dynamic from "next/dynamic";
import { ItemCard } from "@/components/ItemCard";
import { mockItems, mockUsers } from "@/lib/mockData";

// Dynamically import Map with SSR disabled
const Map = dynamic(() => import("@/components/Map"), { ssr: false });

export default function Home() {
  return (
    <div className="flex flex-col lg:flex-row h-[calc(100vh-4rem)]">
      {/* Map Section: Left on desktop, Top on mobile */}
      <div className="w-full lg:w-1/2 h-[40vh] lg:h-full relative border-b lg:border-b-0 lg:border-r border-border/40">
        <Map />
      </div>

      {/* Catalog Grid Section: Right on desktop, Bottom on mobile */}
      <div className="w-full lg:w-1/2 h-[60vh] lg:h-full overflow-y-auto bg-background/50">
        <div className="p-6">
          <div className="mb-6">
            <h2 className="text-3xl font-bold tracking-tight">Catalog</h2>
            <p className="text-muted-foreground mt-1">
              Browse items available to borrow in your neighbourhood.
            </p>
          </div>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            {mockItems.map((item) => {
              const owner = mockUsers.find((u) => u.id === item.owner_id);
              return <ItemCard key={item.id} item={item} owner={owner} />;
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
