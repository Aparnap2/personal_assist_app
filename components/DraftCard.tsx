import { Ionicons } from '@expo/vector-icons';
import React, { useState } from 'react';
import { Animated, TouchableOpacity, View } from 'react-native';
import type { Draft } from '../types';
import { formatTimeAgo, truncateText } from '../utils';
import Button from './ui/Button';
import Card from './ui/Card';
import StatusBadge from './ui/StatusBadge';

const AnimatedView = Animated.createAnimatedComponent(View);

interface DraftCardProps {
  draft: Draft;
  onApprove: (draftId: string, scheduleTime?: Date) => void;
  onReject: (draftId: string, reason?: string) => void;
  onEdit?: (draft: Draft) => void;
  onViewDetails?: (draft: Draft) => void;
  onSchedule?: (draft: Draft, time?: Date) => void;
}

const DraftCard: React.FC<DraftCardProps> = ({
  draft,
  onApprove,
  onReject,
  onEdit,
  onViewDetails,
  onSchedule,
}) => {
  const [expanded, setExpanded] = useState(false);
  const [animatedHeight] = useState(new Animated.Value(0));
  const [processingAction, setProcessingAction] = useState<string | null>(null);

  const getBestTime = () => {
    if (draft.posting_recommendations?.best_time) {
      return draft.posting_recommendations.best_time;
    }
    return '10:30 AM';
  };

  const getConfidenceScore = () => {
    return draft.best_time_score || 85;
  };

  const toggleExpanded = () => {
    setExpanded(!expanded);
    Animated.timing(animatedHeight, {
      toValue: expanded ? 0 : 1,
      duration: 300,
      useNativeDriver: false,
    }).start();
  };

  const handleActionWithLoading = async (action: string, callback: () => Promise<void> | void) => {
    setProcessingAction(action);
    try {
      await callback();
    } catch (error) {
      console.error(`Error in ${action}:`, error);
    } finally {
      setProcessingAction(null);
    }
  };

  const renderActionButtons = () => {
    if (draft.status === 'pending') {
      return (
        <View className="space-y-3">
          {/* Primary Actions */}
          <View className="flex-row space-x-2">
            <Button
              title="Reject"
              variant="outline"
              size="sm"
              onPress={() => handleActionWithLoading('reject', () => onReject(draft.id))}
              loading={processingAction === 'reject'}
              className="flex-1"
              icon={<Ionicons name="close" size={16} color="#ef4444" />}
            />
            <Button
              title="Approve"
              variant="primary"
              size="sm"
              onPress={() => handleActionWithLoading('approve', () => onApprove(draft.id))}
              loading={processingAction === 'approve'}
              className="flex-1"
              icon={<Ionicons name="checkmark" size={16} color="white" />}
            />
          </View>

          {/* Schedule Options */}
          <View className="flex-row space-x-2">
            <Button
              title={`Schedule for ${getBestTime()}`}
              variant="secondary"
              size="sm"
              onPress={() => handleActionWithLoading('schedule', () => onSchedule?.(draft))}
              loading={processingAction === 'schedule'}
              className="flex-1"
              icon={<Ionicons name="time" size={14} color="#6366f1" />}
            />
            <Button
              title="Custom Time"
              variant="outline"
              size="sm"
              onPress={() => handleActionWithLoading('custom-schedule', () => onSchedule?.(draft, new Date()))}
              loading={processingAction === 'custom-schedule'}
              className="px-4"
              icon={<Ionicons name="calendar" size={14} color="#6b7280" />}
            />
          </View>
        </View>
      );
    }

    if (draft.status === 'scheduled') {
      return (
        <View className="flex-row items-center justify-between">
          <View className="flex-row items-center">
            <Ionicons name="time" size={16} color="#10b981" />
            <Text className="ml-2 text-sm text-green-700">
              Scheduled for {getBestTime()}
            </Text>
          </View>
          <Button
            title="Cancel"
            variant="outline"
            size="sm"
            onPress={() => handleActionWithLoading('cancel', () => onReject(draft.id, 'cancelled'))}
            loading={processingAction === 'cancel'}
          />
        </View>
      );
    }

    return null;
  };

  const renderMetadata = () => (
    <View className="mb-4">
      <View className="flex-row items-center justify-between mb-2">
        <View className="flex-row items-center space-x-4">
          <Text className="text-xs text-gray-500">
            {formatTimeAgo(draft.createdAt)}
          </Text>
          <Text className="text-xs text-gray-500">
            {draft.platform.charAt(0).toUpperCase() + draft.platform.slice(1)}
          </Text>
        </View>
        <TouchableOpacity onPress={toggleExpanded}>
          <View className="flex-row items-center">
            <Ionicons name="analytics" size={12} color="#6b7280" />
            <Text className="text-xs text-gray-500 ml-1">
              {getConfidenceScore()}% score
            </Text>
            <Ionicons 
              name={expanded ? "chevron-up" : "chevron-down"} 
              size={12} 
              color="#6b7280" 
              style={{ marginLeft: 4 }}
            />
          </View>
        </TouchableOpacity>
      </View>

      {/* Performance Indicators */}
      <View className="flex-row space-x-2">
        {draft.readabilityScore && (
          <ScoreIndicator
            label="Readability"
            score={draft.readabilityScore}
            color={draft.readabilityScore > 70 ? "#10b981" : draft.readabilityScore > 50 ? "#f59e0b" : "#ef4444"}
          />
        )}
        {draft.hookStrength && (
          <ScoreIndicator
            label="Hook"
            score={draft.hookStrength.score}
            color={draft.hookStrength.score > 70 ? "#10b981" : draft.hookStrength.score > 50 ? "#f59e0b" : "#ef4444"}
          />
        )}
        {draft.personalizationScore && (
          <ScoreIndicator
            label="Voice Match"
            score={draft.personalizationScore}
            color={draft.personalizationScore > 80 ? "#10b981" : draft.personalizationScore > 60 ? "#f59e0b" : "#ef4444"}
          />
        )}
      </View>
    </View>
  );

  const ScoreIndicator = ({ label, score, color }: { label: string; score: number; color: string }) => (
    <View className="bg-gray-50 rounded-full px-2 py-1">
      <Text className="text-xs text-gray-600">
        {label}: <Text style={{ color }}>{Math.round(score)}</Text>
      </Text>
    </View>
  );

  const renderExpandedInsights = () => (
    <AnimatedView
      className="overflow-hidden"
      style={{
        opacity: animatedHeight,
        maxHeight: animatedHeight.interpolate({
          inputRange: [0, 1],
          outputRange: [0, 300],
        }),
      }}
    >
      <View className="bg-gray-50 rounded-lg p-4 mb-3 space-y-4">
        {/* Engagement Prediction */}
        {draft.engagementPrediction && (
          <View>
            <Text className="text-sm font-medium text-gray-700 mb-2">
              📈 Predicted Performance
            </Text>
            <View className="flex-row space-x-4">
              <View className="items-center">
                <Text className="text-xs text-gray-500">Likes</Text>
                <Text className="text-sm font-medium text-primary-600">
                  {draft.engagementPrediction.likes}
                </Text>
              </View>
              <View className="items-center">
                <Text className="text-xs text-gray-500">Shares</Text>
                <Text className="text-sm font-medium text-blue-600">
                  {draft.engagementPrediction.shares}
                </Text>
              </View>
              <View className="items-center">
                <Text className="text-xs text-gray-500">Comments</Text>
                <Text className="text-sm font-medium text-green-600">
                  {draft.engagementPrediction.comments}
                </Text>
              </View>
              <View className="items-center">
                <Text className="text-xs text-gray-500">Reach</Text>
                <Text className="text-sm font-medium text-purple-600">
                  {draft.engagementPrediction.reach_estimate}
                </Text>
              </View>
            </View>
          </View>
        )}

        {/* Optimization Suggestions */}
        {draft.optimizationSuggestions && draft.optimizationSuggestions.length > 0 && (
          <View>
            <Text className="text-sm font-medium text-gray-700 mb-2">
              💡 Suggestions
            </Text>
            {draft.optimizationSuggestions.slice(0, 2).map((suggestion, index) => (
              <View key={index} className="flex-row items-start mb-1">
                <Text className="text-xs text-orange-500 mr-2">•</Text>
                <Text className="text-xs text-gray-600 flex-1">
                  {suggestion}
                </Text>
              </View>
            ))}
          </View>
        )}

        {/* Sentiment Analysis */}
        {draft.sentimentScore && (
          <View>
            <Text className="text-sm font-medium text-gray-700 mb-2">
              😊 Sentiment Analysis
            </Text>
            <View className="flex-row space-x-4">
              <Text className="text-xs text-green-600">
                Positive: {Math.round(draft.sentimentScore.positive)}%
              </Text>
              <Text className="text-xs text-red-600">
                Negative: {Math.round(draft.sentimentScore.negative)}%
              </Text>
              <Text className="text-xs text-blue-600">
                Overall: {Math.round(draft.sentimentScore.compound)}
              </Text>
            </View>
          </View>
        )}
      </View>
    </AnimatedView>
  );

  const renderModerationStatus = () => {
    if (draft.moderationStatus === 'flagged') {
      return (
        <View className="bg-orange-50 border border-orange-200 rounded-lg p-2 mb-3">
          <View className="flex-row items-center">
            <Ionicons name="warning" size={16} color="#ea580c" />
            <Text className="text-sm text-orange-700 ml-2">
              Content flagged for review
            </Text>
          </View>
        </View>
      );
    }
    return null;
  };

  return (
    <Card variant="outlined" className="mb-4 shadow-sm">
      <Card.Header
        title={`${draft.platform === 'twitter' ? '𝕏' : '💼'} Draft Post`}
        action={
          <View className="flex-row items-center space-x-2">
            <StatusBadge status={draft.status} />
            {onEdit && (
              <TouchableOpacity onPress={() => onEdit(draft)}>
                <Ionicons name="pencil" size={16} color="#6b7280" />
              </TouchableOpacity>
            )}
          </View>
        }
      />

      <Card.Content>
        {renderMetadata()}
        {renderModerationStatus()}
        {renderExpandedInsights()}
        
        <Text className="text-gray-900 text-base leading-relaxed mb-4">
          {truncateText(draft.content, expanded ? 500 : 200)}
        </Text>

        {draft.variants && draft.variants.length > 0 && (
          <View className="mb-4">
            <Text className="text-sm font-medium text-gray-700 mb-2">
              🔄 Variants ({draft.variants.length})
            </Text>
            <View className="flex-row flex-wrap">
              {draft.variants.slice(0, expanded ? draft.variants.length : 3).map((variant, index) => (
                <TouchableOpacity
                  key={index}
                  className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg px-3 py-2 mr-2 mb-2"
                  onPress={() => {
                    // Handle variant selection
                  }}
                >
                  <Text className="text-xs text-blue-700 font-medium">
                    Variant {index + 1}
                  </Text>
                  {expanded && (
                    <Text className="text-xs text-blue-600 mt-1">
                      {truncateText(variant, 50)}
                    </Text>
                  )}
                </TouchableOpacity>
              ))}
            </View>
          </View>
        )}

        {/* AI Reasoning */}
        {draft.status === 'pending' && (
          <View className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-4 mb-3">
            <View className="flex-row items-start">
              <View className="w-8 h-8 bg-blue-500 rounded-full items-center justify-center">
                <Ionicons name="sparkles" size={16} color="white" />
              </View>
              <View className="ml-3 flex-1">
                <Text className="text-sm font-semibold text-blue-800 mb-1">
                  🎯 AI Insights
                </Text>
                <Text className="text-xs text-blue-700 leading-relaxed">
                  {draft.themes && draft.themes.length > 0
                    ? `Matches your "${draft.themes[0]}" theme • `
                    : ''
                  }
                  Optimal for {getBestTime()} posting • 
                  {getConfidenceScore() > 80 ? 'High engagement potential' : 'Good audience fit'}
                </Text>
                
                {/* Quick Stats */}
                <View className="flex-row mt-2 space-x-3">
                  <View className="flex-row items-center">
                    <Ionicons name="trending-up" size={12} color="#3b82f6" />
                    <Text className="text-xs text-blue-600 ml-1">
                      {getConfidenceScore()}% match
                    </Text>
                  </View>
                  <View className="flex-row items-center">
                    <Ionicons name="time" size={12} color="#3b82f6" />
                    <Text className="text-xs text-blue-600 ml-1">
                      Best: {getBestTime()}
                    </Text>
                  </View>
                  {draft.engagementPrediction && (
                    <View className="flex-row items-center">
                      <Ionicons name="heart" size={12} color="#3b82f6" />
                      <Text className="text-xs text-blue-600 ml-1">
                        ~{draft.engagementPrediction.likes} likes
                      </Text>
                    </View>
                  )}
                </View>
              </View>
            </View>
          </View>
        )}
      </Card.Content>

      <Card.Footer>
        {renderActionButtons()}
        {onViewDetails && (
          <TouchableOpacity 
            onPress={() => onViewDetails(draft)}
            className="mt-2"
          >
            <Text className="text-sm text-primary-500 text-center">
              View Full Details →
            </Text>
          </TouchableOpacity>
        )}
      </Card.Footer>
    </Card>
  );
};

export default DraftCard;