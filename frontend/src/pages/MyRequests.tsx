import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { api, Request as FoodRequest } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Plus } from "lucide-react";
import { toast } from "sonner";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const MyRequests = () => {
  const navigate = useNavigate();
  const { userId } = useAuth();
  const [requests, setRequests] = useState<FoodRequest[]>([]);
  const [loading, setLoading] = useState(true);

  const loadRequests = async () => {
    try {
      setLoading(true);
      const data = await api.requests.getAll();

      const myRequests = (data.requests || [])
  .map((r: any) => ({
    id: r.request_id,          // ✅ FIX
    receiver_id: r.receiver_id,
    food_type: r.food_type,
    quantity: r.quantity,
    urgency_level: r.urgency_level,
    deadline: r.deadline,
    status: r.status
  }))
  .filter((r: any) => r.receiver_id === Number(userId));

      setRequests(myRequests);
    } catch (error) {
      toast.error("Failed to load requests");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (userId) loadRequests();
  }, [userId]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-secondary/5 to-primary/5 p-4">
      <div className="container mx-auto py-8">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <Button
              variant="ghost"
              onClick={() => navigate(-1)}
              className="mb-2"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
            <h1 className="text-3xl font-bold">My Requests</h1>
            <p className="text-muted-foreground">
              Manage your food requests
            </p>
          </div>

          <Button onClick={() => navigate("/requests/add")}>
            <Plus className="h-4 w-4 mr-2" />
            Create Request
          </Button>
        </div>

        {/* Content */}
        {loading ? (
          <p className="text-center text-muted-foreground">Loading...</p>
        ) : requests.length === 0 ? (
          <p className="text-center text-muted-foreground">
            You have not created any requests yet
          </p>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {requests.map((request) => (
              <Card
                key={request.id}
                className="cursor-pointer hover:shadow-lg transition-shadow"
                onClick={() => navigate(`/requests/${request.id}`)}
              >
                <CardHeader>
                  <CardTitle className="flex justify-between items-center">
                    <span>{request.food_type}</span>
                    <Badge variant="secondary">
                      {request.urgency_level}
                    </Badge>
                  </CardTitle>
                </CardHeader>

                <CardContent className="space-y-2 text-sm">
                  <p>
                    <span className="text-muted-foreground">Quantity:</span>{" "}
                    {request.quantity}
                  </p>
                  <p>
                    <span className="text-muted-foreground">Status:</span>{" "}
                    {request.status || "Open"}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Click to find matching food
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default MyRequests;
