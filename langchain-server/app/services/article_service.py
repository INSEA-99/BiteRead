import re
from sqlalchemy.orm import Session
from ..models import Article, Sentence


class ArticleService:
    @staticmethod
    def split_into_sentences(text: str) -> list[str]:
        """
        Split text into sentences using regex.
        Handles common sentence endings: . ! ?
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())

        # Split on sentence boundaries
        # Matches . ! ? followed by space and capital letter or end of string
        sentence_pattern = r'(?<=[.!?])\s+(?=[A-Z])|(?<=[.!?])$'
        sentences = re.split(sentence_pattern, text)

        # Clean up sentences
        sentences = [s.strip() for s in sentences if s.strip()]

        return sentences

    @staticmethod
    def create_article(db: Session, title: str, content: str) -> Article:
        """
        Create article and split content into sentences.
        """
        # Create article
        article = Article(title=title, content=content)
        db.add(article)
        db.flush()  # Get article.id

        # Split into sentences
        sentences_text = ArticleService.split_into_sentences(content)

        # Create sentence records
        for order, sentence_text in enumerate(sentences_text, start=1):
            sentence = Sentence(
                article_id=article.id,
                text=sentence_text,
                order=order
            )
            db.add(sentence)

        db.commit()
        db.refresh(article)

        return article

    @staticmethod
    def get_article(db: Session, article_id: int) -> Article:
        """Get article by ID with sentences."""
        return db.query(Article).filter(Article.id == article_id).first()

    @staticmethod
    def get_all_articles(db: Session, skip: int = 0, limit: int = 100) -> list[Article]:
        """Get all articles."""
        return db.query(Article).offset(skip).limit(limit).all()

    @staticmethod
    def get_next_sentence(db: Session, current_sentence_id: int) -> Sentence:
        """Get the next sentence in the same article."""
        current = db.query(Sentence).filter(Sentence.id == current_sentence_id).first()
        if not current:
            return None

        return db.query(Sentence).filter(
            Sentence.article_id == current.article_id,
            Sentence.order == current.order + 1
        ).first()
