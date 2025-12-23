import Sidebar from '../components/Sidebar';
import ManageRequestsList from '../components/ManageRequestsList';

const ManageRequestsPage = () => {
  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <main className="flex-1 flex flex-col overflow-hidden">
        <div className="bg-white border-b border-gray-200 px-8 py-6">
          <h1 className="text-3xl font-bold text-gray-800">Manage my requests</h1>
          <p className="text-gray-600 mt-1">Track and manage all review requests you have created</p>
        </div>
        <ManageRequestsList />
      </main>
    </div>
  );
};

export default ManageRequestsPage;

