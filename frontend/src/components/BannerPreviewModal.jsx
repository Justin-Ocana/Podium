import { useState } from 'react';
import Button from './Button';
import './BannerPreviewModal.css';

const BannerPreviewModal = ({ imageUrl, onConfirm, onCancel }) => {
  const [activeView, setActiveView] = useState('desktop');

  const views = [
    { id: 'tv', label: 'Visible on TVs', width: '100%', height: '200px' },
    { id: 'desktop', label: 'Visible on computers', width: '100%', height: '140px' },
    { id: 'mobile', label: 'Visible on all devices', width: '100%', height: '100px' }
  ];

  return (
    <div className="banner-preview-modal-overlay" onClick={onCancel}>
      <div className="banner-preview-modal" onClick={(e) => e.stopPropagation()}>
        <div className="banner-preview-modal-header">
          <h2>Customize Banner</h2>
          <button className="modal-close" onClick={onCancel}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" fill="currentColor"/>
            </svg>
          </button>
        </div>

        <div className="banner-preview-modal-content">
          <div className="banner-preview-container">
            {/* Main preview area */}
            <div className="banner-preview-main">
              <img src={imageUrl} alt="Banner preview" />
              
              {/* Overlay guides for different views */}
              <div className={`preview-guide preview-guide-tv ${activeView === 'tv' ? 'active' : ''}`}>
                <span className="guide-label">Visible on TVs</span>
              </div>
              <div className={`preview-guide preview-guide-desktop ${activeView === 'desktop' ? 'active' : ''}`}>
                <span className="guide-label">Visible on computers</span>
              </div>
              <div className={`preview-guide preview-guide-mobile ${activeView === 'mobile' ? 'active' : ''}`}>
                <span className="guide-label">Visible on all devices</span>
              </div>
            </div>

            {/* View selector tabs */}
            <div className="banner-preview-tabs">
              {views.map(view => (
                <button
                  key={view.id}
                  className={`preview-tab ${activeView === view.id ? 'active' : ''}`}
                  onClick={() => setActiveView(view.id)}
                  onMouseEnter={() => setActiveView(view.id)}
                >
                  {view.label}
                </button>
              ))}
            </div>

            {/* Device previews */}
            <div className="banner-device-previews">
              <div className="device-preview">
                <div className="device-label">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M21 3H3c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h5v2h8v-2h5c1.1 0 1.99-.9 1.99-2L23 5c0-1.1-.9-2-2-2zm0 14H3V5h18v12z"/>
                  </svg>
                  <span>Television</span>
                </div>
                <div className="device-frame device-tv">
                  <img src={imageUrl} alt="TV preview" />
                </div>
              </div>

              <div className="device-preview">
                <div className="device-label">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M20 18c1.1 0 1.99-.9 1.99-2L22 6c0-1.1-.9-2-2-2H4c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2H0v2h24v-2h-4zM4 6h16v10H4V6z"/>
                  </svg>
                  <span>Computer</span>
                </div>
                <div className="device-frame device-desktop">
                  <img src={imageUrl} alt="Desktop preview" />
                </div>
              </div>

              <div className="device-preview">
                <div className="device-label">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M17 1.01L7 1c-1.1 0-2 .9-2 2v18c0 1.1.9 2 2 2h10c1.1 0 2-.9 2-2V3c0-1.1-.9-1.99-2-1.99zM17 19H7V5h10v14z"/>
                  </svg>
                  <span>Mobile</span>
                </div>
                <div className="device-frame device-mobile">
                  <img src={imageUrl} alt="Mobile preview" />
                </div>
              </div>
            </div>

            <div className="banner-preview-info">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/>
              </svg>
              <p>The visible area of the banner varies by device. Make sure important content is in the center.</p>
            </div>
          </div>
        </div>

        <div className="banner-preview-modal-footer">
          <Button variant="secondary" onClick={onCancel}>
            Cancel
          </Button>
          <Button variant="primary" onClick={onConfirm}>
            Done
          </Button>
        </div>
      </div>
    </div>
  );
};

export default BannerPreviewModal;
