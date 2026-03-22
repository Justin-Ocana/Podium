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
import api from '../services/api';
import './Teams.css';

const Teams = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [teams, setTeams] = useState([]);
  const [filteredTeams, setFilteredTeams] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Filters state
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedGame, setSelectedGame] = useState('all');
  const [sortBy, setSortBy] = useState('recent');
  const [lookingForPlayers, setLookingForPlayers] = useState(false);
  
  // Available games (extracted from teams)
  const [availableGames, setAvailableGames] = useState([]);

  useEffect(() => {
    loadTeams();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [teams, searchQuery, selectedGame, sortBy, lookingForPlayers]);

  const loadTeams = async () => {
    try {
      const data = await api.getTeams();
      const teamsList = data.results || [];
      setTeams(teamsList);
      
      // Extract unique games
      const games = [...new Set(teamsList.map(t => t.game?.name).filter(Boolean))];
      setAvailableGames(games);
    } catch (error) {
      console.error('Failed to load teams:', error);
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...teams];

    // Search filter
    if (searchQuery) {
      filtered = filtered.filter(team => 
        team.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        team.tag.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Game filter
    if (selectedGame !== 'all') {
      filtered = filtered.filter(team => team.game?.name === selectedGame);
    }

    // Looking for players filter
    if (lookingForPlayers) {
      filtered = filtered.filter(team => team.looking_for_players);
    }

    // Sort
    switch (sortBy) {
      case 'members':
        filtered.sort((a, b) => (b.members_count || 0) - (a.members_count || 0));
        break;
      case 'tournaments':
        filtered.sort((a, b) => (b.tournaments_count || 0) - (a.tournaments_count || 0));
        break;
      case 'recent':
      default:
        filtered.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
        break;
    }

    setFilteredTeams(filtered);
  };

  // Check if any filter is active
  const hasActiveFilters = () => {
    return searchQuery || selectedGame !== 'all' || lookingForPlayers || sortBy !== 'recent';
  };

  const handleTeamClick = (teamSlug) => {
    navigate(`/teams/${teamSlug}`);
  };

  const handleCreateTeam = () => {
    navigate('/teams/create');
  };

  return (
    <>
      {loading ? (
        <LoadingScreen message="Loading teams..." />
      ) : (
        <div className="page-layout">
          <ParticleBackground />
          <Navbar user={user} onLogout={logout} />
          
          <div className="page-container">
            {/* Header */}
            <div className="page-header">
              <div>
                <h1>
                  Teams
                  {hasActiveFilters() && ` (${filteredTeams.length})`}
                </h1>
                <p className="page-subtitle">Discover competitive teams and find your squad</p>
              </div>
              <Button variant="primary" onClick={handleCreateTeam} className="btn-glow">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="12" y1="5" x2="12" y2="19"/>
                  <line x1="5" y1="12" x2="19" y2="12"/>
                </svg>
                Create Team
              </Button>
            </div>

            {/* Filters Bar */}
            <div className="teams-filters">
              {/* Search */}
              <div className="filter-search">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="11" cy="11" r="8"/>
                  <path d="m21 21-4.35-4.35"/>
                </svg>
                <input
                  type="text"
                  placeholder="Search teams..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>

              {/* Game Filter */}
              <select 
                className="filter-select"
                value={selectedGame}
                onChange={(e) => setSelectedGame(e.target.value)}
              >
                <option value="all">All Games</option>
                {availableGames.map(game => (
                  <option key={game} value={game}>{game}</option>
                ))}
              </select>

              {/* Sort */}
              <select 
                className="filter-select"
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
              >
                <option value="recent">Most Recent</option>
                <option value="members">Most Members</option>
                <option value="tournaments">Most Tournaments</option>
              </select>

              {/* Looking for Players Toggle */}
              <button 
                className={`filter-toggle ${lookingForPlayers ? 'active' : ''}`}
                onClick={() => setLookingForPlayers(!lookingForPlayers)}
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M16 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/>
                  <circle cx="8.5" cy="7" r="4"/>
                  <line x1="20" y1="8" x2="20" y2="14"/>
                  <line x1="23" y1="11" x2="17" y2="11"/>
                </svg>
                Looking for Players
              </button>
            </div>

            {/* Teams Grid */}
            {filteredTeams.length > 0 ? (
              <>
                <div className="teams-grid">
                  {filteredTeams.map(team => (
                    <Card 
                      key={team.id} 
                      hover 
                      className="team-card"
                      onClick={() => handleTeamClick(team.slug)}
                    >
                      {/* Banner */}
                      <div 
                        className="team-card-banner"
                        style={{
                          backgroundImage: team.banner_url 
                            ? `url(${team.banner_url})` 
                            : `linear-gradient(135deg, ${team.primary_color || 'var(--primary)'} 0%, ${team.secondary_color || 'var(--accent-purple)'} 100%)`
                        }}
                      />

                      {/* Avatar with Glow */}
                      <div className="team-card-avatar-wrapper">
                        <Avatar 
                          src={team.logo_url} 
                          username={team.name}
                          size="large"
                          className="team-card-avatar"
                          style={{
                            boxShadow: `0 0 24px ${team.primary_color || 'var(--primary)'}80`
                          }}
                        />
                      </div>

                      {/* Content */}
                      <div className="team-card-content">
                        <h3 style={{ color: team.primary_color || 'var(--text-main)' }}>
                          {team.name}
                        </h3>
                        
                        <div className="team-card-meta">
                          <Badge variant="secondary" className="team-tag-badge">
                            [{team.tag}]
                          </Badge>
                          {team.game && (
                            <Badge variant="primary" className="team-game-badge">
                              {team.game.cover_url && (
                                <img src={team.game.cover_url} alt={team.game.name} />
                              )}
                              {team.game.name}
                            </Badge>
                          )}
                        </div>

                        {team.looking_for_players && (
                          <Badge variant="success" className="team-recruiting-badge">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                              <path d="M16 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/>
                              <circle cx="8.5" cy="7" r="4"/>
                              <line x1="20" y1="8" x2="20" y2="14"/>
                              <line x1="23" y1="11" x2="17" y2="11"/>
                            </svg>
                            Recruiting
                          </Badge>
                        )}

                        <div className="team-card-stats">
                          <span className="stat-muted">
                            {team.members_count || 0} members • {team.tournaments_count || 0} tournaments
                          </span>
                        </div>

                        <Button 
                          variant="ghost" 
                          className="team-card-btn"
                          style={{
                            borderColor: `${team.primary_color || '#6366f1'}66`,
                            color: team.primary_color || 'rgba(255, 255, 255, 0.95)'
                          }}
                        >
                          View Team
                        </Button>
                      </div>
                    </Card>
                  ))}

                  {/* Create Team CTA Card */}
                  <Card 
                    hover 
                    className="team-card team-card-cta"
                    onClick={handleCreateTeam}
                  >
                    <div className="team-card-cta-content">
                      <div className="team-card-cta-icon">
                        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <line x1="12" y1="5" x2="12" y2="19"/>
                          <line x1="5" y1="12" x2="19" y2="12"/>
                        </svg>
                      </div>
                      <h3>Create Your Team</h3>
                      <p>Start your competitive journey</p>
                    </div>
                  </Card>
                </div>
              </>
            ) : (
              <Card className="empty-state">
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                  <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/>
                  <circle cx="9" cy="7" r="4"/>
                  <path d="M23 21v-2a4 4 0 00-3-3.87"/>
                  <path d="M16 3.13a4 4 0 010 7.75"/>
                </svg>
                <h3>No teams found</h3>
                <p>Try adjusting your filters or create the first team</p>
                <Button variant="primary" onClick={handleCreateTeam}>
                  Create Team
                </Button>
              </Card>
            )}
          </div>
        </div>
      )}
    </>
  );
};

export default Teams;
