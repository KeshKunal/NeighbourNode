"use client";

import React, { useState } from "react";
import { Item, User } from "@/types";
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { BorrowDialog } from "@/components/BorrowDialog";
import { motion, Variants } from "framer-motion";
import { Image as ImageIcon } from "lucide-react";

interface ItemCardProps {
  item: any;
  owner?: any;
}

const itemVariants: Variants = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 300, damping: 24 } }
};

const FallbackImage = ({ src, alt }: { src?: string; alt: string }) => {
  const [error, setError] = useState(false);

  // Use AI to generate a contextual image based on the item title!
  const defaultImage = `https://image.pollinations.ai/prompt/${encodeURIComponent(alt + ' realistic product photography clean background')}?width=600&height=400&nologo=true`;
  const imageSrc = src || defaultImage;

  if (error) {
    return (
      <div className="flex items-center justify-center w-full h-full text-muted-foreground bg-muted">
        <ImageIcon className="w-8 h-8 opacity-50" />
      </div>
    );
  }

  return (
    <img
      src={imageSrc}
      alt={alt}
      onError={() => setError(true)}
      className="w-full h-full object-cover"
    />
  );
};

export function ItemCard({ item, owner }: ItemCardProps) {
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const status = item.current_status || item.status || "available";
  const isAvailable = status === "available";

  return (
    <motion.div variants={itemVariants} whileHover={{ y: -5 }} className="h-full">
      <Card className="flex flex-col overflow-hidden transition-all shadow-sm hover:shadow-md h-full">
        <div className="relative h-48 w-full bg-muted">
          <FallbackImage src={item.image_url} alt={item.title || item.name} />
          <div className="absolute top-2 right-2">
            <Badge
              variant={isAvailable ? "default" : "secondary"}
              className={isAvailable ? "bg-green-500 hover:bg-green-600" : ""}
            >
              {status.charAt(0).toUpperCase() + status.slice(1)}
            </Badge>
          </div>
        </div>
        <CardHeader className="p-4 pb-0">
          <h3 className="font-semibold text-lg line-clamp-1">{item.title || item.name}</h3>
        </CardHeader>
        <CardContent className="p-4 pt-2 flex-1">
          <p className="text-sm text-muted-foreground line-clamp-2">
            {item.description}
          </p>
          <div className="mt-4 flex items-center text-sm">
            <span className="font-medium">Building/Location:</span>
            <span className="ml-2">{owner?.building || item.location_hint || "Unknown"}</span>
          </div>
        </CardContent>
        <CardFooter className="p-4 pt-0">
          <Button 
            className="w-full" 
            disabled={!isAvailable}
            onClick={() => setIsDialogOpen(true)}
          >
            {isAvailable ? "Borrow" : "Unavailable"}
          </Button>
        </CardFooter>
      </Card>

      <BorrowDialog 
        item={item} 
        isOpen={isDialogOpen} 
        onOpenChange={setIsDialogOpen} 
      />
    </motion.div>
  );
}
