import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import Optional


class TranslationFeedback(BaseModel):
    """Structure for LLM feedback response"""
    result: str = Field(description="Evaluation result: 'perfect', 'good', or 'incorrect'")
    feedback: Optional[str] = Field(
        description="Short feedback message (1-2 sentences max)"
    )
    is_correct: bool = Field(description="Whether the translation is acceptable (perfect or good)")


class TranslationService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        # Use gpt-4o-mini for cost efficiency
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3,  # Low temperature for consistent feedback
            api_key=api_key
        )

        self.parser = PydanticOutputParser(pydantic_object=TranslationFeedback)

        # Create prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an English teacher evaluating Korean translations of English sentences.

Evaluate the translation into one of three levels:
1. **perfect**: Translation conveys the correct meaning with proper vocabulary and grammar
   - Ignore spacing errors, small typos, and formal/informal variations
   - Focus ONLY on whether the meaning is accurately conveyed
2. **good**: Translation conveys the general idea but has noticeable vocabulary or grammar issues
   - Use this when word choice is awkward or grammar is unclear
3. **incorrect**: Translation is wrong or misses key meaning
   - Use this only when the meaning is significantly different or completely wrong

CRITICAL RULES - These errors should NOT prevent 'perfect' rating:
1. Spacing errors: "매트위에" vs "매트 위에" → Both are PERFECT
2. Formal/informal: "앉아있다" vs "앉아있습니다" → Both are PERFECT
3. Small typos: If meaning is clear despite typo → PERFECT
4. Minor particle variations: If meaning unchanged → PERFECT

Focus ONLY on:
- Does the translation accurately convey the meaning?
- Are the key vocabulary words correct?
- Is the basic grammar structure understandable?

If YES to all three → Mark as 'perfect', regardless of spacing/typos/formality

Response format:
- result: 'perfect', 'good', or 'incorrect'
- is_correct: true for 'perfect' or 'good', false for 'incorrect'
- feedback:
  - For 'perfect': Short encouraging message ONLY (e.g., "완벽합니다!" or "정확합니다!")
    * Do NOT mention spacing, typos, or formality issues
    * Keep it simple and positive
  - For 'good': Brief note on what could be improved (1-2 sentences)
    * Only mention significant vocabulary or grammar issues
  - For 'incorrect': SHORT hint pointing to the issue (1-2 sentences, do NOT give the answer)

Feedback should:
- ALWAYS be in formal Korean (존댓말) - use "~습니다/~세요" endings
- NOT give the answer directly
- For 'perfect': NEVER mention spacing, typos, or formality - just praise
- For 'good': Only point to actual vocabulary/grammar issues, NOT spacing/typos
- Be encouraging and educational

{format_instructions}"""),
            ("user", """Original English: {original_sentence}
Student's Korean translation: {user_translation}

Evaluate the translation:""")
        ])

    def check_translation(self, original_sentence: str, user_translation: str) -> TranslationFeedback:
        """
        Check user's translation against original sentence using LLM.
        Returns feedback with is_correct flag and optional hint.
        """
        chain = self.prompt | self.llm | self.parser

        result = chain.invoke({
            "original_sentence": original_sentence,
            "user_translation": user_translation,
            "format_instructions": self.parser.get_format_instructions()
        })

        return result
