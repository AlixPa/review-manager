import { apiClient } from './client';
import { Reward } from '../types/reward';

export const rewardsApi = {
  // Get rewards for a specific cycle
  getRewards: async (cycleOffset: number = 0): Promise<Reward[]> => {
    return apiClient.get<Reward[]>(`/rewards?cycle_offset=${cycleOffset}`);
  },
};

