import React, { useState } from 'react';
import { Modal, View, Text, TextInput, TouchableOpacity } from 'react-native';
import { useAnalytics } from '../useAnalytics';

export default function RequestIntroModal({ visible, onClose, investorId, userId, sessionId, experiment }) {
  const [message, setMessage] = useState('');
  const { track } = useAnalytics({ userId, sessionId, experiment });

  async function submit() {
    try {
      const res = await fetch('https://api.example.com/requests', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ investor_id: investorId, message }) });
      const payload = await res.json();
      if (!res.ok) throw new Error('request failed');
      await track('request_intro_submitted', { target_investor_id: investorId, request_id: payload.id }, { serverAck: true });
      onClose();
    } catch (e) {
      // surface error - simplified
      console.warn('intro request failed', e);
    }
  }

  return (
    <Modal visible={visible} animationType="slide">
      <View style={{ flex: 1, padding: 16 }}>
        <Text style={{ fontSize: 18, fontWeight: '700' }}>Request an Intro</Text>
        <TextInput value={message} onChangeText={setMessage} placeholder="Why should they meet you?" style={{ marginTop: 12, borderWidth: 1, borderColor: '#ddd', padding: 8 }} />
        <TouchableOpacity onPress={submit} testID="submit-request">
          <Text style={{ marginTop: 12, color: '#fff', backgroundColor: '#007bff', padding: 8, textAlign: 'center' }}>Send Request</Text>
        </TouchableOpacity>
        <TouchableOpacity onPress={onClose} testID="close-request">
          <Text style={{ marginTop: 12, color: '#007bff' }}>Cancel</Text>
        </TouchableOpacity>
      </View>
    </Modal>
  );
}
