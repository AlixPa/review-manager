import { Clock, Code, ExternalLink, Coins, CheckCircle2 } from 'lucide-react';
import { Reward } from '../types/reward';
import { getTaskPriorityName } from '../types/task';
import { getTaskLinesOfCodeDisplay } from '../types/taskLinesOfCode';
import UserBadge from './UserBadge';

interface RewardCardProps {
  reward: Reward;
}

const RewardCard = ({ reward }: RewardCardProps) => {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  };

  return (
    <div className="bg-white rounded-xl border border-gray-300 shadow-sm hover:shadow-lg transition-all duration-200 hover:border-blue-400 overflow-hidden">
      <div className="p-5">
        {/* Line 1: Repo | PR# | Created by | Points | Review Priority | Lines of Code */}
        <div className="grid grid-cols-6 gap-4 mb-4">
          <div className="flex flex-col items-center justify-center">
            <p className="text-xs text-gray-500">Repository</p>
            <p className="font-semibold text-gray-800 text-center text-sm">
              {reward.repo || 'unknown'}
            </p>
          </div>

          <div className="flex flex-col items-center justify-center">
            <p className="text-xs text-gray-500">PR Number</p>
            <p className="font-semibold text-gray-800">
              {reward.pr_number ? `#${reward.pr_number}` : 'unknown'}
            </p>
          </div>

          <div className="flex items-center gap-2 justify-center">
            <UserBadge
              publicId={reward.creator_public_id}
              userName={reward.creator_user_name}
              variant="full"
            />
          </div>

          <div className="flex items-center gap-2 justify-center">
            <Coins className="w-5 h-5 text-green-500" />
            <div>
              <p className="text-xs text-gray-500">Points</p>
              <div className="flex items-center gap-2">
                <p className="font-bold text-green-600">{reward.points}</p>
                {reward.was_quick_review && (
                  <span className="text-[10px] bg-cyan-100 text-cyan-700 px-1.5 py-0.5 rounded font-semibold">
                    Quick review
                  </span>
                )}
              </div>
            </div>
          </div>

          <div className="flex flex-col items-center justify-center">
            <p className="text-xs text-gray-500">Review Priority</p>
            <p className="font-semibold text-gray-800">{getTaskPriorityName(reward.review_priority)}</p>
          </div>

          <div className="flex items-center gap-2 justify-center">
            <Code className="w-5 h-5 text-gray-500" />
            <div>
              <p className="text-xs text-gray-500">Lines of code</p>
              <p className="font-semibold text-gray-800">
                {getTaskLinesOfCodeDisplay(reward.lines_of_code)}
              </p>
            </div>
          </div>
        </div>

        {/* Line 2: Rewarded at */}
        <div className="flex items-center gap-6 mb-4 pb-4 border-b border-gray-200">
          <div className="flex items-center gap-2 text-sm">
            <Clock className="w-4 h-4 text-gray-500" />
            <div>
              <span className="text-gray-500">Rewarded: </span>
              <span className="font-medium text-gray-800">{formatDate(reward.rewarded_at)}</span>
            </div>
          </div>
        </div>

        {/* Line 3: View PR Button */}
        <div className="flex gap-3">
          <a
            href={reward.pr_link}
            target="_blank"
            rel="noopener noreferrer"
            className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-medium transition-colors duration-200 cursor-pointer"
          >
            <ExternalLink className="w-4 h-4" />
            View Pull Request
          </a>
        </div>
      </div>
    </div>
  );
};

export default RewardCard;

