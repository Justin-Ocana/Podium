import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../contexts/ToastContext';
import Navbar from '../components/Navbar';
import Card from '../components/Card';
import Button from '../components/Button';
import Input from '../components/Input';
import TeamLogoCropModal from '../components/TeamLogoCropModal';
import BannerPreviewModal from '../components/BannerPreviewModal';
import ParticleBackground from '../components/ParticleBackground';
import api from '../services/api';
import './CreateTeam.css';

const CreateTeam = () => {
  const { user, logout } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    tag: '',
    game: null,
    description: '',
    country: '',
    region: '',
    primary_color: '#ff4655',
    secondary_color: '#111111',
    looking_for_players: false
  });

  const [logoFile, setLogoFile] = useState(null);
  const [logoPreview, setLogoPreview] = useState(null);
  const [bannerFile, setBannerFile] = useState(null);
  const [bannerPreview, setBannerPreview] = useState(null);
  
  // Modals
  const [showLogoCropModal, setShowLogoCropModal] = useState(false);
  const [showBannerModal, setShowBannerModal] = useState(false);
  const [tempLogoImage, setTempLogoImage] = useState(null);
  const [tempBannerImage, setTempBannerImage] = useState(null);

  // Games search
  const [gameSearch, setGameSearch] = useState('');
  const [games, setGames] = useState([]);
  const [searchingGames, setSearchingGames] = useState(false);
  const [showGameResults, setShowGameResults] = useState(false);

  // Validation
  const [errors, setErrors] = useState({});
  const [tagAvailable, setTagAvailable] = useState(null);
  const [checkingTag, setCheckingTag] = useState(false);

  const [submitting, setSubmitting] = useState(false);

  // Auto-uppercase tag
  useEffect(() => {
    if (formData.tag) {
      const upperTag = formData.tag.toUpperCase();
      if (upperTag !== formData.tag) {
        setFormData(prev => ({ ...prev, tag: upperTag }));
      }
    }
  }, [formData.tag]);

  // Check tag availability
  useEffect(() => {
    if (formData.tag && formData.tag.length >= 2) {
      const timer = setTimeout(async () => {
        setCheckingTag(true);
        try {
          // TODO: Implement tag check endpoint
          // For now, simulate check
          setTagAvailable(true);
        } catch (error) {
          setTagAvailable(false);
        } finally {
          setCheckingTag(false);
        }
      }, 500);
      return () => clearTimeout(timer);
    } else {
      setTagAvailable(null);
    }
  }, [formData.tag]);

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
      setSearchingGames(false);
    }
  }, [gameSearch]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    // Clear error for this field
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: null }));
    }
  };

  const handleLogoChange = (e) => {
    const file = e.target.files[0];
    console.log('Logo file selected:', file);
    if (file) {
      if (file.size > 5 * 1024 * 1024) {
        showToast('Logo must be less than 5MB', 'error');
        return;
      }
      const reader = new FileReader();
      reader.onload = () => {
        console.log('Logo image loaded, setting tempLogoImage and opening modal');
        const imageData = reader.result;
        console.log('Image data length:', imageData.length);
        setTempLogoImage(imageData);
        setShowLogoCropModal(true);
        console.log('Modal state set to true');
      };
      reader.onerror = (error) => {
        console.error('Error reading logo file:', error);
        showToast('Error loading image', 'error');
      };
      reader.readAsDataURL(file);
    }
  };

  const handleLogoSave = (croppedFile) => {
    setLogoFile(croppedFile);
    setLogoPreview(URL.createObjectURL(croppedFile));
    setShowLogoCropModal(false);
    setTempLogoImage(null);
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
    }
  };

  const handleBannerSave = () => {
    // El archivo ya está guardado en bannerFile
    setShowBannerModal(false);
    setTempBannerImage(null);
  };

  const handleGameSelect = (game) => {
    setFormData(prev => ({ ...prev, game }));
    setShowGameResults(false);
    setGames([]);
    setGameSearch(''); // Limpiar el input de búsqueda
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.name || formData.name.length < 3) {
      newErrors.name = 'Team name must be at least 3 characters';
    }
    if (formData.name && formData.name.length > 50) {
      newErrors.name = 'Team name must be less than 50 characters';
    }

    if (!formData.tag || formData.tag.length < 2) {
      newErrors.tag = 'Tag must be at least 2 characters';
    }
    if (formData.tag && formData.tag.length > 5) {
      newErrors.tag = 'Tag must be less than 5 characters';
    }

    if (!formData.game) {
      newErrors.game = 'Please select a game';
    }

    if (formData.description && formData.description.length > 1000) {
      newErrors.description = 'Description must be less than 1000 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      showToast('Please fix the errors in the form', 'error');
      return;
    }

    setSubmitting(true);

    try {
      // Create team
      const teamData = {
        name: formData.name,
        tag: formData.tag,
        game_id: formData.game.rawg_id,
        description: formData.description || null,
        country: formData.country || null,
        region: formData.region || null,
        primary_color: formData.primary_color,
        secondary_color: formData.secondary_color,
        looking_for_players: formData.looking_for_players
      };

      const team = await api.createTeam(teamData);

      // Upload logo if provided
      if (logoFile) {
        try {
          await api.uploadTeamLogo(team.id, logoFile);
        } catch (error) {
          console.error('Failed to upload logo:', error);
        }
      }

      // Upload banner if provided
      if (bannerFile) {
        try {
          await api.uploadTeamBanner(team.id, bannerFile);
        } catch (error) {
          console.error('Failed to upload banner:', error);
        }
      }

      showToast('Team created successfully! 🎉', 'success');
      navigate(`/teams/${team.slug}`);
    } catch (error) {
      console.error('Failed to create team:', error);
      const errorMsg = error.data?.error || error.data?.detail || 'Failed to create team';
      showToast(errorMsg, 'error');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="page-layout">
      <ParticleBackground />
      <Navbar user={user} onLogout={logout} />
      
      <div className="page-container">
        <div className="create-team-header">
          <h1>Create Your Team</h1>
          <p className="page-subtitle">Build your competitive esports team</p>
        </div>

        <div className="create-team-layout">
          {/* Main Form */}
          <Card className="create-team-form">
            <form onSubmit={handleSubmit}>
              {/* Section 1: Team Identity */}
              <div className="form-section">
                <h3 className="section-title">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                    <circle cx="9" cy="7" r="4"/>
                    <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                    <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                  </svg>
                  Team Identity
                </h3>
                
                <div className="logo-upload-section">
                  <div className="logo-upload">
                    <input
                      type="file"
                      id="logo-upload"
                      accept="image/*"
                      onChange={handleLogoChange}
                      style={{ display: 'none' }}
                    />
                    <label htmlFor="logo-upload" className="logo-upload-label">
                      {logoPreview ? (
                        <img src={logoPreview} alt="Logo preview" className="logo-preview" />
                      ) : (
                        <div className="logo-placeholder">
                          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/>
                            <polyline points="17 8 12 3 7 8"/>
                            <line x1="12" y1="3" x2="12" y2="15"/>
                          </svg>
                          <span>Upload Logo</span>
                        </div>
                      )}
                    </label>
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-group flex-2">
                    <label htmlFor="name">Team Name *</label>
                    <Input
                      id="name"
                      name="name"
                      value={formData.name}
                      onChange={handleInputChange}
                      placeholder="Phoenix"
                      error={errors.name}
                      maxLength={50}
                    />
                    {errors.name && <span className="error-text">{errors.name}</span>}
                  </div>

                  <div className="form-group flex-1">
                    <label htmlFor="tag">Team Tag *</label>
                    <Input
                      id="tag"
                      name="tag"
                      value={formData.tag}
                      onChange={handleInputChange}
                      placeholder="PHX"
                      error={errors.tag}
                      maxLength={5}
                    />
                    {checkingTag && <span className="tag-status checking">Checking...</span>}
                    {tagAvailable === true && <span className="tag-status available">✓ Available</span>}
                    {tagAvailable === false && <span className="tag-status taken">✗ Tag taken</span>}
                    {errors.tag && <span className="error-text">{errors.tag}</span>}
                  </div>
                </div>
              </div>

              {/* Section 2: Game */}
              <div className="form-section">
                <h3 className="section-title">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <rect x="2" y="7" width="20" height="15" rx="2" ry="2"/>
                    <polyline points="17 2 12 7 7 2"/>
                  </svg>
                  Game *
                </h3>
                
                <div className="game-search-container">
                  {!formData.game && (
                    <>
                      <div className="input-wrapper">
                        <svg className="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <circle cx="11" cy="11" r="8"/>
                          <path d="m21 21-4.35-4.35"/>
                        </svg>
                        <Input
                          value={gameSearch}
                          onChange={(e) => setGameSearch(e.target.value)}
                          placeholder="Search for your game..."
                          error={errors.game}
                        />
                      </div>
                      
                      {searchingGames && (
                        <div className="game-search-loading">
                          <div className="spinner"></div>
                          <span>Searching games...</span>
                        </div>
                      )}
                      
                      {showGameResults && games.length > 0 && !searchingGames && (
                        <div className="game-results">
                          {games.map(game => (
                            <div
                              key={game.id}
                              className="game-result-item"
                              onClick={() => handleGameSelect(game)}
                            >
                              {game.cover_url ? (
                                <img src={game.cover_url} alt={game.name} className="game-cover" />
                              ) : (
                                <div className="game-cover-placeholder">
                                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                    <rect x="2" y="7" width="20" height="15" rx="2" ry="2"/>
                                    <polyline points="17 2 12 7 7 2"/>
                                  </svg>
                                </div>
                              )}
                              <div className="game-info">
                                <span className="game-name">{game.name}</span>
                                <div className="game-meta">
                                  {game.rating && (
                                    <span className="game-rating">⭐ {game.rating}</span>
                                  )}
                                  {game.genres && game.genres.length > 0 && (
                                    <span className="game-genre">{game.genres[0]}</span>
                                  )}
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                      
                      {showGameResults && games.length === 0 && !searchingGames && (
                        <div className="game-no-results">
                          <p>No games found</p>
                        </div>
                      )}
                    </>
                  )}
                  
                  {formData.game && (
                    <div className="selected-game">
                      {formData.game.cover_url ? (
                        <img src={formData.game.cover_url} alt={formData.game.name} className="selected-game-cover" />
                      ) : (
                        <div className="selected-game-placeholder">
                          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <rect x="2" y="7" width="20" height="15" rx="2" ry="2"/>
                            <polyline points="17 2 12 7 7 2"/>
                          </svg>
                        </div>
                      )}
                      <span>{formData.game.name}</span>
                      <button
                        type="button"
                        className="remove-game"
                        onClick={() => {
                          setFormData(prev => ({ ...prev, game: null }));
                          setGameSearch('');
                        }}
                      >
                        ✕
                      </button>
                    </div>
                  )}
                  
                  {errors.game && <span className="error-text">{errors.game}</span>}
                </div>
              </div>

              {/* Section 3: Description */}
              <div className="form-section">
                <h3 className="section-title">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    <polyline points="14 2 14 8 20 8"/>
                    <line x1="16" y1="13" x2="8" y2="13"/>
                    <line x1="16" y1="17" x2="8" y2="17"/>
                    <polyline points="10 9 9 9 8 9"/>
                  </svg>
                  Description
                </h3>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  placeholder="Describe your team goals, playstyle, or achievements..."
                  className="description-textarea"
                  maxLength={1000}
                  rows={4}
                />
                <span className="char-count">{formData.description.length}/1000</span>
              </div>

              {/* Section 4: Customization */}
              <div className="form-section">
                <h3 className="section-title">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="12" cy="12" r="3"/>
                    <path d="M12 1v6m0 6v6m5.2-13.2l-4.2 4.2m0 6l4.2 4.2M23 12h-6m-6 0H1m18.2 5.2l-4.2-4.2m0-6l4.2-4.2"/>
                  </svg>
                  Customization
                </h3>
                
                <div className="banner-upload-section">
                  <label>Banner (optional)</label>
                  <input
                    type="file"
                    id="banner-upload"
                    accept="image/*"
                    onChange={handleBannerChange}
                    style={{ display: 'none' }}
                  />
                  <label htmlFor="banner-upload" className="banner-upload-label">
                    {bannerPreview ? (
                      <img src={bannerPreview} alt="Banner preview" className="banner-preview" />
                    ) : (
                      <div className="banner-placeholder">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                          <circle cx="8.5" cy="8.5" r="1.5"/>
                          <polyline points="21 15 16 10 5 21"/>
                        </svg>
                        <span>Upload Banner</span>
                      </div>
                    )}
                  </label>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="primary_color">Primary Color</label>
                    <div className="color-input-wrapper">
                      <input
                        type="color"
                        id="primary_color"
                        name="primary_color"
                        value={formData.primary_color}
                        onChange={handleInputChange}
                        className="color-input"
                      />
                      <Input
                        value={formData.primary_color}
                        onChange={handleInputChange}
                        name="primary_color"
                        placeholder="#ff4655"
                      />
                    </div>
                  </div>

                  <div className="form-group">
                    <label htmlFor="secondary_color">Secondary Color</label>
                    <div className="color-input-wrapper">
                      <input
                        type="color"
                        id="secondary_color"
                        name="secondary_color"
                        value={formData.secondary_color}
                        onChange={handleInputChange}
                        className="color-input"
                      />
                      <Input
                        value={formData.secondary_color}
                        onChange={handleInputChange}
                        name="secondary_color"
                        placeholder="#111111"
                      />
                    </div>
                  </div>
                </div>
              </div>

              {/* Section 5: Location */}
              <div className="form-section">
                <h3 className="section-title">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                    <circle cx="12" cy="10" r="3"/>
                  </svg>
                  Location (optional)
                </h3>
                
                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="country">Country</label>
                    <select
                      id="country"
                      name="country"
                      value={formData.country}
                      onChange={handleInputChange}
                      className="select-input"
                    >
                      <option value="">Select country</option>
                      <option value="EC">Ecuador</option>
                      <option value="CO">Colombia</option>
                      <option value="PE">Peru</option>
                      <option value="AR">Argentina</option>
                      <option value="MX">Mexico</option>
                      <option value="US">United States</option>
                    </select>
                  </div>

                  <div className="form-group">
                    <label htmlFor="region">Region</label>
                    <select
                      id="region"
                      name="region"
                      value={formData.region}
                      onChange={handleInputChange}
                      className="select-input"
                    >
                      <option value="">Select region</option>
                      <option value="LATAM">LATAM</option>
                      <option value="NA">North America</option>
                      <option value="EU">Europe</option>
                      <option value="ASIA">Asia</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Section 6: Looking for Players */}
              <div className="form-section">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={formData.looking_for_players}
                    onChange={(e) => setFormData(prev => ({ ...prev, looking_for_players: e.target.checked }))}
                  />
                  <div>
                    <span>Looking for players</span>
                    <p className="checkbox-description">Your team will appear in the "Find Teams" section</p>
                  </div>
                </label>
              </div>

              {/* Submit Button */}
              <div className="form-actions">
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => navigate('/teams/my')}
                  disabled={submitting}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  variant="primary"
                  disabled={submitting}
                >
                  {submitting ? 'Creating...' : 'Create Team'}
                </Button>
              </div>
            </form>
          </Card>

          {/* Preview Card */}
          <Card className="team-preview-card">
            <h3 className="preview-title">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                <circle cx="12" cy="12" r="3"/>
              </svg>
              Team Preview
            </h3>
            
            <div 
              className="team-preview"
              style={{
                borderTop: `3px solid ${formData.primary_color}`,
                boxShadow: `0 0 30px ${formData.primary_color}20`
              }}
            >
              <div className="preview-banner">
                {bannerPreview ? (
                  <img src={bannerPreview} alt="Banner" />
                ) : (
                  <div style={{ 
                    width: '100%', 
                    height: '100%', 
                    background: `linear-gradient(135deg, ${formData.primary_color} 0%, ${formData.secondary_color} 100%)` 
                  }} />
                )}
                <div className="preview-banner-overlay" />
              </div>
              
              <div className="preview-content">
                {logoPreview && (
                  <div 
                    className="preview-logo"
                    style={{
                      boxShadow: `0 0 0 3px ${formData.primary_color}, 0 0 20px ${formData.primary_color}40, 0 8px 32px rgba(0, 0, 0, 0.6)`
                    }}
                  >
                    <img src={logoPreview} alt="Logo" />
                  </div>
                )}
                
                <div className="preview-info">
                  <h2 style={{ 
                    color: formData.primary_color,
                    textShadow: `0 0 20px ${formData.primary_color}80`
                  }}>
                    {formData.name || 'Team Name'}
                  </h2>
                  
                  <div className="preview-meta">
                    <span 
                      className="preview-tag" 
                      style={{ 
                        borderColor: formData.secondary_color,
                        color: formData.secondary_color,
                        boxShadow: `0 0 15px ${formData.secondary_color}40`
                      }}
                    >
                      [{formData.tag || 'TAG'}]
                    </span>
                    
                    {formData.game && (
                      <span className="preview-game">
                        {formData.game.cover_url && (
                          <img src={formData.game.cover_url} alt={formData.game.name} className="preview-game-cover" />
                        )}
                        {formData.game.name}
                      </span>
                    )}
                  </div>
                  
                  {formData.description && (
                    <p className="preview-description">{formData.description}</p>
                  )}
                </div>
              </div>
            </div>
          </Card>
        </div>
      </div>

      {/* Modals */}
      {console.log('Rendering modals - showLogoCropModal:', showLogoCropModal, 'tempLogoImage:', tempLogoImage ? 'YES' : 'NO')}
      {showLogoCropModal && tempLogoImage && (
        <TeamLogoCropModal
          image={tempLogoImage}
          onSave={handleLogoSave}
          onCancel={() => {
            setShowLogoCropModal(false);
            setTempLogoImage(null);
          }}
        />
      )}

      {showBannerModal && tempBannerImage && (
        <BannerPreviewModal
          imageUrl={tempBannerImage}
          onConfirm={handleBannerSave}
          onCancel={() => {
            setShowBannerModal(false);
            setTempBannerImage(null);
          }}
        />
      )}
    </div>
  );
};

export default CreateTeam;
