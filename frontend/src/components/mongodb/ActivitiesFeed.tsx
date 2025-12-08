import React, { useState, useEffect } from 'react';
import { MongoDBCard } from './MongoDBCard';
import { api, Activity } from '@/lib/api';
import { Loader2, Clock, User, CheckCircle, AlertCircle } from 'lucide-react';

export const ActivitiesFeed: React.FC = () => {
  const [activities, setActivities] = useState<Activity[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadActivities();
  }, []);

  const loadActivities = async () => {
    try {
      setLoading(true);
      const data = await api.mongodb.getActivities(10); // Use mongodb.getActivities
      setActivities(data.activities || data || []);
    } catch (error) {
      console.error('Failed to load activities:', error);
    } finally {
      setLoading(false);
    }
  };

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'login_success':
        return <User className="h-4 w-4 text-green-500" />;
      case 'feedback_submitted':
        return <CheckCircle className="h-4 w-4 text-blue-500" />;
      case 'food_image_uploaded':
        return <AlertCircle className="h-4 w-4 text-yellow-500" />;
      case 'route_optimized':
        return <CheckCircle className="h-4 w-4 text-purple-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  const formatActivityType = (type: string): string => {
    const types: Record<string, string> = {
      'login_success': 'User logged in',
      'feedback_submitted': 'Feedback submitted',
      'food_image_uploaded': 'Food image uploaded',
      'route_optimized': 'Route optimized',
      'food_added': 'Food donation added',
      'request_created': 'Food request created',
      'transaction_completed': 'Transaction completed',
      'profile_updated': 'Profile updated'
    };
    return types[type] || type.replace(/_/g, ' ');
  };

  return (
    <MongoDBCard title="Recent Activities" icon="📝">
      {loading ? (
        <div className="flex justify-center py-4">
          <Loader2 className="h-6 w-6 animate-spin text-blue-500" />
        </div>
      ) : activities.length > 0 ? (
        <div className="space-y-3 max-h-80 overflow-y-auto pr-2">
          {activities.map((activity) => (
            <div 
              key={activity._id}
              className="flex items-start gap-3 p-3 bg-white border rounded hover:bg-gray-50 transition"
            >
              <div className="mt-1">
                {getActivityIcon(activity.activity_type)}
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-medium text-sm truncate">
                  {formatActivityType(activity.activity_type)}
                </p>
                {activity.details && (
                  <p className="text-xs text-gray-600 truncate">
                    {typeof activity.details === 'string' 
                      ? activity.details 
                      : JSON.stringify(activity.details)}
                  </p>
                )}
                <div className="flex items-center gap-2 mt-1">
                  <Clock className="h-3 w-3 text-gray-400" />
                  <p className="text-xs text-gray-500">
                    {new Date(activity.created_at).toLocaleString()}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-8">
          <Clock className="h-12 w-12 mx-auto text-gray-300 mb-3" />
          <p className="text-gray-500">No activities yet</p>
          <p className="text-sm text-gray-400 mt-1">
            User activities will appear here
          </p>
        </div>
      )}
    </MongoDBCard>
  );
};