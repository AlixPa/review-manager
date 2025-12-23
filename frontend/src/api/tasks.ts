import { apiClient } from './client';
import { Task } from '../types/task';
import { UpdateAction } from '../types/updateAction';

interface CreateTaskRequest {
  pr_link: string;
  priority: number;
  lines_of_code: number;
  reviewers_id: string[];
}

export const tasksApi = {
  // Get tasks assigned to me (for pending review)
  getAssignedTasks: async (state: number): Promise<Task[]> => {
    return apiClient.get<Task[]>(`/tasks/todo?state=${state}`);
  },

  // Get tasks I created (for pending changes and manage view)
  getMyTasks: async (state: number): Promise<Task[]> => {
    return apiClient.get<Task[]>(`/tasks/my_tasks?state=${state}`);
  },

  // Update a task with a specific action
  updateTask: async (taskId: number, action: UpdateAction): Promise<void> => {
    return apiClient.patch<void>(`/tasks/${taskId}`, {
      action: action,
    });
  },

  // Create a new task
  createTask: async (request: CreateTaskRequest): Promise<void> => {
    return apiClient.post<void>('/tasks', request);
  },

  // Delete a task
  deleteTask: async (taskId: number): Promise<void> => {
    return apiClient.delete<void>(`/tasks/${taskId}`);
  },
};

