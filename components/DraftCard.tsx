import { Ionicons } from '@expo/vector-icons';
import { styled } from 'nativewind';
import React from 'react';
import { Text, TouchableOpacity, View } from 'react-native';
import type { Draft } from '../types';
import { formatTimeAgo, truncateText } from '../utils';
import Button from './ui/Button';
import Card from './ui/Card';
import StatusBadge from './ui/StatusBadge';

const StyledView = styled(View);
const StyledText = styled(Text);

interface DraftCardProps {
  draft: Draft;
  onApprove: (draftId: string, scheduleTime?: Date) => void;
  onReject: (draftId: string, reason?: string) => void;
  onEdit?: (draft: Draft) => void;
  onViewDetails?: (draft: Draft) => void;
}

const DraftCard: React.FC<DraftCardProps> = ({
  draft,
  onApprove,
  onReject,
  onEdit,
  onViewDetails,
}) => {
  const getBestTime = () => {
    // Mock best time - would come from analytics
    return '10:30 AM';
  };

  const getConfidenceScore = () => {
    // Mock confidence score - would come from AI
    return draft.bestTimeScore || 85;
  };

  const renderActionButtons = () => {
    if (draft.status === 'pending') {
      return (
        <StyledView className="flex-row space-x-2">
          <Button
            title="Reject"
            variant="outline"
            size="sm"
            onPress={() => onReject(draft.id)}
            className="flex-1"
          />
          <Button
            title={`Approve & Schedule (${getBestTime()})`}
            variant="primary"
            size="sm"
            onPress={() => onApprove(draft.id)}
            className="flex-2"
          />
        </StyledView>
      );
    }

    return null;
  };

  const renderMetadata = () => (
    <StyledView className="flex-row items-center justify-between text-xs text-gray-500 mb-3">
      <StyledView className="flex-row items-center space-x-4">
        <StyledText className="text-xs text-gray-500">
          {formatTimeAgo(draft.createdAt)}
        </StyledText>
        <StyledText className="text-xs text-gray-500">
          Platform: {draft.platform}
        </StyledText>
      </StyledView>
      <StyledView className="flex-row items-center space-x-2">
        <Ionicons name="analytics" size={12} color="#6b7280" />
        <StyledText className="text-xs text-gray-500">
          {getConfidenceScore()}% confidence
        </StyledText>
      </StyledView>
    </StyledView>
  );

  const renderModerationStatus = () => {
    if (draft.moderationStatus === 'flagged') {
      return (
        <StyledView className="bg-orange-50 border border-orange-200 rounded-lg p-2 mb-3">
          <StyledView className="flex-row items-center">
            <Ionicons name="warning" size={16} color="#ea580c" />
            <StyledText className="text-sm text-orange-700 ml-2">
              Content flagged for review
            </StyledText>
          </StyledView>
        </StyledView>
      );
    }
    return null;
  };

  return (
    <Card variant="outlined" className="mb-4">
      <Card.Header
        title="Draft Post"
        action={
          <StyledView className="flex-row items-center space-x-2">
            <StatusBadge status={draft.status} />
            {onEdit && (
              <TouchableOpacity onPress={() => onEdit(draft)}>
                <Ionicons name="pencil" size={16} color="#6b7280" />
              </TouchableOpacity>
            )}
          </StyledView>
        }
      />

      <Card.Content>
        {renderMetadata()}
        {renderModerationStatus()}
        
        <StyledText className="text-gray-900 text-base leading-relaxed mb-3">
          {truncateText(draft.content, 200)}
        </StyledText>

        {draft.variants && draft.variants.length > 0 && (
          <StyledView className="mb-3">
            <StyledText className="text-sm font-medium text-gray-700 mb-2">
              Variants ({draft.variants.length})
            </StyledText>
            <StyledView className="flex-row flex-wrap">
              {draft.variants.slice(0, 3).map((variant, index) => (
                <StyledView
                  key={index}
                  className="bg-gray-100 rounded-lg px-3 py-1 mr-2 mb-2"
                >
                  <StyledText className="text-xs text-gray-600">
                    Variant {index + 1}
                  </StyledText>
                </StyledView>
              ))}
            </StyledView>
          </StyledView>
        )}

        {draft.status === 'pending' && (
          <StyledView className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-3">
            <StyledView className="flex-row items-start">
              <Ionicons name="bulb" size={16} color="#2563eb" />
              <StyledView className="ml-2 flex-1">
                <StyledText className="text-sm font-medium text-blue-800">
                  Why this draft?
                </StyledText>
                <StyledText className="text-xs text-blue-600 mt-1">
                  Performs well on Tuesday mornings • Matches your "AI strategy" theme • 
                  Similar posts increased reach by 31%
                </StyledText>
              </StyledView>
            </StyledView>
          </StyledView>
        )}
      </Card.Content>

      <Card.Footer>
        {renderActionButtons()}
        {onViewDetails && (
          <TouchableOpacity onPress={() => onViewDetails(draft)}>
            <StyledText className="text-sm text-primary-500">View Details</StyledText>
          </TouchableOpacity>
        )}
      </Card.Footer>
    </Card>
  );
};

export default DraftCard;