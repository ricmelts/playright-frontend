# PlayRight AI Platform - CLAUDE.md

## Overview
PlayRight AI is a comprehensive platform for matching college athletes with NIL (Name, Image, Likeness) deals using AI-powered algorithms. The platform consists of a React frontend and Python backend with multiple microservices.

## High-Level Architecture

### Frontend (React + TypeScript)
- **Framework**: React 18 with TypeScript
- **Styling**: Tailwind CSS + Radix UI components
- **Routing**: React Router v7
- **Theme**: next-themes with dark/light mode
- **Build**: Create React App

### Backend (Python Microservices)
- **API Server**: FastAPI (port 3001)
- **AI Engine**: FastAPI ML service (port 8000)
- **Database**: PocketBase (port 8090)
- **Cache**: Redis (port 6379)
- **Workers**: Celery for background tasks

## Project Structure

```
├── src/                          # React frontend source
│   ├── components/
│   │   ├── ui/                   # Reusable Radix UI components
│   │   ├── pages/               # Page components
│   │   ├── Layout.tsx           # Main layout with sidebar
│   │   ├── ThemeProvider.tsx    # Theme context provider
│   │   └── ThemeToggle.tsx      # Theme switcher
│   ├── styles/globals.css       # Global CSS with theme variables
│   └── App.tsx                  # Main app with routing
├── BACKEND/
│   ├── pocketbase/
│   │   ├── pocketbase.exe       # PocketBase executable
│   │   ├── pb_migrations/       # Database schema migrations
│   │   └── pb_hooks/            # Server-side hooks
│   ├── api-server/              # Main Python FastAPI service
│   │   └── app/
│   │       ├── routes/          # API endpoint definitions
│   │       ├── services/        # Business logic services
│   │       ├── models/          # Pydantic data models
│   │       ├── core/            # Configuration and settings
│   │       └── worker/          # Celery task definitions
│   └── ai-engine/               # ML microservice
│       ├── api/                 # ML API endpoints
│       ├── models/              # ML models and algorithms
│       └── training/            # Model training scripts
├── docker-compose.yml           # Complete service orchestration
└── setup_collections.py        # PocketBase setup script
```

## Key Technologies

### Frontend Dependencies
- **UI Framework**: React 18.2.0
- **Type System**: TypeScript 4.9.0
- **UI Components**: Radix UI (comprehensive component library)
- **Styling**: Tailwind CSS 3.3.5
- **Icons**: Lucide React 0.294.0
- **Theme**: next-themes 0.4.6
- **Routing**: react-router-dom 7.8.1
- **Charts**: Recharts 3.1.2
- **Forms**: react-hook-form 7.62.0

### Backend Dependencies
- **API Framework**: FastAPI
- **Database**: PocketBase (SQLite-based)
- **ML/AI**: sentence-transformers, scikit-learn
- **Tasks**: Celery + Redis
- **HTTP**: requests, aiohttp
- **Environment**: python-dotenv
- **Validation**: Pydantic

## Development Workflow

### Initial Setup
```bash
# Frontend setup
npm install
npm start

# Backend setup
cd BACKEND
docker-compose up -d
python setup_collections.py
```

### Common Commands
```bash
# Frontend development
npm start                        # Start dev server (port 3000)
npm run build                    # Build for production
npm test                         # Run tests

# Backend development
cd BACKEND
docker-compose up -d             # Start all services
docker-compose logs -f api-server # View API logs
docker-compose down              # Stop services

# Individual service development
cd BACKEND/api-server && python -m uvicorn app.main:app --reload --port 3001
cd BACKEND/ai-engine && python -m uvicorn main:app --reload --port 8000

# Testing
cd BACKEND/api-server && python -m pytest tests/
cd BACKEND/ai-engine && python -m pytest tests/
```

## Database Schema (PocketBase)

### Core Collections
- **users**: Extended with role, profile_completed fields
- **athletes**: Athlete profiles with sports, metrics, social data
- **brands**: Brand profiles with budgets, preferences, campaigns
- **deals**: NIL deals with status tracking and contract management
- **campaigns**: Marketing campaigns with targeting criteria
- **athlete_metrics**: Social media and performance analytics

### Key Fields
- Users have roles: athlete, brand, agent, admin
- Athletes track: sport, position, year, social_followers, engagement_rate
- Brands track: industry, budget_range, target_demographics
- Deals track: status, value, deliverables, timeline

## API Architecture

### Authentication (via PocketBase)
```
POST /api/auth/register          # User registration
POST /api/auth/login            # Authentication
GET  /api/auth/me               # Current user
```

### AI Matching Endpoints
```
POST /api/matching/athletes-for-brand    # Find athletes for brand
POST /api/matching/brands-for-athlete    # Find brands for athlete
GET  /api/matching/compatibility-score   # Detailed compatibility
GET  /api/matching/trending-athletes     # Trending by sport
```

