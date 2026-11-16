"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useTheme } from "next-themes";
import {
  Home,
  LayoutDashboard,
  Search,
  User as UserIcon,
  LogOut,
  Sparkles,
  BookOpen,
  Users,
  Bell,
  Moon,
  Sun,
  PlusCircle,
} from "lucide-react";
import { Button, buttonVariants } from "@/components/ui/button";
import { useAuth } from "@/lib/authContext";
import { notificationsApi } from "@/lib/api";

export function Navbar() {
  const { setTheme, theme } = useTheme();
  const pathname = usePathname();
  const { user, isLoading, logout } = useAuth();
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    if (!user) {
      setUnreadCount(0);
      return;
    }
    const loadUnread = async () => {
      try {
        const notes = await notificationsApi.list();
        setUnreadCount(notes.filter((n) => !n.is_read).length);
      } catch {
        // Silently ignore background polling error
      }
    };
    loadUnread();
    const interval = setInterval(loadUnread, 30000);
    return () => clearInterval(interval);
  }, [user]);

  const NavLink = ({
    href,
    icon: Icon,
    children,
  }: {
    href: string;
    icon: any;
    children: React.ReactNode;
  }) => {
    const isActive = pathname === href;
    return (
      <Link
        href={href}
        className={`text-sm font-medium transition-colors flex items-center gap-2 px-3 py-1.5 rounded-lg ${
          isActive
            ? "bg-primary/10 text-primary font-semibold"
            : "text-muted-foreground hover:text-foreground hover:bg-muted/50"
        }`}
      >
        <Icon className="h-4 w-4" /> {children}
      </Link>
    );
  };

  return (
    <nav className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <div className="flex items-center gap-6">
          <Link href="/" className="flex items-center space-x-2.5 group">
            <div className="w-9 h-9 rounded-xl bg-primary/10 border border-primary/20 flex items-center justify-center text-primary group-hover:bg-primary group-hover:text-primary-foreground transition-all">
              <Sparkles className="h-5 w-5" />
            </div>
            <div className="flex flex-col">
              <span className="font-bold text-lg leading-tight tracking-tight">NeighbourNode</span>
              <span className="text-[10px] text-muted-foreground font-medium hidden sm:inline">
                Smart Community Sharing
              </span>
            </div>
          </Link>

          <div className="hidden md:flex gap-1 items-center">
            <NavLink href="/catalog" icon={Search}>
              Resources
            </NavLink>
            <NavLink href="/skills" icon={BookOpen}>
              Skills
            </NavLink>
            <NavLink href="/community" icon={Users}>
              Community
            </NavLink>
            {user && (
              <NavLink href="/dashboard" icon={LayoutDashboard}>
                Dashboard
              </NavLink>
            )}
          </div>
        </div>

        <div className="flex items-center space-x-3">
          {user ? (
            <div className="flex items-center gap-2">
              <Link
                href="/resources/new"
                className={buttonVariants({
                  size: "sm",
                  className: "hidden sm:inline-flex rounded-full gap-1.5",
                })}
              >
                <PlusCircle className="w-4 h-4" />
                <span>Add Listing</span>
              </Link>

              {/* Notification icon */}
              <Link
                href="/notifications"
                className="relative p-2 rounded-full hover:bg-muted text-muted-foreground hover:text-foreground transition-colors"
                title="Notifications"
              >
                <Bell className="w-5 h-5" />
                {unreadCount > 0 && (
                  <span className="absolute top-1 right-1 w-4 h-4 bg-primary text-primary-foreground text-[10px] font-bold rounded-full flex items-center justify-center">
                    {unreadCount > 9 ? "9+" : unreadCount}
                  </span>
                )}
              </Link>

              {/* User profile button */}
              <Link
                href="/profile"
                className="flex items-center gap-2 px-2.5 py-1.5 rounded-full hover:bg-muted transition-colors border border-border/40"
              >
                <div className="w-7 h-7 rounded-full bg-primary/10 flex items-center justify-center text-primary font-semibold text-xs overflow-hidden">
                  {user.avatar_url ? (
                    <img src={user.avatar_url} alt={user.full_name} className="w-full h-full object-cover" />
                  ) : (
                    user.full_name?.charAt(0) || "U"
                  )}
                </div>
                <span className="text-xs font-medium max-w-[100px] truncate hidden sm:inline">
                  {user.full_name?.split(" ")[0]}
                </span>
              </Link>

              <Button
                variant="ghost"
                size="sm"
                onClick={logout}
                className="text-muted-foreground hover:text-destructive h-9 px-2.5"
                title="Sign Out"
              >
                <LogOut className="h-4 w-4" />
              </Button>
            </div>
          ) : !isLoading ? (
            <div className="flex items-center gap-2">
              <Link
                href="/auth/signin"
                className={buttonVariants({ variant: "ghost", size: "sm" })}
              >
                Sign In
              </Link>
              <Link
                href="/auth/signup"
                className={buttonVariants({ size: "sm", className: "rounded-full" })}
              >
                Sign Up
              </Link>
            </div>
          ) : null}

          <button
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
            className="inline-flex items-center justify-center rounded-full text-muted-foreground hover:text-foreground hover:bg-muted h-9 w-9 transition-colors"
            aria-label="Toggle theme"
          >
            <Sun className="h-4 w-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
            <Moon className="absolute h-4 w-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
          </button>
        </div>
      </div>
    </nav>
  );
}
