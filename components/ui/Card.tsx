import { styled } from 'nativewind';
import React from 'react';
import { Text, TouchableOpacity, View } from 'react-native';

const StyledView = styled(View);
const StyledText = styled(Text);
const StyledTouchableOpacity = styled(TouchableOpacity);

interface CardProps {
  children: React.ReactNode;
  className?: string;
  onPress?: () => void;
  variant?: 'default' | 'elevated' | 'outlined';
}

interface CardHeaderProps {
  title: string;
  subtitle?: string;
  action?: React.ReactNode;
  className?: string;
}

interface CardContentProps {
  children: React.ReactNode;
  className?: string;
}

interface CardFooterProps {
  children: React.ReactNode;
  className?: string;
}

const getCardVariantStyles = (variant: string) => {
  switch (variant) {
    case 'elevated':
      return 'bg-white shadow-lg shadow-black/10';
    case 'outlined':
      return 'bg-white border border-gray-200';
    default:
      return 'bg-white shadow-md shadow-black/5';
  }
};

const Card: React.FC<CardProps> & {
  Header: React.FC<CardHeaderProps>;
  Content: React.FC<CardContentProps>;
  Footer: React.FC<CardFooterProps>;
} = ({ children, className = '', onPress, variant = 'default' }) => {
  const baseStyles = `${getCardVariantStyles(variant)} rounded-xl p-4 ${className}`;

  if (onPress) {
    return (
      <StyledTouchableOpacity onPress={onPress} className={`${baseStyles} active:opacity-95`}>
        {children}
      </StyledTouchableOpacity>
    );
  }

  return <StyledView className={baseStyles}>{children}</StyledView>;
};

const CardHeader: React.FC<CardHeaderProps> = ({ title, subtitle, action, className = '' }) => (
  <StyledView className={`flex-row items-start justify-between mb-3 ${className}`}>
    <StyledView className="flex-1">
      <StyledText className="text-lg font-semibold text-gray-900">{title}</StyledText>
      {subtitle && <StyledText className="text-sm text-gray-600 mt-1">{subtitle}</StyledText>}
    </StyledView>
    {action && <StyledView className="ml-3">{action}</StyledView>}
  </StyledView>
);

const CardContent: React.FC<CardContentProps> = ({ children, className = '' }) => (
  <StyledView className={`mb-3 ${className}`}>{children}</StyledView>
);

const CardFooter: React.FC<CardFooterProps> = ({ children, className = '' }) => (
  <StyledView className={`flex-row items-center justify-between ${className}`}>{children}</StyledView>
);

Card.Header = CardHeader;
Card.Content = CardContent;
Card.Footer = CardFooter;

export default Card;