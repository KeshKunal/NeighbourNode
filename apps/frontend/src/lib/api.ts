/**
 * NeighbourNode API Client
 * Central typed interface for FastAPI backend communication with JWT auth.
 */

import {
  AIAskResponse,
  BorrowByNameRequest,
  BorrowRequest,
  BorrowResponse,
  Community,
  CommunityAnalytics,
  NeighbourRecommendation,
  Notification,
  Resource,
  ResourceRecommendation,
  Review,
  Skill,
  SkillRecommendation,
  SkillRequest,
  Transaction,
  User,
  UserAnalytics,
  UserPublicProfile,
} from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";

// ─── Token Management ──────────────────────────────────────────

export function getAuthToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("neighbournode_token");
}

export function setAuthToken(token: string | null): void {
  if (typeof window === "undefined") return;
  if (token) {
    localStorage.setItem("neighbournode_token", token);
  } else {
    localStorage.removeItem("neighbournode_token");
  }
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getAuthToken();
  const headers = new Headers(options.headers || {});

  if (!headers.has("Content-Type") && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const url = endpoint.startsWith("http")
    ? endpoint
    : `${API_BASE}${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`;

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorDetail = `Request failed (${response.status})`;
    try {
      const errJson = await response.json();
      errorDetail = errJson.detail || errJson.message || errorDetail;
    } catch {
      // Non-JSON error
    }
    throw new Error(errorDetail);
  }

  return response.json();
}

// ─── Authentication API ─────────────────────────────────────────

