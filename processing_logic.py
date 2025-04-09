import requests
from bs4 import BeautifulSoup

def clean_url(url, base_url):
    if not url.startswith("http"):
        return base_url + url
    return url

def fetch_description(article_url):
    try:
        response = requests.get(article_url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "lxml")
            paragraph = soup.find("p")
            if paragraph:
                description = paragraph.get_text().split(".")[0] + "."
                return description
    except Exception as e:
        print(f"Error fetching description: {e}")
    return "No description available"