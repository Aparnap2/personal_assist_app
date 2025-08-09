import { Ionicons } from '@expo/vector-icons';
import { styled } from 'nativewind';
import React, { useEffect, useState } from 'react';
import { Dimensions, ScrollView, Text, TouchableOpacity, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import Card from '@/components/ui/Card';
import { useApp } from '@/contexts/AppContext';

const StyledScrollView = styled(ScrollView);
const StyledView = styled(View);
const StyledText = styled(Text);
const StyledSafeAreaView = styled(SafeAreaView);
const StyledTouchableOpacity = styled(TouchableOpacity);

const { width: screenWidth } = Dimensions.get('window');

export default function AnalyticsScreen() {
  const { state, loadAnalytics } = useApp();
  const [selectedTimeRange, setSelectedTimeRange] = useState('week');

  useEffect(() => {
    loadAnalytics(selectedTimeRange);
  }, [selectedTimeRange]);

  const timeRangeOptions = [
    { key: 'week', label: 'Week' },
    { key: 'month', label: 'Month' },
    { key: 'quarter', label: 'Quarter' },
  ];

  // Mock analytics data
  const mockData = {
    overview: {
      draftsGenerated: 24,
      draftsApproved: 18,
      postsPublished: 16,
      engagementGrowth: 12.5,
      timeSaved: 180,
      approvalRate: 75,
    },
    topThemes: [
      { theme: 'AI Strategy', posts: 8, engagement: 156 },
      { theme: 'Content Marketing', posts: 6, engagement: 142 },
      { theme: 'Industry Insights', posts: 4, engagement: 98 },
    ],
    performance: [
      { date: '2024-01-01', impressions: 1200, engagement: 85 },
      { date: '2024-01-02', impressions: 1450, engagement: 92 },
      { date: '2024-01-03', impressions: 1100, engagement: 78 },
      { date: '2024-01-04', impressions: 1800, engagement: 134 },
      { date: '2024-01-05', impressions: 1650, engagement: 118 },
    ],
  };

  const TimeRangePicker = () => (
    <StyledView className="flex-row bg-gray-100 rounded-lg p-1 mb-6">
      {timeRangeOptions.map(option => (
        <StyledTouchableOpacity
          key={option.key}
          onPress={() => setSelectedTimeRange(option.key)}
          className={`
            flex-1 py-2 px-3 rounded-md
            ${selectedTimeRange === option.key ? 'bg-white shadow-sm' : ''}
          `}
        >
          <StyledText className={`
            text-center font-medium
            ${selectedTimeRange === option.key ? 'text-gray-900' : 'text-gray-600'}
          `}>
            {option.label}
          </StyledText>
        </StyledTouchableOpacity>
      ))}
    </StyledView>
  );

  const OverviewCards = () => (
    <StyledView className="grid grid-cols-2 gap-4 mb-6">
      <Card className="flex-1 mr-2">
        <Card.Content>
          <StyledView className="items-center">
            <StyledText className="text-3xl font-bold text-primary-500">
              {mockData.overview.draftsGenerated}
            </StyledText>
            <StyledText className="text-sm text-gray-600 text-center">
              Drafts Generated
            </StyledText>
            <StyledView className="flex-row items-center mt-1">
              <Ionicons name="trending-up" size={12} color="#10b981" />
              <StyledText className="text-xs text-green-600 ml-1">
                +5 from last week
              </StyledText>
            </StyledView>
          </StyledView>
        </Card.Content>
      </Card>

      <Card className="flex-1 ml-2">
        <Card.Content>
          <StyledView className="items-center">
            <StyledText className="text-3xl font-bold text-green-500">
              {mockData.overview.approvalRate}%
            </StyledText>
            <StyledText className="text-sm text-gray-600 text-center">
              Approval Rate
            </StyledText>
            <StyledView className="flex-row items-center mt-1">
              <Ionicons name="trending-up" size={12} color="#10b981" />
              <StyledText className="text-xs text-green-600 ml-1">
                +2% improvement
              </StyledText>
            </StyledView>
          </StyledView>
        </Card.Content>
      </Card>

      <Card className="flex-1 mr-2">
        <Card.Content>
          <StyledView className="items-center">
            <StyledText className="text-3xl font-bold text-blue-500">
              +{mockData.overview.engagementGrowth}%
            </StyledText>
            <StyledText className="text-sm text-gray-600 text-center">
              Engagement Growth
            </StyledText>
            <StyledView className="flex-row items-center mt-1">
              <Ionicons name="trending-up" size={12} color="#10b981" />
              <StyledText className="text-xs text-green-600 ml-1">
                Above target
              </StyledText>
            </StyledView>
          </StyledView>
        </Card.Content>
      </Card>

      <Card className="flex-1 ml-2">
        <Card.Content>
          <StyledView className="items-center">
            <StyledText className="text-3xl font-bold text-purple-500">
              {mockData.overview.timeSaved}m
            </StyledText>
            <StyledText className="text-sm text-gray-600 text-center">
              Time Saved
            </StyledText>
            <StyledView className="flex-row items-center mt-1">
              <Ionicons name="time" size={12} color="#8b5cf6" />
              <StyledText className="text-xs text-purple-600 ml-1">
                3 hours total
              </StyledText>
            </StyledView>
          </StyledView>
        </Card.Content>
      </Card>
    </StyledView>
  );

  const TopThemes = () => (
    <Card className="mb-6">
      <Card.Header title="Top Performing Themes" />
      <Card.Content>
        {mockData.topThemes.map((theme, index) => (
          <StyledView key={theme.theme} className="mb-4 last:mb-0">
            <StyledView className="flex-row items-center justify-between mb-2">
              <StyledText className="font-medium text-gray-900">
                {theme.theme}
              </StyledText>
              <StyledText className="text-sm text-gray-600">
                {theme.posts} posts
              </StyledText>
            </StyledView>
            <StyledView className="bg-gray-200 rounded-full h-2">
              <StyledView 
                className="bg-primary-500 h-2 rounded-full"
                style={{ 
                  width: `${(theme.engagement / Math.max(...mockData.topThemes.map(t => t.engagement))) * 100}%` 
                }}
              />
            </StyledView>
            <StyledText className="text-xs text-gray-600 mt-1">
              {theme.engagement} total engagement
            </StyledText>
          </StyledView>
        ))}
      </Card.Content>
    </Card>
  );

  const BestPerformingContent = () => (
    <Card className="mb-6">
      <Card.Header title="Best Performing Content" />
      <Card.Content>
        <StyledView className="space-y-4">
          <StyledView className="border border-green-200 bg-green-50 rounded-lg p-4">
            <StyledView className="flex-row items-start justify-between mb-2">
              <StyledView className="flex-1">
                <StyledText className="font-medium text-gray-900">
                  "5 AI trends that will shape 2024..."
                </StyledText>
                <StyledText className="text-sm text-gray-600 mt-1">
                  Published 3 days ago • Twitter
                </StyledText>
              </StyledView>
              <StyledView className="bg-green-100 px-2 py-1 rounded-full">
                <StyledText className="text-xs font-medium text-green-800">
                  Top 1%
                </StyledText>
              </StyledView>
            </StyledView>
            <StyledView className="flex-row justify-between">
              <StyledView className="items-center">
                <StyledText className="text-lg font-bold text-gray-900">1.2K</StyledText>
                <StyledText className="text-xs text-gray-600">Impressions</StyledText>
              </StyledView>
              <StyledView className="items-center">
                <StyledText className="text-lg font-bold text-gray-900">87</StyledText>
                <StyledText className="text-xs text-gray-600">Likes</StyledText>
              </StyledView>
              <StyledView className="items-center">
                <StyledText className="text-lg font-bold text-gray-900">23</StyledText>
                <StyledText className="text-xs text-gray-600">Shares</StyledText>
              </StyledView>
              <StyledView className="items-center">
                <StyledText className="text-lg font-bold text-gray-900">12</StyledText>
                <StyledText className="text-xs text-gray-600">Comments</StyledText>
              </StyledView>
            </StyledView>
          </StyledView>

          <StyledView className="border border-gray-200 rounded-lg p-4">
            <StyledView className="flex-row items-start justify-between mb-2">
              <StyledView className="flex-1">
                <StyledText className="font-medium text-gray-900">
                  "Content marketing strategies for consultants..."
                </StyledText>
                <StyledText className="text-sm text-gray-600 mt-1">
                  Published 1 week ago • LinkedIn
                </StyledText>
              </StyledView>
              <StyledView className="bg-blue-100 px-2 py-1 rounded-full">
                <StyledText className="text-xs font-medium text-blue-800">
                  Top 5%
                </StyledText>
              </StyledView>
            </StyledView>
            <StyledView className="flex-row justify-between">
              <StyledView className="items-center">
                <StyledText className="text-lg font-bold text-gray-900">856</StyledText>
                <StyledText className="text-xs text-gray-600">Impressions</StyledText>
              </StyledView>
              <StyledView className="items-center">
                <StyledText className="text-lg font-bold text-gray-900">64</StyledText>
                <StyledText className="text-xs text-gray-600">Likes</StyledText>
              </StyledView>
              <StyledView className="items-center">
                <StyledText className="text-lg font-bold text-gray-900">18</StyledText>
                <StyledText className="text-xs text-gray-600">Shares</StyledText>
              </StyledView>
              <StyledView className="items-center">
                <StyledText className="text-lg font-bold text-gray-900">7</StyledText>
                <StyledText className="text-xs text-gray-600">Comments</StyledText>
              </StyledView>
            </StyledView>
          </StyledView>
        </StyledView>
      </Card.Content>
    </Card>
  );

  const Recommendations = () => (
    <Card>
      <Card.Header title="AI Recommendations" />
      <Card.Content>
        <StyledView className="space-y-3">
          <StyledView className="bg-blue-50 border border-blue-200 rounded-lg p-3">
            <StyledView className="flex-row items-start">
              <Ionicons name="bulb" size={16} color="#2563eb" />
              <StyledView className="ml-3 flex-1">
                <StyledText className="font-medium text-blue-800">
                  Optimal posting time
                </StyledText>
                <StyledText className="text-sm text-blue-600 mt-1">
                  Your audience is most active on Tuesdays at 10:30 AM. Consider scheduling more content at this time.
                </StyledText>
              </StyledView>
            </StyledView>
          </StyledView>

          <StyledView className="bg-purple-50 border border-purple-200 rounded-lg p-3">
            <StyledView className="flex-row items-start">
              <Ionicons name="trending-up" size={16} color="#7c3aed" />
              <StyledView className="ml-3 flex-1">
                <StyledText className="font-medium text-purple-800">
                  Content theme opportunity
                </StyledText>
                <StyledText className="text-sm text-purple-600 mt-1">
                  "Industry insights" posts perform 23% better. Try creating more content around this theme.
                </StyledText>
              </StyledView>
            </StyledView>
          </StyledView>

          <StyledView className="bg-green-50 border border-green-200 rounded-lg p-3">
            <StyledView className="flex-row items-start">
              <Ionicons name="checkmark-circle" size={16} color="#059669" />
              <StyledView className="ml-3 flex-1">
                <StyledText className="font-medium text-green-800">
                  Great improvement
                </StyledText>
                <StyledText className="text-sm text-green-600 mt-1">
                  Your approval rate increased by 12% this week. Keep up the excellent work!
                </StyledText>
              </StyledView>
            </StyledView>
          </StyledView>
        </StyledView>
      </Card.Content>
    </Card>
  );

  return (
    <StyledSafeAreaView className="flex-1 bg-gray-50">
      {/* Header */}
      <StyledView className="bg-white border-b border-gray-200 px-4 py-6">
        <StyledText className="text-2xl font-bold text-gray-900">
          Analytics
        </StyledText>
        <StyledText className="text-gray-600 mt-1">
          Track your content performance and growth
        </StyledText>
      </StyledView>

      <StyledScrollView className="flex-1 px-4 py-6">
        <TimeRangePicker />
        <OverviewCards />
        <TopThemes />
        <BestPerformingContent />
        <Recommendations />
      </StyledScrollView>
    </StyledSafeAreaView>
  );
}