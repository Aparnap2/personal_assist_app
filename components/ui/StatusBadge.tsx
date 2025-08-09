import { styled } from 'nativewind';
import React from 'react';
import { Text, View } from 'react-native';

const StyledView = styled(View);
const StyledText = styled(Text);

interface StatusBadgeProps {
  status: 'pending' | 'approved' | 'rejected' | 'scheduled' | 'published' | 'flagged';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const StatusBadge: React.FC<StatusBadgeProps> = ({ status, size = 'md', className = '' }) => {
  const getStatusStyles = () => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 border-yellow-300';
      case 'approved':
        return 'bg-green-100 border-green-300';
      case 'rejected':
        return 'bg-red-100 border-red-300';
      case 'scheduled':
        return 'bg-blue-100 border-blue-300';
      case 'published':
        return 'bg-cyan-100 border-cyan-300';
      case 'flagged':
        return 'bg-orange-100 border-orange-300';
      default:
        return 'bg-gray-100 border-gray-300';
    }
  };

  const getTextColor = () => {
    switch (status) {
      case 'pending':
        return 'text-yellow-800';
      case 'approved':
        return 'text-green-800';
      case 'rejected':
        return 'text-red-800';
      case 'scheduled':
        return 'text-blue-800';
      case 'published':
        return 'text-cyan-800';
      case 'flagged':
        return 'text-orange-800';
      default:
        return 'text-gray-800';
    }
  };

  const getSizeStyles = () => {
    switch (size) {
      case 'sm':
        return 'px-2 py-1';
      case 'md':
        return 'px-3 py-1';
      case 'lg':
        return 'px-4 py-2';
      default:
        return 'px-3 py-1';
    }
  };

  const getTextSize = () => {
    switch (size) {
      case 'sm':
        return 'text-xs';
      case 'md':
        return 'text-sm';
      case 'lg':
        return 'text-base';
      default:
        return 'text-sm';
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'pending':
        return 'Pending';
      case 'approved':
        return 'Approved';
      case 'rejected':
        return 'Rejected';
      case 'scheduled':
        return 'Scheduled';
      case 'published':
        return 'Published';
      case 'flagged':
        return 'Flagged';
      default:
        return status;
    }
  };

  return (
    <StyledView
      className={`
        ${getStatusStyles()}
        ${getSizeStyles()}
        rounded-full
        border
        ${className}
      `}
    >
      <StyledText
        className={`
          ${getTextColor()}
          ${getTextSize()}
          font-medium
          text-center
        `}
      >
        {getStatusText()}
      </StyledText>
    </StyledView>
  );
};

export default StatusBadge;