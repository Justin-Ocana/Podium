import { useState, useCallback } from 'react';
import Cropper from 'react-easy-crop';
import Button from './Button';
import './TeamLogoCropModal.css';

const TeamLogoCropModal = ({ image, onSave, onCancel }) => {
  const [crop, setCrop] = useState({ x: 0, y: 0 });
  const [zoom, setZoom] = useState(1);
  const [croppedAreaPixels, setCroppedAreaPixels] = useState(null);

  console.log('TeamLogoCropModal rendered');
  console.log('- image prop:', image ? `YES (${image.substring(0, 50)}...)` : 'NO');
  console.log('- onSave prop:', typeof onSave);
  console.log('- onCancel prop:', typeof onCancel);

  const onCropComplete = useCallback((croppedArea, croppedAreaPixels) => {
    setCroppedAreaPixels(croppedAreaPixels);
  }, []);

  const createImage = (url) =>
    new Promise((resolve, reject) => {
      const image = new Image();
      image.addEventListener('load', () => resolve(image));
      image.addEventListener('error', (error) => reject(error));
      image.src = url;
    });

  const getCroppedImg = async (imageSrc, pixelCrop) => {
    const image = await createImage(imageSrc);
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    canvas.width = pixelCrop.width;
    canvas.height = pixelCrop.height;

    ctx.drawImage(
      image,
      pixelCrop.x,
      pixelCrop.y,
      pixelCrop.width,
      pixelCrop.height,
      0,
      0,
      pixelCrop.width,
      pixelCrop.height
    );

    return new Promise((resolve) => {
      canvas.toBlob((blob) => {
        resolve(blob);
      }, 'image/jpeg', 0.95);
    });
  };

  const handleSave = async () => {
    try {
      const croppedBlob = await getCroppedImg(image, croppedAreaPixels);
      const croppedFile = new File([croppedBlob], 'team-logo.jpg', { type: 'image/jpeg' });
      onSave(croppedFile);
    } catch (error) {
      console.error('Error cropping image:', error);
    }
  };

  return (
    <div className="modal-overlay" onClick={onCancel}>
      <div className="modal-content team-logo-crop-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Crop Team Logo</h2>
          <button className="modal-close" onClick={onCancel}>✕</button>
        </div>

        <div className="crop-container">
          <Cropper
            image={image}
            crop={crop}
            zoom={zoom}
            aspect={1}
            cropShape="rect"
            showGrid={true}
            onCropChange={setCrop}
            onCropComplete={onCropComplete}
            onZoomChange={setZoom}
          />
        </div>

        <div className="crop-controls">
          <label>
            Zoom
            <input
              type="range"
              value={zoom}
              min={1}
              max={3}
              step={0.1}
              onChange={(e) => setZoom(e.target.value)}
              className="zoom-slider"
            />
          </label>
        </div>

        <div className="modal-actions">
          <Button variant="secondary" onClick={onCancel}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleSave}>
            Save Logo
          </Button>
        </div>
      </div>
    </div>
  );
};

export default TeamLogoCropModal;
