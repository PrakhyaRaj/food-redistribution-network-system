import React, { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Calendar, Users, Utensils, MapPin, Building2, Info } from "lucide-react";
import { toast } from "sonner";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { useAuth } from "@/contexts/AuthContext";
import { api, User } from "@/lib/api";

/**
 * MealPlanner Component
 * 
 * Allows organizations to plan food requirements for multiple days.
 * Features:
 * - Calculate total meals needed based on: number of people × days × meals per day
 * - Specify dietary preferences (vegetarian, vegan, etc.)
 * - Prototype feature - does not submit actual requests to backend
 * - Designed for NGOs, community centers, schools, and shelters
 * 
 * Usage: Navigate to NGO Page → Meal Planner tab
 */

interface MealPlanFormData {
  numberOfPeople: string;
  numberOfDays: string;
  mealsPerDay: string;
  foodType: string;
  dietaryRestrictions: string;
}

const MealPlanner = () => {
  const { userId } = useAuth();
  const [userName, setUserName] = useState<string>("");
  const [formData, setFormData] = useState<MealPlanFormData>({
    numberOfPeople: "",
    numberOfDays: "",
    mealsPerDay: "3",
    foodType: "any",
    dietaryRestrictions: "",
  });

  // Fetch user name on component mount
  useEffect(() => {
    const fetchUserName = async () => {
      if (!userId) return;
      try {
        const profile: User = await api.user.getProfile(parseInt(userId));
        setUserName(profile.name);
      } catch (error) {
        console.error("Failed to fetch user name:", error);
        setUserName("User");
      }
    };
    fetchUserName();
  }, [userId]);

  const [calculatedMeals, setCalculatedMeals] = useState<number | null>(null);

  const calculateTotalMeals = () => {
    const people = parseInt(formData.numberOfPeople) || 0;
    const days = parseInt(formData.numberOfDays) || 0;
    const mealsPerDay = parseInt(formData.mealsPerDay) || 0;
    return people * days * mealsPerDay;
  };

  const handleCalculate = () => {
    const total = calculateTotalMeals();
    if (total > 0) {
      setCalculatedMeals(total);
      toast.success("Meal requirement calculated!", {
        description: `Total meals needed: ${total}`,
      });
    } else {
      toast.error("Please fill in all required fields");
    }
  };

  const handlePlanRequest = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.numberOfPeople || !formData.numberOfDays) {
      toast.error("Please fill in all required fields");
      return;
    }

    const total = calculateTotalMeals();
    
    // Prototype - just show success message
    toast.success("Meal plan created successfully!", {
      description: `Request for ${total} meals over ${formData.numberOfDays} days has been planned. Check the food bank map for nearby resources.`,
    });

    // Don't actually submit - this is a prototype
    console.log("Meal Plan (Prototype):", {
      organization: userName,
      ...formData,
      totalMeals: total,
      timestamp: new Date().toISOString(),
    });
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Calendar className="h-5 w-5 text-primary" />
          Meal Planning for Organizations
        </CardTitle>
        <CardDescription>
          Plan food requirements for multiple days and calculate total meals needed
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Alert className="mb-6 bg-blue-50 border-blue-200">
          <Info className="h-4 w-4 text-blue-600" />
          <AlertDescription className="text-blue-800">
            This is a planning tool to help organizations calculate their food needs. Use the government food bank map below to find nearby resources.
          </AlertDescription>
        </Alert>

        <form onSubmit={handlePlanRequest} className="space-y-6">
          {/* Display User/Organization Name */}
          {userName && (
            <div className="grid gap-2">
              <Label>Requested By</Label>
              <div className="flex items-center gap-2 p-3 bg-muted rounded-md">
                <Building2 className="h-4 w-4 text-muted-foreground" />
                <span className="font-medium">{userName}</span>
              </div>
            </div>
          )}

          {/* Number of People */}
          <div className="grid gap-2">
            <Label htmlFor="numberOfPeople" className="flex items-center gap-2">
              <Users className="h-4 w-4" />
              Number of People <span className="text-red-500">*</span>
            </Label>
            <Input
              id="numberOfPeople"
              type="number"
              min="1"
              placeholder="e.g., 50"
              value={formData.numberOfPeople}
              onChange={(e) => setFormData({ ...formData, numberOfPeople: e.target.value })}
              required
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Number of Days */}
            <div className="grid gap-2">
              <Label htmlFor="numberOfDays">
                Number of Days <span className="text-red-500">*</span>
              </Label>
              <Input
                id="numberOfDays"
                type="number"
                min="1"
                placeholder="e.g., 3"
                value={formData.numberOfDays}
                onChange={(e) => setFormData({ ...formData, numberOfDays: e.target.value })}
                required
              />
            </div>

            {/* Meals Per Day */}
            <div className="grid gap-2">
              <Label htmlFor="mealsPerDay">
                Meals Per Day <span className="text-red-500">*</span>
              </Label>
              <Select
                value={formData.mealsPerDay}
                onValueChange={(value) => setFormData({ ...formData, mealsPerDay: value })}
              >
                <SelectTrigger id="mealsPerDay">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1">1 meal</SelectItem>
                  <SelectItem value="2">2 meals</SelectItem>
                  <SelectItem value="3">3 meals</SelectItem>
                  <SelectItem value="4">4 meals</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Food Type */}
          <div className="grid gap-2">
            <Label htmlFor="foodType">Food Type Preference</Label>
            <Select
              value={formData.foodType}
              onValueChange={(value) => setFormData({ ...formData, foodType: value })}
            >
              <SelectTrigger id="foodType">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="any">Any</SelectItem>
                <SelectItem value="vegetarian">Vegetarian</SelectItem>
                <SelectItem value="non-vegetarian">Non-Vegetarian</SelectItem>
                <SelectItem value="vegan">Vegan</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Dietary Restrictions */}
          <div className="grid gap-2">
            <Label htmlFor="dietaryRestrictions">Dietary Restrictions (Optional)</Label>
            <Input
              id="dietaryRestrictions"
              placeholder="e.g., No nuts, Gluten-free, etc."
              value={formData.dietaryRestrictions}
              onChange={(e) => setFormData({ ...formData, dietaryRestrictions: e.target.value })}
            />
          </div>

          {/* Calculate Button */}
          <Button
            type="button"
            variant="outline"
            className="w-full"
            onClick={handleCalculate}
          >
            <Utensils className="h-4 w-4 mr-2" />
            Calculate Total Meals
          </Button>

          {/* Calculated Result */}
          {calculatedMeals !== null && (
            <Card className="bg-gradient-to-r from-green-50 to-emerald-50 border-green-200">
              <CardContent className="pt-6">
                <div className="text-center">
                  <p className="text-sm text-green-700 font-medium mb-2">Total Meals Required</p>
                  <p className="text-4xl font-bold text-green-900">{calculatedMeals}</p>
                  <p className="text-xs text-green-600 mt-2">
                    {formData.numberOfPeople} people × {formData.numberOfDays} days × {formData.mealsPerDay} meals/day
                  </p>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Submit Button */}
          <Button type="submit" className="w-full" size="lg">
            <MapPin className="h-4 w-4 mr-2" />
            Create Meal Plan & View Food Banks
          </Button>

          <p className="text-xs text-muted-foreground text-center">
            * This is a prototype feature. Actual requests will be implemented in production.
          </p>
        </form>
      </CardContent>
    </Card>
  );
};

export default MealPlanner;
