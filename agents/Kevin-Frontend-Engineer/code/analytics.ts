/*
Frontend analytics utility
- Ensures required fields are present (adds session_id if missing)
- Sends events to /api/analytics/track
- Supports requireAck: awaits server acknowledgement for critical events
*/

export type EventPayload = {
  name: string;
  user_id?: string;
  session_id?: string;
  experiment?: Record<string, string>;
  metadata?: Record<string, any>;
  requireAck?: boolean; // when true, wait for server ack before resolving
};

const ANALYTICS_ENDPOINT = '/api/analytics/track';

function getSessionId(): string {
  try {
    let s = localStorage.getItem('session_id');
    if (!s) {
      s = `sess_${Math.random().toString(36).slice(2, 10)}`;
      localStorage.setItem('session_id', s);
    }
    return s;
  } catch (e) {
    return `sess_${Date.now()}`;
  }
}

export async function trackEvent(payload: EventPayload): Promise<void> {
  const body = {
    ...payload,
    session_id: payload.session_id || getSessionId(),
  };

  // Basic validation: ensure at least session or user is present
  if (!body.user_id && !body.session_id) {
    console.warn('trackEvent called without user_id or session_id', payload);
  }

  try {
    if (payload.requireAck) {
      // Wait for server acknowledgement
      const res = await fetch(`${ANALYTICS_ENDPOINT}?ack=true`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      if (!res.ok) {
        console.error('Analytics ack failed', await res.text());
        throw new Error('Analytics ack failed');
      }
      return;
    }

    // Fire-and-forget
    fetch(ANALYTICS_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    }).catch((err) => console.warn('Analytics fire-and-forget failed', err));
  } catch (err) {
    console.error('trackEvent error', err);
    throw err;
  }
}
