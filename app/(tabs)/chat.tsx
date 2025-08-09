import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { styled } from 'nativewind';
import React, { useEffect, useRef, useState } from 'react';
import {
    KeyboardAvoidingView,
    Platform,
    ScrollView,
    Text,
    TextInput,
    TouchableOpacity,
    View
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import Button from '@/components/ui/Button';
import { useApp } from '@/contexts/AppContext';
import { useAuth } from '@/contexts/AuthContext';
import type { ChatMessage } from '@/types';
import { formatTimeAgo } from '@/utils';

const StyledScrollView = styled(ScrollView);
const StyledView = styled(View);
const StyledText = styled(Text);
const StyledSafeAreaView = styled(SafeAreaView);
const StyledTouchableOpacity = styled(TouchableOpacity);
const StyledTextInput = styled(TextInput);
const StyledKeyboardAvoidingView = styled(KeyboardAvoidingView);

export default function ChatScreen() {
  const router = useRouter();
  const { user } = useAuth();
  const { state, loadChatHistory, sendMessage, generateDrafts } = useApp();
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const scrollViewRef = useRef<ScrollView>(null);

  useEffect(() => {
    loadChatHistory();
  }, []);

  useEffect(() => {
    // Auto-scroll to bottom when new messages arrive
    setTimeout(() => {
      scrollViewRef.current?.scrollToEnd({ animated: true });
    }, 100);
  }, [state.chatMessages]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const message = inputMessage.trim();
    setInputMessage('');
    setIsTyping(true);

    try {
      await sendMessage(message);
    } finally {
      setIsTyping(false);
    }
  };

  const handleActionPress = async (action: any) => {
    setIsTyping(true);
    try {
      switch (action.type) {
        case 'generate_draft':
          await generateDrafts(action.data?.prompt);
          router.push('/drafts');
          break;
        case 'create_task':
          // Navigate to Notion to create task
          router.push('/notion');
          break;
        case 'schedule_post':
          router.push('/drafts');
          break;
        default:
          console.log('Unknown action type:', action.type);
      }
    } finally {
      setIsTyping(false);
    }
  };

  const MessageBubble = ({ message }: { message: ChatMessage }) => {
    const isUser = message.role === 'user';
    
    return (
      <StyledView className={`mb-4 ${isUser ? 'items-end' : 'items-start'}`}>
        <StyledView
          className={`
            max-w-xs px-4 py-3 rounded-2xl
            ${isUser 
              ? 'bg-primary-500 rounded-br-md' 
              : 'bg-white border border-gray-200 rounded-bl-md'
            }
          `}
        >
          <StyledText className={`${isUser ? 'text-white' : 'text-gray-900'}`}>
            {message.content}
          </StyledText>
          
          {message.actions && message.actions.length > 0 && (
            <StyledView className="mt-3 space-y-2">
              {message.actions.map((action, index) => (
                <Button
                  key={index}
                  title={action.label}
                  variant={isUser ? 'secondary' : 'primary'}
                  size="sm"
                  onPress={() => handleActionPress(action)}
                  className="w-full"
                />
              ))}
            </StyledView>
          )}
        </StyledView>
        
        <StyledText className="text-xs text-gray-500 mt-1 px-2">
          {formatTimeAgo(message.timestamp)}
        </StyledText>
      </StyledView>
    );
  };

  const SuggestedPrompts = () => {
    const prompts = [
      "Generate 5 posts about AI trends",
      "Help me with content strategy",
      "Create a weekly content calendar",
      "Analyze my recent performance",
    ];

    return (
      <StyledView className="mb-4">
        <StyledText className="text-sm font-medium text-gray-700 mb-3 px-4">
          Suggested prompts:
        </StyledText>
        <StyledScrollView horizontal showsHorizontalScrollIndicator={false}>
          <StyledView className="flex-row space-x-3 px-4">
            {prompts.map((prompt, index) => (
              <StyledTouchableOpacity
                key={index}
                onPress={() => setInputMessage(prompt)}
                className="bg-gray-100 px-4 py-2 rounded-full"
              >
                <StyledText className="text-gray-700 text-sm">{prompt}</StyledText>
              </StyledTouchableOpacity>
            ))}
          </StyledView>
        </StyledScrollView>
      </StyledView>
    );
  };

  return (
    <StyledSafeAreaView className="flex-1 bg-gray-50">
      {/* Header */}
      <StyledView className="bg-white border-b border-gray-200 px-4 py-6">
        <StyledText className="text-2xl font-bold text-gray-900">
          AI Assistant
        </StyledText>
        <StyledText className="text-gray-600 mt-1">
          Get personalized content advice and automation
        </StyledText>
      </StyledView>

      <StyledKeyboardAvoidingView 
        className="flex-1" 
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        {/* Messages */}
        <StyledScrollView 
          ref={scrollViewRef}
          className="flex-1 px-4 py-6"
          contentContainerStyle={{ flexGrow: 1 }}
        >
          {state.chatMessages.length === 0 ? (
            <StyledView className="flex-1 justify-center items-center">
              <Ionicons name="chatbubbles" size={64} color="#9ca3af" />
              <StyledText className="text-xl font-semibold text-gray-900 mt-4">
                Start a conversation
              </StyledText>
              <StyledText className="text-gray-600 text-center mt-2 px-8">
                Ask me anything about content strategy, social media, or automation
              </StyledText>
              <SuggestedPrompts />
            </StyledView>
          ) : (
            <>
              {state.chatMessages.map(message => (
                <MessageBubble key={message.id} message={message} />
              ))}
              
              {isTyping && (
                <StyledView className="mb-4 items-start">
                  <StyledView className="bg-white border border-gray-200 rounded-2xl rounded-bl-md px-4 py-3">
                    <StyledView className="flex-row space-x-1">
                      <StyledView className="w-2 h-2 bg-gray-400 rounded-full animate-pulse" />
                      <StyledView className="w-2 h-2 bg-gray-400 rounded-full animate-pulse" />
                      <StyledView className="w-2 h-2 bg-gray-400 rounded-full animate-pulse" />
                    </StyledView>
                  </StyledView>
                </StyledView>
              )}
            </>
          )}
        </StyledScrollView>

        {/* Input */}
        <StyledView className="bg-white border-t border-gray-200 px-4 py-4">
          <StyledView className="flex-row items-end space-x-3">
            <StyledView className="flex-1 min-h-12 max-h-32 bg-gray-100 rounded-2xl px-4 py-3">
              <StyledTextInput
                className="flex-1 text-gray-900"
                placeholder="Ask me anything..."
                value={inputMessage}
                onChangeText={setInputMessage}
                multiline
                textAlignVertical="center"
              />
            </StyledView>
            
            <StyledTouchableOpacity
              onPress={handleSendMessage}
              disabled={!inputMessage.trim() || isTyping}
              className={`
                w-12 h-12 rounded-full items-center justify-center
                ${inputMessage.trim() && !isTyping 
                  ? 'bg-primary-500' 
                  : 'bg-gray-300'
                }
              `}
            >
              <Ionicons 
                name="send" 
                size={20} 
                color={inputMessage.trim() && !isTyping ? 'white' : '#9ca3af'} 
              />
            </StyledTouchableOpacity>
          </StyledView>
        </StyledView>
      </StyledKeyboardAvoidingView>
    </StyledSafeAreaView>
  );
}