import { Request as FoodRequest } from "@/lib/api";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { HandHeart, Calendar, Package, Edit, X } from "lucide-react";
import { Link } from "react-router-dom";
import { api } from "@/lib/api";
import { toast } from "sonner";

interface RequestListProps {
  requests: FoodRequest[];
  onUpdate: () => void;
}

const RequestList = ({ requests, onUpdate }: RequestListProps) => {
  const handleCancel = async (requestId: number) => {
    if (!confirm("Are you sure you want to cancel this request?")) return;
    
    try {
      await api.requests.cancel(requestId);
      toast.success("Request cancelled");
      onUpdate();
    } catch (error) {
      toast.error("Failed to cancel request");
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "fulfilled":
        return "default";
      case "pending":
        return "secondary";
      case "cancelled":
        return "outline";
      default:
        return "secondary";
    }
  };

  if (requests.length === 0) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center justify-center py-12 text-muted-foreground">
          <HandHeart className="h-12 w-12 mb-4 opacity-50" />
          <p>No requests yet</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {requests.map((request) => (
        <Card key={request.id} className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <div className="flex justify-between items-start">
              <CardTitle className="text-lg">{request.food_type}</CardTitle>
              <Badge variant={getStatusColor(request.status)}>
                {request.status}
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Package className="h-4 w-4" />
              <span>Quantity: {request.quantity}</span>
            </div>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Calendar className="h-4 w-4" />
              <span>Deadline: {new Date(request.deadline).toLocaleDateString()}</span>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <Badge variant={request.urgency_level === "high" ? "destructive" : "secondary"}>
                {request.urgency_level} urgency
              </Badge>
            </div>
          </CardContent>
          {request.status === "pending" && (
            <CardFooter className="flex gap-2">
              <Button variant="outline" size="sm" asChild className="flex-1">
                <Link to={`/requests/edit/${request.id}`}>
                  <Edit className="h-4 w-4 mr-1" />
                  Edit
                </Link>
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleCancel(request.id)}
                className="text-destructive hover:bg-destructive/10"
              >
                <X className="h-4 w-4" />
              </Button>
            </CardFooter>
          )}
        </Card>
      ))}
    </div>
  );
};

export default RequestList;
