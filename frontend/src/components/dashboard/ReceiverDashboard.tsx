import { useEffect, useState } from "react";
import { api, Request as FoodRequest } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { HandHeart, Plus, CheckCircle, Clock } from "lucide-react";
import { Link } from "react-router-dom";
import RequestList from "@/components/requests/RequestList";
import { toast } from "sonner";

interface ReceiverDashboardProps {
  userId: string;
}

const ReceiverDashboard = ({ userId }: ReceiverDashboardProps) => {
  const [requests, setRequests] = useState<FoodRequest[]>([]);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      setLoading(true);
      const data = await api.requests.getAll();
      const myRequests = data.requests?.filter(
        (r: FoodRequest) => r.receiver_id === parseInt(userId)
      ) || [];
      setRequests(myRequests);
    } catch (error) {
      toast.error("Failed to load requests");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [userId]);

  const stats = [
    {
      title: "Active Requests",
      value: requests.filter((r) => r.status === "pending").length,
      icon: Clock,
      color: "text-warning",
    },
    {
      title: "Fulfilled",
      value: requests.filter((r) => r.status === "fulfilled").length,
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
    </div>
  );
};

export default ReceiverDashboard;
