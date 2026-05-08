"use client";

import React from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { renderToString } from "react-dom/server";
import { MapPin } from "lucide-react";
import { mockItems } from "@/lib/mockData";
import { Button } from "@/components/ui/button";

// Custom Icon using Lucide React MapPin to avoid default Leaflet broken images
const createCustomIcon = () => {
  const iconHtml = renderToString(<MapPin className="text-primary fill-primary/20 w-8 h-8" />);
  return L.divIcon({
    html: iconHtml,
    className: "custom-leaflet-icon",
    iconSize: [32, 32],
    iconAnchor: [16, 32],
    popupAnchor: [0, -32],
  });
};

export default function Map() {
  const center: L.LatLngTuple = [40.7128, -74.0060];
  const customIcon = createCustomIcon();

  return (
    <MapContainer
      center={center}
      zoom={17}
      scrollWheelZoom={true}
      className="w-full h-full z-0"
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {mockItems.map((item) => (
        <Marker
          key={item.id}
          position={[item.location_lat, item.location_lng]}
          icon={customIcon}
        >
          <Popup className="custom-popup">
            <div className="flex flex-col gap-2 min-w-[200px]">
              {item.image_url ? (
                <img
                  src={item.image_url}
                  alt={item.name}
                  className="w-full h-24 object-cover rounded-md"
                />
              ) : null}
              <h4 className="font-semibold text-sm leading-tight m-0">{item.name}</h4>
              <p className="text-xs text-muted-foreground m-0 p-0 line-clamp-1">{item.description}</p>
              <Button size="sm" className="w-full mt-2 h-8 text-xs">
                View Details
              </Button>
            </div>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}
