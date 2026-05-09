"use client";

import React, { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button, buttonVariants } from "@/components/ui/button";
import { motion } from "framer-motion";
import { PackageSearch, PlusCircle, MoreHorizontal, Image as ImageIcon } from "lucide-react";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";
import Link from "next/link";
import { supabase } from "@/lib/supabase";
import { User } from "@supabase/supabase-js";

const FallbackImage = ({ src, alt }: { src?: string; alt: string }) => {
  const [error, setError] = useState(false);

  if (!src || error) {
    return (
      <div className="w-10 h-10 rounded-md bg-muted flex items-center justify-center flex-shrink-0">
        <ImageIcon className="w-5 h-5 text-muted-foreground" />
      </div>
    );
  }

  return (
    <img
      src={src}
      alt={alt}
      onError={() => setError(true)}
      className="w-10 h-10 rounded-md object-cover flex-shrink-0"
    />
  );
};

export default function Dashboard() {
  const [user, setUser] = useState<User | null>(null);
  const [isAddItemOpen, setIsAddItemOpen] = useState(false);
  const [adding, setAdding] = useState(false);
  const [listedItems, setListedItems] = useState<any[]>([]);
  const [borrowedItems, setBorrowedItems] = useState<any[]>([]);
  
  // Add Item Form State
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState("");

  React.useEffect(() => {
    supabase.auth.getUser().then(({ data }) => {
      setUser(data.user);
      if (data.user) {
        fetchDashboardData(data.user.id);
      }
    });
  }, []);

  const fetchDashboardData = async (userId: string) => {
    // Fetch listed items
    const { data: listed } = await supabase
      .from("items")
      .select("*")
      .eq("owner_id", userId);
    setListedItems(listed || []);

    // Fetch borrowed items
    const { data: borrowed } = await supabase
      .from("transactions")
      .select("*, items(title, image_url), owner:users!owner_id(full_name)")
      .eq("borrower_id", userId);
    setBorrowedItems(borrowed || []);
  };

  const handleAction = (actionName: string) => {
    toast(`Action triggered: ${actionName}`);
  };

  const handleAddItem = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return toast.error("Must be logged in.");
    
    setAdding(true);
    try {
      const res = await fetch("http://localhost:8000/api/items/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          owner_id: user.id,
          name: title, // Backend schemas might expect 'name' not 'title', let's use 'title' as per strict instruction
          // Actually user said items table uses "title", so I will pass "title"
          title: title,
          description,
          category,
          condition: "good",
          location_hint: "Building A",
          image_url: "",
          current_status: "available",
          is_active: true
        })
      });
      
      if (!res.ok) throw new Error("Failed to add item");
      toast.success("Item listed successfully!");
      setIsAddItemOpen(false);
      // reset form
      setTitle("");
      setDescription("");
      setCategory("");
      // Refresh list
      if (user) fetchDashboardData(user.id);
    } catch (err) {
      toast.error("Error listing item.");
    } finally {
      setAdding(false);
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="container mx-auto px-4 py-8 max-w-5xl"
    >
      <div className="mb-8 flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-4xl font-bold tracking-tight">My Dashboard</h1>
          <p className="text-muted-foreground mt-2">
            Manage your items and track your current borrowings.
          </p>
        </div>
        <Link href="/catalog" className={buttonVariants({ className: "gap-2" })}>
          <PackageSearch className="w-4 h-4" />
          Find New Items
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-card p-6 rounded-xl border shadow-sm flex flex-col justify-between">
          <div className="flex items-center gap-2 text-muted-foreground mb-2">
            <PackageSearch className="w-4 h-4" />
            <h3 className="font-medium text-sm">Active Borrows</h3>
          </div>
          <span className="text-3xl font-bold">{borrowedItems.length}</span>
        </div>
        
        <div className="bg-card p-6 rounded-xl border shadow-sm flex flex-col justify-between">
          <div className="flex items-center gap-2 text-muted-foreground mb-2">
            <PlusCircle className="w-4 h-4" />
            <h3 className="font-medium text-sm">Items Listed</h3>
          </div>
          <span className="text-3xl font-bold">{listedItems.length}</span>
        </div>

        <div className="bg-primary p-6 rounded-xl border shadow-sm text-primary-foreground flex flex-col justify-between">
          <div className="flex items-center gap-2 text-primary-foreground/80 mb-2">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            <h3 className="font-medium text-sm">Impact Score</h3>
          </div>
          <span className="text-3xl font-bold">142</span>
        </div>
      </div>

      <Tabs defaultValue="borrowed" className="w-full">
        <TabsList className="grid w-full grid-cols-2 max-w-[400px] mb-8">
          <TabsTrigger value="borrowed">My Borrowed Items</TabsTrigger>
          <TabsTrigger value="listed">My Listed Items</TabsTrigger>
        </TabsList>
        
        <TabsContent value="borrowed">
          {borrowedItems.length === 0 ? (
            <div className="flex flex-col items-center justify-center p-12 border rounded-xl bg-card text-center">
              <PackageSearch className="w-16 h-16 text-muted-foreground mb-4 opacity-50" />
              <h3 className="text-lg font-semibold">You haven&apos;t borrowed anything yet.</h3>
              <p className="text-muted-foreground mb-6">Discover useful items nearby to borrow from your neighbours.</p>
              <Link href="/" className={buttonVariants({ variant: "default" })}>Browse the Catalog</Link>
            </div>
          ) : (
            <div className="border rounded-md">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Item</TableHead>
                    <TableHead>Owner</TableHead>
                    <TableHead className="text-right">Status</TableHead>
                    <TableHead className="w-[50px]"></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {borrowedItems.map((tx) => (
                    <TableRow key={tx.id} className="hover:bg-muted/50 transition-colors">
                      <TableCell className="font-medium">
                        <div className="flex items-center gap-3">
                          <FallbackImage src={tx.items?.image_url} alt={tx.items?.title} />
                          {tx.items?.title || "Unknown Item"}
                        </div>
                      </TableCell>
                      <TableCell>{tx.owner?.full_name || "Unknown"}</TableCell>
                      <TableCell className="text-right">
                        <Badge variant="destructive" className="bg-orange-500 hover:bg-orange-600">
                          {tx.status}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <DropdownMenu>
                          <DropdownMenuTrigger className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground h-8 w-8 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring">
                            <MoreHorizontal className="w-4 h-4" />
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem onClick={() => handleAction("Message Owner")}>Message Owner</DropdownMenuItem>
                            <DropdownMenuItem onClick={() => handleAction("Request Extension")}>Request Extension</DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </TabsContent>
        
        <TabsContent value="listed">
          {listedItems.length === 0 ? (
            <div className="flex flex-col items-center justify-center p-12 border rounded-xl bg-card text-center">
              <PlusCircle className="w-16 h-16 text-muted-foreground mb-4 opacity-50" />
              <h3 className="text-lg font-semibold">You aren&apos;t sharing any items yet.</h3>
              <p className="text-muted-foreground mb-6">Earn trust in your community by listing items you rarely use.</p>
              
              <Button onClick={() => setIsAddItemOpen(true)}>List an Item</Button>
              
              <Dialog open={isAddItemOpen} onOpenChange={setIsAddItemOpen}>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>List a New Item</DialogTitle>
                    <DialogDescription>Share something with your neighbourhood. It will be available for others to borrow.</DialogDescription>
                  </DialogHeader>
                  <form onSubmit={handleAddItem} className="space-y-4 py-4">
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Title</label>
                      <Input value={title} onChange={e => setTitle(e.target.value)} placeholder="e.g. Cordless Power Drill" required />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Description</label>
                      <Textarea value={description} onChange={e => setDescription(e.target.value)} placeholder="Condition, accessories included, etc." />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Category</label>
                      <Input value={category} onChange={e => setCategory(e.target.value)} placeholder="e.g. Tools" />
                    </div>
                    <DialogFooter>
                      <Button type="submit" disabled={adding}>
                        {adding ? "Listing..." : "List Item"}
                      </Button>
                    </DialogFooter>
                  </form>
                </DialogContent>
              </Dialog>

            </div>
          ) : (
            <div className="border rounded-md">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Item</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="text-right">Borrower</TableHead>
                    <TableHead className="w-[50px]"></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {listedItems.map((item) => (
                    <TableRow key={item.id} className="hover:bg-muted/50 transition-colors">
                      <TableCell className="font-medium">
                        <div className="flex items-center gap-3">
                          <FallbackImage src={item.image_url} alt={item.title} />
                          {item.title}
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge 
                          variant={item.current_status === "available" ? "default" : "secondary"}
                          className={item.current_status === "available" ? "bg-green-500" : ""}
                        >
                          {item.current_status.charAt(0).toUpperCase() + item.current_status.slice(1)}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right text-muted-foreground">
                        {item.current_status === "available" ? "--" : "In Use"}
                      </TableCell>
                      <TableCell>
                        <DropdownMenu>
                          <DropdownMenuTrigger className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground h-8 w-8 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring">
                            <MoreHorizontal className="w-4 h-4" />
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem onClick={() => handleAction("Edit Listing")}>Edit Listing</DropdownMenuItem>
                            <DropdownMenuItem onClick={() => handleAction("Mark as Unavailable")}>Mark as Unavailable</DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </TabsContent>
      </Tabs>
    </motion.div>
  );
}
