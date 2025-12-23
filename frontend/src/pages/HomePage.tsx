import Sidebar from '../components/Sidebar';

const HomePage = () => {
  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <main className="flex-1 overflow-y-auto">
        {/* Main content area - currently blank */}
      </main>
    </div>
  );
};

export default HomePage;

