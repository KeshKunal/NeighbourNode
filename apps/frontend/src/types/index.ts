export interface User {
  id: string;
  name: string;
  apartment_number: string;
}

export type TransactionStatus = "available" | "pending" | "reserved" | "overdue" | "returned";

export interface Item {
  id: string;
  name: string;
  description: string;
  owner_id: string;
  status: TransactionStatus;
  image_url?: string;
  location_lat: number;
  location_lng: number;
}
