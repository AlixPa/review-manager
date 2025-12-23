export interface Reward {
  creator_public_id: string;
  creator_user_name: string;
  lines_of_code: number;
  review_priority: number;
  pr_link: string;
  pr_number: number | null;
  repo: string | null;
  points: number;
  was_quick_review: boolean;
  rewarded_at: string; // datetime string
}

