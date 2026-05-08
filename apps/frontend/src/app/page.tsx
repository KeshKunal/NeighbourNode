"use client";

import React, { useState } from "react";
import dynamic from "next/dynamic";
import { ItemCard } from "@/components/ItemCard";
import { mockItems, mockUsers } from "@/lib/mockData";
import { Button } from "@/components/ui/button";
import { Map as MapIcon } from "lucide-react";
import { motion } from "framer-motion";

// Dynamically import Map with SSR disabled
const Map = dynamic(() => import("@/components/Map"), { ssr: false });

const containerVariants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
};

export default function Home() {
  const [showMap, setShowMap] = useState(true);

  return (
    <div className="flex flex-col lg:flex-row h-[calc(100vh-4rem)] overflow-hidden">
      {/* Map Section */}
      <div 
        className={`transition-all duration-500 ease-in-out relative border-b lg:border-b-0 lg:border-r border-border/40
          ${showMap ? "w-full lg:w-1/2 h-[40vh] lg:h-full opacity-100" : "w-0 h-0 opacity-0 overflow-hidden"}
        `}
      >
        <Map />
      </div>

      {/* Catalog Grid Section */}
      <div 
        className={`transition-all duration-500 ease-in-out h-full overflow-y-auto bg-background/50
          ${showMap ? "w-full lg:w-1/2" : "w-full"}
        `}
      >
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-3xl font-bold tracking-tight">Catalog</h2>
              <p className="text-muted-foreground mt-1">
                Browse items available to borrow in your neighbourhood.
              </p>
            </div>
            <Button 
              variant={showMap ? "secondary" : "outline"} 
              onClick={() => setShowMap(!showMap)}
              className="hidden lg:flex"
            >
              <MapIcon className="w-4 h-4 mr-2" />
              {showMap ? "Hide Map" : "Show Map"}
            </Button>
          </div>
          
          {/* Mobile toggle button */}
          <div className="lg:hidden mb-4">
             <Button 
              variant={showMap ? "secondary" : "outline"} 
              onClick={() => setShowMap(!showMap)}
              className="w-full"
            >
              <MapIcon className="w-4 h-4 mr-2" />
              {showMap ? "Hide Map" : "Show Map"}
            </Button>
          </div>
          
          <motion.div 
            variants={containerVariants}
            initial="hidden"
            animate="show"
            className={`grid grid-cols-1 gap-6 ${showMap ? "sm:grid-cols-2" : "sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4"}`}
          >
            {mockItems.map((item) => {
              const owner = mockUsers.find((u) => u.id === item.owner_id);
              return <ItemCard key={item.id} item={item} owner={owner} />;
            })}
          </motion.div>
        </div>
      </div>
    </div>
  );
}
