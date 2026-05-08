"use client";

import * as React from "react";
import Link from "next/link";
import { useTheme } from "next-themes";
import { Moon, Sun, Home, LayoutDashboard, Search } from "lucide-react";

export function Navbar() {
  const { setTheme, theme } = useTheme();

  return (
    <nav className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <div className="flex items-center gap-6">
          <Link href="/" className="flex items-center space-x-2">
            <Home className="h-6 w-6 text-primary" />
            <span className="font-bold text-xl hidden sm:inline-block">NeighbourNode</span>
          </Link>
          <div className="hidden md:flex gap-6">
            <Link href="/" className="text-sm font-medium transition-colors hover:text-primary text-muted-foreground flex items-center gap-2">
              <Search className="h-4 w-4" /> Catalog
            </Link>
            <Link href="/dashboard" className="text-sm font-medium transition-colors hover:text-primary text-muted-foreground flex items-center gap-2">
              <LayoutDashboard className="h-4 w-4" /> My Dashboard
            </Link>
          </div>
        </div>
        
        <div className="flex flex-1 items-center justify-end space-x-4">
          <button
            onClick={() => setTheme(theme === "light" ? "dark" : "light")}
            className="inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 hover:bg-accent hover:text-accent-foreground h-10 w-10"
          >
            <Sun className="h-5 w-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
            <Moon className="absolute h-5 w-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
            <span className="sr-only">Toggle theme</span>
          </button>
        </div>
      </div>
    </nav>
  );
}
