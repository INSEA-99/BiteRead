# BiteRead LangChain Server

AI-powered English learning backend with translation feedback using LangChain and OpenAI.

## Prerequisites

- Python 3.11+
- OpenAI API Key
- Docker (optional, for containerized deployment)

## Setup

### 1. Environment Variables

Copy the example environment file and fill in your API keys:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=your_actual_api_key_here
```

⚠️ **Important**: Never commit your `.env` file to version control!

### 2. Local Development (without Docker)

#### Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Unix/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Run the Server

```bash
python main.py
```

The server will start at `http://localhost:8000`

API documentation available at: `http://localhost:8000/docs`

### 3. Docker Development (recommended)

#### Build and Run with Docker Compose

From the project root directory:

```bash
# Build and start the container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the container
docker-compose down
```

The server will start at `http://localhost:8000`

#### Rebuild After Changes

```bash
docker-compose up -d --build
```

## API Endpoints

- `GET /` - Server info
- `GET /docs` - Interactive API documentation
- `POST /api/articles` - Create new article
- `GET /api/articles` - List all articles
- `GET /api/articles/{id}` - Get article by ID
- `POST /api/translation/check` - Check translation correctness

## Database

This project uses SQLite for simplicity. The database file `biteread.db` is created automatically on first run.

Database location:
- Local: `./biteread.db`
- Docker: Persisted in `./data/` volume

## Helper Scripts

### Add Test Article

```bash
python add_article.py
```

This script adds a sample article to the database for testing.

## Project Structure

```
langchain-server/
├── app/
│   ├── endpoints/       # API route handlers
│   ├── models/          # SQLAlchemy database models
│   ├── schemas/         # Pydantic schemas for validation
│   ├── services/        # Business logic (LangChain integration)
│   └── database.py      # Database configuration
├── main.py              # FastAPI application entry point
├── requirements.txt     # Python dependencies
├── Dockerfile           # Docker image definition
├── .env.example         # Example environment variables
└── README.md
```

## Development Tips

- The server automatically reloads when code changes (both local and Docker)
- Use `/docs` endpoint for interactive API testing
- Check logs for debugging: `docker-compose logs -f` (Docker) or terminal output (local)

## Security Notes

- Never commit your `.env` file
- Rotate your OpenAI API keys regularly
- In production, configure CORS properly in `main.py` (currently set to allow all origins)
- Use environment-specific `.env` files (`.env.development`, `.env.production`)

## Troubleshooting

### "OPENAI_API_KEY not found"
Make sure your `.env` file exists and contains the API key.

### Port 8000 already in use
Stop any existing process using port 8000 or change the port in `main.py` and `docker-compose.yml`.

### Database locked errors
Make sure only one instance of the server is running.
