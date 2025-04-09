import csv
import random
import time
import requests
from bs4 import BeautifulSoup
from processing_logic import clean_url, fetch_description
from newsportals_url import news_portals

# List of possible User-Agent strings to use for each request
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.64 Safari/537.36"
]

# Function to simulate random delays between requests
def random_delay(min_delay=1, max_delay=5):
    time.sleep(random.uniform(min_delay, max_delay))

# Function to fetch news articles (simplified)
def fetch_news(url):
    headers = {
        "User-Agent": random.choice(user_agents),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
    }

    # Removed proxy to simplify for debugging
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for non-2xx responses
        random_delay()  # Simulate random delay between requests
        return response
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def scrape_news():
    all_news = []
    for portal, url in news_portals.items():
        try:
            print(f"Fetching news from: {portal}")
            response = fetch_news(url)
            if not response:
                print(f"Failed to fetch from {portal}, skipping.")
                continue

            soup = BeautifulSoup(response.text, "lxml")
            article_links = soup.find_all("a", href=True)

            count = 0
            for article in article_links:
                title = article.get_text(strip=True)
                if not title or len(title) < 10:
                    continue
                if any(phrase in title.lower() for phrase in [
                    "skip to content", "sign in", "log in", "menu", "home", "search", "live", "read more"
                ]):
                    continue

                parent_classes = " ".join(article.get("class", []))
                if (
                    article.find_parent(["h1", "h2", "h3"]) or
                    "title" in parent_classes.lower() or
                    "headline" in parent_classes.lower()
                ):
                    article_url = clean_url(article["href"], url)
                    description = fetch_description(article_url)
                    all_news.append([count + 1, portal, title, description, article_url])
                    count += 1
                if count >= 2:  # Limiting to the first 2 articles per portal
                    break
        except Exception as e:
            print(f"Error fetching from {portal}: {e}")
            continue

    # Save the scraped news to a CSV file
    with open("news_data.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["ID", "Portal", "Title", "Description", "URL to Portal"])
        writer.writerows(all_news)

    return all_news

# Example of how this can be used
if __name__ == "__main__":
    news_data = scrape_news()
    print("News Scraping Complete!")
    print(news_data)
