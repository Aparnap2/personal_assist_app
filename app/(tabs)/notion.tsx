import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { styled } from 'nativewind';
import React, { useState } from 'react';
import { ScrollView, Text, TouchableOpacity, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import Button from '@/components/ui/Button';
import Card from '@/components/ui/Card';
import StatusBadge from '@/components/ui/StatusBadge';
import { useAuth } from '@/contexts/AuthContext';
import { formatTimeAgo } from '@/utils';

const StyledScrollView = styled(ScrollView);
const StyledView = styled(View);
const StyledText = styled(Text);
const StyledSafeAreaView = styled(SafeAreaView);
const StyledTouchableOpacity = styled(TouchableOpacity);

export default function NotionScreen() {
  const router = useRouter();
  const { userProfile } = useAuth();
  const [isConnected, setIsConnected] = useState(false);
  const [recentPages, setRecentPages] = useState([
    {
      id: '1',
      title: 'Weekly Content Strategy',
      type: 'project',
      updatedAt: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2 hours ago
      tags: ['strategy', 'content'],
    },
    {
      id: '2', 
      title: 'Client Meeting Notes - Acme Corp',
      type: 'meeting',
      updatedAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000), // 1 day ago
      tags: ['client', 'meeting'],
    },
    {
      id: '3',
      title: 'Q1 Marketing Tasks',
      type: 'task',
      updatedAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000), // 3 days ago
      tags: ['tasks', 'marketing'],
    },
  ]);

  const templates = [
    {
      id: 'meeting',
      name: 'Meeting Notes',
      description: 'Structured template for meeting summaries and action items',
      icon: 'people',
    },
    {
      id: 'project',
      name: 'Project Brief',
      description: 'Project overview with objectives, timeline, and resources',
      icon: 'folder',
    },
    {
      id: 'task',
      name: 'Task List',
      description: 'Organized task management with priorities and due dates',
      icon: 'checkbox',
    },
    {
      id: 'note',
      name: 'Quick Note',
      description: 'Simple note template for ideas and thoughts',
      icon: 'document-text',
    },
  ];

  const ConnectNotion = () => (
    <Card className="mb-6">
      <Card.Content>
        <StyledView className="items-center py-8">
          <StyledView className="w-16 h-16 bg-black rounded-xl items-center justify-center mb-4">
            <Ionicons name="library" size={32} color="white" />
          </StyledView>
          <StyledText className="text-xl font-semibold text-gray-900 mb-2">
            Connect to Notion
          </StyledText>
          <StyledText className="text-gray-600 text-center mb-6 px-4">
            Automatically create and organize your notes, tasks, and meeting summaries in Notion
          </StyledText>
          <Button
            title="Connect Notion"
            variant="primary"
            onPress={() => {
              // Mock connection - would handle OAuth in real implementation
              setIsConnected(true);
            }}
            icon={<Ionicons name="link" size={16} color="white" />}
          />
        </StyledView>
      </Card.Content>
    </Card>
  );

  const QuickCreate = () => (
    <Card className="mb-6">
      <Card.Header title="Quick Create" />
      <Card.Content>
        <StyledView className="grid grid-cols-2 gap-3">
          {templates.map(template => (
            <StyledTouchableOpacity
              key={template.id}
              className="bg-gray-50 p-4 rounded-xl border border-gray-200 active:bg-gray-100"
              onPress={() => {
                // Mock page creation
                const newPage = {
                  id: Date.now().toString(),
                  title: `New ${template.name}`,
                  type: template.id as any,
                  updatedAt: new Date(),
                  tags: [template.id],
                };
                setRecentPages([newPage, ...recentPages]);
              }}
            >
              <StyledView className="items-center">
                <Ionicons name={template.icon as any} size={24} color="#3b82f6" />
                <StyledText className="font-medium text-gray-900 mt-2 text-center">
                  {template.name}
                </StyledText>
                <StyledText className="text-xs text-gray-600 text-center mt-1">
                  {template.description}
                </StyledText>
              </StyledView>
            </StyledTouchableOpacity>
          ))}
        </StyledView>
      </Card.Content>
    </Card>
  );

  const RecentPages = () => (
    <Card>
      <Card.Header 
        title="Recent Pages"
        action={
          <Button
            title="View All"
            variant="outline"
            size="sm"
            onPress={() => {}}
          />
        }
      />
      <Card.Content>
        {recentPages.map((page, index) => (
          <StyledView key={page.id}>
            <StyledTouchableOpacity className="py-3">
              <StyledView className="flex-row items-start justify-between">
                <StyledView className="flex-1">
                  <StyledView className="flex-row items-center mb-1">
                    <Ionicons
                      name={
                        page.type === 'meeting' ? 'people' :
                        page.type === 'project' ? 'folder' :
                        page.type === 'task' ? 'checkbox' : 'document-text'
                      }
                      size={16}
                      color="#6b7280"
                    />
                    <StyledText className="font-medium text-gray-900 ml-2 flex-1">
                      {page.title}
                    </StyledText>
                  </StyledView>
                  <StyledView className="flex-row items-center">
                    <StyledText className="text-sm text-gray-600">
                      {formatTimeAgo(page.updatedAt)}
                    </StyledText>
                    <StyledView className="flex-row ml-4">
                      {page.tags.slice(0, 2).map(tag => (
                        <StyledView 
                          key={tag}
                          className="bg-gray-100 px-2 py-1 rounded mr-2"
                        >
                          <StyledText className="text-xs text-gray-600">
                            {tag}
                          </StyledText>
                        </StyledView>
                      ))}
                    </StyledView>
                  </StyledView>
                </StyledView>
                <Ionicons name="chevron-forward" size={16} color="#9ca3af" />
              </StyledView>
            </StyledTouchableOpacity>
            {index < recentPages.length - 1 && (
              <StyledView className="h-px bg-gray-200" />
            )}
          </StyledView>
        ))}
      </Card.Content>
    </Card>
  );

  const SyncStatus = () => (
    <StyledView className="bg-green-50 border border-green-200 rounded-lg p-3 mb-6">
      <StyledView className="flex-row items-center">
        <Ionicons name="checkmark-circle" size={20} color="#059669" />
        <StyledView className="ml-3 flex-1">
          <StyledText className="font-medium text-green-800">
            Sync active
          </StyledText>
          <StyledText className="text-sm text-green-600">
            Last synced 2 minutes ago
          </StyledText>
        </StyledView>
      </StyledView>
    </StyledView>
  );

  return (
    <StyledSafeAreaView className="flex-1 bg-gray-50">
      {/* Header */}
      <StyledView className="bg-white border-b border-gray-200 px-4 py-6">
        <StyledView className="flex-row items-center justify-between">
          <StyledView>
            <StyledText className="text-2xl font-bold text-gray-900">
              Notion Integration
            </StyledText>
            <StyledText className="text-gray-600 mt-1">
              Organize your content and tasks automatically
            </StyledText>
          </StyledView>
          {isConnected && (
            <StatusBadge status="approved" />
          )}
        </StyledView>
      </StyledView>

      <StyledScrollView className="flex-1 px-4 py-6">
        {!isConnected ? (
          <ConnectNotion />
        ) : (
          <>
            <SyncStatus />
            <QuickCreate />
            <RecentPages />
          </>
        )}
      </StyledScrollView>
    </StyledSafeAreaView>
  );
}