import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { TrendingUp, MapPin, Package, Leaf } from 'lucide-react';

interface AnalyticsData {
  transaction_id: number;
  distance_km: number;
  distance_source: string;
  food_name: string;
  quantity_kg: number;
  created_at: string;
}

export const AnalyticsSummary: React.FC<{ userId: string }> = ({ userId }) => {
  const [analytics, setAnalytics] = useState<AnalyticsData[]>([]);
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState({
    totalDistance: 0,
    totalFood: 0,
    totalTransactions: 0,
    avgDistance: 0,
  });

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        setLoading(true);
        const response = await fetch('/api/mongodb/analytics/redistribution', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
        });

        if (response.ok) {
          const data = await response.json();
          if (data.success && data.analytics) {
            setAnalytics(data.analytics);
            
            // Calculate summary
            const totalDistance = data.analytics.reduce((sum: number, a: AnalyticsData) => sum + (a.distance_km || 0), 0);
            const totalFood = data.analytics.reduce((sum: number, a: AnalyticsData) => sum + (a.quantity_kg || 0), 0);
            const avgDistance = data.analytics.length > 0 ? totalDistance / data.analytics.length : 0;
            
            setSummary({
              totalDistance: Math.round(totalDistance * 10) / 10,
              totalFood: Math.round(totalFood * 10) / 10,
              totalTransactions: data.analytics.length,
              avgDistance: Math.round(avgDistance * 10) / 10,
            });
          }
        }
      } catch (error) {
        console.error('Failed to fetch analytics:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, [userId]);

  if (loading) {
    return (
      <Card>
        <CardContent className="py-8">
          <div className="text-center text-gray-400">Loading analytics...</div>
        </CardContent>
      </Card>
    );
  }

  if (analytics.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-blue-600" />
            Redistribution Analytics
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-500 text-center py-4">
            No redistribution data yet. Complete transactions to see analytics.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <TrendingUp className="h-5 w-5 text-blue-600" />
          Redistribution Analytics
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
            <div className="flex items-center gap-2 mb-1">
              <MapPin className="h-4 w-4 text-blue-600" />
              <p className="text-xs font-medium text-gray-600">Total Distance</p>
            </div>
            <p className="text-2xl font-bold text-blue-900">{summary.totalDistance} km</p>
            <p className="text-xs text-gray-500 mt-1">
              Avg: {summary.avgDistance} km
            </p>
          </div>

          <div className="bg-green-50 rounded-lg p-4 border border-green-200">
            <div className="flex items-center gap-2 mb-1">
              <Package className="h-4 w-4 text-green-600" />
              <p className="text-xs font-medium text-gray-600">Food Redistributed</p>
            </div>
            <p className="text-2xl font-bold text-green-900">{summary.totalFood} kg</p>
            <p className="text-xs text-gray-500 mt-1">
              ~{Math.round(summary.totalFood * 5)} meals
            </p>
          </div>

          <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
            <div className="flex items-center gap-2 mb-1">
              <TrendingUp className="h-4 w-4 text-purple-600" />
              <p className="text-xs font-medium text-gray-600">Transactions</p>
            </div>
            <p className="text-2xl font-bold text-purple-900">{summary.totalTransactions}</p>
            <p className="text-xs text-gray-500 mt-1">Completed</p>
          </div>

          <div className="bg-amber-50 rounded-lg p-4 border border-amber-200">
            <div className="flex items-center gap-2 mb-1">
              <Leaf className="h-4 w-4 text-amber-600" />
              <p className="text-xs font-medium text-gray-600">Carbon Saved</p>
            </div>
            <p className="text-2xl font-bold text-amber-900">
              {Math.round(summary.totalDistance * 0.12 * 10) / 10} kg
            </p>
            <p className="text-xs text-gray-500 mt-1">CO₂</p>
          </div>
        </div>

        <div className="space-y-2">
          <h3 className="text-sm font-semibold text-gray-700 mb-2">Recent Activity</h3>
          {analytics.slice(0, 5).map((item, index) => (
            <div
              key={index}
              className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200"
            >
              <div className="flex-1">
                <p className="font-medium text-sm">{item.food_name}</p>
                <p className="text-xs text-gray-500">
                  {new Date(item.created_at).toLocaleDateString()} • {item.quantity_kg} kg
                </p>
              </div>
              <div className="text-right">
                <p className="text-sm font-semibold text-blue-700">{item.distance_km.toFixed(1)} km</p>
                <p className="text-xs text-gray-500">
                  {item.distance_source === 'osrm' ? '🗺️ Map' : '📍 Est'}
                </p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default AnalyticsSummary;
