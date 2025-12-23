import { apiClient } from './client';
import { User } from '../types/user';

export const usersApi = {
  // Get all users
  getUsers: async (): Promise<User[]> => {
    return apiClient.get<User[]>('/users');
  },
};