### Data Management
```
GET  /api/athletes              # List/filter athletes
GET  /api/brands               # List/filter brands
GET  /api/deals                # List/filter deals
GET  /api/campaigns            # List campaigns
```

## AI/ML Features

### Matching Engine (BACKEND/ai-engine/)
- **Embeddings**: sentence-transformers for semantic similarity
- **Compatibility**: Multi-factor scoring (sport, audience, engagement, budget)
- **Recommendations**: Real-time athlete-brand matching
- **Analytics**: Social media performance tracking

### Key Models
- `embedding_model.py`: Creates embeddings for athletes and brands
- `compatibility_model.py`: Multi-factor compatibility scoring
- `training/`: Model training and fine-tuning scripts

## Environment Configuration

### Required Environment Variables
```env
# API Server (.env in BACKEND/api-server/)
POCKETBASE_URL=http://localhost:8090
REDIS_URL=redis://localhost:6379
AI_ENGINE_URL=http://localhost:8000
OPENAI_API_KEY=your_key_here
STRIPE_SECRET_KEY=your_key_here

# Social Media API Keys
INSTAGRAM_ACCESS_TOKEN=
TWITTER_API_KEY=
TIKTOK_API_KEY=
```

## Testing Strategy

### Frontend Testing
- **Framework**: Jest (via react-scripts)
- **Commands**: `npm test`
- **Coverage**: Component testing, integration tests

### Backend Testing
- **Framework**: pytest
- **API Tests**: `cd BACKEND/api-server && python -m pytest tests/`
- **AI Tests**: `cd BACKEND/ai-engine && python -m pytest tests/`
- **Integration**: End-to-end API testing

## Build & Deployment

### Local Development
1. Start backend: `cd BACKEND && docker-compose up -d`
2. Initialize PocketBase: `python setup_collections.py`
3. Start frontend: `npm start`

### Production Build
```bash
# Frontend
npm run build

# Backend
docker-compose -f docker-compose.prod.yml up -d
```

### Service Ports
- Frontend: 3000
- API Server: 3001
- AI Engine: 8000
- PocketBase: 8090
- Redis: 6379

## Code Quality Standards

### Frontend
- **Type Safety**: Full TypeScript coverage
- **Components**: Radix UI + custom components in `components/ui/`
- **Styling**: Tailwind CSS with CSS custom properties for theming
- **State**: React hooks + context for theme management

### Backend
- **Type Hints**: Full Python type annotation
- **Validation**: Pydantic models for all data
- **Architecture**: Clean separation of routes, services, models
- **Error Handling**: Comprehensive exception handling

## Common Patterns

### Frontend Component Structure
```typescript
// Standard component pattern
interface ComponentProps {
  // Props with TypeScript
}

export const Component: React.FC<ComponentProps> = ({ props }) => {
  // Component logic
  return (
    <div className="tailwind-classes">
      {/* JSX content */}
    </div>
  )
}
```

### Backend Route Pattern
```python
# Standard FastAPI route pattern
from fastapi import APIRouter, Depends, HTTPException
from ..services.service_name import ServiceClass
from ..models.models import ModelName

router = APIRouter()

@router.get("/endpoint")
async def endpoint_function(
    service: ServiceClass = Depends()
):
    # Route logic
    return result
```

## Troubleshooting

### Common Issues
1. **PocketBase Migration Errors**: Collections already exist
   - Solution: Modify migrations to extend existing collections

2. **Unicode Errors on Windows**: Print statements with emojis fail
   - Solution: Remove Unicode characters from Python print statements

3. **CORS Issues**: Frontend can't connect to backend
   - Solution: Check CORS middleware in `BACKEND/api-server/app/main.py`

4. **AI Engine Timeout**: ML operations taking too long
   - Solution: Increase timeout in docker-compose configuration

### Service Health Checks
```bash
# Check PocketBase
curl http://localhost:8090/api/health

# Check API Server  
curl http://localhost:3001/health

# Check AI Engine
curl http://localhost:8000/health
```

## Key Implementation Notes

1. **Theme System**: Uses CSS custom properties with next-themes for dynamic switching
2. **AI Matching**: Combines semantic embeddings with rule-based compatibility scoring
3. **Authentication**: PocketBase handles all auth, API server validates JWT tokens
4. **File Storage**: PocketBase manages file uploads and serving
5. **Background Tasks**: Celery workers handle social media sync and metrics updates
6. **Real-time**: WebSocket support planned for live notifications

## Development Tips

1. **Frontend Development**: Use `npm start` for hot reload development
2. **Backend Development**: Use `--reload` flag for FastAPI auto-restart
3. **Database Changes**: Create new migrations in `pb_migrations/`
4. **AI Model Updates**: Retrain models in `ai-engine/training/`
5. **API Testing**: Use FastAPI automatic docs at `/docs` endpoints

This platform represents a sophisticated full-stack AI application with modern development practices and scalable architecture.