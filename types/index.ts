// User Types
export interface User {
  id: string;
  email: string;
  displayName: string;
  photoURL?: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface UserProfile {
  userId: string;
  goals: string[];
  themes: string[];
  voiceProfile?: VoiceProfile;
  integrations: Integration[];
  preferences: UserPreferences;
}

// Voice Profile Types
export interface VoiceProfile {
  id: string;
  samples: string[];
  tone: VoiceTone;
  style: VoiceStyle;
  embedding?: number[];
  createdAt: Date;
  updatedAt: Date;
}

export interface VoiceTone {
  formal: number; // 0-100
  punchy: number; // 0-100
  contrarian: number; // 0-100
}

export interface VoiceStyle {
  personality: string[];
  vocabulary: string[];
  structure: string[];
}

// Content Types
export interface Draft {
  id: string;
  userId: string;
  content: string;
  platform: 'twitter' | 'linkedin';
  status: 'pending' | 'approved' | 'rejected' | 'scheduled' | 'published';
  variants?: string[];
  scheduledFor?: Date;
  bestTimeScore?: number;
  best_time_score?: number; // Alternative naming
  moderationStatus: 'pending' | 'approved' | 'flagged';
  themes?: string[];
  posting_recommendations?: {
    best_time: string;
    confidence_score: number;
    reasoning: string;
  };
  readabilityScore?: number;
  sentimentScore?: {
    positive: number;
    negative: number;
    compound: number;
  };
  hookStrength?: {
    score: number;
    indicators: {
      question: boolean;
      curiosity_gap: boolean;
      urgency: boolean;
      controversy: boolean;
      personal_story: boolean;
    };
  };
  personalizationScore?: number;
  optimizationSuggestions?: string[];
  engagementPrediction?: {
    likes: number;
    shares: number;
    comments: number;
    reach_estimate: number;
  };
  createdAt: Date;
  updatedAt: Date;
}

export interface Post {
  id: string;
  draftId: string;
  userId: string;
  platform: 'twitter' | 'linkedin';
  content: string;
  publishedAt: Date;
  engagement: EngagementMetrics;
  themes: string[];
}

export interface EngagementMetrics {
  likes: number;
  shares: number;
  comments: number;
  impressions: number;
  clicks: number;
  score: number; // Calculated engagement score
}

// Integration Types
export interface Integration {
  id: string;
  type: 'twitter' | 'linkedin' | 'notion';
  status: 'connected' | 'disconnected' | 'error';
  credentials: any; // Encrypted tokens
  permissions: string[];
  connectedAt: Date;
  lastSyncAt?: Date;
}

// Notion Types
export interface NotionPage {
  id: string;
  userId: string;
  notionPageId: string;
  title: string;
  type: 'meeting' | 'task' | 'note' | 'project';
  template: string;
  tags: string[];
  createdAt: Date;
  updatedAt: Date;
}

export interface Task {
  id: string;
  userId: string;
  title: string;
  description?: string;
  status: 'todo' | 'in-progress' | 'done' | 'cancelled';
  priority: 'low' | 'medium' | 'high';
  dueDate?: Date;
  notionTaskId?: string;
  createdAt: Date;
  updatedAt: Date;
}

// Consultation Types
export interface ChatMessage {
  id: string;
  userId: string;
  role: 'user' | 'assistant';
  content: string;
  actions?: ChatAction[];
  timestamp: Date;
}

export interface ChatAction {
  type: 'generate_draft' | 'create_task' | 'create_note' | 'schedule_post';
  label: string;
  data: any;
}

// Feedback Types
export interface Feedback {
  id: string;
  userId: string;
  type: 'draft' | 'consultation' | 'general';
  rating: 1 | 2 | 3 | 4 | 5;
  comment?: string;
  context: any; // Related data (draftId, chatId, etc.)
  createdAt: Date;
}

// Analytics Types
export interface AnalyticsData {
  userId: string;
  timeRange: 'week' | 'month' | 'quarter';
  draftsGenerated: number;
  draftsApproved: number;
  postsPublished: number;
  engagementGrowth: number;
  timeSaved: number; // in minutes
  approvalRate: number; // percentage
  topThemes: string[];
  bestPerformingContent: Post[];
}

// User Preferences
export interface UserPreferences {
  notifications: {
    drafts: boolean;
    approvals: boolean;
    analytics: boolean;
    engagement: boolean;
  };
  posting: {
    autoApprove: boolean;
    bestTimeOnly: boolean;
    requireModeration: boolean;
  };
  consultation: {
    proactive: boolean;
    frequency: 'daily' | 'weekly' | 'monthly';
  };
}

// API Response Types
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

// Navigation Types (Expo Router)
export type RootStackParamList = {
  '(tabs)': undefined;
  onboarding: undefined;
  auth: undefined;
  draft: { draftId: string };
  chat: undefined;
  settings: undefined;
};

export type TabParamList = {
  index: undefined;
  drafts: undefined;
  chat: undefined;
  notion: undefined;
  analytics: undefined;
};