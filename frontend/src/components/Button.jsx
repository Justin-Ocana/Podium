import './Button.css';

const Button = ({ 
  children, 
  variant = 'primary', 
  size = 'medium', 
  type = 'button',
  disabled = false,
  loading = false,
  onClick,
  className = '',
  ...props 
}) => {
  const buttonClass = `btn btn--${variant} btn--${size} ${loading ? 'btn--loading' : ''} ${className}`;

  return (
    <button
      type={type}
      className={buttonClass}
      disabled={disabled || loading}
      onClick={onClick}
      {...props}
    >
      {loading ? 'Loading...' : children}
    </button>
  );
};

export default Button;
