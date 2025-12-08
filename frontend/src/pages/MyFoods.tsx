import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { api, Food } from "@/lib/api";

import { Button } from "@/components/ui/button";
import { ArrowLeft, Plus } from "lucide-react";

import FoodList from "@/components/food/FoodList";
import { toast } from "sonner";

// MongoDB Components
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { FoodImages } from "@/components/food/FoodImages";
import { FoodNotes } from "@/components/food/FoodNotes";

const MyFoods = () => {
  const navigate = useNavigate();
  const { userId } = useAuth();

  const [foods, setFoods] = useState<Food[]>([]);
  const [loading, setLoading] = useState(true);

  // NEW: For MongoDB feature – selected food
  const [selectedFoodId, setSelectedFoodId] = useState<number | null>(null);
  const [mongoTab, setMongoTab] = useState("images");

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
    if (userId) loadFoods();
  }, [userId]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-primary/5 to-secondary/5 p-4">
      <div className="container mx-auto py-8">

        {/* Header (unchanged) */}
        {!selectedFoodId && (
          <div className="flex justify-between items-center mb-8">
            <div>
              <Button variant="ghost" onClick={() => navigate(-1)} className="mb-2">
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
        )}

        {/* Loading State */}
        {loading ? (
          <p className="text-center text-muted-foreground">Loading...</p>
        ) : (
          <>
            {/* If NO food selected — show food list */}
            {!selectedFoodId && (
              <FoodList
                foods={foods}
                onUpdate={loadFoods}
                onSelectFood={setSelectedFoodId}   // 🔥 Pass callback for selection
              />
            )}

            {/* If a food IS selected → Show MongoDB Tabs */}
            {selectedFoodId && (
              <div className="mt-6">
                <Button
                  variant="ghost"
                  className="mb-4"
                  onClick={() => setSelectedFoodId(null)}
                >
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back to Foods
                </Button>

                <h2 className="text-2xl font-bold mb-4">
                  Manage Food Item #{selectedFoodId}
                </h2>

                <Tabs value={mongoTab} onValueChange={setMongoTab} className="mt-4">
                  <TabsList className="grid grid-cols-2 max-w-md">
                    <TabsTrigger value="images">📸 Images</TabsTrigger>
                    <TabsTrigger value="notes">📝 Notes</TabsTrigger>
                  </TabsList>

                  <TabsContent value="images">
                    <FoodImages foodId={selectedFoodId} />
                  </TabsContent>

                  <TabsContent value="notes">
                    <FoodNotes foodId={selectedFoodId} />
                  </TabsContent>
                </Tabs>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default MyFoods;
