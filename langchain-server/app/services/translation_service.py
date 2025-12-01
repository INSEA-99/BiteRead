import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import Optional


class TranslationFeedback(BaseModel):
    """Structure for LLM feedback response"""
    is_correct: bool = Field(description="Whether the translation is correct")
    feedback: Optional[str] = Field(
        description="Short hint if translation is incorrect (1-2 sentences max)"
    )


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

Your task:
1. Check if the student's Korean translation captures the meaning of the original English sentence
2. If correct: respond with is_correct=true, feedback=null
3. If incorrect or incomplete: respond with is_correct=false and provide a SHORT hint (1-2 sentences)

Hints should:
- NOT give the answer directly
- Point to what to reconsider (grammar, vocabulary, tense, word choice)
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
