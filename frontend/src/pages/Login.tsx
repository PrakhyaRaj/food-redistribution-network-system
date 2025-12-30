import { useState, useEffect } from "react";
import { Link, Navigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Heart, Loader2, Leaf, Users, Package } from "lucide-react";
import { api } from "@/lib/api";

const Login = () => {
  const { login, isAuthenticated } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [globalAnalytics, setGlobalAnalytics] = useState<any>(null);
  const [analyticsLoading, setAnalyticsLoading] = useState(true);

  useEffect(() => {
    // Load global analytics for display
    const loadGlobalAnalytics = async () => {
      try {
        setAnalyticsLoading(true);
        const data = await api.mongodb.getGlobalAnalytics();
        setGlobalAnalytics(data.summary || data);
      } catch (error) {
        console.error('Failed to load global analytics:', error);
        setGlobalAnalytics(null);
      } finally {
        setAnalyticsLoading(false);
      }
    };
    
    loadGlobalAnalytics();
  }, []);

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await login(email, password);
    } catch (error) {
      // Error handled in context
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col lg:flex-row items-center justify-center bg-gradient-to-br from-primary/10 via-background to-secondary/10 p-4">
      {/* Left side - Global Analytics Stats */}
      <div className="hidden lg:flex lg:w-1/2 flex-col items-center justify-center space-y-8 pr-8">
        <div className="text-center space-y-3 mb-6">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
            Food Redistribution Network
          </h1>
          <p className="text-lg text-muted-foreground">
            Join a community making a difference
          </p>
        </div>

        {analyticsLoading ? (
          <div className="flex justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          </div>
        ) : globalAnalytics ? (
          <div className="grid grid-cols-1 gap-4 w-full">
            {/* Food Saved */}
            <div className="bg-gradient-to-br from-green-50 to-emerald-50 p-6 rounded-lg border border-green-200">
              <div className="flex items-start gap-4">
                <div className="bg-green-100 p-3 rounded-lg">
                  <Package className="h-6 w-6 text-green-600" />
                </div>
                <div className="flex-1">
                  <p className="text-sm text-green-700 font-medium">Food Saved</p>
                  <p className="text-2xl font-bold text-green-900">
                    {globalAnalytics.total_food_saved_kg >= 1000
                      ? `${(globalAnalytics.total_food_saved_kg / 1000).toFixed(1)} tons`
                      : `${Math.round(globalAnalytics.total_food_saved_kg)} kg`}
                  </p>
                </div>
              </div>
            </div>

            {/* People Fed */}
            <div className="bg-gradient-to-br from-blue-50 to-cyan-50 p-6 rounded-lg border border-blue-200">
              <div className="flex items-start gap-4">
                <div className="bg-blue-100 p-3 rounded-lg">
                  <Users className="h-6 w-6 text-blue-600" />
                </div>
                <div className="flex-1">
                  <p className="text-sm text-blue-700 font-medium">People Fed</p>
                  <p className="text-2xl font-bold text-blue-900">
                    {Math.round(globalAnalytics.total_people_fed)}+
                  </p>
                </div>
              </div>
            </div>

            {/* Trees Planted */}
            <div className="bg-gradient-to-br from-emerald-50 to-teal-50 p-6 rounded-lg border border-emerald-200">
              <div className="flex items-start gap-4">
                <div className="bg-emerald-100 p-3 rounded-lg">
                  <Leaf className="h-6 w-6 text-emerald-600" />
                </div>
                <div className="flex-1">
                  <p className="text-sm text-emerald-700 font-medium">Trees Planted (equiv.)</p>
                  <p className="text-2xl font-bold text-emerald-900">
                    {Math.round((globalAnalytics.total_carbon_saved || 0) / 20)}
                  </p>
                  <p className="text-xs text-emerald-600 mt-1">Based on CO₂ saved</p>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center py-12">
            <p className="text-muted-foreground">Loading impact statistics...</p>
          </div>
        )}
      </div>

      {/* Right side - Login Form */}
      <div className="w-full lg:w-1/2 lg:max-w-md">
      <Card className="shadow-lg border-border/50">
        <CardHeader className="space-y-3 text-center">
          <div className="flex justify-center">
            <div className="bg-primary/10 p-3 rounded-full">
              <Heart className="h-8 w-8 text-primary" fill="currentColor" />
            </div>
          </div>
          <CardTitle className="text-3xl font-bold">Welcome Back</CardTitle>
          <CardDescription className="text-base">
            Sign in to continue sharing and receiving food
          </CardDescription>
        </CardHeader>
        <form onSubmit={handleSubmit}>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                disabled={loading}
                autoComplete="current-password" 
              />
            </div>
          </CardContent>
          <CardFooter className="flex flex-col space-y-4">
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Signing in...
                </>
              ) : (
                "Sign In"
              )}
            </Button>
            <p className="text-sm text-muted-foreground text-center">
              Don't have an account?{" "}
              <Link to="/register" className="text-primary hover:underline font-medium">
                Register here
              </Link>
            </p>
          </CardFooter>
        </form>
      </Card>
      </div>
    </div>
  );
};

export default Login;
