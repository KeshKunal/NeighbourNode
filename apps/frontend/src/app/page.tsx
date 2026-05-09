"use client";

import React from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, PackageSearch, ShieldCheck, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";

const fadeIn = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.6 } }
};

const staggerContainer = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.2
    }
  }
};

export default function LandingPage() {
  return (
    <div className="flex-1 flex flex-col">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-background pt-24 pb-32">
        <div className="absolute inset-0 bg-grid-pattern opacity-5" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-primary/20 rounded-full blur-[120px] pointer-events-none" />
        
        <div className="container mx-auto px-4 relative z-10">
          <motion.div 
            initial="hidden" 
            animate="visible" 
            variants={staggerContainer}
            className="max-w-4xl mx-auto text-center"
          >
            <motion.div variants={fadeIn} className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary mb-8 text-sm font-medium">
              <Sparkles className="w-4 h-4" />
              <span>Hyper-local Sharing Economy</span>
            </motion.div>
            
            <motion.h1 variants={fadeIn} className="text-5xl md:text-7xl font-extrabold tracking-tight mb-8">
              Your neighbourhood is a <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-blue-500">library.</span>
            </motion.h1>
            
            <motion.p variants={fadeIn} className="text-xl text-muted-foreground mb-12 max-w-2xl mx-auto leading-relaxed">
              Borrow, lend, and share items in your community. Powered by AI workflows and instant Telegram notifications to make sharing frictionless.
            </motion.p>
            
            <motion.div variants={fadeIn} className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Button size="lg" className="w-full sm:w-auto text-lg h-14 px-8 rounded-full" asChild>
                <Link href="/auth/signup">
                  Get Started
                  <ArrowRight className="ml-2 w-5 h-5" />
                </Link>
              </Button>
              <Button size="lg" variant="outline" className="w-full sm:w-auto text-lg h-14 px-8 rounded-full" asChild>
                <Link href="/catalog">
                  Browse Catalog
                </Link>
              </Button>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 bg-muted/30">
        <div className="container mx-auto px-4">
          <motion.div 
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-100px" }}
            variants={staggerContainer}
            className="grid grid-cols-1 md:grid-cols-3 gap-8"
          >
            <motion.div variants={fadeIn} className="bg-card p-8 rounded-2xl border shadow-sm">
              <div className="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center mb-6">
                <PackageSearch className="w-6 h-6 text-primary" />
              </div>
              <h3 className="text-xl font-bold mb-3">AI Matchmaking</h3>
              <p className="text-muted-foreground">
                Just tell the AI what you need. It searches local inventory, finds the best match, and negotiates the borrow.
              </p>
            </motion.div>

            <motion.div variants={fadeIn} className="bg-card p-8 rounded-2xl border shadow-sm">
              <div className="w-12 h-12 bg-blue-500/10 rounded-xl flex items-center justify-center mb-6">
                <svg className="w-6 h-6 text-blue-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              </div>
              <h3 className="text-xl font-bold mb-3">Telegram Integrated</h3>
              <p className="text-muted-foreground">
                Never miss a request. Approve borrows and coordinate pickups instantly right from your Telegram app.
              </p>
            </motion.div>

            <motion.div variants={fadeIn} className="bg-card p-8 rounded-2xl border shadow-sm">
              <div className="w-12 h-12 bg-green-500/10 rounded-xl flex items-center justify-center mb-6">
                <ShieldCheck className="w-6 h-6 text-green-500" />
              </div>
              <h3 className="text-xl font-bold mb-3">Verified Neighbours</h3>
              <p className="text-muted-foreground">
                Build a trusted community. See apartment identifiers and trust ratings before handing over your items.
              </p>
            </motion.div>
          </motion.div>
        </div>
      </section>
    </div>
  );
}
