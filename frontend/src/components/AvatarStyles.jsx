// Diferentes estilos de avatares SVG para Podium

// Estilo 1: Minimalista con gradiente
export const MinimalAvatar = ({ username, size = 48 }) => {
  const getInitials = (name) => {
    if (!name) return 'U';
    return name.substring(0, 2).toUpperCase();
  };

  return (
    <svg width={size} height={size} viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="minimal-grad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#3B82F6" />
          <stop offset="100%" stopColor="#A855F7" />
        </linearGradient>
      </defs>
      <circle cx="50" cy="50" r="50" fill="url(#minimal-grad)" />
      <text
        x="50"
        y="50"
        textAnchor="middle"
        dominantBaseline="central"
        fill="white"
        fontSize="32"
        fontWeight="600"
        fontFamily="Inter, sans-serif"
      >
        {getInitials(username)}
      </text>
    </svg>
  );
};

// Estilo 2: Gamer/Esports con hexágono
export const GamerAvatar = ({ username, size = 48 }) => {
  const getInitials = (name) => {
    if (!name) return 'U';
    return name.substring(0, 2).toUpperCase();
  };

  return (
    <svg width={size} height={size} viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="gamer-grad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#22D3EE" />
          <stop offset="50%" stopColor="#3B82F6" />
          <stop offset="100%" stopColor="#A855F7" />
        </linearGradient>
        <clipPath id="hexagon-clip">
          <polygon points="50,5 90,27.5 90,72.5 50,95 10,72.5 10,27.5" />
        </clipPath>
      </defs>
      
      {/* Background hexagon */}
      <polygon
        points="50,5 90,27.5 90,72.5 50,95 10,72.5 10,27.5"
        fill="url(#gamer-grad)"
      />
      
      {/* Inner hexagon border */}
      <polygon
        points="50,10 85,30 85,70 50,90 15,70 15,30"
        fill="none"
        stroke="rgba(255, 255, 255, 0.2)"
        strokeWidth="1"
      />
      
      {/* Initials */}
      <text
        x="50"
        y="50"
        textAnchor="middle"
        dominantBaseline="central"
        fill="white"
        fontSize="28"
        fontWeight="700"
        fontFamily="Inter, sans-serif"
      >
        {getInitials(username)}
      </text>
    </svg>
  );
};

// Estilo 3: Shield/Badge (para capitanes o VIP)
export const ShieldAvatar = ({ username, size = 48 }) => {
  const getInitials = (name) => {
    if (!name) return 'U';
    return name.substring(0, 2).toUpperCase();
  };

  return (
    <svg width={size} height={size} viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="shield-grad" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="#F59E0B" />
          <stop offset="100%" stopColor="#EF4444" />
        </linearGradient>
      </defs>
      
      {/* Shield shape */}
      <path
        d="M 50 5 L 85 20 L 85 50 Q 85 80 50 95 Q 15 80 15 50 L 15 20 Z"
        fill="url(#shield-grad)"
      />
      
      {/* Inner border */}
      <path
        d="M 50 10 L 80 23 L 80 50 Q 80 77 50 90 Q 20 77 20 50 L 20 23 Z"
        fill="none"
        stroke="rgba(255, 255, 255, 0.3)"
        strokeWidth="1"
      />
      
      {/* Initials */}
      <text
        x="50"
        y="52"
        textAnchor="middle"
        dominantBaseline="central"
        fill="white"
        fontSize="26"
        fontWeight="700"
        fontFamily="Inter, sans-serif"
      >
        {getInitials(username)}
      </text>
    </svg>
  );
};

// Estilo 4: Neon/Cyberpunk
export const NeonAvatar = ({ username, size = 48 }) => {
  const getInitials = (name) => {
    if (!name) return 'U';
    return name.substring(0, 2).toUpperCase();
  };

  return (
    <svg width={size} height={size} viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="neon-grad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#06B6D4" />
          <stop offset="100%" stopColor="#A855F7" />
        </linearGradient>
        <filter id="neon-glow">
          <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
          <feMerge>
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
      </defs>
      
      {/* Background */}
      <circle cx="50" cy="50" r="50" fill="#0a0f1e" />
      
      {/* Neon circle */}
      <circle
        cx="50"
        cy="50"
        r="45"
        fill="none"
        stroke="url(#neon-grad)"
        strokeWidth="3"
        filter="url(#neon-glow)"
      />
      
      {/* Inner circle */}
      <circle
        cx="50"
        cy="50"
        r="38"
        fill="none"
        stroke="rgba(34, 211, 238, 0.3)"
        strokeWidth="1"
      />
      
      {/* Initials */}
      <text
        x="50"
        y="50"
        textAnchor="middle"
        dominantBaseline="central"
        fill="#22D3EE"
        fontSize="30"
        fontWeight="700"
        fontFamily="Inter, sans-serif"
        filter="url(#neon-glow)"
      >
        {getInitials(username)}
      </text>
    </svg>
  );
};
