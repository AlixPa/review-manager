import { useState, useEffect } from 'react';
import { Link2, AlertCircle, Code, Users, X } from 'lucide-react';
import Sidebar from '../components/Sidebar';
import { TaskReviewPriority, getTaskPriorityName } from '../types/task';
import { TaskLinesOfCode, getTaskLinesOfCodeDisplay } from '../types/taskLinesOfCode';
import { User } from '../types/user';
import { usersApi } from '../api/users';
import { tasksApi } from '../api/tasks';
import { useAuth } from '../contexts/AuthContext';

const CreateRequestPage = () => {
  const { user: currentUser } = useAuth();
  const [prLink, setPrLink] = useState('');
  const [priority, setPriority] = useState<number>(TaskReviewPriority.FULL_REVIEW);
  const [linesOfCode, setLinesOfCode] = useState<number>(TaskLinesOfCode.UNDER_100);
  const [reviewers, setReviewers] = useState<User[]>([]);
  const [availableUsers, setAvailableUsers] = useState<User[]>([]);
  const [isLoadingUsers, setIsLoadingUsers] = useState(true);
  const [showPrLinkError, setShowPrLinkError] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [allowSingleReviewer, setAllowSingleReviewer] = useState(false);

  const priorityOptions = [
    {
      value: TaskReviewPriority.FULL_REVIEW,
      name: getTaskPriorityName(TaskReviewPriority.FULL_REVIEW),
      description: 'Complete code review with detailed feedback',
    },
    {
      value: TaskReviewPriority.BASED_ON_EVIDENCE,
      name: getTaskPriorityName(TaskReviewPriority.BASED_ON_EVIDENCE),
      description: 'Review based on test results and evidence',
    },
    {
      value: TaskReviewPriority.APPROVE_ONLY,
      name: getTaskPriorityName(TaskReviewPriority.APPROVE_ONLY),
      description: 'Quick approval, minimal review needed',
    },
  ];

  const linesOfCodeOptions = [
    { value: TaskLinesOfCode.UNDER_100, display: getTaskLinesOfCodeDisplay(TaskLinesOfCode.UNDER_100) },
    { value: TaskLinesOfCode.UNDER_500, display: getTaskLinesOfCodeDisplay(TaskLinesOfCode.UNDER_500) },
    { value: TaskLinesOfCode.UNDER_1200, display: getTaskLinesOfCodeDisplay(TaskLinesOfCode.UNDER_1200) },
    { value: TaskLinesOfCode.ABOVE_1200, display: getTaskLinesOfCodeDisplay(TaskLinesOfCode.ABOVE_1200) },
  ];

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const users = await usersApi.getUsers();
        // Sort users alphabetically by user_name
        const sortedUsers = users.sort((a, b) => a.user_name.localeCompare(b.user_name));
        setAvailableUsers(sortedUsers);
      } catch (error) {
        console.error('Error fetching users:', error);
      } finally {
        setIsLoadingUsers(false);
      }
    };
    fetchUsers();
  }, []);

  const handleAddReviewer = (userId: string) => {
    if (userId) {
      const user = availableUsers.find(u => u.public_id === userId);
      if (user && !reviewers.some(r => r.public_id === user.public_id)) {
        setReviewers([...reviewers, user]);
        // Reset the checkbox when adding reviewers
        if (allowSingleReviewer && reviewers.length === 0) {
          setAllowSingleReviewer(false);
        }
      }
    }
  };

  const handleRemoveReviewer = (userId: string) => {
    setReviewers(reviewers.filter(r => r.public_id !== userId));
  };

  const availableUsersToAdd = availableUsers.filter(
    user => user.public_id !== currentUser?.public_id && !reviewers.some(r => r.public_id === user.public_id)
  );

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate PR link
    if (prLink.trim() === '') {
      setShowPrLinkError(true);
      window.scrollTo({ top: 0, behavior: 'smooth' });
      return;
    }
    
    // Validate reviewers
    if (reviewers.length === 0) {
      alert('Please add at least one reviewer');
      return;
    }
    
    setIsSubmitting(true);
    setSubmitError(null);
    
    try {
      await tasksApi.createTask({
        pr_link: prLink,
        priority: priority,
        lines_of_code: linesOfCode,
        reviewers_id: reviewers.map(r => r.public_id),
      });
      
      // Success! Redirect to manage page
      alert('Review request created successfully!');
      window.location.href = '/manage';
    } catch (error) {
      console.error('Error creating task:', error);
      const errorMessage = error instanceof Error ? error.message : 'Failed to create review request';
      setSubmitError(errorMessage);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handlePrLinkChange = (value: string) => {
    setPrLink(value);
    if (showPrLinkError && value.trim() !== '') {
      setShowPrLinkError(false);
    }
  };

  const handleReset = () => {
    setPrLink('');
    setPriority(TaskReviewPriority.FULL_REVIEW);
    setLinesOfCode(TaskLinesOfCode.UNDER_100);
    setReviewers([]);
    setShowPrLinkError(false);
    setSubmitError(null);
    setAllowSingleReviewer(false);
  };

  const canSubmit = reviewers.length >= 2 || (reviewers.length === 1 && allowSingleReviewer);
  const showSingleReviewerWarning = reviewers.length === 1;

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <main className="flex-1 overflow-y-auto">
        <div className="bg-white border-b border-gray-200 px-8 py-6">
          <h1 className="text-3xl font-bold text-gray-800">Create new request</h1>
          <p className="text-gray-600 mt-1">Submit a new code review request to your team</p>
        </div>

        <div className="p-8">
          {/* Error Banner */}
          {submitError && (
            <div className="mb-6 p-4 bg-red-50 border-2 border-red-300 rounded-lg">
              <p className="text-red-600 font-medium">⚠️ {submitError}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* PR Link */}
            <div className={`bg-white rounded-lg border-2 p-6 transition-colors ${
              showPrLinkError ? 'border-red-300 bg-red-50' : 'border-gray-200'
            }`}>
              <div className="flex items-center gap-3 mb-4">
                <div className="bg-blue-100 p-2 rounded-lg">
                  <Link2 className="w-5 h-5 text-blue-600" />
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-800">
                    Pull Request Link
                    <span className="text-red-500 ml-1">*</span>
                  </h3>
                  <p className="text-sm text-gray-500">GitHub PR URL to review</p>
                </div>
              </div>
              <input
                type="url"
                value={prLink}
                onChange={(e) => handlePrLinkChange(e.target.value)}
                placeholder="https://github.com/owner/repo/pull/123"
                className={`w-full px-4 py-3 border-2 rounded-lg focus:outline-none transition-colors ${
                  showPrLinkError
                    ? 'border-red-500 focus:border-red-600 bg-white'
                    : 'border-gray-300 focus:border-blue-500'
                }`}
              />
              {showPrLinkError && (
                <p className="mt-2 text-sm text-red-600 font-medium">
                  ⚠️ Please add a PR link to continue
                </p>
              )}
            </div>

            {/* Priority Selection */}
            <div className="bg-white rounded-lg border-2 border-gray-200 p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="bg-purple-100 p-2 rounded-lg">
                  <AlertCircle className="w-5 h-5 text-purple-600" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-800">Review Priority</h3>
                  <p className="text-sm text-gray-500">Type of review needed</p>
                </div>
              </div>
              <div className="space-y-3">
                {priorityOptions.map((option) => (
                  <label
                    key={option.value}
                    className={`flex items-start gap-4 p-4 rounded-lg border-2 cursor-pointer transition-all ${
                      priority === option.value
                        ? 'border-purple-500 bg-purple-50'
                        : 'border-gray-200 hover:border-purple-300 hover:bg-gray-50'
                    }`}
                  >
                    <input
                      type="radio"
                      name="priority"
                      value={option.value}
                      checked={priority === option.value}
                      onChange={(e) => setPriority(Number(e.target.value))}
                      className="mt-1 w-4 h-4 text-purple-600 cursor-pointer"
                    />
                    <div className="flex-1">
                      <div className="font-semibold text-gray-800">{option.name}</div>
                      <div className="text-sm text-gray-600">{option.description}</div>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            {/* Lines of Code */}
            <div className="bg-white rounded-lg border-2 border-gray-200 p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="bg-green-100 p-2 rounded-lg">
                  <Code className="w-5 h-5 text-green-600" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-800">Lines of Code</h3>
                  <p className="text-sm text-gray-500">Approximate size of the changes</p>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                {linesOfCodeOptions.map((option) => {
                  const isDisabled = priority === TaskReviewPriority.FULL_REVIEW && option.value === TaskLinesOfCode.ABOVE_1200;
                  return (
                    <label
                      key={option.value}
                      className={`flex items-center justify-center gap-2 p-4 rounded-lg border-2 transition-all font-semibold ${
                        isDisabled
                          ? 'border-gray-300 bg-gray-100 text-gray-400 cursor-not-allowed'
                          : linesOfCode === option.value
                          ? 'border-green-500 bg-green-50 text-green-700 cursor-pointer'
                          : 'border-gray-200 hover:border-green-300 hover:bg-gray-50 text-gray-700 cursor-pointer'
                      }`}
                    >
                      <input
                        type="radio"
                        name="linesOfCode"
                        value={option.value}
                        checked={linesOfCode === option.value}
                        onChange={(e) => setLinesOfCode(Number(e.target.value))}
                        disabled={isDisabled}
                        className="sr-only"
                      />
                      {isDisabled ? 'split the pr 🙏' : option.display}
                    </label>
                  );
                })}
              </div>
            </div>

            {/* Reviewers */}
            <div className="bg-white rounded-lg border-2 border-gray-200 p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="bg-amber-100 p-2 rounded-lg">
                  <Users className="w-5 h-5 text-amber-600" />
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-800">
                    Reviewers
                    <span className="text-red-500 ml-1">*</span>
                  </h3>
                  <p className="text-sm text-gray-500">Team members who will review this PR</p>
                </div>
              </div>

              {/* Add Reviewer Selector */}
              <div className="mb-4">
                {isLoadingUsers ? (
                  <div className="px-4 py-2 text-gray-500">Loading users...</div>
                ) : (
                  <select
                    value=""
                    onChange={(e) => handleAddReviewer(e.target.value)}
                    className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-amber-500 focus:outline-none transition-colors cursor-pointer"
                    disabled={availableUsersToAdd.length === 0}
                  >
                    <option value="">
                      {availableUsersToAdd.length > 0 ? 'add reviewers' : 'All users added'}
                    </option>
                    {availableUsersToAdd.map((user) => (
                      <option key={user.public_id} value={user.public_id}>
                        {user.user_name} • time spent this cycle: {user.reward_since_last_tuesday} minutes
                      </option>
                    ))}
                  </select>
                )}
              </div>

              {/* Reviewers List */}
              {reviewers.length > 0 ? (
                <>
                  <div className="space-y-2">
                    {reviewers.map((reviewer) => (
                      <div
                        key={reviewer.public_id}
                        className="flex items-center justify-between p-3 bg-amber-50 border border-amber-200 rounded-lg"
                      >
                        <div className="flex-1">
                          <span className="font-medium text-gray-800">{reviewer.user_name}</span>
                          <span className="text-xs text-gray-600 ml-2">
                            • time spent this cycle: {reviewer.reward_since_last_tuesday} minutes
                          </span>
                        </div>
                        <button
                          type="button"
                          onClick={() => handleRemoveReviewer(reviewer.public_id)}
                          className="p-1 hover:bg-amber-200 rounded transition-colors cursor-pointer"
                        >
                          <X className="w-4 h-4 text-amber-700" />
                        </button>
                      </div>
                    ))}
                  </div>
                  
                  {/* Single Reviewer Warning */}
                  {showSingleReviewerWarning && (
                    <div className="mt-4 p-4 bg-orange-50 border-2 border-orange-300 rounded-lg">
                      <p className="text-orange-700 font-medium mb-3">
                        ⚠️ It is recommended to select at least two reviewers
                      </p>
                      <label className="flex items-start gap-3 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={allowSingleReviewer}
                          onChange={(e) => setAllowSingleReviewer(e.target.checked)}
                          className="mt-1 w-4 h-4 text-orange-600 cursor-pointer"
                        />
                        <span className="text-sm text-orange-700 font-medium">
                          Continue with a single reviewer
                        </span>
                      </label>
                    </div>
                  )}
                </>
              ) : (
                <div className="text-center py-8 bg-red-50 rounded-lg border-2 border-dashed border-red-300">
                  <p className="text-red-600 font-medium">⚠️ At least one reviewer is required</p>
                  <p className="text-red-500 text-sm mt-1">Please add a reviewer to continue</p>
                </div>
              )}
            </div>

            {/* Submit Button */}
            <div className="flex gap-4">
              <button
                type="submit"
                disabled={!canSubmit || isSubmitting}
                style={{ flex: '5' }}
                className={`py-4 rounded-lg font-semibold transition-colors shadow-md ${
                  canSubmit && !isSubmitting
                    ? 'bg-blue-500 hover:bg-blue-600 text-white hover:shadow-lg cursor-pointer'
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }`}
              >
                {isSubmitting ? 'Creating...' : 'Create Review Request'}
              </button>
              <button
                type="button"
                onClick={handleReset}
                disabled={isSubmitting}
                style={{ flex: '1' }}
                className={`py-4 rounded-lg font-semibold transition-colors cursor-pointer ${
                  isSubmitting
                    ? 'bg-gray-200 text-gray-400'
                    : 'bg-gray-200 hover:bg-gray-300 text-gray-700'
                }`}
              >
                Reset
              </button>
            </div>
          </form>
        </div>
      </main>
    </div>
  );
};

export default CreateRequestPage;

