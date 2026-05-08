"use client";

import React, { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button, buttonVariants } from "@/components/ui/button";
import { mockItems, mockUsers } from "@/lib/mockData";
import { motion } from "framer-motion";
import { PackageSearch, PlusCircle, MoreHorizontal, Image as ImageIcon } from "lucide-react";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { toast } from "sonner";
import Link from "next/link";

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
  
  const borrowedItems = [
    { ...mockItems.find(i => i.id === "i3")!, dueDate: "Due in 2 hours" }
  ];

  const listedItems = mockItems.filter(i => i.owner_id === "u1");

  const handleAction = (actionName: string) => {
    toast(`Action triggered: ${actionName}`);
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="container mx-auto px-4 py-8 max-w-5xl"
    >
      <div className="mb-8">
        <h1 className="text-4xl font-bold tracking-tight">My Dashboard</h1>
        <p className="text-muted-foreground mt-2">
          Manage your items and track your current borrowings.
        </p>
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
                  {borrowedItems.map((item) => (
                    <TableRow key={item.id} className="hover:bg-muted/50 transition-colors">
                      <TableCell className="font-medium">
                        <div className="flex items-center gap-3">
                          <FallbackImage src={item.image_url} alt={item.name} />
                          {item.name}
                        </div>
                      </TableCell>
                      <TableCell>{mockUsers.find(u => u.id === item.owner_id)?.name}</TableCell>
                      <TableCell className="text-right">
                        <Badge variant="destructive" className="bg-orange-500 hover:bg-orange-600">
                          {item.dueDate}
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
              <Button onClick={() => handleAction("Open List Item Modal")}>
                List an Item
              </Button>
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
                          <FallbackImage src={item.image_url} alt={item.name} />
                          {item.name}
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge 
                          variant={item.status === "available" ? "default" : "secondary"}
                          className={item.status === "available" ? "bg-green-500" : ""}
                        >
                          {item.status.charAt(0).toUpperCase() + item.status.slice(1)}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right text-muted-foreground">
                        {item.status === "available" ? "--" : "Charlie Davis (Apt 304)"}
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
