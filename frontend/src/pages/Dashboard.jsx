import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import Navbar from '../components/Navbar';
import Card from '../components/Card';
import Badge from '../components/Badge';
import Avatar from '../components/Avatar';
import Button from '../components/Button';
import LoadingScreen from '../components/LoadingScreen';
import api from '../services/api';
import './Dashboard.css';
import './Dashboard-activity.css';
import './Dashboard-matches.css';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const [stats, setStats] = useState(null);
  const [teams, setTeams] = useState([]);
  const [tournaments, setTournaments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [animatedStats, setAnimatedStats] = useState({
    teams: 0,
    tournaments: 0,
    wins: 0,
    winrate: 0
  });

  useEffect(() => {
    loadDashboardData();
  }, []);

  useEffect(() => {
    if (stats) {
      animateStats();
    }
  }, [stats]);

  const animateStats = () => {
    const duration = 1000;
    const steps = 60;
    const interval = duration / steps;

    let currentStep = 0;
    const timer = setInterval(() => {
      currentStep++;
      const progress = currentStep / steps;

      setAnimatedStats({
        teams: Math.floor((stats.teams_count || 0) * progress),
        tournaments: Math.floor((stats.tournaments_played_count || 0) * progress),
        wins: Math.floor((stats.matches_won_count || 0) * progress),
        winrate: Math.floor((stats.winrate || 0) * progress)
      });

      if (currentStep >= steps) {
        clearInterval(timer);
        setAnimatedStats({
          teams: stats.teams_count || 0,
          tournaments: stats.tournaments_played_count || 0,
          wins: stats.matches_won_count || 0,
          winrate: stats.winrate || 0
        });
      }
    }, interval);

    return () => clearInterval(timer);
  };

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load user stats
      if (user?.id) {
        const userStats = await api.getUserStats(user.id);
        setStats(userStats);
      }

      // Load teams
      const teamsData = await api.getTeams({ page_size: 6 });
      setTeams(teamsData.results || []);

      // Load tournaments (placeholder for now)
      const tournamentsData = await api.getTournaments({ page_size: 6 });
      setTournaments(tournamentsData.results || []);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const statusMap = {
      'OPEN': { variant: 'success', label: 'Open' },
      'IN_PROGRESS': { variant: 'warning', label: 'In Progress' },
      'FINISHED': { variant: 'info', label: 'Finished' },
      'CANCELLED': { variant: 'danger', label: 'Cancelled' },
    };
    return statusMap[status] || { variant: 'info', label: status };
  };

  return (
    <>
      {loading ? (
        <LoadingScreen message="Loading dashboard..." />
      ) : (
        <>
          <Navbar user={user} onLogout={logout} />
          <div className="dashboard-layout">
            <div className="dashboard">
            <div className="dashboard-header">
              <div className="dashboard-hero">
                <h1>Welcome back, {user?.username}!</h1>
                <p className="dashboard-tagline">Compete. Organize. Win.</p>
              </div>
            </div>

            <div className="dashboard-top-section">
              {/* Stats Section */}
              <div className="dashboard-stats">
                <div className="stat-card">
                  <div className="stat-icon stat-icon--purple">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                      <path d="M17 21V19C17 17.9391 16.5786 16.9217 15.8284 16.1716C15.0783 15.4214 14.0609 15 13 15H5C3.93913 15 2.92172 15.4214 2.17157 16.1716C1.42143 16.9217 1 17.9391 1 19V21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      <path d="M9 11C11.2091 11 13 9.20914 13 7C13 4.79086 11.2091 3 9 3C6.79086 3 5 4.79086 5 7C5 9.20914 6.79086 11 9 11Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      <path d="M23 21V19C22.9993 18.1137 22.7044 17.2528 22.1614 16.5523C21.6184 15.8519 20.8581 15.3516 20 15.13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      <path d="M16 3.13C16.8604 3.35031 17.623 3.85071 18.1676 4.55232C18.7122 5.25392 19.0078 6.11683 19.0078 7.005C19.0078 7.89318 18.7122 8.75608 18.1676 9.45769C17.623 10.1593 16.8604 10.6597 16 10.88" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  </div>
                  <div className="stat-content">
                    <div className="stat-value">{animatedStats.teams}</div>
                    <div className="stat-label">Teams</div>
                  </div>
                </div>

                <div className="stat-card">
                  <div className="stat-icon stat-icon--cyan">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                      <path d="M6 2L3 6V20C3 20.5304 3.21071 21.0391 3.58579 21.4142C3.96086 21.7893 4.46957 22 5 22H19C19.5304 22 20.0391 21.7893 20.4142 21.4142C20.7893 21.0391 21 20.5304 21 20V6L18 2H6Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      <path d="M3 6H21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      <path d="M16 10C16 11.0609 15.5786 12.0783 14.8284 12.8284C14.0783 13.5786 13.0609 14 12 14C10.9391 14 9.92172 13.5786 9.17157 12.8284C8.42143 12.0783 8 11.0609 8 10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  </div>
                  <div className="stat-content">
                    <div className="stat-value">{animatedStats.tournaments}</div>
                    <div className="stat-label">Tournaments</div>
                  </div>
                </div>

                <div className="stat-card">
                  <div className="stat-icon stat-icon--success">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                      <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  </div>
                  <div className="stat-content">
                    <div className="stat-value">{animatedStats.wins}</div>
                    <div className="stat-label">Wins</div>
                  </div>
                </div>

                <div className="stat-card">
                  <div className="stat-icon stat-icon--primary">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                      <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      <path d="M2 17L12 22L22 17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      <path d="M2 12L12 17L22 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  </div>
                  <div className="stat-content">
                    <div className="stat-value">{animatedStats.winrate > 0 ? `${animatedStats.winrate}%` : '0%'}</div>
                    <div className="stat-label">Win Rate</div>
                  </div>
                </div>
              </div>

              {/* Quick Actions */}
              <div className="quick-actions">
                <h3>Quick Actions</h3>
                <div className="quick-actions-grid">
                  <Link to="/tournaments/create" className="quick-action-btn">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                      <path d="M12 5V19M5 12H19" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                    </svg>
                    Create Tournament
                  </Link>
                  <Link to="/teams/create" className="quick-action-btn">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                      <path d="M12 5V19M5 12H19" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                    </svg>
                    Create Team
                  </Link>
                  <Link to="/tournaments" className="quick-action-btn">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                      <path d="M21 21L15 15M17 10C17 13.866 13.866 17 10 17C6.13401 17 3 13.866 3 10C3 6.13401 6.13401 3 10 3C13.866 3 17 6.13401 17 10Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                    </svg>
                    Browse
                  </Link>
                </div>
              </div>
            </div>

            {/* Activity Feed */}
            <div className="dashboard-section">
              <div className="section-header">
                <h2>Recent Activity</h2>
              </div>
              
              <Card className="activity-feed">
                <div className="activity-item">
                  <div className="activity-icon activity-icon--success">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                      <path d="M20 6L9 17L4 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  </div>
                  <div className="activity-content">
                    <p className="activity-text">You joined <strong>Team Alpha</strong></p>
                    <span className="activity-time">2 hours ago</span>
                  </div>
                </div>
                
                <div className="activity-item">
                  <div className="activity-icon activity-icon--info">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                      <path d="M6 2L3 6V20C3 20.5304 3.21071 21.0391 3.58579 21.4142C3.96086 21.7893 4.46957 22 5 22H19C19.5304 22 20.0391 21.7893 20.4142 21.4142C20.7893 21.0391 21 20.5304 21 20V6L18 2H6Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  </div>
                  <div className="activity-content">
                    <p className="activity-text">Your team registered in <strong>Summer Cup</strong></p>
                    <span className="activity-time">1 day ago</span>
                  </div>
                </div>
                
                <div className="activity-item">
                  <div className="activity-icon activity-icon--purple">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                      <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  </div>
                  <div className="activity-content">
                    <p className="activity-text">You won a match against <strong>Team Nova</strong></p>
                    <span className="activity-time">3 days ago</span>
                  </div>
                </div>
              </Card>
            </div>

            {/* Upcoming Matches */}
            <div className="dashboard-section">
              <div className="section-header">
                <h2>Upcoming Matches</h2>
                <Link to="/matches" className="section-link">View All</Link>
              </div>
              
              <div className="matches-grid">
                <Card hover className="match-card">
                  <div className="match-header">
                    <Badge variant="warning">Upcoming</Badge>
                    <span className="match-tournament">Summer Cup</span>
                  </div>
                  <div className="match-teams">
                    <div className="match-team">
                      <Avatar username="Team Alpha" size="small" />
                      <span className="match-team-name">Team Alpha</span>
                    </div>
                    <div className="match-vs">VS</div>
                    <div className="match-team">
                      <Avatar username="Team Nova" size="small" />
                      <span className="match-team-name">Team Nova</span>
                    </div>
                  </div>
                  <div className="match-time">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                      <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"/>
                      <path d="M12 6V12L16 14" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                    </svg>
                    Tomorrow at 19:00
                  </div>
                </Card>

                <Card hover className="match-card">
                  <div className="match-header">
                    <Badge variant="warning">Upcoming</Badge>
                    <span className="match-tournament">Winter League</span>
                  </div>
                  <div className="match-teams">
                    <div className="match-team">
                      <Avatar username="Team Alpha" size="small" />
                      <span className="match-team-name">Team Alpha</span>
                    </div>
                    <div className="match-vs">VS</div>
                    <div className="match-team">
                      <Avatar username="NightRaid" size="small" />
                      <span className="match-team-name">NightRaid</span>
                    </div>
                  </div>
                  <div className="match-time">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                      <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"/>
                      <path d="M12 6V12L16 14" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                    </svg>
                    Saturday at 18:00
                  </div>
                </Card>
              </div>
            </div>

            {/* Recent Tournaments */}
            <div className="dashboard-section">
              <div className="section-header">
                <h2>Recent Tournaments</h2>
                <Link to="/tournaments" className="section-link">View All</Link>
              </div>
              
              {tournaments.length > 0 ? (
                <div className="tournaments-grid">
                  {tournaments.map(tournament => (
                    <Card key={tournament.id} hover className="tournament-card">
                      <div className="tournament-banner">
                        {tournament.banner_url ? (
                          <img src={tournament.banner_url} alt={tournament.name} />
                        ) : (
                          <div className="tournament-banner-placeholder">
                            <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
                              <path d="M6 2L3 6V20C3 20.5304 3.21071 21.0391 3.58579 21.4142C3.96086 21.7893 4.46957 22 5 22H19C19.5304 22 20.0391 21.7893 20.4142 21.4142C20.7893 21.0391 21 20.5304 21 20V6L18 2H6Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                            </svg>
                          </div>
                        )}
                      </div>
                      <div className="tournament-content">
                        <div className="tournament-header">
                          <h3>{tournament.name}</h3>
                          <Badge variant={getStatusBadge(tournament.status).variant}>
                            {getStatusBadge(tournament.status).label}
                          </Badge>
                        </div>
                        <p className="tournament-game">{tournament.game || 'Game TBD'}</p>
                        <div className="tournament-meta">
                          <span>{tournament.participants_count || 0} teams</span>
                          <span>•</span>
                          <span>{tournament.format || 'Single Elimination'}</span>
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              ) : (
                <Card className="empty-state">
                  <svg width="64" height="64" viewBox="0 0 24 24" fill="none">
                    <path d="M6 2L3 6V20C3 20.5304 3.21071 21.0391 3.58579 21.4142C3.96086 21.7893 4.46957 22 5 22H19C19.5304 22 20.0391 21.7893 20.4142 21.4142C20.7893 21.0391 21 20.5304 21 20V6L18 2H6Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                  <h3>No tournaments yet</h3>
                  <p>Create your first tournament to get started</p>
                  <Link to="/tournaments/create">
                    <Button variant="primary">Create Tournament</Button>
                  </Link>
                </Card>
              )}
            </div>

            {/* My Teams */}
            <div className="dashboard-section">
              <div className="section-header">
                <h2>My Teams</h2>
                <Link to="/teams" className="section-link">View All</Link>
              </div>
              
              {teams.length > 0 ? (
                <div className="teams-grid">
                  {teams.map(team => (
                    <Card key={team.id} hover className="team-card">
                      <div className="team-header">
                        <Avatar 
                          src={team.logo_url} 
                          username={team.name}
                          size="medium"
                        />
                        <div className="team-info">
                          <h3>{team.name}</h3>
                          <p className="team-tag">{team.tag}</p>
                        </div>
                      </div>
                      <div className="team-meta">
                        <div className="team-stat">
                          <span className="team-stat-value">{team.members_count || 0}</span>
                          <span className="team-stat-label">Members</span>
                        </div>
                        <div className="team-stat">
                          <span className="team-stat-value">{team.tournaments_count || 0}</span>
                          <span className="team-stat-label">Tournaments</span>
                        </div>
                      </div>
                      {team.captain && (
                        <div className="team-captain">
                          <span>Captain: {team.captain.username}</span>
                        </div>
                      )}
                    </Card>
                  ))}
                </div>
              ) : (
                <Card className="empty-state">
                  <svg width="64" height="64" viewBox="0 0 24 24" fill="none">
                    <path d="M17 21V19C17 17.9391 16.5786 16.9217 15.8284 16.1716C15.0783 15.4214 14.0609 15 13 15H5C3.93913 15 2.92172 15.4214 2.17157 16.1716C1.42143 16.9217 1 17.9391 1 19V21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    <path d="M9 11C11.2091 11 13 9.20914 13 7C13 4.79086 11.2091 3 9 3C6.79086 3 5 4.79086 5 7C5 9.20914 6.79086 11 9 11Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                  <h3>No teams yet</h3>
                  <p>Create or join a team to start competing</p>
                  <Link to="/teams/create">
                    <Button variant="primary">Create Team</Button>
                  </Link>
                </Card>
              )}
            </div>
          </div>
          </div>
        </>
      )}
    </>
  );
};

export default Dashboard;