export const authApi = {
  async register(data: {
    email: string;
    password: string;
    full_name: string;
    phone?: string;
    locality?: string;
    building?: string;
    unit?: string;
    skills?: string[];
    interests?: string[];
    avatar_url?: string;
  }): Promise<{ access_token: string; user: User }> {
    const res = await request<{ access_token: string; user: User }>("/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    });
    setAuthToken(res.access_token);
    return res;
  },

  async login(data: { email: string; password: string }): Promise<{ access_token: string; user: User }> {
    const res = await request<{ access_token: string; user: User }>("/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    });
    setAuthToken(res.access_token);
    return res;
  },

  async getMe(): Promise<User> {
    return request<User>("/auth/me");
  },

  async logout(): Promise<void> {
    try {
      await request("/auth/logout", { method: "POST" });
    } catch {
      // Ignore network errors on logout
    } finally {
      setAuthToken(null);
    }
  },
};

// ─── Users & Profiles API ───────────────────────────────────────

export const usersApi = {
  async getProfile(userId: string): Promise<UserPublicProfile> {
    return request<UserPublicProfile>(`/users/${userId}`);
  },

  async updateMe(data: Partial<User>): Promise<User> {
    return request<User>("/users/me", {
      method: "PATCH",
      body: JSON.stringify(data),
    });
  },

  async getUserReviews(userId: string): Promise<Review[]> {
    return request<Review[]>(`/users/${userId}/reviews`);
  },
};

// ─── Resources API ──────────────────────────────────────────────

export const resourcesApi = {
  async list(params?: {
    category?: string;
    status?: string;
    search?: string;
    locality?: string;
    owner_id?: string;
  }): Promise<Resource[]> {
    const query = new URLSearchParams();
    if (params?.category && params.category !== "all") query.set("category", params.category);
    if (params?.status) query.set("status", params.status);
    if (params?.search) query.set("search", params.search);
    if (params?.locality) query.set("locality", params.locality);
    if (params?.owner_id) query.set("owner_id", params.owner_id);

    const qs = query.toString();
    return request<Resource[]>(`/resources${qs ? `?${qs}` : ""}`);
  },

  async get(id: string): Promise<Resource> {
    return request<Resource>(`/resources/${id}`);
  },

  async create(data: {
    title: string;
    description: string;
    category: string;
    condition: string;
    images?: string[];
    locality?: string;
    location?: { type: "Point"; coordinates: [number, number] };
    availability?: any;
    lending_rules?: string;
  }): Promise<Resource> {
    return request<Resource>("/resources", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async update(id: string, data: Partial<Resource>): Promise<Resource> {
    return request<Resource>(`/resources/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    });
  },

  async delete(id: string): Promise<{ message: string }> {
    return request<{ message: string }>(`/resources/${id}`, {
      method: "DELETE",
    });
  },

  async nearby(params?: {
    longitude?: number;
    latitude?: number;
    max_distance_meters?: number;
    category?: string;
  }): Promise<Resource[]> {
    const query = new URLSearchParams();
    query.set("longitude", (params?.longitude ?? 77.5649).toString());
    query.set("latitude", (params?.latitude ?? 13.0308).toString());
    if (params?.max_distance_meters) query.set("max_distance_meters", params.max_distance_meters.toString());
    if (params?.category && params.category !== "all") query.set("category", params.category);

    return request<Resource[]>(`/resources/nearby?${query.toString()}`);
  },
};

// ─── Skills API ─────────────────────────────────────────────────

export const skillsApi = {
  async list(params?: {
    category?: string;
    search?: string;
    provider_id?: string;
    locality?: string;
  }): Promise<Skill[]> {
    const query = new URLSearchParams();
    if (params?.category && params.category !== "all") query.set("category", params.category);
    if (params?.search) query.set("search", params.search);
    if (params?.provider_id) query.set("provider_id", params.provider_id);
    if (params?.locality) query.set("locality", params.locality);

    const qs = query.toString();
    return request<Skill[]>(`/skills${qs ? `?${qs}` : ""}`);
  },

  async get(id: string): Promise<Skill> {
    return request<Skill>(`/skills/${id}`);
  },

  async create(data: {
    title: string;
    description: string;
    category: string;
    experience_level?: string;
    availability?: string;
    locality?: string;
    exchange_type?: string;
  }): Promise<Skill> {
    return request<Skill>("/skills", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async requestAssistance(data: {
    skill_id: string;
    requested_date: string;
    description: string;
  }): Promise<SkillRequest> {
    return request<SkillRequest>("/skill-requests", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async listRequests(): Promise<SkillRequest[]> {
    return request<SkillRequest[]>("/skill-requests");
  },

  async acceptRequest(requestId: string): Promise<{ message: string }> {
    return request<{ message: string }>(`/skill-requests/${requestId}/accept`, {
      method: "POST",
    });
  },

  async completeRequest(requestId: string): Promise<{ message: string }> {
    return request<{ message: string }>(`/skill-requests/${requestId}/complete`, {
      method: "POST",
    });
  },
};

// ─── Borrowing & Transactions API ───────────────────────────────

export const borrowApi = {
  async createRequest(data: {
    resource_id: string;
    requested_start: string;
    requested_end: string;
    message?: string;
  }): Promise<BorrowRequest> {
    return request<BorrowRequest>("/borrow-requests", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async listRequests(role: "borrower" | "owner" | "all" = "all"): Promise<BorrowRequest[]> {
    return request<BorrowRequest[]>(`/borrow-requests?role=${role}`);
  },

  async approve(requestId: string): Promise<{ success: boolean; message: string; transaction_id?: string }> {
    return request<{ success: boolean; message: string; transaction_id?: string }>(
      `/borrow-requests/${requestId}/approve`,
      { method: "POST" }
    );
  },

  async reject(requestId: string, reason?: string): Promise<{ message: string }> {
    return request<{ message: string }>(
      `/borrow-requests/${requestId}/reject?reason=${encodeURIComponent(reason || "")}`,
      { method: "POST" }
    );
  },

  async startLoan(requestId: string): Promise<{ message: string }> {
    return request<{ message: string }>(`/borrow-requests/${requestId}/start`, {
      method: "POST",
    });
  },

  async returnLoan(requestId: string): Promise<{ message: string }> {
    return request<{ message: string }>(`/borrow-requests/${requestId}/return`, {
      method: "POST",
    });
  },
};

// ─── Reviews & Ratings API ──────────────────────────────────────

export const reviewsApi = {
  async create(data: {
    reviewed_user_id: string;
    transaction_id?: string;
    skill_exchange_id?: string;
    rating: number;
    comment: string;
  }): Promise<Review> {
    return request<Review>("/reviews", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
};

// ─── Recommendations API ────────────────────────────────────────

export const recommendationsApi = {
  async getResources(params?: { query?: string; category?: string; limit?: number }): Promise<ResourceRecommendation[]> {
    const q = new URLSearchParams();
    if (params?.query) q.set("query", params.query);
    if (params?.category) q.set("category", params.category);
    if (params?.limit) q.set("limit", params.limit.toString());
    return request<ResourceRecommendation[]>(`/recommendations/resources?${q.toString()}`);
  },

  async getSkills(params?: { query?: string; category?: string; limit?: number }): Promise<SkillRecommendation[]> {
    const q = new URLSearchParams();
    if (params?.query) q.set("query", params.query);
    if (params?.category) q.set("category", params.category);
    if (params?.limit) q.set("limit", params.limit.toString());
    return request<SkillRecommendation[]>(`/recommendations/skills?${q.toString()}`);
  },

  async getNeighbours(limit = 6): Promise<NeighbourRecommendation[]> {
    return request<NeighbourRecommendation[]>(`/recommendations/neighbours?limit=${limit}`);
  },
};

// ─── Community API ──────────────────────────────────────────────

export const communityApi = {
  async listMembers(locality?: string): Promise<UserPublicProfile[]> {
    const q = locality ? `?locality=${encodeURIComponent(locality)}` : "";
    return request<UserPublicProfile[]>(`/community${q}`);
  },

  async listGroups(): Promise<Community[]> {
    return request<Community[]>("/community/groups");
  },
};

// ─── Notifications API ──────────────────────────────────────────

export const notificationsApi = {
  async list(): Promise<Notification[]> {
    return request<Notification[]>("/notifications");
  },

  async markRead(id: string): Promise<{ ok: boolean }> {
    return request<{ ok: boolean }>(`/notifications/${id}/read`, {
      method: "PATCH",
    });
  },

  async markAllRead(): Promise<{ marked_read: number }> {
    return request<{ marked_read: number }>("/notifications/read-all", {
      method: "POST",
    });
  },
};

// ─── Analytics API ──────────────────────────────────────────────

export const analyticsApi = {
  async getCommunity(): Promise<CommunityAnalytics> {
    return request<CommunityAnalytics>("/analytics/community");
  },

  async getMe(): Promise<UserAnalytics> {
    return request<UserAnalytics>("/analytics/me");
  },
};

// ─── AI Assistant API ───────────────────────────────────────────

export const aiApi = {
  async ask(query: string): Promise<AIAskResponse> {
    return request<AIAskResponse>("/ai/ask", {
      method: "POST",
      body: JSON.stringify({ query }),
    });
  },
};

// ─── Legacy Backward Compatibility Helpers ─────────────────────

export async function fetchItems(): Promise<Resource[]> {
  return resourcesApi.list();
}

export async function borrowItem(payload: {
  item_id: string;
  borrower_id: string;
  requested_start: string;
  requested_end: string;
}): Promise<BorrowResponse> {
  try {
    const res = await borrowApi.createRequest({
      resource_id: payload.item_id,
      requested_start: payload.requested_start,
      requested_end: payload.requested_end,
      message: "Borrow request via catalogue modal",
    });
    return {
      success: true,
      transaction_id: res.id,
      message: "Borrow request sent to owner for approval!",
    };
  } catch (err: any) {
    return {
      success: false,
      message: err.message || "Failed to submit borrow request.",
    };
  }
}

export async function orchestrateBorrow(payload: BorrowByNameRequest): Promise<BorrowResponse> {
  try {
    const aiRes = await aiApi.ask(payload.item_name);
    if (aiRes.matched_resources && aiRes.matched_resources.length > 0) {
      const best = aiRes.matched_resources[0];
      return borrowItem({
        item_id: best.id,
        borrower_id: payload.borrower_id,
        requested_start: payload.requested_start,
        requested_end: payload.requested_end,
      });
    }
    return {
      success: false,
      message: aiRes.natural_language_answer || "No matching items found.",
    };
  } catch (err: any) {
    return {
      success: false,
      message: err.message || "AI Matching failed.",
    };
  }
}
