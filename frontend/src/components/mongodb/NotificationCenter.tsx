import React, { useState, useEffect } from 'react';
import { MongoDBCard } from './MongoDBCard';
import { Bell, Trash2, CheckCircle, AlertCircle, Info } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface Notification {
  _id: string;
  user_id: number;
  title: string;
  message: string;
  type?: string;
  status: 'unread' | 'read';
  created_at: string;
  transaction_id?: string;
  data?: Record<string, any>;
}

const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:5000";

const getHeaders = () => {
  const token = localStorage.getItem("token");
  return {
    "Content-Type": "application/json",
    ...(token && { Authorization: `Bearer ${token}` }),
  };
};

export const NotificationCenter: React.FC = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    loadNotifications();
    
    // Auto-refresh every 10 seconds
    const interval = setInterval(loadNotifications, 10000);
    return () => clearInterval(interval);
  }, []);

  const loadNotifications = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/mongodb/notifications?unread_only=false`, {
        headers: getHeaders(),
      });
      
      if (response.ok) {
        const data = await response.json();
        const notifs = data.notifications || [];
        setNotifications(notifs);
        setUnreadCount(notifs.filter((n: Notification) => n.status === 'unread').length);
      }
    } catch (error) {
      console.error('Failed to load notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async (notificationId: string) => {
    try {
      const response = await fetch(
        `${API_BASE}/api/mongodb/notifications/${notificationId}/read`,
        {
          method: 'PUT',
          headers: getHeaders(),
        }
      );
      
      if (response.ok) {
        setNotifications(
          notifications.map((n) =>
            n._id === notificationId ? { ...n, status: 'read' } : n
          )
        );
        setUnreadCount(Math.max(0, unreadCount - 1));
      }
    } catch (error) {
      console.error('Failed to mark notification as read:', error);
    }
  };

  const deleteNotification = async (notificationId: string) => {
    try {
      const response = await fetch(
        `${API_BASE}/api/mongodb/notifications/${notificationId}`,
        {
          method: 'DELETE',
          headers: getHeaders(),
        }
      );
      
      if (response.ok) {
        setNotifications(notifications.filter((n) => n._id !== notificationId));
      }
    } catch (error) {
      console.error('Failed to delete notification:', error);
    }
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'success':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'warning':
        return <AlertCircle className="h-5 w-5 text-yellow-500" />;
      case 'error':
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      default:
        return <Info className="h-5 w-5 text-blue-500" />;
    }
  };

  const getNotificationBgColor = (type: string | undefined, status: 'unread' | 'read') => {
    if (status === 'read') return 'bg-gray-50';
    const colors: Record<string, string> = {
      success: 'bg-green-50',
      warning: 'bg-yellow-50',
      error: 'bg-red-50',
      transaction_created: 'bg-blue-50',
      info: 'bg-blue-50',
    };
    return colors[type || 'info'] || 'bg-blue-50';
  };

  return (
    <MongoDBCard 
      title={`Notifications ${unreadCount > 0 ? `(${unreadCount})` : ''}`}
      icon="🔔"
    >
      {loading ? (
        <div className="flex justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
      ) : notifications.length > 0 ? (
        <div className="space-y-2 max-h-96 overflow-y-auto pr-2">
          {notifications.map((notification) => (
            <div
              key={notification._id}
              className={`p-3 rounded-lg border ${getNotificationBgColor(
                notification.type,
                notification.status
              )} ${notification.status === 'unread' ? 'border-blue-300' : 'border-gray-200'}`}
            >
              <div className="flex items-start gap-3">
                <div className="mt-1 flex-shrink-0">
                  {getNotificationIcon(notification.type || 'info')}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-sm">
                    {notification.title}
                  </p>
                  <p className="text-sm text-gray-600 mt-1">
                    {notification.message}
                  </p>
                  <p className="text-xs text-gray-500 mt-2">
                    {new Date(notification.created_at).toLocaleString()}
                  </p>
                </div>
                <div className="flex items-center gap-2 flex-shrink-0">
                  {notification.status === 'unread' && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => markAsRead(notification._id)}
                      className="h-6 w-6 p-0"
                      title="Mark as read"
                    >
                      <CheckCircle className="h-4 w-4" />
                    </Button>
                  )}
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => deleteNotification(notification._id)}
                    className="h-6 w-6 p-0"
                    title="Delete"
                  >
                    <Trash2 className="h-4 w-4 text-red-500" />
                  </Button>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-8">
          <Bell className="h-12 w-12 mx-auto text-gray-300 mb-3" />
          <p className="text-gray-500">No notifications</p>
          <p className="text-sm text-gray-400 mt-1">
            You're all caught up!
          </p>
        </div>
      )}
    </MongoDBCard>
  );
};
