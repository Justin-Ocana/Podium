import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import Navbar from '../components/Navbar';
import Card from '../components/Card';
import Avatar from '../components/Avatar';
import Button from '../components/Button';
import Badge from '../components/Badge';
import Input from '../components/Input';
import LoadingScreen from '../components/LoadingScreen';
import ParticleBackground from '../components/ParticleBackground';
import InvitePlayerModal from '../components/InvitePlayerModal';
import TeamLogoCropModal from '../components/TeamLogoCropModal';
import BannerPreviewModal from '../components/BannerPreviewModal';
import { useToast } from '../contexts/ToastContext';
import api from '../services/api';
import './ManageTeam.css';

const ManageTeam = () => {
  const { slug } = useParams();
  const { user, logout } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();
  
  const [team, setTeam] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeSection, setActiveSection] = useState('overview');
  const [members, setMembers] = useState([]);
  const [requests, setRequests] = useState([]);

  useEffect(() => {
    loadTeamData();
  }, [slug]);

  const loadTeamData = async () => {
    try {
      const teamData = await api.getTeam(slug);
      setTeam(teamData);
      
      // Load members
      await loadMembers(teamData.id);
      
      // TODO: Load requests when endpoint is ready
      setRequests([]);
    } catch (error) {
      console.error('Failed to load team:', error);
      showToast('Failed to load team', 'error');
      navigate('/my-teams');
    } finally {
      setLoading(false);
    }
  };

  const loadMembers = async (teamId) => {
    try {
      const membersData = await api.getTeamMembers(teamId);
      setMembers(membersData);
    } catch (error) {
      console.error('Failed to load members:', error);
    }
  };

  const handleDeleteTeam = async () => {
    if (window.confirm(`Are you sure you want to delete ${team.name}? This action cannot be undone.`)) {
      try {
        await api.deleteTeam(team.id);
        showToast('Team deleted successfully', 'success');
        navigate('/my-teams');
      } catch (error) {
        showToast('Failed to delete team', 'error');
      }
    }
  };

  if (loading) {
    return <LoadingScreen message="Loading team..." />;
  }

  if (!team) {
    return null;
  }

  const pendingRequestsCount = requests.length;

  return (
    <div className="manage-team-layout">
      <ParticleBackground />
      <Navbar user={user} onLogout={logout} />
      
      <div className="manage-team-container">
        {/* Breadcrumb */}
        <div className="breadcrumb">
          <span onClick={() => navigate('/teams')} className="breadcrumb-link">Teams</span>
          <span className="breadcrumb-separator">›</span>
          <span onClick={() => navigate(`/teams/${team.slug}`)} className="breadcrumb-link">{team.name}</span>
          <span className="breadcrumb-separator">›</span>
          <span className="breadcrumb-current">Manage</span>
        </div>

        <div className="manage-team-content">
          {/* Sidebar */}
          <aside className="manage-sidebar">
            {/* Mini Team Card */}
            <Card className="sidebar-team-card">
              <div 
                className="sidebar-team-banner"
                style={{
                  backgroundImage: team.banner_url 
                    ? `url(${team.banner_url})` 
                    : `linear-gradient(135deg, ${team.primary_color || '#6366f1'} 0%, ${team.secondary_color || '#8b5cf6'} 100%)`
                }}
              />
              <div className="sidebar-team-info">
                <Avatar 
                  src={team.logo_url} 
                  username={team.name}
                  size="medium"
                  className="sidebar-team-avatar"
                />
                <h3 style={{ color: team.primary_color || 'var(--text-main)' }}>
                  {team.name}
                </h3>
                <Badge 
                  variant="secondary" 
                  className="sidebar-team-tag"
                  style={{ borderColor: `${team.primary_color || '#6366f1'}40` }}
                >
                  [{team.tag}]
                </Badge>
                {team.game && (
                  <Badge variant="primary" className="sidebar-team-game">
                    {team.game.cover_url && (
                      <img src={team.game.cover_url} alt={team.game.name} />
                    )}
                    {team.game.name}
                  </Badge>
                )}
              </div>
            </Card>

            <div className="sidebar-divider" />

            {/* Navigation */}
            <nav className="sidebar-nav">
              <button
                className={`sidebar-nav-item ${activeSection === 'overview' ? 'active' : ''}`}
                onClick={() => setActiveSection('overview')}
                style={activeSection === 'overview' ? {
                  background: `rgba(${hexToRgb(team.primary_color || '#6366f1')}, 0.12)`,
                  borderLeftColor: team.primary_color || '#6366f1',
                  color: team.primary_color || '#6366f1'
                } : {}}
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="3" y="3" width="7" height="7"/>
                  <rect x="14" y="3" width="7" height="7"/>
                  <rect x="14" y="14" width="7" height="7"/>
                  <rect x="3" y="14" width="7" height="7"/>
                </svg>
                Overview
              </button>

              <button
                className={`sidebar-nav-item ${activeSection === 'members' ? 'active' : ''}`}
                onClick={() => setActiveSection('members')}
                style={activeSection === 'members' ? {
                  background: `rgba(${hexToRgb(team.primary_color || '#6366f1')}, 0.12)`,
                  borderLeftColor: team.primary_color || '#6366f1',
                  color: team.primary_color || '#6366f1'
                } : {}}
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/>
                  <circle cx="9" cy="7" r="4"/>
                  <path d="M23 21v-2a4 4 0 00-3-3.87"/>
                  <path d="M16 3.13a4 4 0 010 7.75"/>
                </svg>
                Members
              </button>

              <button
                className={`sidebar-nav-item ${activeSection === 'requests' ? 'active' : ''}`}
                onClick={() => setActiveSection('requests')}
                style={activeSection === 'requests' ? {
                  background: `rgba(${hexToRgb(team.primary_color || '#6366f1')}, 0.12)`,
                  borderLeftColor: team.primary_color || '#6366f1',
                  color: team.primary_color || '#6366f1'
                } : {}}
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/>
                </svg>
                Requests
                {pendingRequestsCount > 0 && (
                  <Badge variant="warning" className="sidebar-badge-count">
                    {pendingRequestsCount}
                  </Badge>
                )}
              </button>

              <button
                className={`sidebar-nav-item ${activeSection === 'tournaments' ? 'active' : ''}`}
                onClick={() => setActiveSection('tournaments')}
                style={activeSection === 'tournaments' ? {
                  background: `rgba(${hexToRgb(team.primary_color || '#6366f1')}, 0.12)`,
                  borderLeftColor: team.primary_color || '#6366f1',
                  color: team.primary_color || '#6366f1'
                } : {}}
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M6 9H4.5a2.5 2.5 0 010-5H6"/>
                  <path d="M18 9h1.5a2.5 2.5 0 000-5H18"/>
                  <path d="M4 22h16"/>
                  <path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"/>
                  <path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"/>
                  <path d="M18 2H6v7a6 6 0 0012 0V2z"/>
                </svg>
                Tournaments
              </button>

              <button
                className={`sidebar-nav-item ${activeSection === 'edit' ? 'active' : ''}`}
                onClick={() => setActiveSection('edit')}
                style={activeSection === 'edit' ? {
                  background: `rgba(${hexToRgb(team.primary_color || '#6366f1')}, 0.12)`,
                  borderLeftColor: team.primary_color || '#6366f1',
                  color: team.primary_color || '#6366f1'
                } : {}}
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/>
                  <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/>
                </svg>
                Edit Team
              </button>
            </nav>

            {/* Danger Zone */}
            <div className="sidebar-danger-zone">
              <h4>Danger Zone</h4>
              <Button 
                variant="ghost" 
                className="btn-delete-team"
                onClick={handleDeleteTeam}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <polyline points="3 6 5 6 21 6"/>
                  <path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
                </svg>
                Delete Team
              </Button>
            </div>
          </aside>

          {/* Main Content */}
          <main className="manage-main-content">
            {activeSection === 'overview' && <OverviewSection team={team} members={members} requests={requests} />}
            {activeSection === 'members' && <MembersSection team={team} members={members} onReload={loadTeamData} />}
            {activeSection === 'requests' && <RequestsSection team={team} requests={requests} onReload={loadTeamData} />}
            {activeSection === 'tournaments' && <TournamentsSection team={team} />}
            {activeSection === 'edit' && <EditSection team={team} onReload={loadTeamData} />}
          </main>
        </div>
      </div>
    </div>
  );
};

