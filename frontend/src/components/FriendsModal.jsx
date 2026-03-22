import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Avatar from './Avatar';
import api from '../services/api';
import { useToast } from '../contexts/ToastContext';
import { useNotifications } from '../contexts/NotificationsContext';
import './FriendsModal.css';

const FriendsModal = ({ username, isOwnProfile = false, initialRequestsCount = 0, initialTab = 'all', onClose, onDataUpdate }) => {
  const { showToast } = useToast();
  const { notifications } = useNotifications();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState(initialTab);
  const [friends, setFriends] = useState([]);
  const [friendRequests, setFriendRequests] = useState([]);
  const [requestsCount, setRequestsCount] = useState(initialRequestsCount);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [friendToRemove, setFriendToRemove] = useState(null);
  const [isRemoving, setIsRemoving] = useState(false);

  // Listen for real-time updates from notifications
  useEffect(() => {
    // Reload data when friend-related notifications arrive
    const lastNotification = notifications[0];
    if (lastNotification && (
      lastNotification.type === 'FRIEND_REQUEST' ||
      lastNotification.type === 'FRIEND_ACCEPTED'
    )) {
      // Debounce the reload to avoid multiple rapid calls
      const timer = setTimeout(() => {
        loadAllData();
        if (onDataUpdate) onDataUpdate();
      }, 500);
      return () => clearTimeout(timer);
    }
  }, [notifications]);

  // Refresh friend list periodically to update online status
  // Only when modal is open, not loading, and on friends tabs
  useEffect(() => {
    if (loading || activeTab === 'requests') return;
    
    const interval = setInterval(() => {
      // Silently refresh friends list in background
      api.getFriends().then(friendsData => {
        setFriends(friendsData);
      }).catch(err => {
        console.error('Failed to refresh friends:', err);
      });
    }, 120000); // 2 minutes to reduce server load

    return () => clearInterval(interval);
  }, [activeTab, loading]);

  useEffect(() => {
    loadAllData();
  }, [isOwnProfile]);

  const loadAllData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load friends
      const friendsData = await api.getFriends();
      setFriends(friendsData);

      // Load friend requests if own profile
      if (isOwnProfile) {
        const requests = await api.getFriendRequests();
        setFriendRequests(requests);
        setRequestsCount(requests.length);
      }
    } catch (err) {
      console.error('Error loading data:', err);
      setError('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const filteredFriends = activeTab === 'all' 
    ? friends 
    : friends.filter(f => f.presence_status === 'online');

  const getStatusColor = (status) => {
    return status === 'online' ? '#10b981' : '#6b7280';
  };

  const getStatusText = (status) => {
    return status === 'online' ? 'Online' : 'Offline';
  };

  const handleAcceptRequest = async (requestId) => {
    try {
      await api.acceptFriendRequest(requestId);
      showToast('Friend request accepted!', 'success');
      // Reload all data to update both lists
      await loadAllData();
      // Notify parent to update counts
      if (onDataUpdate) onDataUpdate();
    } catch (err) {
      console.error('Error accepting friend request:', err);
      showToast('Failed to accept friend request', 'error');
    }
  };

  const handleDeclineRequest = async (requestId) => {
    try {
      await api.declineFriendRequest(requestId);
      showToast('Friend request declined', 'info');
      // Reload all data
      await loadAllData();
      // Notify parent to update counts
      if (onDataUpdate) onDataUpdate();
    } catch (err) {
      console.error('Error declining friend request:', err);
      showToast('Failed to decline friend request', 'error');
    }
  };

  const handleRemoveFriend = async (username) => {
    setIsRemoving(true);
    
    try {
      await api.removeFriend(username);
      showToast('Friend removed', 'info');
      // Reload all data
      await loadAllData();
      // Notify parent to update counts
      if (onDataUpdate) onDataUpdate();
    } catch (err) {
      console.error('Error removing friend:', err);
      showToast('Failed to remove friend', 'error');
    } finally {
      setIsRemoving(false);
      setShowConfirmModal(false);
      setFriendToRemove(null);
    }
  };

  const handleRemoveClick = (friend) => {
    setFriendToRemove(friend);
    setShowConfirmModal(true);
  };

  const handleCancelRemove = () => {
    setShowConfirmModal(false);
    setFriendToRemove(null);
  };

  const getTimeAgo = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.floor((now - date) / 1000);

    if (seconds < 60) return 'just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)} minutes ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)} hours ago`;
    if (seconds < 604800) return `${Math.floor(seconds / 86400)} days ago`;
    return date.toLocaleDateString();
  };

  const handleViewProfile = (username) => {
    onClose(); // Close modal first
    navigate(`/u/${username}`); // Navigate to profile
  };

  return (
    <div className="friends-modal-overlay" onClick={onClose}>
      <div className="friends-modal" onClick={(e) => e.stopPropagation()}>
        <div className="friends-modal-header">
          <h2>{username}'s Friends</h2>
          <button className="modal-close" onClick={onClose}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        <div className="friends-modal-tabs">
          <button 
            className={`friends-tab ${activeTab === 'all' ? 'active' : ''}`}
            onClick={() => setActiveTab('all')}
          >
            All Friends
            <span className="tab-count">{friends.length}</span>
          </button>
          {isOwnProfile && (
            <>
              <button 
                className={`friends-tab ${activeTab === 'online' ? 'active' : ''}`}
                onClick={() => setActiveTab('online')}
              >
                Online
                <span className="tab-count">{friends.filter(f => f.presence_status === 'online').length}</span>
              </button>
              <button 
                className={`friends-tab ${activeTab === 'requests' ? 'active' : ''}`}
                onClick={() => setActiveTab('requests')}
              >
                Requests
                <span className="tab-count tab-count--pending">{requestsCount}</span>
              </button>
            </>
          )}
        </div>

        <div className="friends-modal-content">
          {loading ? (
            <div className="friends-modal-loading">
              <div className="loading-spinner-small">
                <div className="spinner-ring"></div>
                <div className="spinner-ring"></div>
                <div className="spinner-ring"></div>
              </div>
              <p>Loading friends...</p>
            </div>
          ) : error ? (
            <div className="friends-empty">
              <p>{error}</p>
            </div>
          ) : activeTab === 'requests' ? (
            // Friend Requests Tab
            friendRequests.length === 0 ? (
              <div className="friends-empty">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M16 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/>
                  <circle cx="8.5" cy="7" r="4"/>
                  <line x1="20" y1="8" x2="20" y2="14"/>
                  <line x1="23" y1="11" x2="17" y2="11"/>
                </svg>
                <p>No pending friend requests</p>
              </div>
            ) : (
              <div className="friends-list">
                {friendRequests.map(request => (
                  <div key={request.id} className="friend-request-item">
                    <div 
                      className="friend-avatar-wrapper"
                      onClick={() => handleViewProfile(request.from_user.username)}
                      style={{ cursor: 'pointer' }}
                    >
                      <Avatar 
                        src={request.from_user.avatar_url} 
                        username={request.from_user.username}
                        size="medium"
                      />
                    </div>
                    <div className="friend-info">
                      <div 
                        className="friend-username"
                        onClick={() => handleViewProfile(request.from_user.username)}
                        style={{ cursor: 'pointer' }}
                      >
                        {request.from_user.username}
                      </div>
                      <div className="friend-status">{getTimeAgo(request.created_at)}</div>
                    </div>
                    <div className="friend-request-actions">
                      <button 
                        className="friend-request-btn friend-request-btn--accept"
                        onClick={() => handleAcceptRequest(request.id)}
                        title="Accept"
                      >
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                          <polyline points="20 6 9 17 4 12"/>
                        </svg>
                      </button>
                      <button 
                        className="friend-request-btn friend-request-btn--decline"
                        onClick={() => handleDeclineRequest(request.id)}
                        title="Decline"
                      >
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                          <line x1="18" y1="6" x2="6" y2="18"/>
                          <line x1="6" y1="6" x2="18" y2="18"/>
                        </svg>
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )
          ) : (
            // Friends List Tab
            filteredFriends.length === 0 ? (
            <div className="friends-empty">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/>
                <circle cx="9" cy="7" r="4"/>
                <path d="M23 21v-2a4 4 0 00-3-3.87"/>
                <path d="M16 3.13a4 4 0 010 7.75"/>
              </svg>
              <p>No friends {activeTab !== 'all' ? activeTab : 'yet'}</p>
            </div>
          ) : (
            <div className="friends-list">
              {filteredFriends.map(friend => (
                <div key={friend.id} className="friend-item">
                  <div 
                    className="friend-avatar-wrapper"
                    onClick={() => handleViewProfile(friend.username)}
                    style={{ cursor: 'pointer' }}
                  >
                    <Avatar 
                      src={friend.avatar_url} 
                      username={friend.username}
                      size="medium"
                    />
                    <div 
                      className="friend-status-indicator"
                      style={{ backgroundColor: getStatusColor(friend.presence_status) }}
                    />
                  </div>
                  <div className="friend-info">
                    <div 
                      className="friend-username"
                      onClick={() => handleViewProfile(friend.username)}
                      style={{ cursor: 'pointer' }}
                    >
                      {friend.username}
                    </div>
                    <div className="friend-status">{getStatusText(friend.presence_status)}</div>
                  </div>
                  <div className="friend-actions">
                    <button className="friend-action-btn" title="Send Message">
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/>
                      </svg>
                    </button>
                    <button 
                      className="friend-action-btn" 
                      title="View Profile"
                      onClick={() => handleViewProfile(friend.username)}
                    >
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/>
                        <circle cx="12" cy="7" r="4"/>
                      </svg>
                    </button>
                    {isOwnProfile && (
                      <button 
                        className="friend-action-btn friend-action-btn--remove" 
                        title="Remove Friend"
                        onClick={() => handleRemoveClick(friend)}
                      >
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <polyline points="3 6 5 6 21 6"/>
                          <path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
                        </svg>
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )
          )}
        </div>
      </div>

      {/* Confirmation Modal */}
      {showConfirmModal && friendToRemove && (
        <div className="confirm-modal-overlay" onClick={handleCancelRemove}>
          <div className="confirm-modal" onClick={(e) => e.stopPropagation()}>
            {isRemoving ? (
              <>
                <div className="confirm-modal-loading">
                  <div className="loading-spinner-small">
                    <div className="spinner-ring"></div>
                    <div className="spinner-ring"></div>
                    <div className="spinner-ring"></div>
                  </div>
                  <p>Removing friend...</p>
                </div>
              </>
            ) : (
              <>
                <div className="confirm-modal-icon">
                  <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="12" cy="12" r="10"/>
                    <line x1="12" y1="8" x2="12" y2="12"/>
                    <line x1="12" y1="16" x2="12.01" y2="16"/>
                  </svg>
                </div>
                <h3>Remove Friend</h3>
                <p>Are you sure you want to remove <strong>{friendToRemove.username}</strong> from your friends list?</p>
                <div className="confirm-modal-actions">
                  <button 
                    className="confirm-btn confirm-btn--cancel"
                    onClick={handleCancelRemove}
                  >
                    Cancel
                  </button>
                  <button 
                    className="confirm-btn confirm-btn--remove"
                    onClick={() => handleRemoveFriend(friendToRemove.username)}
                  >
                    Remove Friend
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default FriendsModal;
