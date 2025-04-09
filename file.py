from bs4 import BeautifulSoup
import requests
import lxml
import csv
import tkinter as tk
from tkinter import ttk
import threading
import time

# List of news portals with their URLs
news_portals = {
    "BBC News": "https://www.bbc.com/news",
    "CNN": "https://edition.cnn.com/world",
    "Reuters": "https://www.reuters.com/world/",
    "Al Jazeera": "https://www.aljazeera.com/news/",
    "The Guardian": "https://www.theguardian.com/international",
    "New York Times": "https://www.nytimes.com/section/world",
    "Washington Post": "https://www.washingtonpost.com/world/",
    "Fox News": "https://www.foxnews.com/world",
    "ABC News": "https://abcnews.go.com/International",
    "CBS News": "https://www.cbsnews.com/world/",
    "NBC News": "https://www.nbcnews.com/world",
    "Bloomberg": "https://www.bloomberg.com/international",
    "CNBC": "https://www.cnbc.com/world-news/",
    "Forbes": "https://www.forbes.com/international/",
    "The Hindu": "https://www.thehindu.com/news/international/",
    "Times of India": "https://timesofindia.indiatimes.com/world",
    "Japan Times": "https://www.japantimes.co.jp/news/",
    "DW News": "https://www.dw.com/en/top-stories/s-9097",
    "France 24": "https://www.france24.com/en/",
    "Sydney Morning Herald": "https://www.smh.com.au/world"
}

# Initialize data storage
all_news = []

# Utility function for clean URL
def clean_url(url, base_url):
    if not url.startswith("http"):
        return base_url + url
    return url

# Function to fetch the first sentence of the article from the article's URL
def fetch_description(article_url):
    try:
        response = requests.get(article_url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "lxml")
            # Find the first paragraph with meaningful content
            paragraph = soup.find("p")
            if paragraph:
                # Take the first sentence and strip unnecessary spaces
                description = paragraph.get_text().split(".")[0] + "."
                return description
    except Exception as e:
        print(f"Error fetching description: {e}")
    return "No description available"

# GUI Setup
def update_status(message):
    status_label.config(text=message)
    root.update_idletasks()

def fetch_news():
    global all_news
    all_news.clear()
    update_status("Fetching latest news...")

    new_articles = []

    for portal, url in news_portals.items():
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                continue

            soup = BeautifulSoup(response.text, "lxml")
            # Try to find meaningful titles inside headlines
            article_links = soup.find_all("a", href=True)

            count = 0
            for article in article_links:
                title = article.get_text(strip=True)
                if not title or len(title) < 10:
                    continue
                # Skip common non-headline phrases
                if any(phrase in title.lower() for phrase in [
                    "skip to content", "sign in", "log in", "menu", "home", "search", "live", "read more"
                ]):
                    continue
                # Try to find links that are part of headlines or titles
                parent_classes = " ".join(article.get("class", []))
                if (
                    article.find_parent(["h1", "h2", "h3"]) or
                    "title" in parent_classes.lower() or
                    "headline" in parent_classes.lower()
                ):
                    article_url = clean_url(article["href"], url)
                    description = fetch_description(article_url)

                    if not any(news[4] == article_url for news in all_news):
                        count += 1
                        new_articles.append([count, portal, title, description, article_url])

                if count >= 2:
                    break

        except Exception as e:
            print(f"Error fetching from {portal}: {e}")
            continue

    all_news.extend(new_articles)

    with open("news_data.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["ID", "Portal", "Title", "Description", "URL to Portal"])
        writer.writerows(all_news)

    update_table()
    update_status("Latest news fetched successfully!")

    if hasattr(fetch_news, "timer"):
        fetch_news.timer.cancel()
    fetch_news.timer = threading.Timer(300, fetch_news)
    fetch_news.timer.start()


def update_table():
    for row in tree.get_children():
        tree.delete(row)
    
    for news in all_news[:20]:  # Show latest 10 news
        tree.insert("", "end", values=news)

# Tkinter GUI with improved design
root = tk.Tk()
root.title("News Scraper & Visualizer")
root.geometry("900x500")
root.configure(bg="#f4f4f4")  # Background color

# Header Frame for status and button
header_frame = tk.Frame(root, bg="#4CAF50", pady=10)
header_frame.pack(fill="x")

# Status Label
status_label = tk.Label(header_frame, text="Click 'Fetch News' to start", font=("Arial", 14), fg="white", bg="#4CAF50")
status_label.pack()

# Fetch Button with styling
fetch_button = tk.Button(header_frame, text="Fetch News", font=("Arial", 14), bg="#ffffff", fg="#4CAF50", command=fetch_news, relief="flat", padx=20, pady=10)
fetch_button.pack(pady=10)

# News Table Frame
table_frame = tk.Frame(root, bg="#f4f4f4")
table_frame.pack(expand=True, fill="both", padx=20, pady=10)

# Table for displaying the news
columns = ("ID", "Portal", "Title", "Description", "URL to Portal")
tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

# Style for Treeview
style = ttk.Style()
style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#4CAF50", foreground="white")
style.configure("Treeview", font=("Arial", 10), rowheight=30)

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=180, anchor="w")

tree.pack(expand=True, fill="both")

# Start automatic fetching every 5 minutes
fetch_news()

root.mainloop()
