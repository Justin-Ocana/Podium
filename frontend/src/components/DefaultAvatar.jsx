const DefaultAvatar = ({ username, size = 'medium', className = '' }) => {
  const getInitials = (name) => {
    if (!name) return 'U';
    const parts = name.trim().split(' ');
    if (parts.length >= 2) {
      return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
  };

  const getSizeStyles = () => {
    switch (size) {
      case 'small': 
        return { width: '32px', height: '32px', fontSize: '12px' };
      case 'medium': 
        return { width: '48px', height: '48px', fontSize: '18px' };
      case 'large': 
        return { width: '96px', height: '96px', fontSize: '36px' };
      default: 
        return { width: '48px', height: '48px', fontSize: '18px' };
    }
  };

  const styles = getSizeStyles();
  const initials = getInitials(username);

  return (
    <div
      className={`default-avatar ${className}`}
      style={{
        width: styles.width,
        height: styles.height,
        borderRadius: '50%',
        background: 'linear-gradient(135deg, #3B82F6 0%, #A855F7 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'white',
        fontSize: styles.fontSize,
        fontWeight: '600',
        fontFamily: 'Inter, sans-serif',
        textTransform: 'uppercase',
        userSelect: 'none'
      }}
    >
      {initials}
    </div>
  );
};

export default DefaultAvatar;
