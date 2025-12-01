from pydantic import BaseModel
from typing import Optional


class TranslationCheckRequest(BaseModel):
    sentence_id: int
    user_translation: str


class TranslationCheckResponse(BaseModel):
    is_correct: bool
    feedback: Optional[str] = None
    next_sentence_id: Optional[int] = None
    original_sentence: str
