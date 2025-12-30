import { Food } from "@/lib/api";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Package, Calendar, Edit, Trash2 } from "lucide-react";
import { Link } from "react-router-dom";
import { api } from "@/lib/api";
import { toast } from "sonner";
import { RouteOptimization } from "@/components/RouteOptimization";
import { useState, useEffect } from "react";

// ✅ COMBINED PROPS (A + B)
interface FoodListProps {
  foods: Food[];
  onUpdate: () => void | Promise<void>;
  onSelectFood?: (foodId: number) => void; // <-- NEW
}

const FoodList = ({ foods, onUpdate, onSelectFood }: FoodListProps) => {
  const [foodTransactions, setFoodTransactions] = useState<Record<number, any>>({});

  // AI-style contextual notes derived from food attributes (local heuristic, no external calls)
  const buildAutoNotes = (food: Food) => {
    const notes: string[] = [];

    const name = (food.food_name || food.name || "").toLowerCase();
    const expiresInMs = new Date(food.expiry_date).getTime() - Date.now();
    const daysToExpiry = Math.ceil(expiresInMs / (1000 * 60 * 60 * 24));

    // Freshness / timing
    if (!isNaN(daysToExpiry)) {
      if (daysToExpiry <= 1) notes.push(`Highly perishable: aim to redistribute today (${daysToExpiry}d left)`);
      else if (daysToExpiry <= 3) notes.push(`Use soon: best within ~${daysToExpiry} days`);
      else notes.push(`Good shelf life: ~${daysToExpiry} days to expiry`);
    }

    // Quantity context
    if (food.quantity >= 20) notes.push("Bulk lot: consider splitting across multiple receivers");
    else if (food.quantity <= 3) notes.push("Small batch: prioritize a nearby receiver");

    // Handling & storage cues
    const needsChill = /milk|dairy|yogurt|cheese|meat|fish|chicken|beef|pork/.test(name);
    if (needsChill) notes.push("Cold chain: keep refrigerated until handoff");

    const spicy = /spicy|chili|chilli|pepper/.test(name);
    if (spicy) notes.push("Flavor: spicy profile");

    const nuts = /nut|almond|cashew|peanut|walnut|pistachio|hazelnut/.test(name);
    if (nuts) notes.push("Allergy caution: contains nuts");

    // Status-aware note
    if (food.status === "in_transit") notes.push("In transit: confirm drop-off ETA");

    return notes.slice(0, 4); // keep concise
  };

  // Load transactions for each food item when in matched/in_transit status
  useEffect(() => {
    const loadTransactions = async () => {
      const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:5000";
      for (const food of foods) {
        if (food.status === "in_transit" || food.status === "completed") {
          try {
            const response = await fetch(`${API_BASE}/api/mongodb/transactions?food_id=${food.id}`, {
              headers: {
                "Authorization": `Bearer ${localStorage.getItem("token")}`,
              },
            });
            if (response.ok) {
              const text = await response.text();
              let txns;
              try {
                txns = JSON.parse(text);
              } catch (parseErr) {
                console.error(`Failed to parse JSON for food ${food.id}:`, text.substring(0, 100));
                return;
              }
              if (txns && txns.length > 0) {
                setFoodTransactions(prev => ({
                  ...prev,
                  [food.id]: txns[0]
                }));
              }
            }
          } catch (err) {
            console.error(`Failed to load transaction for food ${food.id}:`, err);
          }
        }
      }
    };

    if (foods.length > 0) {
      loadTransactions();
    }
  }, [foods]);

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

              <Badge
                variant={
                  food.status === "available" ? "default" : "secondary"
                }
              >
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
              <span>
                Expires:{" "}
                {new Date(food.expiry_date).toLocaleDateString()}
              </span>
            </div>

            {/* Auto-generated notes derived from the food attributes */}
            <div className="pt-1 space-y-2">
              <div className="text-xs uppercase tracking-wide text-muted-foreground">Auto Notes</div>
              <div className="flex flex-wrap gap-2">
                {buildAutoNotes(food).map((note, idx) => (
                  <Badge key={idx} variant="outline" className="text-[11px]">
                    {note}
                  </Badge>
                ))}
                {buildAutoNotes(food).length === 0 && (
                  <Badge variant="secondary" className="text-[11px]">No notes</Badge>
                )}
              </div>
            </div>

              {/* 🆕 Route Optimization for matched/in-transit food */}
              {foodTransactions[food.id] && (
                <div className="mt-4 pt-4 border-t">
                  <p className="text-xs font-semibold text-muted-foreground mb-2">Redistribution Route</p>
                  <RouteOptimization 
                    transactionId={foodTransactions[food.id].txn_id}
                    donorId={foodTransactions[food.id].donor_id}
                    receiverId={foodTransactions[food.id].receiver_id}
                    showFull={false}
                  />
                </div>
              )}
          </CardContent>

          <CardFooter className="flex flex-col gap-2">

            {/* 🆕 MongoDB Button (A) */}
            {onSelectFood && (
              <Button
                variant="default"
                size="sm"
                className="w-full"
                onClick={() => onSelectFood(food.id)}
              >
                📊 View MongoDB Features
              </Button>
            )}

            <div className="flex gap-2 w-full">
              <Button variant="outline" size="sm" asChild className="flex-1">
                <Link to={`/food/edit/${food.id}`}>
                  <Edit className="h-4 w-4 mr-1" />
                  Edit
                </Link>
              </Button>

              <Button
                variant="outline"
                size="sm"
                onClick={() => handleDelete(food.id)}
                className="text-destructive hover:bg-destructive/10"
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
          </CardFooter>
        </Card>
      ))}
    </div>
  );
};

export default FoodList;
