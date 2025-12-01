from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import TranslationCheckRequest, TranslationCheckResponse
from ..services import TranslationService, ArticleService
from ..models import Sentence

router = APIRouter(prefix="/api/translation", tags=["translation"])

# Lazy initialization of translation service
_translation_service = None


def get_translation_service():
    """Get or create translation service singleton"""
    global _translation_service
    if _translation_service is None:
        _translation_service = TranslationService()
    return _translation_service


@router.post("/check", response_model=TranslationCheckResponse)
def check_translation(
    request: TranslationCheckRequest,
    db: Session = Depends(get_db)
):
    """
    Check user's translation against the original sentence.
    Returns feedback and next sentence if correct.
    """
    # Get the sentence
    sentence = db.query(Sentence).filter(Sentence.id == request.sentence_id).first()
    if not sentence:
        raise HTTPException(status_code=404, detail="Sentence not found")

    try:
        # Get LLM feedback
        translation_service = get_translation_service()
        feedback_result = translation_service.check_translation(
            original_sentence=sentence.text,
            user_translation=request.user_translation
        )

        # Prepare response
        response = TranslationCheckResponse(
            is_correct=feedback_result.is_correct,
            feedback=feedback_result.feedback,
            original_sentence=sentence.text,
            next_sentence_id=None
        )

        # If correct, get next sentence
        if feedback_result.is_correct:
            next_sentence = ArticleService.get_next_sentence(db, request.sentence_id)
            if next_sentence:
                response.next_sentence_id = next_sentence.id

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation check failed: {str(e)}")
