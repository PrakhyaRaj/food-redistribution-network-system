import React, { useState, useEffect } from "react";
import { MongoDBCard } from "./MongoDBCard";
import { MessageSquare, Star, TrendingUp } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { io, Socket } from "socket.io-client";

interface Feedback {
  _id: string;
  user_id: string;
  rating: number;
  feedback_type: string;
  content: string;
  created_at: string;
}

const API_BASE = "http://127.0.0.1:5000";

const getHeaders = () => {
  const token = localStorage.getItem("token") || localStorage.getItem("access_token");
  return {
    "Content-Type": "application/json",
    ...(token && { Authorization: `Bearer ${token}` }),
  };
};

export const FeedbackInsights: React.FC<{ reloadSignal?: boolean }> = ({ reloadSignal }) => {
  const [feedbacks, setFeedbacks] = useState<Feedback[]>([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalFeedback: 0,
    averageRating: 0,
    typeBreakdown: {} as Record<string, number>,
  });
  const [socket, setSocket] = useState<Socket | null>(null);

  useEffect(() => {
    loadFeedbacks();
    
    // Connect to Socket.IO for real-time feedback updates
    const token = localStorage.getItem('token');
    const newSocket = io('http://127.0.0.1:5000', {
      transports: ['polling'],
      withCredentials: true,
      query: { token },
      auth: { token },
      reconnection: true,
      reconnectionAttempts: 5,
    });

    newSocket.on('feedback_submitted', () => {
      console.log('💬 Feedback submitted, refreshing insights...');
      setTimeout(() => {
        loadFeedbacks();
      }, 500);
    });

    setSocket(newSocket);

    return () => {
      if (newSocket) {
        newSocket.disconnect();
      }
    };
  }, [reloadSignal]);

  const loadFeedbacks = async () => {
    try {
      const response = await fetch(`${API_BASE}/feedback`, { headers: getHeaders() });
      if (response.ok) {
        const data = await response.json();

        // Accept either a plain array or an object with feedbacks property
        const rawList = Array.isArray(data) ? data : (data.feedbacks || []);

        // Sort newest first by created_at
        const feedbackList = [...rawList].sort((a, b) => {
          const ad = new Date(a.created_at || 0).getTime();
          const bd = new Date(b.created_at || 0).getTime();
          return bd - ad;
        });

        setFeedbacks(feedbackList);

        const totalFeedback = feedbackList.length;
        const averageRating =
          totalFeedback > 0
            ? feedbackList.reduce((sum, f) => sum + (f.rating || 0), 0) / totalFeedback
            : 0;

        const typeBreakdown: Record<string, number> = {};
        feedbackList.forEach((f) => {
          const key = f.feedback_type || f.type || "unknown";
          typeBreakdown[key] = (typeBreakdown[key] || 0) + 1;
        });

        setStats({ totalFeedback, averageRating, typeBreakdown });
      }
    } catch (err) {
      console.error("Failed to load feedbacks:", err);
    } finally {
      setLoading(false);
    }
  };

  const getFeedbackTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      suggestion: "bg-blue-100 text-blue-800",
      bug: "bg-red-100 text-red-800",
      praise: "bg-green-100 text-green-800",
      complaint: "bg-yellow-100 text-yellow-800",
    };
    return colors[type] || "bg-gray-100 text-gray-800";
  };

  const renderStars = (rating: number) => (
    <div className="flex gap-1">
      {[1, 2, 3, 4, 5].map((star) => (
        <Star
          key={star}
          className={`h-4 w-4 ${star <= rating ? "fill-yellow-400 text-yellow-400" : "text-gray-300"}`}
        />
      ))}
    </div>
  );

  return (
    <MongoDBCard title="Feedback & Insights" icon="💬">
      {loading ? (
        <div className="flex justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
      ) : (
        <div className="space-y-4">
          {/* Statistics */}
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-blue-50 p-3 rounded-lg border border-blue-200">
              <div className="flex items-center gap-2 mb-1">
                <MessageSquare className="h-4 w-4 text-blue-600" />
                <span className="text-sm font-medium text-blue-800">Total Feedback</span>
              </div>
              <p className="text-2xl font-bold text-blue-900">{stats.totalFeedback}</p>
            </div>
            <div className="bg-yellow-50 p-3 rounded-lg border border-yellow-200">
              <div className="flex items-center gap-2 mb-1">
                <Star className="h-4 w-4 text-yellow-600" />
                <span className="text-sm font-medium text-yellow-800">Avg. Rating</span>
              </div>
              <p className="text-2xl font-bold text-yellow-900">{stats.averageRating.toFixed(1)}/5</p>
            </div>
          </div>

          {/* Type Breakdown */}
          {Object.keys(stats.typeBreakdown).length > 0 && (
            <div className="border-t pt-4">
              <h4 className="text-sm font-semibold mb-3 flex items-center gap-2">
                <TrendingUp className="h-4 w-4" /> Feedback Breakdown
              </h4>
              <div className="space-y-2">
                {Object.entries(stats.typeBreakdown).map(([type, count]) => (
                  <div key={type} className="flex items-center justify-between">
                    <span className="text-sm text-gray-600 capitalize">{type}</span>
                    <Badge className={getFeedbackTypeColor(type)}>{count}</Badge>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recent Feedback */}
          {feedbacks.length > 0 && (
            <div className="border-t pt-4">
              <h4 className="text-sm font-semibold mb-3">Recent Feedback</h4>
              <div className="space-y-3 max-h-60 overflow-y-auto">
                {feedbacks.slice(0, 5).map((f) => (
                  <div key={f._id} className="p-3 bg-gray-50 rounded-lg border border-gray-200">
                    <div className="flex items-start justify-between mb-2">
                      <Badge className={getFeedbackTypeColor(f.feedback_type)}>
                        {f.feedback_type}
                      </Badge>
                      <div>{renderStars(f.rating)}</div>
                    </div>
                    <p className="text-sm text-gray-700">{f.content}</p>
                    <p className="text-xs text-gray-500 mt-2">
                      {new Date(f.created_at).toLocaleDateString()}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {feedbacks.length === 0 && !loading && (
            <div className="text-center py-6">
              <MessageSquare className="h-12 w-12 mx-auto text-gray-300 mb-2" />
              <p className="text-gray-500 text-sm">No feedback submitted yet</p>
            </div>
          )}
        </div>
      )}
    </MongoDBCard>
  );
};
