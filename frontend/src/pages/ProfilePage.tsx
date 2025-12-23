import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import Sidebar from '../components/Sidebar';

const ProfilePage = () => {
  const { user, isLoading, refetchUser } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    // Refetch user after OAuth callback
    refetchUser().then(() => {
      // Redirect to home after successful login
      navigate('/');
    });
  }, []);

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Completing login...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <main className="flex-1 overflow-y-auto p-8">
        <div className="max-w-2xl mx-auto">
          <h1 className="text-3xl font-bold text-gray-800 mb-6">Profile</h1>
          {user && (
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-gray-600 mb-2">Welcome,</p>
              <p className="text-2xl font-semibold text-gray-800">{user.user_name}</p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default ProfilePage;

