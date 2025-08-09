import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { styled } from 'nativewind';
import React, { useState } from 'react';
import { Alert, ScrollView, Text, TouchableOpacity, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import Button from '@/components/ui/Button';
import Card from '@/components/ui/Card';
import Input from '@/components/ui/Input';
import { useAuth } from '@/contexts/AuthContext';
import { validateEmail } from '@/utils';

const StyledScrollView = styled(ScrollView);
const StyledView = styled(View);
const StyledText = styled(Text);
const StyledSafeAreaView = styled(SafeAreaView);
const StyledTouchableOpacity = styled(TouchableOpacity);

export default function AuthScreen() {
  const router = useRouter();
  const { signIn, signUp } = useAuth();
  const [mode, setMode] = useState<'signin' | 'signup'>('signin');
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    displayName: '',
    confirmPassword: '',
  });
  const [errors, setErrors] = useState<any>({});

  const validateForm = () => {
    const newErrors: any = {};

    if (!validateEmail(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }

    if (mode === 'signup') {
      if (!formData.displayName.trim()) {
        newErrors.displayName = 'Display name is required';
      }

      if (formData.password !== formData.confirmPassword) {
        newErrors.confirmPassword = 'Passwords do not match';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validateForm()) return;

    setLoading(true);
    try {
      if (mode === 'signin') {
        await signIn(formData.email, formData.password);
      } else {
        await signUp(formData.email, formData.password, formData.displayName);
      }
      router.replace('/(tabs)');
    } catch (error: any) {
      Alert.alert(
        'Authentication Error',
        error.message || 'An error occurred during authentication'
      );
    } finally {
      setLoading(false);
    }
  };

  const AuthHeader = () => (
    <StyledView className="items-center mb-8">
      <StyledView className="w-20 h-20 bg-primary-500 rounded-full items-center justify-center mb-4">
        <Ionicons name="chatbubbles" size={40} color="white" />
      </StyledView>
      <StyledText className="text-3xl font-bold text-gray-900 mb-2">
        Nexus Personal AI
      </StyledText>
      <StyledText className="text-gray-600 text-center px-4">
        Your AI-powered content creation and automation assistant
      </StyledText>
    </StyledView>
  );

  const AuthForm = () => (
    <Card className="mb-6">
      <Card.Header 
        title={mode === 'signin' ? 'Sign In' : 'Create Account'} 
        subtitle={mode === 'signin' 
          ? 'Welcome back! Sign in to continue' 
          : 'Join thousands of creators using AI to grow their audience'
        }
      />
      <Card.Content>
        <StyledView className="space-y-4">
          {mode === 'signup' && (
            <Input
              label="Display Name"
              placeholder="Enter your full name"
              value={formData.displayName}
              onChangeText={(text) => setFormData(prev => ({ ...prev, displayName: text }))}
              error={errors.displayName}
              leftIcon={<Ionicons name="person" size={20} color="#6b7280" />}
            />
          )}

          <Input
            label="Email Address"
            placeholder="Enter your email"
            value={formData.email}
            onChangeText={(text) => setFormData(prev => ({ ...prev, email: text }))}
            error={errors.email}
            keyboardType="email-address"
            autoCapitalize="none"
            leftIcon={<Ionicons name="mail" size={20} color="#6b7280" />}
          />

          <Input
            label="Password"
            placeholder="Enter your password"
            value={formData.password}
            onChangeText={(text) => setFormData(prev => ({ ...prev, password: text }))}
            error={errors.password}
            secureTextEntry
            leftIcon={<Ionicons name="lock-closed" size={20} color="#6b7280" />}
          />

          {mode === 'signup' && (
            <Input
              label="Confirm Password"
              placeholder="Confirm your password"
              value={formData.confirmPassword}
              onChangeText={(text) => setFormData(prev => ({ ...prev, confirmPassword: text }))}
              error={errors.confirmPassword}
              secureTextEntry
              leftIcon={<Ionicons name="lock-closed" size={20} color="#6b7280" />}
            />
          )}

          <Button
            title={mode === 'signin' ? 'Sign In' : 'Create Account'}
            onPress={handleSubmit}
            loading={loading}
            className="mt-6"
          />

          {/* Uncomment when OAuth is implemented
          <StyledView className="flex-row items-center my-6">
            <StyledView className="flex-1 h-px bg-gray-300" />
            <StyledText className="px-4 text-gray-500">or continue with</StyledText>
            <StyledView className="flex-1 h-px bg-gray-300" />
          </StyledView>

          <Button
            title="Continue with Google"
            variant="outline"
            onPress={() => {}}
            icon={<Ionicons name="logo-google" size={16} color="#3b82f6" />}
            className="mb-3"
          />

          <Button
            title="Continue with LinkedIn"
            variant="outline"
            onPress={() => {}}
            icon={<Ionicons name="logo-linkedin" size={16} color="#3b82f6" />}
          />
          */}
        </StyledView>
      </Card.Content>
    </Card>
  );

  const AuthToggle = () => (
    <StyledTouchableOpacity
      onPress={() => {
        setMode(mode === 'signin' ? 'signup' : 'signin');
        setErrors({});
      }}
      className="items-center"
    >
      <StyledText className="text-gray-600">
        {mode === 'signin' ? "Don't have an account? " : "Already have an account? "}
        <StyledText className="text-primary-500 font-medium">
          {mode === 'signin' ? 'Sign up' : 'Sign in'}
        </StyledText>
      </StyledText>
    </StyledTouchableOpacity>
  );

  const Features = () => (
    <Card variant="outlined" className="mb-6">
      <Card.Content>
        <StyledText className="font-semibold text-gray-900 mb-4">
          What you'll get:
        </StyledText>
        <StyledView className="space-y-3">
          <StyledView className="flex-row items-center">
            <Ionicons name="checkmark-circle" size={20} color="#10b981" />
            <StyledText className="text-gray-700 ml-3 flex-1">
              AI-generated content drafts in your voice
            </StyledText>
          </StyledView>
          <StyledView className="flex-row items-center">
            <Ionicons name="checkmark-circle" size={20} color="#10b981" />
            <StyledText className="text-gray-700 ml-3 flex-1">
              Automated Notion organization
            </StyledText>
          </StyledView>
          <StyledView className="flex-row items-center">
            <Ionicons name="checkmark-circle" size={20} color="#10b981" />
            <StyledText className="text-gray-700 ml-3 flex-1">
              Smart scheduling and analytics
            </StyledText>
          </StyledView>
          <StyledView className="flex-row items-center">
            <Ionicons name="checkmark-circle" size={20} color="#10b981" />
            <StyledText className="text-gray-700 ml-3 flex-1">
              Personal AI consultation chat
            </StyledText>
          </StyledView>
        </StyledView>
      </Card.Content>
    </Card>
  );

  return (
    <StyledSafeAreaView className="flex-1 bg-gray-50">
      <StyledScrollView className="flex-1 px-4 py-8">
        <AuthHeader />
        <AuthForm />
        <AuthToggle />
        
        {mode === 'signup' && (
          <StyledView className="mt-8">
            <Features />
          </StyledView>
        )}
      </StyledScrollView>
    </StyledSafeAreaView>
  );
}