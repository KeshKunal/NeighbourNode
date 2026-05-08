"use client";

import React from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { mockItems, mockUsers } from "@/lib/mockData";
import { motion } from "framer-motion";

export default function Dashboard() {
  // Let's assume the logged-in user is "Alice Smith" (id: "u1")
  const currentUser = mockUsers.find(u => u.id === "u1");
  
  // My Borrowed Items (mocking that we borrowed the Hiking Tent i3)
  const borrowedItems = [
    { ...mockItems.find(i => i.id === "i3")!, dueDate: "Due in 2 hours" }
  ];

  // My Listed Items (items where owner_id === "u1")
  const listedItems = mockItems.filter(i => i.owner_id === "u1");

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
          <div className="border rounded-md">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Item</TableHead>
                  <TableHead>Owner</TableHead>
                  <TableHead className="text-right">Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {borrowedItems.map((item) => (
                  <TableRow key={item.id}>
                    <TableCell className="font-medium">
                      <div className="flex items-center gap-3">
                        <img src={item.image_url} alt={item.name} className="w-10 h-10 rounded-md object-cover" />
                        {item.name}
                      </div>
                    </TableCell>
                    <TableCell>{mockUsers.find(u => u.id === item.owner_id)?.name}</TableCell>
                    <TableCell className="text-right">
                      <Badge variant="destructive" className="bg-orange-500 hover:bg-orange-600">
                        {item.dueDate}
                      </Badge>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </TabsContent>
        
        <TabsContent value="listed">
          <div className="border rounded-md">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Item</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Borrower</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {listedItems.map((item) => (
                  <TableRow key={item.id}>
                    <TableCell className="font-medium">
                      <div className="flex items-center gap-3">
                        <img src={item.image_url} alt={item.name} className="w-10 h-10 rounded-md object-cover" />
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
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </TabsContent>
      </Tabs>
    </motion.div>
  );
}
