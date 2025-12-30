import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import { api, Request as FoodRequest } from "@/lib/api";
import { MatchedFoods } from "@/components/requests/MatchedFoods";
import { useAuth } from "@/contexts/AuthContext";
import { RouteOptimization } from "@/components/RouteOptimization";

const RequestDetail = () => {
  const { requestId } = useParams();
  const { userId } = useAuth();
  const [request, setRequest] = useState<FoodRequest | null>(null);
  const [latestTxn, setLatestTxn] = useState<any | null>(null);

  useEffect(() => {
    const loadRequest = async () => {
      const data = await api.requests.getAll();
      // API returns array directly, and uses request_id not id
      const requestsArray = Array.isArray(data) ? data : data.requests || [];
      const found = requestsArray.find(
        (r: any) => r.request_id === Number(requestId)
      );
      if (found) {
        // Map backend response to FoodRequest interface
        setRequest({
          id: found.request_id,
          receiver_id: found.receiver_id,
          food_type: found.food_type,
          quantity: found.quantity,
          urgency_level: found.urgency_level,
          deadline: found.deadline,
          status: found.status,
        } as FoodRequest);
      } else {
        setRequest(null);
      }
    };

    loadRequest();
  }, [requestId]);

  // Load receiver's latest transaction for route display
  useEffect(() => {
    const loadTransactions = async () => {
      if (!userId) return;
      try {
        const txns = await api.transactions.getUserTransactions(parseInt(userId));
        const arr = Array.isArray(txns) ? txns : [];
        // Find newest transaction for this receiver (optionally matching this request)
        const mine = arr
          .filter((t: any) => t.receiver_id === parseInt(userId))
          .sort((a: any, b: any) => new Date(b.date).getTime() - new Date(a.date).getTime());
        if (mine.length > 0) setLatestTxn(mine[0]);
      } catch (e) {
        // non-blocking
      }
    };
    loadTransactions();
  }, [userId]);

  if (!request) return <p>Loading...</p>;

  return (
    <div className="container mx-auto py-8 space-y-6">
      <h1 className="text-2xl font-bold">{request.food_type}</h1>
      <p>Quantity: {request.quantity}</p>

      <div className="border-t pt-6">
        <h2 className="text-xl font-bold mb-4">Find Matching Food</h2>
        <MatchedFoods
          requestId={request.id}
          foodType={request.food_type}
          quantity={request.quantity}
        />
      </div>

      {latestTxn && (
        <div className="border-t pt-6">
          <h2 className="text-xl font-bold mb-2">Route Optimization</h2>
          <RouteOptimization
            transactionId={latestTxn.txn_id}
            donorId={latestTxn.donor_id}
            receiverId={latestTxn.receiver_id}
            showFull={false}
          />
        </div>
      )}
    </div>
  );
};

export default RequestDetail;
