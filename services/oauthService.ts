/**
 * OAuth Service for Frontend Integration
 * Handles OAuth flows for various providers using environment variables
 */

import * as AuthSession from 'expo-auth-session';
import * as WebBrowser from 'expo-web-browser';

// Configure WebBrowser for OAuth
WebBrowser.maybeCompleteAuthSession();

export interface OAuthConfig {
  clientId: string;
  scopes: string[];
  redirectUri: string;
  responseType: string;
  additionalParameters?: Record<string, string>;
}

export interface OAuthTokens {
  accessToken: string;
  refreshToken?: string;
  expiresIn?: number;
  tokenType?: string;
  scope?: string;
}

export interface OAuthUser {
  id: string;
  email?: string;
  name?: string;
  picture?: string;
  [key: string]: any;
}

/**
 * Google OAuth Service
 */
export class GoogleOAuthService {
  private config: OAuthConfig;

  constructor() {
    this.config = {
      clientId: process.env.EXPO_PUBLIC_GOOGLE_CLIENT_ID || '',
      scopes: ['openid', 'profile', 'email'],
      redirectUri: AuthSession.makeRedirectUri({
        scheme: 'com.personalassist.app', // Update with your app scheme
        path: 'auth/google'
      }),
      responseType: AuthSession.ResponseType.Code,
      additionalParameters: {
        access_type: 'offline',
        prompt: 'consent',
      },
    };
  }

  async authenticate(): Promise<{ tokens: OAuthTokens; user: OAuthUser } | null> {
    try {
      const request = new AuthSession.AuthRequest(this.config);
      const discovery = await AuthSession.fetchDiscoveryAsync(
        'https://accounts.google.com/.well-known/openid_configuration'
      );

      const result = await request.promptAsync(discovery);
      
      if (result.type === 'success') {
        // Exchange code for tokens via your backend
        const tokens = await this.exchangeCodeForTokens(result.params.code);
        const user = await this.getUserInfo(tokens.accessToken);
        
        return { tokens, user };
      }
      
      return null;
    } catch (error) {
      console.error('Google OAuth error:', error);
      throw error;
    }
  }

  private async exchangeCodeForTokens(code: string): Promise<OAuthTokens> {
    const response = await fetch(`${process.env.EXPO_PUBLIC_API_BASE_URL}/auth/google/callback`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ code }),
    });

    if (!response.ok) {
      throw new Error('Failed to exchange code for tokens');
    }

    return response.json();
  }

  private async getUserInfo(accessToken: string): Promise<OAuthUser> {
    const response = await fetch('https://www.googleapis.com/oauth2/v2/userinfo', {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to fetch user info');
    }

    return response.json();
  }
}

/**
 * Twitter OAuth Service
 */
export class TwitterOAuthService {
  private clientId: string;
  private redirectUri: string;

  constructor() {
    this.clientId = process.env.EXPO_PUBLIC_TWITTER_CLIENT_ID || '';
    this.redirectUri = AuthSession.makeRedirectUri({
      scheme: 'com.personalassist.app',
      path: 'auth/twitter'
    });
  }

  async authenticate(): Promise<{ tokens: OAuthTokens; user: OAuthUser } | null> {
    try {
      // For Twitter OAuth 2.0, we need PKCE
      const codeVerifier = AuthSession.AuthRequest.makeRandomCodeChallenge();
      const codeChallenge = await AuthSession.AuthRequest.deriveChallengeAsync(
        AuthSession.CodeChallengeMethod.S256,
        codeVerifier
      );

      const request = new AuthSession.AuthRequest({
        clientId: this.clientId,
        scopes: ['tweet.read', 'tweet.write', 'users.read', 'offline.access'],
        redirectUri: this.redirectUri,
        responseType: AuthSession.ResponseType.Code,
        codeChallenge: codeChallenge.codeChallenge,
        codeChallengeMethod: AuthSession.CodeChallengeMethod.S256,
        additionalParameters: {
          state: AuthSession.AuthRequest.makeRandomState(),
        },
      });

      const authUrl = `https://twitter.com/i/oauth2/authorize?${new URLSearchParams({
        response_type: 'code',
        client_id: this.clientId,
        redirect_uri: this.redirectUri,
        scope: 'tweet.read tweet.write users.read offline.access',
        state: request.state || '',
        code_challenge: codeChallenge.codeChallenge,
        code_challenge_method: 'S256',
      }).toString()}`;

      const result = await WebBrowser.openAuthSessionAsync(authUrl, this.redirectUri);
      
      if (result.type === 'success') {
        const url = new URL(result.url);
        const code = url.searchParams.get('code');
        
        if (code) {
          const tokens = await this.exchangeCodeForTokens(code, codeVerifier);
          const user = await this.getUserInfo(tokens.accessToken);
          
          return { tokens, user };
        }
      }
      
      return null;
    } catch (error) {
      console.error('Twitter OAuth error:', error);
      throw error;
    }
  }

