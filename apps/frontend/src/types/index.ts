// Types matching the backend Pydantic schemas exactly

export type TransactionStatus =
  | "available"
  | "pending_approval"
  | "reserved"
  | "active"
  | "overdue"
  | "returned"
  | "cancelled";

export interface User {
  id: string;
  full_name: string;
  phone: string;
  email?: string;
  building?: string;
  unit?: string;
  telegram_chat_id?: string;
  rating: number;
  created_at: string;
  // Frontend display helpers
  name?: string;
  apartment_number?: string;
}

export interface Item {
  id: string;
  name: string;
  description?: string;
  category?: string;
  condition?: string;
  location_hint?: string;
  is_active: boolean;
  current_status: TransactionStatus;
  owner_id: string;
  created_at: string;
  // Frontend display helpers (mock data compat)
  status?: TransactionStatus;
  image_url?: string;
  location_lat?: number;
  location_lng?: number;
}

export interface BorrowByNameRequest {
  item_name: string;
  borrower_id: string;
  requested_start: string;
  requested_end: string;
}

export interface BorrowResponse {
  success: boolean;
  transaction_id?: string;
  message: string;
}
