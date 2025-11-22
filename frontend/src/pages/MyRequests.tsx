import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { api, Request as FoodRequest } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Plus } from "lucide-react";
import RequestList from "@/components/requests/RequestList";
import { toast } from "sonner";

const MyRequests = () => {
  const navigate = useNavigate();
  const { userId } = useAuth();
  const [requests, setRequests] = useState<FoodRequest[]>([]);
  const [loading, setLoading] = useState(true);

  const loadRequests = async () => {
    try {
      setLoading(true);
      const data = await api.requests.getAll();
      const myRequests = data.requests?.filter(
        (r: FoodRequest) => r.receiver_id === parseInt(userId!)
      ) || [];
      setRequests(myRequests);
    } catch (error) {
      toast.error("Failed to load requests");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRequests();
  }, [userId]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-secondary/5 to-primary/5 p-4">
      <div className="container mx-auto py-8">
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
            <p className="text-muted-foreground">Manage your food requests</p>
          </div>
          <Button onClick={() => navigate("/requests/add")}>
            <Plus className="h-4 w-4 mr-2" />
            Create Request
          </Button>
        </div>

        {loading ? (
          <p className="text-center text-muted-foreground">Loading...</p>
        ) : (
          <RequestList requests={requests} onUpdate={loadRequests} />
        )}
      </div>
    </div>
  );
};

export default MyRequests;
