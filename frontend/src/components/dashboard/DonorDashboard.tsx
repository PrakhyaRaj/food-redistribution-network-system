import React, { useEffect, useState } from "react";
import { api, Food, Request as FoodRequest } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Package, Plus, Users, TrendingUp } from "lucide-react";
import { RouteOptimization } from "@/components/RouteOptimization";
import { Link } from "react-router-dom";
import FoodList from "@/components/food/FoodList";
import NearbyRequests from "@/components/food/NearbyRequests";
import { toast } from "sonner";
import { io, Socket } from "socket.io-client";
import { FoodImages } from "@/components/food/FoodImages";

// 👉 MongoDB Features (from A)
import { 
  ActivitiesFeed, 
  AnalyticsDashboard,
  RouteOptimizer 
} from "@/components/mongodb";

import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";

interface DonorDashboardProps {
  userId: string;
}

const DonorDashboard = ({ userId }: DonorDashboardProps) => {
  /* --------------------------------------------------------------------------
   * SECTION 1 — DATA LOADING (from B)
   * -------------------------------------------------------------------------- */
  const [foods, setFoods] = useState<Food[]>([]);
  const [requests, setRequests] = useState<FoodRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [isTokenReady, setIsTokenReady] = useState(false);
  const [socket, setSocket] = useState<Socket | null>(null);
  const [latestTransaction, setLatestTransaction] = useState<any | null>(null);
  const [selectedFoodId, setSelectedFoodId] = useState<number | null>(null);

  const loadData = async () => {
    try {
      setLoading(true);
      console.log("DonorDashboard: loadData starting...");

      const [foodsData, requestsData] = await Promise.all([
        api.food.getMyFoods(parseInt(userId)),
        api.food.getNearbyRequests(),
      ]);

      const mappedFoods = Array.isArray(foodsData) ? foodsData : foodsData.foods || [];
      const mappedRequests = Array.isArray(requestsData) ? requestsData : requestsData.requests || [];
      console.log("DonorDashboard: loadData got", { foods: mappedFoods.length, requests: mappedRequests.length });
      setFoods(mappedFoods);
      setRequests(mappedRequests);
      if (mappedFoods.length > 0 && selectedFoodId === null) {
        setSelectedFoodId(mappedFoods[0].id);
      }

      // Load latest transaction for route display
      try {
        const txns = await api.transactions.getUserTransactions(parseInt(userId));
        const arr = Array.isArray(txns) ? txns : [];
        const mine = arr
          .filter((t: any) => t.donor_id === parseInt(userId))
          .sort((a: any, b: any) => new Date(b.date || b.created_at).getTime() - new Date(a.date || a.created_at).getTime());
        if (mine.length > 0) setLatestTransaction(mine[0]);
      } catch (e) {
        console.log("No transactions found for donor");
      }
    } catch (error) {
      toast.error("Failed to load data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (foods.length === 0) {
      if (selectedFoodId !== null) setSelectedFoodId(null);
      return;
    }

    const exists = foods.some((food) => food.id === selectedFoodId);
    if (!exists) {
      setSelectedFoodId(foods[0].id);
    }
  }, [foods, selectedFoodId]);

  // Wait until token becomes available
  useEffect(() => {
    const checkToken = () => {
      const token = localStorage.getItem("token");
      if (token) setIsTokenReady(true);
      else setTimeout(checkToken, 100);
    };
    checkToken();
  }, []);

  useEffect(() => {
    if (isTokenReady && userId) {
      loadData();
      
      // Connect to Socket.IO for real-time updates
      const token = localStorage.getItem("token");
      const newSocket = io("http://127.0.0.1:5000", {
        // Force polling transport to avoid WebSocket frame/upgrade errors in dev
        transports: ["polling"],
        withCredentials: true,
        // Send token via query string (most reliable)
        query: { token },
        // Also send via auth object as fallback
        auth: { token },
        reconnection: true,
        reconnectionAttempts: 5,
      });

      newSocket.on("connect", () => {
        console.log("✅ DonorDashboard connected to Socket.IO");
      });

      // When a match is found, refresh food list to show updated status
      newSocket.on("match_found", (data: any) => {
        console.log("📦 Match found, refreshing food list...", data);
        setTimeout(() => {
          loadData();
        }, 1000);
      });
      newSocket.on("transaction_created", (data: any) => {
        console.log("💰 Transaction created (socket event)", data);
        setTimeout(() => {
          loadData();
        }, 1000);
      });

      newSocket.on("transaction_created", (data: any) => {
        console.log("💰 Transaction created, refreshing data...", data);
        setTimeout(() => {
          loadData();
        }, 1000);
      });

      newSocket.on("transaction_updated", (data: any) => {
        console.log("💰 Transaction updated, refreshing data...", data);
        setTimeout(() => {
          loadData();
        }, 1000);
      });

      newSocket.on("food_added", (data: any) => {
        console.log("🍲 Food added, refreshing data...", data);
        setTimeout(() => {
          loadData();
        }, 1000);
      });

      newSocket.on("food_updated", (data: any) => {
        console.log("🍲 Food updated, refreshing data...", data);
        setTimeout(() => {
          loadData();
        }, 1000);
      });

      newSocket.on("request_created", (data: any) => {
        console.log("📋 Request created, refreshing data...", data);
        setTimeout(() => {
          loadData();
        }, 1000);
      });

      newSocket.on("notification", (data: any) => {
        if (data.type === "match_found" || data.type === "food_accepted") {
          console.log("📦 Notification: Food status changed", data);
          setTimeout(() => {
            loadData();
          }, 1000);
        }
      });

      setSocket(newSocket);

      return () => {
        if (newSocket) {
          newSocket.disconnect();
        }
      };
    }
  }, [isTokenReady, userId]);

  /* --------------------------------------------------------------------------
   * SECTION 2 — STAT CARDS (from B)
   * -------------------------------------------------------------------------- */
  const stats = [
    {
      title: "Active Donations",
      value: foods.filter((f) => f.status === "available").length,
      icon: Package,
      color: "text-primary",
    },
    {
      title: "Nearby Requests",
      value: requests.length,
      icon: Users,
      color: "text-secondary",
    },
    {
      title: "Total Donated",
      value: foods.length,
      icon: TrendingUp,
      color: "text-success",
    },
  ];

  if (loading && foods.length === 0 && requests.length === 0) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-lg">Loading dashboard...</div>
      </div>
    );
  }

  /* --------------------------------------------------------------------------
   * SECTION 3 — FINAL RENDER (A + B merged)
   * -------------------------------------------------------------------------- */
  return (
    <div className="space-y-10">

      {/* ----------------------------- 1. STATS ----------------------------- */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {stats.map((stat) => (
          <Card key={stat.title}>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {stat.title}
              </CardTitle>
              <stat.icon className={`h-5 w-5 ${stat.color}`} />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{stat.value}</div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* -------------------------- 2. QUICK ACTIONS -------------------------- */}
      <Card className="bg-gradient-to-r from-[#225266] to-[#b7e255] border border-[#225266]/20 p-4">
        <CardHeader>
          <CardTitle className="text-white">Quick Actions</CardTitle>
          <CardDescription className="text-white">Manage your food donations</CardDescription>
        </CardHeader>

        <CardContent className="flex gap-4 flex-wrap">
          <Button asChild>
            <Link to="/food/add">
              <Plus className="h-4 w-4 mr-2" />
              Add Food
            </Link>
          </Button>

          <Button variant="outline" asChild>
            <Link to="/food/my">
              <Package className="h-4 w-4 mr-2" />
              My Foods
            </Link>
          </Button>

          <Button variant="outline" asChild>
            <Link to="/transactions">
              <TrendingUp className="h-4 w-4 mr-2" />
              Transactions
            </Link>
          </Button>
        </CardContent>
      </Card>

      {/* ---------------------- 3. RECENT FOODS SECTION ---------------------- */}
      <div>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold">Your Recent Food Items</h2>
          <Button variant="outline" size="sm" asChild>
            <Link to="/food/my">View All</Link>
          </Button>
        </div>
        <FoodList foods={foods.slice(0, 2)} onUpdate={loadData} />
      </div>

      {/* ---------------------- 4. NEARBY REQUESTS SECTION ---------------------- */}
      <div>
        <h2 className="text-2xl font-bold mb-4">Nearby Food Requests</h2>
        <NearbyRequests requests={requests.slice(0, 4)} onMatch={loadData} />
      </div>

      {/* ---------------------- 5. ROUTE OPTIMIZATION SECTION ---------------------- */}
      {latestTransaction && (
        <div>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold">Latest Delivery Route</h2>
            <Button variant="outline" size="sm" asChild>
              <Link to="/transactions">View All</Link>
            </Button>
          </div>
          <RouteOptimization
            transactionId={latestTransaction.txn_id}
            donorId={latestTransaction.donor_id}
            receiverId={latestTransaction.receiver_id}
            showFull={true}
          />
        </div>
      )}

      {/* ----------------------------------------------------------------------
       * 6. MONGODB FEATURES (from A)
       * ---------------------------------------------------------------------- */}
      <div className="border-t pt-10">
        <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
          <span className="text-blue-600 text-3xl">📊</span>
          MongoDB Features
        </h2>

        <Tabs defaultValue="overview">
          <TabsList className="grid grid-cols-2 max-w-md">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="media">Food Media</TabsTrigger>
          </TabsList>

          {/* Overview */}
          <TabsContent value="overview" className="space-y-4 py-4">
            <ActivitiesFeed />
          </TabsContent>

          {/* Media */}
          <TabsContent value="media" className="py-4">
            <div className="space-y-4">
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <h3 className="text-lg font-semibold">Food Images Management</h3>
                  <p className="text-gray-500">Upload and manage images for your donated food items.</p>
                </div>
                {foods.length > 0 && (
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-gray-600">Food Item</span>
                    <select
                      className="border rounded-md px-3 py-2 text-sm"
                      value={selectedFoodId ?? ""}
                      onChange={(e) => setSelectedFoodId(Number(e.target.value))}
                    >
                      {foods.map((food) => (
                        <option key={food.id} value={food.id}>
                          {food.food_name} · qty {food.quantity}
                        </option>
                      ))}
                    </select>
                  </div>
                )}
              </div>

              {foods.length === 0 && (
                <Card>
                  <CardContent className="py-6 text-gray-600">Add a food item first to upload images.</CardContent>
                </Card>
              )}

              {selectedFoodId !== null && foods.length > 0 && (
                <FoodImages foodId={selectedFoodId} />
              )}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default DonorDashboard;
