import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import Navbar from '../../components/Navbar';
import Card from '../../components/Card';
import Avatar from '../../components/Avatar';
import Button from '../../components/Button';
import Input from '../../components/Input';
import api from '../../services/api';
import './ProfileEdit.css';

const ProfileEdit = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    bio: user?.bio || '',
    country: user?.country || '',
    region: user?.region || '',
    steam_username: user?.steam_username || '',
    steam_url: user?.steam_url || '',
    riot_id: user?.riot_id || '',
    battlenet_id: user?.battlenet_id || '',
    discord_id: user?.discord_id || '',
    xbox_gamertag: user?.xbox_gamertag || '',
    psn_id: user?.psn_id || '',
    twitter_handle: user?.twitter_handle || '',
    twitch_username: user?.twitch_username || '',
    youtube_channel: user?.youtube_channel || ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (user) {
      setFormData({
        bio: user.bio || '',
        country: user.country || '',
        region: user.region || '',
        steam_username: user.steam_username || '',
        steam_url: user.steam_url || '',
        riot_id: user.riot_id || '',
        battlenet_id: user.battlenet_id || '',
        discord_id: user.discord_id || '',
        xbox_gamertag: user.xbox_gamertag || '',
        psn_id: user.psn_id || '',
        twitter_handle: user.twitter_handle || '',
        twitch_username: user.twitch_username || '',
        youtube_channel: user.youtube_channel || ''
      });
    }
  }, [user]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      await api.updateProfile(formData);
      navigate('/profile');
    } catch (error) {
      console.error('Failed to update profile:', error);
      setError('Failed to update profile. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    navigate('/profile');
  };

  return (
    <div className="page-layout">
      <Navbar user={user} onLogout={logout} />
      
      <div className="page-container">
        <div className="profile-edit-layout">
          <div className="profile-edit-header">
            <h1>Edit Profile</h1>
            <p>Update your profile information and gaming connections</p>
          </div>

          <Card className="profile-edit-card">
            <form onSubmit={handleSubmit} className="profile-edit-form">
              {/* Avatar Section */}
              <div className="form-section">
                <h3>Profile Picture</h3>
                <div className="avatar-section">
                  <Avatar 
                    src={user?.avatar_url} 
                    username={user?.username}
                    size="large"
                  />
                  <div className="avatar-info">
                    <p className="avatar-username">{user?.username}</p>
                    <p className="avatar-hint">Avatar upload coming soon</p>
                  </div>
                </div>
              </div>

              {/* Basic Info */}
              <div className="form-section">
                <h3>Basic Information</h3>
                <Input
                  label="Bio"
                  name="bio"
                  value={formData.bio}
                  onChange={handleChange}
                  placeholder="Tell us about yourself..."
                  maxLength={500}
                />
                <div className="form-row">
                  <Input
                    label="Country"
                    name="country"
                    value={formData.country}
                    onChange={handleChange}
                    placeholder="e.g., United States"
                  />
                  <Input
                    label="Region/State"
                    name="region"
                    value={formData.region}
                    onChange={handleChange}
                    placeholder="e.g., California"
                  />
                </div>
              </div>

              {/* Gaming Connections */}
              <div className="form-section">
                <h3>Gaming Connections</h3>
                <p className="section-description">
                  Connect your gaming accounts to verify your identity and make it easier for others to find you
                </p>
                <div className="form-row">
                  <Input
                    label="Steam Username"
                    name="steam_username"
                    value={formData.steam_username}
                    onChange={handleChange}
                    placeholder="Your Steam display name"
                  />
                  <Input
                    label="Steam Profile URL"
                    name="steam_url"
                    value={formData.steam_url}
                    onChange={handleChange}
                    placeholder="https://steamcommunity.com/id/..."
                  />
                </div>
                <div className="form-row">
                  <Input
                    label="Riot ID"
                    name="riot_id"
                    value={formData.riot_id}
                    onChange={handleChange}
                    placeholder="Username#TAG"
                  />
                </div>
                <div className="form-row">
                  <Input
                    label="Battle.net"
                    name="battlenet_id"
                    value={formData.battlenet_id}
                    onChange={handleChange}
                    placeholder="BattleTag#1234"
                  />
                  <Input
                    label="Discord"
                    name="discord_id"
                    value={formData.discord_id}
                    onChange={handleChange}
                    placeholder="username#1234"
                  />
                </div>
                <div className="form-row">
                  <Input
                    label="Xbox Gamertag"
                    name="xbox_gamertag"
                    value={formData.xbox_gamertag}
                    onChange={handleChange}
                    placeholder="Your gamertag"
                  />
                  <Input
                    label="PSN ID"
                    name="psn_id"
                    value={formData.psn_id}
                    onChange={handleChange}
                    placeholder="PlayStation Network ID"
                  />
                </div>
              </div>

              {/* Social Media */}
              <div className="form-section">
                <h3>Social Media (Optional)</h3>
                <p className="section-description">
                  Connect your social media for streaming and content creation
                </p>
                <div className="form-row">
                  <Input
                    label="Twitter/X"
                    name="twitter_handle"
                    value={formData.twitter_handle}
                    onChange={handleChange}
                    placeholder="username (without @)"
                  />
                  <Input
                    label="Twitch"
                    name="twitch_username"
                    value={formData.twitch_username}
                    onChange={handleChange}
                    placeholder="username"
                  />
                </div>
                <Input
                  label="YouTube"
                  name="youtube_channel"
                  value={formData.youtube_channel}
                  onChange={handleChange}
                  placeholder="Channel URL or handle"
                />
              </div>

              {error && (
                <div className="error-message">
                  {error}
                </div>
              )}

              {/* Actions */}
              <div className="form-actions">
                <Button type="submit" variant="primary" loading={loading}>
                  Save Changes
                </Button>
                <Button 
                  type="button" 
                  variant="secondary" 
                  onClick={handleCancel}
                  disabled={loading}
                >
                  Cancel
                </Button>
              </div>
            </form>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default ProfileEdit;
