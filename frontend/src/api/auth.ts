import { apiClient } from './client';

export interface User {
  public_id: string;
  user_name: string;
}

export const authApi = {
  // Redirects to Google OAuth login
  loginWithGoogle: () => {
    window.location.href = '/api/auth/google/login';
  },

  // Get current user info
  getCurrentUser: async (): Promise<User> => {
    return apiClient.get<User>('/users/me');
  },

  // Logout
  logout: () => {
    window.location.href = '/api/auth/logout';
  },
};

