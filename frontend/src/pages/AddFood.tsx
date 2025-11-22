import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowLeft, Package, Loader2 } from "lucide-react";
import { toast } from "sonner";

const AddFood = () => {
  const navigate = useNavigate();
  const { userId } = useAuth();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    food_name: "",
    quantity: 0,
    expiry_date: "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await api.food.add({...formData, user_id: userId});
      toast.success("Food item added successfully!");
      navigate("/food/my");
    } catch (error) {
      toast.error("Failed to add food item");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-primary/5 to-secondary/5 p-4">
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
              <div className="bg-primary/10 p-2 rounded-lg">
                <Package className="h-6 w-6 text-primary" />
              </div>
              <div>
                <CardTitle className="text-2xl">Add Food Item</CardTitle>
                <CardDescription>Share food with those in need</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="food_name">Food Name</Label>
                <Input
                  id="food_name"
                  placeholder="e.g., Rice, Vegetables, Bread"
                  value={formData.food_name}
                  onChange={(e) => setFormData({ ...formData, food_name: e.target.value })}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="quantity">Quantity (units)</Label>
                <Input
                  id="quantity"
                  type="number"
                  min="1"
                  placeholder="5"
                  value={formData.quantity || ""}
                  onChange={(e) => setFormData({ ...formData, quantity: parseInt(e.target.value) })}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="expiry_date">Expiry Date</Label>
                <Input
                  id="expiry_date"
                  type="date"
                  min={new Date().toISOString().split("T")[0]}
                  value={formData.expiry_date}
                  onChange={(e) => setFormData({ ...formData, expiry_date: e.target.value })}
                  required
                />
              </div>
              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Adding...
                  </>
                ) : (
                  <>
                    <Package className="mr-2 h-4 w-4" />
                    Add Food Item
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

export default AddFood;
