import { Item, User } from "../types";

export const mockUsers: User[] = [
  { id: "u1", name: "Alice Smith", apartment_number: "101" },
  { id: "u2", name: "Bob Jones", apartment_number: "205" },
  { id: "u3", name: "Charlie Davis", apartment_number: "304" },
];

export const mockItems: Item[] = [
  {
    id: "i1",
    name: "Bosch Power Drill",
    description: "Professional grade 18V cordless drill. Comes with a set of standard bits.",
    owner_id: "u1",
    status: "available",
    image_url: "/drill.png",
    location_lat: 40.7128,
    location_lng: -74.0060,
  },
  {
    id: "i2",
    name: "Arduino Starter Kit",
    description: "Complete starter kit for Arduino projects. Includes various sensors and breadboard.",
    owner_id: "u2",
    status: "available",
    image_url: "/arduino.png",
    location_lat: 40.7130,
    location_lng: -74.0050,
  },
  {
    id: "i3",
    name: "Hiking Tent (2-Person)",
    description: "Lightweight 2-person tent perfect for weekend camping trips.",
    owner_id: "u3",
    status: "reserved",
    image_url: "/tent.png",
    location_lat: 40.7125,
    location_lng: -74.0070,
  },
  {
    id: "i4",
    name: "Sony Projector",
    description: "1080p portable projector for movie nights.",
    owner_id: "u1",
    status: "available",
    image_url: "/projector.png",
    location_lat: 40.7129,
    location_lng: -74.0065,
  },
  {
    id: "i5",
    name: "Folding Chairs (Set of 4)",
    description: "Sturdy folding chairs for parties or extra guests.",
    owner_id: "u2",
    status: "pending",
    image_url: "/chairs.png",
    location_lat: 40.7132,
    location_lng: -74.0055,
  },
  {
    id: "i6",
    name: "Dremel Tool Kit",
    description: "Rotary tool kit with 40+ accessories for crafting and DIY.",
    owner_id: "u3",
    status: "available",
    image_url: "/dremel.png",
    location_lat: 40.7126,
    location_lng: -74.0068,
  }
];
