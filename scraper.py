import csv
import requests
from bs4 import BeautifulSoup
from processing_logic import clean_url, fetch_description
from newsportals_url import NEWS_PORTAL

def scrape_news():
    all_news = []
    for portal, url in NEWS_PORTAL.items():
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
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
                if count >= 2:
                    break
        except Exception as e:
            print(f"Error fetching from {portal}: {e}")
            continue

    with open("news_data.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["ID", "Portal", "Title", "Description", "URL to Portal"])
        writer.writerows(all_news)

    return all_news



