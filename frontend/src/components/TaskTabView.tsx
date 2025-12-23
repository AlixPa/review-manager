import { useState, useEffect, useMemo } from 'react';
import { AlertCircle, Loader2, Trash2, CheckCircle2, Users, Code, Coins } from 'lucide-react';
import { Task, TaskState, getTaskPriorityName, TaskReviewPriority } from '../types/task';
import TaskCard from './TaskCard';
import { tasksApi } from '../api/tasks';
import { TaskLinesOfCode, getTaskLinesOfCodeDisplay } from '../types/taskLinesOfCode';

interface TabConfig {
  state: number;
  label: string;
  color: string;
  fetchFn: (state: number) => Promise<Task[]>;
}

interface TaskTabViewProps {
  tabs: TabConfig[];
  defaultTab?: number;
  isManageView?: boolean;
}

const TaskTabView = ({ tabs, defaultTab = 0, isManageView = false }: TaskTabViewProps) => {
  const [activeTabIndex, setActiveTabIndex] = useState(defaultTab);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const activeTab = tabs[activeTabIndex];

  useEffect(() => {
    fetchTasks(activeTab);
  }, [activeTabIndex]);

  const fetchTasks = async (tab: TabConfig) => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await tab.fetchFn(tab.state);
      
      // Sort by (repo, pr_number) for all tabs
      const sortedData = data.sort((a, b) => {
        // First compare by repo (nulls last)
        const repoA = a.github_repo || '\uffff'; // Use high Unicode character for nulls
        const repoB = b.github_repo || '\uffff';
        const repoCompare = repoA.localeCompare(repoB);
        if (repoCompare !== 0) return repoCompare;
        
        // Then compare by PR number (nulls last)
        const prA = a.pr_number ?? Number.MAX_SAFE_INTEGER;
        const prB = b.pr_number ?? Number.MAX_SAFE_INTEGER;
        return prA - prB;
      });
      
      setTasks(sortedData);
    } catch (err) {
      setError('Failed to fetch tasks. Please try again.');
      console.error('Error fetching tasks:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteAll = async () => {
    const count = tasks.length;
    if (count === 0) return;
    
    if (window.confirm(`Are you sure you want to delete all ${count} approved tasks? This action cannot be undone.`)) {
      setIsLoading(true);
      try {
        // Delete all tasks sequentially
        for (const task of tasks) {
          await tasksApi.deleteTask(task.task_id);
        }
        // Refresh the list after all deletions
        await fetchTasks(activeTab);
        alert(`Successfully deleted ${count} tasks.`);
      } catch (error) {
        console.error('Error deleting tasks:', error);
        alert('Failed to delete some tasks. Please try again.');
        // Refresh to show current state
        await fetchTasks(activeTab);
      }
    }
  };

  const showDeleteAllButton = isManageView && activeTab.state === TaskState.APPROVED && tasks.length > 0;

  // Calculate summary statistics for Approved tab in Manage view
  const summary = useMemo(() => {
    if (!isManageView || activeTab.state !== TaskState.APPROVED) return null;

    const totalReviews = tasks.length;

    // Count by priority
    const priorityCounts = {
      [TaskReviewPriority.FULL_REVIEW]: 0,
      [TaskReviewPriority.BASED_ON_EVIDENCE]: 0,
      [TaskReviewPriority.APPROVE_ONLY]: 0,
    };
    tasks.forEach(t => {
      priorityCounts[t.review_priority] = (priorityCounts[t.review_priority] || 0) + 1;
    });

    // Count by lines of code
    const locCounts = {
      [TaskLinesOfCode.UNDER_100]: 0,
      [TaskLinesOfCode.UNDER_500]: 0,
      [TaskLinesOfCode.UNDER_1200]: 0,
      [TaskLinesOfCode.ABOVE_1200]: 0,
    };
    tasks.forEach(t => {
      locCounts[t.lines_of_code] = (locCounts[t.lines_of_code] || 0) + 1;
    });

    // Top 5 reviewers by number of times picked
    const reviewerCounts: Record<string, { name: string; count: number }> = {};
    tasks.forEach(task => {
      task.reviewers?.forEach(reviewer => {
        if (!reviewerCounts[reviewer.public_id]) {
          reviewerCounts[reviewer.public_id] = {
            name: reviewer.user_name,
            count: 0,
          };
        }
        reviewerCounts[reviewer.public_id].count++;
      });
    });
    const topReviewers = Object.values(reviewerCounts)
      .sort((a, b) => b.count - a.count)
      .slice(0, 5);

    return {
      totalReviews,
      priorityCounts,
      locCounts,
      topReviewers,
    };
  }, [tasks, activeTab.state, isManageView]);

  return (
    <div className="flex flex-col h-full">
      {/* Tab Navigation */}
      <div className="border-b border-gray-200 bg-white px-6 py-4">
        <div className="flex gap-2">
          {tabs.map((tab, index) => (
            <button
              key={tab.state}
              onClick={() => setActiveTabIndex(index)}
              className={`flex-1 px-4 py-3 rounded-lg font-medium transition-all duration-200 border-2 cursor-pointer ${
                activeTabIndex === index
                  ? tab.color
                  : 'border-gray-200 bg-white text-gray-600 hover:bg-gray-50'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Summary Section (Approved tab in Manage view) */}
      {summary && !isLoading && !error && (
        <div className="bg-white border-b border-gray-200 px-8 py-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Summary</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Approved Requests */}
            <div className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-lg p-4 border border-blue-200">
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle2 className="w-5 h-5 text-blue-600" />
                <h3 className="font-semibold text-gray-800">Approved Requests</h3>
              </div>
              <p className="text-3xl font-bold text-blue-600 mb-3">{summary.totalReviews}</p>
              {showDeleteAllButton && (
                <button
                  onClick={handleDeleteAll}
                  className="w-full flex items-center justify-center gap-2 px-3 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg font-medium transition-colors cursor-pointer text-sm"
                >
                  <Trash2 className="w-4 h-4" />
                  Delete All
                </button>
              )}
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

            {/* Top Reviewers */}
            <div className="bg-gradient-to-br from-amber-50 to-orange-50 rounded-lg p-4 border border-amber-200">
              <div className="flex items-center gap-2 mb-2">
                <Users className="w-5 h-5 text-amber-600" />
                <h3 className="font-semibold text-gray-800">Most Picked Reviewers</h3>
              </div>
              {summary.topReviewers.length > 0 ? (
                summary.topReviewers.map((reviewer, index) => (
                  <p key={index} className="text-sm text-gray-600">
                    {index + 1}. {reviewer.name}: <span className="font-bold text-gray-800">{reviewer.count}</span>
                  </p>
                ))
              ) : (
                <p className="text-sm text-gray-500 italic">No reviewers</p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Task List Content */}
      <div className="flex-1 overflow-y-auto p-6">
        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <Loader2 className="w-8 h-8 animate-spin text-blue-600 mx-auto mb-2" />
              <p className="text-gray-600">Loading tasks...</p>
            </div>
          </div>
        ) : error ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-3" />
              <p className="text-red-600 font-medium mb-2">Error</p>
              <p className="text-gray-600">{error}</p>
              <button
                onClick={() => fetchTasks(activeTab)}
                className="mt-4 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
              >
                Retry
              </button>
            </div>
          </div>
        ) : tasks.length === 0 ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="bg-gray-100 rounded-full p-6 inline-block mb-4">
                <AlertCircle className="w-12 h-12 text-gray-400" />
              </div>
              <p className="text-gray-600 text-lg font-medium mb-1">No tasks found</p>
              <p className="text-gray-500 text-sm">
                There are no tasks with status "{activeTab.label}"
              </p>
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            {tasks.map((task, index) => (
              <TaskCard 
                key={index} 
                task={task} 
                currentState={activeTab.state} 
                isManageView={isManageView}
                onTaskUpdated={() => fetchTasks(activeTab)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default TaskTabView;

