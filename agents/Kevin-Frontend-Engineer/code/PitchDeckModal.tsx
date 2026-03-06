import React from 'react';
import { trackEvent } from '../analytics';

export interface PitchDeckModalProps {
  pitchId: string;
  open: boolean;
  onClose: () => void;
}

export const PitchDeckModal: React.FC<PitchDeckModalProps> = ({ pitchId, open, onClose }) => {
  React.useEffect(() => {
    if (open) {
      trackEvent({ name: 'pitch_deck_viewed', metadata: { pitch_id: pitchId }, requireAck: true });
    }
  }, [open, pitchId]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div className="bg-white p-6 rounded w-3/4 max-w-3xl">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-semibold">Pitch Deck</h3>
          <button onClick={onClose} aria-label="Close">Close</button>
        </div>
        <div className="h-96 overflow-auto border rounded">{/* deck content stub */}</div>
      </div>
    </div>
  );
};

export default PitchDeckModal;