// Helper function
const hexToRgb = (hex) => {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result 
    ? `${parseInt(result[1], 16)}, ${parseInt(result[2], 16)}, ${parseInt(result[3], 16)}`
    : '99, 102, 241';
};

// Overview Section Component
const OverviewSection = ({ team, members, requests }) => {
  const stats = [
    { label: 'MEMBERS', value: team.member_count || 0, icon: '👥' },
    { label: 'TOURNAMENTS', value: 0, icon: '🏆' },
    { label: 'MATCHES WON', value: 0, icon: '🎯' },
    { label: 'PENDING REQUESTS', value: requests.length, icon: '📩', highlight: requests.length > 0 }
  ];

  const completeness = calculateCompleteness(team);
  const completeFields = ['Banner', 'Logo', 'Game', 'Name', 'Tag'].filter(f => {
    if (f === 'Banner') return team.banner_url;
    if (f === 'Logo') return team.logo_url;
    if (f === 'Game') return team.game;
    return true;
  });

  return (
    <div className="overview-section">
      <h2 className="section-header" style={{ borderLeftColor: team.primary_color || '#6366f1' }}>
        Overview
      </h2>

      {/* Stats Grid */}
      <div className="stats-grid">
        {stats.map((stat, index) => (
          <Card 
            key={index} 
            className={`stat-card ${stat.highlight ? 'stat-card-highlight' : ''}`}
            style={stat.highlight ? {
              borderColor: 'rgba(251, 191, 36, 0.3)',
              background: 'rgba(251, 191, 36, 0.05)',
              boxShadow: '0 8px 40px rgba(0, 0, 0, 0.4), 0 0 20px rgba(251, 191, 36, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.06)'
            } : {}}
          >
            <div className="stat-value">{stat.value}</div>
            <div className="stat-label">{stat.label}</div>
          </Card>
        ))}
      </div>

      {/* Team Completeness */}
      <Card className="completeness-card">
        <h3>Team Completeness</h3>
        <div className="completeness-bar-container">
          <div className="completeness-bar">
            <div 
              className="completeness-bar-fill"
              style={{ 
                width: `${completeness.percentage}%`,
                background: team.primary_color || '#6366f1'
              }}
            />
          </div>
          <span className="completeness-percentage">{completeness.percentage}%</span>
        </div>
        <div className="completeness-items">
          {completeFields.map((item, index) => (
            <Badge key={index} variant="success" className="completeness-item-badge">
              ✓ {item}
            </Badge>
          ))}
          {completeness.missing.map((item, index) => (
            <Badge key={index} variant="secondary" className="completeness-item-badge missing">
              ⚠ {item}
            </Badge>
          ))}
        </div>
      </Card>

      {/* Recent Activity */}
      <Card className="activity-card">
        <h3>Recent Activity</h3>
        <div className="activity-list">
          <div className="activity-item">
            <span className="activity-dot" style={{ background: team.primary_color || '#6366f1' }}></span>
            <span className="activity-text">Team created</span>
            <span className="activity-time">{formatDate(team.created_at)}</span>
          </div>
        </div>
      </Card>
    </div>
  );
};

