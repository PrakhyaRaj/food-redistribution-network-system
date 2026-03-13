// frontend/src/components/mongodb/TransactionHistory.tsx
import React, { useState, useEffect } from 'react';
import { MapPin, Calendar, User, Package, TrendingUp } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { MongoDBCard } from './MongoDBCard';
import { useAuth } from '@/contexts/AuthContext';

interface Transaction {
  _id: string;
  txn_id: number;
  donor_id: number;
  receiver_id: number;
  food_id: number;
  request_id: number;
  status: string;
  route_data?: any;
  created_at: string;
  updated_at: string;
}

const API_BASE = 'http://127.0.0.1:5000';

const getHeaders = () => {
  const token = localStorage.getItem("token") || localStorage.getItem("access_token");
  return {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` })
  };
};

export const TransactionHistory: React.FC = () => {
  const { user } = useAuth();
  const userId = user?.user_id?.toString() || localStorage.getItem("user_id");
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    total_donations: 0,
    total_received: 0,
    completed_donations: 0,
    completed_received: 0
  });

  useEffect(() => {
    loadTransactions();
  }, []);

  const loadTransactions = async () => {
    try {
      setLoading(true);
      
      // Try to get from MongoDB first
      const response = await fetch(`${API_BASE}/api/mongodb/transactions`, {
        headers: getHeaders()
      });

      if (response.ok) {
        const data = await response.json();
        setTransactions(data.transactions || []);
        setStats(data.stats || stats);
      } else {
        // Fallback: fetch from SQL endpoints
        const txnResponse = await fetch(`${API_BASE}/transactions/my`, {
          headers: getHeaders()
        });
        
        if (txnResponse.ok) {
          const txnData = await txnResponse.json();
          setTransactions(txnData.transactions || []);
        }
      }
    } catch (error) {
      console.error('Error loading transactions:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'in_progress':
        return 'bg-blue-100 text-blue-800';
      case 'initiated':
        return 'bg-yellow-100 text-yellow-800';
      case 'cancelled':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const handleMarkDelivered = async (txnId: number) => {
    try {
      const response = await fetch(`${API_BASE}/transactions/update/${txnId}`, {
        method: 'PUT',
        headers: getHeaders(),
        body: JSON.stringify({ status: 'delivered' })
      });

      if (response.ok) {
        await loadTransactions();
        alert('Transaction marked as delivered!');
      } else {
        const error = await response.json();
        alert(error.error || 'Failed to update transaction');
      }
    } catch (error) {
      console.error('Error updating transaction:', error);
      alert('Error updating transaction');
    }
  };

  const handleMarkReceived = async (txnId: number) => {
    try {
      const response = await fetch(`${API_BASE}/transactions/update/${txnId}`, {
        method: 'PUT',
        headers: getHeaders(),
        body: JSON.stringify({ status: 'received' })
      });

      if (response.ok) {
        await loadTransactions();
        alert('Transaction marked as received!');
      } else {
        const error = await response.json();
        alert(error.error || 'Failed to update transaction');
      }
    } catch (error) {
      console.error('Error updating transaction:', error);
      alert('Error updating transaction');
    }
  };

  return (
    <MongoDBCard title="Transaction History" icon={<Package />}>
      {/* Stats Summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="rounded-lg bg-blue-50 p-4">
          <p className="text-sm text-gray-600">Donations Made</p>
          <p className="text-2xl font-bold text-blue-600">{stats.total_donations}</p>
          <p className="text-xs text-gray-500 mt-1">
            {stats.completed_donations} completed
          </p>
        </div>
        <div className="rounded-lg bg-green-50 p-4">
          <p className="text-sm text-gray-600">Items Received</p>
          <p className="text-2xl font-bold text-green-600">{stats.total_received}</p>
          <p className="text-xs text-gray-500 mt-1">
            {stats.completed_received} completed
          </p>
        </div>
        <div className="rounded-lg bg-purple-50 p-4">
          <p className="text-sm text-gray-600">Success Rate</p>
          <p className="text-2xl font-bold text-purple-600">
            {stats.total_donations + stats.total_received > 0
              ? Math.round(
                  ((stats.completed_donations + stats.completed_received) /
                    (stats.total_donations + stats.total_received)) *
                    100
                )
              : 0}
            %
          </p>
        </div>
        <div className="rounded-lg bg-orange-50 p-4">
          <p className="text-sm text-gray-600">Active</p>
          <p className="text-2xl font-bold text-orange-600">
            {transactions.filter(t => t.status === 'in_progress').length}
          </p>
          <p className="text-xs text-gray-500 mt-1">in progress</p>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center p-8">
          <div className="text-center">
            <div className="mb-4">
              <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-gray-300 border-t-blue-600"></div>
            </div>
            <p className="text-gray-600">Loading transactions...</p>
          </div>
        </div>
      ) : transactions.length === 0 ? (
        <div className="text-center py-8">
          <Package className="mx-auto h-12 w-12 text-gray-300 mb-3" />
          <p className="text-gray-600">No transactions yet</p>
          <p className="text-sm text-gray-500 mt-1">
            Your transaction history will appear here
          </p>
        </div>
      ) : (
        <div className="space-y-4 max-h-96 overflow-y-auto">
          {transactions.map((txn) => (
            <div
              key={txn._id}
              className="rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <h4 className="font-semibold">
                    Transaction #{txn.txn_id}
                  </h4>
                  <p className="text-sm text-gray-600">
                    Food ID: {txn.food_id} | Request ID: {txn.request_id}
                  </p>
                </div>
                <Badge className={getStatusColor(txn.status)}>
                  {txn.status.replace(/_/g, ' ').toUpperCase()}
                </Badge>
              </div>

              <div className="grid grid-cols-2 gap-3 text-sm mb-3">
                <div className="flex items-center gap-2">
                  <User className="h-4 w-4 text-gray-500" />
                  <span className="text-gray-600">
                    Donor ID: <span className="font-medium">{txn.donor_id}</span>
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <User className="h-4 w-4 text-gray-500" />
                  <span className="text-gray-600">
                    Receiver ID: <span className="font-medium">{txn.receiver_id}</span>
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <Calendar className="h-4 w-4 text-gray-500" />
                  <span className="text-gray-600">
                    Created: <span className="font-medium">{formatDate(txn.created_at)}</span>
                  </span>
                </div>
                {txn.route_data && (
                  <div className="flex items-center gap-2">
                    <MapPin className="h-4 w-4 text-gray-500" />
                    <span className="text-gray-600">
                      Route optimized
                    </span>
                  </div>
                )}
              </div>

              {/* Route Details if available */}
              {txn.route_data && (
                <div className="mt-3 rounded-md bg-gray-50 p-3 text-xs">
                  <p className="font-semibold mb-2 flex items-center gap-1">
                    <MapPin className="h-3 w-3" />
                    Route Details
                  </p>
                  <div className="grid grid-cols-2 gap-2">
                    {txn.route_data.total_distance_km && (
                      <p className="text-gray-600">
                        Distance: <span className="font-medium">{txn.route_data.total_distance_km}km</span>
                      </p>
                    )}
                    {txn.route_data.estimated_time_hours && (
                      <p className="text-gray-600">
                        Time: <span className="font-medium">{txn.route_data.estimated_time_hours}h</span>
                      </p>
                    )}
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div className="mt-3 flex gap-2">
                {txn.donor_id === parseInt(userId!) && txn.status === "initiated" && (
                  <Button 
                    onClick={() => handleMarkDelivered(txn.txn_id)}
                    size="sm"
                    className="bg-blue-600 hover:bg-blue-700"
                  >
                    Mark as Delivered
                  </Button>
                )}
                {txn.receiver_id === parseInt(userId!) && txn.status === "in_progress" && (
                  <Button 
                    onClick={() => handleMarkReceived(txn.txn_id)}
                    size="sm"
                    className="bg-green-600 hover:bg-green-700"
                  >
                    Mark as Received
                  </Button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </MongoDBCard>
  );
};
