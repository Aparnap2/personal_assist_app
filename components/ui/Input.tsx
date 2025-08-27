import React from 'react';
import { Text, TextInput, TextInputProps, View } from 'react-native';

interface InputProps extends TextInputProps {
  label?: string;
  error?: string;
  helper?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  containerClassName?: string;
  inputClassName?: string;
}

const Input: React.FC<InputProps> = ({
  label,
  error,
  helper,
  leftIcon,
  rightIcon,
  containerClassName = '',
  inputClassName = '',
  ...textInputProps
}) => {
  const hasError = !!error;

  return (
    <View className={`${containerClassName}`}>
      {label && (
        <Text className="text-sm font-medium text-gray-700 mb-2">{label}</Text>
      )}
      
      <View className="relative">
        {leftIcon && (
          <View className="absolute left-3 top-1/2 -translate-y-1/2 z-10">
            {leftIcon}
          </View>
        )}
        
        <TextInput
          className={`
            w-full
            px-4
            py-3
            border
            rounded-lg
            text-gray-900
            placeholder:text-gray-500
            ${hasError ? 'border-red-300 focus:border-red-500' : 'border-gray-300 focus:border-primary-500'}
            ${leftIcon ? 'pl-10' : ''}
            ${rightIcon ? 'pr-10' : ''}
            ${inputClassName}
          `}
          {...textInputProps}
        />
        
        {rightIcon && (
          <View className="absolute right-3 top-1/2 -translate-y-1/2 z-10">
            {rightIcon}
          </View>
        )}
      </View>
      
      {(error || helper) && (
        <Text className={`text-sm mt-1 ${hasError ? 'text-red-600' : 'text-gray-600'}`}>
          {error || helper}
        </Text>
      )}
    </View>
  );
};

export default Input;