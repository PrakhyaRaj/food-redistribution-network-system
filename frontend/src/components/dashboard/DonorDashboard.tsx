import React, { useEffect, useState } from "react";
import { api, Food, Request as FoodRequest } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Package, Plus, Users, TrendingUp } from "lucide-react";
import { Link } from "react-router-dom";
import FoodList from "@/components/food/FoodList";
import NearbyRequests from "@/components/food/NearbyRequests";
import { toast } from "sonner";

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

  const loadData = async () => {
    try {
      setLoading(true);

      const [foodsData, requestsData] = await Promise.all([
        api.food.getMyFoods(parseInt(userId)),
        api.food.getNearbyRequests(),
      ]);

      setFoods(Array.isArray(foodsData) ? foodsData : foodsData.foods || []);
      setRequests(Array.isArray(requestsData) ? requestsData : requestsData.requests || []);
    } catch (error) {
      toast.error("Failed to load data");
    } finally {
      setLoading(false);
    }
  };

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
    if (isTokenReady && userId) loadData();
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

      {/* ----------------------------------------------------------------------
       * 5. MONGODB FEATURES (from A)
       * ---------------------------------------------------------------------- */}
      <div className="border-t pt-10">
        <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
          <span className="text-blue-600 text-3xl">📊</span>
          MongoDB Features
        </h2>

        <Tabs defaultValue="overview">
          <TabsList className="grid grid-cols-3 max-w-md">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
            <TabsTrigger value="media">Food Media</TabsTrigger>
          </TabsList>

          {/* Overview */}
          <TabsContent value="overview" className="space-y-4 py-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <ActivitiesFeed />
              <RouteOptimizer />
            </div>
          </TabsContent>

          {/* Analytics */}
          <TabsContent value="analytics" className="py-4">
            <AnalyticsDashboard />
          </TabsContent>

          {/* Media */}
          <TabsContent value="media" className="py-4">
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">Food Images Management</h3>
              <p className="text-gray-500">
                Select a food item from "My Foods" to manage images.
              </p>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default DonorDashboard;
