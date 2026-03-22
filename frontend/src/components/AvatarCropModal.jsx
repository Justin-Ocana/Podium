import { useState, useRef } from 'react';
import Button from './Button';
import './AvatarCropModal.css';

const AvatarCropModal = ({ imageUrl, username, onConfirm, onCancel }) => {
  const [zoom, setZoom] = useState(1);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const imageRef = useRef(null);
  const containerRef = useRef(null);

  // Calculate boundaries to keep circle within image
  const getBoundaries = () => {
    if (!containerRef.current) return { minX: 0, maxX: 0, minY: 0, maxY: 0 };
    
    const containerSize = containerRef.current.offsetWidth;
    const circleDiameter = containerSize * 0.8; // 80% of container
    const circleRadius = circleDiameter / 2;
    const imageSize = containerSize * zoom;
    
    // Calculate how much the image extends beyond the container on each side
    const imageOverhang = (imageSize - containerSize) / 2;
    
    // The circle must stay within the image bounds
    // When image is at center (position 0,0), circle is also centered
    // We can move the image until the circle edge touches the image edge
    // Max movement = imageOverhang - (distance from container edge to circle edge)
    const containerEdgeToCircleEdge = (containerSize - circleDiameter) / 2;
    const maxMove = imageOverhang - containerEdgeToCircleEdge;
    
    // If image is too small, limit movement
    if (maxMove <= 0) {
      return { minX: 0, maxX: 0, minY: 0, maxY: 0 };
    }
    
    return {
      minX: -maxMove,
      maxX: maxMove,
      minY: -maxMove,
      maxY: maxMove
    };
  };

  const clampPosition = (x, y) => {
    const bounds = getBoundaries();
    return {
      x: Math.max(bounds.minX, Math.min(bounds.maxX, x)),
      y: Math.max(bounds.minY, Math.min(bounds.maxY, y))
    };
  };

  const handleMouseDown = (e) => {
    setIsDragging(true);
    setDragStart({
      x: e.clientX - position.x,
      y: e.clientY - position.y
    });
  };

  const handleMouseMove = (e) => {
    if (!isDragging) return;
    
    const newX = e.clientX - dragStart.x;
    const newY = e.clientY - dragStart.y;
    
    const clamped = clampPosition(newX, newY);
    setPosition(clamped);
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleZoomChange = (e) => {
    const newZoom = parseFloat(e.target.value);
    setZoom(newZoom);
    
    // Re-clamp position with new zoom
    const clamped = clampPosition(position.x, position.y);
    setPosition(clamped);
  };

  return (
    <div className="avatar-crop-modal-overlay" onClick={onCancel}>
      <div className="avatar-crop-modal" onClick={(e) => e.stopPropagation()}>
        <div className="avatar-crop-modal-header">
          <h2>Personalizar imagen</h2>
          <button className="modal-close" onClick={onCancel}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" fill="currentColor"/>
            </svg>
          </button>
        </div>

        <div className="avatar-crop-modal-content">
          <div className="avatar-crop-container">
            {/* Main crop area */}
            <div 
              ref={containerRef}
              className="avatar-crop-area"
              onMouseDown={handleMouseDown}
              onMouseMove={handleMouseMove}
              onMouseUp={handleMouseUp}
              onMouseLeave={handleMouseUp}
            >
              <div className="crop-image-wrapper">
                <img 
                  ref={imageRef}
                  src={imageUrl} 
                  alt="Avatar crop" 
                  style={{
                    transform: `translate(${position.x}px, ${position.y}px) scale(${zoom})`,
                    cursor: isDragging ? 'grabbing' : 'grab'
                  }}
                  draggable={false}
                />
              </div>
              
              {/* Circular crop overlay */}
              <div className="crop-overlay">
                <div className="crop-circle"></div>
              </div>
            </div>

            {/* Zoom control */}
            <div className="avatar-zoom-control">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
              </svg>
              <input
                type="range"
                min="1"
                max="3"
                step="0.1"
                value={zoom}
                onChange={handleZoomChange}
                className="zoom-slider"
              />
              <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                <path d="M19 13H5v-2h14v2z"/>
              </svg>
            </div>

            <div className="avatar-crop-hint">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/>
              </svg>
              <span>Arrastra para reposicionar, usa el control deslizante para hacer zoom</span>
            </div>
          </div>

          {/* Preview section */}
          <div className="avatar-preview-section">
            <h3>Vista previa</h3>
            <div className="avatar-preview-grid">
              <div className="avatar-preview-item">
                <div className="preview-label">Grande</div>
                <div className="preview-avatar preview-large">
                  <div className="preview-circle">
                    <div className="preview-image-wrapper">
                      <img 
                        src={imageUrl} 
                        alt="Preview large"
                        style={{
                          transform: `translate(${position.x * 0.4}px, ${position.y * 0.4}px) scale(${zoom})`
                        }}
                      />
                    </div>
                  </div>
                </div>
              </div>

              <div className="avatar-preview-item">
                <div className="preview-label">Mediano</div>
                <div className="preview-avatar preview-medium">
                  <div className="preview-circle">
                    <div className="preview-image-wrapper">
                      <img 
                        src={imageUrl} 
                        alt="Preview medium"
                        style={{
                          transform: `translate(${position.x * 0.24}px, ${position.y * 0.24}px) scale(${zoom})`
                        }}
                      />
                    </div>
                  </div>
                </div>
              </div>

              <div className="avatar-preview-item">
                <div className="preview-label">Pequeño</div>
                <div className="preview-avatar preview-small">
                  <div className="preview-circle">
                    <div className="preview-image-wrapper">
                      <img 
                        src={imageUrl} 
                        alt="Preview small"
                        style={{
                          transform: `translate(${position.x * 0.14}px, ${position.y * 0.14}px) scale(${zoom})`
                        }}
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="avatar-preview-contexts">
              <div className="context-preview">
                <div className="context-label">En el perfil</div>
                <div className="context-card">
                  <div className="context-avatar-large">
                    <div className="preview-image-wrapper">
                      <img 
                        src={imageUrl} 
                        alt="Context large"
                        style={{
                          transform: `translate(${position.x * 0.24}px, ${position.y * 0.24}px) scale(${zoom})`
                        }}
                      />
                    </div>
                  </div>
                  <div className="context-info">
                    <div className="context-name">{username}</div>
                    <div className="context-text">Jugador competitivo</div>
                  </div>
                </div>
              </div>

              <div className="context-preview">
                <div className="context-label">En la barra de navegación</div>
                <div className="context-navbar">
                  <div className="navbar-items">
                    <span>Tournaments</span>
                    <span>Teams</span>
                  </div>
                  <div className="context-avatar-small">
                    <div className="preview-image-wrapper">
                      <img 
                        src={imageUrl} 
                        alt="Context small"
                        style={{
                          transform: `translate(${position.x * 0.08}px, ${position.y * 0.08}px) scale(${zoom})`
                        }}
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="avatar-crop-modal-footer">
          <Button variant="secondary" onClick={onCancel}>
            Cancelar
          </Button>
          <Button variant="primary" onClick={onConfirm}>
            Hecho
          </Button>
        </div>
      </div>
    </div>
  );
};

export default AvatarCropModal;
