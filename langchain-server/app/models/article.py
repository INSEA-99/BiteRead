from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class Article(Base):
    """
    Article model for storing reading content

    IMPORTANT: For VOA-sourced articles, this stores ONLY AI-rewritten content,
    NOT the original VOA text, to avoid copyright issues.
    """
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)  # AI-generated reading passage
    created_at = Column(DateTime, default=datetime.utcnow)

    # New fields for VOA-sourced content
    difficulty = Column(String(50), nullable=True)  # 'beginner' or 'intermediate'
    category = Column(String(100), nullable=True)   # 'science', 'health', 'as_it_is', etc.
    source_url = Column(String(1000), nullable=True)  # Link to original article (reference only)
    vocabulary = Column(JSON, nullable=True)  # List of {word, definition}
    questions = Column(JSON, nullable=True)   # List of comprehension questions
    published_date = Column(DateTime, nullable=True)  # Original article publish date

    sentences = relationship("Sentence", back_populates="article", cascade="all, delete-orphan")


class Sentence(Base):
    __tablename__ = "sentences"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    text = Column(Text, nullable=False)
    order = Column(Integer, nullable=False)

    article = relationship("Article", back_populates="sentences")
    progress = relationship("UserProgress", back_populates="sentence")
