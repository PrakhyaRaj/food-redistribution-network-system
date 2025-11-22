import { Request as FoodRequest } from "@/lib/api";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { HandHeart, Calendar, Package, AlertCircle } from "lucide-react";
import { api } from "@/lib/api";
import { toast } from "sonner";
import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useAuth } from "@/contexts/AuthContext";

interface NearbyRequestsProps {
  requests: FoodRequest[];
  onMatch: () => void;
}

const NearbyRequests = ({ requests, onMatch }: NearbyRequestsProps) => {
  const { userId } = useAuth();
  const [selectedRequest, setSelectedRequest] = useState<FoodRequest | null>(null);
  const [myFoodId, setMyFoodId] = useState<number | null>(null);

  const handleMatch = async (requestId: number, foodId: number) => {
    try {
      await api.food.match(foodId, requestId);
      toast.success("Successfully matched food with request!");
      setSelectedRequest(null);
      onMatch();
    } catch (error) {
      toast.error("Failed to match food with request");
    }
  };

  const getUrgencyColor = (urgency: string) => {
    switch (urgency) {
      case "high":
        return "destructive";
      case "medium":
        return "default";
      default:
        return "secondary";
    }
  };

  if (requests.length === 0) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center justify-center py-12 text-muted-foreground">
          <HandHeart className="h-12 w-12 mb-4 opacity-50" />
          <p>No nearby requests at the moment</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {requests.map((request) => (
          <Card key={request.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex justify-between items-start">
                <CardTitle className="text-lg">{request.food_type}</CardTitle>
                <Badge variant={getUrgencyColor(request.urgency_level)}>
                  {request.urgency_level} urgency
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Package className="h-4 w-4" />
                <span>Needed: {request.quantity} units</span>
              </div>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Calendar className="h-4 w-4" />
                <span>Deadline: {new Date(request.deadline).toLocaleDateString()}</span>
              </div>
              {request.urgency_level === "high" && (
                <div className="flex items-center gap-2 text-sm text-destructive">
                  <AlertCircle className="h-4 w-4" />
                  <span>Urgent need!</span>
                </div>
              )}
            </CardContent>
            <CardFooter>
              <Button className="w-full" onClick={() => setSelectedRequest(request)}>
                <HandHeart className="h-4 w-4 mr-2" />
                Match with My Food
              </Button>
            </CardFooter>
          </Card>
        ))}
      </div>

      <Dialog open={!!selectedRequest} onOpenChange={() => setSelectedRequest(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Match Food with Request</DialogTitle>
            <DialogDescription>
              This feature requires selecting your food item. Please go to "My Foods" to match items directly.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setSelectedRequest(null)}>
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default NearbyRequests;
