import { EXPO_PUBLIC_API_BASE_URL, EXPO_PUBLIC_API_VERSION } from '@env';
import type { AnalyticsData, ApiResponse, ChatMessage, Draft, UserProfile } from '../types';

class ApiService {
  private baseURL: string;
  private token: string | null = null;

  constructor() {
    this.baseURL = `${EXPO_PUBLIC_API_BASE_URL}/${EXPO_PUBLIC_API_VERSION}`;
  }

  setAuthToken(token: string) {
    this.token = token;
  }

  private async request<T = any>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
        ...(this.token && { Authorization: `Bearer ${this.token}` }),
        ...options.headers,
      };

      const response = await fetch(`${this.baseURL}${endpoint}`, {
        ...options,
        headers,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('API Request failed:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  // Authentication
  async authenticateUser(firebaseToken: string): Promise<ApiResponse<{ token: string }>> {
    return this.request('/auth/verify', {
      method: 'POST',
      body: JSON.stringify({ firebaseToken }),
    });
  }

  // User Profile
  async getUserProfile(): Promise<ApiResponse<UserProfile>> {
    return this.request('/user/profile');
  }

  async updateUserProfile(profile: Partial<UserProfile>): Promise<ApiResponse<UserProfile>> {
    return this.request('/user/profile', {
      method: 'PUT',
      body: JSON.stringify(profile),
    });
  }

  // Voice Profile
  async analyzeVoiceSamples(samples: string[]): Promise<ApiResponse<any>> {
    return this.request('/voice/analyze', {
      method: 'POST',
      body: JSON.stringify({ samples }),
    });
  }

  // Content Generation
  async generateDrafts(prompt?: string, count: number = 5): Promise<ApiResponse<Draft[]>> {
    return this.request('/content/generate', {
      method: 'POST',
      body: JSON.stringify({ prompt, count }),
    });
  }

  async getDrafts(status?: string): Promise<ApiResponse<Draft[]>> {
    const query = status ? `?status=${status}` : '';
    return this.request(`/content/drafts${query}`);
  }

  async approveDraft(draftId: string, scheduleTime?: Date): Promise<ApiResponse<Draft>> {
    return this.request(`/content/drafts/${draftId}/approve`, {
      method: 'POST',
      body: JSON.stringify({ scheduleTime }),
    });
  }

  async rejectDraft(draftId: string, reason?: string): Promise<ApiResponse<Draft>> {
    return this.request(`/content/drafts/${draftId}/reject`, {
      method: 'POST',
      body: JSON.stringify({ reason }),
    });
  }

  // Chat/Consultation
  async sendChatMessage(message: string): Promise<ApiResponse<ChatMessage>> {
    return this.request('/chat/message', {
      method: 'POST',
      body: JSON.stringify({ message }),
    });
  }

  async getChatHistory(limit: number = 50): Promise<ApiResponse<ChatMessage[]>> {
    return this.request(`/chat/history?limit=${limit}`);
  }

  // Integrations
  async connectIntegration(type: string, authCode: string): Promise<ApiResponse<any>> {
    return this.request('/integrations/connect', {
      method: 'POST',
      body: JSON.stringify({ type, authCode }),
    });
  }

  async getIntegrations(): Promise<ApiResponse<any[]>> {
    return this.request('/integrations');
  }

  // Notion
  async createNotionPage(data: any): Promise<ApiResponse<any>> {
    return this.request('/notion/pages', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getNotionPages(): Promise<ApiResponse<any[]>> {
    return this.request('/notion/pages');
  }

  // Analytics
  async getAnalytics(timeRange: string = 'week'): Promise<ApiResponse<AnalyticsData>> {
    return this.request(`/analytics?range=${timeRange}`);
  }

  // Feedback
  async submitFeedback(feedback: any): Promise<ApiResponse<any>> {
    return this.request('/feedback', {
      method: 'POST',
      body: JSON.stringify(feedback),
    });
  }
}

export const apiService = new ApiService();
export default apiService;