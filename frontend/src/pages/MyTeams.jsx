import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import Navbar from '../components/Navbar';
import Card from '../components/Card';
import Avatar from '../components/Avatar';
import Button from '../components/Button';
import Badge from '../components/Badge';
import LoadingScreen from '../components/LoadingScreen';
import ParticleBackground from '../components/ParticleBackground';
import { useToast } from '../contexts/ToastContext';
import api from '../services/api';
import './MyTeams.css';

// Helper function to convert hex to rgb
const hexToRgb = (hex) => {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result 
    ? `${parseInt(result[1], 16)}, ${parseInt(result[2], 16)}, ${parseInt(result[3], 16)}`
    : '99, 102, 241'; // fallback to primary color
};

const MyTeams = () => {
  const { user, logout } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();
  const [myTeams, setMyTeams] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadMyTeams();
  }, []);

  const loadMyTeams = async () => {
    try {
      const data = await api.getMyTeams();
      console.log('My teams data:', data);
      const teams = data.results || data || [];
      console.log('Processed teams:', teams);
      setMyTeams(teams);
    } catch (error) {
      console.error('Failed to load my teams:', error);
      showToast('Failed to load your teams', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleTeamClick = (membership) => {
    if (membership.role === 'captain') {
      navigate(`/teams/${membership.team.slug}/manage`);
    } else {
      navigate(`/teams/${membership.team.slug}`);
    }
  };

  const handleLeaveTeam = async (e, teamId) => {
    e.stopPropagation();
    if (window.confirm('Are you sure you want to leave this team?')) {
      try {
        await api.leaveTeam(teamId);
        showToast('Left team successfully', 'success');
        loadMyTeams();
      } catch (error) {
        showToast('Failed to leave team', 'error');
      }
    }
  };

  const handleCreateTeam = () => {
    navigate('/teams/create');
  };

  const captainTeams = myTeams.filter(m => m.role === 'captain');
  const memberTeams = myTeams.filter(m => m.role === 'member');

  return (
    <>
      {loading ? (
        <LoadingScreen message="Loading your teams..." />
      ) : (
        <div className="page-layout">
          <ParticleBackground />
          <Navbar user={user} onLogout={logout} />
          
          <div className="page-container">
            <div className="page-header">
              <div>
                <h1>My Teams</h1>
                <p className="page-subtitle">Teams you captain or play for</p>
              </div>
              <Button variant="primary" onClick={handleCreateTeam} className="btn-glow">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="12" y1="5" x2="12" y2="19"/>
                  <line x1="5" y1="12" x2="19" y2="12"/>
                </svg>
                Create Team
              </Button>
            </div>

            {myTeams.length > 0 ? (
              <>
                {/* Captaining Section */}
                {captainTeams.length > 0 && (
                  <div className="teams-section">
                    <h2 className="section-title">
                      Captaining
                    </h2>
                    <div className="my-teams-grid">
                      {captainTeams.map(membership => (
                        <Card 
                          key={membership.id} 
                          hover 
                          className="my-team-card captain-card"
                          onClick={() => handleTeamClick(membership)}
                          style={{
                            borderColor: membership.team.primary_color || '#6366f1',
                            boxShadow: `0 8px 40px rgba(0, 0, 0, 0.4), 0 0 0 1px ${membership.team.primary_color || '#6366f1'}40, inset 0 1px 0 rgba(255, 255, 255, 0.06)`
                          }}
                        >
                          {/* Banner */}
                          <div 
                            className="my-team-banner"
                            style={{
                              backgroundImage: membership.team.banner_url 
                                ? `url(${membership.team.banner_url})` 
                                : `linear-gradient(135deg, ${membership.team.primary_color || '#6366f1'} 0%, ${membership.team.secondary_color || '#8b5cf6'} 100%)`
                            }}
                          />

                          {/* Avatar + Badge */}
                          <div className="my-team-avatar-section">
                            <Avatar 
                              src={membership.team.logo_url} 
                              username={membership.team.name}
                              size="large"
                              className="my-team-avatar"
                              style={{
                                boxShadow: `0 0 24px ${membership.team.primary_color || '#6366f1'}80`
                              }}
                            />
                            <Badge 
                              variant="warning" 
                              className="role-badge captain-badge"
                            >
                              <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z"/>
                              </svg>
                              CAPTAIN
                            </Badge>
                          </div>

                          {/* Content */}
                          <div className="my-team-content">
                            <h3 style={{ color: membership.team.primary_color || 'var(--text-main)' }}>
                              {membership.team.name}
                            </h3>
                            
                            <div className="my-team-meta">
                              <Badge variant="secondary" className="team-tag-badge">
                                [{membership.team.tag}]
                              </Badge>
                              {membership.team.game && (
                                <Badge variant="primary" className="team-game-badge">
                                  {membership.team.game.background_image && (
                                    <img src={membership.team.game.background_image} alt={membership.team.game.name} />
                                  )}
                                  {membership.team.game.name}
                                </Badge>
                              )}
                            </div>

                            <div className="my-team-stats">
                              <span className="stat-muted">
                                {membership.team.members_count || 0} members • {membership.team.tournaments_count || 0} tournaments
                              </span>
                              <span className="stat-muted">
                                Joined {new Date(membership.joined_at).toLocaleDateString('en-US', { 
                                  month: 'short', 
                                  year: 'numeric' 
                                })}
                              </span>
                            </div>

                            <Button 
                              variant="ghost" 
                              className="my-team-btn captain-btn"
                              style={{
                                background: `rgba(${hexToRgb(membership.team.primary_color || '#6366f1')}, 0.15)`,
                                borderColor: membership.team.primary_color || '#6366f1',
                                color: membership.team.primary_color || '#6366f1'
                              }}
                            >
                              Manage Team
                            </Button>
                          </div>
                        </Card>
                      ))}
                    </div>
                  </div>
                )}

                {/* Member Section */}
                {memberTeams.length > 0 && (
                  <div className="teams-section">
                    <h2 className="section-title">
                      Member of
                    </h2>
                    <div className="my-teams-grid">
                      {memberTeams.map(membership => (
                        <Card 
                          key={membership.id} 
                          hover 
                          className="my-team-card member-card"
                          onClick={() => handleTeamClick(membership)}
                        >
                          {/* Banner */}
                          <div 
                            className="my-team-banner"
                            style={{
                              backgroundImage: membership.team.banner_url 
                                ? `url(${membership.team.banner_url})` 
                                : `linear-gradient(135deg, ${membership.team.primary_color || '#6366f1'} 0%, ${membership.team.secondary_color || '#8b5cf6'} 100%)`
                            }}
                          />

                          {/* Avatar + Badge */}
                          <div className="my-team-avatar-section">
                            <Avatar 
                              src={membership.team.logo_url} 
                              username={membership.team.name}
                              size="large"
                              className="my-team-avatar"
                              style={{
                                boxShadow: `0 0 16px ${membership.team.primary_color || '#6366f1'}40`
                              }}
                            />
                            <Badge variant="secondary" className="role-badge member-badge">
                              MEMBER
                            </Badge>
                          </div>

                          {/* Content */}
                          <div className="my-team-content">
                            <h3 style={{ color: membership.team.primary_color || 'var(--text-main)' }}>
                              {membership.team.name}
                            </h3>
                            
                            <div className="my-team-meta">
                              <Badge variant="secondary" className="team-tag-badge">
                                [{membership.team.tag}]
                              </Badge>
                              {membership.team.game && (
                                <Badge variant="primary" className="team-game-badge">
                                  {membership.team.game.background_image && (
                                    <img src={membership.team.game.background_image} alt={membership.team.game.name} />
                                  )}
                                  {membership.team.game.name}
                                </Badge>
                              )}
                            </div>

                            <div className="my-team-stats">
                              <span className="stat-muted">
                                {membership.team.members_count || 0} members • {membership.team.tournaments_count || 0} tournaments
                              </span>
                              <span className="stat-muted">
                                Joined {new Date(membership.joined_at).toLocaleDateString('en-US', { 
                                  month: 'short', 
                                  year: 'numeric' 
                                })}
                              </span>
                            </div>

                            <div className="my-team-actions">
                              <Button 
                                variant="ghost" 
                                className="my-team-btn member-btn"
                                style={{
                                  borderColor: `${membership.team.primary_color || '#6366f1'}66`,
                                  color: membership.team.primary_color || 'rgba(255, 255, 255, 0.95)'
                                }}
                              >
                                View Team
                              </Button>
                              <Button 
                                variant="ghost" 
                                className="leave-team-btn"
                                onClick={(e) => handleLeaveTeam(e, membership.team.id)}
                              >
                                Leave Team
                              </Button>
                            </div>
                          </div>
                        </Card>
                      ))}
                    </div>
                  </div>
                )}
              </>
            ) : (
              <Card className="empty-state">
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/>
                  <circle cx="9" cy="7" r="4"/>
                  <path d="M23 21v-2a4 4 0 00-3-3.87"/>
                  <path d="M16 3.13a4 4 0 010 7.75"/>
                </svg>
                <h3>No teams yet</h3>
                <p>Create or join a team to start competing in tournaments</p>
                <Button variant="primary" onClick={handleCreateTeam}>
                  Create Your First Team
                </Button>
              </Card>
            )}
          </div>
        </div>
      )}
    </>
  );
};

export default MyTeams;
