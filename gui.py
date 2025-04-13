import ttkbootstrap as tb
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from datetime import datetime
import webbrowser
import json
import os
import ctypes  # Needed for taskbar icon fix
from scraper import scrape_news  # Must return: (ID, Portal, Title, Description, URL[, Category])

# ✅ Set AppUserModelID BEFORE window creation (critical for taskbar icon appearance)
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(u"news.scraper.app")

all_news = []
filtered_news = []

def update_table(tree, data):
    tree.delete(*tree.get_children())
    for news in data[:30]:
        tree.insert("", "end", values=news)
    tree.yview_moveto(0)

def update_status(status_label, message, footer_label=None):
    status_label.config(text=message)
    status_label.update_idletasks()
    if footer_label:
        footer_label.config(text=f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def fetch_and_display_news(tree, status_label, footer_label, search_entry):
    global all_news, filtered_news
    update_status(status_label, "📰 Fetching latest news...", footer_label)
    try:
        raw_data = scrape_news()
        all_news.clear()
        for item in raw_data:
            if len(item) == 5:
                all_news.append(item + ("General",))  # Add default category
            else:
                all_news.append(item)
        filtered_news = all_news.copy()
        update_table(tree, filtered_news)
        update_status(status_label, "✅ Latest news fetched successfully!", footer_label)
        search_entry.delete(0, tk.END)
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
    filtered_news = [n for n in all_news if query in n[2].lower() or query in n[3].lower()]
    update_table(tree, filtered_news)

def on_row_click(event, tree):
    item = tree.identify_row(event.y)
    if item:
        url = tree.item(item)["values"][4]
        if url:
            webbrowser.open_new_tab(url)

def save_selected_to_json(tree):
    selected_items = tree.selection()
    if not selected_items:
        messagebox.showinfo("No Selection", "Please select at least one news item to save.")
        return

    news_data = [tree.item(item)["values"] for item in selected_items]
    save_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
    if save_path:
        try:
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(news_data, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Saved", f"{len(news_data)} news item(s) saved to:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")

def launch_gui():
    app = tb.Window(themename="superhero")

    # ✅ Set window icon
    icon_path = os.path.join(os.path.dirname(__file__), "news_icon.ico")
    if os.path.exists(icon_path):
        app.iconbitmap(icon_path)
    else:
        print("Icon file not found!")

    app.title("🗞️ News Scraper & Visualizer")
    app.geometry("1200x660")

    # Header
    header = tb.Frame(app, padding=(10, 5))
    header.pack(fill=X)

    status_label = tb.Label(
        header,
        text="Welcome! Click 'Fetch News' to begin.",
        font=("Segoe UI", 14, "bold"),
        anchor="w"
    )
    status_label.pack(side=LEFT, padx=10)

    fetch_btn = tb.Button(
        header,
        text="🔄 Fetch News",
        bootstyle="primary",
        padding=10,
        width=18,
        command=lambda: fetch_and_display_news(tree, status_label, footer_label, search_entry)
    )
    fetch_btn.pack(side=RIGHT, padx=10)

    # Search Bar
    search_frame = tb.Frame(app, padding=(15, 5))
    search_frame.pack(fill=X)

    search_entry = tb.Entry(
        search_frame,
        font=("Segoe UI", 11),
        width=50,
        bootstyle="info"
    )
    search_entry.pack(side=LEFT, padx=(0, 10))

    search_btn = tb.Button(
        search_frame,
        text="🔍 Search",
        bootstyle="info",
        padding=10,
        width=12,
        command=lambda: on_search(tree, search_entry.get())
    )
    search_btn.pack(side=LEFT)

    clear_btn = tb.Button(
        search_frame,
        text="❌ Clear",
        bootstyle="secondary",
        padding=10,
        width=12,
        command=lambda: [search_entry.delete(0, tk.END), update_table(tree, all_news)]
    )
    clear_btn.pack(side=LEFT, padx=10)

    save_btn = tb.Button(
        search_frame,
        text="⭐ Save to Favorites",
        bootstyle="warning",
        padding=10,
        width=18,
        command=lambda: save_selected_to_json(tree)
    )
    save_btn.pack(side=LEFT, padx=20)

    # Table
    table_frame = tb.Frame(app)
    table_frame.pack(fill=BOTH, expand=YES, padx=15, pady=10)

    columns = ["ID", "Portal", "Title", "Description", "URL", "Category"]
    tree = ttk.Treeview(table_frame, columns=columns, show="headings")

    style = ttk.Style()
    style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"))
    style.configure("Treeview", font=("Segoe UI", 10), rowheight=28)

    col_widths = {
        "ID": 50,
        "Portal": 100,
        "Title": 250,
        "Description": 300,
        "URL": 250,
        "Category": 100
    }
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=col_widths.get(col, 120), anchor="w")

    tree.pack(fill=BOTH, expand=YES)
    tree.bind("<Double-1>", lambda e: on_row_click(e, tree))

    # Footer
    footer = tb.Frame(app)
    footer.pack(fill=X, padx=15, pady=(0, 10))

    footer_label = tb.Label(
        footer,
        text="Last updated: --",
        font=("Segoe UI", 10),
        anchor="w"
    )
    footer_label.pack(side=LEFT)

    # Initial load
    fetch_and_display_news(tree, status_label, footer_label, search_entry)

    app.mainloop()

# ✅ Entry point
if __name__ == "__main__":
    launch_gui()
