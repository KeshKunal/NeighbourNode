"use client";

import React, { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import {
  ArrowLeft,
  CheckCircle2,
  Calendar,
  MapPin,
  Star,
  ShieldCheck,
  User,
  Share2,
  AlertCircle,
  Clock,
  Sparkles,
  Package,
} from "lucide-react";
import { resourcesApi, reviewsApi } from "@/lib/api";
import { Resource, Review } from "@/types";
import { Button, buttonVariants } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { BorrowDialog } from "@/components/BorrowDialog";
import { useAuth } from "@/lib/authContext";
import { toast } from "sonner";

export default function ResourceDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { user } = useAuth();
  const id = params?.id as string;

  const [resource, setResource] = useState<Resource | null>(null);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isBorrowOpen, setIsBorrowOpen] = useState(false);
  const [activeImageIndex, setActiveImageIndex] = useState(0);

  useEffect(() => {
    if (!id) return;
    async function loadResource() {
      setLoading(true);
      setError(null);
      try {
        const item = await resourcesApi.get(id);
        setResource(item);
        if (item.owner_id) {
          const revs = await reviewsApi.listForUser?.(item.owner_id).catch(() => []);
          // Or from usersApi.getUserReviews
          const { usersApi } = await import("@/lib/api");
          const userReviews = await usersApi.getUserReviews(item.owner_id).catch(() => []);
          setReviews(userReviews || []);
        }
      } catch (err: any) {
        setError(err.message || "Could not load resource details.");
      } finally {
        setLoading(false);
      }
    }
    loadResource();
  }, [id]);

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-16 flex flex-col items-center justify-center space-y-3">
        <div className="w-8 h-8 rounded-full border-2 border-primary border-t-transparent animate-spin" />
        <span className="text-xs text-muted-foreground">Loading resource details from MongoDB...</span>
      </div>
    );
  }

  if (error || !resource) {
    return (
      <div className="container mx-auto px-4 py-16 text-center space-y-4 max-w-md">
        <div className="w-12 h-12 bg-destructive/10 text-destructive rounded-full flex items-center justify-center mx-auto">
          <AlertCircle className="w-6 h-6" />
        </div>
        <h2 className="text-xl font-bold">Resource Not Found</h2>
        <p className="text-xs text-muted-foreground">{error || "This item may have been removed."}</p>
        <Link href="/catalog" className={buttonVariants({ variant: "outline", size: "sm" })}>
          <ArrowLeft className="w-4 h-4 mr-1.5" /> Back to Catalog
        </Link>
      </div>
    );
  }

  const isOwner = user && user.id === resource.owner_id;
  const isAvailable = resource.status === "AVAILABLE" || resource.status === "available";
  const images = resource.images && resource.images.length > 0 ? resource.images : [];
  const owner = resource.owner;

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl space-y-8">
      {/* Breadcrumb Back */}
      <div className="flex items-center justify-between">
        <Link
          href="/catalog"
          className="text-xs text-muted-foreground hover:text-foreground flex items-center gap-1.5 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Catalog
        </Link>

        <button
          onClick={() => {
            if (typeof navigator !== "undefined") {
              navigator.clipboard?.writeText(window.location.href);
              toast.success("Link copied to clipboard!");
            }
          }}
          className="text-xs text-muted-foreground hover:text-foreground flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-border/50 hover:bg-muted"
        >
          <Share2 className="w-3.5 h-3.5" /> Share
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Image Gallery & Description */}
        <div className="lg:col-span-7 space-y-6">
          {/* Main Photo Showcase */}
          <div className="rounded-3xl overflow-hidden border border-border/60 bg-muted/40 aspect-video relative shadow-sm">
            {images.length > 0 ? (
              <img
                src={images[activeImageIndex] || images[0]}
                alt={resource.title}
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="w-full h-full flex flex-col items-center justify-center text-muted-foreground gap-2">
                <Package className="w-12 h-12 opacity-30" />
                <span className="text-xs font-medium">No photo provided</span>
              </div>
            )}

            <div className="absolute top-4 left-4 flex gap-2">
              <Badge className="backdrop-blur-md bg-background/80 text-foreground font-semibold shadow-sm">
                {resource.category}
              </Badge>
              {resource.condition && (
                <Badge variant="outline" className="backdrop-blur-md bg-background/80 shadow-sm">
                  {resource.condition}
                </Badge>
              )}
            </div>

            <div className="absolute top-4 right-4">
              <Badge
                className={`shadow-sm font-semibold ${
                  isAvailable ? "bg-emerald-600 text-white" : "bg-amber-600 text-white"
                }`}
              >
                {isAvailable ? "Available to Borrow" : resource.status.replace("_", " ")}
              </Badge>
            </div>
          </div>

          {/* Thumbnails */}
          {images.length > 1 && (
            <div className="flex gap-2 overflow-x-auto pb-1">
              {images.map((img, idx) => (
                <button
                  key={idx}
                  onClick={() => setActiveImageIndex(idx)}
                  className={`w-20 h-14 rounded-xl overflow-hidden border-2 transition-all flex-shrink-0 ${
                    activeImageIndex === idx ? "border-primary shadow-sm" : "border-transparent opacity-70"
                  }`}
                >
                  <img src={img} alt="" className="w-full h-full object-cover" />
                </button>
              ))}
            </div>
          )}

          {/* Detailed Description */}
          <div className="space-y-3">
            <h2 className="text-xl font-bold tracking-tight">About this item</h2>
            <p className="text-sm text-muted-foreground leading-relaxed whitespace-pre-line">
              {resource.description}
            </p>
          </div>

          {/* Lending Rules & Guidelines */}
          {resource.lending_rules && (
            <div className="p-5 rounded-2xl bg-muted/40 border border-border/50 space-y-2">
              <h3 className="text-xs font-bold uppercase tracking-wider text-foreground">
                Lending Rules & Care Instructions
              </h3>
              <p className="text-xs text-muted-foreground leading-relaxed">
                {resource.lending_rules}
              </p>
            </div>
          )}

          {/* Reviews Received for Owner */}
          <div className="space-y-4 pt-4 border-t border-border/40">
            <h3 className="text-base font-bold flex items-center gap-2">
              <Star className="w-4 h-4 fill-amber-400 text-amber-400" />
              Community Reviews ({reviews.length})
            </h3>
            {reviews.length === 0 ? (
              <p className="text-xs text-muted-foreground italic">
                No reviews recorded yet. Completed borrows will build public reputation here.
              </p>
            ) : (
              <div className="space-y-3">
                {reviews.map((rev) => (
                  <div key={rev.id} className="p-3.5 rounded-xl bg-card border border-border/50 text-xs space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-foreground">{rev.reviewer_name || "Neighbour"}</span>
                      <div className="flex items-center text-amber-500 font-bold gap-0.5">
                        <Star className="w-3.5 h-3.5 fill-current" />
                        <span>{rev.rating}/5</span>
                      </div>
                    </div>
                    <p className="text-muted-foreground leading-snug">"{rev.comment}"</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Title, Actions & Owner Profile Card */}
        <div className="lg:col-span-5 space-y-6">
          <Card className="p-6 rounded-3xl border-border/70 shadow-sm space-y-5 bg-card">
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-foreground">{resource.title}</h1>
              <p className="text-xs text-muted-foreground mt-1 flex items-center gap-1.5">
                <MapPin className="w-3.5 h-3.5 text-primary" /> {resource.locality}
              </p>
            </div>

            {/* Availability Box */}
            <div className="p-3.5 rounded-2xl bg-muted/50 border border-border/40 text-xs space-y-1">
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Max Duration:</span>
                <span className="font-semibold text-foreground">
                  {resource.availability?.max_duration_days || 7} days
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Available Days:</span>
                <span className="font-semibold text-foreground">
                  {resource.availability?.available_days?.join(", ") || "All days"}
                </span>
              </div>
            </div>

            {/* Action Button */}
            <div>
              {isOwner ? (
                <div className="p-3 text-center rounded-xl bg-muted text-xs text-muted-foreground">
                  This is your listing. Manage requests in your{" "}
                  <Link href="/dashboard" className="text-primary font-semibold underline">
                    Dashboard
                  </Link>
                  .
                </div>
              ) : (
                <Button
                  size="lg"
                  disabled={!isAvailable}
                  onClick={() => setIsBorrowOpen(true)}
                  className="w-full rounded-2xl h-12 text-sm font-bold shadow-md shadow-primary/20"
                >
                  {isAvailable ? "Request to Borrow" : "Currently Unavailable"}
                </Button>
              )}
            </div>

            {/* Owner Profile Box */}
            <div className="pt-4 border-t border-border/40 space-y-3">
              <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider block">
                Listed by Neighbour
              </span>

              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-2xl bg-primary/10 text-primary font-bold text-base flex items-center justify-center overflow-hidden border border-primary/20 flex-shrink-0">
                  {owner?.avatar_url ? (
                    <img src={owner.avatar_url} alt="" className="w-full h-full object-cover" />
                  ) : (
                    owner?.full_name?.charAt(0) || "U"
                  )}
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-1.5">
                    <h4 className="font-bold text-sm text-foreground truncate">{owner?.full_name || "Community Member"}</h4>
                    <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
                  </div>
                  <div className="flex items-center gap-1 text-xs text-muted-foreground mt-0.5">
                    <Star className="w-3 h-3 fill-amber-400 text-amber-400" />
                    <span className="font-semibold text-foreground">{owner?.reputation_score?.toFixed(1) || "4.8"}</span>
                    <span>• Verified Neighbour</span>
                  </div>
                </div>
              </div>
            </div>
          </Card>
        </div>
      </div>

      {/* Borrow Dialog Modal */}
      <BorrowDialog
        item={resource}
        isOpen={isBorrowOpen}
        onOpenChange={setIsBorrowOpen}
      />
    </div>
  );
}

