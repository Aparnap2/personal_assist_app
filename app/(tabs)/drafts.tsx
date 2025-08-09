import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { styled } from 'nativewind';
import React, { useEffect, useState } from 'react';
import { ScrollView, Text, TouchableOpacity, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import DraftCard from '@/components/DraftCard';
import Button from '@/components/ui/Button';
import { useApp } from '@/contexts/AppContext';

const StyledScrollView = styled(ScrollView);
const StyledView = styled(View);
const StyledText = styled(Text);
const StyledSafeAreaView = styled(SafeAreaView);
const StyledTouchableOpacity = styled(TouchableOpacity);

export default function DraftsScreen() {
  const router = useRouter();
  const { state, loadDrafts, generateDrafts, approveDraft, rejectDraft } = useApp();
  const [selectedFilter, setSelectedFilter] = useState<string>('all');

  useEffect(() => {
    loadDrafts();
  }, []);

  const filterOptions = [
    { key: 'all', label: 'All', count: state.drafts.length },
    { key: 'pending', label: 'Pending', count: state.drafts.filter(d => d.status === 'pending').length },
    { key: 'approved', label: 'Approved', count: state.drafts.filter(d => d.status === 'approved').length },
    { key: 'scheduled', label: 'Scheduled', count: state.drafts.filter(d => d.status === 'scheduled').length },
    { key: 'published', label: 'Published', count: state.drafts.filter(d => d.status === 'published').length },
  ];

  const filteredDrafts = selectedFilter === 'all' 
    ? state.drafts 
    : state.drafts.filter(draft => draft.status === selectedFilter);

  const FilterTabs = () => (
    <StyledView className="mb-6">
      <StyledScrollView horizontal showsHorizontalScrollIndicator={false}>
        <StyledView className="flex-row space-x-3 px-4">
          {filterOptions.map(option => (
            <StyledTouchableOpacity
              key={option.key}
              onPress={() => setSelectedFilter(option.key)}
              className={`
                px-4 py-2 rounded-full flex-row items-center space-x-2
                ${selectedFilter === option.key 
                  ? 'bg-primary-500' 
                  : 'bg-white border border-gray-300'
                }
              `}
            >
              <StyledText className={`
                font-medium
                ${selectedFilter === option.key ? 'text-white' : 'text-gray-700'}
              `}>
                {option.label}
              </StyledText>
              <StyledView className={`
                px-2 py-0.5 rounded-full
                ${selectedFilter === option.key 
                  ? 'bg-white/20' 
                  : 'bg-gray-100'
                }
              `}>
                <StyledText className={`
                  text-xs font-medium
                  ${selectedFilter === option.key ? 'text-white' : 'text-gray-600'}
                `}>
                  {option.count}
                </StyledText>
              </StyledView>
            </StyledTouchableOpacity>
          ))}
        </StyledView>
      </StyledScrollView>
    </StyledView>
  );

  const EmptyState = () => (
    <StyledView className="flex-1 items-center justify-center py-16">
      <Ionicons 
        name={selectedFilter === 'pending' ? 'hourglass-outline' : 'document-text-outline'} 
        size={64} 
        color="#9ca3af" 
      />
      <StyledText className="text-xl font-semibold text-gray-900 mt-4">
        {selectedFilter === 'all' ? 'No drafts yet' : `No ${selectedFilter} drafts`}
      </StyledText>
      <StyledText className="text-gray-600 text-center mt-2 px-8">
        {selectedFilter === 'all' 
          ? 'Generate your first batch of content drafts to get started'
          : `You don't have any ${selectedFilter} drafts at the moment`
        }
      </StyledText>
      {selectedFilter === 'all' && (
        <Button
          title="Generate Drafts"
          variant="primary"
          onPress={() => generateDrafts()}
          loading={state.loading.drafts}
          icon={<Ionicons name="add" size={16} color="white" />}
          className="mt-6"
        />
      )}
    </StyledView>
  );

  return (
    <StyledSafeAreaView className="flex-1 bg-gray-50">
      {/* Header */}
      <StyledView className="bg-white border-b border-gray-200">
        <StyledView className="px-4 py-6">
          <StyledView className="flex-row items-center justify-between">
            <StyledView>
              <StyledText className="text-2xl font-bold text-gray-900">
                Content Drafts
              </StyledText>
              <StyledText className="text-gray-600 mt-1">
                Review and approve your AI-generated content
              </StyledText>
            </StyledView>
            <Button
              title="Generate"
              variant="primary"
              size="sm"
              onPress={() => generateDrafts()}
              loading={state.loading.drafts}
              icon={<Ionicons name="add" size={14} color="white" />}
            />
          </StyledView>
        </StyledView>
        <FilterTabs />
      </StyledView>

      {/* Content */}
      {filteredDrafts.length === 0 ? (
        <EmptyState />
      ) : (
        <StyledScrollView className="flex-1">
          <StyledView className="px-4 py-6">
            {filteredDrafts.map(draft => (
              <DraftCard
                key={draft.id}
                draft={draft}
                onApprove={approveDraft}
                onReject={rejectDraft}
                onViewDetails={() => router.push(`/draft?draftId=${draft.id}`)}
              />
            ))}
          </StyledView>
        </StyledScrollView>
      )}
    </StyledSafeAreaView>
  );
}