"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  PackagePlus,
  ArrowLeft,
  Loader2,
  CheckCircle2,
  Upload,
  Calendar,
  MapPin,
  ShieldAlert,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { resourcesApi } from "@/lib/api";
import { useAuth } from "@/lib/authContext";
import { toast } from "sonner";

const CATEGORIES = [
  "Tools and equipment",
  "Electronics",
  "Books and study material",
  "Travel and camping",
  "Sports equipment",
  "Kitchen equipment",
  "Household items",
  "Miscellaneous",
];

const CONDITIONS = ["Like New", "Good", "Fair"];

export default function NewResourcePage() {
  const router = useRouter();
  const { user } = useAuth();
  const [submitting, setSubmitting] = useState(false);

  // Form State
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState("Tools and equipment");
  const [condition, setCondition] = useState("Good");
  const [imageUrl, setImageUrl] = useState("");
  const [locality, setLocality] = useState(user?.locality || "Mathikere, Bengaluru");
  const [maxDays, setMaxDays] = useState(7);
  const [lendingRules, setLendingRules] = useState("Please handle with care and return promptly.");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) {
      toast.error("Please sign in to list an item.");
      router.push("/auth/signin");
      return;
    }

    if (!title.trim() || !description.trim()) {
      toast.error("Title and description are required.");
      return;
    }

    setSubmitting(true);
    try {
      const created = await resourcesApi.create({
        title: title.trim(),
        description: description.trim(),
        category,
        condition,
        images: imageUrl.trim() ? [imageUrl.trim()] : [],
        locality: locality.trim(),
        availability: {
          status: "available",
          available_days: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
          max_duration_days: Number(maxDays),
        },
        lending_rules: lendingRules.trim(),
      });

      toast.success("Resource listed successfully in MongoDB catalog!");
      router.push(`/catalog/${created.id}`);
    } catch (err: any) {
      toast.error(err.message || "Failed to list item.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-2xl">
      <div className="mb-6">
        <Link
          href="/dashboard"
          className="text-xs text-muted-foreground hover:text-foreground flex items-center gap-1.5 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Dashboard
        </Link>
      </div>

      <Card className="rounded-3xl border-border/70 shadow-lg">
        <CardHeader className="space-y-1">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-primary/10 text-primary flex items-center justify-center">
              <PackagePlus className="w-4 h-4" />
            </div>
            <CardTitle className="text-xl font-bold">List a Physical Resource</CardTitle>
          </div>
          <CardDescription className="text-xs">
            Lend tools, electronics, camping kits, or study material to your local community.
          </CardDescription>
        </CardHeader>

        <form onSubmit={handleSubmit}>
          <CardContent className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-muted-foreground" htmlFor="title">
                Item Title *
              </label>
              <Input
                id="title"
                placeholder='e.g., "Bosch 600W Impact Drill Kit with Bits"'
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
                className="rounded-xl text-sm h-11"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-muted-foreground" htmlFor="category">
                  Category *
                </label>
                <select
                  id="category"
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full h-11 rounded-xl border border-input bg-background px-3 py-2 text-xs focus:outline-none focus:ring-1 focus:ring-ring"
                >
                  {CATEGORIES.map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))}
                </select>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-muted-foreground" htmlFor="condition">
                  Item Condition *
                </label>
                <select
                  id="condition"
                  value={condition}
                  onChange={(e) => setCondition(e.target.value)}
                  className="w-full h-11 rounded-xl border border-input bg-background px-3 py-2 text-xs focus:outline-none focus:ring-1 focus:ring-ring"
                >
                  {CONDITIONS.map((cond) => (
                    <option key={cond} value={cond}>
                      {cond}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-muted-foreground" htmlFor="desc">
                Detailed Description *
              </label>
              <Textarea
                id="desc"
                rows={3}
                placeholder="Mention what's included, any accessories, power cords, or special notes..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                required
                className="rounded-xl text-xs resize-none"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-muted-foreground" htmlFor="image">
                Image URL
              </label>
              <Input
                id="image"
                type="url"
                placeholder="https://images.unsplash.com/... or media URL"
                value={imageUrl}
                onChange={(e) => setImageUrl(e.target.value)}
                className="rounded-xl text-xs h-10"
              />
              <span className="text-[10px] text-muted-foreground">
                Paste an Unsplash image URL or image link for demonstration.
              </span>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-muted-foreground" htmlFor="locality">
                  Locality / Area
                </label>
                <Input
                  id="locality"
                  value={locality}
                  onChange={(e) => setLocality(e.target.value)}
                  placeholder="Mathikere, Bengaluru"
                  className="rounded-xl text-xs h-10"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-muted-foreground" htmlFor="maxDays">
                  Max Borrow Duration (Days)
                </label>
                <Input
                  id="maxDays"
                  type="number"
                  min={1}
                  max={30}
                  value={maxDays}
                  onChange={(e) => setMaxDays(Number(e.target.value))}
                  className="rounded-xl text-xs h-10"
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-muted-foreground" htmlFor="rules">
                Lending Rules & Care Instructions
              </label>
              <Input
                id="rules"
                value={lendingRules}
                onChange={(e) => setLendingRules(e.target.value)}
                placeholder="e.g. Return clean, dry tent before folding..."
                className="rounded-xl text-xs h-10"
              />
            </div>
          </CardContent>

          <CardFooter className="pt-2">
            <Button
              type="submit"
              disabled={submitting}
              className="w-full rounded-2xl h-11 font-semibold text-sm shadow-md shadow-primary/20"
            >
              {submitting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin mr-2" />
                  Publishing Listing...
                </>
              ) : (
                "Publish Resource Listing"
              )}
            </Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}

