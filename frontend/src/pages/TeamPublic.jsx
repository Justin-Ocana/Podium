import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../contexts/ToastContext';
import Navbar from '../components/Navbar';
import Card from '../components/Card';
import Button from '../components/Button';
import Avatar from '../components/Avatar';
import LoadingScreen from '../components/LoadingScreen';
import api from '../services/api';
import './TeamPublic.css';

const TeamPublic = () => {
  const { slug } = useParams();
  const { user, logout } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();

  const [team, setTeam] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isMember, setIsMember] = useState(false);
  const [isCaptain, setIsCaptain] = useState(false);

  useEffect(() => {
    loadTeam();
  }, [slug]);

  const loadTeam = async () => {
    try {
      const data = await api.getTeam(slug);
      setTeam(data);
      
      // Check if current user is member or captain
      if (user && data.members) {
        const membership = data.members.find(m => m.user.id === user.id);
        if (membership) {
          setIsMember(true);
          setIsCaptain(membership.role === 'CAPTAIN');
        }
      }
    } catch (error) {
      console.error('Failed to load team:', error);
      showToast('Failed to load team', 'error');
      navigate('/teams');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingScreen message="Loading team..." />;
  }

  if (!team) {
    return null;
  }

  return (
    <div className="page-layout">
      <Navbar user={user} onLogout={logout} />
      
      <div className="team-public-container">
        {/* Team Banner */}
        {team.banner_url && (
          <div className="team-banner">
            <img src={team.banner_url} alt={`${team.name} banner`} />
          </div>
        )}

        {/* Team Header */}
        <div className="team-header">
          <div className="team-header-content">
            <Avatar 
              src={team.logo_url} 
              username={team.name}
              size="xlarge"
              className="team-logo"
            />
            
            <div className="team-title-section">
              <h1 style={{ color: team.primary_color || 'var(--text-main)' }}>
                {team.name}
              </h1>
              <p className="team-tag" style={{ color: team.secondary_color || 'var(--text-secondary)' }}>
                [{team.tag}]
              </p>
              {team.game && (
                <p className="team-game">🎮 {team.game.name}</p>
              )}
            </div>

            {isCaptain && (
              <Button variant="primary" onClick={() => navigate(`/teams/${slug}/edit`)}>
                Edit Team
              </Button>
            )}
          </div>

          {team.description && (
            <p className="team-description">{team.description}</p>
          )}

          <div className="team-stats-row">
            <div className="stat-box">
              <span className="stat-value">{team.members_count || 0}</span>
              <span className="stat-label">Members</span>
            </div>
            <div className="stat-box">
              <span className="stat-value">{team.tournaments_count || 0}</span>
              <span className="stat-label">Tournaments</span>
            </div>
            <div className="stat-box">
              <span className="stat-value">{team.wins || 0}</span>
              <span className="stat-label">Wins</span>
            </div>
            <div className="stat-box">
              <span className="stat-value">{team.losses || 0}</span>
              <span className="stat-label">Losses</span>
            </div>
          </div>
        </div>

        {/* Team Content */}
        <div className="team-content-grid">
          {/* Members Section */}
          <Card className="team-section">
            <h2>Team Members</h2>
            <div className="members-list">
              {team.members && team.members.length > 0 ? (
                team.members.map(member => (
                  <div key={member.id} className="member-item">
                    <Avatar 
                      src={member.user.avatar_url} 
                      username={member.user.username}
                      size="medium"
                    />
                    <div className="member-info">
                      <span className="member-name">{member.user.username}</span>
                      <span className={`member-role ${member.role.toLowerCase()}`}>
                        {member.role === 'CAPTAIN' ? '👑 Captain' : 'Member'}
                      </span>
                    </div>
                  </div>
                ))
              ) : (
                <p className="empty-text">No members yet</p>
              )}
            </div>
          </Card>

          {/* Tournaments Section */}
          <Card className="team-section">
            <h2>Tournaments</h2>
            <div className="tournaments-list">
              {team.tournaments && team.tournaments.length > 0 ? (
                team.tournaments.map(tournament => (
                  <div key={tournament.id} className="tournament-item">
                    <span className="tournament-name">{tournament.name}</span>
                    <span className="tournament-status">{tournament.status}</span>
                  </div>
                ))
              ) : (
                <p className="empty-text">No tournaments yet</p>
              )}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default TeamPublic;
