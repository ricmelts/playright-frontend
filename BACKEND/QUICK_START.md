# 🚀 PlayRight Backend Quick Start

## Prerequisites
- Python 3.11+ installed
- Docker Desktop (recommended) OR manual setup

## Option 1: Docker Setup (Recommended)

1. **Setup Environment**
```bash
cd BACKEND
make setup
```

2. **Edit Configuration**
Update the `.env` files with your API keys:
- `BACKEND/.env` - Main configuration  
- `BACKEND/api-server/.env` - API server config
- `BACKEND/ai-engine/.env` - AI engine config

3. **Start All Services**
```bash
make up
```

4. **Access Services**
- 📊 **PocketBase Admin**: http://localhost:8090/_/
- 🔗 **API Server**: http://localhost:3001/docs  
- 🤖 **AI Engine**: http://localhost:8000/docs

## Option 2: Manual Setup

### 1. Start PocketBase
```bash
cd BACKEND/pocketbase
./start.bat                    # Windows
# or ./pocketbase serve        # Linux/Mac
```

### 2. Setup Admin Account
- Go to http://localhost:8090/_/
- Create admin account: `admin@playright.ai` / `your-password`
- The migrations will auto-create collections

### 3. Start API Server
```bash
cd BACKEND/api-server
pip install -r requirements.txt
cp .env.example .env           # Edit with your config
python -m uvicorn app.main:app --reload --port 3001
```

### 4. Start AI Engine  
```bash
cd BACKEND/ai-engine
pip install -r requirements.txt
cp .env.example .env           # Edit with your config
python -m uvicorn main:app --reload --port 8000
```

## 🎯 First Steps

1. **Create Collections** - PocketBase will auto-run migrations
2. **Test API** - Visit http://localhost:3001/docs
3. **Create Sample Data** - Use the PocketBase admin panel
4. **Test AI Matching** - Try the `/api/matching/*` endpoints

## 🔑 Default Credentials

**PocketBase Admin**: Set up during first visit to admin panel
**Sample Users** (created by setup hook):
- Athlete: `marcus.johnson@university.edu` / `athlete123`
- Brand: `nike.local@nike.com` / `brand123`

## 🧪 Testing

```bash
# Run API tests
cd api-server && python -m pytest tests/

# Run AI engine tests
cd ai-engine && python -m pytest tests/

# Check service health
make health
```

## 📊 Key Endpoints to Test

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login

### AI Matching  
- `POST /api/matching/athletes-for-brand` - Find athletes for brand
- `GET /api/matching/compatibility-score` - Calculate compatibility
- `GET /api/matching/trending-athletes` - Get trending athletes

### Data Management
- `GET /api/athletes` - List athletes
- `GET /api/brands` - List brands  
- `GET /api/deals` - List deals
- `POST /api/deals` - Create new deal

Your AI-powered NIL matching platform backend is ready! 🎉