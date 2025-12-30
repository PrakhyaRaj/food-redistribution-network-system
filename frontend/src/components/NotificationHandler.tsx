import { useEffect, useState } from 'react';
import { toast } from 'sonner';
import { io, Socket } from 'socket.io-client';
import { useAuth } from '@/contexts/AuthContext';

interface Notification {
  type: string;
  title: string;
  message: string;
  timestamp?: string;
  food_id?: number;
  request_id?: number;
  transaction_id?: number;
  donor_id?: number;
  receiver_id?: number;
}

const NotificationHandler = () => {
  const { userId, isAuthenticated } = useAuth();
  const [socket, setSocket] = useState<Socket | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<'disconnected' | 'connecting' | 'connected' | 'error'>('disconnected');

  useEffect(() => {
    if (!isAuthenticated || !userId) {
      if (socket) {
        socket.disconnect();
        setSocket(null);
        setConnectionStatus('disconnected');
      }
      return;
    }

    console.log('🔌 Attempting to connect to WebSocket...');
    setConnectionStatus('connecting');

    // Get token from localStorage
    const token = localStorage.getItem('token');
    if (!token) {
      console.error('❌ No token found for WebSocket connection');
      setConnectionStatus('error');
      return;
    }

    console.log('🔑 Token found, attempting connection with:', token ? 'Bearer token' : 'no token');

    // Connect to WebSocket server with token in multiple ways for compatibility
    const newSocket = io('http://127.0.0.1:5000', {
      transports: ['polling'],
      withCredentials: true,
      // Send token via query string (most reliable for Socket.IO)
      query: {
        token: token
      },
      // Also send via auth object as fallback
      auth: {
        token: token
      },
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
    });

    newSocket.on('connect', () => {
      console.log('✅ Connected to notification server');
      setConnectionStatus('connected');
      toast.info('Real-time notifications enabled');
    });

    newSocket.on('connection_status', (data) => {
      console.log('🔌 Connection status:', data);
      if (data.status === 'connected') {
        setConnectionStatus('connected');
      } else if (data.status === 'unauthorized') {
        console.error('❌ WebSocket authentication failed');
        setConnectionStatus('error');
        toast.error('Notification connection failed: Authentication required');
      }
    });

    newSocket.on('notification', (notification: Notification) => {
      console.log('🔔 New notification received:', notification);
      
      // Show toast notification based on type
      switch (notification.type) {
        case 'food_matched':
          toast.success(notification.title, {
            description: notification.message,
            duration: 8000,
          });
          break;
        
        case 'request_fulfilled':
          toast.success(notification.title, {
            description: notification.message,
            duration: 8000,
          });
          break;
        
        case 'food_accepted':
          toast.info(notification.title, {
            description: notification.message,
            duration: 6000,
          });
          break;
        
        case 'new_request':
          toast.info(notification.title, {
            description: notification.message,
            duration: 5000,
          });
          break;
        
        case 'match_found':
          toast.success('🎉 Match Found!', {
            description: notification.message,
            duration: 6000,
            action: {
              label: 'View',
              onClick: () => {
                // Navigate to matches page
                window.location.href = `/requests/${notification.request_id}`;
              }
            }
          });
          break;
        
        case 'transaction_update':
          toast.info(notification.title, {
            description: notification.message,
            duration: 5000,
          });
          break;
        
        default:
          toast.info(notification.title, {
            description: notification.message,
            duration: 4000,
          });
      }
    });

    // Listen for real-time match notifications
    newSocket.on('match_found', (data: any) => {
      console.log('🎉 Match notification received:', data);
      toast.success('🎉 Match Found!', {
        description: data.message,
        duration: 6000,
        action: {
          label: 'View Match',
          onClick: () => {
            window.location.href = `/requests/${data.request_id}`;
          }
        }
      });
    });

    newSocket.on('disconnect', (reason) => {
      console.log('🔌 Disconnected from notification server:', reason);
      setConnectionStatus('disconnected');
      if (reason === 'io server disconnect') {
        // Server intentionally disconnected, try to reconnect
        newSocket.connect();
      }
    });

    newSocket.on('connect_error', (error) => {
      console.error('❌ WebSocket connection error:', error);
      setConnectionStatus('error');
      toast.error('Failed to connect to notifications');
    });

    newSocket.on('error', (error) => {
      console.error('❌ Notification error:', error);
    });

    setSocket(newSocket);

    // Cleanup on unmount
    return () => {
      console.log('🔌 Cleaning up WebSocket connection');
      newSocket.disconnect();
    };
  }, [isAuthenticated, userId]);

  // Debug connection status
  useEffect(() => {
    console.log(`🔌 WebSocket status: ${connectionStatus}`);
  }, [connectionStatus]);

  return null;
};

export default NotificationHandler;