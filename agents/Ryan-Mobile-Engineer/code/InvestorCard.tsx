import React from 'react';
import { View, Text, TouchableOpacity, Image } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { useAnalytics } from '../useAnalytics';

export default function InvestorCard({ investor, userId, sessionId, experiment }) {
  const navigation = useNavigation();
  const { track } = useAnalytics({ userId, sessionId, experiment });

  async function onPress() {
    track('investor_card_tap', { investor_id: investor.id }).catch(() => {});
    navigation.navigate('InvestorProfile', { id: investor.id });
  }

  return (
    <TouchableOpacity onPress={onPress} testID={`investor-card-${investor.id}`}>
      <View style={{ flexDirection: 'row', padding: 12, alignItems: 'center' }}>
        <Image source={{ uri: investor.avatar_url }} style={{ width: 48, height: 48, borderRadius: 24 }} />
        <View style={{ marginLeft: 12 }}>
          <Text style={{ fontWeight: '600' }}>{investor.name}</Text>
          <Text style={{ color: '#666' }}>{investor.title}</Text>
        </View>
      </View>
    </TouchableOpacity>
  );
}
