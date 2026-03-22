import { createContext, useContext, useState, useEffect, useRef } from 'react';
import { useAuth } from './AuthContext';
import { useToast } from './ToastContext';
import { useNavigate } from 'react-router-dom';

const NotificationsContext = createContext({
  notifications: [],
  unreadCount: 0,
  handleNotificationClick: () => {},
  markAsRead: () => {},
  markAllAsRead: () => {},
  deleteNotification: () => {},
  refreshNotifications: () => {}
});

export const useNotifications = () => {
  const context = useContext(NotificationsContext);
  return context;
};

export const NotificationsProvider = ({ children }) => {
  const { user } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const processingRef = useRef(new Set()); // Track notifications being processed

  useEffect(() => {
    if (user) {
      connectWebSocket();
      loadNotifications();
      // Update last_seen every 4 minutes to maintain online status
      // (threshold is 5 minutes, so this keeps user online)
      const presenceInterval = setInterval(() => {
        updatePresence();
      }, 240000); // 4 minutes

      return () => {
        clearInterval(presenceInterval);
        disconnectWebSocket();
      };
    } else {
      disconnectWebSocket();
      setNotifications([]);
      setUnreadCount(0);
    }
  }, [user]);

  const updatePresence = async () => {
    try {
      await fetch('http://localhost:8000/api/users/me/', {
        method: 'PATCH',
        headers: {
          'Authorization': `Token ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ update_presence: true })
      });
    } catch (error) {
      console.error('Failed to update presence:', error);
    }
  };

  const connectWebSocket = () => {
    // Don't create a new connection if one already exists
    if (wsRef.current && (wsRef.current.readyState === WebSocket.OPEN || wsRef.current.readyState === WebSocket.CONNECTING)) {
      console.log('WebSocket already connected or connecting, skipping...');
      return;
    }

    const token = localStorage.getItem('token');
    if (!token) return;

    try {
      console.log('Creating new WebSocket connection...');
      const ws = new WebSocket(`ws://localhost:8000/ws/notifications/?token=${token}`);
      
      ws.onopen = () => {
        console.log('✅ WebSocket connected');
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('📨 WebSocket message received:', data.type);
        
        if (data.type === 'notification') {
          handleNewNotification(data.notification);
          // Update unread count if provided
          if (data.unread_count !== undefined) {
            setUnreadCount(data.unread_count);
          }
        } else if (data.type === 'unread_count') {
          setUnreadCount(data.count);
        }
      };

      ws.onerror = (error) => {
        console.warn('WebSocket error (will work without real-time notifications):', error);
      };

      ws.onclose = () => {
        console.log('❌ WebSocket disconnected');
        wsRef.current = null;
        // Only attempt to reconnect if user is still logged in and we haven't exceeded retry limit
        if (user && reconnectTimeoutRef.current === null) {
          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectTimeoutRef.current = null;
            if (user) {
              console.log('🔄 Attempting to reconnect WebSocket...');
              connectWebSocket();
            }
          }, 10000); // Retry after 10 seconds to avoid rapid reconnection loops
        }
      };

      wsRef.current = ws;
    } catch (error) {
      console.warn('Failed to connect WebSocket (will work without real-time notifications):', error);
    }
  };

  const disconnectWebSocket = () => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  };

  const loadNotifications = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/notifications/', {
        headers: {
          'Authorization': `Token ${localStorage.getItem('token')}`
        }
      });
      const data = await response.json();
      setNotifications(data.results || []);
      setUnreadCount(data.results?.filter(n => !n.is_read).length || 0);
    } catch (error) {
      console.error('Failed to load notifications:', error);
    }
  };

  const handleNewNotification = (notification) => {
    const notificationKey = notification.id.toString();
    const processedKey = `processed_notif-${notificationKey}`;
    const now = Date.now();
    
    console.log('📨 Received notification:', notificationKey, notification);
    
    // Check if this notification was already added to the list
    const alreadyInList = notifications.some(n => n.id === notification.id);
    
    // Check if recently processed (within last 5 seconds)
    const lastProcessed = localStorage.getItem(processedKey);
    const recentlyProcessed = lastProcessed && (now - parseInt(lastProcessed)) < 5000;
    
    if (recentlyProcessed && alreadyInList) {
      console.log('🚫 Notification already fully processed:', notificationKey);
      return;
    }
    
    // Mark as processed
    localStorage.setItem(processedKey, now.toString());
    processingRef.current.add(notificationKey);
    
    console.log('✅ Processing notification:', notificationKey);
    
    // Clean up old entries (older than 1 hour)
    setTimeout(() => {
      try {
        const keysToRemove = [];
        for (let i = 0; i < localStorage.length; i++) {
          const key = localStorage.key(i);
          if (key && key.startsWith('processed_notif-')) {
            const timestamp = parseInt(localStorage.getItem(key) || '0');
            if (now - timestamp > 3600000) {
              keysToRemove.push(key);
            }
          }
        }
        keysToRemove.forEach(key => localStorage.removeItem(key));
      } catch (e) {
        console.error('Failed to clean old notifications:', e);
      }
    }, 100);
    
    // Add notification to the list if not already there
    if (!alreadyInList) {
      setNotifications(prev => {
        // Double-check it's not in the list
        if (prev.some(n => n.id === notification.id)) {
          console.log('🚫 Notification already in list (race condition):', notificationKey);
          return prev;
        }
        console.log('➕ Adding notification to list');
        return [notification, ...prev];
      });
      
      // Update unread count
      setUnreadCount(prev => prev + 1);
    }
    
    // Always show toast (even if notification was already in list)
    if (!recentlyProcessed) {
      console.log('🔔 Showing toast for notification:', notificationKey);
      showToast(notification.message, 'info');
      
      // Show browser notification if permission granted
      if (Notification.permission === 'granted') {
        new Notification('Podium', {
          body: notification.message,
          icon: '/logo.png'
        });
      }
    }
  };

  const handleNotificationClick = (notification) => {
    // Mark as read
    markAsRead(notification.id);

    // Navigate based on notification type
    if (notification.type === 'FRIEND_REQUEST') {
      navigate(`/u/${user.username}?openFriends=true&tab=requests`);
    } else if (notification.type === 'FRIEND_ACCEPTED') {
      // Navigate to the friend's profile
      if (notification.actor) {
        navigate(`/u/${notification.actor.username}`);
      }
    }
  };

  const markAsRead = async (notificationId) => {
    try {
      await fetch(`http://localhost:8000/api/notifications/${notificationId}/mark_as_read/`, {
        method: 'POST',
        headers: {
          'Authorization': `Token ${localStorage.getItem('token')}`
        }
      });
      
      setNotifications(prev => 
        prev.map(n => n.id === notificationId ? { ...n, is_read: true } : n)
      );
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (error) {
      console.error('Failed to mark notification as read:', error);
    }
  };

  const markAllAsRead = async () => {
    try {
      await fetch('http://localhost:8000/api/notifications/mark_all_as_read/', {
        method: 'POST',
        headers: {
          'Authorization': `Token ${localStorage.getItem('token')}`
        }
      });
      
      setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
      setUnreadCount(0);
    } catch (error) {
      console.error('Failed to mark all as read:', error);
    }
  };

  const deleteNotification = async (notificationId) => {
    try {
      await fetch(`http://localhost:8000/api/notifications/${notificationId}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Token ${localStorage.getItem('token')}`
        }
      });
      
      setNotifications(prev => prev.filter(n => n.id !== notificationId));
      setUnreadCount(prev => {
        const notification = notifications.find(n => n.id === notificationId);
        return notification && !notification.is_read ? Math.max(0, prev - 1) : prev;
      });
    } catch (error) {
      console.error('Failed to delete notification:', error);
    }
  };

  const value = {
    notifications,
    unreadCount,
    handleNotificationClick,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    refreshNotifications: loadNotifications
  };

  return (
    <NotificationsContext.Provider value={value}>
      {children}
    </NotificationsContext.Provider>
  );
};
