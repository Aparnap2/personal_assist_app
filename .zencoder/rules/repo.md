# Personal Assist - AI Content Assistant Repository

## Project Overview

Personal Assist is a React Native mobile application that uses AI to help users create, schedule, and optimize social media content. It features an intelligent AI assistant that learns the user's voice and writing style to generate personalized content suggestions.

## Architecture

### Frontend (React Native + Expo)
- **Framework**: React Native with Expo Router
- **Styling**: NativeWind (Tailwind CSS for React Native)
- **Navigation**: Expo Router (file-based routing)
- **State Management**: React Context API
- **Authentication**: Firebase Auth
- **UI Library**: Custom components built on top of NativeWind

### Backend (Python FastAPI)
- **Framework**: FastAPI
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT tokens
- **AI Integration**: OpenAI GPT models
- **Content Analysis**: Custom NLP pipeline
- **Scheduling**: Background task system

## Key Features

1. **AI Content Generation**: Creates drafts based on user's voice profile and content themes
2. **Intelligent Scheduling**: Analyzes optimal posting times based on audience engagement
3. **Voice Profile Learning**: Learns from user's writing samples to match their style
4. **Multi-Platform Support**: Twitter/X and LinkedIn integration
5. **Content Analytics**: Performance tracking and engagement predictions
6. **Smart Onboarding**: Guided setup for new users
7. **Consultation Chat**: AI assistant for content strategy advice

## Project Structure

```
/
├── app/                    # Expo Router pages
│   ├── (tabs)/            # Tab-based navigation
│   ├── auth.tsx           # Authentication screen
│   ├── onboarding.tsx     # New user onboarding
│   └── _layout.tsx        # Root layout
├── components/            # Reusable UI components
│   ├── ui/               # Base UI components (Button, Card, etc.)
│   └── DraftCard.tsx     # Content draft display component
├── contexts/             # React Context providers
├── services/             # API and external service integrations
├── hooks/                # Custom React hooks
├── types/                # TypeScript type definitions
├── utils/                # Utility functions
├── server/               # Python FastAPI backend
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Core functionality
│   │   ├── models/       # Database models
│   │   ├── services/     # Business logic services
│   │   └── schemas/      # Pydantic schemas
│   └── requirements.txt  # Python dependencies
└── assets/               # Static assets
```

## Recent Enhancements

### Enhanced Scheduling System
- **Intelligent Time Optimization**: AI analyzes user's audience engagement patterns
- **Flexible Scheduling**: Support for immediate publishing, optimal time scheduling, or custom time selection
- **Content Performance Prediction**: Engagement forecasting before publishing
- **Bulk Operations**: Schedule multiple drafts with optimal timing

### Advanced Content Analysis
- **Readability Scoring**: Automated content readability assessment
- **Sentiment Analysis**: Emotional tone analysis and optimization
- **Hook Strength Evaluation**: Opening line effectiveness scoring
- **Voice Matching**: Personalization score based on user's voice profile
- **SEO/Engagement Optimization**: Actionable improvement suggestions

### Enhanced User Experience
- **Rich Draft Cards**: Expandable content previews with detailed analytics
- **Interactive Onboarding**: Multi-step guided setup with voice profile creation
- **Real-time Feedback**: Live content scoring and suggestions
- **Performance Insights**: Detailed analytics and recommendations

## Development Guidelines

### Code Style
- Use TypeScript for type safety
- Follow React Native best practices
- Use functional components with hooks
- Implement proper error handling
- Write descriptive component and function names

### Component Structure
- Keep components small and focused
- Use composition over inheritance
- Implement proper prop typing
- Add loading and error states
- Include accessibility features

### State Management
- Use React Context for global state
- Keep component state local when possible
- Implement proper data flow patterns
- Handle async operations gracefully

### API Integration
- Use proper error handling
- Implement loading states
- Cache data when appropriate
- Handle offline scenarios

## Key Technologies

- **Frontend**: React Native, Expo, NativeWind, TypeScript
- **Backend**: FastAPI, SQLAlchemy, Pydantic, SQLite
- **AI/ML**: OpenAI API, Custom NLP pipelines
- **Authentication**: Firebase Auth, JWT
- **Development**: ESLint, Prettier, Git hooks

## Current Focus Areas

1. **Content Quality Enhancement**: Improving AI-generated content quality and personalization
2. **Advanced Analytics**: Building comprehensive performance tracking and insights
3. **Multi-Platform Expansion**: Adding support for more social media platforms
4. **Performance Optimization**: Improving app performance and reducing loading times
5. **User Experience**: Refining UI/UX based on user feedback

## Future Roadmap

- Advanced content calendar management
- Team collaboration features
- Integration with more social platforms
- Advanced analytics and reporting
- Content template system
- Automated A/B testing for posts

---

This repository is actively maintained and follows modern React Native and Python development practices.