import { useState, useEffect } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { useNavigate } from "react-router-dom";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis,
  CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area, RadarChart, 
  PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ComposedChart
} from "recharts";
import {
  Users, Package, ShoppingCart, TrendingUp, LogOut, BarChart3,
  PieChart as PieChartIcon, ChevronLeft, ChevronRight, Trash2, Edit, Shield, RefreshCw,
  Activity, Clock, MapPin, Star
} from "lucide-react";
import { api } from "@/lib/api";
import { toast } from "sonner";
import { io, Socket } from 'socket.io-client';

const AdminDashboard = () => {
  const { roles, logout } = useAuth();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState("overview");
  const [isLoading, setIsLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [users, setUsers] = useState<any[]>([]);
  const [foods, setFoods] = useState<any[]>([]);
  const [requests, setRequests] = useState<any[]>([]);
  const [transactions, setTransactions] = useState<any[]>([]);
  const [statistics, setStatistics] = useState<any>(null);
  const [activityData, setActivityData] = useState<any>(null);
  const [systemHealth, setSystemHealth] = useState<any>(null);
  const [currentPage, setCurrentPage] = useState({ users: 1, foods: 1, requests: 1, transactions: 1 });
  const [socket, setSocket] = useState<Socket | null>(null);
  const [realtimeStats, setRealtimeStats] = useState<any>(null);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  useEffect(() => {
    if (!roles.includes("admin")) {
      toast.error("Admin access required");
      navigate("/dashboard");
    }
  }, [roles, navigate]);

  // Real-time Socket.IO connection for admin
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token || !roles.includes("admin")) return;

    const newSocket = io('http://127.0.0.1:5000', {
      transports: ['polling'],
      withCredentials: true,
      query: { token },
      auth: { token },
    });

    newSocket.on('connect', () => {
      console.log('Admin socket connected');
      newSocket.emit('join_room', { room: 'admin_dashboard' });
    });

    // Listen for real-time updates
    newSocket.on('transaction_created', () => {
      console.log('Real-time: Transaction created');
      setLastUpdate(new Date());
      fetchDashboardData();
      if (activeTab === 'analytics') {
        fetchActivity();
        fetchStatistics();
      }
    });

    newSocket.on('transaction_updated', () => {
      console.log('Real-time: Transaction updated');
      setLastUpdate(new Date());
      fetchDashboardData();
    });

    newSocket.on('food_added', () => {
      console.log('Real-time: Food added');
      setLastUpdate(new Date());
      fetchDashboardData();
    });

    newSocket.on('analytics_updated', (data) => {
      console.log('Real-time: Analytics updated', data);
      setRealtimeStats(data);
      setLastUpdate(new Date());
    });

    setSocket(newSocket);

    return () => {
      newSocket.disconnect();
    };
  }, [roles, activeTab]);

  const fetchDashboardData = async () => {
    setIsLoading(true);
    try {
      const response = await api.get("/api/admin/dashboard/summary");
      if (response.success) setDashboardData(response.summary);
    } catch (error) {
      console.error("Error fetching dashboard data:", error);
    }
    setIsLoading(false);
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchUsers = async (page = 1) => {
    try {
      const response = await api.get(`/api/admin/users?page=${page}&per_page=10`);
      if (response.success) {
        setUsers(response.users);
        setCurrentPage((p) => ({ ...p, users: page }));
      }
    } catch (error) {
      console.error("Error fetching users:", error);
      toast.error("Failed to fetch users");
    }
  };

  const fetchFoods = async (page = 1) => {
    try {
      const response = await api.get(`/api/admin/foods?page=${page}&per_page=10`);
      if (response.success) {
        setFoods(response.foods);
        setCurrentPage((p) => ({ ...p, foods: page }));
      }
    } catch (error) {
        console.error("Error fetching foods:", error);
      toast.error("Failed to fetch foods");
    }
  };

  const fetchRequests = async (page = 1) => {
    try {
      const response = await api.get(`/api/admin/requests?page=${page}&per_page=10`);
      if (response.success) {
        setRequests(response.requests);
        setCurrentPage((p) => ({ ...p, requests: page }));
      }
    } catch (error) {
      console.error("Error fetching requests:", error);
      toast.error("Failed to fetch requests");
    }
  };

  const fetchTransactions = async (page = 1) => {
    try {
      const response = await api.get(`/api/admin/transactions?page=${page}&per_page=10`);
      if (response.success) {
        setTransactions(response.transactions);
        setCurrentPage((p) => ({ ...p, transactions: page }));
      }
    } catch (error) {
      console.error("Error fetching transactions:", error);
      toast.error("Failed to fetch transactions");
    }
  };

  const fetchStatistics = async () => {
    try {
      const response = await api.get("/api/admin/statistics/food-types");
      if (response.success) setStatistics(response.statistics);
    } catch (error) {
      console.error("Error fetching statistics:", error);
    }
  };

  const fetchActivity = async () => {
    try {
      // Remove the ?days=30 limit to fetch all activity
      const response = await api.get("/api/admin/statistics/daily-activity");
      if (response.success) {
        setActivityData(response.activity);
      }
    } catch (error) {
      console.error("Error fetching activity:", error);
    }
  };

  const fetchSystemHealth = async () => {
    try {
      const response = await api.get("/api/admin/health");
      if (response.success) setSystemHealth(response.health);
    } catch (error) {
        console.error("Error fetching system health:", error);
    }
  };

  const handleDeleteFood = async (foodId: number) => {
    if (!window.confirm("Are you sure you want to delete this food item?")) return;
    try {
      const response = await api.delete(`/api/admin/foods/${foodId}`);
      if (response.success) {
        toast.success("Food deleted successfully");
        fetchFoods(currentPage.foods);
      }
    } catch (error) {
      toast.error("Failed to delete food");
    }
  };

  const handleDeleteRequest = async (requestId: number) => {
    if (!window.confirm("Are you sure you want to delete this request?")) return;
    try {
      const response = await api.delete(`/api/admin/requests/${requestId}`);
      if (response.success) {
        toast.success("Request deleted successfully");
        fetchRequests(currentPage.requests);
      }
    } catch (error) {
      toast.error("Failed to delete request");
    }
  };

  const handleDeactivateUser = async (userId: number) => {
    if (!window.confirm("Are you sure you want to deactivate this user?")) return;
    try {
      const response = await api.delete(`/api/admin/users/${userId}`);
      if (response.success) {
        toast.success("User deactivated successfully");
        fetchUsers(currentPage.users);
      }
    } catch (error) {
      toast.error("Failed to deactivate user");
    }
  };

  useEffect(() => {
    if (activeTab === "users") fetchUsers(1);
    else if (activeTab === "foods") fetchFoods(1);
    else if (activeTab === "requests") fetchRequests(1);
    else if (activeTab === "transactions") fetchTransactions(1);
    
    // Always fetch analytics data for all tabs
    fetchStatistics();
    fetchActivity();
  }, [activeTab]);

  const chartData = activityData
    ? Object.entries(activityData).map(([date, data]: [string, any]) => ({
        date: new Date(date).toLocaleDateString("en-US", { month: "short", day: "numeric" }),
        foods: data.foods || 0,
        requests: data.requests || 0,
        transactions: data.transactions || 0,
      }))
    : [];

  const foodTypeChartData = statistics
    ? Object.entries(statistics).map(([type, data]: [string, any]) => ({
        name: type,
        value: data.count,
      }))
    : [];

  const COLORS = ["#3b82f6", "#ef4444", "#10b981", "#f59e0b", "#8b5cf6", "#ec4899"];

  if (isLoading && !dashboardData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-background via-primary/5 to-secondary/5 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4" />
          <p className="text-muted-foreground">Loading admin dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-primary/5 to-secondary/5">
      <header className="border-b bg-card/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="bg-red-500/10 p-2 rounded-lg">
              <Shield className="h-6 w-6 text-red-500" />
            </div>
            <div>
              <h1 className="text-2xl font-bold">Admin Dashboard</h1>
              <p className="text-sm text-muted-foreground">System Management & Analytics</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={logout}>
              <LogOut className="h-4 w-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-5 mb-8">
            <TabsTrigger value="overview" className="gap-2"><BarChart3 className="h-4 w-4" /><span className="hidden sm:inline">Overview</span></TabsTrigger>
            <TabsTrigger value="users" className="gap-2"><Users className="h-4 w-4" /><span className="hidden sm:inline">Users</span></TabsTrigger>
            <TabsTrigger value="foods" className="gap-2"><Package className="h-4 w-4" /><span className="hidden sm:inline">Foods</span></TabsTrigger>
            <TabsTrigger value="requests" className="gap-2"><ShoppingCart className="h-4 w-4" /><span className="hidden sm:inline">Requests</span></TabsTrigger>
            <TabsTrigger value="transactions" className="gap-2"><TrendingUp className="h-4 w-4" /><span className="hidden sm:inline">Transactions</span></TabsTrigger>
          </TabsList>

          {/* Overview */}
          <TabsContent value="overview">
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Total Users</CardTitle>
                    <Users className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{dashboardData?.users?.total || 0}</div>
                    <p className="text-xs text-muted-foreground mt-1">
                      {dashboardData?.users?.donors || 0} donors, {dashboardData?.users?.receivers || 0} receivers
                    </p>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Total Foods</CardTitle>
                    <Package className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{dashboardData?.foods?.total || 0}</div>
                    <p className="text-xs text-muted-foreground mt-1">
                      {dashboardData?.foods?.available || 0} available
                    </p>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Total Requests</CardTitle>
                    <ShoppingCart className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{dashboardData?.requests?.total || 0}</div>
                    <p className="text-xs text-muted-foreground mt-1">
                      {dashboardData?.requests?.pending || 0} pending
                    </p>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
                    <TrendingUp className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">
                      {dashboardData?.transactions?.success_rate || 0}%
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">
                      {dashboardData?.transactions?.completed || 0}/{dashboardData?.transactions?.total || 0} completed
                    </p>
                  </CardContent>
                </Card>
              </div>

              <Card>
                <CardHeader>
                  <CardTitle>System Status</CardTitle>
                  <CardDescription>Overall platform health</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <p className="text-sm font-medium">Database</p>
                      <div className="flex items-center gap-2">
                        <div className="h-2 w-2 rounded-full bg-green-500" />
                        <p className="text-sm text-muted-foreground">PostgreSQL - Healthy</p>
                      </div>
                    </div>
                    <div className="space-y-2">
                      <p className="text-sm font-medium">MongoDB</p>
                      <div className="flex items-center gap-2">
                        <div className="h-2 w-2 rounded-full bg-blue-500" />
                        <p className="text-sm text-muted-foreground">Analytics Database</p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                    <CardTitle>Activities Summary</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-3 gap-4">
                    <div className="text-center">
                      <p className="text-3xl font-bold">{dashboardData?.activities_summary?.foods || 0}</p>
                      <p className="text-xs text-muted-foreground">Total Foods</p>
                    </div>
                    <div className="text-center">
                      <p className="text-3xl font-bold">{dashboardData?.activities_summary?.requests || 0}</p>
                      <p className="text-xs text-muted-foreground">Total Requests</p>
                    </div>
                    <div className="text-center">
                      <p className="text-3xl font-bold">{dashboardData?.activities_summary?.transactions || 0}</p>
                      <p className="text-xs text-muted-foreground">Total Transactions</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Analytics Section */}
              <div className="mt-8">
                <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
                  <BarChart3 className="h-6 w-6" />
                  Analytics Overview
                </h2>
                
                {/* Real-time Update Indicator */}
                <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200 mb-6">
                  <CardContent className="pt-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <Activity className="h-5 w-5 text-blue-600 animate-pulse" />
                        <div>
                          <p className="font-semibold text-blue-900">Real-time Analytics</p>
                          <p className="text-sm text-blue-700">Last updated: {lastUpdate.toLocaleTimeString()}</p>
                        </div>
                      </div>
                      <Button 
                        variant="outline" 
                        size="sm" 
                        onClick={() => {
                          fetchDashboardData();
                          fetchActivity();
                          fetchStatistics();
                          toast.success('Dashboard refreshed');
                        }}
                      >
                        <RefreshCw className="h-4 w-4 mr-2" />
                        Refresh
                      </Button>
                    </div>
                  </CardContent>
                </Card>

                {/* System Performance Radar Chart */}
                <Card className="mb-6">
                  <CardHeader>
                    <CardTitle>System Performance Metrics</CardTitle>
                    <CardDescription>Multi-dimensional view of platform health</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={350}>
                      <RadarChart data={[
                        { metric: 'User Engagement', value: Math.min(100, (dashboardData?.users?.total || 0) * 5) },
                        { metric: 'Food Availability', value: Math.min(100, (dashboardData?.foods?.available || 0) * 10) },
                        { metric: 'Match Success', value: dashboardData?.transactions?.success_rate || 0 },
                        { metric: 'Request Fulfillment', value: Math.min(100, ((dashboardData?.requests?.total || 1) - (dashboardData?.requests?.pending || 0)) / (dashboardData?.requests?.total || 1) * 100) },
                        { metric: 'Transaction Speed', value: 85 },
                      ]}>
                        <PolarGrid stroke="#e5e7eb" />
                        <PolarAngleAxis dataKey="metric" tick={{ fontSize: 12 }} />
                        <PolarRadiusAxis angle={90} domain={[0, 100]} />
                        <Radar name="Platform Health" dataKey="value" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.6} />
                        <Tooltip />
                      </RadarChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </div>
            </div>
          </TabsContent>

          {/* Users */}
          <TabsContent value="users">
            <Card>
              <CardHeader>
                <CardTitle>User Management</CardTitle>
                <CardDescription>Manage and monitor all users on the platform</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b">
                          <th className="text-left py-3 px-4 font-medium">Name</th>
                          <th className="text-left py-3 px-4 font-medium">Email</th>
                          <th className="text-left py-3 px-4 font-medium">Roles</th>
                          <th className="text-left py-3 px-4 font-medium">Created</th>
                          <th className="text-left py-3 px-4 font-medium">Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {users.map((user) => (
                          <tr key={user.user_id} className="border-b hover:bg-muted/50">
                            <td className="py-3 px-4">{user.name}</td>
                            <td className="py-3 px-4">{user.email}</td>
                            <td className="py-3 px-4">
                              <div className="flex gap-1">
                                {user.roles.map((role) => (
                                  <span
                                    key={role}
                                    className="px-2 py-1 text-xs bg-primary/10 text-primary rounded-full"
                                  >
                                    {role}
                                  </span>
                                ))}
                            </div>
                            </td>
                            <td className="py-3 px-4 text-xs text-muted-foreground">
                              {new Date(user.created_at).toLocaleDateString()}
                            </td>
                            <td className="py-3 px-4">
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => navigate(`/admin/user/${user.user_id}`)}
                              >
                                <Edit className="h-4 w-4" />
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleDeactivateUser(user.user_id)}
                              >
                                <Trash2 className="h-4 w-4 text-red-500" />
                              </Button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  <div className="flex justify-between items-center">
                    <p className="text-sm text-muted-foreground">Page {currentPage.users}</p>
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm" onClick={() => fetchUsers(currentPage.users - 1)} disabled={currentPage.users === 1}>
                        <ChevronLeft className="h-4 w-4" />
                      </Button>
                      <Button variant="outline" size="sm" onClick={() => fetchUsers(currentPage.users + 1)}>
                        <ChevronRight className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Analytics Section for Users */}
            <div className="mt-8">
              <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
                <BarChart3 className="h-6 w-6" />
                User Analytics
              </h2>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Platform Activity */}
                {chartData.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle>Platform Activity</CardTitle>
                      <CardDescription>Daily activity trends</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <ResponsiveContainer width="100%" height={250}>
                        <LineChart data={chartData}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                          <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                          <YAxis tick={{ fontSize: 11 }} />
                          <Tooltip />
                          <Legend />
                          <Line type="monotone" dataKey="foods" stroke="#3b82f6" strokeWidth={2} />
                          <Line type="monotone" dataKey="requests" stroke="#ef4444" strokeWidth={2} />
                          <Line type="monotone" dataKey="transactions" stroke="#10b981" strokeWidth={2} />
                        </LineChart>
                      </ResponsiveContainer>
                    </CardContent>
                  </Card>
                )}

                {/* User Distribution */}
                <Card>
                  <CardHeader>
                    <CardTitle>User Distribution</CardTitle>
                    <CardDescription>Donors vs Receivers</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={250}>
                      <PieChart>
                        <Pie 
                          data={[
                            { name: 'Donors', value: dashboardData?.users?.donors || 0 },
                            { name: 'Receivers', value: dashboardData?.users?.receivers || 0 }
                          ]}
                          cx="50%" 
                          cy="50%" 
                          labelLine={false}
                          label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                          outerRadius={80} 
                          dataKey="value"
                        >
                          <Cell fill="#3b82f6" />
                          <Cell fill="#10b981" />
                        </Pie>
                        <Tooltip />
                      </PieChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </div>
            </div>
          </TabsContent>

          {/* Foods */}
          <TabsContent value="foods">
            <Card>
              <CardHeader>
                <CardTitle>Food Items Management</CardTitle>
                <CardDescription>Manage all food items in the system</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b">
                          <th className="text-left py-3 px-4 font-medium">Food Name</th>
                          <th className="text-left py-3 px-4 font-medium">Type</th>
                          <th className="text-left py-3 px-4 font-medium">Quantity (kg)</th>
                          <th className="text-left py-3 px-4 font-medium">Status</th>
                          <th className="text-left py-3 px-4 font-medium">Donor</th>
                          <th className="text-left py-3 px-4 font-medium">Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {foods.map((food) => (
                          <tr key={food.food_id} className="border-b hover:bg-muted/50">
                            <td className="py-3 px-4">{food.name}</td>
                            <td className="py-3 px-4">{food.type}</td>
                            <td className="py-3 px-4">{food.quantity}</td>
                            <td className="py-3 px-4">
                              <span className={`px-2 py-1 text-xs rounded-full ${
                                food.status === "available"
                                  ? "bg-green-100 text-green-800"
                                  : food.status === "expired"
                                  ? "bg-red-100 text-red-800"
                                  : "bg-yellow-100 text-yellow-800"
                              }`}>
                                {food.status}
                              </span>
                            </td>
                            <td className="py-3 px-4">{food.donor?.name || "Unknown"}</td>
                            <td className="py-3 px-4">
                              <Button variant="ghost" size="sm" onClick={() => handleDeleteFood(food.food_id)}>
                                <Trash2 className="h-4 w-4 text-red-500" />
                              </Button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  <div className="flex justify-between items-center">
                    <p className="text-sm text-muted-foreground">Page {currentPage.foods}</p>
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm" onClick={() => fetchFoods(currentPage.foods - 1)} disabled={currentPage.foods === 1}>
                        <ChevronLeft className="h-4 w-4" />
                      </Button>
                      <Button variant="outline" size="sm" onClick={() => fetchFoods(currentPage.foods + 1)}>
                        <ChevronRight className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Analytics Section for Foods */}
            <div className="mt-8">
              <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
                <BarChart3 className="h-6 w-6" />
                Food Analytics
              </h2>
              
              {foodTypeChartData.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle>Food Types Distribution</CardTitle>
                    <CardDescription>Breakdown by food categories</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={350}>
                      <PieChart>
                        <Pie 
                          data={foodTypeChartData} 
                          cx="50%" 
                          cy="50%" 
                          labelLine={false}
                          label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                          outerRadius={120} 
                          dataKey="value"
                        >
                          {foodTypeChartData.map((_, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip />
                      </PieChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              )}
            </div>
          </TabsContent>

          {/* Requests */}
          <TabsContent value="requests">
            <Card>
                <CardHeader>
                <CardTitle>Requests Management</CardTitle>
                <CardDescription>Manage all food requests</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b">
                          <th className="text-left py-3 px-4 font-medium">Food Type</th>
                          <th className="text-left py-3 px-4 font-medium">Quantity</th>
                          <th className="text-left py-3 px-4 font-medium">Status</th>
                          <th className="text-left py-3 px-4 font-medium">Urgency</th>
                          <th className="text-left py-3 px-4 font-medium">Receiver</th>
                          <th className="text-left py-3 px-4 font-medium">Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {requests.map((req) => (
                          <tr key={req.request_id} className="border-b hover:bg-muted/50">
                            <td className="py-3 px-4">{req.food_type}</td>
                            <td className="py-3 px-4">{req.quantity}</td>
                            <td className="py-3 px-4">
                              <span className={`px-2 py-1 text-xs rounded-full ${
                                req.status === "pending"
                                  ? "bg-yellow-100 text-yellow-800"
                                  : req.status === "completed"
                                  ? "bg-green-100 text-green-800"
                                  : "bg-gray-100 text-gray-800"
                              }`}>
                                {req.status}
                              </span>
                            </td>
                            <td className="py-3 px-4">
                              <span className={`px-2 py-1 text-xs rounded-full ${
                                req.urgency === "high"
                                  ? "bg-red-100 text-red-800"
                                  : req.urgency === "medium"
                                  ? "bg-orange-100 text-orange-800"
                                  : "bg-green-100 text-green-800"
                              }`}>
                                {req.urgency}
                              </span>
                            </td>
                            <td className="py-3 px-4">{req.receiver?.name || "Unknown"}</td>
                            <td className="py-3 px-4">
                              <Button variant="ghost" size="sm" onClick={() => handleDeleteRequest(req.request_id)}>
                                <Trash2 className="h-4 w-4 text-red-500" />
                              </Button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                </div>
                  <div className="flex justify-between items-center">
                    <p className="text-sm text-muted-foreground">Page {currentPage.requests}</p>
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm" onClick={() => fetchRequests(currentPage.requests - 1)} disabled={currentPage.requests === 1}>
                        <ChevronLeft className="h-4 w-4" />
                      </Button>
                      <Button variant="outline" size="sm" onClick={() => fetchRequests(currentPage.requests + 1)}>
                        <ChevronRight className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Analytics Section for Requests */}
            <div className="mt-8">
              <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
                <BarChart3 className="h-6 w-6" />
                Request Analytics
              </h2>
              
              <Card>
                <CardHeader>
                  <CardTitle>Request Status Overview</CardTitle>
                  <CardDescription>Pending vs fulfilled requests</CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={[
                      { name: 'Pending', value: dashboardData?.requests?.pending || 0, fill: '#f59e0b' },
                      { name: 'Fulfilled', value: (dashboardData?.requests?.total || 0) - (dashboardData?.requests?.pending || 0), fill: '#10b981' },
                    ]}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="value" fill="#8884d8" radius={[8, 8, 0, 0]}>
                        {[0, 1].map((index) => (
                          <Cell key={`cell-${index}`} fill={index === 0 ? '#f59e0b' : '#10b981'} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Transactions */}
          <TabsContent value="transactions">
            <Card>
              <CardHeader>
                <CardTitle>Transactions Management</CardTitle>
                <CardDescription>Monitor all food transactions</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b">
                          <th className="text-left py-3 px-4 font-medium">Transaction ID</th>
                          <th className="text-left py-3 px-4 font-medium">Donor</th>
                          <th className="text-left py-3 px-4 font-medium">Receiver</th>
                          <th className="text-left py-3 px-4 font-medium">Status</th>
                          <th className="text-left py-3 px-4 font-medium">Date</th>
                        </tr>
                      </thead>
                      <tbody>
                        {transactions.map((txn) => (
                          <tr key={txn.transaction_id} className="border-b hover:bg-muted/50">
                            <td className="py-3 px-4 font-mono text-xs">{txn.transaction_id}</td>
                            <td className="py-3 px-4">{txn.donor?.name || "Unknown"}</td>
                            <td className="py-3 px-4">{txn.receiver?.name || "Unknown"}</td>
                            <td className="py-3 px-4">
                              <span className={`px-2 py-1 text-xs rounded-full ${
                                txn.status === "completed"
                                  ? "bg-green-100 text-green-800"
                                  : txn.status === "in_progress"
                                  ? "bg-blue-100 text-blue-800"
                                  : "bg-gray-100 text-gray-800"
                              }`}>
                                {txn.status}
                              </span>
                            </td>
                            <td className="py-3 px-4 text-xs text-muted-foreground">
                              {new Date(txn.created_at).toLocaleDateString()}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  <div className="flex justify-between items-center">
                    <p className="text-sm text-muted-foreground">Page {currentPage.transactions}</p>
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm" onClick={() => fetchTransactions(currentPage.transactions - 1)} disabled={currentPage.transactions === 1}>
                        <ChevronLeft className="h-4 w-4" />
                      </Button>
                      <Button variant="outline" size="sm" onClick={() => fetchTransactions(currentPage.transactions + 1)}>
                        <ChevronRight className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Analytics Section for Transactions */}
            <div className="mt-8">
              <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
                <BarChart3 className="h-6 w-6" />
                Transaction Analytics
              </h2>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Daily Activity Trend */}
                {chartData.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle>Daily Activity Trends</CardTitle>
                      <CardDescription>Foods, requests, and transactions over time</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <ResponsiveContainer width="100%" height={300}>
                        <ComposedChart data={chartData}>
                          <defs>
                            <linearGradient id="colorFoods" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.1}/>
                            </linearGradient>
                            <linearGradient id="colorRequests" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="5%" stopColor="#ef4444" stopOpacity={0.8}/>
                              <stop offset="95%" stopColor="#ef4444" stopOpacity={0.1}/>
                            </linearGradient>
                          </defs>
                          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                          <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                          <YAxis tick={{ fontSize: 11 }} />
                          <Tooltip />
                          <Legend />
                          <Area type="monotone" dataKey="foods" stroke="#3b82f6" fillOpacity={1} fill="url(#colorFoods)" />
                          <Area type="monotone" dataKey="requests" stroke="#ef4444" fillOpacity={1} fill="url(#colorRequests)" />
                          <Bar dataKey="transactions" fill="#10b981" radius={[8, 8, 0, 0]} />
                        </ComposedChart>
                      </ResponsiveContainer>
                    </CardContent>
                  </Card>
                )}

                {/* Transaction Status Breakdown */}
                <Card>
                  <CardHeader>
                    <CardTitle>Transaction Status</CardTitle>
                    <CardDescription>Current transaction states</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={[
                        { name: 'Completed', value: dashboardData?.transactions?.completed || 0, fill: '#10b981' },
                        { name: 'In Progress', value: (dashboardData?.transactions?.total || 0) - (dashboardData?.transactions?.completed || 0), fill: '#f59e0b' },
                      ]}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="value" fill="#8884d8" radius={[8, 8, 0, 0]}>
                          {[0, 1].map((index) => (
                            <Cell key={`cell-${index}`} fill={index === 0 ? '#10b981' : '#f59e0b'} />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </div>
            </div>
          </TabsContent>

          {/* Remove the standalone Analytics tab - content moved to each tab */}
        </Tabs>
      </div>
    </div>
  );
};

export default AdminDashboard;