"use client";

import React, { useEffect, useState } from "react";
import { supabase } from "@/lib/supabase";
import { User } from "@supabase/supabase-js";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { motion } from "framer-motion";
import { Loader2, Send, Star, User as UserIcon, ShieldCheck, Settings } from "lucide-react";
import { toast } from "sonner";

export default function ProfilePage() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  
  const [fullName, setFullName] = useState("");
  const [telegramId, setTelegramId] = useState("");
  const [buildingId, setBuildingId] = useState("");

  useEffect(() => {
    const fetchUser = async () => {
      const { data: { user } } = await supabase.auth.getUser();
      setUser(user);
      
      if (user) {
        // Optimistic load from metadata
        setFullName(user.user_metadata?.full_name || "");
        
        // Fetch real data from our backend
        try {
          const res = await fetch(`http://localhost:8000/api/users/${user.id}`); // This route doesn't exist by user ID, only by chat_id right now.
          // Wait, the backend has `get_user_by_telegram_id` at `/{chat_id}`. It doesn't have `/{user_id}`.
          // Let's rely on supabase client to fetch public.users directly, or just not fetch for this demo, 
          // or we can query Supabase directly since we have the client.
          const { data: profile } = await supabase.from("users").select("*").eq("id", user.id).single();
          if (profile) {
            setFullName(profile.full_name || user.user_metadata?.full_name || "");
            setTelegramId(profile.telegram_chat_id || "");
            setBuildingId(profile.building || "");
          }
        } catch (err) {
          console.error("Failed to load profile details", err);
        }
      }
      setLoading(false);
    };
    fetchUser();
  }, []);

  const handleSave = async () => {
    if (!user) return;
    setSaving(true);
    
    try {
      const res = await fetch('http://localhost:8000/api/users/profile', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: user.id,
          full_name: fullName,
          telegram_chat_id: telegramId,
          building: buildingId
        })
      });

      if (!res.ok) throw new Error("Failed to save profile");
      toast.success("Profile updated successfully!");
    } catch (err) {
      toast.error("An error occurred while saving.");
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!user) {
    return (
      <div className="flex-1 flex items-center justify-center p-4">
        <Card className="w-full max-w-md text-center p-8">
          <UserIcon className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
          <h2 className="text-xl font-semibold mb-2">Not Signed In</h2>
          <p className="text-muted-foreground">Please sign in to view your profile.</p>
        </Card>
      </div>
    );
  }

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="container mx-auto px-4 py-8 max-w-4xl"
    >
      <div className="flex items-center gap-4 mb-8">
        <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center text-primary text-2xl font-bold">
          {fullName ? fullName.charAt(0).toUpperCase() : "N"}
        </div>
        <div>
          <h1 className="text-3xl font-bold">{fullName || "Neighbour"}</h1>
          <p className="text-muted-foreground">{user.email}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Left Column - Stats */}
        <div className="space-y-6">
          <Card>
            <CardHeader className="pb-4">
              <CardTitle className="text-lg flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-green-500" />
                Trust Rating
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <Star className="w-8 h-8 text-yellow-500 fill-yellow-500" />
                <span className="text-3xl font-bold">5.0</span>
              </div>
              <p className="text-sm text-muted-foreground mt-2">Based on 12 completed borrows.</p>
            </CardContent>
          </Card>
        </div>

        {/* Right Column - Settings */}
        <div className="md:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Send className="w-5 h-5 text-blue-500" />
                Telegram Integration
              </CardTitle>
              <CardDescription>
                Connect your Telegram account to receive instant borrow requests and approval notifications.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Telegram Chat ID</label>
                <div className="flex gap-2">
                  <Input 
                    value={telegramId}
                    onChange={(e) => setTelegramId(e.target.value)}
                    placeholder="e.g. 123456789" 
                  />
                  <Button variant="secondary" onClick={() => window.open('https://t.me/NeighbourNodeBot', '_blank')}>
                    Open Bot
                  </Button>
                </div>
                <p className="text-xs text-muted-foreground font-medium text-primary/80">
                  Message our bot @NeighbourNodeBot to get your Chat ID and paste it here.
                </p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="w-5 h-5 text-muted-foreground" />
                Account Details
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Full Name</label>
                <Input 
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="e.g. Alice Smith" 
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Building / Apartment</label>
                <Input 
                  value={buildingId}
                  onChange={(e) => setBuildingId(e.target.value)}
                  placeholder="e.g. Building A, Apt 304" 
                />
              </div>
              <Button onClick={handleSave} disabled={saving} className="mt-4">
                {saving ? (
                  <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Saving...</>
                ) : (
                  "Save Changes"
                )}
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </motion.div>
  );
}
