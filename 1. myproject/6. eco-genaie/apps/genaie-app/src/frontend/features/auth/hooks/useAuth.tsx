import { useState, useCallback } from 'react';
import { authService } from '../services/authService';

interface AuthState {
  isAuthenticated: boolean;
  user: any | null;
}

export const useAuth = () => {
  const [authState, setAuthState] = useState<AuthState>({
    isAuthenticated: false,
    user: null,
  });

  const login = useCallback(async (email: string, password: string) => {
    try {
      const response = await authService.login(email, password);
      setAuthState({
        isAuthenticated: true,
        user: response.data,
      });
      localStorage.setItem('token', response.data.token);
    } catch (error) {
      throw error;
    }
  }, []);

  const logout = useCallback(() => {
    setAuthState({
      isAuthenticated: false,
      user: null,
    });
    localStorage.removeItem('token');
  }, []);

  const checkAuth = useCallback(() => {
    const token = localStorage.getItem('token');
    if (token) {
      setAuthState({
        isAuthenticated: true,
        user: JSON.parse(atob(token.split('.')[1])),
      });
    }
  }, []);

  return {
    ...authState,
    login,
    logout,
    checkAuth,
  };
}; 