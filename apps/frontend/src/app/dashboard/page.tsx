"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  PackageSearch,
  PlusCircle,
  Clock,
  CheckCircle2,
  AlertCircle,
  Star,
  Users,
  BookOpen,
  ArrowRight,
  MapPin,
  ShieldCheck,
  Calendar,
  XCircle,
  Repeat,
  Loader2,
  Sparkles,
} from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Button, buttonVariants } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/lib/authContext";
import {
  analyticsApi,
  borrowApi,
  recommendationsApi,
  resourcesApi,
  skillsApi,
} from "@/lib/api";
import {
  BorrowRequest,
  NeighbourRecommendation,
  Resource,
  ResourceRecommendation,
  Skill,
  UserAnalytics,
} from "@/types";
import { toast } from "sonner";
import { ItemCard } from "@/components/ItemCard";

export default function DashboardPage() {
  const { user, loginDemo, isLoading: authLoading } = useAuth();
  const [analytics, setAnalytics] = useState<UserAnalytics | null>(null);
  const [myResources, setMyResources] = useState<Resource[]>([]);
  const [mySkills, setMySkills] = useState<Skill[]>([]);
  const [borrowRequests, setBorrowRequests] = useState<BorrowRequest[]>([]);
  const [incomingRequests, setIncomingRequests] = useState<BorrowRequest[]>([]);
  const [recommendedResources, setRecommendedResources] = useState<ResourceRecommendation[]>([]);
  const [recommendedNeighbours, setRecommendedNeighbours] = useState<NeighbourRecommendation[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchDashboardData = async () => {
    if (!user) return;
    setLoading(true);
    try {
      const [
        statsData,
        resData,
        skillsData,
        borrowData,
        ownerData,
        recResData,
        recNeighboursData,
      ] = await Promise.all([
        analyticsApi.getMe().catch(() => null),
        resourcesApi.list({ owner_id: user.id }),
        skillsApi.list({ provider_id: user.id }),
        borrowApi.listRequests("borrower"),
        borrowApi.listRequests("owner"),
        recommendationsApi.getResources({ limit: 4 }),
        recommendationsApi.getNeighbours(4),
      ]);

      setAnalytics(statsData);
      setMyResources(resData || []);
      setMySkills(skillsData || []);
      setBorrowRequests(borrowData || []);
      setIncomingRequests(ownerData || []);
      setRecommendedResources(recResData || []);
      setRecommendedNeighbours(recNeighboursData || []);
    } catch (err) {
      console.error("Dashboard fetch error:", err);
      toast.error("Failed to load some dashboard records.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user) {
      fetchDashboardData();
    } else if (!authLoading) {
      setLoading(false);
    }
  }, [user, authLoading]);

  const handleApproveRequest = async (requestId: string) => {
    try {
      const res = await borrowApi.approve(requestId);
      toast.success(res.message || "Borrow request approved! Reservation active.");
      fetchDashboardData();
    } catch (err: any) {
      toast.error(err.message || "Failed to approve request.");
    }
  };

  const handleRejectRequest = async (requestId: string) => {
    try {
      await borrowApi.reject(requestId, "Unavailable at requested timeframe.");
      toast.info("Borrow request rejected.");
      fetchDashboardData();
    } catch (err: any) {
      toast.error(err.message || "Failed to reject request.");
    }
  };

  const handleConfirmReturn = async (requestId: string) => {
    try {
      await borrowApi.returnLoan(requestId);
      toast.success("Resource marked as returned and available again!");
      fetchDashboardData();
    } catch (err: any) {
      toast.error(err.message || "Failed to confirm return.");
    }
  };

  if (authLoading) {
    return (
      <div className="flex-1 flex items-center justify-center p-8">
        <Loader2 className="w-8 h-8 text-primary animate-spin" />
      </div>
    );
  }

  // Guest State / Not Logged In
  if (!user) {
    return (
      <div className="flex-1 flex items-center justify-center p-6 bg-muted/20">
        <Card className="w-full max-w-md text-center p-8 rounded-3xl shadow-lg border-border/60 space-y-4">
          <div className="w-14 h-14 bg-primary/10 text-primary rounded-2xl flex items-center justify-center mx-auto">
            <Users className="w-7 h-7" />
          </div>
          <CardTitle className="text-2xl font-bold">Sign In to View Dashboard</CardTitle>
          <CardDescription className="text-xs max-w-xs mx-auto">
            Log in to manage your listed community resources, respond to borrow requests, and track active loans.
          </CardDescription>

          <div className="space-y-2 pt-2">
            <Link href="/auth/signin" className={buttonVariants({ className: "w-full rounded-xl" })}>
              Sign In
            </Link>
            <div className="pt-2 text-xs text-muted-foreground">
              <span>Or test with a demo account:</span>
              <div className="grid grid-cols-2 gap-2 mt-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => loginDemo("borrower")}
                  className="text-xs rounded-xl"
                >
                  ⚡ Demo Borrower
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => loginDemo("owner")}
                  className="text-xs rounded-xl"
                >
                  ⚡ Demo Owner
                </Button>
              </div>
            </div>
          </div>
        </Card>
      </div>
    );
  }

  const activeBorrows = borrowRequests.filter(
    (r) => r.status === "APPROVED" || r.status === "RESERVED" || r.status === "ACTIVE"
  );
  const pendingIncoming = incomingRequests.filter((r) => r.status === "PENDING_APPROVAL");
  const activeLoans = incomingRequests.filter(
    (r) => r.status === "APPROVED" || r.status === "RESERVED" || r.status === "ACTIVE"
  );

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl space-y-8">
      {/* Header Profile Greeting */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 rounded-3xl bg-card border border-border/60 shadow-sm">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-2xl bg-primary/10 text-primary font-bold text-xl flex items-center justify-center overflow-hidden border border-primary/20 flex-shrink-0">
            {user.avatar_url ? (
              <img src={user.avatar_url} alt={user.full_name} className="w-full h-full object-cover" />
            ) : (
              user.full_name.charAt(0)
            )}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold tracking-tight">Welcome, {user.full_name}</h1>
              {user.is_verified && (
                <Badge variant="secondary" className="bg-emerald-500/10 text-emerald-600 text-[10px] gap-1 font-semibold">
                  <ShieldCheck className="w-3 h-3" /> Verified Member
                </Badge>
              )}
            </div>
            <p className="text-xs text-muted-foreground mt-0.5 flex items-center gap-1.5">
              <MapPin className="w-3.5 h-3.5 text-primary" /> {user.locality}
              {user.building && ` • ${user.building}`}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Trust Score Box */}
          <div className="flex items-center gap-2.5 px-4 py-2.5 rounded-2xl bg-muted/60 border border-border/40">
            <div className="w-8 h-8 rounded-xl bg-amber-400/20 text-amber-500 flex items-center justify-center">
              <Star className="w-4 h-4 fill-amber-400 text-amber-400" />
            </div>
            <div className="flex flex-col">
              <span className="text-xs text-muted-foreground font-medium">Reputation</span>
              <span className="text-sm font-bold text-foreground">
                {user.reputation_score ? user.reputation_score.toFixed(1) : "4.8"} / 5.0
              </span>
            </div>
          </div>

          <Link href="/resources/new" className={buttonVariants({ className: "rounded-2xl gap-1.5 font-semibold text-xs h-11 px-5" })}>
            <PlusCircle className="w-4 h-4" /> Add Listing
          </Link>
        </div>
      </div>

      {/* Metric Tiles */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="rounded-2xl border-border/60 p-5 space-y-1 shadow-sm">
          <span className="text-xs text-muted-foreground font-medium">My Resources Listed</span>
          <div className="text-2xl font-bold text-foreground">{myResources.length}</div>
          <span className="text-[11px] text-muted-foreground">in community catalog</span>
        </Card>

        <Card className="rounded-2xl border-border/60 p-5 space-y-1 shadow-sm">
          <span className="text-xs text-muted-foreground font-medium">Pending Approvals</span>
          <div className="text-2xl font-bold text-amber-600">{pendingIncoming.length}</div>
          <span className="text-[11px] text-muted-foreground">needs your action</span>
        </Card>

        <Card className="rounded-2xl border-border/60 p-5 space-y-1 shadow-sm">
          <span className="text-xs text-muted-foreground font-medium">Active Borrowings</span>
          <div className="text-2xl font-bold text-emerald-600">{activeBorrows.length}</div>
          <span className="text-[11px] text-muted-foreground">currently with you</span>
        </Card>

        <Card className="rounded-2xl border-border/60 p-5 space-y-1 shadow-sm">
          <span className="text-xs text-muted-foreground font-medium">Skills Offered</span>
          <div className="text-2xl font-bold text-blue-600">{mySkills.length}</div>
          <span className="text-[11px] text-muted-foreground">active skill listings</span>
        </Card>
      </div>

      {/* Main Tabs Navigation */}
      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="bg-muted/60 p-1 rounded-2xl flex-wrap h-auto gap-1">
          <TabsTrigger value="overview" className="rounded-xl text-xs font-semibold px-4 py-2">
            Overview & Recommendations
          </TabsTrigger>
          <TabsTrigger value="incoming" className="rounded-xl text-xs font-semibold px-4 py-2 relative">
            Incoming Requests
            {pendingIncoming.length > 0 && (
              <span className="ml-1.5 px-1.5 py-0.2 bg-amber-600 text-white rounded-full text-[10px]">
                {pendingIncoming.length}
              </span>
            )}
          </TabsTrigger>
          <TabsTrigger value="borrows" className="rounded-xl text-xs font-semibold px-4 py-2">
            My Borrows ({borrowRequests.length})
          </TabsTrigger>
          <TabsTrigger value="listings" className="rounded-xl text-xs font-semibold px-4 py-2">
            My Listings ({myResources.length})
          </TabsTrigger>
          <TabsTrigger value="skills" className="rounded-xl text-xs font-semibold px-4 py-2">
            My Skills ({mySkills.length})
          </TabsTrigger>
        </TabsList>

        {/* ─── TAB 1: OVERVIEW & INTELLIGENT RECOMMENDATIONS ────── */}
        <TabsContent value="overview" className="space-y-8">
          {/* Pending Approval Alert Banner */}
          {pendingIncoming.length > 0 && (
            <div className="p-4 rounded-2xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <Clock className="w-5 h-5 text-amber-600 flex-shrink-0" />
                <div className="text-xs">
                  <span className="font-bold text-foreground">
                    You have {pendingIncoming.length} borrow request(s) waiting for approval!
                  </span>
                  <p className="text-muted-foreground">Neighbours are waiting for your confirmation.</p>
                </div>
              </div>
              <TabsTrigger
                value="incoming"
                className="text-xs bg-amber-600 text-white hover:bg-amber-700 font-semibold px-4 py-1.5 rounded-xl shadow-sm"
              >
                Review Now
              </TabsTrigger>
            </div>
          )}

          {/* Recommended Resources (Intelligent Matchmaking) */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-bold tracking-tight flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-primary" /> Recommended Nearby Resources
                </h3>
                <p className="text-xs text-muted-foreground">
                  Personalized based on distance, owner trust rating, and category relevance.
                </p>
              </div>
              <Link href="/catalog" className="text-xs text-primary font-medium hover:underline flex items-center gap-1">
                View all <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {recommendedResources.map((rec) => (
                <div key={rec.resource.id} className="relative group">
                  <ItemCard item={rec.resource} />
                  <div className="mt-1 text-[11px] text-muted-foreground px-1 line-clamp-1 italic">
                    ⭐ {rec.breakdown.explanation}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Recommended Neighbours (Community Graph) */}
          <div className="space-y-4 pt-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-bold tracking-tight flex items-center gap-2">
                  <Users className="w-4 h-4 text-primary" /> Neighbours with Shared Interests
                </h3>
                <p className="text-xs text-muted-foreground">
                  Connect with residents sharing DIY, robotics, sports, and academic interests.
                </p>
              </div>
              <Link href="/community" className="text-xs text-primary font-medium hover:underline flex items-center gap-1">
                Explore community <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {recommendedNeighbours.map((rec) => (
                <Card key={rec.neighbour.id} className="p-4 rounded-2xl border-border/60 space-y-3 bg-card shadow-sm">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center font-bold text-primary text-xs overflow-hidden">
                      {rec.neighbour.avatar_url ? (
                        <img src={rec.neighbour.avatar_url} alt="" className="w-full h-full object-cover" />
                      ) : (
                        rec.neighbour.full_name.charAt(0)
                      )}
                    </div>
                    <div className="min-w-0 flex-1">
                      <h4 className="font-semibold text-sm truncate">{rec.neighbour.full_name}</h4>
                      <p className="text-[11px] text-muted-foreground truncate">{rec.neighbour.locality.split(",")[0]}</p>
                    </div>
                  </div>

                  <div className="flex flex-wrap gap-1">
                    {rec.shared_interests.map((int, i) => (
                      <Badge key={i} variant="secondary" className="text-[10px] px-2 py-0.5">
                        {int}
                      </Badge>
                    ))}
                  </div>

                  <div className="pt-1 text-[11px] text-muted-foreground flex items-center justify-between border-t border-border/40">
                    <span>Reputation: {rec.neighbour.reputation_score.toFixed(1)}/5</span>
                    <Link href={`/community`} className="text-primary hover:underline font-medium">
                      Connect
                    </Link>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        </TabsContent>

        {/* ─── TAB 2: INCOMING REQUESTS & OWNER ACTIONS ─────────── */}
        <TabsContent value="incoming" className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-base">Requests Received from Neighbours</h3>
            <span className="text-xs text-muted-foreground">{incomingRequests.length} total request(s)</span>
          </div>

          {incomingRequests.length === 0 ? (
            <div className="py-12 text-center space-y-2 border border-dashed rounded-2xl p-6 bg-muted/10">
              <PackageSearch className="w-8 h-8 text-muted-foreground mx-auto opacity-50" />
              <p className="text-sm font-semibold">No requests received yet</p>
              <p className="text-xs text-muted-foreground">
                When neighbours request to borrow your listings, they will show up here for your approval.
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {incomingRequests.map((req) => (
                <Card key={req.id} className="p-4 rounded-2xl border-border/60 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-sm text-foreground">{req.resource_title || "Item"}</span>
                      <Badge
                        variant="secondary"
                        className={`text-[10px] font-semibold ${
                          req.status === "PENDING_APPROVAL"
                            ? "bg-amber-500/10 text-amber-600"
                            : req.status === "APPROVED" || req.status === "RESERVED"
                            ? "bg-emerald-500/10 text-emerald-600"
                            : ""
                        }`}
                      >
                        {req.status}
                      </Badge>
                    </div>
                    <p className="text-xs text-muted-foreground">
                      Requested by <strong className="text-foreground">{req.borrower_name || "Neighbour"}</strong>
                    </p>
                    <p className="text-[11px] text-muted-foreground italic">"{req.message}"</p>
                    <div className="text-[11px] text-muted-foreground flex items-center gap-1.5 pt-1">
                      <Calendar className="w-3 h-3 text-primary" />
                      <span>
                        {new Date(req.requested_start).toLocaleDateString()} →{" "}
                        {new Date(req.requested_end).toLocaleDateString()}
                      </span>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex items-center gap-2 w-full sm:w-auto">
                    {req.status === "PENDING_APPROVAL" && (
                      <>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleRejectRequest(req.id)}
                          className="text-xs rounded-xl flex-1 sm:flex-none text-muted-foreground hover:text-destructive"
                        >
                          Decline
                        </Button>
                        <Button
                          size="sm"
                          onClick={() => handleApproveRequest(req.id)}
                          className="text-xs rounded-xl flex-1 sm:flex-none font-semibold bg-emerald-600 hover:bg-emerald-700 text-white"
                        >
                          Approve Loan
                        </Button>
                      </>
                    )}

                    {(req.status === "APPROVED" || req.status === "RESERVED" || req.status === "ACTIVE") && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleConfirmReturn(req.id)}
                        className="text-xs rounded-xl gap-1 text-emerald-600 border-emerald-500/40 hover:bg-emerald-500/10"
                      >
                        <CheckCircle2 className="w-3.5 h-3.5" /> Confirm Return
                      </Button>
                    )}
                  </div>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        {/* ─── TAB 3: MY BORROWS ───────────────────────────────── */}
        <TabsContent value="borrows" className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-base">Items You Have Requested or Borrowed</h3>
            <Link href="/catalog" className="text-xs text-primary font-medium hover:underline">
              + Borrow another item
            </Link>
          </div>

          {borrowRequests.length === 0 ? (
            <div className="py-12 text-center space-y-2 border border-dashed rounded-2xl p-6 bg-muted/10">
              <PackageSearch className="w-8 h-8 text-muted-foreground mx-auto opacity-50" />
              <p className="text-sm font-semibold">No active borrows</p>
              <p className="text-xs text-muted-foreground">
                Browse your neighbourhood catalog to borrow drills, camping kits, or textbooks.
              </p>
              <Link href="/catalog" className={buttonVariants({ size: "sm", className: "rounded-xl mt-2 text-xs" })}>
                Browse Catalog
              </Link>
            </div>
          ) : (
            <div className="space-y-3">
              {borrowRequests.map((req) => (
                <Card key={req.id} className="p-4 rounded-2xl border-border/60 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-sm text-foreground">{req.resource_title || "Item"}</span>
                      <Badge variant="outline" className="text-[10px]">
                        {req.status}
                      </Badge>
                    </div>
                    <p className="text-xs text-muted-foreground">
                      Owner: <strong className="text-foreground">{req.owner_name || "Community Member"}</strong>
                    </p>
                    <div className="text-[11px] text-muted-foreground flex items-center gap-1.5 pt-1">
                      <Calendar className="w-3 h-3 text-primary" />
                      <span>
                        {new Date(req.requested_start).toLocaleDateString()} →{" "}
                        {new Date(req.requested_end).toLocaleDateString()}
                      </span>
                    </div>
                  </div>

                  {(req.status === "ACTIVE" || req.status === "RESERVED" || req.status === "APPROVED") && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleConfirmReturn(req.id)}
                      className="text-xs rounded-xl"
                    >
                      I have returned this
                    </Button>
                  )}
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        {/* ─── TAB 4: MY LISTINGS ──────────────────────────────── */}
        <TabsContent value="listings" className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-base">Your Active Resources</h3>
            <Link href="/resources/new" className={buttonVariants({ size: "sm", className: "rounded-xl text-xs gap-1" })}>
              <PlusCircle className="w-3.5 h-3.5" /> Add Resource
            </Link>
          </div>

          {myResources.length === 0 ? (
            <div className="py-12 text-center space-y-2 border border-dashed rounded-2xl p-6 bg-muted/10">
              <PackageSearch className="w-8 h-8 text-muted-foreground mx-auto opacity-50" />
              <p className="text-sm font-semibold">You have not listed any items yet</p>
              <p className="text-xs text-muted-foreground">
                Lend tools, study material, or equipment sitting unused in your closet.
              </p>
              <Link href="/resources/new" className={buttonVariants({ size: "sm", className: "rounded-xl mt-2 text-xs" })}>
                Add your first item
              </Link>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
              {myResources.map((item) => (
                <ItemCard key={item.id} item={item} />
              ))}
            </div>
          )}
        </TabsContent>

        {/* ─── TAB 5: MY SKILLS ────────────────────────────────── */}
        <TabsContent value="skills" className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-base">Skills You Offer to Neighbours</h3>
            <Link href="/skills" className={buttonVariants({ size: "sm", className: "rounded-xl text-xs" })}>
              Explore Skills Marketplace
            </Link>
          </div>

          {mySkills.length === 0 ? (
            <div className="py-12 text-center space-y-2 border border-dashed rounded-2xl p-6 bg-muted/10">
              <BookOpen className="w-8 h-8 text-muted-foreground mx-auto opacity-50" />
              <p className="text-sm font-semibold">No skills listed yet</p>
              <p className="text-xs text-muted-foreground">
                Teach guitar, Python coding, photography, or cycle repair to neighbours in your complex.
              </p>
              <Link href="/skills" className={buttonVariants({ size: "sm", className: "rounded-xl mt-2 text-xs" })}>
                Add Skill Listing
              </Link>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {mySkills.map((skill) => (
                <Card key={skill.id} className="p-4 rounded-2xl border-border/60 space-y-2">
                  <Badge variant="outline" className="text-[10px]">
                    {skill.category}
                  </Badge>
                  <h4 className="font-bold text-base">{skill.title}</h4>
                  <p className="text-xs text-muted-foreground line-clamp-2">{skill.description}</p>
                  <div className="pt-2 text-[11px] text-muted-foreground flex justify-between border-t border-border/40">
                    <span>{skill.experience_level}</span>
                    <span className="font-medium text-primary">{skill.exchange_type}</span>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
