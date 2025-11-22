import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { api, Transaction } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, TrendingUp, Calendar } from "lucide-react";
import { toast } from "sonner";

const Transactions = () => {
  const navigate = useNavigate();
  const { userId } = useAuth();
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);

  const loadTransactions = async () => {
    try {
      setLoading(true);
      const data = await api.transactions.getUserTransactions(parseInt(userId!));
      setTransactions(data.transactions || []);
    } catch (error) {
      toast.error("Failed to load transactions");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTransactions();
  }, [userId]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "default";
      case "pending":
        return "secondary";
      case "cancelled":
        return "outline";
      default:
        return "secondary";
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
          <h1 className="text-3xl font-bold">Transaction History</h1>
          <p className="text-muted-foreground">View all your food donation transactions</p>
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
              <Card key={txn.id}>
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <CardTitle className="text-lg">Transaction #{txn.id}</CardTitle>
                    <Badge variant={getStatusColor(txn.status)}>
                      {txn.status}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <p className="text-sm text-muted-foreground">Donor ID</p>
                    <p className="font-medium">{txn.donor_id}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Receiver ID</p>
                    <p className="font-medium">{txn.receiver_id}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Food ID</p>
                    <p className="font-medium">{txn.food_id}</p>
                  </div>
                  <div className="col-span-1 md:col-span-3">
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <Calendar className="h-4 w-4" />
                      <span>Created: {new Date(txn.created_at).toLocaleString()}</span>
                    </div>
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
