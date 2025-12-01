from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class UserProgress(Base):
    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True, index=True)
    sentence_id = Column(Integer, ForeignKey("sentences.id"), nullable=False)
    user_translation = Column(String(500))
    is_correct = Column(Boolean, default=False)
    attempts = Column(Integer, default=0)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    sentence = relationship("Sentence", back_populates="progress")
