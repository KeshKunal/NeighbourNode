import { Item, BorrowResponse } from "@/types";

const API_BASE = "/api";

export async function fetchItems(): Promise<Item[]> {
  const res = await fetch(`${API_BASE}/items/`);
  if (!res.ok) throw new Error(`Failed to fetch items: ${res.status}`);
  return res.json();
}

/**
 * Portal-first borrow: user already selected an item from the catalog.
 * Sends item_id directly to the orchestrator.
 */
export async function borrowItem(payload: {
  item_id: string;
  borrower_id: string;
  requested_start: string;
  requested_end: string;
}): Promise<BorrowResponse> {
  const res = await fetch(`${API_BASE}/api/orchestrate/borrow`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(error.detail || `Borrow failed: ${res.status}`);
  }
  return res.json();
}
