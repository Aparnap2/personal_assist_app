import { styled } from 'nativewind';
import React from 'react';
import { Text, TextInput, TextInputProps, View } from 'react-native';

const StyledView = styled(View);
const StyledText = styled(Text);
const StyledTextInput = styled(TextInput);

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
    <StyledView className={`${containerClassName}`}>
      {label && (
        <StyledText className="text-sm font-medium text-gray-700 mb-2">{label}</StyledText>
      )}
      
      <StyledView className="relative">
        {leftIcon && (
          <StyledView className="absolute left-3 top-1/2 -translate-y-1/2 z-10">
            {leftIcon}
          </StyledView>
        )}
        
        <StyledTextInput
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
          <StyledView className="absolute right-3 top-1/2 -translate-y-1/2 z-10">
            {rightIcon}
          </StyledView>
        )}
      </StyledView>
      
      {(error || helper) && (
        <StyledText className={`text-sm mt-1 ${hasError ? 'text-red-600' : 'text-gray-600'}`}>
          {error || helper}
        </StyledText>
      )}
    </StyledView>
  );
};

export default Input;