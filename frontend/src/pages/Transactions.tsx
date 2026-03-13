import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { api, Transaction } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, TrendingUp, Calendar, RefreshCw } from "lucide-react";
import { toast } from "sonner";
import { io, Socket } from "socket.io-client";
import { RouteOptimization } from "@/components/RouteOptimization";

const Transactions = () => {
  const navigate = useNavigate();
  const { userId } = useAuth();
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [socket, setSocket] = useState<Socket | null>(null);

  const loadTransactions = async () => {
    try {
      setLoading(true);
      const data = await api.transactions.getUserTransactions(parseInt(userId!));
      // Backend returns array directly, map txn_id to id and date to created_at
      const txns = Array.isArray(data) ? data : data.transactions || [];
      const mapped = txns.map((t: any) => ({
        id: t.txn_id,
        txn_id: t.txn_id,
        donor_id: t.donor_id,
        receiver_id: t.receiver_id,
        food_id: t.food_id,
        food_name: t.food_name,
        status: t.status,
        created_at: t.date,
        date: t.date
      }));
      setTransactions(mapped);
    } catch (error) {
      toast.error("Failed to load transactions");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTransactions();

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
      console.log("✅ Transactions page connected to Socket.IO");
    });

    // Listen for match found event and refresh transactions
    newSocket.on("match_found", (data: any) => {
      console.log("📊 New transaction detected, refreshing...", data);
      toast.success("New transaction created!", {
        description: "Refreshing your transaction list...",
      });
      setTimeout(() => {
        loadTransactions();
      }, 500);
    });

    newSocket.on("transaction_created", (data: any) => {
      console.log("💰 Transaction created event received:", data);
      toast.success("New transaction!", {
        description: `Transaction #${data.txn_id} created`,
      });
      setTimeout(() => {
        loadTransactions();
      }, 500);
    });

    newSocket.on("transaction_updated", (data: any) => {
      console.log("💰 Transaction updated event received:", data);
      toast.info("Transaction updated", {
        description: `Transaction #${data.txn_id} status changed to ${data.status}`,
      });
      setTimeout(() => {
        loadTransactions();
      }, 500);
    });

    newSocket.on("notification", (data: any) => {
      if (data.type === "match_found" || data.type === "food_accepted") {
        console.log("📊 Notification: New transaction", data);
        setTimeout(() => {
          loadTransactions();
        }, 500);
      }
    });

    setSocket(newSocket);

    return () => {
      if (newSocket) {
        newSocket.disconnect();
      }
    };
  }, [userId]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "default";
      case "in_progress":
        return "secondary";
      case "pending":
        return "secondary";
      case "cancelled":
        return "outline";
      default:
        return "secondary";
    }
  };

  const handleMarkDelivered = async (txnId: number) => {
    try {
      await api.transactions.markDelivered(txnId);
      toast.success("Transaction marked as delivered!");
      loadTransactions();
    } catch (error) {
      toast.error("Failed to mark as delivered");
    }
  };

  const handleMarkReceived = async (txnId: number) => {
    try {
      await api.transactions.markReceived(txnId);
      toast.success("Transaction completed!");
      loadTransactions();
    } catch (error) {
      toast.error("Failed to mark as received");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-primary/5 to-secondary/5 p-4">
      <div className="container mx-auto py-8">
        <div className="mb-8">
          <Button
            variant="ghost"
            onClick={() => navigate(-1)}
            className="mb-2"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-bold">Transaction History</h1>
              <p className="text-muted-foreground">View all your food donation transactions</p>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={loadTransactions}
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
          </div>
        </div>

        {loading ? (
          <p className="text-center text-muted-foreground">Loading...</p>
        ) : transactions.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12 text-muted-foreground">
              <TrendingUp className="h-12 w-12 mb-4 opacity-50" />
              <p>No transactions yet</p>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            {transactions.map((txn) => (
              <Card key={txn.txn_id}>
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <CardTitle className="text-lg">Transaction #{txn.txn_id}</CardTitle>
                    <Badge variant={getStatusColor(txn.status)}>
                      {txn.status}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <p className="text-sm text-muted-foreground">Food Item</p>
                      <p className="font-medium">{txn.food_name || `Food #${txn.food_id}`}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Status</p>
                      <p className="font-medium capitalize">{txn.status}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Party</p>
                      <p className="font-medium">
                        {txn.donor_id === parseInt(userId!) ? `Recipient: #${txn.receiver_id}` : `Donor: #${txn.donor_id}`}
                      </p>
                    </div>
                    <div className="col-span-1 md:col-span-3">
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Calendar className="h-4 w-4" />
                        <span>Created: {new Date(txn.date).toLocaleString()}</span>
                      </div>
                    </div>
                  </div>
                  
                  {/* Action Buttons */}
                  {txn.status !== "completed" && txn.status !== "cancelled" && (
                    <div className="flex gap-2 mt-4">
                      {/* Donor can mark as delivered when status is initiated */}
                      {txn.donor_id === parseInt(userId!) && txn.status === "initiated" && (
                        <Button
                          onClick={() => handleMarkDelivered(txn.txn_id)}
                          variant="default"
                          size="sm"
                        >
                          Mark as Delivered
                        </Button>
                      )}
                      {/* Receiver can mark as received when status is in_progress */}
                      {txn.receiver_id === parseInt(userId!) && txn.status === "in_progress" && (
                        <Button
                          onClick={() => handleMarkReceived(txn.txn_id)}
                          variant="default"
                          size="sm"
                        >
                          Mark as Received
                        </Button>
                      )}
                    </div>
                  )}
                  
                  {/* Route Optimization Component */}
                  <div className="mt-4 pt-4 border-t">
                    <RouteOptimization 
                      transactionId={txn.txn_id} 
                      donorId={txn.donor_id}
                      receiverId={txn.receiver_id}
                      showFull={false}
                    />
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Transactions;
