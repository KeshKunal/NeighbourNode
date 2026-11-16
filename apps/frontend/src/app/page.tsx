"use client";

import React from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  ArrowRight,
  PackageSearch,
  ShieldCheck,
  Sparkles,
  MapPin,
  BookOpen,
  Users,
  Repeat,
  HeartHandshake,
  CheckCircle2,
  Clock,
  Compass,
} from "lucide-react";
import { buttonVariants } from "@/components/ui/button";

const fadeIn = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5 } },
};

const staggerContainer = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.15 },
  },
};

export default function LandingPage() {
  return (
    <div className="flex-1 flex flex-col">
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-20 pb-28 md:pt-28 md:pb-36 bg-gradient-to-b from-background via-muted/20 to-background border-b border-border/40">
        <div className="container mx-auto px-4 relative z-10">
          <motion.div
            initial="hidden"
            animate="visible"
            variants={staggerContainer}
            className="max-w-4xl mx-auto text-center"
          >
            <motion.div
              variants={fadeIn}
              className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-primary/10 border border-primary/20 text-primary mb-6 text-xs font-semibold tracking-wide"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>MongoDB NoSQL Community Resource & Skill Platform</span>
            </motion.div>

            <motion.h1
              variants={fadeIn}
              className="text-4xl sm:text-6xl md:text-7xl font-extrabold tracking-tight mb-6 leading-[1.1]"
            >
              Your neighbourhood is a{" "}
              <span className="text-primary underline decoration-primary/30 underline-offset-8">
                living library.
              </span>
            </motion.h1>

            <motion.p
              variants={fadeIn}
              className="text-lg sm:text-xl text-muted-foreground mb-10 max-w-2xl mx-auto leading-relaxed font-normal"
            >
              Borrow tools, textbooks, camping gear, and appliances from trusted neighbours.
              Exchange skills, learn together, and build community trust with transparent reputation scores.
            </motion.p>

            <motion.div
              variants={fadeIn}
              className="flex flex-col sm:flex-row items-center justify-center gap-3.5"
            >
              <Link
                href="/catalog"
                className={buttonVariants({
                  size: "lg",
                  className: "w-full sm:w-auto text-base h-13 px-8 rounded-full font-semibold shadow-lg shadow-primary/20",
                })}
              >
                Browse Resources
                <ArrowRight className="ml-2 w-4 h-4" />
              </Link>
              <Link
                href="/skills"
                className={buttonVariants({
                  size: "lg",
                  variant: "outline",
                  className: "w-full sm:w-auto text-base h-13 px-8 rounded-full font-semibold border-border/80",
                })}
              >
                Explore Skills
              </Link>
              <Link
                href="/auth/signup"
                className={buttonVariants({
                  size: "lg",
                  variant: "secondary",
                  className: "w-full sm:w-auto text-base h-13 px-7 rounded-full font-medium",
                })}
              >
                Join Community
              </Link>
            </motion.div>

            {/* Quick Stats Banner */}
            <motion.div
              variants={fadeIn}
              className="mt-14 grid grid-cols-2 md:grid-cols-4 gap-4 p-5 rounded-2xl bg-card/80 backdrop-blur border border-border/60 shadow-sm max-w-3xl mx-auto text-left"
            >
              <div>
                <div className="text-2xl font-bold text-foreground">25+</div>
                <div className="text-xs text-muted-foreground">Community Tools & Kits</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-foreground">16+</div>
                <div className="text-xs text-muted-foreground">Skills Offered</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-foreground">2dsphere</div>
                <div className="text-xs text-muted-foreground">MongoDB Geo-Proximity</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-emerald-600">4.9/5</div>
                <div className="text-xs text-muted-foreground">Verified Trust Score</div>
              </div>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-24 bg-muted/20 border-b border-border/40">
        <div className="container mx-auto px-4 max-w-5xl">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="text-3xl font-bold tracking-tight">How NeighbourNode Works</h2>
            <p className="text-muted-foreground mt-2 text-sm">
              Frictionless borrowing, verified accountability, and community skill exchange.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-card p-7 rounded-2xl border border-border/60 space-y-4 shadow-sm">
              <div className="w-11 h-11 bg-primary/10 rounded-xl flex items-center justify-center text-primary font-bold">
                1
              </div>
              <h3 className="text-lg font-bold">Discover Nearby</h3>
              <p className="text-xs text-muted-foreground leading-relaxed">
                Use the interactive map or AI Matchmaker to discover tools, equipment, textbooks, and skills located within your apartment complex or locality.
              </p>
            </div>

            <div className="bg-card p-7 rounded-2xl border border-border/60 space-y-4 shadow-sm">
              <div className="w-11 h-11 bg-primary/10 rounded-xl flex items-center justify-center text-primary font-bold">
                2
              </div>
              <h3 className="text-lg font-bold">Request & Coordinate</h3>
              <p className="text-xs text-muted-foreground leading-relaxed">
                Submit a borrow or skill request with your preferred dates. Owners receive instant in-app alerts and optional Telegram notifications to approve.
              </p>
            </div>

            <div className="bg-card p-7 rounded-2xl border border-border/60 space-y-4 shadow-sm">
              <div className="w-11 h-11 bg-primary/10 rounded-xl flex items-center justify-center text-primary font-bold">
                3
              </div>
              <h3 className="text-lg font-bold">Borrow & Build Trust</h3>
              <p className="text-xs text-muted-foreground leading-relaxed">
                Pick up the item, complete the exchange, and return it safely. Both neighbours exchange reviews to build an authentic reputation score.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Core Platform Capabilities */}
      <section className="py-24">
        <div className="container mx-auto px-4 max-w-6xl">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="text-3xl font-bold tracking-tight">Dual Physical & Skill Sharing</h2>
            <p className="text-muted-foreground mt-2 text-sm">
              NeighbourNode combines physical resource libraries with peer-to-peer knowledge sharing into one platform.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Physical Sharing Card */}
            <div className="p-8 rounded-3xl bg-card border border-border/70 space-y-6 shadow-sm flex flex-col justify-between">
              <div className="space-y-4">
                <div className="w-12 h-12 bg-emerald-500/10 text-emerald-600 rounded-2xl flex items-center justify-center">
                  <PackageSearch className="w-6 h-6" />
                </div>
                <h3 className="text-2xl font-bold">Physical Resource Library</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  Avoid buying expensive single-use items. Borrow drills, projectors, camping gear, ladders, oscilloscopes, and textbooks right from neighbours down the street.
                </p>
                <ul className="space-y-2 text-xs text-muted-foreground pt-2">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                    <span>Atomic reservation concurrency prevents double bookings</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                    <span>MongoDB 2dsphere index for radius-based proximity sorting</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                    <span>Warden background checker monitors return dates automatically</span>
                  </li>
                </ul>
              </div>

              <Link
                href="/catalog"
                className={buttonVariants({ variant: "outline", className: "w-full rounded-xl mt-4" })}
              >
                Explore Physical Catalog
              </Link>
            </div>

            {/* Skill Sharing Card */}
            <div className="p-8 rounded-3xl bg-card border border-border/70 space-y-6 shadow-sm flex flex-col justify-between">
              <div className="space-y-4">
                <div className="w-12 h-12 bg-blue-500/10 text-blue-600 rounded-2xl flex items-center justify-center">
                  <HeartHandshake className="w-6 h-6" />
                </div>
                <h3 className="text-2xl font-bold">Skill & Service Marketplace</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  Offer what you know and learn what you need. From Python coding, Calculus tutoring, and guitar lessons to cycle repair and balcony gardening.
                </p>
                <ul className="space-y-2 text-xs text-muted-foreground pt-2">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-blue-600 flex-shrink-0" />
                    <span>Free community barter & skill swapping with zero payment friction</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-blue-600 flex-shrink-0" />
                    <span>First-class session scheduling and completion tracking</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-blue-600 flex-shrink-0" />
                    <span>Peer reviews and reputation boosts for each completed exchange</span>
                  </li>
                </ul>
              </div>

              <Link
                href="/skills"
                className={buttonVariants({ variant: "outline", className: "w-full rounded-xl mt-4" })}
              >
                Explore Skills Marketplace
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Trust & Reputation Section */}
      <section className="py-20 bg-muted/20 border-y border-border/40">
        <div className="container mx-auto px-4 max-w-4xl text-center space-y-6">
          <div className="w-12 h-12 bg-amber-500/10 text-amber-600 rounded-2xl flex items-center justify-center mx-auto">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <h2 className="text-3xl font-bold tracking-tight">Transparent Reputation Engine</h2>
          <p className="text-muted-foreground text-sm max-w-2xl mx-auto leading-relaxed">
            Every user's reputation score is computed deterministically from verified reviews, completed exchanges, and on-time return rates. No black-box algorithms or pay-to-win mechanics.
          </p>
          <div className="pt-2">
            <Link href="/auth/signup" className={buttonVariants({ size: "lg", className: "rounded-full px-8" })}>
              Create Your Community Profile
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 bg-card border-t border-border/40 text-xs text-muted-foreground">
        <div className="container mx-auto px-4 max-w-6xl flex flex-col md:flex-row items-center justify-between gap-6 text-center md:text-left">
          <div className="space-y-1">
            <div className="font-bold text-foreground text-sm">NeighbourNode</div>
            <p>Smart Community Resource & Skill Sharing Platform</p>
            <p className="text-[11px] text-muted-foreground/80">
              Academic Course: <strong>CSAEC59 — AEC-NoSQL</strong> • Ramaiah Institute of Technology, Bengaluru
            </p>
          </div>
          <div className="flex flex-wrap justify-center gap-6 font-medium">
            <Link href="/catalog" className="hover:text-primary">
              Catalogue
            </Link>
            <Link href="/skills" className="hover:text-primary">
              Skills
            </Link>
            <Link href="/community" className="hover:text-primary">
              Community
            </Link>
            <Link href="/dashboard" className="hover:text-primary">
              Dashboard
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
