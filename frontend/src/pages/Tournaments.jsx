import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import Navbar from '../components/Navbar';
import Card from '../components/Card';
import Badge from '../components/Badge';
import Button from '../components/Button';
import LoadingScreen from '../components/LoadingScreen';
import api from '../services/api';
import './Tournaments.css';

const Tournaments = () => {
  const { user, logout } = useAuth();
  const [tournaments, setTournaments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTournaments();
  }, []);

  const loadTournaments = async () => {
    try {
      const data = await api.getTournaments();
      setTournaments(data.results || []);
    } catch (error) {
      console.error('Failed to load tournaments:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {loading ? (
        <LoadingScreen message="Loading tournaments..." />
      ) : (
        <div className="page-layout">
          <Navbar user={user} onLogout={logout} />
          
          <div className="page-container">
            <div className="page-header">
              <div>
                <h1>Tournaments</h1>
                <p className="page-subtitle">Browse and join competitive tournaments</p>
              </div>
              <Button variant="primary">Create Tournament</Button>
            </div>

            {tournaments.length > 0 ? (
              <div className="tournaments-list">
                {tournaments.map(tournament => (
                  <Card key={tournament.id} hover className="tournament-item">
                    <h3>{tournament.name}</h3>
                    <Badge variant="info">{tournament.status}</Badge>
                  </Card>
                ))}
              </div>
            ) : (
              <Card className="empty-state">
                <h3>No tournaments available</h3>
                <p>Be the first to create a tournament</p>
                <Button variant="primary">Create Tournament</Button>
              </Card>
            )}
          </div>
        </div>
      )}
    </>
  );
};

export default Tournaments;
