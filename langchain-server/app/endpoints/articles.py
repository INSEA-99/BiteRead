from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..schemas import ArticleCreate, ArticleResponse
from ..services import ArticleService

router = APIRouter(prefix="/api/articles", tags=["articles"])


@router.post("/", response_model=ArticleResponse, status_code=201)
def create_article(article: ArticleCreate, db: Session = Depends(get_db)):
    """
    Create a new article and automatically split into sentences.
    """
    try:
        new_article = ArticleService.create_article(
            db=db,
            title=article.title,
            content=article.content
        )
        return new_article
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[ArticleResponse])
def get_articles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all articles with their sentences.
    """
    articles = ArticleService.get_all_articles(db=db, skip=skip, limit=limit)
    return articles


@router.get("/{article_id}", response_model=ArticleResponse)
def get_article(article_id: int, db: Session = Depends(get_db)):
    """
    Get a specific article by ID with all sentences.
    """
    article = ArticleService.get_article(db=db, article_id=article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article
