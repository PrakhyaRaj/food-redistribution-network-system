import React, { useState, useEffect } from 'react';
import { MongoDBCard } from './MongoDBCard';
import { api, AnalyticsSummary } from '@/lib/api';
import { TrendingUp, TrendingDown, Users, Leaf, Package } from 'lucide-react';
import { Badge } from '@/components/ui/badge';

export const AnalyticsDashboard: React.FC = () => {
  const [analytics, setAnalytics] = useState<AnalyticsSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      const data = await api.mongodb.getAnalytics(); // Use mongodb.getAnalytics
      setAnalytics(data.summary || data);
    } catch (error) {
      console.error('Failed to load analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <MongoDBCard title="Food Redistribution Analytics" icon="📈">
      {loading ? (
        <div className="flex justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
      ) : analytics ? (
        <div className="space-y-4">
          <div className="bg-gradient-to-r from-green-50 to-emerald-50 p-4 rounded-lg border border-green-200">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-semibold text-green-800 flex items-center gap-2">
                <Package className="h-4 w-4" />
                🍲 Food Saved
              </h4>
              <Badge variant="outline" className="bg-green-100 text-green-800">
                {analytics.total_food_saved_kg >= 1000 
                  ? `${(analytics.total_food_saved_kg / 1000).toFixed(1)} tons` 
                  : `${analytics.total_food_saved_kg} kg`}
              </Badge>
            </div>
            <p className="text-3xl font-bold text-green-900">
              {analytics.total_food_saved_kg} kg
            </p>
            <p className="text-sm text-green-700 mt-1 flex items-center gap-1">
              <Users className="h-3 w-3" />
              ≈ {analytics.total_people_fed} people fed
            </p>
          </div>
          
          <div className="bg-gradient-to-r from-blue-50 to-cyan-50 p-4 rounded-lg border border-blue-200">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-semibold text-blue-800 flex items-center gap-2">
                <Leaf className="h-4 w-4" />
                🌱 Carbon Saved
              </h4>
              <Badge variant="outline" className="bg-blue-100 text-blue-800">
                {analytics.total_carbon_saved >= 1000 
                  ? `${(analytics.total_carbon_saved / 1000).toFixed(1)} tons` 
                  : `${analytics.total_carbon_saved} kg`}
              </Badge>
            </div>
            <p className="text-3xl font-bold text-blue-900">
              {analytics.total_carbon_saved} kg CO₂
            </p>
            <p className="text-sm text-blue-700 mt-1">
              Equivalent to {Math.round(analytics.total_carbon_saved / 22)} trees planted
            </p>
          </div>
          
          {analytics.weekly_trend !== undefined && (
            <div className="bg-gradient-to-r from-yellow-50 to-amber-50 p-4 rounded-lg border border-yellow-200">
              <div className="flex items-center justify-between">
                <span className="font-medium">📈 Weekly Trend</span>
                <Badge 
                  variant={analytics.weekly_trend > 0 ? "default" : "secondary"}
                  className="flex items-center gap-1"
                >
                  {analytics.weekly_trend > 0 ? (
                    <TrendingUp className="h-3 w-3" />
                  ) : (
                    <TrendingDown className="h-3 w-3" />
                  )}
                  {analytics.weekly_trend > 0 ? '+' : ''}{analytics.weekly_trend}%
                </Badge>
              </div>
              <p className="text-sm text-gray-600 mt-2">
                {analytics.weekly_trend > 0 
                  ? 'Positive growth this week!'
                  : 'Looking for improvement this week'}
              </p>
            </div>
          )}
        </div>
      ) : (
        <div className="text-center py-8">
          <Package className="h-12 w-12 mx-auto text-gray-300 mb-3" />
          <p className="text-gray-500">No analytics data</p>
          <p className="text-sm text-gray-400 mt-1">
            Analytics will appear when data is available
          </p>
        </div>
      )}
    </MongoDBCard>
  );
};