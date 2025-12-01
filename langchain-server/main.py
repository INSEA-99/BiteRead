from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.endpoints import articles_router, translation_router
from app.database import init_db

# Load environment variables
load_dotenv()

app = FastAPI(
    title="BiteRead LangChain Server",
    description="AI-powered English learning with translation feedback",
    version="1.0.0"
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()

# Include routers
app.include_router(articles_router)
app.include_router(translation_router)


@app.get("/")
def root():
    return {
        "message": "BiteRead LangChain server running!",
        "docs": "/docs",
        "endpoints": {
            "articles": "/api/articles",
            "translation_check": "/api/translation/check"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
