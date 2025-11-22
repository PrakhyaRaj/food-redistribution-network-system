import { Food } from "@/lib/api";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Package, Calendar, Edit, Trash2 } from "lucide-react";
import { Link } from "react-router-dom";
import { api } from "@/lib/api";
import { toast } from "sonner";

interface FoodListProps {
  foods: Food[];
  onUpdate: () => void;
}

const FoodList = ({ foods, onUpdate }: FoodListProps) => {
  const handleDelete = async (foodId: number) => {
    if (!confirm("Are you sure you want to delete this food item?")) return;
    
    try {
      await api.food.delete(foodId);
      toast.success("Food item deleted");
      onUpdate();
    } catch (error) {
      toast.error("Failed to delete food item");
    }
  };

  if (foods.length === 0) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center justify-center py-12 text-muted-foreground">
          <Package className="h-12 w-12 mb-4 opacity-50" />
          <p>No food items yet</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {foods.map((food) => (
        <Card key={food.id} className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <div className="flex justify-between items-start">
              <CardTitle className="text-lg">{food.food_name}</CardTitle>
              <Badge variant={food.status === "available" ? "default" : "secondary"}>
                {food.status}
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Package className="h-4 w-4" />
              <span>Quantity: {food.quantity}</span>
            </div>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Calendar className="h-4 w-4" />
              <span>Expires: {new Date(food.expiry_date).toLocaleDateString()}</span>
            </div>
          </CardContent>
          <CardFooter className="flex gap-2">
            <Button variant="outline" size="sm" asChild className="flex-1">
              <Link to={`/food/edit/${food.id}`}>
                <Edit className="h-4 w-4 mr-1" />
                Edit
              </Link>
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleDelete(food.food_id)}
              className="text-destructive hover:bg-destructive/10"
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </CardFooter>
        </Card>
      ))}
    </div>
  );
};

export default FoodList;
