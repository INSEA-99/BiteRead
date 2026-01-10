from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..schemas import ArticleCreate, ArticleResponse
from ..services import ArticleService
from ..services.voa_service import VOAService
from ..services.content_generator import ContentGeneratorService

router = APIRouter(prefix="/api/articles", tags=["articles"])

# Services will be initialized on first use to ensure .env is loaded
_voa_service = None
_content_generator = None

def get_voa_service():
    """Get or create VOA service instance"""
    global _voa_service
    if _voa_service is None:
        _voa_service = VOAService()
    return _voa_service

def get_content_generator():
    """Get or create content generator instance"""
    global _content_generator
    if _content_generator is None:
        _content_generator = ContentGeneratorService()
    return _content_generator


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


@router.delete("/{article_id}", status_code=200)
def delete_article(article_id: int, db: Session = Depends(get_db)):
    """
    Delete a specific article by ID.
    This will also delete all associated sentences due to cascade delete.
    """
    from ..models.article import Article

    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    db.delete(article)
    db.commit()

    return {
        "message": f"Article {article_id} deleted successfully",
        "deleted_id": article_id
    }


@router.post("/generate-from-voa", status_code=201)
def generate_from_voa(
    difficulty: str = Query(..., description="'beginner' or 'intermediate'"),
    category: Optional[str] = Query(None, description="VOA category (e.g., 'as_it_is', 'science', 'health')"),
    limit: int = Query(1, description="Number of articles to generate"),
    db: Session = Depends(get_db)
):
    """
    Generate new reading content from VOA Learning English RSS feeds.

    This endpoint:
    1. Fetches articles from VOA RSS feeds (reference only)
    2. Uses AI to rewrite them into original educational content
    3. Stores ONLY the AI-generated content (not original VOA text)
    4. Returns the generated articles

    IMPORTANT: Original VOA content is NOT stored, only used as reference for AI rewriting.
    """
    try:
        # Get service instances
        voa_svc = get_voa_service()
        content_gen = get_content_generator()

        # Step 1: Fetch VOA articles (metadata only)
        voa_articles = voa_svc.fetch_articles(
            difficulty=difficulty,
            category=category,
            limit=limit
        )

        if not voa_articles:
            raise HTTPException(status_code=404, detail="No VOA articles found")

        generated_articles = []

        # Step 2: Generate content for each article
        for voa_article in voa_articles:
            # Generate AI-rewritten content
            generated_content = content_gen.generate_content(
                title=voa_article['title'],
                summary=voa_article['summary'],
                difficulty=difficulty,
                category=voa_article['category']
            )

            # Step 3: Store in database (AI-generated content only)
            new_article = ArticleService.create_article(
                db=db,
                title=voa_article['title'],
                content=generated_content.reading_passage
            )

            # Update with VOA-specific fields
            from ..models.article import Article
            db_article = db.query(Article).filter(Article.id == new_article.id).first()
            db_article.difficulty = difficulty
            db_article.category = voa_article['category']
            db_article.source_url = voa_article['source_url']
            db_article.vocabulary = [v.dict() for v in generated_content.vocabulary]
            db_article.questions = [q.dict() for q in generated_content.questions]

            if voa_article.get('published_date'):
                from datetime import datetime
                db_article.published_date = datetime.fromisoformat(voa_article['published_date'])

            db.commit()
            db.refresh(db_article)

            generated_articles.append({
                "id": db_article.id,
                "title": db_article.title,
                "difficulty": db_article.difficulty,
                "category": db_article.category,
                "source_url": db_article.source_url,
            })

        return {
            "message": f"Successfully generated {len(generated_articles)} articles",
            "articles": generated_articles
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating content: {str(e)}")