// Members Section Component
const MembersSection = ({ team, members, onReload }) => {
  const { showToast } = useToast();
  const [menuOpen, setMenuOpen] = useState(null);
  const [showInviteModal, setShowInviteModal] = useState(false);

  const handleRemoveMember = async (memberId, username) => {
    if (window.confirm(`Are you sure you want to remove ${username} from the team?`)) {
      try {
        await api.removeMember(team.id, memberId);
        showToast('Member removed successfully', 'success');
        onReload();
      } catch (error) {
        showToast('Failed to remove member', 'error');
      }
    }
    setMenuOpen(null);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', { 
      month: 'short', 
      year: 'numeric' 
    });
  };

  return (
    <div className="members-section">
      <div className="section-header-row">
        <h2 className="section-header" style={{ borderLeftColor: team.primary_color || '#6366f1' }}>
          Members ({members.length})
        </h2>
        <Button 
          variant="primary" 
          className="btn-invite"
          onClick={() => setShowInviteModal(true)}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="12" y1="5" x2="12" y2="19"/>
            <line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
          Invite Player
        </Button>
      </div>

      <InvitePlayerModal 
        isOpen={showInviteModal}
        onClose={() => setShowInviteModal(false)}
        team={team}
      />

      <Card className="members-table-card">
        {members.length > 0 ? (
          <div className="members-table">
            <div className="members-table-header">
              <div className="member-col-avatar">Member</div>
              <div className="member-col-role">Role</div>
              <div className="member-col-joined">Joined</div>
              <div className="member-col-actions">Actions</div>
            </div>
            <div className="members-table-body">
              {members.map((member) => (
                <div key={member.id} className="member-row">
                  <div className="member-col-avatar">
                    <Avatar 
                      src={member.user.avatar_url} 
                      username={member.user.username}
                      size="small"
                    />
                    <span className="member-username">{member.user.username}</span>
                  </div>
                  <div className="member-col-role">
                    {member.role === 'captain' ? (
                      <Badge variant="warning" className="role-badge-captain">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
                          <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z"/>
                        </svg>
                        Captain
                      </Badge>
                    ) : (
                      <Badge variant="secondary" className="role-badge-member">
                        Member
                      </Badge>
                    )}
                  </div>
                  <div className="member-col-joined">
                    {formatDate(member.joined_at)}
                  </div>
                  <div className="member-col-actions">
                    {member.role !== 'captain' ? (
                      <div className="member-actions-menu">
                        <button 
                          className="member-menu-btn"
                          onClick={() => setMenuOpen(menuOpen === member.id ? null : member.id)}
                        >
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <circle cx="12" cy="12" r="1"/>
                            <circle cx="12" cy="5" r="1"/>
                            <circle cx="12" cy="19" r="1"/>
                          </svg>
                        </button>
                        {menuOpen === member.id && (
                          <div className="member-dropdown">
                            <button 
                              className="member-dropdown-item danger"
                              onClick={() => handleRemoveMember(member.user.id, member.user.username)}
                            >
                              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <polyline points="3 6 5 6 21 6"/>
                                <path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
                              </svg>
                              Remove from team
                            </button>
                          </div>
                        )}
                      </div>
                    ) : (
                      <span className="member-no-actions">—</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <p className="empty-state-text">No members yet</p>
        )}
      </Card>
    </div>
  );
};

// Requests Section Component
const RequestsSection = ({ team, requests }) => {
  return (
    <div className="requests-section">
      <h2 className="section-header" style={{ borderLeftColor: team.primary_color || '#6366f1' }}>
        Join Requests
      </h2>

      {requests.length === 0 ? (
        <Card className="empty-state-card">
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
            <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/>
          </svg>
          <h3>No pending requests</h3>
          <p>Players who apply to join will appear here</p>
        </Card>
      ) : (
        <div className="requests-list">
          {/* TODO: Render requests */}
        </div>
      )}
    </div>
  );
};

// Tournaments Section Component
const TournamentsSection = ({ team }) => {
  return (
    <div className="tournaments-section">
      <h2 className="section-header" style={{ borderLeftColor: team.primary_color || '#6366f1' }}>
        Tournaments
      </h2>

      <Card className="empty-state-card">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <path d="M6 9H4.5a2.5 2.5 0 010-5H6"/>
          <path d="M18 9h1.5a2.5 2.5 0 000-5H18"/>
          <path d="M4 22h16"/>
          <path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"/>
          <path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"/>
          <path d="M18 2H6v7a6 6 0 0012 0V2z"/>
        </svg>
        <h3>No tournaments yet</h3>
        <p>Your team hasn't participated in any tournaments</p>
        <Button variant="primary">Browse Tournaments</Button>
      </Card>
    </div>
  );
};

// Edit Section Component
const EditSection = ({ team, onReload }) => {
  const { showToast } = useToast();
  
  const [formData, setFormData] = useState({
    name: team.name || '',
    tag: team.tag || '',
    game: team.game || null,
    description: team.description || '',
    country: team.country || '',
    region: team.region || '',
    primary_color: team.primary_color || '#ff4655',
    secondary_color: team.secondary_color || '#111111',
    looking_for_players: team.looking_for_players || false
  });
  
  const [logoFile, setLogoFile] = useState(null);
  const [logoPreview, setLogoPreview] = useState(team.logo_url || null);
  const [bannerFile, setBannerFile] = useState(null);
  const [bannerPreview, setBannerPreview] = useState(team.banner_url || null);
  
  const [showLogoCropModal, setShowLogoCropModal] = useState(false);
  const [showBannerModal, setShowBannerModal] = useState(false);
  const [tempLogoImage, setTempLogoImage] = useState(null);
  const [tempBannerImage, setTempBannerImage] = useState(null);
  
  const [gameSearch, setGameSearch] = useState('');
  const [games, setGames] = useState([]);
  const [searchingGames, setSearchingGames] = useState(false);
  const [showGameResults, setShowGameResults] = useState(false);
  
  const [submitting, setSubmitting] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  // Search games
  useEffect(() => {
    if (gameSearch.length >= 2) {
      const timer = setTimeout(async () => {
        setSearchingGames(true);
        try {
          const data = await api.searchGames(gameSearch);
          setGames(data.results || []);
          setShowGameResults(true);
        } catch (error) {
          console.error('Failed to search games:', error);
          setGames([]);
        } finally {
          setSearchingGames(false);
        }
      }, 300);
      return () => clearTimeout(timer);
    } else {
      setGames([]);
      setShowGameResults(false);
    }
  }, [gameSearch]);

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
    setHasChanges(true);
  };

  const handleLogoChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) {
        showToast('Logo must be less than 5MB', 'error');
        return;
      }
      const reader = new FileReader();
      reader.onload = () => {
        setTempLogoImage(reader.result);
        setShowLogoCropModal(true);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleLogoSave = (croppedFile) => {
    setLogoFile(croppedFile);
    setLogoPreview(URL.createObjectURL(croppedFile));
    setShowLogoCropModal(false);
    setTempLogoImage(null);
    setHasChanges(true);
  };

  const handleBannerChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.size > 10 * 1024 * 1024) {
        showToast('Banner must be less than 10MB', 'error');
        return;
      }
      const reader = new FileReader();
      reader.onload = () => {
        setTempBannerImage(reader.result);
        setBannerPreview(reader.result);
        setShowBannerModal(true);
      };
      reader.readAsDataURL(file);
      setBannerFile(file);
      setHasChanges(true);
    }
  };

  const handleBannerSave = () => {
    setShowBannerModal(false);
    setTempBannerImage(null);
  };

  const handleGameSelect = (game) => {
    setFormData(prev => ({ ...prev, game }));
    setShowGameResults(false);
    setGames([]);
    setGameSearch('');
    setHasChanges(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      // Update team data
      const updateData = {
        name: formData.name,
        tag: formData.tag,
        description: formData.description,
        country: formData.country,
        region: formData.region,
        primary_color: formData.primary_color,
        secondary_color: formData.secondary_color,
        looking_for_players: formData.looking_for_players
      };
      
      if (formData.game) {
        updateData.game_id = formData.game.id;
      }

      await api.updateTeam(team.id, updateData);

      // Upload logo if changed
      if (logoFile) {
        await api.uploadTeamLogo(team.id, logoFile);
      }

      // Upload banner if changed
      if (bannerFile) {
        await api.uploadTeamBanner(team.id, bannerFile);
      }

      showToast('Team updated successfully', 'success');
      setHasChanges(false);
      onReload();
    } catch (error) {
      console.error('Failed to update team:', error);
      showToast(error.data?.error || 'Failed to update team', 'error');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="edit-section">
      <h2 className="section-header" style={{ borderLeftColor: team.primary_color || '#6366f1' }}>
        Edit Team
      </h2>

      <form onSubmit={handleSubmit} className="edit-form">
        {/* Team Identity */}
        <Card className="form-section-card">
          <h3 className="form-section-title">Team Identity</h3>
          
          {/* Logo Upload */}
          <div className="form-group">
            <label>Upload Logo</label>
            <div className="logo-upload-area">
              {logoPreview ? (
                <div className="logo-preview">
                  <img src={logoPreview} alt="Team logo" />
                  <button
                    type="button"
                    className="change-logo-btn"
                    onClick={() => document.getElementById('logo-input-edit').click()}
                  >
                    Change Logo
                  </button>
                </div>
              ) : (
                <button
                  type="button"
                  className="upload-placeholder"
                  onClick={() => document.getElementById('logo-input-edit').click()}
                >
                  <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M17 8l-5-5-5 5M12 3v12"/>
                  </svg>
                  <span>Click to upload logo</span>
                </button>
              )}
              <input
                id="logo-input-edit"
                type="file"
                accept="image/*"
                onChange={handleLogoChange}
                style={{ display: 'none' }}
              />
            </div>
          </div>

          {/* Team Name */}
          <div className="form-group">
            <label>Team Name *</label>
            <Input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              placeholder="Enter team name"
              required
            />
          </div>

          {/* Team Tag */}
          <div className="form-group">
            <label>Team Tag *</label>
            <Input
              type="text"
              name="tag"
              value={formData.tag}
              onChange={handleInputChange}
              placeholder="TAG"
              maxLength={5}
              required
            />
          </div>

          {/* Game */}
          <div className="form-group">
            <label>Game *</label>
            {formData.game ? (
              <div className="selected-game">
                {formData.game.cover_url && (
                  <img src={formData.game.cover_url} alt={formData.game.name} />
                )}
                <span>{formData.game.name}</span>
                <button
                  type="button"
                  onClick={() => {
                    setFormData(prev => ({ ...prev, game: null }));
                    setHasChanges(true);
                  }}
                  className="remove-game-btn"
                >
                  ×
                </button>
              </div>
            ) : (
              <div className="game-search-wrapper">
                <Input
                  type="text"
                  value={gameSearch}
                  onChange={(e) => setGameSearch(e.target.value)}
                  placeholder="Search for a game..."
                />
                {searchingGames && !showGameResults && (
                  <div className="game-search-loading">
                    <div className="spinner"></div>
                    <span>Searching games...</span>
                  </div>
                )}
                {showGameResults && (
                  <div className="game-results">
                    {searchingGames ? (
                      <div className="game-result-item loading">
                        <div className="spinner"></div>
                        <span>Searching...</span>
                      </div>
                    ) : games.length > 0 ? (
                      games.map(game => (
                        <div
                          key={game.id}
                          className="game-result-item"
                          onClick={() => handleGameSelect(game)}
                        >
                          {game.cover_url && (
                            <img src={game.cover_url} alt={game.name} />
                          )}
                          <span>{game.name}</span>
                        </div>
                      ))
                    ) : (
                      <div className="game-result-item empty">No games found</div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Description */}
          <div className="form-group">
            <label>Description</label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleInputChange}
              placeholder="Tell us about your team..."
              rows={4}
              maxLength={1000}
              className="form-textarea"
            />
            <span className="char-count">{formData.description.length}/1000</span>
          </div>
        </Card>

        {/* Customization */}
        <Card className="form-section-card">
          <h3 className="form-section-title">Customization</h3>
          
          {/* Banner Upload */}
          <div className="form-group">
            <label>Banner (optional)</label>
            <div className="banner-upload-area">
              {bannerPreview ? (
                <div className="banner-preview">
                  <img src={bannerPreview} alt="Team banner" />
                  <button
                    type="button"
                    className="change-banner-btn"
                    onClick={() => document.getElementById('banner-input-edit').click()}
                  >
                    Change Banner
                  </button>
                </div>
              ) : (
                <button
                  type="button"
                  className="upload-placeholder banner"
                  onClick={() => document.getElementById('banner-input-edit').click()}
                >
                  <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M17 8l-5-5-5 5M12 3v12"/>
                  </svg>
                  <span>Upload Banner</span>
                </button>
              )}
              <input
                id="banner-input-edit"
                type="file"
                accept="image/*"
                onChange={handleBannerChange}
                style={{ display: 'none' }}
              />
            </div>
          </div>

          {/* Colors */}
          <div className="form-row">
            <div className="form-group">
              <label>Primary Color</label>
              <div className="color-input-wrapper">
                <input
                  type="color"
                  name="primary_color"
                  value={formData.primary_color}
                  onChange={handleInputChange}
                  className="color-input"
                />
                <span className="color-value">{formData.primary_color}</span>
              </div>
            </div>

            <div className="form-group">
              <label>Secondary Color</label>
              <div className="color-input-wrapper">
                <input
                  type="color"
                  name="secondary_color"
                  value={formData.secondary_color}
                  onChange={handleInputChange}
                  className="color-input"
                />
                <span className="color-value">{formData.secondary_color}</span>
              </div>
            </div>
          </div>
        </Card>

        {/* Location */}
        <Card className="form-section-card">
          <h3 className="form-section-title">Location (optional)</h3>
          
          <div className="form-row">
            <div className="form-group">
              <label>Country</label>
              <select
                name="country"
                value={formData.country}
                onChange={handleInputChange}
                className="form-select"
              >
                <option value="">Select country</option>
                <option value="Ecuador">Ecuador</option>
                <option value="Colombia">Colombia</option>
                <option value="Peru">Peru</option>
                <option value="Argentina">Argentina</option>
                <option value="Mexico">Mexico</option>
                <option value="United States">United States</option>
              </select>
            </div>

            <div className="form-group">
              <label>Region</label>
              <select
                name="region"
                value={formData.region}
                onChange={handleInputChange}
                className="form-select"
              >
                <option value="">Select region</option>
                <option value="LATAM">LATAM</option>
                <option value="North America">North America</option>
                <option value="Europe">Europe</option>
                <option value="Asia">Asia</option>
              </select>
            </div>
          </div>
        </Card>

        {/* Looking for Players */}
        <Card className="form-section-card">
          <div className="form-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                name="looking_for_players"
                checked={formData.looking_for_players}
                onChange={handleInputChange}
              />
              <span>Looking for players</span>
            </label>
          </div>
        </Card>

        {/* Actions */}
        <div className="form-actions">
          <Button
            type="button"
            variant="ghost"
            onClick={() => window.location.reload()}
            disabled={!hasChanges}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            variant="primary"
            disabled={submitting || !hasChanges}
          >
            {submitting ? 'Saving...' : 'Save Changes'}
          </Button>
        </div>
      </form>

      {/* Modals */}
      {showLogoCropModal && (
        <TeamLogoCropModal
          image={tempLogoImage}
          onSave={handleLogoSave}
          onCancel={() => {
            setShowLogoCropModal(false);
            setTempLogoImage(null);
          }}
        />
      )}

      {showBannerModal && (
        <BannerPreviewModal
          image={tempBannerImage}
          onSave={handleBannerSave}
          onCancel={() => {
            setShowBannerModal(false);
            setTempBannerImage(null);
            setBannerFile(null);
            setBannerPreview(team.banner_url || null);
          }}
        />
      )}
    </div>
  );
};

// Helper functions
const calculateCompleteness = (team) => {
  const fields = [
    { key: 'description', label: 'Description' },
    { key: 'country', label: 'Country' },
    { key: 'region', label: 'Region' },
    { key: 'banner_url', label: 'Banner' }
  ];

  const missing = fields.filter(field => !team[field.key]).map(field => field.label);
  const percentage = Math.round(((fields.length - missing.length) / fields.length) * 100);

  return { percentage, missing };
};

const formatDate = (dateString) => {
  const date = new Date(dateString);
  const now = new Date();
  const diffTime = Math.abs(now - date);
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

  if (diffDays === 0) return 'today';
  if (diffDays === 1) return 'yesterday';
  if (diffDays < 7) return `${diffDays} days ago`;
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
  return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
};

export default ManageTeam;
