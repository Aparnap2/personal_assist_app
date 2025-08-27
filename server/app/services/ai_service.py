import os
import json
import re
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import openai
from anthropic import Anthropic
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import asyncio
import aiohttp

from app.core.config import settings
from app.models.user import User, UserProfile

class AIService:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
        self.anthropic_client = Anthropic(api_key=settings.ANTHROPIC_API_KEY) if settings.ANTHROPIC_API_KEY else None
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        
        # Content performance learning data
        self.performance_patterns = {
            "high_engagement": {
                "time_patterns": ["09:00-11:00", "15:00-17:00", "19:00-21:00"],
                "content_patterns": ["question", "statistic", "story", "tip"],
                "hashtag_patterns": ["#AI", "#productivity", "#innovation"]
            },
            "content_themes": {
                "ai": {"engagement_multiplier": 1.3, "best_times": ["10:00", "16:00"]},
                "productivity": {"engagement_multiplier": 1.2, "best_times": ["09:00", "17:00"]},
                "strategy": {"engagement_multiplier": 1.1, "best_times": ["08:00", "14:00"]}
            }
        }
    
    async def generate_content_drafts(
        self, 
        user_profile: Optional[Dict[str, Any]] = None,
        prompt: Optional[str] = None,
        count: int = 5,
        platform: str = "twitter",
        performance_data: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Enhanced content generation with learning and optimization"""
        
        # Build enhanced context from user profile and performance data
        context = self._build_enhanced_context(user_profile, performance_data)
        
        # Create optimized prompts based on performance patterns
        system_prompt = self._create_intelligent_prompt(context, platform, performance_data)
        user_prompt = self._optimize_user_prompt(prompt, user_profile)
        
        try:
            # Generate with multiple strategies for diversity
            drafts_data = []
            
            if self.openai_client or self.anthropic_client:
                # Generate diverse content using different approaches
                base_content = await self._generate_with_ai(system_prompt, user_prompt, count)
                drafts_data = await self._enhance_generated_content(base_content, user_profile, platform)
            else:
                # Enhanced mock generation with patterns
                drafts_data = self._intelligent_mock_generation(count, platform, user_profile)
            
            # Add intelligence layer to each draft
            enhanced_drafts = []
            for i, draft_data in enumerate(drafts_data):
                enhanced_draft = await self._add_intelligence_layer(draft_data, user_profile, platform)
                enhanced_drafts.append(enhanced_draft)
            
            return enhanced_drafts
            
        except Exception as e:
            print(f"Error generating content: {e}")
            return self._intelligent_mock_generation(count, platform, user_profile)
    
    def _build_enhanced_context(self, user_profile: Dict[str, Any], performance_data: Dict[str, Any]) -> str:
        """Build enhanced context with performance insights"""
        base_context = self._build_user_context(user_profile)
        
        if not performance_data:
            return base_context
        
        # Add performance insights
        performance_insights = []
        
        top_themes = performance_data.get("top_performing_themes", [])
        if top_themes:
            performance_insights.append(f"High-performing themes: {', '.join(top_themes[:3])}")
        
        best_times = performance_data.get("best_posting_times", [])
        if best_times:
            performance_insights.append(f"Optimal posting times: {', '.join(best_times[:2])}")
        
        engagement_patterns = performance_data.get("engagement_patterns", [])
        if engagement_patterns:
            performance_insights.append(f"Effective content patterns: {', '.join(engagement_patterns[:2])}")
        
        if performance_insights:
            return f"{base_context}; Performance insights: {'; '.join(performance_insights)}"
        
        return base_context
    
    def _create_intelligent_prompt(self, context: str, platform: str, performance_data: Dict[str, Any]) -> str:
        """Create AI prompt optimized for performance patterns"""
        base_prompt = self._create_content_generation_prompt(context, platform)
        
        if not performance_data:
            return base_prompt
        
        # Add performance-based instructions
        performance_instructions = []
        
        if performance_data.get("high_engagement_patterns"):
            patterns = performance_data["high_engagement_patterns"][:2]
            performance_instructions.append(f"Incorporate these successful patterns: {', '.join(patterns)}")
        
        if performance_data.get("audience_preferences"):
            prefs = performance_data["audience_preferences"]
            performance_instructions.append(f"Audience responds well to: {', '.join(prefs[:2])}")
        
        if performance_instructions:
            enhanced_prompt = f"{base_prompt}\n\nPerformance Optimization:\n{chr(10).join(f'- {inst}' for inst in performance_instructions)}"
            return enhanced_prompt
        
        return base_prompt
    
    def _optimize_user_prompt(self, prompt: str, user_profile: Dict[str, Any]) -> str:
        """Optimize user prompt based on profile and goals"""
        if not prompt:
            # Generate intelligent default based on profile
            goals = user_profile.get("goals", []) if user_profile else []
            themes = user_profile.get("themes", []) if user_profile else []
            
            if goals and themes:
                return f"Create content about {themes[0]} that helps achieve {goals[0]}"
            elif themes:
                return f"Generate engaging posts about {themes[0]}"
            else:
                return "Create valuable, engaging content for my audience"
        
        return prompt
    
    async def _generate_with_ai(self, system_prompt: str, user_prompt: str, count: int) -> List[str]:
        """Generate content using available AI services with fallback"""
        try:
            if self.openai_client:
                return await self._generate_with_openai(system_prompt, user_prompt, count)
            elif self.anthropic_client:
                return await self._generate_with_anthropic(system_prompt, user_prompt, count)
            else:
                return []
        except Exception as e:
            print(f"Error in AI generation: {e}")
            return []
    
    async def _generate_with_anthropic(self, system_prompt: str, user_prompt: str, count: int) -> List[str]:
        """Generate content using Anthropic Claude"""
        try:
            response = await self.anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": f"Generate {count} different posts about: {user_prompt}"}
                ]
            )
            
            content = response.content[0].text
            posts = [post.strip() for post in content.split('\n\n') if post.strip()]
            return posts[:count]
            
        except Exception as e:
            print(f"Error with Anthropic: {e}")
            return []
    
    async def _enhance_generated_content(self, base_content: List[str], user_profile: Dict[str, Any], platform: str) -> List[Dict[str, Any]]:
        """Enhance generated content with additional intelligence"""
        enhanced_content = []
        
        for i, content in enumerate(base_content):
            # Generate variants for first few posts
            variants = await self._generate_intelligent_variants(content, user_profile) if i < 3 else None
            
            # Calculate performance predictions
            performance_score = self._predict_performance(content, user_profile, platform)
            
            # Extract and enhance themes
            themes = self._extract_intelligent_themes(content, user_profile)
            
            # Generate posting recommendations
            posting_recommendations = self._generate_posting_recommendations(content, themes, user_profile)
            
            enhanced_draft = {
                "content": content,
                "platform": platform,
                "variants": variants,
                "best_time_score": performance_score,
                "themes": themes,
                "moderation_status": await self._moderate_content(content),
                "posting_recommendations": posting_recommendations,
                "engagement_prediction": self._predict_engagement(content, user_profile),
                "optimization_suggestions": self._suggest_optimizations(content, user_profile)
            }
            
            enhanced_content.append(enhanced_draft)
        
        return enhanced_content
    
    def _intelligent_mock_generation(self, count: int, platform: str, user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Enhanced mock generation with user profile intelligence"""
        
        # Get user themes and goals for personalization
        themes = user_profile.get("themes", ["AI", "productivity", "strategy"]) if user_profile else ["AI", "productivity"]
        goals = user_profile.get("goals", ["grow audience", "thought leadership"]) if user_profile else ["grow audience"]
        voice_profile = user_profile.get("voice_profile", {}) if user_profile else {}
        
        # Tone adjustments
        tone = voice_profile.get("tone", {"formal": 40, "punchy": 70, "contrarian": 30})
        is_punchy = tone.get("punchy", 50) > 60
        is_formal = tone.get("formal", 50) > 60
        
        # Enhanced content templates based on themes and goals
        content_templates = {
            "AI": [
                "🤖 {punchy}AI is transforming {theme} in ways we never imagined. Here's what I learned building with AI for the past month:{formal}",
                "{question}What if AI could {goal_action}? {insight} {hashtags}",
                "{statistic} of companies are already using AI for {theme}. Are you ready for what's next? {hashtags}"
            ],
            "productivity": [
                "⚡ {punchy}Stop doing these 3 things that kill your productivity:{formal} {list_items} {hashtags}",
                "{insight} about productivity: {tip}. Try this for one week and see the difference. {hashtags}",
                "Productivity hack: {specific_technique}. {result_claim} {hashtags}"
            ],
            "strategy": [
                "🎯 {punchy}Your {goal} strategy is missing this crucial element:{formal} {strategic_insight} {hashtags}",
                "{contrarian_take} about {theme} strategy. Here's why everyone gets it wrong: {explanation} {hashtags}",
                "Strategy lesson from {example}: {lesson} {application} {hashtags}"
            ]
        }
        
        mock_drafts = []
        for i in range(count):
            # Select theme and template
            theme = themes[i % len(themes)]
            goal = goals[i % len(goals)]
            
            templates = content_templates.get(theme, content_templates["AI"])
            template = templates[i % len(templates)]
            
            # Fill template with personalized content
            content = self._fill_content_template(template, theme, goal, tone, platform)
            
            # Calculate mock metrics
            performance_score = 75 + (i * 3) + (10 if is_punchy else 0)
            engagement_prediction = {
                "likes": 50 + (i * 10),
                "shares": 5 + (i * 2),
                "comments": 3 + i,
                "reach_estimate": 1000 + (i * 200)
            }
            
            mock_draft = {
                "content": content,
                "platform": platform,
                "variants": [self._create_variant(content, j) for j in range(2)] if i < 2 else None,
                "best_time_score": performance_score,
                "themes": [theme, "innovation"] if theme != "innovation" else [theme],
                "moderation_status": "approved",
                "posting_recommendations": {
                    "best_time": "10:30 AM",
                    "day_of_week": "Tuesday",
                    "confidence": 0.8
                },
                "engagement_prediction": engagement_prediction,
                "optimization_suggestions": self._generate_mock_suggestions(content, theme)
            }
            
            mock_drafts.append(mock_draft)
        
        return mock_drafts
    
    def _fill_content_template(self, template: str, theme: str, goal: str, tone: Dict[str, int], platform: str) -> str:
        """Fill content template with personalized data"""
        is_punchy = tone.get("punchy", 50) > 60
        is_formal = tone.get("formal", 50) > 60
        is_contrarian = tone.get("contrarian", 50) > 50
        
        # Content components
        components = {
            "{punchy}": "🚀 " if is_punchy else "",
            "{formal}": " Furthermore, this approach demonstrates significant value." if is_formal else "",
            "{theme}": theme,
            "{goal}": goal,
            "{goal_action}": f"help you achieve {goal}",
            "{question}": "🤔 " if is_punchy else "",
            "{insight}": f"Here's what 3 years of {theme} taught me:",
            "{hashtags}": f"#{theme.replace(' ', '')} #innovation #productivity",
            "{statistic}": "73%",
            "{list_items}": "\n1. Multitasking (it doesn't work)\n2. Checking email every 5 minutes\n3. Not setting clear priorities",
            "{tip}": "focus on systems, not goals",
            "{result_claim}": "Increased my output by 40%",
            "{specific_technique}": "the 2-minute rule",
            "{contrarian_take}": "Unpopular opinion:" if is_contrarian else "Hot take:",
            "{strategic_insight}": f"understanding your audience's real needs in {theme}",
            "{explanation}": "they focus on tactics instead of fundamentals",
            "{example}": "Apple's product launches",
            "{lesson}": "simplicity beats complexity every time",
            "{application}": f"Apply this to your {goal} strategy."
        }
        
        # Replace placeholders
        content = template
        for placeholder, value in components.items():
            content = content.replace(placeholder, value)
        
        # Platform-specific adjustments
        if platform == "linkedin":
            content = content.replace("🚀", "")  # Less emojis for LinkedIn
            if not content.endswith("."):
                content += "."
        elif platform == "twitter":
            # Ensure under 280 characters
            if len(content) > 270:
                content = content[:267] + "..."
        
        return content.strip()
    
    def _create_variant(self, original: str, variant_num: int) -> str:
        """Create intelligent variants of content"""
        variants_strategies = [
            lambda x: x.replace("🚀", "✨").replace("!", "."),  # Tone down
            lambda x: x.replace("Here's", "This is").replace("?", "."),  # More declarative
            lambda x: re.sub(r'(\d+)%', lambda m: f"{int(m.group(1))+5}%", x),  # Adjust stats
        ]
        
        if variant_num < len(variants_strategies):
            return variants_strategies[variant_num](original)
        
        return original
    
    async def _add_intelligence_layer(self, draft_data: Dict[str, Any], user_profile: Dict[str, Any], platform: str) -> Dict[str, Any]:
        """Add intelligence layer to draft"""
        content = draft_data["content"]
        
        # Add intelligent analysis
        draft_data.update({
            "readability_score": self._calculate_readability(content),
            "sentiment_score": self._analyze_sentiment(content),
            "hook_strength": self._analyze_hook_strength(content),
            "call_to_action": self._detect_cta(content),
            "platform_optimization": self._get_platform_optimization(content, platform),
            "personalization_score": self._calculate_personalization(content, user_profile)
        })
        
        return draft_data
    
    def _predict_performance(self, content: str, user_profile: Dict[str, Any], platform: str) -> float:
        """Predict content performance score"""
        base_score = 70
        
        # Content length optimization
        word_count = len(content.split())
        if platform == "twitter" and 15 <= word_count <= 25:
            base_score += 10
        elif platform == "linkedin" and 50 <= word_count <= 150:
            base_score += 10
        
        # Engagement indicators
        if "?" in content:
            base_score += 5  # Questions drive engagement
        if any(emoji in content for emoji in "🚀✨💡🎯⚡"):
            base_score += 3  # Visual elements
        if content.count("#") >= 2:
            base_score += 4  # Hashtags
        
        # Theme alignment
        if user_profile and user_profile.get("themes"):
            themes = user_profile["themes"]
            content_lower = content.lower()
            for theme in themes:
                if theme.lower() in content_lower:
                    base_score += 8
                    break
        
        return min(95, max(60, base_score))
    
    async def _moderate_content(self, content: str) -> str:
        """Enhanced content moderation"""
        # Basic keyword filtering
        flagged_words = ["hate", "violence", "spam", "scam"]
        
        if any(word in content.lower() for word in flagged_words):
            return "flagged"
        
        # Length check for platform
        if len(content) < 10:
            return "flagged"  # Too short
        
        # Check for excessive caps or exclamation marks
        caps_ratio = sum(1 for c in content if c.isupper()) / len(content)
        if caps_ratio > 0.3:
            return "flagged"  # Too shouty
        
        return "approved"
    
    def _generate_mock_suggestions(self, content: str, theme: str) -> List[str]:
        """Generate optimization suggestions"""
        suggestions = []
        
        if "?" not in content:
            suggestions.append("Add a question to increase engagement")
        
        if len(content.split()) > 30:
            suggestions.append("Consider shortening for better readability")
        
        if "#" not in content:
            suggestions.append(f"Add relevant hashtags like #{theme}")
        
        return suggestions[:3]
    
    # Add the missing helper methods
    def _calculate_readability(self, content: str) -> float:
        """Calculate readability score (Flesch-Kincaid inspired)"""
        sentences = len(re.split(r'[.!?]+', content))
        words = len(content.split())
        syllables = sum([self._count_syllables(word) for word in content.split()])
        
        if sentences == 0 or words == 0:
            return 50.0
        
        # Simplified readability score
        avg_sentence_length = words / sentences
        avg_syllables = syllables / words
        
        # Score from 0-100 (higher = more readable)
        score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables)
        return max(0, min(100, score))
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (approximation)"""
        word = word.lower()
        vowels = "aeiouy"
        syllable_count = 0
        previous_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel
        
        # Handle silent e
        if word.endswith('e'):
            syllable_count -= 1
        
        return max(1, syllable_count)
    
    def _analyze_sentiment(self, content: str) -> Dict[str, float]:
        """Analyze sentiment of content"""
        positive_words = ["great", "amazing", "awesome", "fantastic", "excellent", "love", "happy", "excited", "brilliant", "wonderful"]
        negative_words = ["bad", "terrible", "awful", "hate", "sad", "disappointed", "frustrated", "angry", "horrible", "worst"]
        
        content_lower = content.lower()
        positive_score = sum(1 for word in positive_words if word in content_lower)
        negative_score = sum(1 for word in negative_words if word in content_lower)
        total_words = len(content.split())
        
        return {
            "positive": positive_score / max(total_words, 1) * 100,
            "negative": negative_score / max(total_words, 1) * 100,
            "compound": (positive_score - negative_score) / max(total_words, 1) * 100
        }
    
    def _analyze_hook_strength(self, content: str) -> Dict[str, Any]:
        """Analyze the strength of the content hook"""
        first_sentence = content.split('.')[0] if '.' in content else content
        first_sentence = first_sentence.strip()
        
        hook_indicators = {
            "question": "?" in first_sentence,
            "statistic": bool(re.search(r'\d+%|\d+\s*(percent|x|times)', first_sentence)),
            "emoji": bool(re.search(r'[😀-🙿🌀-🗿🚀-🛿🇦-🇿]', first_sentence)),
            "power_words": any(word in first_sentence.lower() for word in ["secret", "surprising", "shocking", "revealed", "exposed"]),
            "urgency": any(word in first_sentence.lower() for word in ["now", "today", "urgent", "limited", "only"]),
            "curiosity": any(phrase in first_sentence.lower() for phrase in ["what if", "imagine if", "here's why", "the reason"])
        }
        
        strength_score = sum(hook_indicators.values()) * 20  # Max 100
        
        return {
            "score": min(100, strength_score),
            "indicators": hook_indicators,
            "first_sentence": first_sentence
        }
    
    def _detect_cta(self, content: str) -> Dict[str, Any]:
        """Detect call-to-action in content"""
        cta_patterns = [
            r"\b(follow|like|share|comment|subscribe|join|try|get|download|learn|discover|start)\b",
            r"\b(click|tap|swipe|visit|check out)\b",
            r"\b(what do you think|thoughts|opinions|agree)\b"
        ]
        
        cta_found = []
        for pattern in cta_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            cta_found.extend(matches)
        
        return {
            "has_cta": len(cta_found) > 0,
            "cta_count": len(cta_found),
            "cta_words": list(set(cta_found))
        }
    
    def _get_platform_optimization(self, content: str, platform: str) -> Dict[str, Any]:
        """Get platform-specific optimization scores"""
        optimizations = {}
        
        if platform == "twitter":
            char_count = len(content)
            optimizations = {
                "length_score": 100 if char_count <= 280 else max(0, 100 - (char_count - 280) * 2),
                "hashtag_count": content.count("#"),
                "mention_count": content.count("@"),
                "media_suggested": char_count < 200,  # Room for media
                "thread_potential": char_count > 240
            }
        
        elif platform == "linkedin":
            word_count = len(content.split())
            optimizations = {
                "length_score": 100 if 50 <= word_count <= 200 else max(0, 100 - abs(word_count - 125) * 2),
                "professionalism_score": 90 if not any(emoji in content for emoji in "😀😂🤣") else 70,
                "hashtag_count": content.count("#"),
                "paragraph_count": len([p for p in content.split('\n\n') if p.strip()]),
                "engagement_words": sum(1 for word in ["insights", "thoughts", "experience", "learned"] if word in content.lower())
            }
        
        return optimizations
    
    def _calculate_personalization(self, content: str, user_profile: Dict[str, Any]) -> float:
        """Calculate how well content matches user profile"""
        if not user_profile:
            return 50.0
        
        score = 0
        max_score = 0
        
        # Check theme alignment
        themes = user_profile.get("themes", [])
        if themes:
            max_score += 30
            content_lower = content.lower()
            theme_matches = sum(1 for theme in themes if theme.lower() in content_lower)
            score += (theme_matches / len(themes)) * 30
        
        # Check goal alignment
        goals = user_profile.get("goals", [])
        if goals:
            max_score += 20
            goal_keywords = {
                "grow audience": ["audience", "followers", "reach", "growth"],
                "thought leadership": ["insights", "experience", "opinion", "perspective"],
                "engagement": ["comment", "share", "thoughts", "discussion"]
            }
            
            for goal in goals:
                if goal in goal_keywords:
                    keywords = goal_keywords[goal]
                    if any(keyword in content.lower() for keyword in keywords):
                        score += 20 / len(goals)
        
        # Check voice alignment
        voice_profile = user_profile.get("voice_profile", {})
        if voice_profile:
            max_score += 50
            tone = voice_profile.get("tone", {})
            
            # Simple tone matching
            if tone.get("punchy", 0) > 60 and ("!" in content or any(emoji in content for emoji in "🚀⚡✨")):
                score += 15
            if tone.get("formal", 0) > 60 and not any(emoji in content for emoji in "😀😂🤣😍"):
                score += 15
            if tone.get("contrarian", 0) > 60 and any(phrase in content.lower() for phrase in ["unpopular", "controversial", "disagree"]):
                score += 20
        
        return (score / max(max_score, 1)) * 100 if max_score > 0 else 50.0
    
    async def _generate_intelligent_variants(self, content: str, user_profile: Dict[str, Any]) -> List[str]:
        """Generate intelligent variants based on user profile"""
        variants = []
        
        # Tone variations
        if user_profile and user_profile.get("voice_profile"):
            tone = user_profile["voice_profile"].get("tone", {})
            
            # More formal variant
            if tone.get("formal", 0) < 60:
                formal_variant = content.replace("!", ".").replace("🚀", "").replace("amazing", "significant")
                variants.append(formal_variant)
            
            # More punchy variant
            if tone.get("punchy", 0) < 70:
                punchy_variant = content.replace(".", "!") if not content.endswith("!") else content
                if "🚀" not in punchy_variant:
                    punchy_variant = "🚀 " + punchy_variant
                variants.append(punchy_variant)
        
        # Length variations
        if len(content.split()) > 20:
            # Shorter version
            sentences = content.split(".")
            short_variant = ". ".join(sentences[:2]) + "."
            variants.append(short_variant)
        
        return variants[:3]
    
    def _extract_intelligent_themes(self, content: str, user_profile: Dict[str, Any]) -> List[str]:
        """Extract themes using intelligent matching"""
        themes = []
        content_lower = content.lower()
        
        # User profile themes first
        if user_profile and user_profile.get("themes"):
            for theme in user_profile["themes"]:
                if theme.lower() in content_lower:
                    themes.append(theme)
        
        # AI/Technology themes
        ai_keywords = ["ai", "artificial intelligence", "machine learning", "automation", "technology", "innovation"]
        if any(keyword in content_lower for keyword in ai_keywords):
            themes.append("AI & Technology")
        
        # Business themes
        business_keywords = ["strategy", "business", "growth", "marketing", "sales", "leadership"]
        if any(keyword in content_lower for keyword in business_keywords):
            themes.append("Business Strategy")
        
        # Productivity themes
        productivity_keywords = ["productivity", "efficiency", "time management", "workflow", "organization"]
        if any(keyword in content_lower for keyword in productivity_keywords):
            themes.append("Productivity")
        
        return list(set(themes))[:3]
    
    def _generate_posting_recommendations(self, content: str, themes: List[str], user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Generate intelligent posting recommendations"""
        recommendations = {
            "best_time": "10:30 AM",
            "day_of_week": "Tuesday",
            "confidence": 0.7
        }
        
        # Theme-based timing
        if "AI" in str(themes):
            recommendations.update({
                "best_time": "9:00 AM",
                "day_of_week": "Wednesday",
                "confidence": 0.8
            })
        elif "Productivity" in str(themes):
            recommendations.update({
                "best_time": "8:00 AM",
                "day_of_week": "Monday",
                "confidence": 0.85
            })
        
        return recommendations
    
    def _predict_engagement(self, content: str, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Predict engagement metrics"""
        base_likes = 50
        base_shares = 5
        base_comments = 3
        
        # Boost based on content features
        if "?" in content:
            base_comments += 5
        if any(emoji in content for emoji in "🚀⚡✨"):
            base_likes += 20
        if "#" in content:
            base_likes += 10
        
        # User profile influence
        if user_profile:
            themes = user_profile.get("themes", [])
            if "AI" in str(themes):
                base_likes += 15
                base_shares += 3
        
        return {
            "likes": base_likes,
            "shares": base_shares,
            "comments": base_comments,
            "reach_estimate": base_likes * 20
        }
    
    def _suggest_optimizations(self, content: str, user_profile: Dict[str, Any]) -> List[str]:
        """Suggest content optimizations"""
        suggestions = []
        
        # Length optimization
        word_count = len(content.split())
        if word_count > 50:
            suggestions.append("Consider shortening for better engagement")
        elif word_count < 15:
            suggestions.append("Add more context for better value")
        
        # Engagement optimization
        if "?" not in content:
            suggestions.append("Add a question to increase comments")
        
        if "#" not in content:
            suggestions.append("Add relevant hashtags for discoverability")
        
        # Visual optimization
        if not any(emoji in content for emoji in "🚀⚡✨💡🎯"):
            suggestions.append("Consider adding relevant emojis")
        
        return suggestions[:3]
    
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
    
    async def analyze_voice_samples(self, samples: List[str], user_id: str = None) -> Dict[str, Any]:
        """Enhanced voice analysis with multiple techniques"""
        
        if not samples:
            return {"error": "No samples provided"}
        
        try:
            # Combine all techniques for comprehensive analysis
            linguistic_analysis = self._analyze_linguistic_patterns(samples)
            stylistic_analysis = self._analyze_stylistic_patterns(samples)
            ai_analysis = await self._ai_voice_analysis(samples)
            
            # Create voice embedding
            voice_embedding = self._create_voice_embedding(samples)
            
            # Combine analyses
            combined_analysis = {
                "tone": self._combine_tone_analysis(linguistic_analysis, stylistic_analysis, ai_analysis),
                "style": {
                    "personality": ai_analysis.get("personality", []) + stylistic_analysis.get("personality", []),
                    "vocabulary": linguistic_analysis.get("key_words", [])[:10],
                    "structure": stylistic_analysis.get("structure", [])
                },
                "metrics": {
                    "avg_sentence_length": linguistic_analysis.get("avg_sentence_length", 0),
                    "complexity_score": linguistic_analysis.get("complexity_score", 0),
                    "emotion_score": stylistic_analysis.get("emotion_score", 0),
                    "confidence_level": ai_analysis.get("confidence", 0.8)
                },
                "embedding": voice_embedding,
                "summary": ai_analysis.get("summary", "Unique voice profile created"),
                "improvement_suggestions": self._generate_voice_improvements(linguistic_analysis, stylistic_analysis)
            }
            
            return combined_analysis
            
        except Exception as e:
            print(f"Error in comprehensive voice analysis: {e}")
            # Enhanced fallback with sample analysis
            return self._fallback_voice_analysis(samples)
    
    def _analyze_linguistic_patterns(self, samples: List[str]) -> Dict[str, Any]:
        """Analyze linguistic patterns in writing samples"""
        combined_text = " ".join(samples)
        sentences = re.split(r'[.!?]+', combined_text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Sentence length analysis
        sentence_lengths = [len(s.split()) for s in sentences]
        avg_sentence_length = np.mean(sentence_lengths) if sentence_lengths else 0
        
        # Word complexity analysis
        complex_words = re.findall(r'\b\w{8,}\b', combined_text.lower())
        complexity_score = len(complex_words) / max(len(combined_text.split()), 1) * 100
        
        # Extract key vocabulary
        words = re.findall(r'\b\w+\b', combined_text.lower())
        word_freq = {}
        for word in words:
            if len(word) > 3:  # Skip short words
                word_freq[word] = word_freq.get(word, 0) + 1
        
        key_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:20]
        key_words = [word for word, freq in key_words]
        
        return {
            "avg_sentence_length": avg_sentence_length,
            "complexity_score": complexity_score,
            "key_words": key_words,
            "total_words": len(words),
            "unique_words": len(set(words))
        }
    
    def _analyze_stylistic_patterns(self, samples: List[str]) -> Dict[str, Any]:
        """Analyze stylistic patterns and emotional tone"""
        combined_text = " ".join(samples)
        
        # Punctuation patterns
        exclamation_count = combined_text.count('!')
        question_count = combined_text.count('?')
        emoji_pattern = re.compile(r'[😀-🙿🌀-🗿🚀-🛿🇦-🇿]+')
        emoji_count = len(emoji_pattern.findall(combined_text))
        
        # Emotional indicators
        emotion_words = {
            "positive": ["amazing", "fantastic", "great", "awesome", "love", "excited", "brilliant"],
            "negative": ["terrible", "awful", "hate", "disappointed", "frustrated", "angry"],
            "neutral": ["okay", "fine", "decent", "average", "normal"]
        }
        
        emotion_scores = {}
        for emotion, words in emotion_words.items():
            score = sum(1 for word in words if word in combined_text.lower())
            emotion_scores[emotion] = score
        
        # Determine dominant emotion
        dominant_emotion = max(emotion_scores.items(), key=lambda x: x[1])
        emotion_score = dominant_emotion[1] / max(len(combined_text.split()), 1) * 100
        
        # Personality traits based on patterns
        personality_traits = []
        if exclamation_count > len(samples):
            personality_traits.append("enthusiastic")
        if question_count > len(samples) * 0.5:
            personality_traits.append("inquisitive")
        if emoji_count > 0:
            personality_traits.append("expressive")
        
        # Structure patterns
        structure_patterns = []
        if any("first" in sample.lower() and "second" in sample.lower() for sample in samples):
            structure_patterns.append("structured")
        if any(len(sample.split()) > 50 for sample in samples):
            structure_patterns.append("detailed")
        if any(len(sample.split()) < 20 for sample in samples):
            structure_patterns.append("concise")
        
        return {
            "emotion_score": emotion_score,
            "dominant_emotion": dominant_emotion[0],
            "punctuation_style": {
                "exclamations": exclamation_count,
                "questions": question_count,
                "emojis": emoji_count
            },
            "personality": personality_traits,
            "structure": structure_patterns
        }
    
    async def _ai_voice_analysis(self, samples: List[str]) -> Dict[str, Any]:
        """AI-powered voice analysis using LLM"""
        
        prompt = f"""
        Analyze these writing samples and provide a detailed voice profile. Be specific and actionable.
        
        Writing Samples:
        {chr(10).join(f"{i+1}. {sample}" for i, sample in enumerate(samples))}
        
        Provide analysis as JSON:
        {{
            "tone": {{
                "formal": 0-100,
                "punchy": 0-100, 
                "contrarian": 0-100,
                "confident": 0-100,
                "empathetic": 0-100
            }},
            "personality": ["trait1", "trait2", "trait3"],
            "writing_style": {{
                "sentence_structure": "simple/complex/varied",
                "vocabulary_level": "casual/professional/academic",
                "persuasion_style": "direct/story-driven/data-driven"
            }},
            "content_patterns": ["pattern1", "pattern2"],
            "summary": "2-3 sentence voice description",
            "confidence": 0.0-1.0
        }}
        """
        
        try:
            if self.openai_client:
                response = await self.openai_client.chat.completions.create(
                    model="gpt-4" if "gpt-4" in str(settings.OPENAI_API_KEY) else "gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2
                )
                
                content = response.choices[0].message.content
                # Extract JSON from response
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                    
            # Fallback analysis
            return {
                "tone": {"formal": 45, "punchy": 65, "contrarian": 30, "confident": 70, "empathetic": 50},
                "personality": ["professional", "direct", "insightful"],
                "writing_style": {
                    "sentence_structure": "varied",
                    "vocabulary_level": "professional",
                    "persuasion_style": "data-driven"
                },
                "content_patterns": ["actionable insights", "clear examples"],
                "summary": "Professional voice with direct communication style and actionable insights",
                "confidence": 0.75
            }
            
        except Exception as e:
            print(f"Error in AI voice analysis: {e}")
            return {"error": "AI analysis failed"}
    
    def _create_voice_embedding(self, samples: List[str]) -> List[float]:
        """Create numerical embedding representing voice characteristics"""
        try:
            combined_text = " ".join(samples)
            
            # Use TF-IDF for basic embedding
            if hasattr(self, '_fitted_vectorizer'):
                vector = self._fitted_vectorizer.transform([combined_text])
            else:
                # Fit on current samples (in production, use pre-trained embeddings)
                vector = self.tfidf_vectorizer.fit_transform([combined_text])
                self._fitted_vectorizer = self.tfidf_vectorizer
            
            # Convert to dense array and then to list
            embedding = vector.toarray()[0].tolist()
            
            # Normalize to unit vector
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = [x / norm for x in embedding]
            
            return embedding[:100]  # Limit size
            
        except Exception as e:
            print(f"Error creating voice embedding: {e}")
            # Return random normalized vector as fallback
            random_vector = np.random.random(50)
            norm = np.linalg.norm(random_vector)
            return (random_vector / norm).tolist()
    
    def _combine_tone_analysis(self, linguistic: Dict, stylistic: Dict, ai: Dict) -> Dict[str, int]:
        """Combine tone analysis from different methods"""
        # Get AI tone as base
        ai_tone = ai.get("tone", {})
        
        # Adjust based on linguistic patterns
        formal_boost = min(20, linguistic.get("complexity_score", 0))
        punchy_boost = min(30, stylistic.get("punctuation_style", {}).get("exclamations", 0) * 5)
        
        # Combine and normalize
        combined_tone = {
            "formal": max(0, min(100, ai_tone.get("formal", 50) + formal_boost)),
            "punchy": max(0, min(100, ai_tone.get("punchy", 50) + punchy_boost)),
            "contrarian": ai_tone.get("contrarian", 40),
            "confident": ai_tone.get("confident", 60),
            "empathetic": ai_tone.get("empathetic", 50)
        }
        
        return combined_tone
    
    def _generate_voice_improvements(self, linguistic: Dict, stylistic: Dict) -> List[str]:
        """Generate suggestions for voice improvement"""
        suggestions = []
        
        avg_length = linguistic.get("avg_sentence_length", 0)
        if avg_length > 25:
            suggestions.append("Consider shorter sentences for better readability")
        elif avg_length < 10:
            suggestions.append("Try varying sentence length for more engaging content")
        
        complexity = linguistic.get("complexity_score", 0)
        if complexity > 15:
            suggestions.append("Simplify vocabulary for broader audience appeal")
        elif complexity < 5:
            suggestions.append("Add more sophisticated vocabulary to establish expertise")
        
        emotion_score = stylistic.get("emotion_score", 0)
        if emotion_score < 2:
            suggestions.append("Add more emotional language to increase engagement")
        
        return suggestions[:3]  # Limit to top 3 suggestions
    
    def _fallback_voice_analysis(self, samples: List[str]) -> Dict[str, Any]:
        """Enhanced fallback analysis when AI is not available"""
        combined_text = " ".join(samples)
        
        # Basic analysis
        word_count = len(combined_text.split())
        sentence_count = len(re.split(r'[.!?]+', combined_text))
        avg_sentence_length = word_count / max(sentence_count, 1)
        
        # Determine tone based on patterns
        formal_score = 40 + min(30, len(re.findall(r'\b(?:furthermore|however|therefore|consequently)\b', combined_text.lower())) * 10)
        punchy_score = 30 + min(40, combined_text.count('!') * 15)
        
        return {
            "tone": {
                "formal": formal_score,
                "punchy": punchy_score,
                "contrarian": 35,
                "confident": 60,
                "empathetic": 45
            },
            "style": {
                "personality": ["analytical", "direct", "professional"],
                "vocabulary": re.findall(r'\b\w{6,}\b', combined_text.lower())[:10],
                "structure": ["clear", "structured"]
            },
            "metrics": {
                "avg_sentence_length": avg_sentence_length,
                "complexity_score": len(re.findall(r'\b\w{8,}\b', combined_text)) / word_count * 100,
                "confidence_level": 0.6
            },
            "summary": f"Voice profile created from {len(samples)} samples with {word_count} total words",
            "embedding": self._create_voice_embedding(samples)
        }
    
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