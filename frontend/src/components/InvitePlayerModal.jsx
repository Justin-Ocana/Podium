import { useState, useEffect } from 'react';
import { useToast } from '../contexts/ToastContext';
import Card from './Card';
import Avatar from './Avatar';
import Button from './Button';
import Input from './Input';
import api from '../services/api';
import './InvitePlayerModal.css';

const InvitePlayerModal = ({ isOpen, onClose, team }) => {
  const { showToast } = useToast();
  const [activeTab, setActiveTab] = useState('friends');
  const [friends, setFriends] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen && activeTab === 'friends') {
      loadFriends();
    }
  }, [isOpen, activeTab]);

  useEffect(() => {
    if (searchQuery.length >= 2) {
      const timer = setTimeout(() => {
        searchUsers();
      }, 300);
      return () => clearTimeout(timer);
    } else {
      setSearchResults([]);
    }
  }, [searchQuery]);

  const loadFriends = async () => {
    try {
      setLoading(true);
      const data = await api.getFriends();
      setFriends(data.results || data || []);
    } catch (error) {
      console.error('Failed to load friends:', error);
    } finally {
      setLoading(false);
    }
  };

  const searchUsers = async () => {
    try {
      setLoading(true);
      const data = await api.searchUsers(searchQuery);
      setSearchResults(data.results || data || []);
      console.log('Search results:', data);
    } catch (error) {
      console.error('Failed to search users:', error);
      setSearchResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleInvite = (username) => {
    // TODO: Implement invite functionality when backend is ready
    console.log('Invite player:', username);
    // showToast(`Invite sent to ${username}`, 'success');
  };

  const handleCopyLink = () => {
    // TODO: Generate and copy invite link when backend is ready
    console.log('Copy invite link');
    // showToast('Invite link copied to clipboard', 'success');
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div 
        className="modal-content invite-modal" 
        onClick={(e) => e.stopPropagation()}
        style={{ '--team-primary-color': team.primary_color || '#6366f1' }}
      >
        <div className="modal-header">
          <h2>Invite Players to {team.name}</h2>
          <button className="modal-close-btn" onClick={onClose}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        {/* Tabs */}
        <div className="invite-tabs">
          <button
            className={`invite-tab ${activeTab === 'friends' ? 'active' : ''}`}
            onClick={() => setActiveTab('friends')}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/>
              <circle cx="9" cy="7" r="4"/>
              <path d="M23 21v-2a4 4 0 00-3-3.87"/>
              <path d="M16 3.13a4 4 0 010 7.75"/>
            </svg>
            Friends
          </button>
          <button
            className={`invite-tab ${activeTab === 'search' ? 'active' : ''}`}
            onClick={() => setActiveTab('search')}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="11" cy="11" r="8"/>
              <path d="M21 21l-4.35-4.35"/>
            </svg>
            Search User
          </button>
          <button
            className={`invite-tab ${activeTab === 'link' ? 'active' : ''}`}
            onClick={() => setActiveTab('link')}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71"/>
              <path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71"/>
            </svg>
            Generate Link
          </button>
        </div>

        {/* Tab Content */}
        <div className="invite-tab-content">
          {/* Friends Tab */}
          {activeTab === 'friends' && (
            <div className="friends-list">
              {loading ? (
                <p className="loading-text">Loading friends...</p>
              ) : friends.length > 0 ? (
                friends.map((friend) => (
                  <div key={friend.id} className="friend-item">
                    <Avatar 
                      src={friend.avatar_url} 
                      username={friend.username}
                      size="medium"
                    />
                    <div className="friend-info">
                      <span className="friend-username">{friend.username}</span>
                    </div>
                    <Button 
                      variant="primary" 
                      size="small"
                      onClick={() => handleInvite(friend.username)}
                      style={{
                        background: `linear-gradient(135deg, ${team.primary_color || '#6366f1'} 0%, ${team.secondary_color || '#8b5cf6'} 100%)`,
                        borderColor: team.primary_color || '#6366f1'
                      }}
                    >
                      Invite
                    </Button>
                  </div>
                ))
              ) : (
                <div className="empty-state">
                  <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                    <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/>
                    <circle cx="9" cy="7" r="4"/>
                    <path d="M23 21v-2a4 4 0 00-3-3.87"/>
                    <path d="M16 3.13a4 4 0 010 7.75"/>
                  </svg>
                  <p>No friends to invite</p>
                </div>
              )}
            </div>
          )}

          {/* Search Tab */}
          {activeTab === 'search' && (
            <div className="search-users">
              <Input
                type="text"
                placeholder="Search by username..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                icon={
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="11" cy="11" r="8"/>
                    <path d="M21 21l-4.35-4.35"/>
                  </svg>
                }
              />
              <div className="search-results">
                {loading ? (
                  <p className="loading-text">Searching...</p>
                ) : searchQuery.length < 2 ? (
                  <p className="hint-text">Type at least 2 characters to search</p>
                ) : searchResults.length > 0 ? (
                  searchResults.map((user) => (
                    <div key={user.id} className="friend-item">
                      <Avatar 
                        src={user.avatar_url} 
                        username={user.username}
                        size="medium"
                      />
                      <div className="friend-info">
                        <span className="friend-username">{user.username}</span>
                      </div>
                      <Button 
                        variant="primary" 
                        size="small"
                        onClick={() => handleInvite(user.username)}
                        style={{
                          background: `linear-gradient(135deg, ${team.primary_color || '#6366f1'} 0%, ${team.secondary_color || '#8b5cf6'} 100%)`,
                          borderColor: team.primary_color || '#6366f1'
                        }}
                      >
                        Invite
                      </Button>
                    </div>
                  ))
                ) : (
                  <div className="empty-state">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                      <circle cx="11" cy="11" r="8"/>
                      <path d="M21 21l-4.35-4.35"/>
                    </svg>
                    <p>No users found</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Link Tab */}
          {activeTab === 'link' && (
            <div className="generate-link">
              <div className="link-info">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71"/>
                  <path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71"/>
                </svg>
                <h3>Share Invite Link</h3>
                <p>Generate a link that anyone can use to request to join your team</p>
              </div>
              <Button 
                variant="primary" 
                onClick={handleCopyLink}
                style={{ width: '100%' }}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                  <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/>
                </svg>
                Copy Invite Link
              </Button>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="modal-footer">
          <Button 
            variant="ghost" 
            onClick={onClose}
            className="btn-cancel"
          >
            Cancel
          </Button>
          <Button 
            variant="primary"
            onClick={onClose}
            disabled={activeTab === 'link'}
          >
            Done
          </Button>
        </div>
      </div>
    </div>
  );
};

export default InvitePlayerModal;
