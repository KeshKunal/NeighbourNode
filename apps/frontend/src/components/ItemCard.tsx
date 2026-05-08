import React from "react";
import { Item, User } from "@/types";
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

interface ItemCardProps {
  item: Item;
  owner?: User;
}

export function ItemCard({ item, owner }: ItemCardProps) {
  // Support both backend (current_status) and mock (status) field names
  const status = item.current_status || item.status || "available";
  const isAvailable = status === "available";

  const statusLabel = status
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());

  const statusColor = {
    available: "bg-green-500 hover:bg-green-600",
    pending_approval: "bg-yellow-500 hover:bg-yellow-600",
    reserved: "bg-blue-500 hover:bg-blue-600",
    active: "bg-purple-500 hover:bg-purple-600",
    overdue: "bg-red-500 hover:bg-red-600",
    returned: "bg-gray-500 hover:bg-gray-600",
    cancelled: "bg-gray-400 hover:bg-gray-500",
  }[status] || "";

  const ownerDisplay = owner?.apartment_number || owner?.name || item.location_hint || "—";

  return (
    <Card className="flex flex-col overflow-hidden transition-all hover:shadow-md h-full">
      <div className="relative h-48 w-full bg-muted">
        {item.image_url ? (
          <img
            src={item.image_url}
            alt={item.name}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="flex items-center justify-center w-full h-full text-muted-foreground text-sm">
            <span className="text-4xl">📦</span>
          </div>
        )}
        <div className="absolute top-2 right-2">
          <Badge
            variant={isAvailable ? "default" : "secondary"}
            className={statusColor}
          >
            {statusLabel}
          </Badge>
        </div>
        {item.category && (
          <div className="absolute top-2 left-2">
            <Badge variant="outline" className="bg-background/80 backdrop-blur-sm text-xs">
              {item.category}
            </Badge>
          </div>
        )}
      </div>
      <CardHeader className="p-4 pb-0">
        <h3 className="font-semibold text-lg line-clamp-1">{item.name}</h3>
      </CardHeader>
      <CardContent className="p-4 pt-2 flex-1">
        <p className="text-sm text-muted-foreground line-clamp-2">
          {item.description || "No description available."}
        </p>
        <div className="mt-4 flex items-center text-sm">
          <span className="font-medium">📍</span>
          <span className="ml-2">{ownerDisplay}</span>
        </div>
        {item.condition && (
          <div className="mt-1 flex items-center text-sm">
            <span className="font-medium">Condition:</span>
            <span className="ml-2 text-muted-foreground">{item.condition}</span>
          </div>
        )}
      </CardContent>
      <CardFooter className="p-4 pt-0">
        <Button className="w-full" disabled={!isAvailable}>
          {isAvailable ? "Borrow" : statusLabel}
        </Button>
      </CardFooter>
    </Card>
  );
}
