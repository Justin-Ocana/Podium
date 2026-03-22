import { useState, useEffect } from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../contexts/ToastContext';
import Navbar from '../components/Navbar';
import Card from '../components/Card';
import Avatar from '../components/Avatar';
import Button from '../components/Button';
import Badge from '../components/Badge';
import FriendsModal from '../components/FriendsModal';
import LoadingScreen from '../components/LoadingScreen';
import ParticleBackground from '../components/ParticleBackground';
import api from '../services/api';
import './Profile.css';

const Profile = () => {
  const { user: currentUser, logout } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();
  const location = useLocation();
  const { username } = useParams();
  
  const [profileUser, setProfileUser] = useState(null);
  const [stats, setStats] = useState(null);
  const [teams, setTeams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showFriendsModal, setShowFriendsModal] = useState(false);
  const [friendsModalTab, setFriendsModalTab] = useState('all');
  const [friendsCount, setFriendsCount] = useState(0);
  const [friendRequestsCount, setFriendRequestsCount] = useState(0);
  const [friendRequestSent, setFriendRequestSent] = useState(false);
  const [areFriends, setAreFriends] = useState(false);
  const [sendingRequest, setSendingRequest] = useState(false);

  const isOwnProfile = !username || (currentUser && username === currentUser.username);
  const isAuthenticated = !!currentUser;

  useEffect(() => {
    if (location.pathname === '/profile' && currentUser) {
      navigate(`/u/${currentUser.username}`, { replace: true });
      return;
    }
    
    // Only load if we have the necessary data
    if (username || currentUser) {
      loadProfileData();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [username, location.pathname]); // Removed currentUser to prevent re-renders

  useEffect(() => {
    // Check if we should open friends modal from notification
    const params = new URLSearchParams(location.search);
    if (params.get('openFriends') === 'true') {
      const tab = params.get('tab') || 'all';
      setFriendsModalTab(tab);
      setShowFriendsModal(true);
      // Clean up URL
      navigate(location.pathname, { replace: true });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.search]);

  const loadProfileData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      let userData;
      if (username) {
        userData = await api.getUserByUsername(username);
      } else if (currentUser) {
        userData = currentUser;
      } else {
        setError('User not found');
        setLoading(false);
        return;
      }

      setProfileUser(userData);
      
      if (userData?.id) {
        // Load stats and friends data
        await Promise.all([
          loadStats(userData.id),
          loadFriendsData(userData)
        ]);
        
        // Load teams AFTER profileUser is set
        await loadTeams(userData);
      }
    } catch (error) {
      console.error('Failed to load profile:', error);
      setError(error.status === 404 ? 'User not found' : 'Failed to load profile');
    } finally {
      setLoading(false);
    }
  };

  const loadFriendsData = async (userData = profileUser) => {
    // Only load friends data if user is authenticated
    const token = localStorage.getItem('token');
    if (!token) return; // Don't load if not authenticated
    
    try {
      const friends = await api.getFriends();
      setFriendsCount(friends.length);
      
      // Load friend requests count if own profile
      if (isOwnProfile) {
        const requests = await api.getFriendRequests();
        setFriendRequestsCount(requests.length);
      }
      
      // Check if viewing user is a friend
      if (!isOwnProfile && userData) {
        const isFriend = friends.some(f => f.username === userData.username);
        setAreFriends(isFriend);
        
        // Check if friend request already sent (only if not friends)
        if (!isFriend) {
          const sentRequests = await api.getSentRequests();
          const requestExists = sentRequests.some(r => r.to_user.username === userData.username);
          setFriendRequestSent(requestExists);
        } else {
          setFriendRequestSent(false); // Reset if already friends
        }
      }
    } catch (error) {
      console.error('Failed to load friends data:', error);
    }
  };

  const handleSendFriendRequest = async () => {
    if (!profileUser || sendingRequest || friendRequestSent || areFriends) return;
    
    try {
      setSendingRequest(true);
      await api.sendFriendRequest(profileUser.username);
      setFriendRequestSent(true);
      showToast(`Friend request sent to ${profileUser.username}!`, 'success');
    } catch (error) {
      console.error('Failed to send friend request:', error);
      const errorMessage = error.data?.error || 'Failed to send friend request';
      showToast(errorMessage, 'error');
      // Reload to sync state with server
      await loadFriendsData();
    } finally {
      setSendingRequest(false);
    }
  };

  const loadStats = async (userId) => {
    try {
      const userStats = await api.getUserStats(userId);
      setStats(userStats);
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const loadTeams = async (userData = profileUser) => {
    try {
      // If viewing own profile, use my_teams endpoint
      if (isOwnProfile) {
        const response = await api.getMyTeams();
        console.log('My teams response:', response);
        // Extract team objects from memberships
        const teamsList = (response.results || response || []).map(membership => membership.team);
        setTeams(teamsList);
      } else if (userData?.username) {
        // For other users, use user-specific teams endpoint
        const response = await api.getUserTeams(userData.username);
        console.log('User teams response:', response);
        // Extract team objects from memberships
        const teamsList = (response.results || response || []).map(membership => membership.team);
        setTeams(teamsList);
      }
    } catch (error) {
      console.error('Failed to load teams:', error);
      setTeams([]);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long'
    });
  };

  const hasConnections = profileUser?.steam_username || profileUser?.riot_id || profileUser?.discord_id || 
                         profileUser?.battlenet_id || profileUser?.xbox_gamertag || profileUser?.psn_id;

  if (loading) {
    return <LoadingScreen message="Loading profile..." />;
  }

  if (error) {
    return (
      <div className="page-layout">
        <ParticleBackground />
        <Navbar user={currentUser} onLogout={logout} />
        <div className="page-container">
          <Card className="profile-error">
            <h2>Profile Not Found</h2>
            <p>{error}</p>
            <Button variant="primary" onClick={() => navigate('/dashboard')}>
              Go to Dashboard
            </Button>
          </Card>
        </div>
      </div>
    );
  }

  // Mock activity feed
  const recentActivity = [
    { id: 1, type: 'match_won', text: 'Won a match', time: '2 hours ago' },
    { id: 2, type: 'team_joined', text: `Joined team "${teams[0]?.name || 'Team'}"`, time: '1 day ago' },
    { id: 3, type: 'tournament_registered', text: 'Registered for tournament', time: '3 days ago' },
  ].filter((_, i) => i === 0 || (i === 1 && teams.length > 0) || i === 2);

  return (
    <div className="page-layout">
      <ParticleBackground />
      <Navbar user={currentUser} onLogout={logout} />
      
      {showFriendsModal && (
        <FriendsModal 
          username={profileUser?.username}
          isOwnProfile={isOwnProfile}
          initialRequestsCount={friendRequestsCount}
          initialTab={friendsModalTab}
          onClose={() => {
            setShowFriendsModal(false);
            setFriendsModalTab('all'); // Reset to default
          }}
          onDataUpdate={loadFriendsData}
        />
      )}
      
      <div className="page-container profile-container">
        {/* Profile Banner */}
        <div className="profile-banner">
          <div className="profile-banner-bg" style={{
            backgroundImage: profileUser?.banner_url ? `url(${profileUser.banner_url})` : 'none'
          }}></div>
          <div className="profile-banner-content">
            <div className="profile-banner-header">
              <Avatar 
                src={profileUser?.avatar_url} 
                username={profileUser?.username}
                size="large"
                className="profile-banner-avatar"
              />
              <div className="profile-banner-title">
                <h1>{profileUser?.username}</h1>
                <p className="profile-handle">@{profileUser?.username}</p>
                <div className="profile-meta">
                  {(profileUser?.country || profileUser?.region) && (
                    <div className="profile-meta-item">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/>
                        <circle cx="12" cy="10" r="3"/>
                      </svg>
                      <span>{[profileUser?.region, profileUser?.country].filter(Boolean).join(', ')}</span>
                    </div>
                  )}
                  <button 
                    className="profile-meta-item profile-friends-btn"
                    onClick={() => setShowFriendsModal(true)}
                  >
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/>
                      <circle cx="9" cy="7" r="4"/>
                      <path d="M23 21v-2a4 4 0 00-3-3.87"/>
                      <path d="M16 3.13a4 4 0 010 7.75"/>
                    </svg>
                    <span>{friendsCount} Friends</span>
                  </button>
                  <div className="profile-meta-item">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                      <line x1="16" y1="2" x2="16" y2="6"/>
                      <line x1="8" y1="2" x2="8" y2="6"/>
                      <line x1="3" y1="10" x2="21" y2="10"/>
                    </svg>
                    <span>Joined {formatDate(profileUser?.created_at)}</span>
                  </div>
                </div>
              </div>
              <div className="profile-banner-actions">
                {isOwnProfile ? (
                  <Button variant="primary" onClick={() => navigate('/profile/edit')}>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/>
                      <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/>
                    </svg>
                    Edit Profile
                  </Button>
                ) : isAuthenticated ? (
                  <>
                    {areFriends ? (
                      <Button variant="success" disabled>
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <polyline points="20 6 9 17 4 12"/>
                        </svg>
                        Friends
                      </Button>
                    ) : friendRequestSent ? (
                      <Button variant="secondary" disabled>
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <circle cx="12" cy="12" r="10"/>
                          <polyline points="12 6 12 12 16 14"/>
                        </svg>
                        Request Sent
                      </Button>
                    ) : (
                      <Button variant="secondary" onClick={handleSendFriendRequest} loading={sendingRequest} disabled={sendingRequest}>
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M16 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/>
                          <circle cx="8.5" cy="7" r="4"/>
                          <line x1="20" y1="8" x2="20" y2="14"/>
                          <line x1="23" y1="11" x2="17" y2="11"/>
                        </svg>
                        Add Friend
                      </Button>
                    )}
                    <Button variant="secondary" onClick={() => alert('Message feature coming soon!')}>
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/>
                      </svg>
                      Message
                    </Button>
                    <Button variant="primary" onClick={() => alert('Invite to Team feature coming soon!')}>
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/>
                        <circle cx="9" cy="7" r="4"/>
                        <path d="M23 21v-2a4 4 0 00-3-3.87"/>
                        <path d="M16 3.13a4 4 0 010 7.75"/>
                      </svg>
                      Invite to Team
                    </Button>
                  </>
                ) : (
                  <Button variant="primary" onClick={() => navigate('/register')}>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M16 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/>
                      <circle cx="8.5" cy="7" r="4"/>
                      <line x1="20" y1="8" x2="20" y2="14"/>
                      <line x1="23" y1="11" x2="17" y2="11"/>
                    </svg>
                    Sign Up to Interact
                  </Button>
                )}
              </div>
            </div>
            {profileUser?.bio && (
              <div className="profile-banner-body">
                <div className="profile-banner-bio">
                  <p>{profileUser.bio}</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Dashboard Grid */}
        <div className="profile-dashboard">
          {/* Left Column */}
          <div className="profile-main">
            {/* Connections (Full Width) */}
            {hasConnections && (
                <Card className="connections-card">
                  <h3>Connections</h3>
                  <div className="connections-list">
                    {profileUser?.steam_username && (
                      <div className="connection-item">
                        <div className="connection-icon connection-icon-steam">
                          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M11.979 0C5.678 0 .511 4.86.022 11.037l6.432 2.658c.545-.371 1.203-.59 1.912-.59.063 0 .125.004.188.006l2.861-4.142V8.91c0-2.495 2.028-4.524 4.524-4.524 2.494 0 4.524 2.031 4.524 4.527s-2.03 4.525-4.524 4.525h-.105l-4.076 2.911c0 .052.004.105.004.159 0 1.875-1.515 3.396-3.39 3.396-1.635 0-3.016-1.173-3.331-2.727L.436 15.27C1.862 20.307 6.486 24 11.979 24c6.627 0 11.999-5.373 11.999-12S18.605 0 11.979 0zM7.54 18.21l-1.473-.61c.262.543.714.999 1.314 1.25 1.297.539 2.793-.076 3.332-1.375.263-.63.264-1.319.005-1.949s-.75-1.121-1.377-1.383c-.624-.26-1.29-.249-1.878-.03l1.523.63c.956.4 1.409 1.5 1.009 2.455-.397.957-1.497 1.41-2.454 1.012H7.54zm11.415-9.303c0-1.662-1.353-3.015-3.015-3.015-1.665 0-3.015 1.353-3.015 3.015 0 1.665 1.35 3.015 3.015 3.015 1.663 0 3.015-1.35 3.015-3.015zm-5.273-.005c0-1.252 1.013-2.266 2.265-2.266 1.249 0 2.266 1.014 2.266 2.266 0 1.251-1.017 2.265-2.266 2.265-1.253 0-2.265-1.014-2.265-2.265z"/>
                          </svg>
                        </div>
                        <div className="connection-info">
                          <span className="connection-platform">Steam</span>
                          {profileUser.steam_url ? (
                            <a href={profileUser.steam_url} target="_blank" rel="noopener noreferrer" className="connection-username">
                              {profileUser.steam_username}
                            </a>
                          ) : (
                            <span className="connection-username">{profileUser.steam_username}</span>
                          )}
                        </div>
                        <span className="connection-status">✓ Connected</span>
                      </div>
                    )}
                    {profileUser?.riot_id && (
                      <div className="connection-item">
                        <div className="connection-icon connection-icon-riot">
                          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M12.534 21.77l-1.09-2.81 10.52.54-.451 4.5zM15.06 0L.307 6.969 2.59 17.471H5.6l-.52-7.512.461-.144 1.81 7.656h3.126l-.116-9.15.462-.144 1.582 9.294h3.31l.78-11.053.462-.144.82 11.197h4.376l1.54-15.37Z"/>
                          </svg>
                        </div>
                        <div className="connection-info">
                          <span className="connection-platform">Riot ID</span>
                          <span className="connection-username">{profileUser.riot_id}</span>
                        </div>
                        <span className="connection-status">✓ Connected</span>
                      </div>
                    )}
                    {profileUser?.discord_id && (
                      <div className="connection-item">
                        <div className="connection-icon connection-icon-discord">
                          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057 19.9 19.9 0 0 0 5.993 3.03.078.078 0 0 0 .084-.028c.462-.63.874-1.295 1.226-1.994a.076.076 0 0 0-.041-.106 13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008-.128 10.2 10.2 0 0 0 .372-.292.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0 a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.892.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z"/>
                          </svg>
                        </div>
                        <div className="connection-info">
                          <span className="connection-platform">Discord</span>
                          <span className="connection-username">{profileUser.discord_id}</span>
                        </div>
                        <span className="connection-status">✓ Connected</span>
                      </div>
                    )}
                    {profileUser?.battlenet_id && (
                      <div className="connection-item">
                        <div className="connection-icon connection-icon-battlenet">
                          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M11.907 8.624c-.261 0-.48.037-.672.112-.192.075-.352.18-.48.315-.128.136-.224.298-.288.486-.064.189-.096.396-.096.621 0 .224.032.43.096.618.064.187.16.349.288.486.128.136.288.241.48.315.192.075.411.112.672.112.261 0 .48-.037.672-.112.192-.074.352-.179.48-.315.128-.137.224-.299.288-.486.064-.188.096-.394.096-.618 0-.225-.032-.432-.096-.621-.064-.188-.16-.35-.288-.486-.128-.135-.288-.24-.48-.315-.192-.075-.411-.112-.672-.112zm0-8.624C5.373 0 0 5.373 0 12s5.373 12 11.907 12c6.533 0 11.906-5.373 11.906-12S18.44 0 11.907 0zm6.384 15.168c-.288.544-.672 1.024-1.152 1.44-.48.416-1.024.736-1.632.96-.608.224-1.248.336-1.92.336-.672 0-1.312-.112-1.92-.336-.608-.224-1.152-.544-1.632-.96-.48-.416-.864-.896-1.152-1.44-.288-.544-.432-1.136-.432-1.776 0-.64.144-1.232.432-1.776.288-.544.672-1.024 1.152-1.44.48-.416 1.024-.736 1.632-.96.608-.224 1.248-.336 1.92-.336.672 0 1.312.112 1.92.336.608.224 1.152.544 1.632.96.48.416.864.896 1.152 1.44.288.544.432 1.136.432 1.776 0 .64-.144 1.232-.432 1.776z"/>
                          </svg>
                        </div>
                        <div className="connection-info">
                          <span className="connection-platform">Battle.net</span>
                          <span className="connection-username">{profileUser.battlenet_id}</span>
                        </div>
                        <span className="connection-status">✓ Connected</span>
                      </div>
                    )}
                    {profileUser?.xbox_gamertag && (
                      <div className="connection-item">
                        <div className="connection-icon connection-icon-xbox">
                          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M4.102 21.033A11.947 11.947 0 0 0 12 24a11.96 11.96 0 0 0 7.902-2.967c1.877-1.912-4.316-8.709-7.902-11.417-3.582 2.708-9.779 9.505-7.898 11.417zm11.16-14.406c2.5 2.961 7.484 10.313 6.076 12.912A11.942 11.942 0 0 0 24 12.004a11.95 11.95 0 0 0-3.57-8.536 12.607 12.607 0 0 0-5.168 3.159zM12 0C9.348 0 6.872.959 4.898 2.565a12.607 12.607 0 0 0-5.168-3.159A11.95 11.95 0 0 0 0 12.004c0 2.893 1.027 5.547 2.738 7.535 1.408-2.599 3.592-9.951 6.092-12.912C10.32 5.094 11.178 4.109 12 3.285c.822.824 1.68 1.809 3.17 3.342z"/>
                          </svg>
                        </div>
                        <div className="connection-info">
                          <span className="connection-platform">Xbox</span>
                          <span className="connection-username">{profileUser.xbox_gamertag}</span>
                        </div>
                        <span className="connection-status">✓ Connected</span>
                      </div>
                    )}
                    {profileUser?.psn_id && (
                      <div className="connection-item">
                        <div className="connection-icon connection-icon-playstation">
                          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                            <path d="M8.985 2.596v17.548l3.915 1.261V6.688c0-.69.304-1.151.794-.991.636.181.794.814.794 1.505v5.876c2.441 1.193 4.362-.002 4.362-3.153 0-3.237-1.126-4.675-4.438-5.827-1.307-.448-3.728-1.186-5.427-1.502zm4.656 16.242l6.296-2.275c.715-.258.826-.625.246-.818-.586-.192-1.637-.139-2.357.123l-4.205 1.5v-2.042l.24-.085s1.201-.42 2.913-.615c1.696-.18 3.785.029 5.437.661 1.848.601 2.041 1.472 1.576 2.072-.465.6-1.622 1.036-1.622 1.036l-8.544 3.107V18.84l.02-.002zM1.808 18.6c-1.9-.545-2.214-1.668-1.352-2.321.801-.585 2.159-1.051 2.159-1.051l5.616-2.013v2.155L4.181 16.83c-.718.258-.826.625-.246.818.586.192 1.637.139 2.357-.123l2.939-1.039v1.795c-.121.029-.256.044-.391.073-2.009.405-4.165.266-6.032-.154z"/>
                          </svg>
                        </div>
                        <div className="connection-info">
                          <span className="connection-platform">PlayStation</span>
                          <span className="connection-username">{profileUser.psn_id}</span>
                        </div>
                        <span className="connection-status">✓ Connected</span>
                      </div>
                    )}
                  </div>
                </Card>
              )}

            {/* Teams + Tournament History Row */}
            <div className="profile-row">
              {/* Teams */}
              <Card className="teams-card">
                <h3>Teams</h3>
                {teams.length > 0 ? (
                  <div className="teams-list">
                    {teams.map(team => {
                      const primaryColor = team.primary_color || '#6366f1';
                      const secondaryColor = team.secondary_color || '#8b5cf6';
                      
                      return (
                        <div 
                          key={team.id} 
                          className="team-item"
                          onClick={() => navigate(`/teams/${team.slug}`)}
                          style={{
                            borderLeft: `3px solid ${primaryColor}`,
                            boxShadow: `0 0 20px ${primaryColor}15`
                          }}
                        >
                          {/* Avatar */}
                          {team.logo_url && (
                            <div 
                              className="team-item-avatar"
                              style={{
                                boxShadow: `0 0 0 2px ${primaryColor}, 0 0 15px ${primaryColor}40`
                              }}
                            >
                              <img src={team.logo_url} alt={`${team.name} logo`} />
                            </div>
                          )}
                          
                          {/* Info */}
                          <div className="team-item-info">
                            <div className="team-item-header">
                              <h4 
                                className="team-item-name"
                                style={{ 
                                  color: primaryColor
                                }}
                              >
                                {team.name}
                              </h4>
                              <span 
                                className="team-item-tag"
                                style={{
                                  borderColor: `${secondaryColor}66`,
                                  color: secondaryColor
                                }}
                              >
                                [{team.tag}]
                              </span>
                            </div>
                            
                            {/* Game */}
                            {team.game && (
                              <div className="team-item-game">
                                {team.game.cover_url && (
                                  <img 
                                    src={team.game.cover_url} 
                                    alt={team.game.name}
                                    className="team-item-game-cover"
                                  />
                                )}
                                <span>{team.game.name}</span>
                              </div>
                            )}
                          </div>
                          
                          {/* Action */}
                          <div className="team-item-action">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                              <polyline points="9 18 15 12 9 6"/>
                            </svg>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                ) : isOwnProfile ? (
                  <div className="empty-state">
                    <p className="empty-state-title">No teams yet</p>
                    <p className="empty-state-text">Join or create a team to compete</p>
                    <Button variant="primary" onClick={() => navigate('/teams')}>
                      Explore Teams
                    </Button>
                  </div>
                ) : (
                  <div className="empty-state">
                    <p className="empty-state-title">No teams yet</p>
                  </div>
                )}
              </Card>

              {/* Tournament History */}
              <Card className="tournament-history-card">
                <h3>Tournament History</h3>
                {stats?.tournaments_played_count > 0 ? (
                  <div className="tournament-history-list">
                    <div className="tournament-history-item">
                      <h4>Recent Tournament</h4>
                      <p>{stats.tournaments_played_count} tournament{stats.tournaments_played_count !== 1 ? 's' : ''} played</p>
                    </div>
                  </div>
                ) : isOwnProfile ? (
                  <div className="empty-state">
                    <div className="empty-state-icon">
                      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                        <path d="M7 3V1h10v2h5v6c0 2.21-1.79 4-4 4h-.54c-.77 1.76-2.31 3.12-4.21 3.57L13 21h4v2H7v-2h4l-.25-4.43C8.85 16.12 7.31 14.76 6.54 13H6c-2.21 0-4-1.79-4-4V3h5z"/>
                      </svg>
                    </div>
                    <p className="empty-state-title">No tournament history</p>
                    <p className="empty-state-text">Compete in tournaments to build your record</p>
                    <Button variant="primary" onClick={() => navigate('/tournaments')}>
                      Browse Tournaments
                    </Button>
                  </div>
                ) : (
                  <div className="empty-state">
                    <div className="empty-state-icon">
                      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                        <path d="M7 3V1h10v2h5v6c0 2.21-1.79 4-4 4h-.54c-.77 1.76-2.31 3.12-4.21 3.57L13 21h4v2H7v-2h4l-.25-4.43C8.85 16.12 7.31 14.76 6.54 13H6c-2.21 0-4-1.79-4-4V3h5z"/>
                      </svg>
                    </div>
                    <p className="empty-state-title">No tournament history</p>
                  </div>
                )}
              </Card>
            </div>

            {/* Recent Activity */}
            {recentActivity.length > 0 && (
              <Card className="activity-card">
                <h3>Recent Activity</h3>
                <div className="activity-feed">
                  {recentActivity.map(activity => (
                    <div key={activity.id} className="activity-item">
                      <div className="activity-icon">
                        {activity.type === 'match_won' && (
                          <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                            <path d="M9 16.2L4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4L9 16.2z" fill="currentColor"/>
                          </svg>
                        )}
                        {activity.type === 'team_joined' && (
                          <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                            <path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z" fill="currentColor"/>
                          </svg>
                        )}
                        {activity.type === 'tournament_registered' && (
                          <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                            <path d="M7 3V1h10v2h5v6c0 2.21-1.79 4-4 4h-.54c-.77 1.76-2.31 3.12-4.21 3.57L13 21h4v2H7v-2h4l-.25-4.43C8.85 16.12 7.31 14.76 6.54 13H6c-2.21 0-4-1.79-4-4V3h5z" fill="currentColor"/>
                          </svg>
                        )}
                      </div>
                      <div className="activity-content">
                        <p className="activity-text">{activity.text}</p>
                        <span className="activity-time">{activity.time}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            )}
          </div>

          {/* Right Column - Stats Cards */}
          <div className="profile-sidebar">
            <div className="stats-widgets">
              <Card className="stat-widget stat-widget-highlight">
                <div className="stat-widget-value">
                  {stats?.winrate ? `${stats.winrate.toFixed(1)}%` : '0%'}
                </div>
                <div className="stat-widget-label">Win Rate</div>
                {stats?.winrate > 0 && (
                  <div className="stat-progress">
                    <div 
                      className="stat-progress-bar" 
                      style={{ width: `${Math.min(stats.winrate, 100)}%` }}
                    ></div>
                  </div>
                )}
              </Card>

              <Card className="stat-widget">
                <div className="stat-widget-value">{stats?.matches_played_count || 0}</div>
                <div className="stat-widget-label">Matches Played</div>
              </Card>

              <Card className="stat-widget">
                <div className="stat-widget-value">{stats?.matches_won_count || 0}</div>
                <div className="stat-widget-label">Matches Won</div>
              </Card>

              <Card className="stat-widget">
                <div className="stat-widget-value">{stats?.teams_count || 0}</div>
                <div className="stat-widget-label">Teams</div>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;
