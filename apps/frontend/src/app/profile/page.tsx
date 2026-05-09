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
  const [telegramId, setTelegramId] = useState("");
  const [buildingId, setBuildingId] = useState("");

  useEffect(() => {
    const fetchUser = async () => {
      const { data } = await supabase.auth.getUser();
      setUser(data.user);
      // In a real app, we'd fetch the public.users table data here
      // to get the actual telegram_chat_id and building_id
      setLoading(false);
    };
    fetchUser();
  }, []);

  const handleSave = async () => {
    setSaving(true);
    // Stub for saving user preferences
    setTimeout(() => {
      setSaving(false);
      toast.success("Profile updated successfully!");
    }, 1000);
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

  const fullName = user.user_metadata?.full_name || "Neighbour";

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="container mx-auto px-4 py-8 max-w-4xl"
    >
      <div className="flex items-center gap-4 mb-8">
        <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center text-primary text-2xl font-bold">
          {fullName.charAt(0).toUpperCase()}
        </div>
        <div>
          <h1 className="text-3xl font-bold">{fullName}</h1>
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
                <p className="text-xs text-muted-foreground">Message /start to the bot to get your ID.</p>
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
                <label className="text-sm font-medium">Building / Apartment</label>
                <Input 
                  value={buildingId}
                  onChange={(e) => setBuildingId(e.target.value)}
                  placeholder="e.g. Building A, Apt 304" 
                />
              </div>
              <Button onClick={handleSave} disabled={saving}>
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
