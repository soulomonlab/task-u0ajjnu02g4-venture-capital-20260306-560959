import React from 'react';
import { trackEvent } from '../analytics';

export interface InvestorCardProps {
  id: string;
  name: string;
  firm?: string;
  avatarUrl?: string;
}

export const InvestorCard: React.FC<InvestorCardProps> = ({ id, name, firm, avatarUrl }) => {
  const onClick = async () => {
    // Track click; critical event requires ack
    await trackEvent({ name: 'investor_card_clicked', user_id: undefined, metadata: { investor_id: id }, requireAck: true });
    // navigate to investor profile (stub)
    window.location.href = `/investors/${id}`;
  };

  return (
    <div className="p-4 border rounded shadow-sm hover:shadow-md cursor-pointer" onClick={onClick} role="button" tabIndex={0}>
      <div className="flex items-center">
        <img src={avatarUrl} alt={`${name} avatar`} className="w-12 h-12 rounded-full mr-4" />
        <div>
          <div className="font-semibold">{name}</div>
          {firm && <div className="text-sm text-gray-500">{firm}</div>}
        </div>
      </div>
    </div>
  );
};

export default InvestorCard;
