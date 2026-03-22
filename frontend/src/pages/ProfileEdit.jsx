import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import Navbar from '../components/Navbar';
import Card from '../components/Card';
import Avatar from '../components/Avatar';
import Button from '../components/Button';
import BannerPreviewModal from '../components/BannerPreviewModal';
import AvatarCropModal from '../components/AvatarCropModal';
import ParticleBackground from '../components/ParticleBackground';
import api from '../services/api';
import './ProfileEdit.css';

const ProfileEdit = () => {
  const { user, logout, refreshUser } = useAuth();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    bio: '',
    country: '',
    region: '',
    steam_username: '',
    steam_url: '',
    riot_id: '',
    battlenet_id: '',
    discord_id: '',
    xbox_gamertag: '',
    psn_id: '',
    twitter_handle: '',
    twitch_username: '',
    youtube_channel: ''
  });
  const [loading, setLoading] = useState(false);
  const [uploadingAvatar, setUploadingAvatar] = useState(false);
  const [uploadingBanner, setUploadingBanner] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');
  const [avatarPreview, setAvatarPreview] = useState(null);
  const [bannerPreview, setBannerPreview] = useState(null);
  const [showBannerModal, setShowBannerModal] = useState(false);
  const [showAvatarModal, setShowAvatarModal] = useState(false);
  const [tempBannerFile, setTempBannerFile] = useState(null);
  const [tempBannerUrl, setTempBannerUrl] = useState(null);
  const [tempAvatarFile, setTempAvatarFile] = useState(null);
  const [tempAvatarUrl, setTempAvatarUrl] = useState(null);
  const [pendingAvatarFile, setPendingAvatarFile] = useState(null);
  const [pendingBannerFile, setPendingBannerFile] = useState(null);

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
    setSuccess(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess(false);
    
    try {
      // First upload images if there are pending files
      if (pendingAvatarFile) {
        setUploadingAvatar(true);
        await api.uploadAvatar(pendingAvatarFile);
        setUploadingAvatar(false);
      }

      if (pendingBannerFile) {
        setUploadingBanner(true);
        await api.uploadBanner(pendingBannerFile);
        setUploadingBanner(false);
      }

      // Then update profile data
      await api.updateProfile(formData);
      
      setSuccess(true);
      
      // Clean up pending files and preview URLs
      if (avatarPreview && avatarPreview.startsWith('blob:')) {
        URL.revokeObjectURL(avatarPreview);
      }
      if (bannerPreview && bannerPreview.startsWith('blob:')) {
        URL.revokeObjectURL(bannerPreview);
      }
      
      setPendingAvatarFile(null);
      setPendingBannerFile(null);
      
      // Refresh user data
      await refreshUser();
      
      setTimeout(() => {
        navigate(`/u/${user.username}`);
      }, 1500);
    } catch (error) {
      console.error('Failed to update profile:', error);
      setError(error.data?.error || 'Failed to update profile. Please try again.');
    } finally {
      setLoading(false);
      setUploadingAvatar(false);
      setUploadingBanner(false);
    }
  };

  const handleCancel = () => {
    navigate(`/u/${user.username}`);
  };

  const handleAvatarChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Validate file size (5MB)
    if (file.size > 5 * 1024 * 1024) {
      setError('Avatar file size must be less than 5MB');
      return;
    }

    // Validate file type
    if (!['image/jpeg', 'image/jpg', 'image/png', 'image/webp'].includes(file.type)) {
      setError('Avatar must be a JPEG, PNG, or WebP image');
      return;
    }

    // Create preview URL
    const previewUrl = URL.createObjectURL(file);
    setTempAvatarFile(file);
    setTempAvatarUrl(previewUrl);
    setShowAvatarModal(true);
    setError('');
  };

  const handleAvatarConfirm = () => {
    if (!tempAvatarFile) return;

    // Store file for later upload, don't upload yet
    setPendingAvatarFile(tempAvatarFile);
    setAvatarPreview(tempAvatarUrl);
    setShowAvatarModal(false);
    
    // Don't revoke URL yet, we need it for preview
    setTempAvatarFile(null);
  };

  const handleAvatarCancel = () => {
    setShowAvatarModal(false);
    setTempAvatarFile(null);
    if (tempAvatarUrl) {
      URL.revokeObjectURL(tempAvatarUrl);
      setTempAvatarUrl(null);
    }
  };

  const handleBannerChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Validate file size (10MB)
    if (file.size > 10 * 1024 * 1024) {
      setError('Banner file size must be less than 10MB');
      return;
    }

    // Validate file type
    if (!['image/jpeg', 'image/jpg', 'image/png', 'image/webp'].includes(file.type)) {
      setError('Banner must be a JPEG, PNG, or WebP image');
      return;
    }

    // Create preview URL
    const previewUrl = URL.createObjectURL(file);
    setTempBannerFile(file);
    setTempBannerUrl(previewUrl);
    setShowBannerModal(true);
    setError('');
  };

  const handleBannerConfirm = () => {
    if (!tempBannerFile) return;

    // Store file for later upload, don't upload yet
    setPendingBannerFile(tempBannerFile);
    setBannerPreview(tempBannerUrl);
    setShowBannerModal(false);
    
    // Don't revoke URL yet, we need it for preview
    setTempBannerFile(null);
  };

  const handleBannerCancel = () => {
    setShowBannerModal(false);
    setTempBannerFile(null);
    if (tempBannerUrl) {
      URL.revokeObjectURL(tempBannerUrl);
      setTempBannerUrl(null);
    }
  };

  const handleDeleteAvatar = async () => {
    if (!confirm('Are you sure you want to delete your avatar?')) return;

    setUploadingAvatar(true);
    setError('');

    try {
      await api.deleteAvatar();
      setAvatarPreview(null);
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
      // Refresh user data
      await refreshUser();
    } catch (error) {
      console.error('Failed to delete avatar:', error);
      setError(error.data?.error || 'Failed to delete avatar');
    } finally {
      setUploadingAvatar(false);
    }
  };

  const handleDeleteBanner = async () => {
    if (!confirm('Are you sure you want to delete your banner?')) return;

    setUploadingBanner(true);
    setError('');

    try {
      await api.deleteBanner();
      setBannerPreview(null);
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
      // Refresh user data
      await refreshUser();
    } catch (error) {
      console.error('Failed to delete banner:', error);
      setError(error.data?.error || 'Failed to delete banner');
    } finally {
      setUploadingBanner(false);
    }
  };

  return (
    <div className="page-layout">
      <ParticleBackground />
      <Navbar user={user} onLogout={logout} />
      
      {showBannerModal && tempBannerUrl && (
        <BannerPreviewModal
          imageUrl={tempBannerUrl}
          onConfirm={handleBannerConfirm}
          onCancel={handleBannerCancel}
        />
      )}

      {showAvatarModal && tempAvatarUrl && (
        <AvatarCropModal
          imageUrl={tempAvatarUrl}
          username={user?.username}
          onConfirm={handleAvatarConfirm}
          onCancel={handleAvatarCancel}
        />
      )}
      
      <div className="page-container profile-edit-container">
        <div className="profile-edit-header">
          <h1>Edit Profile</h1>
          <p>Update your personal information and connected accounts</p>
        </div>

        <form onSubmit={handleSubmit} className="profile-edit-grid">
          {/* Left Column */}
          <div className="profile-edit-main">

            {/* Banner Upload Section */}
            <Card className="edit-section">
              <h3 className="section-title">Profile Banner</h3>
              <div className="banner-upload">
                <div className="banner-preview">
                  {bannerPreview || user?.banner_url ? (
                    <img 
                      src={bannerPreview || user?.banner_url} 
                      alt="Banner preview" 
                      style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                    />
                  ) : (
                    <div className="banner-placeholder">
                      <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
                        <path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z" fill="currentColor"/>
                      </svg>
                      <span>Banner preview</span>
                    </div>
                  )}
                </div>
                <div className="banner-upload-actions">
                  <input
                    type="file"
                    id="banner-upload"
                    accept="image/jpeg,image/jpg,image/png,image/webp"
                    onChange={handleBannerChange}
                    style={{ display: 'none' }}
                  />
                  <Button 
                    type="button" 
                    variant="primary" 
                    onClick={() => document.getElementById('banner-upload').click()}
                    loading={uploadingBanner}
                    disabled={uploadingBanner}
                  >
                    {uploadingBanner ? 'Uploading...' : (user?.banner_url ? 'Change Banner' : 'Upload Banner')}
                  </Button>
                  {(user?.banner_url || bannerPreview) && (
                    <Button 
                      type="button" 
                      variant="secondary" 
                      onClick={handleDeleteBanner}
                      disabled={uploadingBanner}
                    >
                      Delete Banner
                    </Button>
                  )}
                  <span className="upload-hint">1920x400px recommended, max 10MB</span>
                </div>
              </div>
            </Card>

            {/* Profile Picture */}
            <Card className="edit-section">
              <h3 className="section-title">Profile Picture</h3>
              <div className="avatar-upload">
                <Avatar 
                  src={avatarPreview || user?.avatar_url} 
                  username={user?.username}
                  size="large"
                  className="avatar-preview"
                />
                <div className="avatar-upload-actions">
                  <input
                    type="file"
                    id="avatar-upload"
                    accept="image/jpeg,image/jpg,image/png,image/webp"
                    onChange={handleAvatarChange}
                    style={{ display: 'none' }}
                  />
                  <Button 
                    type="button" 
                    variant="primary"
                    onClick={() => document.getElementById('avatar-upload').click()}
                    loading={uploadingAvatar}
                    disabled={uploadingAvatar}
                  >
                    {uploadingAvatar ? 'Uploading...' : (user?.avatar_url ? 'Change Photo' : 'Upload Photo')}
                  </Button>
                  {(user?.avatar_url || avatarPreview) && (
                    <Button 
                      type="button" 
                      variant="secondary" 
                      onClick={handleDeleteAvatar}
                      disabled={uploadingAvatar}
                    >
                      Delete Photo
                    </Button>
                  )}
                  <span className="upload-hint">Max 5MB, square recommended</span>
                </div>
              </div>
            </Card>

            {/* Basic Information */}
            <Card className="edit-section">
              <h3 className="section-title">Basic Information</h3>
              <div className="form-fields">
                <div className="form-field">
                  <label>Bio</label>
                  <textarea
                    name="bio"
                    value={formData.bio}
                    onChange={handleChange}
                    placeholder="Tell us about yourself..."
                    maxLength={500}
                    rows={4}
                  />
                  <span className="field-hint">{formData.bio.length}/500</span>
                </div>
                <div className="form-row">
                  <div className="form-field">
                    <label>Country</label>
                    <input
                      type="text"
                      name="country"
                      value={formData.country}
                      onChange={handleChange}
                      placeholder="e.g., United States"
                    />
                  </div>
                  <div className="form-field">
                    <label>Region/State</label>
                    <input
                      type="text"
                      name="region"
                      value={formData.region}
                      onChange={handleChange}
                      placeholder="e.g., California"
                    />
                  </div>
                </div>
              </div>
            </Card>


            {/* Gaming Connections */}
            <Card className="edit-section">
              <h3 className="section-title">Gaming Connections</h3>
              <p className="section-description">Connect gaming accounts to verify your profile</p>
              <div className="form-fields gaming-connections-grid">
                {/* Steam */}
                <div className="platform-field">
                  <div className="platform-label">
                    <div className="platform-icon platform-icon-steam">
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M11.979 0C5.678 0 .511 4.86.022 11.037l6.432 2.658c.545-.371 1.203-.59 1.912-.59.063 0 .125.004.188.006l2.861-4.142V8.91c0-2.495 2.028-4.524 4.524-4.524 2.494 0 4.524 2.031 4.524 4.527s-2.03 4.525-4.524 4.525h-.105l-4.076 2.911c0 .052.004.105.004.159 0 1.875-1.515 3.396-3.39 3.396-1.635 0-3.016-1.173-3.331-2.727L.436 15.27C1.862 20.307 6.486 24 11.979 24c6.627 0 11.999-5.373 11.999-12S18.605 0 11.979 0zM7.54 18.21l-1.473-.61c.262.543.714.999 1.314 1.25 1.297.539 2.793-.076 3.332-1.375.263-.63.264-1.319.005-1.949s-.75-1.121-1.377-1.383c-.624-.26-1.29-.249-1.878-.03l1.523.63c.956.4 1.409 1.5 1.009 2.455-.397.957-1.497 1.41-2.454 1.012H7.54zm11.415-9.303c0-1.662-1.353-3.015-3.015-3.015-1.665 0-3.015 1.353-3.015 3.015 0 1.665 1.35 3.015 3.015 3.015 1.663 0 3.015-1.35 3.015-3.015zm-5.273-.005c0-1.252 1.013-2.266 2.265-2.266 1.249 0 2.266 1.014 2.266 2.266 0 1.251-1.017 2.265-2.266 2.265-1.253 0-2.265-1.014-2.265-2.265z"/>
                      </svg>
                    </div>
                    <span>Steam</span>
                  </div>
                  <div className="platform-inputs">
                    <input
                      type="text"
                      name="steam_username"
                      value={formData.steam_username}
                      onChange={handleChange}
                      placeholder="Username"
                    />
                    <input
                      type="text"
                      name="steam_url"
                      value={formData.steam_url}
                      onChange={handleChange}
                      placeholder="Profile URL"
                    />
                  </div>
                </div>

                {/* Riot */}
                <div className="platform-field">
                  <div className="platform-label">
                    <div className="platform-icon platform-icon-riot">
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12.534 21.77l-1.09-2.81 10.52.54-.451 4.5zM15.06 0L.307 6.969 2.59 17.471H5.6l-.52-7.512.461-.144 1.81 7.656h3.126l-.116-9.15.462-.144 1.582 9.294h3.31l.78-11.053.462-.144.82 11.197h4.376l1.54-15.37Z"/>
                      </svg>
                    </div>
                    <span>Riot</span>
                  </div>
                  <div className="platform-inputs">
                    <input
                      type="text"
                      name="riot_id"
                      value={formData.riot_id}
                      onChange={handleChange}
                      placeholder="Username#TAG"
                    />
                  </div>
                </div>


                {/* Battle.net */}
                <div className="platform-field">
                  <div className="platform-label">
                    <div className="platform-icon platform-icon-battlenet">
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M11.907 8.624c-.261 0-.48.037-.672.112-.192.075-.352.18-.48.315-.128.136-.224.298-.288.486-.064.189-.096.396-.096.621 0 .224.032.43.096.618.064.187.16.349.288.486.128.136.288.241.48.315.192.075.411.112.672.112.261 0 .48-.037.672-.112.192-.074.352-.179.48-.315.128-.137.224-.299.288-.486.064-.188.096-.394.096-.618 0-.225-.032-.432-.096-.621-.064-.188-.16-.35-.288-.486-.128-.135-.288-.24-.48-.315-.192-.075-.411-.112-.672-.112zm0-8.624C5.373 0 0 5.373 0 12s5.373 12 11.907 12c6.533 0 11.906-5.373 11.906-12S18.44 0 11.907 0zm6.384 15.168c-.288.544-.672 1.024-1.152 1.44-.48.416-1.024.736-1.632.96-.608.224-1.248.336-1.92.336-.672 0-1.312-.112-1.92-.336-.608-.224-1.152-.544-1.632-.96-.48-.416-.864-.896-1.152-1.44-.288-.544-.432-1.136-.432-1.776 0-.64.144-1.232.432-1.776.288-.544.672-1.024 1.152-1.44.48-.416 1.024-.736 1.632-.96.608-.224 1.248-.336 1.92-.336.672 0 1.312.112 1.92.336.608.224 1.152.544 1.632.96.48.416.864.896 1.152 1.44.288.544.432 1.136.432 1.776 0 .64-.144 1.232-.432 1.776z"/>
                      </svg>
                    </div>
                    <span>Battle.net</span>
                  </div>
                  <div className="platform-inputs">
                    <input
                      type="text"
                      name="battlenet_id"
                      value={formData.battlenet_id}
                      onChange={handleChange}
                      placeholder="BattleTag#1234"
                    />
                  </div>
                </div>

                {/* Discord */}
                <div className="platform-field">
                  <div className="platform-label">
                    <div className="platform-icon platform-icon-discord">
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057 19.9 19.9 0 0 0 5.993 3.03.078.078 0 0 0 .084-.028c.462-.63.874-1.295 1.226-1.994a.076.076 0 0 0-.041-.106 13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008-.128 10.2 10.2 0 0 0 .372-.292.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0 a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.892.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z"/>
                      </svg>
                    </div>
                    <span>Discord</span>
                  </div>
                  <div className="platform-inputs">
                    <input
                      type="text"
                      name="discord_id"
                      value={formData.discord_id}
                      onChange={handleChange}
                      placeholder="username#1234"
                    />
                  </div>
                </div>


                {/* Xbox */}
                <div className="platform-field">
                  <div className="platform-label">
                    <div className="platform-icon platform-icon-xbox">
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M4.102 21.033A11.947 11.947 0 0 0 12 24a11.96 11.96 0 0 0 7.902-2.967c1.877-1.912-4.316-8.709-7.902-11.417-3.582 2.708-9.779 9.505-7.898 11.417zm11.16-14.406c2.5 2.961 7.484 10.313 6.076 12.912A11.942 11.942 0 0 0 24 12.004a11.95 11.95 0 0 0-3.57-8.536 12.607 12.607 0 0 0-5.168 3.159zM12 0C9.348 0 6.872.959 4.898 2.565a12.607 12.607 0 0 0-5.168-3.159A11.95 11.95 0 0 0 0 12.004c0 2.893 1.027 5.547 2.738 7.535 1.408-2.599 3.592-9.951 6.092-12.912C10.32 5.094 11.178 4.109 12 3.285c.822.824 1.68 1.809 3.17 3.342z"/>
                      </svg>
                    </div>
                    <span>Xbox</span>
                  </div>
                  <div className="platform-inputs">
                    <input
                      type="text"
                      name="xbox_gamertag"
                      value={formData.xbox_gamertag}
                      onChange={handleChange}
                      placeholder="Gamertag"
                    />
                  </div>
                </div>

                {/* PlayStation */}
                <div className="platform-field">
                  <div className="platform-label">
                    <div className="platform-icon platform-icon-playstation">
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M8.985 2.596v17.548l3.915 1.261V6.688c0-.69.304-1.151.794-.991.636.181.794.814.794 1.505v5.876c2.441 1.193 4.362-.002 4.362-3.153 0-3.237-1.126-4.675-4.438-5.827-1.307-.448-3.728-1.186-5.427-1.502zm4.656 16.242l6.296-2.275c.715-.258.826-.625.246-.818-.586-.192-1.637-.139-2.357.123l-4.205 1.5v-2.042l.24-.085s1.201-.42 2.913-.615c1.696-.18 3.785.029 5.437.661 1.848.601 2.041 1.472 1.576 2.072-.465.6-1.622 1.036-1.622 1.036l-8.544 3.107V18.84l.02-.002zM1.808 18.6c-1.9-.545-2.214-1.668-1.352-2.321.801-.585 2.159-1.051 2.159-1.051l5.616-2.013v2.155L4.181 16.83c-.718.258-.826.625-.246.818.586.192 1.637.139 2.357-.123l2.939-1.039v1.795c-.121.029-.256.044-.391.073-2.009.405-4.165.266-6.032-.154z"/>
                      </svg>
                    </div>
                    <span>PlayStation</span>
                  </div>
                  <div className="platform-inputs">
                    <input
                      type="text"
                      name="psn_id"
                      value={formData.psn_id}
                      onChange={handleChange}
                      placeholder="PSN ID"
                    />
                  </div>
                </div>
              </div>
            </Card>


            {/* Social Media */}
            <Card className="edit-section social-section">
              <h3 className="section-title">Social Media <span className="optional-badge">(Optional)</span></h3>
              <div className="form-fields social-fields">
                <div className="form-row">
                  <div className="form-field">
                    <label>Twitter/X</label>
                    <input
                      type="text"
                      name="twitter_handle"
                      value={formData.twitter_handle}
                      onChange={handleChange}
                      placeholder="username"
                    />
                  </div>
                  <div className="form-field">
                    <label>Twitch</label>
                    <input
                      type="text"
                      name="twitch_username"
                      value={formData.twitch_username}
                      onChange={handleChange}
                      placeholder="username"
                    />
                  </div>
                </div>
                <div className="form-field">
                  <label>YouTube</label>
                  <input
                    type="text"
                    name="youtube_channel"
                    value={formData.youtube_channel}
                    onChange={handleChange}
                    placeholder="Channel URL or handle"
                  />
                </div>
              </div>
            </Card>
          </div>

          {/* Right Column - Actions */}
          <div className="profile-edit-sidebar">
            <Card className="edit-actions-card">
              <h3 className="section-title">Save Changes</h3>
              {(pendingAvatarFile || pendingBannerFile) && (
                <div className="pending-changes-notice">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M12 9v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                  </svg>
                  <div className="notice-content">
                    <span className="notice-title">Pending Upload</span>
                    <span className="notice-text">
                      {pendingAvatarFile && pendingBannerFile 
                        ? 'Avatar and banner will be uploaded'
                        : pendingAvatarFile 
                        ? 'Avatar will be uploaded'
                        : 'Banner will be uploaded'}
                    </span>
                  </div>
                </div>
              )}
              {success && (
                <div className="success-message">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                  </svg>
                  <div className="message-content">
                    <span className="message-title">Success!</span>
                    <span className="message-text">Profile updated successfully</span>
                  </div>
                </div>
              )}
              {error && (
                <div className="error-message">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                  </svg>
                  <div className="message-content">
                    <span className="message-title">Error</span>
                    <span className="message-text">{error}</span>
                  </div>
                </div>
              )}
              <div className="edit-actions">
                <Button type="submit" variant="primary" loading={loading} fullWidth>
                  {loading 
                    ? (uploadingAvatar || uploadingBanner 
                      ? 'Uploading images...' 
                      : 'Saving...')
                    : 'Save Changes'}
                </Button>
                <Button 
                  type="button" 
                  variant="secondary" 
                  onClick={handleCancel}
                  disabled={loading}
                  fullWidth
                >
                  Cancel
                </Button>
              </div>
            </Card>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ProfileEdit;
