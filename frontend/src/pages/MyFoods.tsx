import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { api, Food } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Plus } from "lucide-react";
import FoodList from "@/components/food/FoodList";
import { toast } from "sonner";

const MyFoods = () => {
  const navigate = useNavigate();
  const { userId } = useAuth();
  const [foods, setFoods] = useState<Food[]>([]);
  const [loading, setLoading] = useState(true);

  const loadFoods = async () => {
  try {
    setLoading(true);
    const data = await api.food.getMyFoods(parseInt(userId!));
    setFoods(data || []);   
  } catch (error) {
    toast.error("Failed to load food items");
  } finally {
    setLoading(false);
  }
};

  useEffect(() => {
    loadFoods();
  }, [userId]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-primary/5 to-secondary/5 p-4">
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
            <h1 className="text-3xl font-bold">My Food Items</h1>
            <p className="text-muted-foreground">Manage your food donations</p>
          </div>
          <Button onClick={() => navigate("/food/add")}>
            <Plus className="h-4 w-4 mr-2" />
            Add Food
          </Button>
        </div>

        {loading ? (
          <p className="text-center text-muted-foreground">Loading...</p>
        ) : (
          <FoodList foods={foods} onUpdate={loadFoods} />
        )}
      </div>
    </div>
  );
};

export default MyFoods;
