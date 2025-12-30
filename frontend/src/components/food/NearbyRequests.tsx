import { Request as FoodRequest, Food } from "@/lib/api";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { HandHeart, Calendar, Package, AlertCircle, Loader2 } from "lucide-react";
import { api } from "@/lib/api";
import { toast } from "sonner";
import { useState, useEffect } from "react";
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
  const [myFoods, setMyFoods] = useState<Food[]>([]);
  const [loadingFoods, setLoadingFoods] = useState(false);
  const [matching, setMatching] = useState(false);

  // Load donor's foods whenever a request is selected
  useEffect(() => {
    if (selectedRequest && userId) {
      loadMyFoods();
    }
  }, [selectedRequest, userId]);

  const loadMyFoods = async () => {
    try {
      setLoadingFoods(true);
      const data = await api.food.getMyFoods(Number(userId));
      const foods = Array.isArray(data) ? data : data.foods || [];
      setMyFoods(foods.filter(f => f.status === "available"));
    } catch (error) {
      toast.error("Failed to load your food items");
    } finally {
      setLoadingFoods(false);
    }
  };

  const handleMatch = async () => {
    if (!selectedRequest || !myFoodId) {
      toast.error("Please select a food item");
      return;
    }

    try {
      setMatching(true);
      const res = await api.food.match(myFoodId, selectedRequest.id);
      console.log("NearbyRequests: match response", res);
      toast.success("Successfully matched food with request!");
      setSelectedRequest(null);
      setMyFoodId(null);
      // Give backend a short moment to process and emit events, then refresh parent
      setTimeout(() => {
        try {
          onMatch(); // Trigger dashboard refresh
        } catch (e) {
          console.error("NearbyRequests: onMatch failed", e);
        }
      }, 800);
    } catch (error) {
      console.error("NearbyRequests: match error", error);
      const msg = (error && (error.message || (error.error && error.error))) || "Failed to match food with request";
      toast.error(msg);
    } finally {
      setMatching(false);
    }
  };

  const getUrgencyColor = (urgency: string) => {
    switch (urgency) {
      case "high": return "destructive";
      case "medium": return "default";
      default: return "secondary";
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
      {/* Requests Grid */}
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

      {/* Match Dialog */}
      <Dialog open={!!selectedRequest} onOpenChange={() => setSelectedRequest(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Match Food with Request</DialogTitle>
            <DialogDescription>
              {selectedRequest &&
                `Select one of your available food items to match with "${selectedRequest.food_type}" request`}
            </DialogDescription>
          </DialogHeader>

          <div className="max-h-96 overflow-y-auto space-y-2 my-4">
            {loadingFoods ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
                Loading your food items...
              </div>
            ) : myFoods.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <p>You don't have any available food items</p>
                <p className="text-sm mt-2">Add food items in "My Foods" first</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-2">
                {myFoods.map((food) => {
                  const foodIdNum = Number(food.id); // Ensure numeric ID
                  const isSelected = myFoodId === foodIdNum;

                  return (
                    <div
                      key={food.id}
                      onClick={() => setMyFoodId(foodIdNum)}
                      className={`p-3 border rounded-lg cursor-pointer transition-all flex justify-between items-center ${
                        isSelected ? "border-primary bg-primary/10" : "border-border hover:border-primary/50"
                      }`}
                    >
                      <div>
                        <p className="font-medium">{food.food_name}</p>
                        <p className="text-sm text-muted-foreground">{food.quantity} units available</p>
                      </div>
                      <Badge variant={isSelected ? "secondary" : "outline"}>{food.status}</Badge>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setSelectedRequest(null)}>
              Cancel
            </Button>
            <Button
              onClick={handleMatch}
              disabled={!myFoodId || matching || myFoods.length === 0}
              className="gap-2"
            >
              {matching && <Loader2 className="h-4 w-4 animate-spin" />}
              {matching ? "Matching..." : "Confirm Match"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default NearbyRequests;
