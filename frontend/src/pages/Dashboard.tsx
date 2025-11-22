import { useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Heart, Package, HandHeart, LogOut } from "lucide-react";
import DonorDashboard from "@/components/dashboard/DonorDashboard";
import ReceiverDashboard from "@/components/dashboard/ReceiverDashboard";
import ProfileButton from "@/components/ProfileButton";

const Dashboard = () => {
  const { roles, logout, userId } = useAuth();
  const [activeMode, setActiveMode] = useState<"donor" | "receiver">(
    roles.includes("donor") ? "donor" : "receiver"
  );

  const isDonor = roles.includes("donor");
  const isReceiver = roles.includes("receiver");
  const isBoth = isDonor && isReceiver;

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

          {/* Right: Profile button + Logout */}
          <div className="flex items-center gap-2">
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
      </div>
    </div>
  );
};

export default Dashboard;
