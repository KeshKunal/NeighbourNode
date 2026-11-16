"use client";

import React, { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { renderToString } from "react-dom/server";
import { MapPin, Navigation, Star } from "lucide-react";
import { Resource } from "@/types";
import { resourcesApi } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { BorrowDialog } from "@/components/BorrowDialog";

// Custom Icon using Lucide React MapPin
const createCustomIcon = (isAvailable = true) => {
  const iconHtml = renderToString(
    <div className={`flex items-center justify-center w-8 h-8 rounded-full shadow-lg ${
      isAvailable ? "bg-emerald-600 text-white" : "bg-amber-600 text-white"
    }`}>
      <MapPin className="w-5 h-5 fill-current" />
    </div>
  );
  return L.divIcon({
    html: iconHtml,
    className: "custom-leaflet-icon",
    iconSize: [32, 32],
    iconAnchor: [16, 32],
    popupAnchor: [0, -32],
  });
};

export default function Map() {
  // Center at Ramaiah Institute of Technology (MSRIT), Mathikere, Bengaluru
  const center: L.LatLngTuple = [13.0308, 77.5649];
  const [items, setItems] = useState<Resource[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedItem, setSelectedItem] = useState<Resource | null>(null);

  useEffect(() => {
    async function fetchMapItems() {
      try {
        const data = await resourcesApi.list();
        setItems(data);
      } catch (err) {
        console.error("Failed to load map markers from MongoDB:", err);
      } finally {
        setLoading(false);
      }
    }
    fetchMapItems();
  }, []);

  return (
    <div className="relative w-full h-full">
      <MapContainer
        center={center}
        zoom={14}
        scrollWheelZoom={true}
        className="w-full h-full z-0"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {items.map((item) => {
          const coords = item.location?.coordinates;
          // Coordinates in GeoJSON are [longitude, latitude]
          const lat = coords ? coords[1] : item.location_lat || 13.0308;
          const lng = coords ? coords[0] : item.location_lng || 77.5649;
          const isAvail = item.status === "AVAILABLE" || item.status === "available";

          return (
            <Marker
              key={item.id}
              position={[lat, lng]}
              icon={createCustomIcon(isAvail)}
            >
              <Popup className="custom-popup">
                <div className="flex flex-col gap-2 min-w-[220px] p-1">
                  {item.images && item.images.length > 0 ? (
                    <img
                      src={item.images[0]}
                      alt={item.title || item.name}
                      className="w-full h-24 object-cover rounded-lg"
                    />
                  ) : null}
                  <div className="flex items-center justify-between gap-1">
                    <Badge variant="outline" className="text-[10px]">
                      {item.category}
                    </Badge>
                    <span className="text-[10px] text-muted-foreground font-medium">
                      {item.locality?.split(",")[0] || "Bengaluru"}
                    </span>
                  </div>
                  <h4 className="font-bold text-sm leading-tight m-0 text-foreground">
                    {item.title || item.name}
                  </h4>
                  <p className="text-xs text-muted-foreground m-0 p-0 line-clamp-2">
                    {item.description}
                  </p>
                  <Button
                    size="sm"
                    className="w-full mt-2 h-7 text-xs font-semibold"
                    disabled={!isAvail}
                    onClick={() => setSelectedItem(item)}
                  >
                    Request to Borrow
                  </Button>
                </div>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>

      {/* Geospatial Legend Overlay */}
      <div className="absolute top-4 left-4 z-[1000] bg-background/90 backdrop-blur-md border border-border/60 p-3 rounded-2xl shadow-md pointer-events-auto max-w-xs hidden sm:block">
        <div className="flex items-center gap-1.5 text-xs font-bold text-foreground mb-1">
          <Navigation className="w-3.5 h-3.5 text-primary" />
          <span>Bengaluru Neighbourhood Grid</span>
        </div>
        <p className="text-[11px] text-muted-foreground leading-snug">
          MongoDB 2dsphere geospatial indexing around Ramaiah Campus & Mathikere.
        </p>
      </div>

      {selectedItem && (
        <BorrowDialog
          item={selectedItem}
          isOpen={!!selectedItem}
          onOpenChange={(open) => !open && setSelectedItem(null)}
        />
      )}
    </div>
  );
}
