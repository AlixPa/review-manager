import { User } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

interface UserBadgeProps {
  publicId: string;
  userName: string;
  variant?: 'full' | 'pill';
}

const UserBadge = ({ publicId, userName, variant = 'full' }: UserBadgeProps) => {
  const { user } = useAuth();
  const isCurrentUser = user?.public_id === publicId;
  const displayName = isCurrentUser ? 'Me' : userName;

  if (variant === 'pill') {
    return (
      <span
        className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-medium border ${
          isCurrentUser
            ? 'bg-blue-50 text-blue-700 border-blue-200'
            : 'bg-purple-50 text-purple-700 border-purple-200'
        }`}
      >
        <User className="w-3.5 h-3.5" />
        {displayName}
      </span>
    );
  }

  // 'full' variant with icon circle
  return (
    <div className="flex items-center gap-2">
      <div className={`${isCurrentUser ? 'bg-blue-100' : 'bg-purple-100'} p-2 rounded-full`}>
        <User className={`w-4 h-4 ${isCurrentUser ? 'text-blue-600' : 'text-purple-600'}`} />
      </div>
      <div>
        <p className="text-xs text-gray-500">Created by</p>
        <p className="font-semibold text-gray-800">{displayName}</p>
      </div>
    </div>
  );
};

export default UserBadge;

