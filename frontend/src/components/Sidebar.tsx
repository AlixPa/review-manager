import { useState, useEffect } from 'react';
import { ClipboardList, PlusCircle, FolderKanban, Trophy, LogOut, User } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { usersApi } from '../api/users';
import { User as UserType } from '../types/user';
import { apiClient } from '../api/client';

const Sidebar = () => {
  const { user, isAuthenticated, login, logout, refetchUser } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  
  // Dev login state
  const isDevelopmentLogin = import.meta.env.VITE_FLAG_DEVELOPMENT_LOGIN === 'true';
  const [devUsers, setDevUsers] = useState<UserType[]>([]);
  const [isLoadingDevUsers, setIsLoadingDevUsers] = useState(false);
  
  useEffect(() => {
    if (isDevelopmentLogin && !isAuthenticated) {
      const fetchDevUsers = async () => {
        setIsLoadingDevUsers(true);
        try {
          const users = await usersApi.getUsers();
          setDevUsers(users.sort((a, b) => a.user_name.localeCompare(b.user_name)));
        } catch (error) {
          console.error('Failed to fetch dev users:', error);
        } finally {
          setIsLoadingDevUsers(false);
        }
      };
      fetchDevUsers();
    }
  }, [isDevelopmentLogin, isAuthenticated]);
  
  const handleDevLogin = async (userId: string) => {
    try {
      // Call PATCH /users/set_user to set cookies
      await apiClient.patch('/users/set_user', { user_public_id: userId });
    } catch (error) {
      // Backend returns RedirectResponse, which causes fetch to follow redirect
      // and return HTML instead of JSON, causing a parsing error.
      // But the cookie is already set, so we can ignore the error and just refresh.
      console.log('Dev login: Cookie set, refreshing auth state...');
    } finally {
      // Always refresh auth state after login attempt
      await refetchUser();
    }
  };
  
  const menuItems = [
    {
      id: 'my-todo',
      title: 'My todo',
      description: 'View reviews to do and pending changes',
      icon: ClipboardList,
      iconBg: 'bg-blue-100',
      iconColor: 'text-blue-600',
      borderColor: 'border-blue-200',
      hoverBg: 'hover:bg-blue-50',
      path: '/todo',
    },
    {
      id: 'create-request',
      title: 'Create new request',
      description: 'Submit a new code review request to your team members',
      icon: PlusCircle,
      iconBg: 'bg-green-100',
      iconColor: 'text-green-600',
      borderColor: 'border-green-200',
      hoverBg: 'hover:bg-green-50',
      path: '/create',
    },
    {
      id: 'manage-requests',
      title: 'Manage my requests',
      description: 'Track and manage all review requests you have created',
      icon: FolderKanban,
      iconBg: 'bg-purple-100',
      iconColor: 'text-purple-600',
      borderColor: 'border-purple-200',
      hoverBg: 'hover:bg-purple-50',
      path: '/manage',
    },
    {
      id: 'rewards',
      title: 'Rewards',
      description: 'View your earned rewards and points by cycle',
      icon: Trophy,
      iconBg: 'bg-amber-100',
      iconColor: 'text-amber-600',
      borderColor: 'border-amber-200',
      hoverBg: 'hover:bg-amber-50',
      path: '/rewards',
    },
  ];

  return (
    <aside className="w-96 bg-white shadow-lg border-r border-gray-200 flex flex-col">
      <div className="p-6 flex-1">
        <h1 className="text-2xl font-bold text-gray-800 mb-8">
          Review Manager
        </h1>
        
        {!isAuthenticated ? (
          <div className="mb-8">
            {isDevelopmentLogin ? (
              <div className="bg-amber-50 border-2 border-amber-300 rounded-xl p-4">
                <div className="flex items-center gap-2 mb-3">
                  <div className="bg-amber-500 p-2 rounded-full">
                    <User className="w-4 h-4 text-white" />
                  </div>
                  <h3 className="font-semibold text-amber-900">Dev Login</h3>
                </div>
                {isLoadingDevUsers ? (
                  <p className="text-sm text-amber-700">Loading users...</p>
                ) : (
                  <select
                    onChange={(e) => e.target.value && handleDevLogin(e.target.value)}
                    className="w-full p-3 border-2 border-amber-300 rounded-lg focus:border-amber-500 focus:outline-none transition-colors cursor-pointer bg-white"
                    defaultValue=""
                  >
                    <option value="" disabled>
                      Select user to login as
                    </option>
                    {devUsers.map((devUser) => (
                      <option key={devUser.public_id} value={devUser.public_id}>
                        {devUser.user_name}
                      </option>
                    ))}
                  </select>
                )}
              </div>
            ) : (
              <button
                onClick={login}
                className="w-full flex items-center justify-center gap-3 p-4 rounded-xl bg-white border-2 border-gray-300 hover:border-blue-500 hover:bg-blue-50 transition-all duration-200 shadow-sm hover:shadow-md group cursor-pointer"
              >
                <svg className="w-5 h-5" viewBox="0 0 24 24">
                  <path
                    fill="#4285F4"
                    d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                  />
                  <path
                    fill="#34A853"
                    d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                  />
                  <path
                    fill="#FBBC05"
                    d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                  />
                  <path
                    fill="#EA4335"
                    d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                  />
                </svg>
                <span className="font-medium text-gray-700 group-hover:text-blue-700">
                  Connect with Google
                </span>
              </button>
            )}
          </div>
        ) : (
          <div className="mb-8 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl border border-blue-200">
            <div className="flex items-center gap-3 mb-3">
              <div className="bg-blue-500 p-2 rounded-full">
                <User className="w-4 h-4 text-white" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-xs text-gray-600 mb-0.5">Logged in as</p>
                <p className="font-semibold text-gray-800 truncate">{user?.user_name}</p>
              </div>
            </div>
            <button
              onClick={logout}
              className="w-full flex items-center justify-center gap-2 px-3 py-2 bg-white hover:bg-red-50 text-gray-700 hover:text-red-600 rounded-lg border border-gray-200 hover:border-red-300 transition-all duration-200 text-sm font-medium cursor-pointer"
            >
              <LogOut className="w-4 h-4" />
              Logout
            </button>
          </div>
        )}
        
        <nav className="space-y-5">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <button
                key={item.id}
                onClick={() => isAuthenticated && navigate(item.path)}
                className={`w-full flex gap-4 p-5 rounded-xl border-2 transition-all duration-200 group text-left ${
                  !isAuthenticated 
                    ? 'cursor-not-allowed border-gray-200 bg-white'
                    : isActive
                    ? `${item.borderColor} bg-gradient-to-r from-blue-50 to-purple-50 shadow-md cursor-pointer border-l-4`
                    : `${item.borderColor} ${item.hoverBg} bg-white hover:shadow-md cursor-pointer`
                }`}
                disabled={!isAuthenticated}
                style={{ opacity: isAuthenticated ? 1 : 0.5 }}
              >
                <div className={`${item.iconBg} ${item.iconColor} p-3 rounded-lg flex-shrink-0 h-fit transition-transform duration-200 group-hover:scale-110 ${isActive ? 'scale-110' : ''}`}>
                  <Icon className="w-6 h-6" />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className={`font-semibold text-base mb-1 ${isActive ? 'text-gray-900' : 'text-gray-800'}`}>
                    {item.title}
                  </h3>
                  <p className="text-sm text-gray-600 leading-relaxed">
                    {item.description}
                  </p>
                </div>
              </button>
            );
          })}
        </nav>
      </div>
    </aside>
  );
};

export default Sidebar;

