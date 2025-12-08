import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { api, User } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, User as UserIcon } from "lucide-react";
import { toast } from "sonner";
import { MongoDBCard } from "@/components/mongodb/MongoDBCard";

const ProfilePage: React.FC = () => {
  const navigate = useNavigate();
  const { userId } = useAuth();
  const [profile, setProfile] = useState<User | null>(null);
  const [feedbackHistory, setFeedbackHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  // Load SQL profile
  useEffect(() => {
    const loadProfile = async () => {
      if (!userId) return;

      try {
        setLoading(true);
        const data: User = await api.user.getProfile(parseInt(userId));
        setProfile(data);
      } catch (error: any) {
        toast.error(error.message || "Failed to load profile");
      } finally {
        setLoading(false);
      }
    };
    loadProfile();
  }, [userId]);

  // Load MongoDB feedback history
  useEffect(() => {
    if (userId) loadFeedbackHistory();
  }, [userId]);

  const loadFeedbackHistory = async () => {
    try {
      const data = await api.mongodb.getFeedbackHistory(parseInt(userId!));
      setFeedbackHistory(data.feedback || data || []);
    } catch (error) {
      console.error("Failed to load feedback:", error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-primary/5 to-secondary/5 p-4">
      <div className="container mx-auto py-8">

        {/* Back Button */}
        <Button variant="ghost" onClick={() => navigate(-1)} className="mb-4">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back
        </Button>

        {/* SQL PROFILE */}
        {loading ? (
          <p className="text-center text-muted-foreground">Loading...</p>
        ) : !profile ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12 text-muted-foreground">
              <UserIcon className="h-12 w-12 mb-4 opacity-50" />
              <p>No profile found</p>
            </CardContent>
          </Card>
        ) : (
          <Card className="mb-10">
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <UserIcon className="h-5 w-5" />
                {profile.name}
              </CardTitle>
            </CardHeader>

            <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-muted-foreground">Email</p>
                <p className="font-medium">{profile.email}</p>
              </div>

              <div>
                <p className="text-sm text-muted-foreground">Phone</p>
                <p className="font-medium">{profile.phone || "Not provided"}</p>
              </div>

              <div>
                <p className="text-sm text-muted-foreground">Location</p>
                <p className="font-medium">
                  {profile.location_lat && profile.location_long
                    ? `${profile.location_lat}, ${profile.location_long}`
                    : "Not set"}
                </p>
              </div>

              <div>
                <p className="text-sm text-muted-foreground">Roles</p>
                <div className="flex gap-2 flex-wrap">
                  {profile.roles.map((role) => (
                    <Badge key={role}>{role}</Badge>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* -------------------------------- */}
        {/* 💚 MONGODB FEATURES SECTION      */}
        {/* -------------------------------- */}

        <div className="mt-10 pt-8 border-t">
          <h2 className="text-2xl font-bold mb-6">MongoDB Features</h2>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Feedback card */}
            <MongoDBCard title="💬 Feedback History" icon="💬">
              {feedbackHistory.length > 0 ? (
                <div className="space-y-3 max-h-80 overflow-y-auto">
                  {feedbackHistory.map((feedback: any) => (
                    <div key={feedback._id} className="p-3 bg-white border rounded">
                      <p className="font-medium">{feedback.comment}</p>
                      <div className="flex justify-between text-sm text-gray-500 mt-1">
                        <span>Rating: {feedback.rating}/5</span>
                        <span>
                          {new Date(feedback.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-center text-gray-500 py-4">
                  No feedback submitted yet
                </p>
              )}
            </MongoDBCard>

            {/* You can add more MongoDB features here */}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
