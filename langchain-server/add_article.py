"""
간단하게 글을 추가하는 스크립트
사용법: python add_article.py
"""
import requests

API_URL = "http://localhost:8000/api/articles/"

# 추가할 글
articles = [
    {
        "title": "Why singing is good for your health",
        "content": """It's that time of year when the air starts to tinkle with angelic voices. All that harking and heralding. It's joyful and triumphant.

But these bands of tinsel-draped singers may be on to something. Whether they realise it or not as they fill shopping centres with jubilant song, they are also giving their own health a boost.

From the brain to the heart, singing has been found to bring a wide range of benefits to those who do it. It can draw people closer together and even suppress pain. So might it be worth raising your own voice in good cheer?"""
    },
    {
        "title": "A Simple Morning Routine",
        "content": """I wake up at 6 AM every morning. The first thing I do is drink a glass of water. Then I go for a short walk around my neighborhood.

After my walk, I make breakfast. I usually have eggs and toast. While eating, I read the news on my phone.

By 7:30 AM, I'm ready to start my day. This simple routine helps me feel energized and focused."""
    }
]

def add_article(title, content):
    try:
        response = requests.post(API_URL, json={"title": title, "content": content})
        if response.status_code == 201:
            data = response.json()
            print(f"✓ Added: {title}")
            print(f"  - ID: {data['id']}")
            print(f"  - Sentences: {len(data['sentences'])}")
            return True
        else:
            print(f"✗ Failed: {title}")
            print(f"  Status: {response.status_code}")
            print(f"  Error: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Error adding {title}: {e}")
        return False

if __name__ == "__main__":
    print("Adding articles to BiteRead...\n")

    success_count = 0
    for article in articles:
        if add_article(article["title"], article["content"]):
            success_count += 1
        print()

    print(f"\nDone! Added {success_count}/{len(articles)} articles.")
    print(f"View at: http://localhost:8000/docs")
