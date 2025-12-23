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

  // Logout (triggers backend logout and page reload)
  logout: async (): Promise<void> => {
    try {
      // Call logout endpoint (may return redirect)
      await fetch('/api/auth/logout', {
        method: 'GET',
        credentials: 'include',
      });
    } catch (error) {
      // Ignore errors from redirect response
      console.log('Logout: Cookie cleared');
    }
    // Always reload page to reset app state
    window.location.href = '/';
  },
};

