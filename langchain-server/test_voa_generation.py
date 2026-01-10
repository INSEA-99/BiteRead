"""
Test script for VOA content generation

This script tests the entire flow:
1. Fetch VOA RSS feed
2. Generate AI-rewritten content
3. Store in database
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.voa_service import VOAService
from app.services.content_generator import ContentGeneratorService

def test_voa_fetch():
    """Test fetching VOA articles"""
    print("\n=== Testing VOA RSS Feed Fetching ===\n")

    voa = VOAService()

    try:
        # Test intermediate level
        print("Fetching intermediate articles...")
        articles = voa.fetch_articles(difficulty='intermediate', limit=2)

        for idx, article in enumerate(articles, 1):
            print(f"\nArticle {idx}:")
            print(f"  Title: {article['title']}")
            print(f"  Category: {article['category']}")
            print(f"  Published: {article['published_date']}")
            print(f"  URL: {article['source_url']}")
            print(f"  Summary: {article['summary'][:100]}...")

        return articles[0] if articles else None

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_content_generation(voa_article):
    """Test AI content generation"""
    print("\n\n=== Testing AI Content Generation ===\n")

    if not voa_article:
        print("No article to test with")
        return

    generator = ContentGeneratorService()

    try:
        print("Generating AI-rewritten content...")
        print(f"Source: {voa_article['title']}\n")

        generated = generator.generate_content(
            title=voa_article['title'],
            summary=voa_article['summary'],
            difficulty=voa_article['difficulty'],
            category=voa_article['category']
        )

        print("✓ Generation successful!\n")
        print("=" * 60)
        print("GENERATED READING PASSAGE:")
        print("=" * 60)
        print(generated.reading_passage)
        print("\n" + "=" * 60)
        print("VOCABULARY (5 words):")
        print("=" * 60)
        for vocab in generated.vocabulary:
            print(f"  • {vocab.word}: {vocab.definition}")

        print("\n" + "=" * 60)
        print("COMPREHENSION QUESTIONS (3 questions):")
        print("=" * 60)
        for idx, q in enumerate(generated.questions, 1):
            print(f"\nQ{idx}: {q.question}")
            for opt_idx, option in enumerate(q.options):
                marker = "✓" if opt_idx == q.correct_answer else " "
                print(f"  {marker} {chr(65 + opt_idx)}. {option}")

        print("\n" + "=" * 60)
        print("✓ Content generation test completed!")
        print("=" * 60)

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    # Test VOA fetching
    article = test_voa_fetch()

    # Test content generation
    if article:
        test_content_generation(article)
    else:
        print("\nCould not fetch VOA article for testing")
