"use client";

import React, { useState, useEffect } from "react";
import {
  BookOpen,
  Search,
  PlusCircle,
  Star,
  MapPin,
  Clock,
  Sparkles,
  HeartHandshake,
  Loader2,
  Calendar,
  X,
  User,
  CheckCircle2,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button, buttonVariants } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { skillsApi } from "@/lib/api";
import { Skill } from "@/types";
import { useAuth } from "@/lib/authContext";
import { toast } from "sonner";
import { motion } from "framer-motion";

const SKILL_CATEGORIES = [
  "All",
  "Programming",
  "Mathematics tutoring",
  "Music lessons",
  "Photography",
  "Repair assistance",
  "Language learning",
  "Academic guidance",
  "Fitness training",
  "Practical skills",
];

export default function SkillsPage() {
  const { user, loginDemo } = useAuth();
  const [skills, setSkills] = useState<Skill[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("All");

  // Request Assistance Dialog
  const [requestSkill, setRequestSkill] = useState<Skill | null>(null);
  const [sessionDate, setSessionDate] = useState(() => {
    const nextWeek = new Date();
    nextWeek.setDate(nextWeek.getDate() + 2);
    nextWeek.setHours(17, 0, 0, 0);
    return nextWeek.toISOString().slice(0, 16);
  });
  const [requestDesc, setRequestDesc] = useState("Hi! I would love to learn from you in a community session.");
  const [requesting, setRequesting] = useState(false);

  // Add Skill Dialog
  const [isAddOpen, setIsAddOpen] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newCategory, setNewCategory] = useState("Programming");
  const [newExperience, setNewExperience] = useState("Intermediate");
  const [newAvailability, setNewAvailability] = useState("Weekends & Evenings");
  const [newDesc, setNewDesc] = useState("");
  const [newExchangeType, setNewExchangeType] = useState("Free / Community Barter");
  const [creating, setCreating] = useState(false);

  const fetchSkills = async () => {
    setLoading(true);
    try {
      const data = await skillsApi.list({
        search: searchQuery.trim() || undefined,
        category: selectedCategory === "All" ? undefined : selectedCategory,
      });
      setSkills(data || []);
    } catch (err) {
      console.error("Failed to load skills:", err);
      toast.error("Failed to load skills from MongoDB.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchSkills();
    }, 250);
    return () => clearTimeout(timer);
  }, [searchQuery, selectedCategory]);

  const handleRequestSubmit = async () => {
    if (!user) {
      toast.error("Please sign in or use a demo account to request skills.");
      return;
    }
    if (!requestSkill) return;

    setRequesting(true);
    try {
      await skillsApi.requestAssistance({
        skill_id: requestSkill.id,
        requested_date: new Date(sessionDate).toISOString(),
        description: requestDesc.trim(),
      });
      toast.success("Skill exchange request sent to provider!");
      setRequestSkill(null);
    } catch (err: any) {
      toast.error(err.message || "Failed to submit request.");
    } finally {
      setRequesting(false);
    }
  };

  const handleCreateSkill = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) {
      toast.error("Please sign in to offer a skill.");
      return;
    }
    setCreating(true);
    try {
      await skillsApi.create({
        title: newTitle.trim(),
        category: newCategory,
        experience_level: newExperience,
        availability: newAvailability,
        description: newDesc.trim(),
        exchange_type: newExchangeType,
        locality: user.locality || "Mathikere, Bengaluru",
      });
      toast.success("Skill listing published in community marketplace!");
      setIsAddOpen(false);
      fetchSkills();
    } catch (err: any) {
      toast.error(err.message || "Failed to create skill.");
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl space-y-8">
      {/* Hero Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-8 rounded-3xl bg-gradient-to-r from-card via-muted/30 to-card border border-border/60 shadow-sm">
        <div className="space-y-1.5 max-w-2xl">
          <Badge className="bg-primary/10 text-primary border-primary/20 text-xs gap-1.5 font-semibold">
            <BookOpen className="w-3.5 h-3.5" /> Peer-to-Peer Knowledge Sharing
          </Badge>
          <h1 className="text-3xl font-extrabold tracking-tight">Skills & Services Marketplace</h1>
          <p className="text-xs sm:text-sm text-muted-foreground leading-relaxed">
            Connect with neighbours to learn coding, get math tutoring, pick up guitar, repair home appliances, or practice French.
          </p>
        </div>

        <div>
          {user ? (
            <Button
              onClick={() => setIsAddOpen(true)}
              className="rounded-2xl gap-2 h-11 px-6 font-semibold shadow-md shadow-primary/20"
            >
              <PlusCircle className="w-4 h-4" /> Offer a Skill
            </Button>
          ) : (
            <Button
              variant="outline"
              onClick={() => loginDemo("skills")}
              className="rounded-2xl gap-2 h-11 px-5 text-xs font-semibold"
            >
              ⚡ Sign In as Skill Provider
            </Button>
          )}
        </div>
      </div>

      {/* Search and Category Filter Bar */}
      <div className="space-y-4">
        <div className="relative max-w-2xl">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search skills (e.g., Python, Guitar, Calculus, Photography, Bicycles)..."
            className="pl-11 pr-10 h-12 rounded-2xl text-sm border-border/70"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery("")}
              className="absolute right-3.5 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground p-1"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Categories Bar */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-2 scrollbar-none">
          {SKILL_CATEGORIES.map((cat) => {
            const isSelected = selectedCategory === cat;
            return (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-3.5 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-all ${
                  isSelected
                    ? "bg-primary text-primary-foreground shadow-sm"
                    : "bg-muted/60 text-muted-foreground hover:bg-muted hover:text-foreground border border-border/40"
                }`}
              >
                {cat}
              </button>
            );
          })}
        </div>
      </div>

      {/* Grid of Skills */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {[1, 2, 3, 4, 5, 6].map((n) => (
            <div key={n} className="rounded-3xl border border-border/40 bg-card h-64 animate-pulse p-6 space-y-3">
              <div className="h-4 bg-muted rounded w-1/3" />
              <div className="h-6 bg-muted rounded w-3/4" />
              <div className="h-12 bg-muted rounded w-full" />
            </div>
          ))}
        </div>
      ) : skills.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {skills.map((skill) => (
            <Card
              key={skill.id}
              className="rounded-3xl border-border/60 hover:border-primary/40 transition-all duration-200 shadow-sm hover:shadow-md flex flex-col justify-between bg-card"
            >
              <CardHeader className="p-6 pb-3 space-y-2.5">
                <div className="flex items-center justify-between gap-2">
                  <Badge variant="secondary" className="text-[11px] font-medium bg-muted">
                    {skill.category}
                  </Badge>
                  <Badge variant="outline" className="text-[10px] font-semibold">
                    {skill.experience_level}
                  </Badge>
                </div>

                <CardTitle className="text-lg font-bold tracking-tight text-foreground line-clamp-1">
                  {skill.title}
                </CardTitle>
                <CardDescription className="text-xs line-clamp-3 leading-relaxed text-muted-foreground">
                  {skill.description}
                </CardDescription>
              </CardHeader>

              <CardContent className="px-6 py-2 space-y-2.5 text-xs text-muted-foreground">
                <div className="flex items-center gap-1.5">
                  <Clock className="w-3.5 h-3.5 text-primary flex-shrink-0" />
                  <span className="truncate">{skill.availability}</span>
                </div>

                <div className="flex items-center justify-between pt-2 border-t border-border/40">
                  <div className="flex items-center gap-2">
                    <div className="w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center font-bold text-primary text-[10px]">
                      {skill.provider?.avatar_url ? (
                        <img src={skill.provider.avatar_url} alt="" className="w-full h-full object-cover rounded-full" />
                      ) : (
                        skill.provider?.full_name?.charAt(0) || "U"
                      )}
                    </div>
                    <span className="font-medium text-foreground text-[11px] truncate max-w-[120px]">
                      {skill.provider?.full_name || "Neighbour"}
                    </span>
                  </div>

                  <span className="text-[11px] font-semibold text-primary">{skill.exchange_type}</span>
                </div>
              </CardContent>

              <CardFooter className="p-6 pt-2">
                <Button
                  size="sm"
                  onClick={() => setRequestSkill(skill)}
                  className="w-full rounded-xl text-xs font-semibold h-9 shadow-sm"
                >
                  Request Session
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>
      ) : (
        <div className="py-16 text-center space-y-3 border border-dashed rounded-3xl p-8 bg-muted/20">
          <BookOpen className="w-10 h-10 text-muted-foreground mx-auto opacity-50" />
          <h3 className="font-bold text-base">No skills found</h3>
          <p className="text-xs text-muted-foreground max-w-sm mx-auto">
            Try a different search term or category. You can also offer a new skill for your neighbours!
          </p>
        </div>
      )}

      {/* Request Skill Modal */}
      {requestSkill && (
        <Dialog open={!!requestSkill} onOpenChange={(open) => !open && setRequestSkill(null)}>
          <DialogContent className="sm:max-w-[480px] rounded-3xl">
            <DialogHeader>
              <DialogTitle className="text-lg font-bold">Request Skill Exchange</DialogTitle>
              <DialogDescription className="text-xs">
                {requestSkill.title} • {requestSkill.provider?.full_name || "Provider"}
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4 py-2">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-muted-foreground">Proposed Date & Time</label>
                <Input
                  type="datetime-local"
                  value={sessionDate}
                  onChange={(e) => setSessionDate(e.target.value)}
                  className="rounded-xl text-xs"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-muted-foreground">Note / Goals for Session</label>
                <Textarea
                  rows={3}
                  value={requestDesc}
                  onChange={(e) => setRequestDesc(e.target.value)}
                  placeholder="Explain what specific topics or tasks you'd like guidance with..."
                  className="rounded-xl text-xs resize-none"
                />
              </div>

              <div className="p-3.5 rounded-2xl bg-muted/50 text-[11px] text-muted-foreground space-y-1">
                <span className="font-semibold text-foreground">Exchange Arrangement:</span>
                <p>{requestSkill.exchange_type} • Community peer-learning model</p>
              </div>
            </div>

            <DialogFooter>
              <Button variant="outline" size="sm" onClick={() => setRequestSkill(null)}>
                Cancel
              </Button>
              <Button size="sm" disabled={requesting} onClick={handleRequestSubmit}>
                {requesting ? "Submitting..." : "Send Request"}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      )}

      {/* Add Skill Modal */}
      <Dialog open={isAddOpen} onOpenChange={setIsAddOpen}>
        <DialogContent className="sm:max-w-[500px] rounded-3xl">
          <DialogHeader>
            <DialogTitle className="text-lg font-bold">Offer a Community Skill</DialogTitle>
            <DialogDescription className="text-xs">
              Share your skills with neighbours in Bengaluru.
            </DialogDescription>
          </DialogHeader>

          <form onSubmit={handleCreateSkill} className="space-y-3.5 py-2">
            <div className="space-y-1">
              <label className="text-xs font-semibold text-muted-foreground">Skill Title *</label>
              <Input
                placeholder='e.g., "Beginner Acoustic Guitar Lessons"'
                value={newTitle}
                onChange={(e) => setNewTitle(e.target.value)}
                required
                className="rounded-xl text-xs h-10"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <label className="text-xs font-semibold text-muted-foreground">Category</label>
                <select
                  value={newCategory}
                  onChange={(e) => setNewCategory(e.target.value)}
                  className="w-full h-10 rounded-xl border border-input bg-background px-3 text-xs"
                >
                  {SKILL_CATEGORIES.filter((c) => c !== "All").map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))}
                </select>
              </div>

              <div className="space-y-1">
                <label className="text-xs font-semibold text-muted-foreground">Experience Level</label>
                <select
                  value={newExperience}
                  onChange={(e) => setNewExperience(e.target.value)}
                  className="w-full h-10 rounded-xl border border-input bg-background px-3 text-xs"
                >
                  <option value="Beginner">Beginner</option>
                  <option value="Intermediate">Intermediate</option>
                  <option value="Expert">Expert</option>
                </select>
              </div>
            </div>

            <div className="space-y-1">
              <label className="text-xs font-semibold text-muted-foreground">Availability</label>
              <Input
                placeholder="e.g. Saturdays 3 PM - 6 PM"
                value={newAvailability}
                onChange={(e) => setNewAvailability(e.target.value)}
                className="rounded-xl text-xs h-10"
              />
            </div>

            <div className="space-y-1">
              <label className="text-xs font-semibold text-muted-foreground">Exchange Arrangement</label>
              <select
                value={newExchangeType}
                onChange={(e) => setNewExchangeType(e.target.value)}
                className="w-full h-10 rounded-xl border border-input bg-background px-3 text-xs"
              >
                <option value="Free / Community Barter">Free / Community Barter</option>
                <option value="Skill Swap">Skill Swap (trade 1:1)</option>
                <option value="Optional Stipend">Optional Stipend</option>
              </select>
            </div>

            <div className="space-y-1">
              <label className="text-xs font-semibold text-muted-foreground">Description *</label>
              <Textarea
                rows={3}
                placeholder="What will you teach or help with? Any prerequisites? Equipment provided?..."
                value={newDesc}
                onChange={(e) => setNewDesc(e.target.value)}
                required
                className="rounded-xl text-xs resize-none"
              />
            </div>

            <DialogFooter className="pt-2">
              <Button type="button" variant="outline" size="sm" onClick={() => setIsAddOpen(false)}>
                Cancel
              </Button>
              <Button type="submit" size="sm" disabled={creating}>
                {creating ? "Publishing..." : "Publish Skill"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}

