import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ArrowLeft, HandHeart, Loader2 } from "lucide-react";
import { toast } from "sonner";

const AddRequest = () => {
  const navigate = useNavigate();
  const { userId } = useAuth();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    food_type: "",
    quantity: 0,
    urgency_level: "medium",
    deadline: "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await api.requests.create({
        receiver_id: parseInt(userId!),
        ...formData,
        deadline: formData.deadline + " 23:59:59",
      });
      toast.success("Request created successfully!");
      navigate("/requests/my");
    } catch (error) {
      toast.error("Failed to create request");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-secondary/5 to-primary/5 p-4">
      <div className="container mx-auto max-w-2xl py-8">
        <Button
          variant="ghost"
          onClick={() => navigate(-1)}
          className="mb-4"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back
        </Button>

        <Card>
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="bg-secondary/10 p-2 rounded-lg">
                <HandHeart className="h-6 w-6 text-secondary" />
              </div>
              <div>
                <CardTitle className="text-2xl">Create Food Request</CardTitle>
                <CardDescription>Request food assistance from donors</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="food_type">Food Type</Label>
                <Input
                  id="food_type"
                  placeholder="e.g., Rice, Vegetables, Groceries"
                  value={formData.food_type}
                  onChange={(e) => setFormData({ ...formData, food_type: e.target.value })}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="quantity">Quantity (units)</Label>
                <Input
                  id="quantity"
                  type="number"
                  min="1"
                  placeholder="3"
                  value={formData.quantity || ""}
                  onChange={(e) => setFormData({ ...formData, quantity: parseInt(e.target.value) })}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="urgency">Urgency Level</Label>
                <Select
                  value={formData.urgency_level}
                  onValueChange={(value) => setFormData({ ...formData, urgency_level: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">Low</SelectItem>
                    <SelectItem value="medium">Medium</SelectItem>
                    <SelectItem value="high">High</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="deadline">Deadline</Label>
                <Input
                  id="deadline"
                  type="date"
                  min={new Date().toISOString().split("T")[0]}
                  value={formData.deadline}
                  onChange={(e) => setFormData({ ...formData, deadline: e.target.value })}
                  required
                />
              </div>
              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Creating...
                  </>
                ) : (
                  <>
                    <HandHeart className="mr-2 h-4 w-4" />
                    Create Request
                  </>
                )}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default AddRequest;
