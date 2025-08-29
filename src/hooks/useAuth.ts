/**
 * Authentication Hook
 * Manages user authentication state and provides auth methods
 */

import { useState, useEffect, useContext, createContext, ReactNode } from 'react';
import { apiClient } from '../services/api';
import { pbClient } from '../services/pocketbase';

interface User {
  id: string;
  email: string;
  name: string;
  role: 'athlete' | 'brand' | 'admin';
  profile_completed: boolean;
  verified: boolean;
  avatar?: string;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (userData: {
    email: string;
    password: string;
    name: string;
    role: 'athlete' | 'brand';
  }) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = !!user && pbClient.isAuthenticated();

  // Initialize auth state from PocketBase
  useEffect(() => {
    const initAuth = async () => {
      try {
        if (pbClient.isAuthenticated()) {
          const currentUser = pbClient.getCurrentUser();
          if (currentUser) {
            setUser({
              id: currentUser.id,
              email: currentUser.email,
              name: currentUser.name,
              role: currentUser.role,
              profile_completed: currentUser.profile_completed,
              verified: currentUser.verified,
              avatar: currentUser.avatar,
            });

            // Set API client token
            apiClient.setAuthToken(pbClient.getAuthToken());
          }
        }
      } catch (error) {
        console.error('Error initializing auth:', error);
        // Clear invalid auth state
        pbClient.logout();
        apiClient.clearAuthToken();
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();
  }, []);

  // Listen for auth changes in PocketBase
  useEffect(() => {
    return pbClient.pb.authStore.onChange((token, model) => {
      if (model) {
        setUser({
          id: model.id,
          email: model.email,
          name: model.name,
          role: model.role,
          profile_completed: model.profile_completed,
          verified: model.verified,
          avatar: model.avatar,
        });
        apiClient.setAuthToken(token);
      } else {
        setUser(null);
        apiClient.clearAuthToken();
      }
    });
  }, []);

  const login = async (email: string, password: string) => {
    try {
      setIsLoading(true);
      
      // Login with PocketBase
      const authData = await pbClient.login(email, password);
      
      // Also authenticate with API server
      await apiClient.login(email, password);

      setUser({
        id: authData.record.id,
        email: authData.record.email,
        name: authData.record.name,
        role: authData.record.role,
        profile_completed: authData.record.profile_completed,
        verified: authData.record.verified,
        avatar: authData.record.avatar,
      });

      apiClient.setAuthToken(authData.token);
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (userData: {
    email: string;
    password: string;
    name: string;
    role: 'athlete' | 'brand';
  }) => {
    try {
      setIsLoading(true);

      // Register with API server
      const response = await apiClient.register(userData);

      // Also register with PocketBase
      const pbResponse = await pbClient.register(userData.email, userData.password, {
        name: userData.name,
        role: userData.role,
      });

      setUser({
        id: pbResponse.record.id,
        email: pbResponse.record.email,
        name: pbResponse.record.name,
        role: pbResponse.record.role,
        profile_completed: false,
        verified: false,
      });

      apiClient.setAuthToken(pbResponse.token);
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      setIsLoading(true);

      // Logout from API server
      await apiClient.logout().catch(console.error);

      // Logout from PocketBase
      pbClient.logout();

      setUser(null);
      apiClient.clearAuthToken();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const refreshUser = async () => {
    if (!isAuthenticated) return;

    try {
      const currentUser = pbClient.getCurrentUser();
      if (currentUser) {
        // Refresh user data from PocketBase
        const updatedUser = await pbClient.getRecordById('users', currentUser.id);
        setUser({
          id: updatedUser.id,
          email: updatedUser.email,
          name: updatedUser.name,
          role: updatedUser.role,
          profile_completed: updatedUser.profile_completed,
          verified: updatedUser.verified,
          avatar: updatedUser.avatar,
        });
      }
    } catch (error) {
      console.error('Error refreshing user:', error);
    }
  };

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated,
    login,
    register,
    logout,
    refreshUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default useAuth;