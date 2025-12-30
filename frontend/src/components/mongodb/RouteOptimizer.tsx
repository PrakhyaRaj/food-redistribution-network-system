import React, { useState, useEffect } from 'react';
import { MongoDBCard } from './MongoDBCard';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Loader2, Navigation, MapPin, Package, Clock, Trash2 } from 'lucide-react';
import { api } from '@/lib/api';
import { io, Socket } from 'socket.io-client';

interface RoutePoint {
  lat: number;
  lng: number;
  weight: number;
  timeSlot: string;
}

interface RouteMetrics {
  total_distance_km: number;
  estimated_time_hours: number;
  efficiency_score: number;
  fuel_saved_liters?: number;
  stops_optimized?: number;
}

interface RouteResult {
  metrics: RouteMetrics;
  optimized_path: Array<{
    type: 'pickup' | 'delivery';
    location: [number, number];
    weight_kg: number;
    time_window: string;
  }>;
  original_distance?: number;
  time_saved_hours?: number;
}

export const RouteOptimizer: React.FC = () => {
  const [pickupPoints, setPickupPoints] = useState<RoutePoint[]>([
    { lat: 23.76, lng: 76.34, weight: 50, timeSlot: "9-12" }
  ]);
  const [deliveryPoints, setDeliveryPoints] = useState<RoutePoint[]>([
    { lat: 23.77, lng: 76.35, weight: 50, timeSlot: "13-16" }
  ]);
  const [optimizing, setOptimizing] = useState(false);
  const [routeResult, setRouteResult] = useState<RouteResult | null>(null);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [socket, setSocket] = useState<Socket | null>(null);

  // Set up Socket.IO listener for real-time updates
  useEffect(() => {
    const token = localStorage.getItem('token');
    const newSocket = io('http://127.0.0.1:5000', {
      transports: ['polling'],
      withCredentials: true,
      query: { token },
      auth: { token },
      reconnection: true,
      reconnectionAttempts: 5,
    });

    newSocket.on('transaction_created', () => {
      console.log('🗺️ Route Optimizer: Transaction detected, route may need reoptimization');
      // Clear previous results to prompt re-optimization
      setRouteResult(null);
    });

    newSocket.on('food_added', () => {
      console.log('🗺️ Route Optimizer: New food item, route may need reoptimization');
      setRouteResult(null);
    });

    setSocket(newSocket);

    return () => {
      if (newSocket) {
        newSocket.disconnect();
      }
    };
  }, []);

  const addPickupPoint = () => {
    setPickupPoints([
      ...pickupPoints,
      { lat: 23.76 + (pickupPoints.length * 0.01), lng: 76.34, weight: 20, timeSlot: "9-12" }
    ]);
  };

  const removePickupPoint = (index: number) => {
    if (pickupPoints.length > 1) {
      setPickupPoints(pickupPoints.filter((_, i) => i !== index));
    }
  };

  const addDeliveryPoint = () => {
    setDeliveryPoints([
      ...deliveryPoints,
      { lat: 23.77 + (deliveryPoints.length * 0.01), lng: 76.35, weight: 20, timeSlot: "13-16" }
    ]);
  };

  const removeDeliveryPoint = (index: number) => {
    if (deliveryPoints.length > 1) {
      setDeliveryPoints(deliveryPoints.filter((_, i) => i !== index));
    }
  };

  const updatePoint = (
    index: number,
    field: keyof RoutePoint,
    value: string | number,
    isPickup: boolean
  ) => {
    const points = isPickup ? [...pickupPoints] : [...deliveryPoints];
    points[index] = { ...points[index], [field]: value };
    if (isPickup) {
      setPickupPoints(points);
    } else {
      setDeliveryPoints(points);
    }
  };

  const optimizeRoute = async () => {
    try {
      setOptimizing(true);
      
      // Format data for API - Type assertion ensures correct tuple type
      const routeData = {
        pickup_points: pickupPoints.map(p => [p.lat, p.lng, p.weight, p.timeSlot] as [number, number, number, string]),
        delivery_points: deliveryPoints.map(p => [p.lat, p.lng, p.weight, p.timeSlot] as [number, number, number, string]),
        algorithm: "genetic",
        constraints: {
          max_distance_km: 100,
          time_windows: true,
          vehicle_capacity_kg: 500
        }
      };

      console.log('Route optimization data:', routeData);
      const data = await api.mongodb.optimizeRoute(routeData);
      setRouteResult(data.optimized_route || data);
    } catch (error) {
      console.error('Route optimization failed:', error);
    } finally {
      setOptimizing(false);
    }
  };

  const resetPoints = () => {
    setPickupPoints([{ lat: 23.76, lng: 76.34, weight: 50, timeSlot: "9-12" }]);
    setDeliveryPoints([{ lat: 23.77, lng: 76.35, weight: 50, timeSlot: "13-16" }]);
    setRouteResult(null);
  };

  const getEfficiencyColor = (score: number) => {
    if (score >= 90) return "text-green-600";
    if (score >= 75) return "text-yellow-600";
    return "text-red-600";
  };

  const getEfficiencyBadge = (score: number) => {
    if (score >= 90) return "bg-green-100 text-green-800";
    if (score >= 75) return "bg-yellow-100 text-yellow-800";
    return "bg-red-100 text-red-800";
  };

  return (
    <MongoDBCard title="Route Optimization (AI)" icon="🗺️">
      <div className="space-y-6">
        {/* Input Section */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold flex items-center gap-2">
              <Package className="h-4 w-4" />
              Pickup Points ({pickupPoints.length})
            </h3>
            <div className="flex gap-2">
              <Button size="sm" variant="outline" onClick={addPickupPoint}>
                + Add
              </Button>
              {pickupPoints.length > 1 && (
                <Button size="sm" variant="outline" onClick={() => removePickupPoint(pickupPoints.length - 1)}>
                  <Trash2 className="h-3 w-3" />
                </Button>
              )}
            </div>
          </div>
          
          {pickupPoints.map((point, index) => (
            <div key={`pickup-${index}`} className="grid grid-cols-2 md:grid-cols-5 gap-2 p-3 bg-white border rounded">
              <div>
                <Label className="text-xs">Latitude</Label>
                <Input
                  type="number"
                  step="0.0001"
                  value={point.lat}
                  onChange={(e) => updatePoint(index, 'lat', parseFloat(e.target.value) || 0, true)}
                  className="h-8 text-sm"
                />
              </div>
              <div>
                <Label className="text-xs">Longitude</Label>
                <Input
                  type="number"
                  step="0.0001"
                  value={point.lng}
                  onChange={(e) => updatePoint(index, 'lng', parseFloat(e.target.value) || 0, true)}
                  className="h-8 text-sm"
                />
              </div>
              <div>
                <Label className="text-xs">Weight (kg)</Label>
                <Input
                  type="number"
                  value={point.weight}
                  onChange={(e) => updatePoint(index, 'weight', parseInt(e.target.value) || 0, true)}
                  className="h-8 text-sm"
                />
              </div>
              <div>
                <Label className="text-xs">Time Slot</Label>
                <Input
                  value={point.timeSlot}
                  onChange={(e) => updatePoint(index, 'timeSlot', e.target.value, true)}
                  className="h-8 text-sm"
                />
              </div>
              {pickupPoints.length > 1 && (
                <div className="flex items-end">
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => removePickupPoint(index)}
                    className="h-8"
                  >
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </div>
              )}
            </div>
          ))}

          <div className="flex items-center justify-between mt-6">
            <h3 className="font-semibold flex items-center gap-2">
              <MapPin className="h-4 w-4" />
              Delivery Points ({deliveryPoints.length})
            </h3>
            <div className="flex gap-2">
              <Button size="sm" variant="outline" onClick={addDeliveryPoint}>
                + Add
              </Button>
              {deliveryPoints.length > 1 && (
                <Button size="sm" variant="outline" onClick={() => removeDeliveryPoint(deliveryPoints.length - 1)}>
                  <Trash2 className="h-3 w-3" />
                </Button>
              )}
            </div>
          </div>
          
          {deliveryPoints.map((point, index) => (
            <div key={`delivery-${index}`} className="grid grid-cols-2 md:grid-cols-5 gap-2 p-3 bg-white border rounded">
              <div>
                <Label className="text-xs">Latitude</Label>
                <Input
                  type="number"
                  step="0.0001"
                  value={point.lat}
                  onChange={(e) => updatePoint(index, 'lat', parseFloat(e.target.value) || 0, false)}
                  className="h-8 text-sm"
                />
              </div>
              <div>
                <Label className="text-xs">Longitude</Label>
                <Input
                  type="number"
                  step="0.0001"
                  value={point.lng}
                  onChange={(e) => updatePoint(index, 'lng', parseFloat(e.target.value) || 0, false)}
                  className="h-8 text-sm"
                />
              </div>
              <div>
                <Label className="text-xs">Weight (kg)</Label>
                <Input
                  type="number"
                  value={point.weight}
                  onChange={(e) => updatePoint(index, 'weight', parseInt(e.target.value) || 0, false)}
                  className="h-8 text-sm"
                />
              </div>
              <div>
                <Label className="text-xs">Time Slot</Label>
                <Input
                  value={point.timeSlot}
                  onChange={(e) => updatePoint(index, 'timeSlot', e.target.value, false)}
                  className="h-8 text-sm"
                />
              </div>
              {deliveryPoints.length > 1 && (
                <div className="flex items-end">
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => removeDeliveryPoint(index)}
                    className="h-8"
                  >
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3">
          <Button 
            onClick={optimizeRoute} 
            disabled={optimizing || pickupPoints.length === 0 || deliveryPoints.length === 0}
            className="flex-1"
          >
            {optimizing ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Optimizing with AI...
              </>
            ) : (
              <>
                <Navigation className="h-4 w-4 mr-2" />
                Optimize Route
              </>
            )}
          </Button>
          
          <Button
            variant="outline"
            onClick={resetPoints}
            className="flex-none"
          >
            Reset
          </Button>
        </div>

        {/* Advanced Options Toggle */}
        <Button
          variant="ghost"
          size="sm"
          className="w-full text-xs"
          onClick={() => setShowAdvanced(!showAdvanced)}
        >
          {showAdvanced ? 'Hide' : 'Show'} Advanced Options
        </Button>

        {showAdvanced && (
          <div className="p-3 bg-blue-50 border border-blue-200 rounded space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm">Algorithm:</span>
              <Badge variant="outline">Genetic Algorithm</Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Vehicle Capacity:</span>
              <Badge variant="outline">500 kg</Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Time Windows:</span>
              <Badge variant="outline">Enabled</Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Max Distance:</span>
              <Badge variant="outline">100 km</Badge>
            </div>
          </div>
        )}

        {/* Results Section */}
        {routeResult && (
          <div className="space-y-4 p-4 bg-gradient-to-r from-blue-50 to-green-50 border rounded-lg">
            <h3 className="font-semibold text-lg flex items-center gap-2">
              <Navigation className="h-5 w-5" />
              Optimization Results
            </h3>
            
            {/* Main Metrics */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <div className="bg-white p-3 rounded border text-center">
                <p className="text-xs text-gray-500 mb-1">📏 Distance</p>
                <p className="text-xl font-bold">
                  {routeResult.metrics.total_distance_km.toFixed(1)} km
                </p>
                {routeResult.original_distance && (
                  <p className="text-xs text-green-600">
                    ↓ {((routeResult.original_distance - routeResult.metrics.total_distance_km) / routeResult.original_distance * 100).toFixed(0)}%
                  </p>
                )}
              </div>
              
              <div className="bg-white p-3 rounded border text-center">
                <p className="text-xs text-gray-500 mb-1 flex items-center justify-center gap-1">
                  <Clock className="h-3 w-3" /> Time
                </p>
                <p className="text-xl font-bold">
                  {routeResult.metrics.estimated_time_hours.toFixed(1)} hrs
                </p>
                {routeResult.time_saved_hours && (
                  <p className="text-xs text-green-600">
                    Save {routeResult.time_saved_hours.toFixed(1)} hrs
                  </p>
                )}
              </div>
              
              <div className="bg-white p-3 rounded border text-center">
                <p className="text-xs text-gray-500 mb-1">🌿 Efficiency</p>
                <p className={`text-xl font-bold ${getEfficiencyColor(routeResult.metrics.efficiency_score)}`}>
                  {routeResult.metrics.efficiency_score}%
                </p>
                <Badge className={`text-xs ${getEfficiencyBadge(routeResult.metrics.efficiency_score)}`}>
                  {routeResult.metrics.efficiency_score >= 90 ? 'Excellent' : 
                   routeResult.metrics.efficiency_score >= 75 ? 'Good' : 'Needs Improvement'}
                </Badge>
              </div>
              
              <div className="bg-white p-3 rounded border text-center">
                <p className="text-xs text-gray-500 mb-1">⛽ Fuel Saved</p>
                <p className="text-xl font-bold">
                  {routeResult.metrics.fuel_saved_liters?.toFixed(1) || '0'} L
                </p>
                <p className="text-xs text-gray-500">≈ ₹{(routeResult.metrics.fuel_saved_liters || 0) * 100}</p>
              </div>
            </div>

            {/* Optimized Path */}
            {routeResult.optimized_path && routeResult.optimized_path.length > 0 && (
              <div className="mt-4">
                <h4 className="font-medium mb-2 text-sm">Optimized Route Path:</h4>
                <div className="space-y-2 max-h-40 overflow-y-auto">
                  {routeResult.optimized_path.map((stop, index) => (
                    <div key={index} className="flex items-center gap-3 p-2 bg-white border rounded text-sm">
                      <Badge variant={stop.type === 'pickup' ? 'default' : 'secondary'} className="text-xs">
                        {stop.type === 'pickup' ? 'Pickup' : 'Delivery'}
                      </Badge>
                      <span className="text-xs">
                        ({stop.location[0].toFixed(4)}, {stop.location[1].toFixed(4)})
                      </span>
                      <span className="text-xs ml-auto">
                        {stop.weight_kg}kg • {stop.time_window}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Summary */}
            <div className="pt-3 border-t">
              <p className="text-sm text-gray-600">
                <strong>AI Analysis:</strong> Route optimized using genetic algorithm with time window constraints.
                {routeResult.metrics.stops_optimized && (
                  <span> Reduced {routeResult.metrics.stops_optimized} unnecessary stops.</span>
                )}
              </p>
            </div>
          </div>
        )}

        {/* No Results Placeholder */}
        {!routeResult && !optimizing && (
          <div className="text-center py-6 border-2 border-dashed border-gray-200 rounded">
            <Navigation className="h-12 w-12 mx-auto text-gray-300 mb-3" />
            <p className="text-gray-500 mb-2">No optimization results yet</p>
            <p className="text-sm text-gray-400">
              Add pickup and delivery points, then click "Optimize Route"
            </p>
          </div>
        )}
      </div>
    </MongoDBCard>
  );
};