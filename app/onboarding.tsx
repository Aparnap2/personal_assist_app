import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import React, { useState } from 'react';
import {
  Alert,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  Text,
  TextInput,
  View
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import Button from '@/components/ui/Button';
import Card from '@/components/ui/Card';
import { useAuth } from '@/contexts/AuthContext';
import { apiService } from '@/services/api';
import type { VoiceProfile } from '@/types';

interface OnboardingStep {
  id: string;
  title: string;
  subtitle: string;
  component: React.ComponentType<any>;
}

export default function OnboardingScreen() {
  const router = useRouter();
  const { updateUserProfile } = useAuth();
  
  const [currentStep, setCurrentStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [onboardingData, setOnboardingData] = useState({
    goals: [] as string[],
    themes: [] as string[],
    writingSamples: [] as string[],
    voiceProfile: null as VoiceProfile | null,
    preferences: {
      notifications: {
        drafts: true,
        approvals: true,
        analytics: true,
        engagement: true,
      },
      posting: {
        autoApprove: false,
        bestTimeOnly: true,
        requireModeration: true,
      },
      consultation: {
        proactive: true,
        frequency: 'daily' as 'daily' | 'weekly' | 'monthly',
      },
    }
  });

  const steps: OnboardingStep[] = [
    {
      id: 'welcome',
      title: 'Welcome to Nexus AI',
      subtitle: 'Your personal AI content assistant',
      component: WelcomeStep,
    },
    {
      id: 'goals',
      title: 'What are your goals?',
      subtitle: 'Help us understand what you want to achieve',
      component: GoalsStep,
    },
    {
      id: 'themes',
      title: 'Content themes',
      subtitle: 'What topics do you write about?',
      component: ThemesStep,
    },
    {
      id: 'voice',
      title: 'Your writing voice',
      subtitle: 'Help us learn your unique style',
      component: VoiceStep,
    },
    {
      id: 'preferences',
      title: 'Preferences',
      subtitle: 'Customize your experience',
      component: PreferencesStep,
    },
    {
      id: 'integrations',
      title: 'Connect accounts',
      subtitle: 'Link your social media accounts',
      component: IntegrationsStep,
    },
    {
      id: 'complete',
      title: 'You\'re all set!',
      subtitle: 'Let\'s create your first content',
      component: CompleteStep,
    },
  ];

  const handleNext = async () => {
    if (currentStep === steps.length - 1) {
      await completeOnboarding();
      return;
    }

    // Validate current step
    const isValid = await validateCurrentStep();
    if (!isValid) return;

    setCurrentStep(currentStep + 1);
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const validateCurrentStep = async (): Promise<boolean> => {
    const step = steps[currentStep];

    switch (step.id) {
      case 'goals':
        if (onboardingData.goals.length === 0) {
          Alert.alert('Please select at least one goal');
          return false;
        }
        break;
      
      case 'themes':
        if (onboardingData.themes.length === 0) {
          Alert.alert('Please select at least one theme');
          return false;
        }
        break;
      
      case 'voice':
        if (onboardingData.writingSamples.length < 2) {
          Alert.alert('Please provide at least 2 writing samples');
          return false;
        }
        // Process voice analysis
        await processVoiceAnalysis();
        break;
    }

    return true;
  };

  const processVoiceAnalysis = async () => {
    if (onboardingData.writingSamples.length === 0) return;

    setLoading(true);
    try {
      const response = await apiService.post('/v1/user/analyze-voice', {
        samples: onboardingData.writingSamples
      });

      if (response.data.success) {
        const voiceProfile: VoiceProfile = {
          id: response.data.data.id || 'temp',
          samples: onboardingData.writingSamples,
          tone: response.data.data.tone,
          style: response.data.data.style,
          embedding: response.data.data.embedding,
          createdAt: new Date(),
          updatedAt: new Date(),
        };

        setOnboardingData(prev => ({
          ...prev,
          voiceProfile
        }));
      }
    } catch (error) {
      console.error('Voice analysis failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const completeOnboarding = async () => {
    setLoading(true);
    try {
      const profileData = {
        goals: onboardingData.goals,
        themes: onboardingData.themes,
        voiceProfile: onboardingData.voiceProfile,
        preferences: onboardingData.preferences,
        onboardingCompleted: true,
      };

      await updateUserProfile(profileData);
      router.replace('/(tabs)');
    } catch (error) {
      console.error('Onboarding completion failed:', error);
      Alert.alert('Error', 'Failed to complete onboarding. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const CurrentStepComponent = steps[currentStep].component;

  return (
    <SafeAreaView className="flex-1 bg-gradient-to-br from-blue-50 to-indigo-100">
      <KeyboardAvoidingView
        className="flex-1"
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        {/* Progress Bar */}
        <View className="px-6 py-4">
          <View className="flex-row items-center justify-between mb-2">
            <Text className="text-sm text-gray-600">
              Step {currentStep + 1} of {steps.length}
            </Text>
            <Text className="text-sm text-primary-600 font-medium">
              {Math.round(((currentStep + 1) / steps.length) * 100)}%
            </Text>
          </View>
          <View className="h-2 bg-gray-200 rounded-full">
            <View 
              className="h-full bg-gradient-to-r from-primary-500 to-primary-600 rounded-full transition-all duration-300"
              style={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
            />
          </View>
        </View>

        {/* Content */}
        <ScrollView className="flex-1 px-6">
          <View className="mb-8">
            <Text className="text-3xl font-bold text-gray-900 mb-2">
              {steps[currentStep].title}
            </Text>
            <Text className="text-lg text-gray-600">
              {steps[currentStep].subtitle}
            </Text>
          </View>

          <CurrentStepComponent
            data={onboardingData}
            updateData={setOnboardingData}
            loading={loading}
          />
        </ScrollView>

        {/* Navigation */}
        <View className="px-6 py-6 border-t border-gray-200 bg-white">
          <View className="flex-row space-x-4">
            {currentStep > 0 && (
              <Button
                title="Back"
                variant="outline"
                onPress={handleBack}
                className="flex-1"
                disabled={loading}
              />
            )}
            <Button
              title={currentStep === steps.length - 1 ? 'Get Started' : 'Continue'}
              variant="primary"
              onPress={handleNext}
              className="flex-1"
              loading={loading}
            />
          </View>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

// Step Components
function WelcomeStep() {
  return (
    <View className="items-center py-8">
      <View className="w-24 h-24 bg-gradient-to-br from-primary-500 to-primary-600 rounded-full items-center justify-center mb-6">
        <Ionicons name="sparkles" size={40} color="white" />
      </View>
      <Text className="text-lg text-gray-700 text-center leading-relaxed">
        Nexus AI helps you create authentic, engaging content that matches your unique voice and grows your audience.
      </Text>
      <Text className="text-base text-gray-600 text-center mt-4">
        Let's get you set up in just a few minutes.
      </Text>
    </View>
  );
}

function GoalsStep({ data, updateData }: any) {
  const goals = [
    { id: 'grow_audience', label: 'Grow my audience', icon: 'trending-up' },
    { id: 'thought_leadership', label: 'Establish thought leadership', icon: 'bulb' },
    { id: 'increase_engagement', label: 'Increase engagement', icon: 'heart' },
    { id: 'save_time', label: 'Save time on content creation', icon: 'time' },
    { id: 'consistent_posting', label: 'Post more consistently', icon: 'calendar' },
    { id: 'professional_brand', label: 'Build professional brand', icon: 'briefcase' },
  ];

  const toggleGoal = (goalId: string) => {
    updateData((prev: any) => ({
      ...prev,
      goals: prev.goals.includes(goalId)
        ? prev.goals.filter((g: string) => g !== goalId)
        : [...prev.goals, goalId]
    }));
  };

  return (
    <View>
      <Text className="text-base text-gray-600 mb-6">
        Select all that apply to help us tailor your experience:
      </Text>
      <View className="space-y-3">
        {goals.map((goal) => (
          <Card
            key={goal.id}
            className={`border-2 ${
              data.goals.includes(goal.id)
                ? 'border-primary-500 bg-primary-50'
                : 'border-gray-200 bg-white'
            }`}
            onPress={() => toggleGoal(goal.id)}
          >
            <Card.Content className="flex-row items-center p-4">
              <Ionicons
                name={goal.icon as any}
                size={24}
                color={data.goals.includes(goal.id) ? '#3b82f6' : '#6b7280'}
              />
              <Text
                className={`ml-3 text-base ${
                  data.goals.includes(goal.id)
                    ? 'text-primary-700 font-medium'
                    : 'text-gray-700'
                }`}
              >
                {goal.label}
              </Text>
            </Card.Content>
          </Card>
        ))}
      </View>
    </View>
  );
}

function ThemesStep({ data, updateData }: any) {
  const themes = [
    'AI & Technology', 'Business Strategy', 'Marketing', 'Productivity',
    'Leadership', 'Entrepreneurship', 'Design', 'Development',
    'Data Science', 'Finance', 'Health & Wellness', 'Education',
    'Sustainability', 'Innovation', 'Remote Work', 'Personal Growth'
  ];

  const toggleTheme = (theme: string) => {
    updateData((prev: any) => ({
      ...prev,
      themes: prev.themes.includes(theme)
        ? prev.themes.filter((t: string) => t !== theme)
        : [...prev.themes, theme]
    }));
  };

  return (
    <View>
      <Text className="text-base text-gray-600 mb-6">
        Choose the topics you write about most often:
      </Text>
      <View className="flex-row flex-wrap gap-3">
        {themes.map((theme) => (
          <Button
            key={theme}
            title={theme}
            variant={data.themes.includes(theme) ? 'primary' : 'outline'}
            size="sm"
            onPress={() => toggleTheme(theme)}
            className="mb-2"
          />
        ))}
      </View>
    </View>
  );
}

function VoiceStep({ data, updateData, loading }: any) {
  const [currentSample, setCurrentSample] = useState('');

  const addSample = () => {
    if (currentSample.trim()) {
      updateData((prev: any) => ({
        ...prev,
        writingSamples: [...prev.writingSamples, currentSample.trim()]
      }));
      setCurrentSample('');
    }
  };

  const removeSample = (index: number) => {
    updateData((prev: any) => ({
      ...prev,
      writingSamples: prev.writingSamples.filter((_: any, i: number) => i !== index)
    }));
  };

  return (
    <View>
      <Text className="text-base text-gray-600 mb-6">
        Share 2-3 examples of your writing so we can learn your voice:
      </Text>

      <Card className="mb-4">
        <Card.Content>
          <TextInput
            className="text-base text-gray-900 min-h-24"
            placeholder="Paste a recent post, email, or any piece of your writing..."
            multiline
            textAlignVertical="top"
            value={currentSample}
            onChangeText={setCurrentSample}
          />
          <Button
            title="Add Sample"
            variant="primary"
            size="sm"
            onPress={addSample}
            disabled={!currentSample.trim()}
            className="mt-3 self-end"
          />
        </Card.Content>
      </Card>

      {data.writingSamples.length > 0 && (
        <View>
          <Text className="text-sm font-medium text-gray-700 mb-3">
            Your samples ({data.writingSamples.length}):
          </Text>
          {data.writingSamples.map((sample: string, index: number) => (
            <Card key={index} className="mb-2 bg-gray-50">
              <Card.Content>
                <View className="flex-row justify-between items-start">
                  <Text className="text-sm text-gray-700 flex-1 mr-3">
                    {sample.substring(0, 100)}...
                  </Text>
                  <Button
                    title=""
                    variant="ghost"
                    size="sm"
                    onPress={() => removeSample(index)}
                    icon={<Ionicons name="close" size={16} color="#ef4444" />}
                  />
                </View>
              </Card.Content>
            </Card>
          ))}
        </View>
      )}

      {loading && (
        <View className="items-center py-4">
          <Text className="text-primary-600 text-sm">
            Analyzing your writing voice...
          </Text>
        </View>
      )}

      {data.voiceProfile && (
        <Card className="bg-green-50 border-green-200">
          <Card.Content>
            <View className="flex-row items-center mb-2">
              <Ionicons name="checkmark-circle" size={20} color="#10b981" />
              <Text className="ml-2 text-green-800 font-medium">
                Voice analysis complete!
              </Text>
            </View>
            <Text className="text-green-700 text-sm">
              {data.voiceProfile.style?.summary || 'Your unique voice profile has been created.'}
            </Text>
          </Card.Content>
        </Card>
      )}
    </View>
  );
}

function PreferencesStep({ data, updateData }: any) {
  const updatePreference = (section: string, key: string, value: any) => {
    updateData((prev: any) => ({
      ...prev,
      preferences: {
        ...prev.preferences,
        [section]: {
          ...prev.preferences[section],
          [key]: value
        }
      }
    }));
  };

  return (
    <View className="space-y-6">
      <Card>
        <Card.Header title="Posting Preferences" />
        <Card.Content>
          <PreferenceToggle
            title="Auto-approve high confidence posts"
            subtitle="Posts with 90%+ confidence score will be published automatically"
            value={data.preferences.posting.autoApprove}
            onChange={(value: any) => updatePreference('posting', 'autoApprove', value)}
          />
          <PreferenceToggle
            title="Only suggest optimal posting times"
            subtitle="Show only the best times based on audience activity"
            value={data.preferences.posting.bestTimeOnly}
            onChange={(value: any) => updatePreference('posting', 'bestTimeOnly', value)}
          />
        </Card.Content>
      </Card>

      <Card>
        <Card.Header title="AI Consultation" />
        <Card.Content>
          <PreferenceToggle
            title="Proactive suggestions"
            subtitle="Get AI recommendations for content improvements"
            value={data.preferences.consultation.proactive}
            onChange={(value: any) => updatePreference('consultation', 'proactive', value)}
          />
          
          <View className="mt-4">
            <Text className="text-sm font-medium text-gray-700 mb-2">
              Consultation frequency:
            </Text>
            <View className="flex-row space-x-2">
              {['daily', 'weekly', 'monthly'].map((freq) => (
                <Button
                  key={freq}
                  title={freq.charAt(0).toUpperCase() + freq.slice(1)}
                  variant={data.preferences.consultation.frequency === freq ? 'primary' : 'outline'}
                  size="sm"
                  onPress={() => updatePreference('consultation', 'frequency', freq)}
                />
              ))}
            </View>
          </View>
        </Card.Content>
      </Card>
    </View>
  );
}

function PreferenceToggle({ title, subtitle, value, onChange }: any) {
  return (
    <View className="flex-row items-center justify-between py-3">
      <View className="flex-1 mr-4">
        <Text className="text-base font-medium text-gray-900">
          {title}
        </Text>
        <Text className="text-sm text-gray-600 mt-1">
          {subtitle}
        </Text>
      </View>
      <Button
        title={value ? 'On' : 'Off'}
        variant={value ? 'primary' : 'outline'}
        size="sm"
        onPress={() => onChange(!value)}
      />
    </View>
  );
}

function IntegrationsStep() {
  const integrations = [
    { id: 'twitter', name: 'Twitter/X', icon: 'logo-twitter', available: true },
    { id: 'linkedin', name: 'LinkedIn', icon: 'logo-linkedin', available: false },
    { id: 'notion', name: 'Notion', icon: 'document-text', available: true },
  ];

  return (
    <View>
      <Text className="text-base text-gray-600 mb-6">
        Connect your accounts to start publishing content (optional - you can do this later):
      </Text>
      
      <View className="space-y-3">
        {integrations.map((integration) => (
          <Card
            key={integration.id}
            className={`border ${
              integration.available
                ? 'border-gray-200 bg-white'
                : 'border-gray-100 bg-gray-50'
            }`}
          >
            <Card.Content className="flex-row items-center justify-between p-4">
              <View className="flex-row items-center">
                <Ionicons
                  name={integration.icon as any}
                  size={24}
                  color={integration.available ? '#3b82f6' : '#9ca3af'}
                />
                <View className="ml-3">
                  <Text className="text-base font-medium text-gray-900">
                    {integration.name}
                  </Text>
                  {!integration.available && (
                    <Text className="text-sm text-gray-500">
                      Coming soon
                    </Text>
                  )}
                </View>
              </View>
              
              {integration.available && (
                <Button
                  title="Connect"
                  variant="outline"
                  size="sm"
                  onPress={() => {/* Handle connection */}}
                />
              )}
            </Card.Content>
          </Card>
        ))}
      </View>

      <Text className="text-sm text-gray-500 text-center mt-6">
        You can always connect accounts later in Settings
      </Text>
    </View>
  );
}

function CompleteStep() {
  return (
    <View className="items-center py-8">
      <View className="w-24 h-24 bg-gradient-to-br from-green-500 to-green-600 rounded-full items-center justify-center mb-6">
        <Ionicons name="checkmark" size={40} color="white" />
      </View>
      <Text className="text-lg text-gray-700 text-center leading-relaxed mb-4">
        Perfect! Your AI assistant is now calibrated to your unique voice and preferences.
      </Text>
      <Text className="text-base text-gray-600 text-center">
        Let's create your first piece of content together.
      </Text>
    </View>
  );
}