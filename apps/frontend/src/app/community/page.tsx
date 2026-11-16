"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  Users,
  Search,
  Star,
  MapPin,
  ShieldCheck,
  Sparkles,
  MessageSquare,
  CheckCircle2,
  BookOpen,
  Filter,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button, buttonVariants } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { communityApi, recommendationsApi } from "@/lib/api";
import { NeighbourRecommendation, UserPublicProfile } from "@/types";
import { useAuth } from "@/lib/authContext";
import { toast } from "sonner";

export default function CommunityPage() {
  const { user } = useAuth();
  const [members, setMembers] = useState<UserPublicProfile[]>([]);
  const [recommendations, setRecommendations] = useState<NeighbourRecommendation[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadCommunity() {
      setLoading(true);
      try {
        const [allMembers, recs] = await Promise.all([
          communityApi.listMembers(),
          recommendationsApi.getNeighbours(6).catch(() => []),
        ]);
        setMembers(allMembers || []);
        setRecommendations(recs || []);
      } catch (err) {
        console.error("Community load error:", err);
      } finally {
        setLoading(false);
      }
    }
    loadCommunity();
  }, []);

  const filtered = members.filter((m) => {
    const q = search.toLowerCase();
    if (!q) return true;
    return (
      m.full_name.toLowerCase().includes(q) ||
      m.locality.toLowerCase().includes(q) ||
      m.skills.some((s) => s.toLowerCase().includes(q)) ||
      m.interests.some((i) => i.toLowerCase().includes(q))
    );
  });

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl space-y-8">
      {/* Header Banner */}
      <div className="p-8 rounded-3xl bg-gradient-to-r from-card via-muted/30 to-card border border-border/60 shadow-sm space-y-2">
        <Badge className="bg-primary/10 text-primary border-primary/20 text-xs font-semibold gap-1.5">
          <Users className="w-3.5 h-3.5" /> Hyper-Local Social Fabric
        </Badge>
        <h1 className="text-3xl font-extrabold tracking-tight">Community Resident Network</h1>
        <p className="text-xs sm:text-sm text-muted-foreground max-w-2xl leading-relaxed">
          Discover verified neighbours in Ramaiah, Mathikere, New BEL Road, and Malleshwaram.
          Connect on shared interests, study groups, and cooperative resource sharing.
        </p>
      </div>

      {/* Recommended Neighbours (Graph match) */}
      {recommendations.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-bold tracking-tight flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-primary" /> Suggested Community Connections
              </h2>
              <p className="text-xs text-muted-foreground">
                Matched based on shared interests, geographic proximity, and community trust.
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {recommendations.map((rec) => (
              <Card
                key={rec.neighbour.id}
                className="p-5 rounded-3xl border-border/60 shadow-sm flex flex-col justify-between space-y-3 bg-card hover:border-primary/40 transition-colors"
              >
                <div className="space-y-3">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-2xl bg-primary/10 text-primary font-bold text-base flex items-center justify-center overflow-hidden flex-shrink-0">
                      {rec.neighbour.avatar_url ? (
                        <img src={rec.neighbour.avatar_url} alt="" className="w-full h-full object-cover" />
                      ) : (
                        rec.neighbour.full_name.charAt(0)
                      )}
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-1.5">
                        <h4 className="font-bold text-sm truncate">{rec.neighbour.full_name}</h4>
                        <ShieldCheck className="w-3.5 h-3.5 text-emerald-600 flex-shrink-0" />
                      </div>
                      <p className="text-xs text-muted-foreground flex items-center gap-1">
                        <MapPin className="w-3 h-3 text-primary" /> {rec.neighbour.locality.split(",")[0]}
                      </p>
                    </div>
                  </div>

                  <div className="flex flex-wrap gap-1">
                    {rec.shared_interests.map((int, i) => (
                      <Badge key={i} variant="secondary" className="text-[10px] px-2 py-0.5">
                        ★ {int}
                      </Badge>
                    ))}
                  </div>

                  <p className="text-[11px] text-muted-foreground italic leading-snug">
                    {rec.breakdown.explanation}
                  </p>
                </div>

                <div className="pt-2 border-t border-border/40 flex items-center justify-between text-xs">
                  <div className="flex items-center gap-1 text-amber-500 font-bold">
                    <Star className="w-3.5 h-3.5 fill-current" />
                    <span>{rec.neighbour.reputation_score.toFixed(1)}/5</span>
                  </div>
                  <Button
                    size="sm"
                    variant="outline"
                    className="text-xs h-7 rounded-lg"
                    onClick={() => toast.info(`Connection request sent to ${rec.neighbour.full_name}`)}
                  >
                    Connect
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Search Input for All Members */}
      <div className="space-y-4 pt-4 border-t border-border/40">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="relative max-w-md w-full">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by name, locality, skills, or interests..."
              className="pl-10 rounded-2xl text-xs h-10"
            />
          </div>
          <span className="text-xs text-muted-foreground">
            {filtered.length} registered neighbour(s)
          </span>
        </div>

        {/* Members Grid */}
        {loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {[1, 2, 3, 4, 5, 6].map((n) => (
              <div key={n} className="rounded-3xl border border-border/40 bg-card h-52 animate-pulse p-5 space-y-3">
                <div className="w-12 h-12 bg-muted rounded-full" />
                <div className="h-4 bg-muted rounded w-1/2" />
                <div className="h-3 bg-muted rounded w-3/4" />
              </div>
            ))}
          </div>
        ) : filtered.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {filtered.map((m) => (
              <Card
                key={m.id}
                className="p-5 rounded-3xl border-border/60 hover:border-primary/40 transition-colors shadow-sm flex flex-col justify-between space-y-3 bg-card"
              >
                <div className="space-y-2.5">
                  <div className="flex items-center gap-3">
                    <div className="w-11 h-11 rounded-2xl bg-primary/10 text-primary font-bold text-sm flex items-center justify-center overflow-hidden flex-shrink-0">
                      {m.avatar_url ? (
                        <img src={m.avatar_url} alt="" className="w-full h-full object-cover" />
                      ) : (
                        m.full_name.charAt(0)
                      )}
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-1.5">
                        <h4 className="font-bold text-sm truncate">{m.full_name}</h4>
                        {m.is_verified && <ShieldCheck className="w-3.5 h-3.5 text-emerald-600 flex-shrink-0" />}
                      </div>
                      <p className="text-xs text-muted-foreground flex items-center gap-1">
                        <MapPin className="w-3 h-3 text-primary" /> {m.locality}
                      </p>
                    </div>
                  </div>

                  {m.bio && <p className="text-xs text-muted-foreground line-clamp-2 leading-snug">{m.bio}</p>}

                  {/* Skills tags */}
                  {m.skills && m.skills.length > 0 && (
                    <div className="space-y-1">
                      <span className="text-[10px] uppercase font-bold text-muted-foreground tracking-wider block">
                        Skills
                      </span>
                      <div className="flex flex-wrap gap-1">
                        {m.skills.slice(0, 3).map((s, idx) => (
                          <Badge key={idx} variant="outline" className="text-[10px] px-2 py-0.5">
                            {s}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                <div className="pt-2 border-t border-border/40 flex items-center justify-between text-xs">
                  <div className="flex items-center gap-1 text-muted-foreground">
                    <Star className="w-3.5 h-3.5 fill-amber-400 text-amber-400" />
                    <span className="font-bold text-foreground">{m.reputation_score.toFixed(1)}</span>
                    <span className="text-[11px]">({m.completed_exchanges} loans)</span>
                  </div>

                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => toast.success(`Wave sent to ${m.full_name}!`)}
                    className="text-xs h-7 px-3 text-primary hover:bg-primary/10 rounded-lg"
                  >
                    Wave 👋
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        ) : (
          <div className="py-12 text-center text-xs text-muted-foreground">No neighbours match your search.</div>
        )}
      </div>
    </div>
  );
}

