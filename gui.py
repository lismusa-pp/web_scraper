import ttkbootstrap as tb
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import ttk
import threading
from datetime import datetime
import webbrowser
from scraper import scrape_news  # Ensure it returns list of (ID, Portal, Title, Desc, URL)

all_news = []
filtered_news = []

def update_table(tree, data):
    tree.delete(*tree.get_children())
    for news in data[:30]:
        tree.insert("", "end", values=news)

def update_status(status_label, message, footer_label=None):
    status_label.config(text=message)
    status_label.update_idletasks()
    if footer_label:
        footer_label.config(text=f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def fetch_and_display_news(tree, status_label, footer_label, search_entry):
    global all_news, filtered_news
    update_status(status_label, "📰 Fetching latest news...", footer_label)
    try:
        all_news = scrape_news()
        filtered_news = all_news.copy()
        update_table(tree, filtered_news)
        update_status(status_label, "✅ Latest news fetched successfully!", footer_label)
        search_entry.delete(0, tk.END)  # Reset search bar
    except Exception as e:
        update_status(status_label, f"❌ Error: {e}", footer_label)

    if hasattr(fetch_and_display_news, "timer"):
        fetch_and_display_news.timer.cancel()
    fetch_and_display_news.timer = threading.Timer(
        300, lambda: fetch_and_display_news(tree, status_label, footer_label, search_entry)
    )
    fetch_and_display_news.timer.start()

def on_search(tree, query):
    global all_news, filtered_news
    query = query.lower()
    filtered_news = [news for news in all_news if query in news[2].lower() or query in news[3].lower()]
    update_table(tree, filtered_news)

def on_row_click(event, tree):
    item = tree.identify_row(event.y)
    if item:
        url = tree.item(item)["values"][4]
        if url:
            webbrowser.open_new_tab(url)

def launch_gui():
    app = tb.Window(themename="superhero")
    app.title("🗞️ News Scraper & Visualizer")
    app.geometry("1100x640")

    # Header
    header = tb.Frame(app, padding=(10, 5))
    header.pack(fill=X)

    status_label = tb.Label(header, text="Welcome! Click 'Fetch News' to begin.",
                            font=("Segoe UI", 14, "bold"), anchor="w")
    status_label.pack(side=LEFT, padx=10)

    fetch_btn = tb.Button(header, text="🔄 Fetch News", bootstyle="primary outline",
                          command=lambda: fetch_and_display_news(tree, status_label, footer_label, search_entry))
    fetch_btn.pack(side=RIGHT, padx=10)

    # Search Bar
    search_frame = tb.Frame(app, padding=(15, 5))
    search_frame.pack(fill=X)

    search_entry = tb.Entry(search_frame, font=("Segoe UI", 11), width=50)
    search_entry.pack(side=LEFT, padx=(0, 10))

    search_btn = tb.Button(search_frame, text="🔍 Search", bootstyle="info outline",
                           command=lambda: on_search(tree, search_entry.get()))
    search_btn.pack(side=LEFT)

    clear_btn = tb.Button(search_frame, text="❌ Clear", bootstyle="secondary outline",
                          command=lambda: [search_entry.delete(0, tk.END), update_table(tree, all_news)])
    clear_btn.pack(side=LEFT, padx=10)

    # Table
    table_frame = tb.Frame(app)
    table_frame.pack(fill=BOTH, expand=YES, padx=15, pady=10)

    columns = ["ID", "Portal", "Title", "Description", "URL"]
    tree = ttk.Treeview(table_frame, columns=columns, show="headings")
    style = ttk.Style()
    style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"))
    style.configure("Treeview", font=("Segoe UI", 10), rowheight=28)

    for col in columns:
        tree.heading(col, text=col)
        if col == "Description":
            tree.column(col, width=320, anchor="w")
        elif col == "Title":
            tree.column(col, width=280, anchor="w")
        elif col == "URL":
            tree.column(col, width=200)
        else:
            tree.column(col, width=100)

    tree.pack(fill=BOTH, expand=YES)
    tree.bind("<Double-1>", lambda e: on_row_click(e, tree))  # Double-click to open link

    # Footer
    footer = tb.Frame(app)
    footer.pack(fill=X, padx=15, pady=(0, 10))
    footer_label = tb.Label(footer, text="Last updated: --", font=("Segoe UI", 10), anchor="w")
    footer_label.pack(side=LEFT)

    # Initial load
    fetch_and_display_news(tree, status_label, footer_label, search_entry)
    app.mainloop()
