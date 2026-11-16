"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import {
  Sparkles,
  MapPin,
  BookOpen,
  Heart,
  CheckCircle2,
  ArrowRight,
  ArrowLeft,
  Building,
  Phone,
  User,
  Clock,
  Shield,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/lib/authContext";
import { usersApi } from "@/lib/api";
import { toast } from "sonner";

const AVAILABLE_SKILLS = [
  "Python Programming",
  "Mathematics Tutoring",
  "Guitar Lessons",
  "Portrait Photography",
  "Bicycle Maintenance",
  "Home Appliance Repair",
  "Balcony Gardening",
  "PCB Soldering & Electronics",
  "French / Language Tutoring",
  "Fitness & Calisthenics",
];

const AVAILABLE_INTERESTS = [
  "DIY & Hardware",
  "Robotics",
  "Cycling",
  "Reading & Book Club",
  "Camping & Trekking",
  "Board Games",
  "Urban Farming",
  "Coffee & Baking",
  "Music & Guitars",
  "Woodworking",
];

export default function OnboardingPage() {
  const router = useRouter();
  const { user, refreshUser } = useAuth();
  const [step, setStep] = useState(1);
  const [saving, setSaving] = useState(false);

  // Form State
  const [fullName, setFullName] = useState("");
  const [phone, setPhone] = useState("");
  const [locality, setLocality] = useState("Mathikere, Bengaluru");
  const [building, setBuilding] = useState("");
  const [unit, setUnit] = useState("");
  const [bio, setBio] = useState("");
  const [selectedSkills, setSelectedSkills] = useState<string[]>([]);
  const [selectedInterests, setSelectedInterests] = useState<string[]>([]);
  const [customSkill, setCustomSkill] = useState("");
  const [customInterest, setCustomInterest] = useState("");
  const [locationConsent, setLocationConsent] = useState(true);

  useEffect(() => {
    if (user) {
      setFullName(user.full_name || "");
      setPhone(user.phone || "");
      setLocality(user.locality || "Mathikere, Bengaluru");
      setBuilding(user.building || "");
      setUnit(user.unit || "");
      setBio(user.bio || "");
      setSelectedSkills(user.skills || []);
      setSelectedInterests(user.interests || []);
    }
  }, [user]);

  const toggleSkill = (skill: string) => {
    if (selectedSkills.includes(skill)) {
      setSelectedSkills(selectedSkills.filter((s) => s !== skill));
    } else {
      setSelectedSkills([...selectedSkills, skill]);
    }
  };

  const toggleInterest = (interest: string) => {
    if (selectedInterests.includes(interest)) {
      setSelectedInterests(selectedInterests.filter((i) => i !== interest));
    } else {
      setSelectedInterests([...selectedInterests, interest]);
    }
  };

  const addCustomSkill = () => {
    if (customSkill.trim() && !selectedSkills.includes(customSkill.trim())) {
      setSelectedSkills([...selectedSkills, customSkill.trim()]);
      setCustomSkill("");
    }
  };

  const addCustomInterest = () => {
    if (customInterest.trim() && !selectedInterests.includes(customInterest.trim())) {
      setSelectedInterests([...selectedInterests, customInterest.trim()]);
      setCustomInterest("");
    }
  };

  const handleFinish = async () => {
    setSaving(true);
    try {
      await usersApi.updateMe({
        full_name: fullName,
        phone,
        locality,
        building,
        unit,
        bio,
        skills: selectedSkills,
        interests: selectedInterests,
        location_visibility: locationConsent ? "approximate" : "hidden",
      });
      await refreshUser();
      toast.success("Profile setup complete! Welcome to your neighbourhood community.");
      router.push("/dashboard");
    } catch (err: any) {
      toast.error(err.message || "Failed to update profile.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center p-4 bg-muted/20">
      <motion.div
        key={step}
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: -20 }}
        transition={{ duration: 0.3 }}
        className="w-full max-w-xl"
      >
        <Card className="shadow-xl border-border/60 rounded-3xl overflow-hidden">
          {/* Step Progress Bar */}
          <div className="h-1.5 w-full bg-muted flex">
            <div
              className="bg-primary transition-all duration-300"
              style={{ width: `${(step / 3) * 100}%` }}
            />
          </div>

          <CardHeader className="text-center pt-8 pb-4">
            <div className="w-12 h-12 bg-primary/10 text-primary rounded-2xl flex items-center justify-center mx-auto mb-3">
              {step === 1 && <User className="w-6 h-6" />}
              {step === 2 && <BookOpen className="w-6 h-6" />}
              {step === 3 && <Heart className="w-6 h-6" />}
            </div>
            <CardTitle className="text-2xl font-bold">
              {step === 1 && "Personal & Locality Profile"}
              {step === 2 && "Skills You Can Share"}
              {step === 3 && "Interests & Community Preferences"}
            </CardTitle>
            <CardDescription className="text-xs">
              Step {step} of 3 • Customizing your local sharing experience
            </CardDescription>
          </CardHeader>

          <CardContent className="space-y-4 px-6 sm:px-8">
            {/* STEP 1: IDENTITY & RESIDENTIAL LOCALITY */}
            {step === 1 && (
              <div className="space-y-3.5">
                <div className="space-y-1">
                  <label className="text-xs font-semibold text-muted-foreground">Full Name</label>
                  <Input
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="e.g. Aarav Sharma"
                    className="rounded-xl text-sm h-10"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1">
                    <label className="text-xs font-semibold text-muted-foreground">Phone Number (Optional)</label>
                    <Input
                      value={phone}
                      onChange={(e) => setPhone(e.target.value)}
                      placeholder="+91 98450 00000"
                      className="rounded-xl text-sm h-10"
                    />
                  </div>

                  <div className="space-y-1">
                    <label className="text-xs font-semibold text-muted-foreground">Locality / Area</label>
                    <Input
                      value={locality}
                      onChange={(e) => setLocality(e.target.value)}
                      placeholder="e.g. Mathikere, Bengaluru"
                      className="rounded-xl text-sm h-10"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1">
                    <label className="text-xs font-semibold text-muted-foreground">Building / Apartment</label>
                    <Input
                      value={building}
                      onChange={(e) => setBuilding(e.target.value)}
                      placeholder="e.g. Tower B, Gokula Apts"
                      className="rounded-xl text-sm h-10"
                    />
                  </div>

                  <div className="space-y-1">
                    <label className="text-xs font-semibold text-muted-foreground">Door / Unit #</label>
                    <Input
                      value={unit}
                      onChange={(e) => setUnit(e.target.value)}
                      placeholder="e.g. 304"
                      className="rounded-xl text-sm h-10"
                    />
                  </div>
                </div>

                <div className="space-y-1">
                  <label className="text-xs font-semibold text-muted-foreground">About You</label>
                  <Textarea
                    rows={2}
                    value={bio}
                    onChange={(e) => setBio(e.target.value)}
                    placeholder="A quick note about your studies, hobbies, or what you like to lend/borrow..."
                    className="rounded-xl text-xs resize-none"
                  />
                </div>

                {/* Location Privacy Checkbox */}
                <div className="p-3.5 rounded-2xl bg-muted/50 border border-border/50 flex items-start gap-3 text-xs">
                  <input
                    type="checkbox"
                    id="loc_consent"
                    checked={locationConsent}
                    onChange={(e) => setLocationConsent(e.target.checked)}
                    className="mt-0.5 rounded text-primary"
                  />
                  <label htmlFor="loc_consent" className="cursor-pointer space-y-0.5 text-muted-foreground">
                    <span className="font-semibold text-foreground block">
                      Enable Approximate Proximity Matching
                    </span>
                    <span>
                      NeighbourNode never exposes exact door numbers. Coordinates are used only for MongoDB 2dsphere radius calculations (e.g. within 2 km).
                    </span>
                  </label>
                </div>
              </div>
            )}

            {/* STEP 2: SKILLS OFFERED */}
            {step === 2 && (
              <div className="space-y-4">
                <p className="text-xs text-muted-foreground">
                  Select practical skills you are happy to teach, guide, or exchange with neighbours:
                </p>

                <div className="flex flex-wrap gap-2">
                  {AVAILABLE_SKILLS.map((skill) => {
                    const selected = selectedSkills.includes(skill);
                    return (
                      <button
                        type="button"
                        key={skill}
                        onClick={() => toggleSkill(skill)}
                        className={`text-xs px-3.5 py-1.5 rounded-full font-medium transition-all ${
                          selected
                            ? "bg-primary text-primary-foreground shadow-sm"
                            : "bg-muted/70 text-muted-foreground hover:bg-muted hover:text-foreground border border-border/50"
                        }`}
                      >
                        {selected ? "✓ " : "+ "}
                        {skill}
                      </button>
                    );
                  })}
                </div>

                {/* Add Custom Skill */}
                <div className="flex gap-2 pt-2">
                  <Input
                    value={customSkill}
                    onChange={(e) => setCustomSkill(e.target.value)}
                    placeholder="Add custom skill (e.g. Sourdough baking, Drone repair)"
                    className="rounded-xl text-xs h-9"
                    onKeyDown={(e) => e.key === "Enter" && addCustomSkill()}
                  />
                  <Button type="button" size="sm" variant="outline" onClick={addCustomSkill} className="h-9 text-xs">
                    Add
                  </Button>
                </div>
              </div>
            )}

            {/* STEP 3: INTERESTS & COMMUNITY PREFERENCES */}
            {step === 3 && (
              <div className="space-y-4">
                <p className="text-xs text-muted-foreground">
                  What activities or tools are you most interested in borrowing or collaborating on?
                </p>

                <div className="flex flex-wrap gap-2">
                  {AVAILABLE_INTERESTS.map((interest) => {
                    const selected = selectedInterests.includes(interest);
                    return (
                      <button
                        type="button"
                        key={interest}
                        onClick={() => toggleInterest(interest)}
                        className={`text-xs px-3.5 py-1.5 rounded-full font-medium transition-all ${
                          selected
                            ? "bg-primary text-primary-foreground shadow-sm"
                            : "bg-muted/70 text-muted-foreground hover:bg-muted hover:text-foreground border border-border/50"
                        }`}
                      >
                        {selected ? "✓ " : "+ "}
                        {interest}
                      </button>
                    );
                  })}
                </div>

                {/* Add Custom Interest */}
                <div className="flex gap-2 pt-2">
                  <Input
                    value={customInterest}
                    onChange={(e) => setCustomInterest(e.target.value)}
                    placeholder="Add custom interest (e.g. Drone racing, Astronomy)"
                    className="rounded-xl text-xs h-9"
                    onKeyDown={(e) => e.key === "Enter" && addCustomInterest()}
                  />
                  <Button type="button" size="sm" variant="outline" onClick={addCustomInterest} className="h-9 text-xs">
                    Add
                  </Button>
                </div>
              </div>
            )}
          </CardContent>

          <CardFooter className="flex justify-between px-6 sm:px-8 py-5 bg-muted/20 border-t border-border/40">
            {step > 1 ? (
              <Button variant="ghost" size="sm" onClick={() => setStep(step - 1)} className="text-xs gap-1">
                <ArrowLeft className="w-3.5 h-3.5" /> Back
              </Button>
            ) : (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => router.push("/dashboard")}
                className="text-xs text-muted-foreground"
              >
                Skip for now
              </Button>
            )}

            {step < 3 ? (
              <Button size="sm" onClick={() => setStep(step + 1)} className="text-xs gap-1 font-semibold">
                Continue <ArrowRight className="w-3.5 h-3.5" />
              </Button>
            ) : (
              <Button
                size="sm"
                disabled={saving}
                onClick={handleFinish}
                className="text-xs gap-1 font-semibold bg-primary text-primary-foreground shadow"
              >
                {saving ? "Saving..." : "Complete Setup"} <CheckCircle2 className="w-4 h-4 ml-1" />
              </Button>
            )}
          </CardFooter>
        </Card>
      </motion.div>
    </div>
  );
}
