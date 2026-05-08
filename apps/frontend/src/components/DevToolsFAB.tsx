"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { Settings2, Zap, X } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export function DevToolsFAB() {
  const [isOpen, setIsOpen] = useState(false);

  const simulateWebhook = (type: "approved" | "warden") => {
    if (type === "approved") {
      toast("🎉 Request Approved!", {
        description: "Alice Smith has approved your request for the Bosch Power Drill.",
        action: {
          label: "View",
          onClick: () => console.log("View clicked"),
        },
      });
    } else if (type === "warden") {
      toast.error("⚠️ AI Warden Alert", {
        description: "Please return the Arduino Starter Kit in 1 hour.",
      });
    }
    setIsOpen(false);
  };

  return (
    <div className="fixed bottom-6 left-6 z-50 flex flex-col-reverse items-start gap-4">
      <Button
        onClick={() => setIsOpen(!isOpen)}
        size="icon"
        variant="default"
        className="rounded-full w-12 h-12 shadow-lg hover:shadow-xl transition-all"
      >
        {isOpen ? <X className="w-5 h-5" /> : <Settings2 className="w-5 h-5" />}
      </Button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 10, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 10, scale: 0.9 }}
            className="flex flex-col gap-2 bg-background/95 backdrop-blur border rounded-lg p-2 shadow-lg"
          >
            <div className="text-xs font-bold text-muted-foreground uppercase px-2 py-1">
              Simulate Webhook
            </div>
            <Button
              variant="ghost"
              size="sm"
              className="justify-start text-xs"
              onClick={() => simulateWebhook("approved")}
            >
              <Zap className="w-3 h-3 mr-2 text-green-500" />
              Owner Approved
            </Button>
            <Button
              variant="ghost"
              size="sm"
              className="justify-start text-xs"
              onClick={() => simulateWebhook("warden")}
            >
              <Zap className="w-3 h-3 mr-2 text-yellow-500" />
              AI Warden Alert
            </Button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
