import { useEffect, useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Heart, Package, HandHeart, LogOut, Shield } from "lucide-react";
import DonorDashboard from "@/components/dashboard/DonorDashboard";
import ReceiverDashboard from "@/components/dashboard/ReceiverDashboard";
import ProfileButton from "@/components/ProfileButton";
import { HomepageFeedback } from "@/components/mongodb/HomepageFeedback";
import { TransactionHistory } from "@/components/mongodb/TransactionHistory";

import { 
  NotificationCenter, 
  FeedbackInsights, 
  FoodNotesManager,
  ActivitiesFeed,
  AnalyticsDashboard 
} from '@/components/mongodb';

const Dashboard = () => {
  const { roles, logout, userId } = useAuth();
  const navigate = useNavigate();
  const [activeMode, setActiveMode] = useState<"donor" | "receiver">("donor");

  const isDonor = roles.includes("donor");
  const isReceiver = roles.includes("receiver");
  const isBoth = isDonor && isReceiver;

  useEffect(() => {
    if (roles.includes("admin") && !isDonor && !isReceiver) {
      navigate("/admin/dashboard", { replace: true });
    }
  }, [roles, isDonor, isReceiver, navigate]);

  useEffect(() => {
    if (roles.includes("donor") && !roles.includes("receiver")) setActiveMode("donor");
    else if (!roles.includes("donor") && roles.includes("receiver")) setActiveMode("receiver");
  }, [roles]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-primary/5 to-secondary/5">
      {/* Header */}
      <header className="border-b bg-card/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          {/* Left: Logo + role info */}
          <div className="flex items-center gap-3">
            <div className="bg-primary/10 p-2 rounded-lg">
              <Heart className="h-6 w-6 text-primary" fill="currentColor" />
            </div>
            <div>
              <h1 className="text-2xl font-bold">Food Share</h1>
              <p className="text-sm text-muted-foreground">
                {isBoth
                  ? "Donor & Receiver"
                  : roles[0]?.charAt(0).toUpperCase() + roles[0]?.slice(1)}
              </p>
            </div>  
          </div>

          {/* Right: Profile button + Logout + Admin Link */}
          <div className="flex items-center gap-2">
            {roles.includes("admin") && (
              <Button 
                variant="outline" 
                size="sm" 
                onClick={() => navigate("/admin/dashboard")}
              >
                <Shield className="h-4 w-4 mr-2" />
                Admin
              </Button>
            )}
            <ProfileButton />
            <Button variant="outline" size="sm" onClick={logout}>
              <LogOut className="h-4 w-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        {isBoth ? (
          <Tabs
            value={activeMode}
            onValueChange={(v) => setActiveMode(v as "donor" | "receiver")}
          >
            <TabsList className="grid w-full max-w-md mx-auto grid-cols-2 mb-8">
              <TabsTrigger value="donor" className="gap-2">
                <Package className="h-4 w-4" />
                Donor Mode
              </TabsTrigger>
              <TabsTrigger value="receiver" className="gap-2">
                <HandHeart className="h-4 w-4" />
                Receiver Mode
              </TabsTrigger>
            </TabsList>
            <TabsContent value="donor">
              <DonorDashboard userId={userId!} />
            </TabsContent>
            <TabsContent value="receiver">
              <ReceiverDashboard userId={userId!} />
            </TabsContent>
          </Tabs>
        ) : isDonor ? (
          <DonorDashboard userId={userId!} />
        ) : (
          <ReceiverDashboard userId={userId!} />
        )}

        {/* ================= Platform Analytics (MongoDB) ================= */}
        <section className="mt-16">
          {/* Section Divider */}
          <div className="flex items-center gap-4 mb-8">
            <div className="flex-1 h-px bg-border" />
            <h2 className="text-2xl font-bold text-muted-foreground">
              Platform Analytics
            </h2>
            <div className="flex-1 h-px bg-border" />
          </div>

          {/* Analytics Cards */}
          <div className="space-y-8">
            {/* Top analytics */}
            <AnalyticsDashboard />

            {/* Notifications + Feedback */}
            <div className="grid md:grid-cols-2 gap-6">
              <NotificationCenter />
              <HomepageFeedback />
            </div>

            {/* Activity feed */}
            <ActivitiesFeed />
          </div>
        </section>
      </div>
    </div>
  );
};

export default Dashboard;
