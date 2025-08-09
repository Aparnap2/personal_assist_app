import os
import json
from typing import List, Dict, Any, Optional
import openai
from anthropic import Anthropic

from app.core.config import settings
from app.models.user import User, UserProfile

class AIService:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
        self.anthropic_client = Anthropic(api_key=settings.ANTHROPIC_API_KEY) if settings.ANTHROPIC_API_KEY else None
    
    async def generate_content_drafts(
        self, 
        user_profile: Optional[Dict[str, Any]] = None,
        prompt: Optional[str] = None,
        count: int = 5,
        platform: str = "twitter"
    ) -> List[Dict[str, Any]]:
        """Generate content drafts using AI"""
        
        # Build context from user profile
        context = self._build_user_context(user_profile)
        
        # Create the prompt
        system_prompt = self._create_content_generation_prompt(context, platform)
        user_prompt = prompt or "Generate engaging posts for my audience"
        
        try:
            # Use OpenAI for content generation
            if self.openai_client:
                response = await self._generate_with_openai(system_prompt, user_prompt, count)
            else:
                # Fallback to mock generation for demo
                response = self._mock_content_generation(count, platform)
            
            # Process and structure the response
            drafts = []
            for i, content in enumerate(response):
                draft = {
                    "content": content,
                    "platform": platform,
                    "variants": await self._generate_variants(content) if i < 2 else None,
                    "best_time_score": self._calculate_best_time_score(),
                    "themes": self._extract_themes(content, user_profile),
                    "moderation_status": "approved",  # Would run through moderation service
                }
                drafts.append(draft)
            
            return drafts
            
        except Exception as e:
            print(f"Error generating content: {e}")
            # Return mock content as fallback
            return self._mock_content_generation(count, platform)
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        user_profile: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate AI chat response with potential actions"""
        
        context = self._build_user_context(user_profile)
        system_prompt = self._create_chat_system_prompt(context)
        
        try:
            if self.openai_client:
                response = await self._chat_with_openai(system_prompt, messages)
            else:
                response = self._mock_chat_response(messages[-1]["content"])
            
            # Parse response for actions
            actions = self._extract_actions(response["content"])
            
            return {
                "content": response["content"],
                "actions": actions
            }
            
        except Exception as e:
            print(f"Error in chat completion: {e}")
            return self._mock_chat_response(messages[-1]["content"])
    
    async def analyze_voice_samples(self, samples: List[str]) -> Dict[str, Any]:
        """Analyze writing samples to create voice profile"""
        
        prompt = f"""
        Analyze these writing samples and create a voice profile:
        
        Samples:
        {chr(10).join(f"- {sample}" for sample in samples)}
        
        Return a JSON object with:
        - tone: {{formal: 0-100, punchy: 0-100, contrarian: 0-100}}
        - style: {{personality: [traits], vocabulary: [words], structure: [patterns]}}
        - summary: brief description of the writing voice
        """
        
        try:
            if self.openai_client:
                response = await self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3
                )
                
                content = response.choices[0].message.content
                return json.loads(content)
            else:
                # Mock voice analysis
                return {
                    "tone": {"formal": 40, "punchy": 70, "contrarian": 30},
                    "style": {
                        "personality": ["professional", "approachable", "insightful"],
                        "vocabulary": ["strategic", "innovative", "growth"],
                        "structure": ["clear", "concise", "actionable"]
                    },
                    "summary": "Professional yet approachable voice with focus on actionable insights"
                }
                
        except Exception as e:
            print(f"Error analyzing voice: {e}")
            return {"error": "Failed to analyze voice samples"}
    
    def _build_user_context(self, user_profile: Optional[Dict[str, Any]]) -> str:
        """Build context string from user profile"""
        if not user_profile:
            return "Generic content creator"
        
        goals = user_profile.get("goals", [])
        themes = user_profile.get("themes", [])
        voice_profile = user_profile.get("voice_profile", {})
        
        context_parts = []
        if goals:
            context_parts.append(f"Goals: {', '.join(goals)}")
        if themes:
            context_parts.append(f"Themes: {', '.join(themes)}")
        if voice_profile:
            tone = voice_profile.get("tone", {})
            style = voice_profile.get("style", {})
            if tone:
                context_parts.append(f"Voice tone - Formal: {tone.get('formal', 50)}%, Punchy: {tone.get('punchy', 50)}%, Contrarian: {tone.get('contrarian', 50)}%")
        
        return "; ".join(context_parts)
    
    def _create_content_generation_prompt(self, context: str, platform: str) -> str:
        """Create system prompt for content generation"""
        platform_specs = {
            "twitter": "280 characters max, engaging, hashtag-friendly",
            "linkedin": "professional, thought leadership, longer form allowed"
        }
        
        spec = platform_specs.get(platform, platform_specs["twitter"])
        
        return f"""
        You are a personal AI content creation assistant. Generate high-quality social media posts based on the user's profile and preferences.
        
        User Context: {context}
        Platform: {platform} ({spec})
        
        Guidelines:
        - Match the user's voice and style
        - Create engaging, valuable content
        - Include relevant hashtags when appropriate
        - Focus on the user's themes and goals
        - Make each post unique and compelling
        """
    
    def _create_chat_system_prompt(self, context: str) -> str:
        """Create system prompt for chat consultation"""
        return f"""
        You are a personal AI assistant specialized in content strategy and social media growth. 
        You provide concise, actionable advice and can suggest specific actions.
        
        User Context: {context}
        
        When appropriate, suggest actions like:
        - generate_draft: Create content drafts
        - create_task: Add tasks to Notion
        - schedule_post: Schedule content
        
        Be concise, decisive, and focus on actionable insights.
        """
    
    async def _generate_with_openai(self, system_prompt: str, user_prompt: str, count: int) -> List[str]:
        """Generate content using OpenAI"""
        response = await self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Generate {count} different posts about: {user_prompt}"}
            ],
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        # Parse the response to extract individual posts
        posts = [post.strip() for post in content.split('\n\n') if post.strip()]
        return posts[:count]
    
    async def _chat_with_openai(self, system_prompt: str, messages: List[Dict[str, str]]) -> Dict[str, str]:
        """Chat completion using OpenAI"""
        formatted_messages = [{"role": "system", "content": system_prompt}]
        formatted_messages.extend(messages)
        
        response = await self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=formatted_messages,
            temperature=0.6
        )
        
        return {"content": response.choices[0].message.content}
    
    def _mock_content_generation(self, count: int, platform: str) -> List[Dict[str, Any]]:
        """Mock content generation for demo purposes"""
        mock_contents = [
            "🚀 Just discovered a game-changing AI tool that's revolutionizing content creation. The future of marketing is here! #AI #ContentMarketing #Innovation",
            "Stop overthinking your content strategy. Start with these 3 simple questions: Who? What? Why? Everything else follows. #ContentStrategy #Marketing",
            "The best content doesn't sell. It serves. Focus on adding value first, and the sales will follow naturally. #ContentMarketing #Value",
            "Your audience doesn't want perfect content. They want authentic, helpful, and consistent content. Be real. #Authenticity #Content",
            "Content creation tip: Write for one person, not everyone. When you try to speak to everyone, you speak to no one. #ContentTips #Marketing"
        ]
        
        drafts = []
        for i in range(min(count, len(mock_contents))):
            draft = {
                "content": mock_contents[i],
                "platform": platform,
                "variants": None,
                "best_time_score": 85 + (i * 2),
                "themes": ["content marketing", "strategy"],
                "moderation_status": "approved"
            }
            drafts.append(draft)
        
        return drafts
    
    def _mock_chat_response(self, user_message: str) -> Dict[str, Any]:
        """Mock chat response for demo"""
        responses = {
            "generate": {
                "content": "I'd be happy to help you generate some content! Based on your profile, I can create posts that match your voice and focus on your key themes. Would you like me to create 5 draft posts for Twitter?",
                "actions": [
                    {"type": "generate_draft", "label": "Generate 5 Twitter Posts", "data": {"count": 5, "platform": "twitter"}}
                ]
            },
            "strategy": {
                "content": "For a strong content strategy, focus on these 3 pillars: 1) Know your audience deeply, 2) Create valuable, consistent content, 3) Engage authentically. I can help you create a content calendar and generate posts that align with these principles.",
                "actions": [
                    {"type": "create_task", "label": "Create Strategy Task", "data": {"title": "Content Strategy Review"}},
                    {"type": "generate_draft", "label": "Generate Strategy Posts", "data": {"prompt": "content strategy tips"}}
                ]
            },
            "default": {
                "content": "I'm here to help with your content creation and strategy! I can generate posts, help with planning, or answer questions about social media growth. What would you like to work on?",
                "actions": []
            }
        }
        
        # Simple keyword matching
        message_lower = user_message.lower()
        if "generate" in message_lower or "post" in message_lower:
            return responses["generate"]
        elif "strategy" in message_lower or "plan" in message_lower:
            return responses["strategy"]
        else:
            return responses["default"]
    
    async def _generate_variants(self, original_content: str) -> List[str]:
        """Generate variants of content"""
        # Mock variants for demo
        return [
            original_content.replace("!", "."),
            original_content.replace("🚀", "✨") if "🚀" in original_content else original_content + " 💡"
        ]
    
    def _calculate_best_time_score(self) -> float:
        """Calculate best time score (mock)"""
        import random
        return round(random.uniform(70, 95), 1)
    
    def _extract_themes(self, content: str, user_profile: Optional[Dict[str, Any]]) -> List[str]:
        """Extract themes from content"""
        themes = []
        if user_profile and user_profile.get("themes"):
            themes.extend(user_profile["themes"][:2])
        
        # Simple keyword-based theme extraction
        content_lower = content.lower()
        if "ai" in content_lower:
            themes.append("AI")
        if "marketing" in content_lower:
            themes.append("marketing")
        if "strategy" in content_lower:
            themes.append("strategy")
        
        return list(set(themes))
    
    def _extract_actions(self, response_content: str) -> List[Dict[str, Any]]:
        """Extract potential actions from AI response"""
        actions = []
        content_lower = response_content.lower()
        
        if "generate" in content_lower and ("post" in content_lower or "content" in content_lower):
            actions.append({
                "type": "generate_draft",
                "label": "Generate Drafts",
                "data": {"count": 5}
            })
        
        if "task" in content_lower or "todo" in content_lower:
            actions.append({
                "type": "create_task", 
                "label": "Create Task",
                "data": {"title": "Follow up on discussion"}
            })
        
        return actions

# Global AI service instance
ai_service = AIService()