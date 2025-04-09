import tkinter as tk
from tkinter import ttk
import threading
from scraper import scrape_news

all_news = []

def update_table(tree):
    for row in tree.get_children():
        tree.delete(row)
    for news in all_news[:20]:
        tree.insert("", "end", values=news)

def update_status(status_label, message):
    status_label.config(text=message)
    status_label.update_idletasks()

def fetch_and_display_news(tree, status_label):
    global all_news
    update_status(status_label, "Fetching latest news...")
    all_news.clear()
    all_news.extend(scrape_news())
    update_table(tree)
    update_status(status_label, "Latest news fetched successfully!")
    if hasattr(fetch_and_display_news, "timer"):
        fetch_and_display_news.timer.cancel()
    fetch_and_display_news.timer = threading.Timer(300, lambda: fetch_and_display_news(tree, status_label))
    fetch_and_display_news.timer.start()

def launch_gui():
    root = tk.Tk()
    root.title("News Scraper & Visualizer")
    root.geometry("900x500")
    root.configure(bg="#f4f4f4")

    header_frame = tk.Frame(root, bg="#4CAF50", pady=10)
    header_frame.pack(fill="x")

    status_label = tk.Label(header_frame, text="Click 'Fetch News' to start", font=("Arial", 14), fg="white", bg="#4CAF50")
    status_label.pack()

    table_frame = tk.Frame(root, bg="#f4f4f4")
    table_frame.pack(expand=True, fill="both", padx=20, pady=10)

    columns = ("ID", "Portal", "Title", "Description", "URL to Portal")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

    style = ttk.Style()
    style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#4CAF50", foreground="white")
    style.configure("Treeview", font=("Arial", 10), rowheight=30)

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=180, anchor="w")
    tree.pack(expand=True, fill="both")

    fetch_button = tk.Button(header_frame, text="Fetch News", font=("Arial", 14),
                             bg="#ffffff", fg="#4CAF50",
                             command=lambda: fetch_and_display_news(tree, status_label),
                             relief="flat", padx=20, pady=10)
    fetch_button.pack(pady=10)

    fetch_and_display_news(tree, status_label)
    root.mainloop()