// Task state enum matching backend
export enum TaskState {
  PENDING_REVIEW = 1,
  PENDING_CHANGES = 2,
  APPROVED = 3,
}

// Task review priority enum matching backend
export enum TaskReviewPriority {
  FULL_REVIEW = 1,
  BASED_ON_EVIDENCE = 2,
  APPROVE_ONLY = 3,
}

// Reviewer interface matching backend response
export interface Reviewer {
  public_id: string;
  user_name: string;
}

// Task interface matching backend response
export interface Task {
  task_id: number;
  github_repo: string | null;
  pr_number: number | null;
  creator_user_name: string;
  creator_public_id: string;
  review_priority: number;
  lines_of_code: number;
  created_at: string;
  approved_at: string | null;
  state: number;
  reward: number;
  has_been_reviewed_once: boolean;
  pr_link: string;
  reviewers: Reviewer[]; // Now returned by both /todo and /my_tasks endpoints
}

// Helper functions for display
export const getTaskStateName = (state: number): string => {
  switch (state) {
    case TaskState.PENDING_REVIEW:
      return 'Pending Review';
    case TaskState.PENDING_CHANGES:
      return 'Pending Changes';
    case TaskState.APPROVED:
      return 'Approved';
    default:
      return 'Unknown';
  }
};

export const getTaskPriorityName = (priority: number): string => {
  switch (priority) {
    case TaskReviewPriority.FULL_REVIEW:
      return 'Full Review';
    case TaskReviewPriority.BASED_ON_EVIDENCE:
      return 'Based on Evidence';
    case TaskReviewPriority.APPROVE_ONLY:
      return 'Approve Only';
    default:
      return 'Unknown';
  }
};