  private async exchangeCodeForTokens(code: string, codeVerifier: string): Promise<OAuthTokens> {
    const response = await fetch(`${process.env.EXPO_PUBLIC_API_BASE_URL}/auth/twitter/callback`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ code, code_verifier: codeVerifier }),
    });

    if (!response.ok) {
      throw new Error('Failed to exchange code for tokens');
    }

    return response.json();
  }

  private async getUserInfo(accessToken: string): Promise<OAuthUser> {
    const response = await fetch(`${process.env.EXPO_PUBLIC_API_BASE_URL}/twitter/user`, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to fetch user info');
    }

    return response.json();
  }
}

/**
 * LinkedIn OAuth Service
 */
export class LinkedInOAuthService {
  private config: OAuthConfig;

  constructor() {
    this.config = {
      clientId: process.env.EXPO_PUBLIC_LINKEDIN_CLIENT_ID || '',
      scopes: ['r_liteprofile', 'r_emailaddress', 'w_member_social'],
      redirectUri: AuthSession.makeRedirectUri({
        scheme: 'com.personalassist.app',
        path: 'auth/linkedin'
      }),
      responseType: AuthSession.ResponseType.Code,
    };
  }

  async authenticate(): Promise<{ tokens: OAuthTokens; user: OAuthUser } | null> {
    try {
      const authUrl = `https://www.linkedin.com/oauth/v2/authorization?${new URLSearchParams({
        response_type: 'code',
        client_id: this.config.clientId,
        redirect_uri: this.config.redirectUri,
        state: AuthSession.AuthRequest.makeRandomState(),
        scope: this.config.scopes.join(' '),
      }).toString()}`;

      const result = await WebBrowser.openAuthSessionAsync(authUrl, this.config.redirectUri);
      
      if (result.type === 'success') {
        const url = new URL(result.url);
        const code = url.searchParams.get('code');
        
        if (code) {
          const tokens = await this.exchangeCodeForTokens(code);
          const user = await this.getUserInfo(tokens.accessToken);
          
          return { tokens, user };
        }
      }
      
      return null;
    } catch (error) {
      console.error('LinkedIn OAuth error:', error);
      throw error;
    }
  }

  private async exchangeCodeForTokens(code: string): Promise<OAuthTokens> {
    const response = await fetch(`${process.env.EXPO_PUBLIC_API_BASE_URL}/auth/linkedin/callback`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ code }),
    });

    if (!response.ok) {
      throw new Error('Failed to exchange code for tokens');
    }

    return response.json();
  }

  private async getUserInfo(accessToken: string): Promise<OAuthUser> {
    const response = await fetch(`${process.env.EXPO_PUBLIC_API_BASE_URL}/linkedin/user`, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to fetch user info');
    }

    return response.json();
  }
}

/**
 * Centralized OAuth Manager
 */
export class OAuthManager {
  public google: GoogleOAuthService;
  public twitter: TwitterOAuthService;
  public linkedin: LinkedInOAuthService;

  constructor() {
    this.google = new GoogleOAuthService();
    this.twitter = new TwitterOAuthService();
    this.linkedin = new LinkedInOAuthService();
  }

  async authenticateWithProvider(provider: 'google' | 'twitter' | 'linkedin') {
    switch (provider) {
      case 'google':
        return this.google.authenticate();
      case 'twitter':
        return this.twitter.authenticate();
      case 'linkedin':
        return this.linkedin.authenticate();
      default:
        throw new Error(`Unsupported OAuth provider: ${provider}`);
    }
  }
}

// Export singleton instance
export const oauthManager = new OAuthManager();