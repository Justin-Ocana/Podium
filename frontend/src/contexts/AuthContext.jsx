import { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem('token'));

  useEffect(() => {
    if (token) {
      loadUser();
    } else {
      setLoading(false);
    }
  }, [token]);

  const loadUser = async () => {
    try {
      const userData = await api.getCurrentUser();
      setUser(userData);
    } catch (error) {
      console.error('Failed to load user:', error);
      logout();
    } finally {
      setLoading(false);
    }
  };

  const login = async (credentials) => {
    const response = await api.login(credentials);
    const { token: newToken, user_id } = response.auth;
    
    localStorage.setItem('token', newToken);
    localStorage.setItem('user_id', user_id);
    setToken(newToken);
    setUser(response.user);
    
    return response;
  };

  const register = async (userData) => {
    const response = await api.register(userData);
    const { token: newToken, user_id } = response.auth;
    
    localStorage.setItem('token', newToken);
    localStorage.setItem('user_id', user_id);
    setToken(newToken);
    setUser(response.user);
    
    return response;
  };

  const logout = async () => {
    try {
      if (token) {
        await api.logout();
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('token');
      localStorage.removeItem('user_id');
      setToken(null);
      setUser(null);
    }
  };

  const refreshUser = async () => {
    if (token) {
      try {
        const userData = await api.getCurrentUser();
        setUser(userData);
        return userData;
      } catch (error) {
        console.error('Failed to refresh user:', error);
        throw error;
      }
    }
  };

  const value = {
    user,
    token,
    loading,
    login,
    register,
    logout,
    refreshUser,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
