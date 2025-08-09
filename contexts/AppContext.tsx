import React, { createContext, useContext, useReducer } from 'react';
import { apiService } from '../services/api';
import type { AnalyticsData, ChatMessage, Draft } from '../types';

interface AppState {
  drafts: Draft[];
  chatMessages: ChatMessage[];
  analytics: AnalyticsData | null;
  loading: {
    drafts: boolean;
    chat: boolean;
    analytics: boolean;
  };
  error: string | null;
}

type AppAction =
  | { type: 'SET_LOADING'; payload: { key: keyof AppState['loading']; value: boolean } }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'SET_DRAFTS'; payload: Draft[] }
  | { type: 'ADD_DRAFT'; payload: Draft }
  | { type: 'UPDATE_DRAFT'; payload: Draft }
  | { type: 'SET_CHAT_MESSAGES'; payload: ChatMessage[] }
  | { type: 'ADD_CHAT_MESSAGE'; payload: ChatMessage }
  | { type: 'SET_ANALYTICS'; payload: AnalyticsData };

const initialState: AppState = {
  drafts: [],
  chatMessages: [],
  analytics: null,
  loading: {
    drafts: false,
    chat: false,
    analytics: false,
  },
  error: null,
};

const appReducer = (state: AppState, action: AppAction): AppState => {
  switch (action.type) {
    case 'SET_LOADING':
      return {
        ...state,
        loading: { ...state.loading, [action.payload.key]: action.payload.value },
      };
    case 'SET_ERROR':
      return { ...state, error: action.payload };
    case 'SET_DRAFTS':
      return { ...state, drafts: action.payload };
    case 'ADD_DRAFT':
      return { ...state, drafts: [action.payload, ...state.drafts] };
    case 'UPDATE_DRAFT':
      return {
        ...state,
        drafts: state.drafts.map(draft =>
          draft.id === action.payload.id ? action.payload : draft
        ),
      };
    case 'SET_CHAT_MESSAGES':
      return { ...state, chatMessages: action.payload };
    case 'ADD_CHAT_MESSAGE':
      return { ...state, chatMessages: [...state.chatMessages, action.payload] };
    case 'SET_ANALYTICS':
      return { ...state, analytics: action.payload };
    default:
      return state;
  }
};

interface AppContextType {
  state: AppState;
  // Drafts
  loadDrafts: () => Promise<void>;
  generateDrafts: (prompt?: string) => Promise<void>;
  approveDraft: (draftId: string, scheduleTime?: Date) => Promise<void>;
  rejectDraft: (draftId: string, reason?: string) => Promise<void>;
  // Chat
  loadChatHistory: () => Promise<void>;
  sendMessage: (message: string) => Promise<void>;
  // Analytics
  loadAnalytics: (timeRange?: string) => Promise<void>;
}

const AppContext = createContext<AppContextType>({} as AppContextType);

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};

export const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(appReducer, initialState);

  const setLoading = (key: keyof AppState['loading'], value: boolean) => {
    dispatch({ type: 'SET_LOADING', payload: { key, value } });
  };

  const setError = (error: string | null) => {
    dispatch({ type: 'SET_ERROR', payload: error });
  };

  // Draft Management
  const loadDrafts = async () => {
    try {
      setLoading('drafts', true);
      setError(null);
      
      const response = await apiService.getDrafts();
      if (response.success && response.data) {
        dispatch({ type: 'SET_DRAFTS', payload: response.data });
      } else {
        setError(response.error || 'Failed to load drafts');
      }
    } catch (error) {
      setError('Failed to load drafts');
      console.error('Error loading drafts:', error);
    } finally {
      setLoading('drafts', false);
    }
  };

  const generateDrafts = async (prompt?: string) => {
    try {
      setLoading('drafts', true);
      setError(null);
      
      const response = await apiService.generateDrafts(prompt);
      if (response.success && response.data) {
        response.data.forEach(draft => {
          dispatch({ type: 'ADD_DRAFT', payload: draft });
        });
      } else {
        setError(response.error || 'Failed to generate drafts');
      }
    } catch (error) {
      setError('Failed to generate drafts');
      console.error('Error generating drafts:', error);
    } finally {
      setLoading('drafts', false);
    }
  };

  const approveDraft = async (draftId: string, scheduleTime?: Date) => {
    try {
      const response = await apiService.approveDraft(draftId, scheduleTime);
      if (response.success && response.data) {
        dispatch({ type: 'UPDATE_DRAFT', payload: response.data });
      } else {
        setError(response.error || 'Failed to approve draft');
      }
    } catch (error) {
      setError('Failed to approve draft');
      console.error('Error approving draft:', error);
    }
  };

  const rejectDraft = async (draftId: string, reason?: string) => {
    try {
      const response = await apiService.rejectDraft(draftId, reason);
      if (response.success && response.data) {
        dispatch({ type: 'UPDATE_DRAFT', payload: response.data });
      } else {
        setError(response.error || 'Failed to reject draft');
      }
    } catch (error) {
      setError('Failed to reject draft');
      console.error('Error rejecting draft:', error);
    }
  };

  // Chat Management
  const loadChatHistory = async () => {
    try {
      setLoading('chat', true);
      setError(null);
      
      const response = await apiService.getChatHistory();
      if (response.success && response.data) {
        dispatch({ type: 'SET_CHAT_MESSAGES', payload: response.data });
      } else {
        setError(response.error || 'Failed to load chat history');
      }
    } catch (error) {
      setError('Failed to load chat history');
      console.error('Error loading chat history:', error);
    } finally {
      setLoading('chat', false);
    }
  };

  const sendMessage = async (message: string) => {
    try {
      // Add user message immediately
      const userMessage: ChatMessage = {
        id: Date.now().toString(),
        userId: 'current-user',
        role: 'user',
        content: message,
        timestamp: new Date(),
      };
      dispatch({ type: 'ADD_CHAT_MESSAGE', payload: userMessage });
      
      // Send to API
      const response = await apiService.sendChatMessage(message);
      if (response.success && response.data) {
        dispatch({ type: 'ADD_CHAT_MESSAGE', payload: response.data });
      } else {
        setError(response.error || 'Failed to send message');
      }
    } catch (error) {
      setError('Failed to send message');
      console.error('Error sending message:', error);
    }
  };

  // Analytics
  const loadAnalytics = async (timeRange: string = 'week') => {
    try {
      setLoading('analytics', true);
      setError(null);
      
      const response = await apiService.getAnalytics(timeRange);
      if (response.success && response.data) {
        dispatch({ type: 'SET_ANALYTICS', payload: response.data });
      } else {
        setError(response.error || 'Failed to load analytics');
      }
    } catch (error) {
      setError('Failed to load analytics');
      console.error('Error loading analytics:', error);
    } finally {
      setLoading('analytics', false);
    }
  };

  const value = {
    state,
    loadDrafts,
    generateDrafts,
    approveDraft,
    rejectDraft,
    loadChatHistory,
    sendMessage,
    loadAnalytics,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};