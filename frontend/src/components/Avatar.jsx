import DefaultAvatar from './DefaultAvatar';
import './Avatar.css';

const Avatar = ({ 
  src, 
  alt, 
  size = 'medium', 
  username,
  className = '' 
}) => {
  return (
    <div className={`avatar avatar--${size} ${className}`}>
      {src ? (
        <img src={src} alt={alt || username} />
      ) : (
        <DefaultAvatar username={username || alt} size={size} />
      )}
    </div>
  );
};

export default Avatar;
