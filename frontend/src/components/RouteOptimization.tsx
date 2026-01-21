import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Map, Truck, Clock, Leaf, TrendingUp } from 'lucide-react';
import { api } from '@/lib/api';
import { io, Socket } from 'socket.io-client';

const API_BASE = 'http://127.0.0.1:5000';

interface RouteOptimizationData {
  total_distance_km: number;
  estimated_time_hours: number;
  vehicle_recommendation: string;
  distance_source: string;
  estimated_cost_currency?: number;
  delivery_window?: string;
  metrics?: {
    fuel_consumed_liters: number;
    carbon_saved_kg: number;
    efficiency_score: number;
    meals_impacted: number;
  };
}

interface RouteOptimizationProps {
  transactionId?: string | number;
  donorId?: number;
  receiverId?: number;
  showFull?: boolean; // Show full card vs compact view
}

export const RouteOptimization: React.FC<RouteOptimizationProps> = ({
  transactionId,
  donorId,
  receiverId,
  showFull = true,
}) => {
  const [routeData, setRouteData] = useState<RouteOptimizationData | null>(null);
  const [loading, setLoading] = useState(true);
  const [fallbackUsed, setFallbackUsed] = useState(false);
  const [socket, setSocket] = useState<Socket | null>(null);

  const mapRouteData = (txn: any): RouteOptimizationData | null => {
    const rd = txn?.route_data?.route;
    const rm = txn?.route_data?.metrics;
    if (!rd) return null;
    return {
      total_distance_km: rd.total_distance_km ?? 0,
      estimated_time_hours: rd.estimated_time_hours ?? 0,
      vehicle_recommendation: rd.vehicle_recommendation ?? "auto",
      distance_source: rd.distance_source ?? "haversine",
      estimated_cost_currency: rd.estimated_cost_currency,
      delivery_window: rd.delivery_window,
      metrics: rm || undefined,
    };
  };

  useEffect(() => {
    const fetchRouteOptimization = async () => {
      try {
        setLoading(true);
        setFallbackUsed(false);
        let foundRoute = false;
        
        console.log('🗺️ [RouteOptimization] Starting fetch, transactionId:', transactionId);
        
        // Always fetch latest transactions to ensure we get the most recent route
        console.log('🗺️ [RouteOptimization] Fetching all user transactions...');
        try {
          const response = await fetch(`${API_BASE}/api/mongodb/transactions`, {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('token') || ''}`,
            },
          });
          console.log('🗺️ [RouteOptimization] Response status:', response.status);
          
          if (response.ok) {
            const text = await response.text();
            let data;
            try {
              data = JSON.parse(text);
            } catch (e) {
              console.error('❌ [RouteOptimization] Failed to parse JSON:', text.substring(0, 200));
              return;
            }
            console.log('🗺️ [RouteOptimization] Response data:', data);
            console.log('🗺️ [RouteOptimization] Number of transactions:', data.transactions?.length || 0);
            
            // If transactionId provided, try to find that specific transaction first
            if (transactionId) {
              const specificTxn = (data.transactions || []).find(
                (t: any) => t.txn_id === transactionId || t._id === transactionId
              );
              if (specificTxn && specificTxn.route_data?.route) {
                const mapped = mapRouteData(specificTxn);
                if (mapped) {
                  console.log('✅ [RouteOptimization] Setting route data from specific transaction');
                  setRouteData(mapped);
                  foundRoute = true;
                }
              }
            }
            
            // If no specific transaction found or no transactionId, use most recent with route_data
            if (!foundRoute) {
              const transactionsWithRoutes = (data.transactions || []).filter(
                (t: any) => t?.route_data?.route
              );
              
              // Sort by created_at or _id to get the most recent
              transactionsWithRoutes.sort((a: any, b: any) => {
                const timeA = a.created_at ? new Date(a.created_at).getTime() : 0;
                const timeB = b.created_at ? new Date(b.created_at).getTime() : 0;
                return timeB - timeA; // Descending order (newest first)
              });
              
              const mostRecentWithRoute = transactionsWithRoutes[0];
              console.log('🗺️ [RouteOptimization] Most recent transaction with route:', mostRecentWithRoute);
              
              if (mostRecentWithRoute) {
                const mapped = mapRouteData(mostRecentWithRoute);
                console.log('🗺️ [RouteOptimization] Mapped route:', mapped);
                if (mapped) {
                  console.log('✅ [RouteOptimization] Setting route data from most recent transaction');
                  setRouteData(mapped);
                  setFallbackUsed(!transactionId);
                  foundRoute = true;
                }
              } else {
                console.warn('⚠️ [RouteOptimization] No transactions with route_data found');
              }
            }
          }
        } catch (err) {
          console.error('❌ [RouteOptimization] Route fetch failed', err);
        }
      } catch (error) {
        console.error('❌ [RouteOptimization] Failed to fetch route optimization:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchRouteOptimization();
  }, [transactionId]);

  // Socket.IO listener for real-time route updates
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) return;

    const newSocket = io('http://127.0.0.1:5000', {
      transports: ['polling'],
      withCredentials: true,
      query: { token },
      auth: { token },
      reconnection: true,
      reconnectionAttempts: 5,
    });

    newSocket.on('connect', () => {
      console.log('✅ [RouteOptimization] Connected to Socket.IO');
    });

    // Listen for transaction creation and refresh route data
    newSocket.on('transaction_created', (data: any) => {
      console.log('🔄 [RouteOptimization] Transaction created event received:', data);
      // Reload route optimization data when a new transaction is created
      if (transactionId || true) {
        // Force reload by calling the fetch logic again
        const reloadRoute = async () => {
          try {
            const response = await fetch(
              `${API_BASE}/api/mongodb/transactions`,
              {
                headers: {
                  'Authorization': `Bearer ${localStorage.getItem('token')}`,
                },
              }
            );
            if (response.ok) {
              const text = await response.text();
              const result = JSON.parse(text);
              const firstWithRoute = (result.transactions || []).find(
                (t: any) => t?.route_data?.route
              );
              if (firstWithRoute) {
                const mapped = mapRouteData(firstWithRoute);
                if (mapped) {
                  console.log('✅ [RouteOptimization] Updated route after transaction_created');
                  setRouteData(mapped);
                }
              }
            }
          } catch (err) {
            console.error('❌ [RouteOptimization] Failed to reload route:', err);
          }
        };
        reloadRoute();
      }
    });

    // Listen for transaction updates
    newSocket.on('transaction_updated', (data: any) => {
      console.log('🔄 [RouteOptimization] Transaction updated event received:', data);
      // Similar reload logic for transaction updates
      if (transactionId || true) {
        const reloadRoute = async () => {
          try {
            const response = await fetch(
              `${API_BASE}/api/mongodb/transactions`,
              {
                headers: {
                  'Authorization': `Bearer ${localStorage.getItem('token')}`,
                },
              }
            );
            if (response.ok) {
              const text = await response.text();
              const result = JSON.parse(text);
              const firstWithRoute = (result.transactions || []).find(
                (t: any) => t?.route_data?.route
              );
              if (firstWithRoute) {
                const mapped = mapRouteData(firstWithRoute);
                if (mapped) {
                  console.log('✅ [RouteOptimization] Updated route after transaction_updated');
                  setRouteData(mapped);
                }
              }
            }
          } catch (err) {
            console.error('❌ [RouteOptimization] Failed to reload route:', err);
          }
        };
        reloadRoute();
      }
    });

    setSocket(newSocket);

    return () => {
      newSocket.disconnect();
    };
  }, [transactionId]);

  if (loading) {
    return (
      <Card className="bg-gradient-to-br from-blue-50 to-indigo-50">
        <CardContent className="py-8 flex justify-center">
          <div className="animate-pulse text-gray-400">Loading route optimization...</div>
        </CardContent>
      </Card>
    );
  }

  if (!routeData) {
    return (
      <Card className="bg-gradient-to-br from-blue-50 to-indigo-50">
        <CardContent className="py-6">
          <p className="text-sm text-blue-900">
            No route data is available yet for this delivery.
          </p>
        </CardContent>
      </Card>
    );
  }

  if (!showFull) {
    // Compact view
    return (
      <div className="flex items-center gap-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
        <Map className="h-5 w-5 text-blue-600" />
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-700">
            {routeData.total_distance_km.toFixed(1)} km distance
          </p>
          <p className="text-xs text-gray-500">
            ~{routeData.estimated_time_hours.toFixed(1)}h delivery • {routeData.distance_source === 'osrm' ? '🗺️ Map API' : '📍 Est.'}
          </p>
        </div>
        {routeData.metrics?.carbon_saved_kg && (
          <div className="flex items-center gap-1">
            <Leaf className="h-4 w-4 text-green-600" />
            <span className="text-xs font-semibold text-green-700">
              {routeData.metrics.carbon_saved_kg.toFixed(1)}kg CO₂ saved
            </span>
          </div>
        )}
      </div>
    );
  }

  // Full card view
  return (
    <Card className="bg-gradient-to-br from-blue-50 to-indigo-50 border-2 border-blue-200">
      <CardHeader>
        <div className="flex items-center gap-2">
          <Map className="h-5 w-5 text-blue-600" />
          <CardTitle className="text-lg text-blue-900">Route Optimization</CardTitle>
          <Badge variant="secondary" className="ml-auto">
            {routeData.distance_source === 'osrm' ? '🗺️ Map API' : '📍 Estimated'}
          </Badge>
          {fallbackUsed && (
            <Badge variant="outline" className="ml-2">Last completed</Badge>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Distance & Time */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-white rounded-lg p-4 border border-blue-100">
            <div className="flex items-center gap-2 mb-2">
              <Map className="h-4 w-4 text-blue-600" />
              <p className="text-sm font-medium text-gray-600">Distance</p>
            </div>
            <p className="text-2xl font-bold text-blue-900">
              {routeData.total_distance_km.toFixed(1)} km
            </p>
            <p className="text-xs text-gray-500 mt-1">Optimal route</p>
          </div>

          <div className="bg-white rounded-lg p-4 border border-blue-100">
            <div className="flex items-center gap-2 mb-2">
              <Clock className="h-4 w-4 text-orange-600" />
              <p className="text-sm font-medium text-gray-600">Estimated Time</p>
            </div>
            <p className="text-2xl font-bold text-orange-900">
              {routeData.estimated_time_hours.toFixed(1)}h
            </p>
            <p className="text-xs text-gray-500 mt-1">
              {routeData.delivery_window || 'Standard delivery'}
            </p>
          </div>
        </div>

        {/* Metrics */}
        {routeData.metrics && (
          <div className="bg-white rounded-lg p-4 border border-green-100">
            <div className="flex items-center gap-2 mb-4">
              <Leaf className="h-4 w-4 text-green-600" />
              <p className="font-medium text-gray-700">Environmental Impact</p>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-gray-500 mb-1">Carbon Saved</p>
                <p className="text-lg font-bold text-green-700">
                  {routeData.metrics.carbon_saved_kg.toFixed(1)} kg CO₂
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500 mb-1">Fuel Used</p>
                <p className="text-lg font-bold text-amber-700">
                  {routeData.metrics.fuel_consumed_liters.toFixed(2)}L
                </p>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4 mt-4">
              <div>
                <p className="text-xs text-gray-500 mb-1">Efficiency Score</p>
                <div className="flex items-center gap-2">
                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all"
                      style={{ width: `${routeData.metrics.efficiency_score}%` }}
                    />
                  </div>
                  <p className="text-sm font-bold text-blue-700">
                    {routeData.metrics.efficiency_score.toFixed(0)}%
                  </p>
                </div>
              </div>
              <div>
                <p className="text-xs text-gray-500 mb-1">Meals Impacted</p>
                <p className="text-lg font-bold text-purple-700">
                  {routeData.metrics.meals_impacted}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Vehicle & Cost */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-white rounded-lg p-4 border border-blue-100">
            <div className="flex items-center gap-2 mb-2">
              <Truck className="h-4 w-4 text-indigo-600" />
              <p className="text-sm font-medium text-gray-600">Vehicle</p>
            </div>
            <p className="font-semibold text-indigo-900 capitalize">
              {routeData.vehicle_recommendation}
            </p>
            <p className="text-xs text-gray-500 mt-1">Recommended</p>
          </div>

          {routeData.estimated_cost_currency && (
            <div className="bg-white rounded-lg p-4 border border-blue-100">
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp className="h-4 w-4 text-green-600" />
                <p className="text-sm font-medium text-gray-600">Est. Cost</p>
              </div>
              <p className="font-semibold text-green-900">
                ${routeData.estimated_cost_currency.toFixed(2)}
              </p>
              <p className="text-xs text-gray-500 mt-1">Delivery cost</p>
            </div>
          )}
        </div>

        {/* Info Footer */}
        <div className="bg-blue-100 rounded-lg p-3 border border-blue-200">
          <p className="text-xs text-blue-900">
            ℹ️ Route optimized using{' '}
            <strong>
              {routeData.distance_source === 'osrm'
                ? 'OSRM Map API for actual road distances'
                : 'location-based estimation'}
            </strong>
            . Real-time tracking available on map view.
          </p>
        </div>
      </CardContent>
    </Card>
  );
};

export default RouteOptimization;
