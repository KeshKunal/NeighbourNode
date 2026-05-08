import { Item, BorrowByNameRequest, BorrowResponse } from "@/types";

const API_BASE = "/api";

export async function fetchItems(): Promise<Item[]> {
  const res = await fetch(`${API_BASE}/items/`);
  if (!res.ok) throw new Error(`Failed to fetch items: ${res.status}`);
  return res.json();
}

export async function orchestrateBorrow(
  payload: BorrowByNameRequest
): Promise<BorrowResponse> {
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
