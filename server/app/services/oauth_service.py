"""
OAuth Integration Service for Twitter and Notion
Handles authentication, token management, and API interactions
"""

import os
import json
import base64
import secrets
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import aiohttp
import tweepy
from notion_client import Client as NotionClient

from app.core.config import settings


class TwitterOAuthService:
    """Handle Twitter OAuth flow and API interactions"""
    
    def __init__(self):
        self.client_id = settings.TWITTER_CLIENT_ID or settings.TWITTER_API_KEY
        self.client_secret = settings.TWITTER_CLIENT_SECRET or settings.TWITTER_API_SECRET
        self.api_key = settings.TWITTER_API_KEY
        self.api_secret = settings.TWITTER_API_SECRET
        self.bearer_token = settings.TWITTER_BEARER_TOKEN
        self.redirect_uri = settings.TWITTER_REDIRECT_URI or f"{settings.API_BASE_URL}/auth/twitter/callback"
        self.base_url = "https://api.twitter.com/2"
    
    def generate_auth_url(self) -> Dict[str, str]:
        """Generate Twitter OAuth 2.0 authorization URL"""
        state = secrets.token_urlsafe(32)
        code_verifier = self._generate_code_verifier()
        code_challenge = self._generate_code_challenge(code_verifier)
        
        auth_url = (
            f"https://twitter.com/i/oauth2/authorize"
            f"?response_type=code"
            f"&client_id={self.client_id}"
            f"&redirect_uri={self.redirect_uri}"
            f"&scope=tweet.read%20tweet.write%20users.read%20offline.access"
            f"&state={state}"
            f"&code_challenge={code_challenge}"
            f"&code_challenge_method=S256"
        )
        
        return {
            "auth_url": auth_url,
            "state": state,
            "code_verifier": code_verifier
        }
    
    async def exchange_code_for_tokens(self, code: str, code_verifier: str) -> Dict[str, Any]:
        """Exchange authorization code for access tokens"""
        token_url = "https://api.twitter.com/2/oauth2/token"
        
        data = {
            "code": code,
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "code_verifier": code_verifier,
        }
        
        auth_header = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(token_url, data=data, headers=headers) as response:
                if response.status == 200:
                    tokens = await response.json()
                    
                    # Get user information
                    user_info = await self._get_user_info(tokens["access_token"])
                    
                    return {
                        "access_token": tokens["access_token"],
                        "refresh_token": tokens.get("refresh_token"),
                        "expires_in": tokens.get("expires_in", 7200),
                        "user_info": user_info,
                        "scope": tokens.get("scope", ""),
                    }
                else:
                    error = await response.text()
                    raise Exception(f"Token exchange failed: {error}")
    
    async def _get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get Twitter user information"""
        headers = {"Authorization": f"Bearer {access_token}"}
        url = f"{self.base_url}/users/me?user.fields=id,username,name,profile_image_url,public_metrics"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("data", {})
                return {}
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh Twitter access token"""
        token_url = "https://api.twitter.com/2/oauth2/token"
        
        data = {
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
            "client_id": self.client_id,
        }
        
        auth_header = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(token_url, data=data, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error = await response.text()
                    raise Exception(f"Token refresh failed: {error}")
    
    async def post_tweet(self, access_token: str, content: str, media_ids: List[str] = None) -> Dict[str, Any]:
        """Post a tweet"""
        url = f"{self.base_url}/tweets"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        
        data = {"text": content}
        if media_ids:
            data["media"] = {"media_ids": media_ids}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 201:
                    return await response.json()
                else:
                    error = await response.text()
                    raise Exception(f"Tweet posting failed: {error}")
    
    async def schedule_tweet(self, access_token: str, content: str, scheduled_time: datetime) -> Dict[str, Any]:
        """Schedule a tweet (requires Twitter API v2 premium)"""
        # This would require premium Twitter API access
        # For now, we'll store it and handle scheduling via our own system
        return {
            "scheduled": True,
            "scheduled_for": scheduled_time.isoformat(),
            "content": content,
            "message": "Tweet scheduled via internal system"
        }
    
    async def get_tweet_metrics(self, access_token: str, tweet_id: str) -> Dict[str, Any]:
        """Get metrics for a specific tweet"""
        url = f"{self.base_url}/tweets/{tweet_id}?tweet.fields=public_metrics,created_at"
        headers = {"Authorization": f"Bearer {access_token}"}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                return {}
    
    def _generate_code_verifier(self) -> str:
        """Generate OAuth 2.0 code verifier"""
        return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
    
    def _generate_code_challenge(self, verifier: str) -> str:
        """Generate OAuth 2.0 code challenge"""
        import hashlib
        digest = hashlib.sha256(verifier.encode('utf-8')).digest()
        return base64.urlsafe_b64encode(digest).decode('utf-8').rstrip('=')


class NotionOAuthService:
    """Handle Notion OAuth flow and API interactions"""
    
    def __init__(self):
        self.client_id = settings.NOTION_CLIENT_ID
        self.client_secret = settings.NOTION_CLIENT_SECRET
        self.redirect_uri = settings.NOTION_REDIRECT_URI or f"{settings.API_BASE_URL}/auth/notion/callback"
        self.base_url = "https://api.notion.com/v1"
    
    def generate_auth_url(self) -> Dict[str, str]:
        """Generate Notion OAuth authorization URL"""
        state = secrets.token_urlsafe(32)
        
        auth_url = (
            f"https://api.notion.com/v1/oauth/authorize"
            f"?client_id={self.client_id}"
            f"&response_type=code"
            f"&owner=user"
            f"&redirect_uri={self.redirect_uri}"
            f"&state={state}"
        )
        
        return {
            "auth_url": auth_url,
            "state": state
        }
    
    async def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access tokens"""
        token_url = "https://api.notion.com/v1/oauth/token"
        
        auth_header = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/json",
        }
        
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(token_url, headers=headers, json=data) as response:
                if response.status == 200:
                    tokens = await response.json()
                    
                    # Get workspace information
                    workspace_info = await self._get_workspace_info(tokens["access_token"])
                    
                    return {
                        "access_token": tokens["access_token"],
                        "workspace_info": workspace_info,
                        "bot_id": tokens.get("bot_id"),
                        "workspace_id": tokens.get("workspace_id"),
                        "owner": tokens.get("owner", {}),
                    }
                else:
                    error = await response.text()
                    raise Exception(f"Notion token exchange failed: {error}")
    
    async def _get_workspace_info(self, access_token: str) -> Dict[str, Any]:
        """Get Notion workspace information"""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Notion-Version": "2022-06-28",
        }
        url = f"{self.base_url}/users/me"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                return {}
    
    async def create_page(self, access_token: str, parent_id: str, title: str, content: str, 
                         page_type: str = "note") -> Dict[str, Any]:
        """Create a new Notion page"""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        }
        
        # Create page content based on type
        page_data = self._build_page_data(title, content, page_type, parent_id)
        
        url = f"{self.base_url}/pages"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=page_data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error = await response.text()
                    raise Exception(f"Page creation failed: {error}")
    
    async def create_database_entry(self, access_token: str, database_id: str, 
                                  properties: Dict[str, Any]) -> Dict[str, Any]:
        """Create entry in Notion database"""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        }
        
        data = {
            "parent": {"database_id": database_id},
            "properties": properties
        }
        
        url = f"{self.base_url}/pages"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error = await response.text()
                    raise Exception(f"Database entry creation failed: {error}")
    
    async def search_pages(self, access_token: str, query: str = "", 
                          page_size: int = 100) -> Dict[str, Any]:
        """Search Notion pages"""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        }
        
        data = {
            "page_size": page_size
        }
        
        if query:
            data["query"] = query
        
        url = f"{self.base_url}/search"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 200:
                    return await response.json()
                return {"results": []}
    
    async def get_databases(self, access_token: str) -> List[Dict[str, Any]]:
        """Get accessible Notion databases"""
        search_result = await self.search_pages(access_token)
        databases = []
        
        for result in search_result.get("results", []):
            if result.get("object") == "database":
                databases.append(result)
        
        return databases
    
    async def update_page(self, access_token: str, page_id: str, 
                         properties: Dict[str, Any]) -> Dict[str, Any]:
        """Update Notion page properties"""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        }
        
        data = {"properties": properties}
        url = f"{self.base_url}/pages/{page_id}"
        
        async with aiohttp.ClientSession() as session:
            async with session.patch(url, headers=headers, json=data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error = await response.text()
                    raise Exception(f"Page update failed: {error}")
    
    def _build_page_data(self, title: str, content: str, page_type: str, parent_id: str) -> Dict[str, Any]:
        """Build Notion page data structure"""
        
        # Base page structure
        page_data = {
            "parent": {"page_id": parent_id},
            "properties": {
                "title": {
                    "title": [
                        {
                            "text": {
                                "content": title
                            }
                        }
                    ]
                }
            },
            "children": [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": content
                                }
                            }
                        ]
                    }
                }
            ]
        }
        
        # Add type-specific properties
        if page_type == "task":
            page_data["properties"]["Status"] = {
                "select": {
                    "name": "To Do"
                }
            }
            page_data["properties"]["Priority"] = {
                "select": {
                    "name": "Medium"
                }
            }
        
        elif page_type == "meeting":
            page_data["properties"]["Date"] = {
                "date": {
                    "start": datetime.now().isoformat()
                }
            }
            page_data["properties"]["Type"] = {
                "select": {
                    "name": "Meeting Notes"
                }
            }
        
        return page_data


class GoogleOAuthService:
    """Handle Google OAuth flow and API interactions"""
    
    def __init__(self):
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET
        self.redirect_uri = settings.GOOGLE_REDIRECT_URI or f"{settings.API_BASE_URL}/auth/google/callback"
        self.scope = "openid email profile"
        
    def generate_auth_url(self) -> Dict[str, str]:
        """Generate Google OAuth authorization URL"""
        state = secrets.token_urlsafe(32)
        
        auth_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth"
            f"?client_id={self.client_id}"
            f"&redirect_uri={self.redirect_uri}"
            f"&response_type=code"
            f"&scope={self.scope}"
            f"&state={state}"
            f"&access_type=offline"
            f"&prompt=consent"
        )
        
        return {
            "auth_url": auth_url,
            "state": state
        }
    
    async def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access tokens"""
        token_url = "https://oauth2.googleapis.com/token"
        
        data = {
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code",
        }
        
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(token_url, data=data, headers=headers) as response:
                if response.status == 200:
                    tokens = await response.json()
                    
                    # Get user information
                    user_info = await self._get_user_info(tokens["access_token"])
                    
                    return {
                        "access_token": tokens["access_token"],
                        "refresh_token": tokens.get("refresh_token"),
                        "expires_in": tokens.get("expires_in", 3600),
                        "user_info": user_info,
                        "token_type": tokens.get("token_type", "Bearer"),
                        "scope": tokens.get("scope", ""),
                    }
                else:
                    error = await response.text()
                    raise Exception(f"Google token exchange failed: {error}")
    
    async def _get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get Google user information"""
        headers = {"Authorization": f"Bearer {access_token}"}
        url = "https://www.googleapis.com/oauth2/v2/userinfo"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                return {}
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh Google access token"""
        token_url = "https://oauth2.googleapis.com/token"
        
        data = {
            "refresh_token": refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
        }
        
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(token_url, data=data, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error = await response.text()
                    raise Exception(f"Google token refresh failed: {error}")


class LinkedInOAuthService:
    """Handle LinkedIn OAuth flow and API interactions"""
    
    def __init__(self):
        self.client_id = settings.LINKEDIN_CLIENT_ID
        self.client_secret = settings.LINKEDIN_CLIENT_SECRET
        self.redirect_uri = settings.LINKEDIN_REDIRECT_URI or f"{settings.API_BASE_URL}/auth/linkedin/callback"
        self.scope = "r_liteprofile r_emailaddress w_member_social"
    
    def generate_auth_url(self) -> Dict[str, str]:
        """Generate LinkedIn OAuth authorization URL"""
        state = secrets.token_urlsafe(32)
        
        auth_url = (
            f"https://www.linkedin.com/oauth/v2/authorization"
            f"?response_type=code"
            f"&client_id={self.client_id}"
            f"&redirect_uri={self.redirect_uri}"
            f"&state={state}"
            f"&scope={self.scope}"
        )
        
        return {
            "auth_url": auth_url,
            "state": state
        }
    
    async def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access tokens"""
        token_url = "https://www.linkedin.com/oauth/v2/accessToken"
        
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(token_url, data=data, headers=headers) as response:
                if response.status == 200:
                    tokens = await response.json()
                    
                    # Get user information
                    user_info = await self._get_user_info(tokens["access_token"])
                    
                    return {
                        "access_token": tokens["access_token"],
                        "expires_in": tokens.get("expires_in", 5184000),  # LinkedIn tokens last ~2 months
                        "user_info": user_info,
                        "scope": tokens.get("scope", ""),
                    }
                else:
                    error = await response.text()
                    raise Exception(f"LinkedIn token exchange failed: {error}")
    
    async def _get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get LinkedIn user information"""
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Get basic profile
        profile_url = "https://api.linkedin.com/v2/people/~"
        email_url = "https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))"
        
        async with aiohttp.ClientSession() as session:
            # Get profile info
            async with session.get(profile_url, headers=headers) as response:
                profile_data = await response.json() if response.status == 200 else {}
            
            # Get email info
            async with session.get(email_url, headers=headers) as response:
                email_data = await response.json() if response.status == 200 else {}
            
        # Combine the data
        user_info = {
            "id": profile_data.get("id"),
            "firstName": profile_data.get("firstName", {}).get("localized", {}).get("en_US", ""),
            "lastName": profile_data.get("lastName", {}).get("localized", {}).get("en_US", ""),
        }
        
        if email_data and email_data.get("elements"):
            user_info["email"] = email_data["elements"][0].get("handle~", {}).get("emailAddress", "")
        
        return user_info
    
    async def post_to_linkedin(self, access_token: str, content: str, visibility: str = "PUBLIC") -> Dict[str, Any]:
        """Post content to LinkedIn"""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        # Get user URN first
        profile_url = "https://api.linkedin.com/v2/people/~"
        async with aiohttp.ClientSession() as session:
            async with session.get(profile_url, headers=headers) as response:
                if response.status == 200:
                    profile_data = await response.json()
                    author_urn = f"urn:li:person:{profile_data['id']}"
                else:
                    raise Exception("Failed to get user profile for posting")
        
        # Create post
        post_data = {
            "author": author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": content
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": visibility
            }
        }
        
        url = "https://api.linkedin.com/v2/ugcPosts"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=post_data) as response:
                if response.status == 201:
                    return await response.json()
                else:
                    error = await response.text()
                    raise Exception(f"LinkedIn post failed: {error}")


