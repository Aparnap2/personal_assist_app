import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { styled } from 'nativewind';
import React, { useEffect } from 'react';
import { RefreshControl, ScrollView, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import DraftCard from '@/components/DraftCard';
import Button from '@/components/ui/Button';
import Card from '@/components/ui/Card';
import { useApp } from '@/contexts/AppContext';
import { useAuth } from '@/contexts/AuthContext';

const StyledScrollView = styled(ScrollView);
const StyledView = styled(View);
const StyledText = styled(Text);
const StyledSafeAreaView = styled(SafeAreaView);

export default function DashboardScreen() {
  const router = useRouter();
  const { user, userProfile } = useAuth();
  const { state, loadDrafts, generateDrafts, approveDraft, rejectDraft } = useApp();
  const [refreshing, setRefreshing] = React.useState(false);

  useEffect(() => {
    loadDrafts();
  }, []);

  const onRefresh = React.useCallback(async () => {
    setRefreshing(true);
    await loadDrafts();
    setRefreshing(false);
  }, []);

  const pendingDrafts = state.drafts.filter(draft => draft.status === 'pending');
  const scheduledPosts = state.drafts.filter(draft => draft.status === 'scheduled');

  const handleGenerateContent = async () => {
    await generateDrafts();
  };

  const mockAnalytics = {
    draftsToday: pendingDrafts.length,
    postsScheduled: scheduledPosts.length,
    engagementGrowth: 12.5,
    timeSaved: 45,
  };

  const QuickActions = () => (
    <Card className="mb-6">
      <Card.Header title="Quick Actions" />
      <Card.Content>
        <StyledView className="flex-row space-x-3">
          <Button
            title="Generate Drafts"
            variant="primary"
            onPress={handleGenerateContent}
            loading={state.loading.drafts}
            icon={<Ionicons name="add" size={16} color="white" />}
            className="flex-1"
          />
          <Button
            title="Chat"
            variant="outline"
            onPress={() => router.push('/chat')}
            icon={<Ionicons name="chatbubbles" size={16} color="#3b82f6" />}
            className="flex-1"
          />
        </StyledView>
      </Card.Content>
    </Card>
  );

  const AnalyticsOverview = () => (
    <Card className="mb-6">
      <Card.Header 
        title="Today's Overview" 
        action={
          <Button
            title="View All"
            variant="outline"
            size="sm"
            onPress={() => router.push('/analytics')}
          />
        }
      />
      <Card.Content>
        <StyledView className="flex-row justify-between">
          <StyledView className="items-center flex-1">
            <StyledText className="text-2xl font-bold text-primary-500">
              {mockAnalytics.draftsToday}
            </StyledText>
            <StyledText className="text-sm text-gray-600">Drafts Ready</StyledText>
          </StyledView>
          <StyledView className="items-center flex-1">
            <StyledText className="text-2xl font-bold text-green-500">
              {mockAnalytics.postsScheduled}
            </StyledText>
            <StyledText className="text-sm text-gray-600">Scheduled</StyledText>
          </StyledView>
          <StyledView className="items-center flex-1">
            <StyledText className="text-2xl font-bold text-blue-500">
              +{mockAnalytics.engagementGrowth}%
            </StyledText>
            <StyledText className="text-sm text-gray-600">Engagement</StyledText>
          </StyledView>
          <StyledView className="items-center flex-1">
            <StyledText className="text-2xl font-bold text-purple-500">
              {mockAnalytics.timeSaved}m
            </StyledText>
            <StyledText className="text-sm text-gray-600">Time Saved</StyledText>
          </StyledView>
        </StyledView>
      </Card.Content>
    </Card>
  );

  const PendingDrafts = () => (
    <StyledView className="mb-6">
      <StyledView className="flex-row items-center justify-between mb-4">
        <StyledText className="text-lg font-semibold text-gray-900">
          Pending Approvals ({pendingDrafts.length})
        </StyledText>
        {pendingDrafts.length > 0 && (
          <Button
            title="View All"
            variant="outline"
            size="sm"
            onPress={() => router.push('/drafts')}
          />
        )}
      </StyledView>
      
      {pendingDrafts.length === 0 ? (
        <Card>
          <Card.Content>
            <StyledView className="items-center py-8">
              <Ionicons name="checkmark-circle" size={48} color="#10b981" />
              <StyledText className="text-gray-600 text-center mt-4">
                No pending drafts. Great work!
              </StyledText>
              <Button
                title="Generate New Content"
                variant="primary"
                onPress={handleGenerateContent}
                loading={state.loading.drafts}
                className="mt-4"
              />
            </StyledView>
          </Card.Content>
        </Card>
      ) : (
        pendingDrafts.slice(0, 2).map(draft => (
          <DraftCard
            key={draft.id}
            draft={draft}
            onApprove={approveDraft}
            onReject={rejectDraft}
            onViewDetails={() => router.push(`/draft?draftId=${draft.id}`)}
          />
        ))
      )}
    </StyledView>
  );

  return (
    <StyledSafeAreaView className="flex-1 bg-gray-50">
      <StyledScrollView
        className="flex-1"
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        <StyledView className="px-4 py-6">
          {/* Header */}
          <StyledView className="mb-6">
            <StyledText className="text-2xl font-bold text-gray-900">
              Good morning, {user?.displayName || 'there'}!
            </StyledText>
            <StyledText className="text-gray-600 mt-1">
              Ready to create some amazing content?
            </StyledText>
          </StyledView>

          <QuickActions />
          <AnalyticsOverview />
          <PendingDrafts />
        </StyledView>
      </StyledScrollView>
    </StyledSafeAreaView>
  );
}
