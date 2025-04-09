import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk  # PIL for image handling
import threading
import time
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
    update_status(status_label, f"Last updated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    if hasattr(fetch_and_display_news, "timer"):
        fetch_and_display_news.timer.cancel()
    fetch_and_display_news.timer = threading.Timer(300, lambda: fetch_and_display_news(tree, status_label))
    fetch_and_display_news.timer.start()

def launch_gui():
    root = tk.Tk()
    root.title("🗞️ News Scraper & Visualizer")
    root.geometry("1000x600")
    root.configure(bg="#1e1e2f")

    # Load and display image at the top of the GUI
    try:
        # Replace this with your image path. Example assumes the image is in the same directory.
        image = Image.open("blue_mountains.jpg")  # Ensure the image file is in the same folder or provide the correct path
        image = image.resize((1000, 200))  # Resize image to fit the width of the screen
        img = ImageTk.PhotoImage(image)

        # Create label for image at the top
        img_label = tk.Label(root, image=img)
        img_label.image = img  # Keep a reference to avoid garbage collection
        img_label.pack(fill="x", pady=5)
    except Exception as e:
        print(f"Error loading image: {e}")

    # Header
    header_frame = tk.Frame(root, bg="#2d2f3a", pady=10)
    header_frame.pack(fill="x")

    status_label = tk.Label(
        header_frame, 
        text="Click 'Fetch News' to start", 
        font=("Segoe UI", 14), 
        fg="#ffffff", 
        bg="#2d2f3a"
    )
    status_label.pack(pady=(0, 5))

    fetch_button = tk.Button(
        header_frame, 
        text="Fetch News", 
        font=("Segoe UI", 12, "bold"), 
        bg="#008cff", 
        fg="#ffffff", 
        activebackground="#006bb3",
        activeforeground="#ffffff",
        command=lambda: fetch_and_display_news(tree, status_label),
        relief="flat", 
        padx=20, 
        pady=8,
        cursor="hand2"
    )
    fetch_button.pack(pady=5)

    # News Table
    table_frame = tk.Frame(root, bg="#1e1e2f")
    table_frame.pack(expand=True, fill="both", padx=20, pady=10)

    columns = ("ID", "Portal", "Title", "Description", "URL to Portal")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)

    style = ttk.Style()
    style.theme_use("default")
    style.configure("Treeview",
                    background="#282c34",
                    foreground="#ffffff",
                    rowheight=28,
                    fieldbackground="#282c34",
                    borderwidth=0,
                    font=("Segoe UI", 10))
    style.map("Treeview", background=[("selected", "#3e8ed0")])

    style.configure("Treeview.Heading",
                    background="#3e3f4a",
                    foreground="#ffffff",
                    font=("Segoe UI", 11, "bold"))

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=180, anchor="w")

    tree.pack(expand=True, fill="both")

    fetch_and_display_news(tree, status_label)
    root.mainloop()

