import React from 'react';
import { Text, TouchableOpacity, View } from 'react-native';

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
      <TouchableOpacity onPress={onPress} className={`${baseStyles} active:opacity-95`}>
        {children}
      </TouchableOpacity>
    );
  }

  return <View className={baseStyles}>{children}</View>;
};

const CardHeader: React.FC<CardHeaderProps> = ({ title, subtitle, action, className = '' }) => (
  <View className={`flex-row items-start justify-between mb-3 ${className}`}>
    <View className="flex-1">
      <Text className="text-lg font-semibold text-gray-900">{title}</Text>
      {subtitle && <Text className="text-sm text-gray-600 mt-1">{subtitle}</Text>}
    </View>
    {action && <View className="ml-3">{action}</View>}
  </View>
);

const CardContent: React.FC<CardContentProps> = ({ children, className = '' }) => (
  <View className={`mb-3 ${className}`}>{children}</View>
);

const CardFooter: React.FC<CardFooterProps> = ({ children, className = '' }) => (
  <View className={`flex-row items-center justify-between ${className}`}>{children}</View>
);

Card.Header = CardHeader;
Card.Content = CardContent;
Card.Footer = CardFooter;

export default Card;