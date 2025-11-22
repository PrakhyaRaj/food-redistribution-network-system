import { useState } from "react";
import { Link, Navigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Heart, Loader2 } from "lucide-react";

const Register = () => {
  const { register, isAuthenticated } = useAuth();
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    phone: "",
    location_lat: 0,
    location_long: 0,
  });
  const [roles, setRoles] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  const handleRoleChange = (role: string, checked: boolean) => {
    if (checked) {
      setRoles([...roles, role]);
    } else {
      setRoles(roles.filter((r) => r !== role));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (roles.length === 0) {
      alert("Please select at least one role");
      return;
    }
    setLoading(true);
    try {
      await register({ ...formData, roles });
    } catch (error) {
      // Error handled in context
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-secondary/10 via-background to-primary/10 p-4">
      <Card className="w-full max-w-lg shadow-lg border-border/50">
        <CardHeader className="space-y-3 text-center">
          <div className="flex justify-center">
            <div className="bg-secondary/10 p-3 rounded-full">
              <Heart className="h-8 w-8 text-secondary" fill="currentColor" />
            </div>
          </div>
          <CardTitle className="text-3xl font-bold">Join Our Community</CardTitle>
          <CardDescription className="text-base">
            Create an account to start sharing or receiving food
          </CardDescription>
        </CardHeader>
        <form onSubmit={handleSubmit}>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="name">Full Name</Label>
                <Input
                  id="name"
                  placeholder="John Doe"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="phone">Phone</Label>
                <Input
                  id="phone"
                  placeholder="9876543210"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  required
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="you@example.com"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                required
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="lat">Latitude</Label>
                <Input
                  id="lat"
                  type="number"
                  step="any"
                  placeholder="12.34"
                  value={formData.location_lat || ""}
                  onChange={(e) => setFormData({ ...formData, location_lat: parseFloat(e.target.value) })}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="long">Longitude</Label>
                <Input
                  id="long"
                  type="number"
                  step="any"
                  placeholder="56.78"
                  value={formData.location_long || ""}
                  onChange={(e) => setFormData({ ...formData, location_long: parseFloat(e.target.value) })}
                  required
                />
              </div>
            </div>
            <div className="space-y-3">
              <Label>I want to be a:</Label>
              <div className="flex flex-col space-y-2">
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="donor"
                    checked={roles.includes("donor")}
                    onCheckedChange={(checked) => handleRoleChange("donor", checked as boolean)}
                  />
                  <label htmlFor="donor" className="text-sm cursor-pointer">
                    Donor - I want to share food
                  </label>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="receiver"
                    checked={roles.includes("receiver")}
                    onCheckedChange={(checked) => handleRoleChange("receiver", checked as boolean)}
                  />
                  <label htmlFor="receiver" className="text-sm cursor-pointer">
                    Receiver - I need food assistance
                  </label>
                </div>
              </div>
            </div>
          </CardContent>
          <CardFooter className="flex flex-col space-y-4">
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Creating account...
                </>
              ) : (
                "Create Account"
              )}
            </Button>
            <p className="text-sm text-muted-foreground text-center">
              Already have an account?{" "}
              <Link to="/login" className="text-primary hover:underline font-medium">
                Sign in here
              </Link>
            </p>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
};

export default Register;
