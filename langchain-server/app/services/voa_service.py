import feedparser
from typing import List, Dict, Optional
from datetime import datetime


class VOAService:
    """Service for fetching articles from VOA Learning English RSS feeds"""

    # VOA Learning English RSS feed URLs by difficulty and category
    RSS_FEEDS = {
        'intermediate': {
            'as_it_is': 'https://learningenglish.voanews.com/api/zkm-ql-vomx-tpej-rqi',  # News magazine
            'science': 'https://learningenglish.voanews.com/api/zmg_pl-vomx-tpeymtm',   # Science & Technology
            'health': 'https://learningenglish.voanews.com/api/zmmpql-vomx-tpey-_q',    # Health & Lifestyle
        },
        'beginner': {
            'news_words': 'https://learningenglish.voanews.com/api/z_qoteupeo',  # News Words (placeholder - need to find actual URL)
        }
    }

    def fetch_articles(
        self,
        difficulty: str = 'intermediate',
        category: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Fetch articles from VOA Learning English RSS feeds

        Args:
            difficulty: 'beginner' or 'intermediate'
            category: Specific category (e.g., 'as_it_is', 'science', 'health')
                     If None, fetches from all categories for the difficulty level
            limit: Maximum number of articles to fetch

        Returns:
            List of article dictionaries with metadata (NOT the full original text)
        """
        articles = []

        if difficulty not in self.RSS_FEEDS:
            raise ValueError(f"Invalid difficulty: {difficulty}. Must be 'beginner' or 'intermediate'")

        feeds_to_fetch = {}
        if category:
            if category not in self.RSS_FEEDS[difficulty]:
                raise ValueError(f"Invalid category: {category} for difficulty: {difficulty}")
            feeds_to_fetch[category] = self.RSS_FEEDS[difficulty][category]
        else:
            feeds_to_fetch = self.RSS_FEEDS[difficulty]

        for cat_name, feed_url in feeds_to_fetch.items():
            feed = feedparser.parse(feed_url)

            for entry in feed.entries[:limit]:
                article = self._extract_article_metadata(entry, difficulty, cat_name)
                articles.append(article)

        return articles[:limit]

    def _extract_article_metadata(
        self,
        entry: feedparser.FeedParserDict,
        difficulty: str,
        category: str
    ) -> Dict:
        """
        Extract metadata from RSS feed entry

        IMPORTANT: This method extracts ONLY metadata and summary.
        The full original text is NOT stored to avoid copyright issues.
        """
        return {
            'title': entry.get('title', ''),
            'summary': entry.get('summary', ''),  # Short summary only
            'source_url': entry.get('link', ''),  # Link to original article
            'published_date': self._parse_date(entry.get('published', '')),
            'difficulty': difficulty,
            'category': category,
            # NOTE: Full original content is NOT included here
            # It will only be used temporarily for AI rewriting
        }

    def _parse_date(self, date_string: str) -> Optional[str]:
        """Parse date string to ISO format"""
        try:
            # RSS dates are typically in RFC 2822 format
            from email.utils import parsedate_to_datetime
            dt = parsedate_to_datetime(date_string)
            return dt.isoformat()
        except Exception:
            return None

    def fetch_full_content(self, article_url: str) -> Optional[str]:
        """
        Fetch full article content from URL for AI rewriting

        IMPORTANT: This content should ONLY be used as reference for AI rewriting
        and should NOT be stored in the database.

        Args:
            article_url: URL to the VOA article

        Returns:
            Full article text (for temporary AI processing only)
        """
        # TODO: Implement web scraping if needed
        # For now, we'll use the summary from RSS as reference
        # In production, you might want to scrape the full article
        # using BeautifulSoup or similar
        return None
