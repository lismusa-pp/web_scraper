import csv
import time
import random
import logging
import requests

from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

from processing_logic import clean_url, fetch_description
from newsportals_url import NEWS_PORTAL

# Setup logging
logging.basicConfig(
    filename="scraper.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com"
}

EXCLUDE_PHRASES = {
    "skip to content", "sign in", "log in", "menu",
    "home", "search", "live", "read more"
}


def is_valid_title(title: str) -> bool:
    return bool(title and len(title) >= 10 and not any(p in title.lower() for p in EXCLUDE_PHRASES))


def is_likely_news(article) -> bool:
    parent_classes = " ".join(article.get("class", []))
    return (
        article.find_parent(["h1", "h2", "h3", "article"]) or
        "title" in parent_classes.lower() or
        "headline" in parent_classes.lower()
    )


def scrape_single_portal(portal: str, base_url: str, session: requests.Session, max_articles: int = 2) -> list:
    news_items = []

    try:
        response = session.get(base_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")

        # Target common news elements
        article_links = soup.select("article a, h1 a, h2 a, h3 a, .headline a, .title a")
        seen_titles = set()
        count = 0

        for article in article_links:
            title = article.get_text(strip=True)

            if not is_valid_title(title) or title in seen_titles:
                continue
            if not is_likely_news(article):
                continue

            full_url = clean_url(article.get("href"), base_url)

            try:
                description = fetch_description(full_url)  # Still potentially slow
            except Exception as e:
                logging.warning(f"Description fetch failed for {full_url}: {e}")
                description = ""

            news_items.append((count + 1, portal, title, description, full_url))
            seen_titles.add(title)
            count += 1

            if count >= max_articles:
                break

        time.sleep(random.uniform(1.0, 2.5))  # Respectful pause

    except Exception as e:
        logging.error(f"[{portal}] Error: {e}")

    return news_items


def scrape_news(max_articles_per_portal: int = 2) -> list:
    """
    Parallel scraping of news portals.
    Returns a list of (ID, Portal, Title, Description, URL)
    """
    all_news = []
    session = requests.Session()
    session.headers.update(HEADERS)

    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {
            executor.submit(scrape_single_portal, portal, url, session, max_articles_per_portal): portal
            for portal, url in NEWS_PORTAL.items()
        }

        for future in as_completed(futures):
            try:
                result = future.result()
                all_news.extend(result)
            except Exception as e:
                logging.error(f"Thread failed: {e}")

    _save_to_csv(all_news)
    return all_news


def _save_to_csv(data: list, filename: str = "news_data.csv") -> None:
    try:
        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["ID", "Portal", "Title", "Description", "URL to Portal"])
            writer.writerows(data)
    except Exception as e:
        logging.error(f"CSV Write Failed: {e}")
