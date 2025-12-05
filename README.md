# BiteRead

AI-powered English learning mobile app with sentence-by-sentence translation practice.

## Project Structure

```
BiteRead/
├── frontend/              # React Native mobile app (Expo)
│   ├── app/              # Expo Router screens
│   ├── components/       # Reusable UI components
│   ├── services/         # API integration layer
│   └── .env.example      # Frontend environment template
├── langchain-server/     # Python FastAPI backend
│   ├── app/              # Application modules
│   │   ├── endpoints/    # API routes
│   │   ├── models/       # Database models
│   │   ├── schemas/      # Pydantic schemas
│   │   └── services/     # LangChain AI integration
│   ├── main.py           # Server entry point
│   └── .env.example      # Backend environment template
├── docker-compose.yml    # Docker orchestration
└── CLAUDE.md            # AI assistant instructions
```

## Quick Start

### Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- OpenAI API Key
- Docker (optional, recommended for backend)
- Expo Go app on your mobile device (for testing)

### 1. Backend Setup

#### Option A: Docker (Recommended)

```bash
# Copy and configure environment
cd langchain-server
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# From project root, start backend
cd ..
docker-compose up -d

# View logs
docker-compose logs -f

# Backend will be available at http://localhost:8000
```

#### Option B: Local Python

```bash
cd langchain-server

# Copy and configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Activate (Unix/Mac)
source venv/bin/activate

# Install dependencies and run
pip install -r requirements.txt
python main.py

# Backend will be available at http://localhost:8000
```

### 2. Add Test Data

```bash
cd langchain-server
python add_article.py
```

This adds a sample English article with Korean translations for testing.

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Start Expo development server
npm start
```

### 4. Run on Device

#### Web Browser
Press `w` in the terminal or visit `http://localhost:8081`

#### Physical Device (iOS/Android)
1. Install **Expo Go** from App Store or Google Play
2. Make sure your phone and computer are on the **same WiFi network**
3. Scan the QR code shown in terminal with Expo Go

**If connection fails:**
- Get your computer's local IP: `ipconfig` (Windows) or `ifconfig` (Mac/Linux)
- Edit `frontend/.env`: `EXPO_PUBLIC_API_URL=http://YOUR_IP:8000`
- Restart Expo: `npm start`

#### iOS Simulator (Mac only)
Press `i` in the terminal

#### Android Emulator
Press `a` in the terminal (requires Android Studio)

## Features

- 📚 **Article-based learning**: Study English through authentic articles
- 🔄 **Sentence-by-sentence translation**: Practice translating one sentence at a time
- 🤖 **AI-powered feedback**: Get intelligent feedback from GPT-4o-mini
- 📊 **Progress tracking**: See your completion percentage
- ✅ **Instant validation**: Color-coded feedback (green = correct, red = incorrect)
- 🎯 **Auto-advance**: Automatically move to next sentence after correct answer

## API Documentation

Once the backend is running, visit:
- **Interactive API docs**: http://localhost:8000/docs
- **API info**: http://localhost:8000

### Main Endpoints

- `POST /api/articles` - Create new article
- `GET /api/articles` - List all articles
- `GET /api/articles/{id}` - Get article details with sentences
- `POST /api/translation/check` - Check translation correctness with AI feedback

## Development

### Frontend Development
```bash
cd frontend
npm start          # Start with LAN mode (default)
npm run start:tunnel  # Use tunnel mode (slower but works across networks)
```

### Backend Development

With Docker:
```bash
docker-compose up -d --build  # Rebuild after code changes
```

Without Docker:
```bash
cd langchain-server
python main.py  # Auto-reloads on code changes
```

### Git Workflow

This project follows [Conventional Commits](https://www.conventionalcommits.org/):

```bash
# Feature
git commit -m "feat(frontend): add dark mode support"

# Bug fix
git commit -m "fix(backend): resolve translation timeout"

# Chore
git commit -m "chore: update dependencies"
```

See [CLAUDE.md](./CLAUDE.md) for full commit conventions.

## Technology Stack

### Frontend
- **React Native** with Expo
- **Expo Router** (file-based routing)
- **Axios** for API calls
- Platform-specific configurations for web/iOS/Android

### Backend
- **FastAPI** (Python web framework)
- **LangChain** (AI orchestration)
- **OpenAI GPT-4o-mini** (translation feedback)
- **SQLAlchemy** (ORM)
- **SQLite** (database)

### DevOps
- **Docker** and **Docker Compose**
- **Uvicorn** (ASGI server)

## Troubleshooting

### "Could not connect to server"
- Verify backend is running: http://localhost:8000
- Check firewall allows port 8000
- For physical devices: ensure same WiFi and correct IP in `.env`

### "OPENAI_API_KEY not found"
- Make sure `langchain-server/.env` exists with valid API key
- Restart backend after adding the key

### "Port 8000 already in use"
- Find and kill process: `netstat -ano | findstr :8000` (Windows)
- Or change port in `main.py` and `docker-compose.yml`

### Frontend hot reload not working
- Try clearing Expo cache: `npx expo start -c`
- Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`

## Security

⚠️ **Important Security Notes:**

1. **Never commit `.env` files** - They contain sensitive API keys
2. **Use `.env.example`** as templates for team members
3. **Rotate API keys regularly** - Especially if accidentally exposed
4. **Configure CORS properly** - Current setup allows all origins (dev only)
5. **Use HTTPS in production** - Never send API keys over HTTP

## Contributing

1. Create a feature branch: `git checkout -b feat/your-feature`
2. Follow commit conventions (see CLAUDE.md)
3. Test on multiple platforms (web, iOS, Android)
4. Submit pull request

## License

Private project - All rights reserved

## Support

For questions or issues:
1. Check existing documentation in `langchain-server/README.md`
2. Review API docs at http://localhost:8000/docs
3. Check troubleshooting section above
