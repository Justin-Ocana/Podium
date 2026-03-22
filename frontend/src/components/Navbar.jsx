import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNotifications } from '../contexts/NotificationsContext';
import Avatar from './Avatar';
import api from '../services/api';
import './Navbar-v2.css';

const Navbar = ({ user, onLogout }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { refreshUser } = useAuth();
  const notificationsContext = useNotifications();
  const { notifications = [], unreadCount = 0, handleNotificationClick = () => {}, markAllAsRead = () => {} } = notificationsContext || {};
  const [showUserDropdown, setShowUserDropdown] = useState(false);
  const [showCreateDropdown, setShowCreateDropdown] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const handleLogout = () => {
    onLogout();
    navigate('/login');
  };

  const handleToggleInvisible = async () => {
    try {
      await api.toggleInvisibleMode(!user.is_invisible);
      await refreshUser();
    } catch (error) {
      console.error('Failed to toggle invisible mode:', error);
    }
  };

  const getTimeAgo = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.floor((now - date) / 1000);

    if (seconds < 60) return 'just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
    return date.toLocaleDateString();
  };

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <div className="navbar-left">
          <Link to="/dashboard" className="navbar-logo">
            PODIUM
          </Link>

          {/* Global Search */}
          <div className="navbar-search">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" className="search-icon">
              <path d="M21 21L15 15M17 10C17 13.866 13.866 17 10 17C6.13401 17 3 13.866 3 10C3 6.13401 6.13401 3 10 3C13.866 3 17 6.13401 17 10Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
            <input
              type="text"
              placeholder="Search tournaments, teams..."
              className="search-input"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.setQuery)}
            />
          </div>
        </div>

        <div className="navbar-center">
          <Link 
            to="/tournaments" 
            className={`navbar-link ${isActive('/tournaments') ? 'navbar-link--active' : ''}`}
          >
            Tournaments
          </Link>
          <Link 
            to="/teams" 
            className={`navbar-link ${isActive('/teams') ? 'navbar-link--active' : ''}`}
          >
            Teams
          </Link>
          <Link 
            to="/leaderboard" 
            className={`navbar-link ${isActive('/leaderboard') ? 'navbar-link--active' : ''}`}
          >
            Leaderboard
          </Link>
        </div>

        <div className="navbar-right">
          {user ? (
            <>
              {/* Create Button */}
              <div className="navbar-create">
                <button 
                  className="navbar-create-btn"
                  onClick={() => setShowCreateDropdown(!showCreateDropdown)}
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                    <path d="M12 5V19M5 12H19" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                  </svg>
                  Create
                </button>
                
                {showCreateDropdown && (
                  <div className="navbar-dropdown navbar-dropdown--create">
                    <Link to="/tournaments/create" className="dropdown-item" onClick={() => setShowCreateDropdown(false)}>
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                        <path d="M6 2L3 6V20C3 20.5304 3.21071 21.0391 3.58579 21.4142C3.96086 21.7893 4.46957 22 5 22H19C19.5304 22 20.0391 21.7893 20.4142 21.4142C20.7893 21.0391 21 20.5304 21 20V6L18 2H6Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                      Create Tournament
                    </Link>
                    <Link to="/teams/create" className="dropdown-item" onClick={() => setShowCreateDropdown(false)}>
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                        <path d="M17 21V19C17 17.9391 16.5786 16.9217 15.8284 16.1716C15.0783 15.4214 14.0609 15 13 15H5C3.93913 15 2.92172 15.4214 2.17157 16.1716C1.42143 16.9217 1 17.9391 1 19V21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                      Create Team
                    </Link>
                  </div>
                )}
              </div>

              {/* Notifications */}
              <div className="navbar-notifications-wrapper">
                <button 
                  className="navbar-notifications"
                  onClick={() => {
                    setShowNotifications(!showNotifications);
                    // Refresh notifications when opening dropdown
                    if (!showNotifications && notificationsContext?.refreshNotifications) {
                      notificationsContext.refreshNotifications();
                    }
                  }}
                >
                  <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                    <path d="M15 6.66667C15 5.34058 14.4732 4.06881 13.5355 3.13113C12.5979 2.19345 11.3261 1.66667 10 1.66667C8.67392 1.66667 7.40215 2.19345 6.46447 3.13113C5.52678 4.06881 5 5.34058 5 6.66667C5 12.5 2.5 14.1667 2.5 14.1667H17.5C17.5 14.1667 15 12.5 15 6.66667Z" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                    <path d="M11.4417 17.5C11.2952 17.7526 11.0849 17.9622 10.8319 18.1079C10.5789 18.2537 10.292 18.3304 10 18.3304C9.70802 18.3304 9.42115 18.2537 9.16815 18.1079C8.91515 17.9622 8.70486 17.7526 8.55835 17.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                  {unreadCount > 0 && (
                    <span className="notification-badge">{unreadCount}</span>
                  )}
                </button>

                {showNotifications && (
                  <div className="navbar-dropdown navbar-dropdown--notifications">
                    <div className="dropdown-header">
                      <span>Notifications</span>
                      <span className="notification-count">{unreadCount}</span>
                    </div>
                    <div className="dropdown-divider"></div>
                    {notifications.length === 0 ? (
                      <div className="notification-empty">
                        <p>No notifications</p>
                      </div>
                    ) : (
                      <>
                        {notifications.slice(0, 5).map(notification => (
                          <div 
                            key={notification.id} 
                            className={`notification-item ${!notification.is_read ? 'notification-item--unread' : ''}`}
                            onClick={() => {
                              handleNotificationClick(notification);
                              setShowNotifications(false);
                            }}
                          >
                            <div className={`notification-icon notification-icon--${
                              notification.type === 'FRIEND_REQUEST' ? 'info' : 
                              notification.type === 'FRIEND_ACCEPTED' ? 'success' : 
                              'default'
                            }`}>
                              {notification.type === 'FRIEND_REQUEST' && (
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                                  <path d="M16 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2" stroke="currentColor" strokeWidth="2"/>
                                  <circle cx="8.5" cy="7" r="4" stroke="currentColor" strokeWidth="2"/>
                                  <line x1="20" y1="8" x2="20" y2="14" stroke="currentColor" strokeWidth="2"/>
                                  <line x1="23" y1="11" x2="17" y2="11" stroke="currentColor" strokeWidth="2"/>
                                </svg>
                              )}
                              {notification.type === 'FRIEND_ACCEPTED' && (
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                                  <path d="M20 6L9 17L4 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                                </svg>
                              )}
                            </div>
                            <div className="notification-content">
                              <p>{notification.message}</p>
                              <span className="notification-time">{getTimeAgo(notification.created_at)}</span>
                            </div>
                          </div>
                        ))}
                        {notifications.length > 0 && (
                          <div className="dropdown-footer">
                            <button onClick={() => {
                              markAllAsRead();
                              setShowNotifications(false);
                            }}>
                              Mark all as read
                            </button>
                            {notifications.length > 5 && (
                              <button onClick={() => navigate('/notifications')}>View all</button>
                            )}
                          </div>
                        )}
                      </>
                    )}
                  </div>
                )}
              </div>

              {/* User Avatar */}
              <div className="navbar-user" onClick={() => setShowUserDropdown(!showUserDropdown)}>
                <Avatar 
                  src={user?.avatar_url} 
                  username={user?.username}
                  size="small"
                />
                
                {showUserDropdown && (
                  <div className="navbar-dropdown">
                    <Link to={`/u/${user.username}`} className="dropdown-item" onClick={() => setShowUserDropdown(false)}>
                      <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                        <path d="M13.3333 14V12.6667C13.3333 11.9594 13.0524 11.2811 12.5523 10.781C12.0522 10.281 11.3739 10 10.6667 10H5.33333C4.62609 10 3.94781 10.281 3.44772 10.781C2.94762 11.2811 2.66667 11.9594 2.66667 12.6667V14" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                        <path d="M8.00001 7.33333C9.47277 7.33333 10.6667 6.13943 10.6667 4.66667C10.6667 3.19391 9.47277 2 8.00001 2C6.52725 2 5.33334 3.19391 5.33334 4.66667C5.33334 6.13943 6.52725 7.33333 8.00001 7.33333Z" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                      Profile
                    </Link>
                    <Link to="/teams/my" className="dropdown-item" onClick={() => setShowUserDropdown(false)}>
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                        <path d="M17 21V19C17 17.9391 16.5786 16.9217 15.8284 16.1716C15.0783 15.4214 14.0609 15 13 15H5C3.93913 15 2.92172 15.4214 2.17157 16.1716C1.42143 16.9217 1 17.9391 1 19V21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                      My Teams
                    </Link>
                    <Link to="/tournaments" className="dropdown-item" onClick={() => setShowUserDropdown(false)}>
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                        <path d="M6 2L3 6V20C3 20.5304 3.21071 21.0391 3.58579 21.4142C3.96086 21.7893 4.46957 22 5 22H19C19.5304 22 20.0391 21.7893 20.4142 21.4142C20.7893 21.0391 21 20.5304 21 20V6L18 2H6Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                      My Tournaments
                    </Link>
                    <div className="dropdown-divider"></div>
                    <div className="dropdown-item dropdown-item--status">
                      <div className="status-info">
                        <div className="status-indicator-wrapper">
                          <div className={`status-indicator ${!user?.is_invisible ? 'status-indicator--online' : 'status-indicator--offline'}`}></div>
                          <span className="status-text">{!user?.is_invisible ? 'Online' : 'Offline'}</span>
                        </div>
                        <span className="status-label">Status</span>
                      </div>
                      <button 
                        onClick={(e) => {
                          e.stopPropagation();
                          handleToggleInvisible();
                        }}
                        className={`status-toggle ${!user?.is_invisible ? 'status-toggle--active' : ''}`}
                      >
                        <span className="status-toggle-slider"></span>
                      </button>
                    </div>
                    <Link to="/settings" className="dropdown-item" onClick={() => setShowUserDropdown(false)}>
                      <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                        <path d="M8 10C9.10457 10 10 9.10457 10 8C10 6.89543 9.10457 6 8 6C6.89543 6 6 6.89543 6 8C6 9.10457 6.89543 10 8 10Z" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                      Settings
                    </Link>
                    <button onClick={handleLogout} className="dropdown-item dropdown-item--danger">
                      <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                        <path d="M6 14H3.33333C2.97971 14 2.64057 13.8595 2.39052 13.6095C2.14048 13.3594 2 13.0203 2 12.6667V3.33333C2 2.97971 2.14048 2.64057 2.39052 2.39052C2.64057 2.14048 2.97971 2 3.33333 2H6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                        <path d="M10.6667 11.3333L14 8L10.6667 4.66667" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                        <path d="M14 8H6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                      Logout
                    </button>
                  </div>
                )}
              </div>
            </>
          ) : (
            /* Sign Up button for unauthenticated users */
            <Link to="/register" className="navbar-signup-btn">
              Sign Up
            </Link>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
