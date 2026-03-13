import React, { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { MapPin, Building2, Phone, Clock, Info } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";

/**
 * FoodBankMap Component
 * 
 * Interactive map displaying government food banks and distribution centers.
 * Features:
 * - 10 government food bank locations across Bangalore
 * - Includes Indira Canteens, BBMP centers, and emergency relief centers
 * - Click markers to view: address, phone, operating hours, services
 * - Mock data for prototype - will integrate with government APIs in production
 * - Blue markers indicate government-operated facilities
 * 
 * Data includes: Indira Canteens (subsidized meals), BBMP food distribution centers,
 * Karnataka Food Commission centers, and emergency relief facilities.
 * 
 * Usage: Navigate to NGO Page → Food Banks Map tab
 */

// Fix for default markers in react-leaflet
delete (L.Icon.Default.prototype as unknown as { _getIconUrl?: unknown })._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png",
  iconUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png",
  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
});

// Create custom icon for government food banks
const foodBankIcon = new L.Icon({
  iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png",
  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

interface FoodBank {
  id: number;
  name: string;
  lat: number;
  long: number;
  address: string;
  phone?: string;
  operatingHours?: string;
  services?: string[];
  type: "government" | "ngo" | "community";
}

// Mock data for government food banks in Bangalore
const governmentFoodBanks: FoodBank[] = [
  {
    id: 1,
    name: "Indira Canteen - Jayanagar",
    lat: 12.9279,
    long: 77.5937,
    address: "4th Block, Jayanagar, Bangalore",
    phone: "+91 80 2222 3333",
    operatingHours: "7:00 AM - 10:00 AM, 12:00 PM - 3:00 PM, 7:00 PM - 9:00 PM",
    services: ["Subsidized Meals", "Breakfast", "Lunch", "Dinner"],
    type: "government",
  },
  {
    id: 2,
    name: "Indira Canteen - Koramangala",
    lat: 12.9352,
    long: 77.6245,
    address: "Koramangala 5th Block, Bangalore",
    phone: "+91 80 2222 4444",
    operatingHours: "7:00 AM - 10:00 AM, 12:00 PM - 3:00 PM, 7:00 PM - 9:00 PM",
    services: ["Subsidized Meals", "Breakfast", "Lunch", "Dinner"],
    type: "government",
  },
  {
    id: 3,
    name: "BBMP Food Distribution Center - Shivajinagar",
    lat: 12.9826,
    long: 77.6006,
    address: "Shivajinagar, Bangalore",
    phone: "+91 80 2222 5555",
    operatingHours: "10:00 AM - 5:00 PM",
    services: ["Food Packets", "Emergency Relief", "Bulk Food Distribution"],
    type: "government",
  },
  {
    id: 4,
    name: "Karnataka Food Commission Center",
    lat: 12.9716,
    long: 77.5946,
    address: "Cubbon Park Area, Bangalore",
    phone: "+91 80 2222 6666",
    operatingHours: "9:00 AM - 6:00 PM (Mon-Fri)",
    services: ["Food Security Programs", "Ration Distribution", "NGO Coordination"],
    type: "government",
  },
  {
    id: 5,
    name: "Indira Canteen - Indiranagar",
    lat: 12.9716,
    long: 77.6412,
    address: "100 Feet Road, Indiranagar, Bangalore",
    phone: "+91 80 2222 7777",
    operatingHours: "7:00 AM - 10:00 AM, 12:00 PM - 3:00 PM, 7:00 PM - 9:00 PM",
    services: ["Subsidized Meals", "Breakfast", "Lunch", "Dinner"],
    type: "government",
  },
  {
    id: 6,
    name: "Government Community Kitchen - Banashankari",
    lat: 12.9250,
    long: 77.5462,
    address: "Banashankari 2nd Stage, Bangalore",
    phone: "+91 80 2222 8888",
    operatingHours: "8:00 AM - 8:00 PM",
    services: ["Community Meals", "Takeaway", "Bulk Orders"],
    type: "government",
  },
  {
    id: 7,
    name: "Indira Canteen - Malleshwaram",
    lat: 13.0067,
    long: 77.5703,
    address: "18th Cross, Malleshwaram, Bangalore",
    phone: "+91 80 2222 9999",
    operatingHours: "7:00 AM - 10:00 AM, 12:00 PM - 3:00 PM, 7:00 PM - 9:00 PM",
    services: ["Subsidized Meals", "Breakfast", "Lunch", "Dinner"],
    type: "government",
  },
  {
    id: 8,
    name: "BBMP Emergency Food Relief Center",
    lat: 12.9698,
    long: 77.7499,
    address: "Whitefield, Bangalore",
    phone: "+91 80 2223 0000",
    operatingHours: "24/7 (Emergency)",
    services: ["Emergency Food", "Disaster Relief", "Homeless Support"],
    type: "government",
  },
  {
    id: 9,
    name: "Indira Canteen - Rajajinagar",
    lat: 12.9899,
    long: 77.5544,
    address: "3rd Block, Rajajinagar, Bangalore",
    phone: "+91 80 2223 1111",
    operatingHours: "7:00 AM - 10:00 AM, 12:00 PM - 3:00 PM, 7:00 PM - 9:00 PM",
    services: ["Subsidized Meals", "Breakfast", "Lunch", "Dinner"],
    type: "government",
  },
  {
    id: 10,
    name: "Government Food Distribution Hub - Electronic City",
    lat: 12.8456,
    long: 77.6603,
    address: "Electronic City Phase 1, Bangalore",
    phone: "+91 80 2223 2222",
    operatingHours: "10:00 AM - 6:00 PM",
    services: ["Food Distribution", "NGO Support", "Corporate Partnerships"],
    type: "government",
  },
];

// Component to fit bounds to show all markers
const FitBounds = ({ foodBanks }: { foodBanks: FoodBank[] }) => {
  const map = useMap();

  useEffect(() => {
    if (foodBanks.length > 0) {
      const bounds = L.latLngBounds(foodBanks.map((fb) => [fb.lat, fb.long]));
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [map, foodBanks]);

  return null;
};

const FoodBankMap = () => {
  const [mapKey, setMapKey] = useState(0);

  // Default center (Bangalore city center)
  const defaultCenter: [number, number] = [12.9716, 77.5946];

  // Force map refresh on mount to fix initialization
  useEffect(() => {
    const timer = setTimeout(() => {
      setMapKey(prev => prev + 1);
    }, 100);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Building2 className="h-5 w-5 text-blue-600" />
            Government Food Banks & Distribution Centers
          </CardTitle>
          <CardDescription>
            View {governmentFoodBanks.length} government-operated food banks and distribution centers across Bangalore
          </CardDescription>
        </CardHeader>
        <CardContent>
          {/* Map Container */}
          <div className="rounded-lg overflow-hidden border border-gray-200 shadow-sm" style={{ height: "500px" }}>
            <MapContainer
              key={mapKey}
              center={defaultCenter}
              zoom={11}
              style={{ height: "100%", width: "100%" }}
              scrollWheelZoom={true}
            >
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              
              <FitBounds foodBanks={governmentFoodBanks} />

              {governmentFoodBanks.map((foodBank) => (
                <Marker
                  key={foodBank.id}
                  position={[foodBank.lat, foodBank.long]}
                  icon={foodBankIcon}
                >
                  <Popup maxWidth={300}>
                    <div className="p-2">
                      <h3 className="font-bold text-lg mb-2 flex items-center gap-2">
                        <Building2 className="h-4 w-4 text-blue-600" />
                        {foodBank.name}
                      </h3>
                      
                      <div className="space-y-2 text-sm">
                        <div className="flex items-start gap-2">
                          <MapPin className="h-4 w-4 text-gray-500 mt-0.5 flex-shrink-0" />
                          <span>{foodBank.address}</span>
                        </div>
                        
                        {foodBank.phone && (
                          <div className="flex items-center gap-2">
                            <Phone className="h-4 w-4 text-gray-500 flex-shrink-0" />
                            <span>{foodBank.phone}</span>
                          </div>
                        )}
                        
                        {foodBank.operatingHours && (
                          <div className="flex items-start gap-2">
                            <Clock className="h-4 w-4 text-gray-500 mt-0.5 flex-shrink-0" />
                            <span>{foodBank.operatingHours}</span>
                          </div>
                        )}
                        
                        {foodBank.services && foodBank.services.length > 0 && (
                          <div className="mt-3">
                            <p className="font-semibold mb-1">Services:</p>
                            <div className="flex flex-wrap gap-1">
                              {foodBank.services.map((service, idx) => (
                                <span
                                  key={idx}
                                  className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded"
                                >
                                  {service}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                        
                        <div className="mt-2 pt-2 border-t">
                          <span className="inline-flex items-center text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                            Government Facility
                          </span>
                        </div>
                      </div>
                    </div>
                  </Popup>
                </Marker>
              ))}
            </MapContainer>
          </div>

          {/* Legend */}
          <div className="mt-4 p-4 bg-gray-50 rounded-lg">
            <h4 className="font-semibold mb-2 text-sm">Map Legend:</h4>
            <div className="flex flex-wrap gap-4 text-sm">
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 bg-blue-500 rounded-full"></div>
                <span>Government Food Bank</span>
              </div>
              <div className="flex items-center gap-2">
                <MapPin className="h-5 w-5 text-blue-600" />
                <span>Click markers for details</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Statistics Card */}
      <Card className="bg-gradient-to-r from-blue-50 to-cyan-50 border-blue-200">
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-3xl font-bold text-blue-900">{governmentFoodBanks.length}</p>
              <p className="text-sm text-blue-700">Food Banks</p>
            </div>
            <div>
              <p className="text-3xl font-bold text-blue-900">24/7</p>
              <p className="text-sm text-blue-700">Emergency Support</p>
            </div>
            <div>
              <p className="text-3xl font-bold text-blue-900">Free</p>
              <p className="text-sm text-blue-700">Government Service</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default FoodBankMap;
