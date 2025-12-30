// frontend/src/components/profile/ProfileFeedback.tsx
import React, { useState, useEffect } from 'react';
import { Star, MessageSquare, TrendingUp, Award } from 'lucide-react';
import { Badge } from '@/components/ui/badge';

interface Feedback {
  _id: string;
  user_id: string;
  rating: number;
  feedback_type: string;
  content: string;
  created_at: string;
}

interface FeedbackStats {
  totalFeedback: number;
  averageRating: number;
  typeBreakdown: Record<string, number>;
}

const API_BASE = 'http://127.0.0.1:5000';

const getHeaders = () => {
  const token = localStorage.getItem("token") || localStorage.getItem("access_token");
  return {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` })
  };
};

export const ProfileFeedback: React.FC<{ userId?: string }> = ({ userId }) => {
  const [feedbacks, setFeedbacks] = useState<Feedback[]>([]);
  const [stats, setStats] = useState<FeedbackStats>({
    totalFeedback: 0,
    averageRating: 0,
    typeBreakdown: {}
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadFeedback();
  }, [userId]);

  const loadFeedback = async () => {
    try {
      setLoading(true);
      
      // Get user feedback
      const endpoint = userId ? `/api/feedback/user/${userId}` : '/api/feedback/my';
      
      const response = await fetch(`${API_BASE}${endpoint}`, {
        headers: getHeaders()
      });

      if (response.ok) {
        const data = await response.json();
        const feedbackList = data.feedbacks || data.feedback || [];
        setFeedbacks(feedbackList);

        // Calculate stats
        const totalFeedback = feedbackList.length;
        const averageRating =
          totalFeedback > 0
            ? feedbackList.reduce((sum: number, f: Feedback) => sum + f.rating, 0) / totalFeedback
            : 0;

        const typeBreakdown: Record<string, number> = {};
        feedbackList.forEach((f: Feedback) => {
          typeBreakdown[f.feedback_type] = (typeBreakdown[f.feedback_type] || 0) + 1;
        });

        setStats({
          totalFeedback,
          averageRating: Math.round(averageRating * 10) / 10,
          typeBreakdown
        });
      }
    } catch (error) {
      console.error('Error loading feedback:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRatingColor = (rating: number) => {
    if (rating >= 4.5) return 'text-green-600';
    if (rating >= 3.5) return 'text-blue-600';
    if (rating >= 2.5) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getFeedbackTypeBadgeColor = (type: string) => {
    switch (type) {
      case 'positive':
        return 'bg-green-100 text-green-800';
      case 'negative':
        return 'bg-red-100 text-red-800';
      case 'neutral':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-blue-100 text-blue-800';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <div className="mb-4">
            <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-gray-300 border-t-blue-600"></div>
          </div>
          <p className="text-gray-600">Loading feedback...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Rating Summary */}
      <div className="rounded-lg bg-gradient-to-br from-purple-50 to-blue-50 p-6 border border-purple-200">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Award className="h-5 w-5" />
          Community Rating
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Average Rating */}
          <div className="text-center">
            <div className={`text-5xl font-bold ${getRatingColor(stats.averageRating)} mb-2`}>
              {stats.averageRating.toFixed(1)}
            </div>
            <div className="flex justify-center gap-1 mb-2">
              {[...Array(5)].map((_, i) => (
                <Star
                  key={i}
                  size={16}
                  className={
                    i < Math.round(stats.averageRating)
                      ? 'fill-yellow-400 text-yellow-400'
                      : 'text-gray-300'
                  }
                />
              ))}
            </div>
            <p className="text-sm text-gray-600">
              Based on {stats.totalFeedback} rating{stats.totalFeedback !== 1 ? 's' : ''}
            </p>
          </div>

          {/* Feedback Breakdown */}
          <div>
            <p className="font-semibold text-sm mb-3 text-gray-700">Feedback Types</p>
            <div className="space-y-2">
              {Object.entries(stats.typeBreakdown).map(([type, count]) => (
                <div key={type} className="flex items-center justify-between text-sm">
                  <span className="text-gray-600 capitalize">{type}</span>
                  <Badge variant="outline">{count}</Badge>
                </div>
              ))}
            </div>
          </div>

          {/* Stats */}
          <div>
            <p className="font-semibold text-sm mb-3 text-gray-700">Statistics</p>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Total Feedback</span>
                <span className="font-medium">{stats.totalFeedback}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Avg Rating</span>
                <span className="font-medium">{stats.averageRating}/5</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Positive %</span>
                <span className="font-medium">
                  {stats.totalFeedback > 0
                    ? Math.round(
                        ((stats.typeBreakdown['positive'] || 0) / stats.totalFeedback) * 100
                      )
                    : 0}
                  %
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Feedback */}
      <div>
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <MessageSquare className="h-5 w-5" />
          Recent Feedback ({feedbacks.length})
        </h3>

        {feedbacks.length === 0 ? (
          <div className="text-center py-8 rounded-lg border border-gray-200 bg-gray-50">
            <MessageSquare className="mx-auto h-12 w-12 text-gray-300 mb-3" />
            <p className="text-gray-600">No feedback yet</p>
            <p className="text-sm text-gray-500 mt-1">
              Feedback from other users will appear here
            </p>
          </div>
        ) : (
          <div className="space-y-4 max-h-96 overflow-y-auto">
            {feedbacks.map((feedback) => (
              <div
                key={feedback._id}
                className="rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow"
              >
                {/* Header */}
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <div className="flex gap-0.5">
                      {[...Array(5)].map((_, i) => (
                        <Star
                          key={i}
                          size={16}
                          className={
                            i < feedback.rating
                              ? 'fill-yellow-400 text-yellow-400'
                              : 'text-gray-300'
                          }
                        />
                      ))}
                    </div>
                    <span className="font-semibold">{feedback.rating}/5</span>
                  </div>
                  <Badge className={getFeedbackTypeBadgeColor(feedback.feedback_type)}>
                    {feedback.feedback_type}
                  </Badge>
                </div>

                {/* Content */}
                <p className="text-gray-700 mb-3">{feedback.content}</p>

                {/* Date */}
                <p className="text-xs text-gray-500">
                  {new Date(feedback.created_at).toLocaleDateString('en-US', {
                    month: 'short',
                    day: 'numeric',
                    year: 'numeric'
                  })}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
