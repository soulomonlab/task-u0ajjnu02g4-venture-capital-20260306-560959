import React from 'react';
import { trackEvent } from '../analytics';

export interface ProfileHeaderProps {
  userId?: string;
  name: string;
  avatarUrl?: string;
}

export const ProfileHeader: React.FC<ProfileHeaderProps> = ({ userId, name, avatarUrl }) => {
  const onEdit = () => {
    trackEvent({ name: 'profile_edit_clicked', user_id: userId, metadata: {} });
    // open edit modal (stub)
    console.log('open edit modal');
  };

  return (
    <div className="flex items-center p-4 border-b">
      <img src={avatarUrl} alt={`${name} avatar`} className="w-14 h-14 rounded-full mr-4" />
      <div className="flex-1">
        <div className="font-bold text-lg">{name}</div>
      </div>
      <button onClick={onEdit} className="px-3 py-2 bg-blue-600 text-white rounded">Edit</button>
    </div>
  );
};

export default ProfileHeader;
