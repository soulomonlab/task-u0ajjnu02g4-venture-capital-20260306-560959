import React from 'react';
import { trackEvent } from '../analytics';

export interface RequestIntroModalProps {
  investorId: string;
  open: boolean;
  onClose: () => void;
}

export const RequestIntroModal: React.FC<RequestIntroModalProps> = ({ investorId, open, onClose }) => {
  const [message, setMessage] = React.useState('');

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      // track request intro submission as critical
      await trackEvent({ name: 'request_intro_submitted', metadata: { investor_id: investorId, message }, requireAck: true });
      // simulate API call
      await new Promise((r) => setTimeout(r, 300));
      onClose();
    } catch (err) {
      console.error('submit failed', err);
      alert('Failed to send request. Please try again.');
    }
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div className="bg-white p-6 rounded w-full max-w-md">
        <h3 className="text-lg font-semibold mb-2">Request Introduction</h3>
        <form onSubmit={onSubmit}>
          <textarea value={message} onChange={(e) => setMessage(e.target.value)} className="w-full border p-2 mb-3" placeholder="Why should this investor meet you?" />
          <div className="flex justify-end">
            <button type="button" onClick={onClose} className="px-3 py-2 mr-2">Cancel</button>
            <button type="submit" className="px-3 py-2 bg-green-600 text-white rounded">Send</button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default RequestIntroModal;
