import { useEffect, useState } from "react";
import { api, Request as FoodRequest } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { HandHeart, Plus, CheckCircle, Clock } from "lucide-react";
import { Link } from "react-router-dom";
import RequestList from "@/components/requests/RequestList";
import { toast } from "sonner";
import { io, Socket } from "socket.io-client";
import { RouteOptimization } from "@/components/RouteOptimization";

interface ReceiverDashboardProps {
  userId: string;
}

const ReceiverDashboard = ({ userId }: ReceiverDashboardProps) => {
  const [requests, setRequests] = useState<FoodRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [socket, setSocket] = useState<Socket | null>(null);
  const [latestTransaction, setLatestTransaction] = useState<any | null>(null);
  const [isTokenReady, setIsTokenReady] = useState(false);

  const loadData = async () => {
    try {
      setLoading(true);
      const data = await api.requests.getAll();
      // API returns array directly, handle both cases
      const allRequests = Array.isArray(data) ? data : data.requests || [];
      // Map backend fields to match FoodRequest interface
      const mapped = allRequests
        .map((r: any) => ({
          id: r.request_id,
          request_id: r.request_id,
          receiver_id: r.receiver_id,
          food_type: r.food_type,
          quantity: r.quantity,
          urgency_level: r.urgency_level,
          deadline: r.deadline,
          status: r.status,
        }))
        .filter((r: any) => r.receiver_id === parseInt(userId));
      setRequests(mapped);

      // Load latest transaction for route display
      try {
        const txns = await api.transactions.getUserTransactions(parseInt(userId));
        const arr = Array.isArray(txns) ? txns : [];
        const mine = arr
          .filter((t: any) => t.receiver_id === parseInt(userId))
          .sort((a: any, b: any) => new Date(b.date || b.created_at).getTime() - new Date(a.date || a.created_at).getTime());
        if (mine.length > 0) setLatestTransaction(mine[0]);
      } catch (e) {
        console.log("No transactions found for receiver");
      }
    } catch (error) {
      toast.error("Failed to load requests");
    } finally {
      setLoading(false);
    }
  };

  // Wait for token to be present before loading data or opening sockets
  useEffect(() => {
    const checkToken = () => {
      const token = localStorage.getItem("token");
      if (token) setIsTokenReady(true);
      else setTimeout(checkToken, 100);
    };
    checkToken();
  }, []);

  useEffect(() => {
    if (!isTokenReady || !userId) return;

    loadData();

    // Connect to Socket.IO for real-time updates
    const token = localStorage.getItem("token");
    const newSocket = io("http://127.0.0.1:5000", {
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
      console.log("✅ ReceiverDashboard connected to Socket.IO");
    });

    // When a match is found, refresh request list to show updated status
    newSocket.on("match_found", (data: any) => {
      console.log("🎯 Match found, refreshing requests...", data);
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

    newSocket.on("request_created", (data: any) => {
      console.log("📋 Request created, refreshing data...", data);
      setTimeout(() => {
        loadData();
      }, 1000);
    });

    newSocket.on("request_updated", (data: any) => {
      console.log("📋 Request updated, refreshing data...", data);
      setTimeout(() => {
        loadData();
      }, 1000);
    });

    newSocket.on("notification", (data: any) => {
      if (data.type === "match_found" || data.type === "request_fulfilled") {
        console.log("🎯 Notification: Request status changed", data);
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
  }, [isTokenReady, userId]);

  const stats = [
    {
      title: "Active Requests",
      value: requests.filter((r) => r.status === "pending").length,
      icon: Clock,
      color: "text-warning",
    },
    {
      title: "Fulfilled",
      value: requests.filter((r) => r.status === "completed").length,
      icon: CheckCircle,
      color: "text-success",
    },
    {
      title: "Total Requests",
      value: requests.length,
      icon: HandHeart,
      color: "text-primary",
    },
  ];

  return (
    <div className="space-y-8">
      {/* Stats */}
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

      {/* Quick Actions */}
      <Card className="bg-gradient-to-r from-secondary/10 to-primary/10 border-secondary/20">
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>Manage your food requests</CardDescription>
        </CardHeader>
        <CardContent className="flex gap-4 flex-wrap">
          <Button asChild>
            <Link to="/requests/add">
              <Plus className="h-4 w-4 mr-2" />
              Create Request
            </Link>
          </Button>
          <Button variant="outline" asChild>
            <Link to="/requests/my">
              <HandHeart className="h-4 w-4 mr-2" />
              My Requests
            </Link>
          </Button>
          <Button variant="outline" asChild>
            <Link to="/transactions">
              <CheckCircle className="h-4 w-4 mr-2" />
              Transactions
            </Link>
          </Button>
        </CardContent>
      </Card>

      {/* Recent Requests */}
      <div>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold">Your Recent Requests</h2>
          <Button variant="outline" size="sm" asChild>
            <Link to="/requests/my">View All</Link>
          </Button>
        </div>
        <RequestList requests={requests.slice(0, 4)} onUpdate={loadData} />
      </div>

      {/* Route Optimization */}
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

    </div>
  );
};

export default ReceiverDashboard;
