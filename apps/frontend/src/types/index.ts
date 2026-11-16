// Unified TypeScript types for NeighbourNode MongoDB NoSQL Platform

export type TransactionStatus =
  | "AVAILABLE"
  | "PENDING_APPROVAL"
  | "APPROVED"
  | "RESERVED"
  | "ACTIVE"
  | "OVERDUE"
  | "RETURN_PENDING_CONFIRMATION"
  | "RETURNED"
  | "REJECTED"
  | "CANCELLED";

export interface GeoPoint {
  type: "Point";
  coordinates: [number, number]; // [longitude, latitude]
}

export interface ReputationBreakdown {
  score: number;
  average_rating: number;
  review_count: number;
  completed_exchanges: number;
  on_time_return_rate: number;
  verified_bonus: number;
  explanation: string;
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  phone?: string;
  avatar_url?: string;
  bio?: string;
  locality: string;
  building?: string;
  unit?: string;
  location?: GeoPoint;
  location_visibility: "approximate" | "exact" | "hidden";
  skills: string[];
  interests: string[];
  reputation_score: number;
  reputation_breakdown?: ReputationBreakdown;
  completed_exchanges: number;
  is_verified: boolean;
  is_active: boolean;
  telegram_chat_id?: string;
  created_at?: string;
  updated_at?: string;
}

export interface UserPublicProfile {
  id: string;
  full_name: string;
  avatar_url?: string;
  bio?: string;
  locality: string;
  skills: string[];
  interests: string[];
  reputation_score: number;
  completed_exchanges: number;
  is_verified: boolean;
  distance_km?: number;
}

export interface ResourceAvailability {
  status: string;
  available_days: string[];
  max_duration_days: number;
  notes?: string;
}

export interface ResourceOwnerSummary {
  id: string;
  full_name: string;
  locality: string;
  reputation_score: number;
  avatar_url?: string;
  telegram_chat_id?: string;
}

export interface Resource {
  id: string;
  owner_id: string;
  title: string;
  description: string;
  category: string;
  condition: string;
  images: string[];
  location?: GeoPoint;
  locality: string;
  availability?: ResourceAvailability;
  lending_rules?: string;
  status: TransactionStatus;
  owner?: ResourceOwnerSummary;
  distance_km?: number;
  created_at?: string;
  updated_at?: string;
  // Backward compatibility aliases
  name?: string;
  current_status?: string;
  image_url?: string;
  location_lat?: number;
  location_lng?: number;
}

export type Item = Resource;

export interface Skill {
  id: string;
  provider_id: string;
  title: string;
  description: string;
  category: string;
  experience_level: string;
  availability: string;
  location?: GeoPoint;
  locality: string;
  exchange_type: string;
  status: string;
  provider?: ResourceOwnerSummary;
  distance_km?: number;
  created_at?: string;
  updated_at?: string;
}

export interface BorrowRequest {
  id: string;
  resource_id: string;
  resource_title?: string;
  borrower_id: string;
  borrower_name?: string;
  owner_id: string;
  owner_name?: string;
  requested_start: string;
  requested_end: string;
  status: string;
  message?: string;
  transaction_id?: string;
  created_at?: string;
  updated_at?: string;
}

export interface Transaction {
  id: string;
  resource_id: string;
  resource_title?: string;
  borrow_request_id?: string;
  borrower_id: string;
  borrower_name?: string;
  owner_id: string;
  owner_name?: string;
  approved_start: string;
  approved_end: string;
  actual_return_date?: string;
  status: TransactionStatus;
  calendar_event_id?: string;
  created_at?: string;
  updated_at?: string;
}

export interface SkillRequest {
  id: string;
  skill_id: string;
  skill_title?: string;
  requester_id: string;
  requester_name?: string;
  provider_id: string;
  provider_name?: string;
  requested_date: string;
  description: string;
  status: string;
  created_at?: string;
  updated_at?: string;
}

export interface Review {
  id: string;
  reviewer_id: string;
  reviewer_name?: string;
  reviewed_user_id: string;
  transaction_id?: string;
  skill_exchange_id?: string;
  rating: number;
  comment: string;
  created_at?: string;
}

export interface Notification {
  id: string;
  user_id: string;
  type: string;
  title: string;
  message: string;
  related_entity_id?: string;
  is_read: boolean;
  created_at?: string;
}

export interface Community {
  id: string;
  name: string;
  description: string;
  locality: string;
  approximate_location?: GeoPoint;
  member_count: number;
  created_at?: string;
}

export interface RecommendationFactorBreakdown {
  relevance: number;
  proximity: number;
  availability: number;
  reputation: number;
  community_relationship: number;
  previous_interaction: number;
  total_score: number;
  explanation: string;
}

export interface ResourceRecommendation {
  resource: Resource;
  score: number;
  breakdown: RecommendationFactorBreakdown;
}

export interface SkillRecommendation {
  skill: Skill;
  score: number;
  breakdown: RecommendationFactorBreakdown;
}

export interface NeighbourRecommendation {
  neighbour: UserPublicProfile;
  score: number;
  shared_interests: string[];
  breakdown: RecommendationFactorBreakdown;
}

export interface CommunityAnalytics {
  total_users: number;
  total_resources: number;
  total_skills: number;
  total_completed_exchanges: number;
  top_rated_members: Array<{
    user_id: string;
    full_name: string;
    avatar_url?: string;
    locality: string;
    reputation_score: number;
    completed_exchanges: number;
    review_count: number;
  }>;
  category_distribution: Array<{ category: string; count: number }>;
  most_shared_resources: Array<{ resource_id: string; title: string; category: string; borrow_count: number }>;
  most_requested_categories: Array<{ category: string; count: number }>;
}

export interface UserAnalytics {
  user_id: string;
  resources_listed: number;
  skills_offered: number;
  active_borrows: number;
  completed_borrows: number;
  active_lends: number;
  completed_lends: number;
  reputation_score: number;
  review_count: number;
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

export interface AIAskResponse {
  intent: "resource" | "skill" | "general";
  keywords: string[];
  category?: string;
  natural_language_answer: string;
  matched_resources: Resource[];
  matched_skills: Skill[];
  matched_neighbours: UserPublicProfile[];
  explanation: string;
}
