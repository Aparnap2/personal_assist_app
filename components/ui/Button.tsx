import { styled } from 'nativewind';
import React from 'react';
import { ActivityIndicator, Text, TouchableOpacity, View } from 'react-native';

const StyledTouchableOpacity = styled(TouchableOpacity);
const StyledText = styled(Text);
const StyledView = styled(View);

interface ButtonProps {
  title: string;
  onPress: () => void;
  variant?: 'primary' | 'secondary' | 'outline' | 'danger' | 'success';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  disabled?: boolean;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
  className?: string;
}

const Button: React.FC<ButtonProps> = ({
  title,
  onPress,
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled = false,
  icon,
  iconPosition = 'left',
  className = '',
}) => {
  const getVariantStyles = () => {
    switch (variant) {
      case 'primary':
        return 'bg-primary-500 active:bg-primary-600';
      case 'secondary':
        return 'bg-gray-500 active:bg-gray-600';
      case 'outline':
        return 'bg-transparent border border-primary-500 active:bg-primary-50';
      case 'danger':
        return 'bg-red-500 active:bg-red-600';
      case 'success':
        return 'bg-green-500 active:bg-green-600';
      default:
        return 'bg-primary-500 active:bg-primary-600';
    }
  };

  const getSizeStyles = () => {
    switch (size) {
      case 'sm':
        return 'px-3 py-2';
      case 'md':
        return 'px-4 py-3';
      case 'lg':
        return 'px-6 py-4';
      default:
        return 'px-4 py-3';
    }
  };

  const getTextVariantStyles = () => {
    switch (variant) {
      case 'outline':
        return 'text-primary-500';
      default:
        return 'text-white';
    }
  };

  const getTextSizeStyles = () => {
    switch (size) {
      case 'sm':
        return 'text-sm';
      case 'md':
        return 'text-base';
      case 'lg':
        return 'text-lg';
      default:
        return 'text-base';
    }
  };

  const isDisabled = disabled || loading;

  return (
    <StyledTouchableOpacity
      onPress={onPress}
      disabled={isDisabled}
      className={`
        ${getVariantStyles()}
        ${getSizeStyles()}
        rounded-lg
        flex-row
        items-center
        justify-center
        ${isDisabled ? 'opacity-50' : ''}
        ${className}
      `}
    >
      {loading ? (
        <ActivityIndicator color="white" size="small" />
      ) : (
        <StyledView className="flex-row items-center justify-center">
          {icon && iconPosition === 'left' && (
            <StyledView className="mr-2">{icon}</StyledView>
          )}
          <StyledText
            className={`
              ${getTextVariantStyles()}
              ${getTextSizeStyles()}
              font-semibold
            `}
          >
            {title}
          </StyledText>
          {icon && iconPosition === 'right' && (
            <StyledView className="ml-2">{icon}</StyledView>
          )}
        </StyledView>
      )}
    </StyledTouchableOpacity>
  );
};

export default Button;