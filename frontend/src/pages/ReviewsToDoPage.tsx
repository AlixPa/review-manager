import Sidebar from '../components/Sidebar';
import TaskList from '../components/TaskList';

const ReviewsToDoPage = () => {
  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <main className="flex-1 flex flex-col overflow-hidden">
        <div className="bg-white border-b border-gray-200 px-8 py-6">
          <h1 className="text-3xl font-bold text-gray-800">My todo</h1>
          <p className="text-gray-600 mt-1">View reviews to do and pending changes</p>
        </div>
        <TaskList />
      </main>
    </div>
  );
};

export default ReviewsToDoPage;

