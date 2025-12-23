import { useState, useEffect, useMemo } from 'react';
import Sidebar from '../components/Sidebar';
import RewardCard from '../components/RewardCard';
import { rewardsApi } from '../api/rewards';
import { Reward } from '../types/reward';
import { Loader2, AlertCircle, Inbox, CheckCircle2, Users, Code, Coins } from 'lucide-react';
import { TaskReviewPriority, getTaskPriorityName } from '../types/task';
import { TaskLinesOfCode, getTaskLinesOfCodeDisplay } from '../types/taskLinesOfCode';

const RewardsPage = () => {
  const [cycleOffset, setCycleOffset] = useState(0);
  const [rewards, setRewards] = useState<Reward[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchRewards = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await rewardsApi.getRewards(cycleOffset);
      // Sort by (repo, pr_number)
      const sortedData = data.sort((a, b) => {
        // First compare by repo (nulls last)
        const repoA = a.repo || '\uffff'; // Use high Unicode character for nulls
        const repoB = b.repo || '\uffff';
        const repoCompare = repoA.localeCompare(repoB);
        if (repoCompare !== 0) return repoCompare;
        
        // Then compare by PR number (nulls last)
        const prA = a.pr_number ?? Number.MAX_SAFE_INTEGER;
        const prB = b.pr_number ?? Number.MAX_SAFE_INTEGER;
        return prA - prB;
      });
      setRewards(sortedData);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch rewards.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchRewards();
  }, [cycleOffset]);

  const cycleOptions = [
    { value: 0, label: 'Current Cycle' },
    { value: 1, label: 'Previous Cycle' },
    { value: 2, label: '2 Cycles Ago' },
    { value: 3, label: '3 Cycles Ago' },
    { value: 4, label: '4 Cycles Ago' },
  ];

  // Calculate summary statistics
  const summary = useMemo(() => {
    const firstReviews = rewards.filter(r => !r.was_quick_review).length;
    const quickReviews = rewards.filter(r => r.was_quick_review).length;
    const totalReward = rewards.reduce((sum, r) => sum + r.points, 0);

    // Count by priority
    const priorityCounts = {
      [TaskReviewPriority.FULL_REVIEW]: 0,
      [TaskReviewPriority.BASED_ON_EVIDENCE]: 0,
      [TaskReviewPriority.APPROVE_ONLY]: 0,
    };
    rewards.forEach(r => {
      priorityCounts[r.review_priority] = (priorityCounts[r.review_priority] || 0) + 1;
    });

    // Count by lines of code
    const locCounts = {
      [TaskLinesOfCode.UNDER_100]: 0,
      [TaskLinesOfCode.UNDER_500]: 0,
      [TaskLinesOfCode.UNDER_1200]: 0,
      [TaskLinesOfCode.ABOVE_1200]: 0,
    };
    rewards.forEach(r => {
      locCounts[r.lines_of_code] = (locCounts[r.lines_of_code] || 0) + 1;
    });

    // Top 5 creators by number of reviews
    const creatorCounts: Record<string, { name: string; count: number }> = {};
    rewards.forEach(r => {
      if (!creatorCounts[r.creator_public_id]) {
        creatorCounts[r.creator_public_id] = {
          name: r.creator_user_name,
          count: 0,
        };
      }
      creatorCounts[r.creator_public_id].count++;
    });
    const topCreators = Object.values(creatorCounts)
      .sort((a, b) => b.count - a.count)
      .slice(0, 5);

    return {
      firstReviews,
      quickReviews,
      totalReward,
      priorityCounts,
      locCounts,
      topCreators,
    };
  }, [rewards]);

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <main className="flex-1 flex flex-col overflow-hidden">
        <div className="bg-white border-b border-gray-200 px-8 py-6">
          <h1 className="text-3xl font-bold text-gray-800">Rewards</h1>
          <p className="text-gray-600 mt-1">View your earned rewards by cycle</p>
        </div>

        {/* Cycle Selector */}
        <div className="bg-white border-b border-gray-200 px-8 py-4">
          <div className="flex items-center gap-4">
            <label htmlFor="cycle-selector" className="text-sm font-medium text-gray-700">
              Select Cycle:
            </label>
            <select
              id="cycle-selector"
              value={cycleOffset}
              onChange={(e) => setCycleOffset(Number(e.target.value))}
              className="px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none transition-colors cursor-pointer"
            >
              {cycleOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Cycle Summary */}
        {!isLoading && !error && (
          <div className="bg-white border-b border-gray-200 px-8 py-6">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">Cycle Summary</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Reviews & Total Reward */}
              <div className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-lg p-4 border border-blue-200">
                <div className="flex items-center gap-2 mb-2">
                  <CheckCircle2 className="w-5 h-5 text-blue-600" />
                  <h3 className="font-semibold text-gray-800">Reviews Done</h3>
                </div>
                <p className="text-sm text-gray-600 mb-1">
                  First reviews: <span className="font-bold text-gray-800">{summary.firstReviews}</span>
                </p>
                <p className="text-sm text-gray-600 mb-2">
                  Quick reviews: <span className="font-bold text-gray-800">{summary.quickReviews}</span>
                </p>
                <div className="flex items-center gap-1 mt-3 pt-3 border-t border-blue-200">
                  <Coins className="w-4 h-4 text-amber-600" />
                  <p className="text-sm text-gray-600">
                    Total: <span className="font-bold text-amber-600 text-lg">{summary.totalReward}</span>
                  </p>
                </div>
              </div>

              {/* By Priority */}
              <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-lg p-4 border border-purple-200">
                <div className="flex items-center gap-2 mb-2">
                  <CheckCircle2 className="w-5 h-5 text-purple-600" />
                  <h3 className="font-semibold text-gray-800">By Priority</h3>
                </div>
                {Object.entries(summary.priorityCounts).map(([priority, count]) => (
                  <p key={priority} className="text-sm text-gray-600">
                    {getTaskPriorityName(Number(priority))}: <span className="font-bold text-gray-800">{count}</span>
                  </p>
                ))}
              </div>

              {/* By Lines of Code */}
              <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-lg p-4 border border-green-200">
                <div className="flex items-center gap-2 mb-2">
                  <Code className="w-5 h-5 text-green-600" />
                  <h3 className="font-semibold text-gray-800">By Lines of Code</h3>
                </div>
                {Object.entries(summary.locCounts).map(([loc, count]) => (
                  <p key={loc} className="text-sm text-gray-600">
                    {getTaskLinesOfCodeDisplay(Number(loc))}: <span className="font-bold text-gray-800">{count}</span>
                  </p>
                ))}
              </div>

              {/* Top Creators */}
              <div className="bg-gradient-to-br from-amber-50 to-orange-50 rounded-lg p-4 border border-amber-200">
                <div className="flex items-center gap-2 mb-2">
                  <Users className="w-5 h-5 text-amber-600" />
                  <h3 className="font-semibold text-gray-800">Top 5 Creators</h3>
                </div>
                {summary.topCreators.length > 0 ? (
                  summary.topCreators.map((creator, index) => (
                    <p key={index} className="text-sm text-gray-600">
                      {index + 1}. {creator.name}: <span className="font-bold text-gray-800">{creator.count}</span>
                    </p>
                  ))
                ) : (
                  <p className="text-sm text-gray-500 italic">No reviews yet</p>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Rewards List */}
        <div className="flex-1 overflow-y-auto p-6">
          {isLoading ? (
            <div className="flex items-center justify-center h-64">
              <div className="text-center">
                <Loader2 className="w-8 h-8 animate-spin text-blue-600 mx-auto mb-2" />
                <p className="text-gray-600">Loading rewards...</p>
              </div>
            </div>
          ) : error ? (
            <div className="flex items-center justify-center h-64">
              <div className="text-center">
                <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-3" />
                <p className="text-red-600 font-medium mb-2">Error</p>
                <p className="text-gray-600 mb-4">{error}</p>
                <button
                  onClick={fetchRewards}
                  className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors cursor-pointer"
                >
                  Retry
                </button>
              </div>
            </div>
          ) : rewards.length === 0 ? (
            <div className="flex items-center justify-center h-64">
              <div className="text-center">
                <div className="bg-gray-100 rounded-full p-6 inline-block mb-4">
                  <Inbox className="w-12 h-12 text-gray-400" />
                </div>
                <p className="text-gray-600 text-lg font-medium mb-1">No rewards found</p>
                <p className="text-gray-500 text-sm">
                  You haven't earned any rewards in this cycle yet
                </p>
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              {rewards.map((reward, index) => (
                <RewardCard key={index} reward={reward} />
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default RewardsPage;

