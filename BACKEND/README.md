# PlayRight Backend

AI-powered NIL deals matching platform backend using Python FastAPI and PocketBase.

## Architecture

```
BACKEND/
├── pocketbase/          # Database & Auth service
│   ├── pb_migrations/   # Database schema migrations
│   └── pb_hooks/        # Server-side logic hooks
├── api-server/          # Main Python FastAPI service
│   └── app/
│       ├── routes/      # API endpoints
│       ├── services/    # Business logic
│       ├── models/      # Pydantic models
│       └── core/        # Core configurations
└── ai-engine/           # ML/AI microservice
    ├── api/             # ML API endpoints
    ├── models/          # ML models
    └── training/        # Training scripts
```

## Quick Start

1. **Environment Setup**
```bash
cd BACKEND
cp api-server/.env.example api-server/.env
# Edit .env with your configuration
```

2. **Start Services**
```bash
docker-compose up -d
```

3. **Initialize Database**
```bash
# PocketBase will auto-run migrations on first start
# Access admin panel at http://localhost:8090/_/
```

## Services

- **PocketBase**: `localhost:8090` - Database, Auth, File Storage
- **API Server**: `localhost:3001` - Main application API  
- **AI Engine**: `localhost:8000` - ML matching algorithms
- **Redis**: `localhost:6379` - Caching and job queues

## Key Features

### 🔐 Authentication (PocketBase)
- User registration/login with role-based access
- JWT token management
- OAuth integration ready

### 👥 User Management
- **Athletes**: profiles, social metrics, NIL eligibility
- **Brands**: company profiles, budgets, campaign preferences
- **Agents**: deal management and oversight

### 🤖 AI Matching Engine
- Semantic similarity using sentence transformers
- Multi-factor compatibility scoring
- Real-time match recommendations
- Bulk analysis for campaigns

### 📊 Deal Management
- Full deal lifecycle tracking
- Contract document management  
- Progress monitoring
- Automated status updates

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User authentication
- `GET /api/auth/me` - Current user info

### AI Matching
- `POST /api/matching/athletes-for-brand` - Find athletes for brand
- `POST /api/matching/brands-for-athlete` - Find brands for athlete  
- `GET /api/matching/compatibility-score` - Detailed compatibility analysis
- `GET /api/matching/trending-athletes` - Trending athletes by sport

### Data Management
- `GET /api/athletes` - List athletes with filters
- `GET /api/brands` - List brands with filters
- `GET /api/deals` - List deals with filters
- `GET /api/campaigns` - List campaigns

## Development

### Local Development
```bash
# Start individual services
cd api-server && python -m uvicorn app.main:app --reload --port 3001
cd ai-engine && python -m uvicorn main:app --reload --port 8000
```

### Testing
```bash
# API tests
cd api-server && python -m pytest tests/

# AI engine tests  
cd ai-engine && python -m pytest tests/
```

## Configuration

Key environment variables:

- `POCKETBASE_URL` - PocketBase instance URL
- `OPENAI_API_KEY` - For advanced AI features
- `REDIS_URL` - Redis connection for caching
- `STRIPE_SECRET_KEY` - Payment processing
- Social media API keys for metrics collection

## Deployment

Production deployment uses Docker Compose with:
- Persistent volumes for data
- Health checks for all services
- Proper security configurations
- Log aggregation setup