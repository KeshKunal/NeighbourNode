"use client";

import React, { useState } from "react";
import { Item, User } from "@/types";
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { BorrowDialog } from "@/components/BorrowDialog";
import { motion } from "framer-motion";

interface ItemCardProps {
  item: Item;
  owner?: User;
}

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 300, damping: 24 } }
};

export function ItemCard({ item, owner }: ItemCardProps) {
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const isAvailable = item.status === "available";

  return (
    <motion.div variants={itemVariants} whileHover={{ y: -5 }} className="h-full">
      <Card className="flex flex-col overflow-hidden transition-all shadow-sm hover:shadow-md h-full">
        <div className="relative h-48 w-full bg-muted">
          {item.image_url ? (
            <img
              src={item.image_url}
              alt={item.name}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="flex items-center justify-center w-full h-full text-muted-foreground">
              No Image
            </div>
          )}
          <div className="absolute top-2 right-2">
            <Badge
              variant={isAvailable ? "default" : "secondary"}
              className={isAvailable ? "bg-green-500 hover:bg-green-600" : ""}
            >
              {item.status.charAt(0).toUpperCase() + item.status.slice(1)}
            </Badge>
          </div>
        </div>
        <CardHeader className="p-4 pb-0">
          <h3 className="font-semibold text-lg line-clamp-1">{item.name}</h3>
        </CardHeader>
        <CardContent className="p-4 pt-2 flex-1">
          <p className="text-sm text-muted-foreground line-clamp-2">
            {item.description}
          </p>
          <div className="mt-4 flex items-center text-sm">
            <span className="font-medium">Owner Apt:</span>
            <span className="ml-2">{owner?.apartment_number || "Unknown"}</span>
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
