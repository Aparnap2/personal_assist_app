import React from 'react';
import { ActivityIndicator, Text, TouchableOpacity, View } from 'react-native';

interface ButtonProps {
  title: string;
  onPress: () => void;
  variant?: 'primary' | 'secondary' | 'outline' | 'danger' | 'success' | 'ghost';
  size?: 'xs' | 'sm' | 'md' | 'lg';
  loading?: boolean;
  disabled?: boolean;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
  className?: string;
  fullWidth?: boolean;
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
  fullWidth = false,
}) => {
  const getVariantStyles = () => {
    switch (variant) {
      case 'primary':
        return 'bg-primary-500 active:bg-primary-600 border border-primary-500 shadow-sm';
      case 'secondary':
        return 'bg-primary-50 active:bg-primary-100 border border-primary-200';
      case 'outline':
        return 'bg-transparent border border-gray-300 active:bg-gray-50';
      case 'danger':
        return 'bg-red-500 active:bg-red-600 border border-red-500 shadow-sm';
      case 'success':
        return 'bg-green-500 active:bg-green-600 border border-green-500 shadow-sm';
      case 'ghost':
        return 'bg-transparent border-0 active:bg-gray-100';
      default:
        return 'bg-primary-500 active:bg-primary-600 border border-primary-500 shadow-sm';
    }
  };

  const getSizeStyles = () => {
    switch (size) {
      case 'xs':
        return 'px-2 py-1';
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
        return 'text-gray-700';
      case 'secondary':
        return 'text-primary-700';
      case 'ghost':
        return 'text-primary-500';
      default:
        return 'text-white';
    }
  };

  const getTextSizeStyles = () => {
    switch (size) {
      case 'xs':
        return 'text-xs';
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

  const getLoadingColor = () => {
    switch (variant) {
      case 'outline':
      case 'ghost':
        return '#6b7280';
      case 'secondary':
        return '#6366f1';
      default:
        return 'white';
    }
  };

  const isDisabled = disabled || loading;

  return (
    <TouchableOpacity
      onPress={onPress}
      disabled={isDisabled}
      className={`
        ${getVariantStyles()}
        ${getSizeStyles()}
        rounded-lg
        flex-row
        items-center
        justify-center
        ${fullWidth ? 'w-full' : ''}
        ${isDisabled ? 'opacity-50' : ''}
        ${className}
      `}
    >
      {loading ? (
        <View className="flex-row items-center">
          <ActivityIndicator color={getLoadingColor()} size="small" />
          {title && (
            <Text
              className={`
                ${getTextVariantStyles()}
                ${getTextSizeStyles()}
                font-semibold
                ml-2
              `}
            >
              {title}
            </Text>
          )}
        </View>
      ) : (
        <View className="flex-row items-center justify-center">
          {icon && iconPosition === 'left' && (
            <View className={title ? "mr-2" : ""}>{icon}</View>
          )}
          {title && (
            <Text
              className={`
                ${getTextVariantStyles()}
                ${getTextSizeStyles()}
                font-semibold
              `}
            >
              {title}
            </Text>
          )}
          {icon && iconPosition === 'right' && (
            <View className={title ? "ml-2" : ""}>{icon}</View>
          )}
        </View>
      )}
    </TouchableOpacity>
  );
};

export default Button;