// Avatar SVG alternativo con diseño más elaborado
const DefaultAvatarAlt = ({ username, size = 'medium', className = '' }) => {
  const getInitials = (name) => {
    if (!name) return 'U';
    const parts = name.trim().split(' ');
    if (parts.length >= 2) {
      return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
  };

  const getSizeValue = () => {
    switch (size) {
      case 'small': return 32;
      case 'medium': return 48;
      case 'large': return 96;
      default: return 48;
    }
  };

  const getFontSize = () => {
    switch (size) {
      case 'small': return '14px';
      case 'medium': return '18px';
      case 'large': return '36px';
      default: return '18px';
    }
  };

  const sizeValue = getSizeValue();
  const initials = getInitials(username);
  
  // Generate a consistent color based on username
  const getColorFromUsername = (name) => {
    if (!name) return { start: '#3B82F6', end: '#A855F7' };
    
    const colors = [
      { start: '#3B82F6', end: '#6366F1' }, // Blue to Indigo
      { start: '#8B5CF6', end: '#A855F7' }, // Violet to Purple
      { start: '#EC4899', end: '#F43F5E' }, // Pink to Rose
      { start: '#10B981', end: '#14B8A6' }, // Emerald to Teal
      { start: '#F59E0B', end: '#EF4444' }, // Amber to Red
      { start: '#06B6D4', end: '#3B82F6' }, // Cyan to Blue
    ];
    
    const hash = name.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    return colors[hash % colors.length];
  };

  const colors = getColorFromUsername(username);

  return (
    <svg
      width={sizeValue}
      height={sizeValue}
      viewBox="0 0 120 120"
      className={className}
      xmlns="http://www.w3.org/2000/svg"
    >
      <defs>
        <linearGradient id={`gradient-${username}`} x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor={colors.start} />
          <stop offset="100%" stopColor={colors.end} />
        </linearGradient>
        
        <radialGradient id={`radial-${username}`} cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="rgba(255, 255, 255, 0.2)" />
          <stop offset="100%" stopColor="rgba(255, 255, 255, 0)" />
        </radialGradient>
        
        <filter id={`glow-${username}`}>
          <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
          <feMerge>
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
      </defs>
      
      {/* Background */}
      <circle
        cx="60"
        cy="60"
        r="60"
        fill={`url(#gradient-${username})`}
      />
      
      {/* Overlay glow */}
      <circle
        cx="60"
        cy="60"
        r="60"
        fill={`url(#radial-${username})`}
      />
      
      {/* Decorative circles */}
      <circle
        cx="60"
        cy="60"
        r="52"
        fill="none"
        stroke="rgba(255, 255, 255, 0.15)"
        strokeWidth="1"
      />
      <circle
        cx="60"
        cy="60"
        r="45"
        fill="none"
        stroke="rgba(255, 255, 255, 0.1)"
        strokeWidth="0.5"
      />
      
      {/* Geometric pattern */}
      <path
        d="M 60 20 L 70 40 L 60 45 L 50 40 Z"
        fill="rgba(255, 255, 255, 0.05)"
      />
      <path
        d="M 60 100 L 70 80 L 60 75 L 50 80 Z"
        fill="rgba(255, 255, 255, 0.05)"
      />
      
      {/* Initials */}
      <text
        x="60"
        y="60"
        textAnchor="middle"
        dominantBaseline="central"
        fill="white"
        fontSize={getFontSize()}
        fontWeight="700"
        fontFamily="Inter, sans-serif"
        letterSpacing="1"
        filter={`url(#glow-${username})`}
      >
        {initials}
      </text>
    </svg>
  );
};

export default DefaultAvatarAlt;
