import { tasksApi } from '../api/tasks';
import { TaskState } from '../types/task';
import TaskTabView from './TaskTabView';

const ManageRequestsList = () => {
  const tabs = [
    {
      state: TaskState.PENDING_REVIEW,
      label: 'Pending Reviews',
      color: 'border-blue-500 bg-blue-50 text-blue-700',
      fetchFn: tasksApi.getMyTasks,
    },
    {
      state: TaskState.APPROVED,
      label: 'Approved',
      color: 'border-green-500 bg-green-50 text-green-700',
      fetchFn: tasksApi.getMyTasks,
    },
  ];

  return <TaskTabView tabs={tabs} defaultTab={0} isManageView={true} />;
};

export default ManageRequestsList;

