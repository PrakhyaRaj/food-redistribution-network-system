import React, { useEffect, useState } from "react";
import { AlertCircle, Check } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { api } from "@/lib/api";
import { io, Socket } from "socket.io-client";

interface Match {
  food_id: number;
  donor_id: number;
  donor_name: string;
  food_name: string;
  quantity: number;
  expiry_date: string;
  distance_km: number;
  urgency_match: string;
}

interface Props {
  requestId: number;
  foodType: string;
  quantity: number;
}

export const MatchedFoods: React.FC<Props> = ({ requestId, foodType, quantity }) => {
  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(true);
  const [acceptingId, setAcceptingId] = useState<number | null>(null);
  const { toast } = useToast();

  useEffect(() => {
    loadMatches();

    // 🔴 Socket.IO listener for real-time transaction updates
    const socket = io(import.meta.env.VITE_API_URL || "http://localhost:5000", {
      transports: ["polling"],
    });

    socket.on("connect", () => {
      const token = localStorage.getItem("token");
      if (token) {
        socket.emit("authenticate", { token });
      }
    });

    // Listen for transaction_created event and refresh matches
    socket.on("transaction_created", () => {
      console.log("[MatchedFoods] Transaction created, refreshing matches...");
      loadMatches();
    });

    // Also poll for updates every 5 seconds as fallback
    const pollInterval = setInterval(() => {
      loadMatches();
    }, 5000);

    return () => {
      socket.off("transaction_created");
      socket.disconnect();
      clearInterval(pollInterval);
    };
  }, [requestId]);

  const loadMatches = async () => {
    try {
      setLoading(true);

      const data = await api.requests.findMatches(requestId);

      // ✅ backend-safe handling
      const matchesArray = data.matches || data || [];

      setMatches(matchesArray);

      if (matchesArray.length > 0) {
        toast({
          title: `Found ${matchesArray.length} matches`,
          description: "Matching food items available",
        });
      }
    } catch (err: any) {
      toast({
        title: "Matching failed",
        description: err.message || "Unable to fetch matches",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const acceptMatch = async (foodId: number) => {
    try {
      setAcceptingId(foodId);

      // ✅ use EXISTING API
      const result = await api.food.match(foodId, requestId);

      toast({
        title: "Match accepted",
        description: "Transaction created successfully",
      });

      // Remove the accepted match from the list
      setMatches((prev) => prev.filter((m) => m.food_id !== foodId));
      
      // Reload remaining matches after a brief delay
      setTimeout(() => {
        loadMatches();
      }, 1000);
    } catch (err: any) {
      toast({
        title: "Failed to accept match",
        description: err.message || "Error creating transaction",
        variant: "destructive",
      });
    } finally {
      setAcceptingId(null);
    }
  };

  if (loading) {
    return <p className="text-center text-muted-foreground">Finding matches…</p>;
  }

  if (matches.length === 0) {
    return (
      <div className="border rounded p-6 text-center">
        <AlertCircle className="mx-auto mb-2 text-muted-foreground" />
        <p>No matching food available yet</p>
        <Button variant="outline" onClick={loadMatches} className="mt-4">
          Refresh
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h3 className="font-semibold">
        Looking for {quantity} × {foodType}
      </h3>

      {matches.map((m) => (
        <div key={m.food_id} className="border rounded p-4">
          <div className="flex justify-between items-center">
            <div>
              <p className="font-semibold">{m.food_name}</p>
              <p className="text-sm text-muted-foreground">
                Donor: {m.donor_name}
              </p>
            </div>
            <Badge>{m.urgency_match}</Badge>
          </div>

          <div className="mt-2 text-sm">
            Quantity: {m.quantity} | Distance: {m.distance_km} km
          </div>

          <Button
            className="mt-3 w-full"
            disabled={acceptingId === m.food_id}
            onClick={() => acceptMatch(m.food_id)}
          >
            <Check className="h-4 w-4 mr-2" />
            {acceptingId === m.food_id ? "Processing…" : "Accept Match"}
          </Button>
        </div>
      ))}
    </div>
  );
};
