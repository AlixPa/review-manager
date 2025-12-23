import { Clock, Coins, ExternalLink, CheckCircle2, Code, X, Trash2, Users, RotateCcw } from 'lucide-react';
import { Task, getTaskPriorityName, TaskState } from '../types/task';
import { tasksApi } from '../api/tasks';
import { UpdateAction } from '../types/updateAction';
import { getTaskLinesOfCodeDisplay } from '../types/taskLinesOfCode';
import UserBadge from './UserBadge';

interface TaskCardProps {
  task: Task;
  currentState?: number;
  isManageView?: boolean;
  onTaskUpdated?: () => void;
}

const TaskCard = ({ task, currentState, isManageView = false, onTaskUpdated }: TaskCardProps) => {
  const showReward = currentState === TaskState.PENDING_REVIEW;
  // Show reviewers whenever the data is available
  const showReviewers = task.reviewers && task.reviewers.length > 0;
  // Show Done button only in "My tasks" view for Pending Review and Pending Changes
  const showDoneButton = !isManageView && (currentState === TaskState.PENDING_REVIEW || currentState === TaskState.PENDING_CHANGES);
  
  // Calculate number of items in first row for dynamic grid layout
  const firstRowItemCount = 5 + (showReward ? 1 : 0); // Base: Repo, PR#, Created by, Priority, Lines of Code (5) + optional reward
  const gridColsClass = firstRowItemCount === 5 ? 'grid-cols-5' : 'grid-cols-6';

  const handleApprove = async () => {
    if (window.confirm('Confirm that you want to approve this review?')) {
      try {
        await tasksApi.updateTask(task.task_id, UpdateAction.APPROVE);
        onTaskUpdated?.();
      } catch (error) {
        console.error('Error approving task:', error);
        alert('Failed to approve task. Please try again.');
      }
    }
  };

  const handleRequestChanges = async () => {
    if (window.confirm('Confirm that you want to request changes for this review?')) {
      try {
        await tasksApi.updateTask(task.task_id, UpdateAction.REQUEST_CHANGES);
        onTaskUpdated?.();
      } catch (error) {
        console.error('Error requesting changes:', error);
        alert('Failed to request changes. Please try again.');
      }
    }
  };

  const handleChangesAddressed = async () => {
    if (window.confirm('Confirm that you want to mark the changes as addressed?')) {
      try {
        await tasksApi.updateTask(task.task_id, UpdateAction.CHANGES_ADDRESSED);
        onTaskUpdated?.();
      } catch (error) {
        console.error('Error marking changes as addressed:', error);
        alert('Failed to mark changes as addressed. Please try again.');
      }
    }
  };

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this review request? This action cannot be undone.')) {
      try {
        await tasksApi.deleteTask(task.task_id);
        onTaskUpdated?.();
      } catch (error) {
        console.error('Error deleting task:', error);
        alert('Failed to delete task. Please try again.');
      }
    }
  };

  const handleReopenQuick = async () => {
    if (window.confirm('Re-open for Quick Review?\n\nThis will just require a quick check again.')) {
      try {
        await tasksApi.updateTask(task.task_id, UpdateAction.RE_OPEN_QUICK_REVIEW);
        onTaskUpdated?.();
      } catch (error) {
        console.error('Error reopening task:', error);
        alert('Failed to reopen task. Please try again.');
      }
    }
  };

  const handleReopenReset = async () => {
    if (window.confirm('Re-open with Reset?\n\nThis will require a review as if it was the first time.')) {
      try {
        await tasksApi.updateTask(task.task_id, UpdateAction.RE_OPEN_RESET_REVIEW);
        onTaskUpdated?.();
      } catch (error) {
        console.error('Error reopening task:', error);
        alert('Failed to reopen task. Please try again.');
      }
    }
  };

  const showDeleteButton = isManageView && (currentState === TaskState.PENDING_REVIEW || currentState === TaskState.APPROVED);
  const showReopenButtons = isManageView && currentState === TaskState.APPROVED;
  
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
        {/* Line 1: Repo | PR# | Created by | Reward (conditional) | Review Priority | Lines of Code */}
        <div className={`grid ${gridColsClass} gap-4 mb-4`}>
          <div className="flex flex-col items-center justify-center">
            <p className="text-xs text-gray-500">Repository</p>
            <p className="font-semibold text-gray-800 text-center text-sm">
              {task.github_repo || 'unknown'}
            </p>
          </div>

          <div className="flex flex-col items-center justify-center">
            <p className="text-xs text-gray-500">PR Number</p>
            <p className="font-semibold text-gray-800">
              {task.pr_number ? `#${task.pr_number}` : 'unknown'}
            </p>
          </div>

          <div className="flex items-center gap-2 justify-center">
            <UserBadge
              publicId={task.creator_public_id}
              userName={task.creator_user_name}
              variant="full"
            />
          </div>

          {showReward && (
            <div className="flex items-center gap-2 justify-center">
              <Coins className="w-5 h-5 text-amber-500" />
              <div>
                <p className="text-xs text-gray-500">Reward</p>
                <div className="flex items-center gap-2">
                  <p className="font-bold text-amber-600">{task.reward}</p>
                  {task.has_been_reviewed_once && (
                    <span className="text-[10px] bg-cyan-100 text-cyan-700 px-1.5 py-0.5 rounded font-semibold">
                      Quick review
                    </span>
                  )}
                </div>
              </div>
            </div>
          )}

          <div className="flex flex-col items-center justify-center">
            <p className="text-xs text-gray-500">Review Priority</p>
            <p className="font-semibold text-gray-800">{getTaskPriorityName(task.review_priority)}</p>
          </div>

          <div className="flex items-center gap-2 justify-center">
            <Code className="w-5 h-5 text-gray-500" />
            <div>
              <p className="text-xs text-gray-500">Lines of code</p>
              <p className="font-semibold text-gray-800">
                {getTaskLinesOfCodeDisplay(task.lines_of_code)}
              </p>
            </div>
          </div>
        </div>

        {/* Reviewers Row (shown when data is available from /my_tasks endpoint) */}
        {showReviewers && (
          <div className="mb-4 pb-4 border-b border-gray-200">
            <div className="flex items-start gap-2">
              <Users className="w-5 h-5 text-gray-500 mt-0.5" />
              <div className="flex-1">
                <p className="text-xs text-gray-500 mb-1">Reviewers</p>
                <div className="flex flex-wrap gap-2">
                  {task.reviewers!.map((reviewer) => (
                    <UserBadge
                      key={reviewer.public_id}
                      publicId={reviewer.public_id}
                      userName={reviewer.user_name}
                      variant="pill"
                    />
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Line 2: Created at | Approved at */}
        <div className="flex items-center gap-6 mb-4 pb-4 border-b border-gray-200">
          <div className="flex items-center gap-2 text-sm">
            <Clock className="w-4 h-4 text-gray-500" />
            <div>
              <span className="text-gray-500">Created: </span>
              <span className="font-medium text-gray-800">{formatDate(task.created_at)}</span>
            </div>
          </div>

          <div className="flex items-center gap-2 text-sm">
            <CheckCircle2 className="w-4 h-4 text-gray-500" />
            <div>
              <span className="text-gray-500">Approved: </span>
              {task.approved_at ? (
                <span className="font-medium text-gray-800">{formatDate(task.approved_at)}</span>
              ) : (
                <span className="font-medium text-orange-600">Pending</span>
              )}
            </div>
          </div>
        </div>

        {/* Line 3: View PR Button | Delete Button (conditional) | Reopen Buttons (conditional) | Action Buttons (conditional) */}
        <div className="flex gap-3">
          <a
            href={task.pr_link}
            target="_blank"
            rel="noopener noreferrer"
            style={showReopenButtons ? { flex: '3' } : { flex: '5' }}
            className="flex items-center justify-center gap-2 px-4 py-2.5 bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-medium transition-colors duration-200 cursor-pointer"
          >
            <ExternalLink className="w-4 h-4" />
            View Pull Request
          </a>
          {showReopenButtons && (
            <>
              <button
                onClick={handleReopenQuick}
                style={{ flex: '1' }}
                className="flex items-center justify-center gap-2 py-2.5 bg-cyan-500 hover:bg-cyan-600 text-white rounded-lg font-medium transition-colors duration-200 cursor-pointer"
              >
                <RotateCcw className="w-4 h-4" />
                Re Open (Quick)
              </button>
              <button
                onClick={handleReopenReset}
                style={{ flex: '1' }}
                className="flex items-center justify-center gap-2 py-2.5 bg-orange-500 hover:bg-orange-600 text-white rounded-lg font-medium transition-colors duration-200 cursor-pointer"
              >
                <RotateCcw className="w-4 h-4" />
                Re Open (Reset)
              </button>
            </>
          )}
          {showDeleteButton && (
            <button
              onClick={handleDelete}
              style={{ flex: '1' }}
              className="flex items-center justify-center gap-2 py-2.5 bg-red-500 hover:bg-red-600 text-white rounded-lg font-medium transition-colors duration-200 cursor-pointer"
            >
              <Trash2 className="w-4 h-4" />
              Delete
            </button>
          )}
          {showDoneButton && currentState === TaskState.PENDING_CHANGES && (
            <button
              onClick={handleChangesAddressed}
              className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-green-500 hover:bg-green-600 text-white rounded-lg font-medium transition-colors duration-200 cursor-pointer"
            >
              <CheckCircle2 className="w-4 h-4" />
              Changes Addressed
            </button>
          )}
          {showDoneButton && currentState === TaskState.PENDING_REVIEW && (
            <>
              <button
                onClick={handleApprove}
                className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-green-500 hover:bg-green-600 text-white rounded-lg font-medium transition-colors duration-200 cursor-pointer"
              >
                <CheckCircle2 className="w-4 h-4" />
                Approved
              </button>
              <button
                onClick={handleRequestChanges}
                className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-orange-500 hover:bg-orange-600 text-white rounded-lg font-medium transition-colors duration-200 cursor-pointer"
              >
                <X className="w-4 h-4" />
                Requested Changes
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default TaskCard;

