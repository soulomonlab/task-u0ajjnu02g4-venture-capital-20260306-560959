import React from 'react';
import { trackEvent } from '../analytics';

export interface SchedulerProps {
  userId?: string;
}

export const Scheduler: React.FC<SchedulerProps> = ({ userId }) => {
  const [selected, setSelected] = React.useState<string | null>(null);

  const onSelectSlot = (slotId: string) => {
    setSelected(slotId);
    trackEvent({ name: 'scheduler_slot_selected', user_id: userId, metadata: { slot_id: slotId } });
  };

  const onConfirm = async () => {
    if (!selected) return;
    await trackEvent({ name: 'scheduler_slot_confirmed', user_id: userId, metadata: { slot_id: selected }, requireAck: true });
    alert('Slot confirmed');
  };

  return (
    <div className="p-4 border rounded">
      <div className="grid grid-cols-3 gap-2">
        {['slot1', 'slot2', 'slot3', 'slot4', 'slot5', 'slot6'].map((s) => (
          <button key={s} onClick={() => onSelectSlot(s)} className={`p-2 border rounded ${selected === s ? 'bg-blue-100' : ''}`}>{s}</button>
        ))}
      </div>
      <div className="flex justify-end mt-3">
        <button onClick={onConfirm} className="px-3 py-2 bg-blue-600 text-white rounded">Confirm</button>
      </div>
    </div>
  );
};

export default Scheduler;
