import { tasksApi } from '../api/tasks';
import { TaskState } from '../types/task';
import TaskTabView from './TaskTabView';

const TaskList = () => {
  const tabs = [
    {
      state: TaskState.PENDING_REVIEW,
      label: 'Pending Review',
      color: 'border-blue-500 bg-blue-50 text-blue-700',
      fetchFn: tasksApi.getAssignedTasks,
    },
    {
      state: TaskState.PENDING_CHANGES,
      label: 'Pending Changes',
      color: 'border-yellow-500 bg-yellow-50 text-yellow-700',
      fetchFn: tasksApi.getMyTasks,
    },
  ];

  return <TaskTabView tabs={tabs} defaultTab={0} />;
};

export default TaskList;