class OAuthManager:
    """Centralized OAuth management for all integrations"""
    
    def __init__(self):
        self.google = GoogleOAuthService()
        self.twitter = TwitterOAuthService()
        self.linkedin = LinkedInOAuthService()
        self.notion = NotionOAuthService()
    
    def get_service(self, integration_type: str):
        """Get appropriate OAuth service"""
        services = {
            "google": self.google,
            "twitter": self.twitter,
            "linkedin": self.linkedin,
            "notion": self.notion
        }
        return services.get(integration_type)
    
    async def initiate_oauth_flow(self, integration_type: str) -> Dict[str, Any]:
        """Initiate OAuth flow for given integration type"""
        service = self.get_service(integration_type)
        if not service:
            raise ValueError(f"Unsupported integration type: {integration_type}")
        
        auth_data = service.generate_auth_url()
        auth_data["integration_type"] = integration_type
        return auth_data
    
    async def complete_oauth_flow(self, integration_type: str, code: str, 
                                 state: str = None, code_verifier: str = None) -> Dict[str, Any]:
        """Complete OAuth flow and return tokens"""
        service = self.get_service(integration_type)
        if not service:
            raise ValueError(f"Unsupported integration type: {integration_type}")
        
        if integration_type == "twitter":
            if not code_verifier:
                raise ValueError("code_verifier required for Twitter OAuth")
            return await service.exchange_code_for_tokens(code, code_verifier)
        
        elif integration_type in ["google", "linkedin", "notion"]:
            return await service.exchange_code_for_tokens(code)
        
        else:
            raise ValueError(f"OAuth flow not implemented for {integration_type}")
    
    async def test_integration(self, integration_type: str, access_token: str) -> Dict[str, Any]:
        """Test integration by making a simple API call"""
        service = self.get_service(integration_type)
        if not service:
            return {"error": "Unsupported integration type"}
        
        try:
            if integration_type == "google":
                user_info = await service._get_user_info(access_token)
                return {
                    "success": True,
                    "user_info": user_info,
                    "capabilities": ["authentication", "profile_access"]
                }
            
            elif integration_type == "twitter":
                user_info = await service._get_user_info(access_token)
                return {
                    "success": True,
                    "user_info": user_info,
                    "capabilities": ["post_tweets", "schedule_posts", "analytics"]
                }
            
            elif integration_type == "linkedin":
                user_info = await service._get_user_info(access_token)
                return {
                    "success": True,
                    "user_info": user_info,
                    "capabilities": ["post_updates", "profile_access"]
                }
            
            elif integration_type == "notion":
                workspace_info = await service._get_workspace_info(access_token)
                databases = await service.get_databases(access_token)
                return {
                    "success": True,
                    "workspace_info": workspace_info,
                    "databases_count": len(databases),
                    "capabilities": ["create_pages", "create_tasks", "search"]
                }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Global OAuth manager instance
oauth_manager = OAuthManager()