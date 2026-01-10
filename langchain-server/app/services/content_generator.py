import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List, Optional


class VocabularyItem(BaseModel):
    """Vocabulary word with definition"""
    word: str = Field(description="The vocabulary word")
    definition: str = Field(description="Simple definition in English")


class ComprehensionQuestion(BaseModel):
    """Reading comprehension question"""
    question: str = Field(description="The question text")
    options: List[str] = Field(description="4 multiple choice options")
    correct_answer: int = Field(description="Index of correct answer (0-3)")


class GeneratedContent(BaseModel):
    """Complete generated reading content"""
    reading_passage: str = Field(description="The rewritten reading passage (150-250 words)")
    vocabulary: List[VocabularyItem] = Field(description="5 vocabulary words with definitions")
    questions: List[ComprehensionQuestion] = Field(description="3 comprehension questions")


class ContentGeneratorService:
    """Service for generating original reading content from VOA articles using AI"""

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        # Use GPT-4o-mini for cost efficiency
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,  # Some creativity for rewriting
            api_key=api_key
        )

        self.parser = PydanticOutputParser(pydantic_object=GeneratedContent)

        # Prompt template for copyright-safe content generation
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an English learning content creator.

Using the following article ONLY as a reference for ideas and facts,
rewrite it into a completely new reading passage for English learners.

CRITICAL COPYRIGHT RULES:
- Do NOT copy any sentences or phrases from the original text
- Do NOT keep the same sentence structure
- Change wording, sentence order, and paragraph structure
- Use simpler and more neutral expressions suitable for learners
- The output must be an ORIGINAL educational text, not a summary
- Do not mention VOA or the original source in the text

CONTENT REQUIREMENTS:
1. Reading passage: 150-250 words
   - Written in clear, natural English
   - Suitable for {difficulty} level learners
   - Present tense preferred for timeless facts
   - Past tense for specific events

2. Vocabulary: 5 key words
   - Select important words from YOUR rewritten text
   - Provide simple definitions (one sentence each)

3. Comprehension questions: 3 questions
   - Based on YOUR rewritten passage
   - Multiple choice with 4 options each
   - Test understanding of main ideas and details

{format_instructions}"""),
            ("user", """Difficulty level: {difficulty}
Category: {category}

Original article reference:
Title: {title}
Summary: {summary}

Create a completely new reading passage based on these ideas:""")
        ])

    def generate_content(
        self,
        title: str,
        summary: str,
        difficulty: str,
        category: str
    ) -> GeneratedContent:
        """
        Generate original reading content from article reference

        IMPORTANT: The input article is used ONLY as reference.
        The output is completely rewritten content.

        Args:
            title: Original article title (reference only)
            summary: Original article summary (reference only)
            difficulty: 'beginner' or 'intermediate'
            category: Article category

        Returns:
            GeneratedContent with reading passage, vocabulary, and questions
        """
        chain = self.prompt | self.llm | self.parser

        result = chain.invoke({
            "title": title,
            "summary": summary,
            "difficulty": difficulty,
            "category": category,
            "format_instructions": self.parser.get_format_instructions()
        })

        return result
