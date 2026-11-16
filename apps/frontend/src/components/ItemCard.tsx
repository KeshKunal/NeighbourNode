"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Resource } from "@/types";
import { Card, CardContent, CardFooter } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { BorrowDialog } from "@/components/BorrowDialog";
import { motion, Variants } from "framer-motion";
import { Image as ImageIcon, MapPin, Star, User } from "lucide-react";

interface ItemCardProps {
  item: Resource;
  owner?: any;
}

const itemVariants: Variants = {
  hidden: { opacity: 0, y: 15 },
  show: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 300, damping: 25 } },
};

export function ItemCard({ item, owner }: ItemCardProps) {
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [imgError, setImgError] = useState(false);

  const status = item.status || (item as any).current_status || "AVAILABLE";
  const isAvailable = status === "AVAILABLE" || status === "available";
  const imageUrl =
    item.images && item.images.length > 0
      ? item.images[0]
      : item.image_url || null;

  const ownerInfo = item.owner || owner;

  return (
    <>
      <motion.div variants={itemVariants} whileHover={{ y: -4 }} className="h-full">
        <Card className="flex flex-col overflow-hidden transition-all duration-200 border-border/60 hover:border-primary/40 shadow-sm hover:shadow-md h-full rounded-2xl group bg-card">
          {/* Image */}
          <div className="relative h-48 w-full bg-muted/60 overflow-hidden">
            {imageUrl && !imgError ? (
              <img
                src={imageUrl}
                alt={item.title || item.name || "Item"}
                onError={() => setImgError(true)}
                className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
              />
            ) : (
              <div className="flex flex-col items-center justify-center w-full h-full text-muted-foreground gap-2">
                <ImageIcon className="w-8 h-8 opacity-40" />
                <span className="text-xs font-medium text-muted-foreground/60">{item.category}</span>
              </div>
            )}

            <div className="absolute top-3 left-3 flex gap-1.5 flex-wrap">
              <Badge variant="secondary" className="backdrop-blur-md bg-background/80 text-[11px] font-medium shadow-sm">
                {item.category}
              </Badge>
              {item.condition && (
                <Badge variant="outline" className="backdrop-blur-md bg-background/80 text-[10px] font-normal shadow-sm">
                  {item.condition}
                </Badge>
              )}
            </div>

            <div className="absolute top-3 right-3">
              <Badge
                className={`text-[11px] font-semibold shadow-sm ${
                  isAvailable
                    ? "bg-emerald-600 hover:bg-emerald-700 text-white"
                    : "bg-amber-600 text-white"
                }`}
              >
                {isAvailable ? "Available" : status.replace("_", " ")}
              </Badge>
            </div>
          </div>

          <CardContent className="flex-1 p-5 flex flex-col justify-between">
            <div>
              <Link href={`/catalog/${item.id}`} className="hover:underline">
                <h3 className="font-semibold text-lg line-clamp-1 group-hover:text-primary transition-colors">
                  {item.title || item.name}
                </h3>
              </Link>
              <p className="text-muted-foreground text-sm line-clamp-2 mt-1.5 leading-relaxed">
                {item.description}
              </p>
            </div>

            <div className="mt-4 pt-3 border-t border-border/40 flex items-center justify-between text-xs text-muted-foreground">
              {/* Owner info */}
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold text-[10px] overflow-hidden">
                  {ownerInfo?.avatar_url ? (
                    <img src={ownerInfo.avatar_url} alt="" className="w-full h-full object-cover" />
                  ) : (
                    ownerInfo?.full_name?.charAt(0) || <User className="w-3 h-3" />
                  )}
                </div>
                <div className="flex flex-col">
                  <span className="font-medium text-foreground line-clamp-1 text-[11px]">
                    {ownerInfo?.full_name || "Community Member"}
                  </span>
                  <div className="flex items-center gap-1 text-[10px] text-muted-foreground">
                    <Star className="w-3 h-3 fill-amber-400 text-amber-400 inline" />
                    <span>{ownerInfo?.reputation_score ? ownerInfo.reputation_score.toFixed(1) : "4.8"}</span>
                  </div>
                </div>
              </div>

              {/* Proximity / Locality */}
              <div className="flex items-center gap-1 text-right text-[11px] text-muted-foreground">
                <MapPin className="w-3 h-3 text-primary flex-shrink-0" />
                <span className="line-clamp-1 max-w-[110px]">
                  {item.distance_km !== undefined
                    ? `${item.distance_km} km away`
                    : item.locality?.split(",")[0] || "Bengaluru"}
                </span>
              </div>
            </div>
          </CardContent>

          <CardFooter className="p-4 pt-0 gap-2">
            <Link
              href={`/catalog/${item.id}`}
              className="flex-1 text-center py-2 text-xs font-medium rounded-lg border border-border/70 hover:bg-muted transition-colors"
            >
              Details
            </Link>
            <Button
              size="sm"
              disabled={!isAvailable}
              onClick={() => setIsDialogOpen(true)}
              className="flex-1 rounded-lg text-xs font-semibold shadow-sm"
            >
              Borrow
            </Button>
          </CardFooter>
        </Card>
      </motion.div>

      {/* Borrow Dialog */}
      <BorrowDialog
        item={item}
        isOpen={isDialogOpen}
        onOpenChange={setIsDialogOpen}
      />
    </>
  );
}
