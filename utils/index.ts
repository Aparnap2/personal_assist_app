export const formatDate = (date: Date): string => {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
};

export const formatTimeAgo = (date: Date): string => {
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (diffInSeconds < 60) return 'Just now';
  
  const diffInMinutes = Math.floor(diffInSeconds / 60);
  if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
  
  const diffInHours = Math.floor(diffInMinutes / 60);
  if (diffInHours < 24) return `${diffInHours}h ago`;
  
  const diffInDays = Math.floor(diffInHours / 24);
  if (diffInDays < 7) return `${diffInDays}d ago`;
  
  return formatDate(date);
};

export const calculateEngagementScore = (metrics: {
  likes: number;
  shares: number;
  comments: number;
  impressions: number;
}): number => {
  const { likes, shares, comments, impressions } = metrics;
  
  if (impressions === 0) return 0;
  
  // Weighted engagement calculation
  const engagementActions = likes + shares * 3 + comments * 5;
  return Math.round((engagementActions / impressions) * 100);
};

export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength - 3) + '...';
};

export const generateId = (): string => {
  return Math.random().toString(36).substring(2) + Date.now().toString(36);
};

export const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const capitalizeFirst = (text: string): string => {
  return text.charAt(0).toUpperCase() + text.slice(1);
};

export const getStatusColor = (status: string): string => {
  switch (status) {
    case 'pending':
      return '#f59e0b'; // yellow-500
    case 'approved':
      return '#10b981'; // green-500
    case 'rejected':
      return '#ef4444'; // red-500
    case 'scheduled':
      return '#3b82f6'; // blue-500
    case 'published':
      return '#06b6d4'; // cyan-500
    default:
      return '#6b7280'; // gray-500
  }
};

export const getBestPostingTimes = (): { hour: number; label: string; score: number }[] => {
  // Mock data for best posting times
  return [
    { hour: 9, label: '9:00 AM', score: 85 },
    { hour: 12, label: '12:00 PM', score: 92 },
    { hour: 15, label: '3:00 PM', score: 78 },
    { hour: 18, label: '6:00 PM', score: 89 },
    { hour: 20, label: '8:00 PM', score: 94 },
  ];
};

export const extractHashtags = (text: string): string[] => {
  const hashtagRegex = /#[\w]+/g;
  return text.match(hashtagRegex) || [];
};

export const extractMentions = (text: string): string[] => {
  const mentionRegex = /@[\w]+/g;
  return text.match(mentionRegex) || [];
};export const formatDate = (date: Date): string => {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
};

export const formatTimeAgo = (date: Date): string => {
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (diffInSeconds < 60) return 'Just now';
  
  const diffInMinutes = Math.floor(diffInSeconds / 60);
  if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
  
  const diffInHours = Math.floor(diffInMinutes / 60);
  if (diffInHours < 24) return `${diffInHours}h ago`;
  
  const diffInDays = Math.floor(diffInHours / 24);
  if (diffInDays < 7) return `${diffInDays}d ago`;
  
  return formatDate(date);
};

export const calculateEngagementScore = (metrics: {
  likes: number;
  shares: number;
  comments: number;
  impressions: number;
}): number => {
  const { likes, shares, comments, impressions } = metrics;
  
  if (impressions === 0) return 0;
  
  // Weighted engagement calculation
  const engagementActions = likes + shares * 3 + comments * 5;
  return Math.round((engagementActions / impressions) * 100);
};

export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength - 3) + '...';
};

export const generateId = (): string => {
  return Math.random().toString(36).substring(2) + Date.now().toString(36);
};

export const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const capitalizeFirst = (text: string): string => {
  return text.charAt(0).toUpperCase() + text.slice(1);
};

export const getStatusColor = (status: string): string => {
  switch (status) {
    case 'pending':
      return '#f59e0b'; // yellow-500
    case 'approved':
      return '#10b981'; // green-500
    case 'rejected':
      return '#ef4444'; // red-500
    case 'scheduled':
      return '#3b82f6'; // blue-500
    case 'published':
      return '#06b6d4'; // cyan-500
    default:
      return '#6b7280'; // gray-500
  }
};

export const getBestPostingTimes = (): { hour: number; label: string; score: number }[] => {
  // Mock data for best posting times
  return [
    { hour: 9, label: '9:00 AM', score: 85 },
    { hour: 12, label: '12:00 PM', score: 92 },
    { hour: 15, label: '3:00 PM', score: 78 },
    { hour: 18, label: '6:00 PM', score: 89 },
    { hour: 20, label: '8:00 PM', score: 94 },
  ];
};

export const extractHashtags = (text: string): string[] => {
  const hashtagRegex = /#[\w]+/g;
  return text.match(hashtagRegex) || [];
};

export const extractMentions = (text: string): string[] => {
  const mentionRegex = /@[\w]+/g;
  return text.match(mentionRegex) || [];
};