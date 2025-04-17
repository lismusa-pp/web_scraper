import ttkbootstrap as tb
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from datetime import datetime
import webbrowser
import json
import os
import ctypes
from scraper import scrape_news

# Set AppUserModelID for taskbar icon
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(u"news.scraper.app")

all_news = []
filtered_news = []
font_size = 12  # Default font size
search_history = []  # Store search queries

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

def fetch_and_display_news(tree, status_label, footer_label, search_entry, loading_label):
    global all_news, filtered_news
    update_status(status_label, "📰 Fetching latest news...", footer_label)
    loading_label.config(state="normal")  # Show loading indicator
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
    finally:
        loading_label.config(state="hidden")  # Hide loading indicator

    if hasattr(fetch_and_display_news, "timer"):
        fetch_and_display_news.timer.cancel()
    fetch_and_display_news.timer = threading.Timer(
        300, lambda: fetch_and_display_news(tree, status_label, footer_label, search_entry, loading_label)
    )
    fetch_and_display_news.timer.start()

def on_search(tree, query):
    global all_news, filtered_news, search_history
    if query.lower() not in [item.lower() for item in search_history]:
        search_history.append(query)  # Add new search query to history
        if len(search_history) > 5:
            search_history.pop(0)  # Keep only the last 5 searches
    update_search_history_treeview()
    
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

def update_search_history_treeview():
    search_history_treeview.delete(*search_history_treeview.get_children())
    for idx, search in enumerate(search_history):
        search_history_treeview.insert("", "end", values=(idx+1, search))

def on_search_history_select(event, tree):
    selected_item = search_history_treeview.item(search_history_treeview.focus())
    selected_query = selected_item['values'][1]  # Get search query
    search_entry.delete(0, tk.END)
    search_entry.insert(tk.END, selected_query)
    on_search(tree, selected_query)

def increase_font_size():
    global font_size
    font_size += 2
    update_fonts()

def decrease_font_size():
    global font_size
    font_size -= 2
    update_fonts()

def update_fonts():
    status_label.config(font=("Segoe UI", font_size))
    search_entry.config(font=("Segoe UI", font_size))
    # Update other widgets similarly
    tree.config(font=("Segoe UI", font_size))

def on_key_press(event):
    if event.keysym == 'Return':  # Enter key
        fetch_and_display_news(tree, status_label, footer_label, search_entry, loading_label)
    elif event.keysym == 'Escape':  # Escape key
        app.quit()  # Close the app

def launch_gui():
    global tree, status_label, footer_label, search_entry, loading_label, app, search_history_treeview
    app = tb.Window(themename="minty")
    app.configure(background="#1e1e1e")  # Dark background for better contrast

    # Set up the path to the icon
    icon_path = os.path.join(os.path.dirname(__file__), "news_icon.ico")
    print(f"Icon Path: {icon_path}")  # Check the path for debugging
    
    # Check if the icon file exists
    if os.path.exists(icon_path):
        app.iconbitmap(icon_path)
    else:
        print("Icon file not found!")  # Debug message if the icon file isn't found
    
    app.title("\U0001f5f3\ufe0f News Scraper & Visualizer")
    app.geometry("1200x700")

    # Modern Header with Logo and Styled Buttons
    header = tb.Frame(app, padding=(10, 5), bootstyle="success")
    header.pack(fill=X)

    status_label = tb.Label(
        header,
        text="Welcome! Click 'Fetch News' to begin.",
        font=("Segoe UI", font_size, "bold"),
        anchor="w",
        bootstyle="inverse-success"
    )
    status_label.pack(side=LEFT, padx=10)

    # Loading indicator
    loading_label = tb.Label(
        header,
        text="🔄 Fetching news...",
        font=("Segoe UI", font_size),
        bootstyle="info",
        anchor="w",
        state="hidden"
    )
    loading_label.pack(side=LEFT, padx=10)

    fetch_btn = tb.Button(
        header,
        text="\U0001f504 Fetch News",
        bootstyle="success-outline",
        padding=10,
        width=18,
        command=lambda: fetch_and_display_news(tree, status_label, footer_label, search_entry, loading_label)
    )
    fetch_btn.pack(side=RIGHT, padx=10)

    # Font size adjustment
    increase_font_btn = tb.Button(header, text="Increase Font Size", command=increase_font_size)
    increase_font_btn.pack(side=RIGHT, padx=10)
    
    decrease_font_btn = tb.Button(header, text="Decrease Font Size", command=decrease_font_size)
    decrease_font_btn.pack(side=RIGHT, padx=10)

    # Search Section
    search_frame = tb.Frame(app, padding=(15, 5), bootstyle="dark")
    search_frame.pack(fill=X)

    search_entry = tb.Entry(
        search_frame,
        font=("Segoe UI", font_size),
        width=50,
        bootstyle="light"
    )
    search_entry.pack(side=LEFT, padx=(0, 10))

    search_btn = tb.Button(
        search_frame,
        text="\U0001f50d Search",
        bootstyle="success",
        padding=10,
        width=12,
        command=lambda: on_search(tree, search_entry.get())
    )
    search_btn.pack(side=LEFT)

    clear_btn = tb.Button(
        search_frame,
        text="\u274c Clear",
        bootstyle="secondary",
        padding=10,
        width=12,
        command=lambda: [search_entry.delete(0, tk.END), update_table(tree, all_news)]
    )
    clear_btn.pack(side=LEFT, padx=10)

    save_btn = tb.Button(
        search_frame,
        text="\u2b50 Save to Favorites",
        bootstyle="success-outline",
        padding=10,
        width=18,
        command=lambda: save_selected_to_json(tree)
    )
    save_btn.pack(side=LEFT, padx=20)

    # Search History Section with Label and Adjusted Size
    history_frame = tb.Frame(app, padding=(10, 5), bootstyle="light")
    history_frame.pack(fill=X, pady=5)

    # Label for Search History
    history_label = tb.Label(history_frame, text="Search History", font=("Segoe UI", font_size, "bold"))
    history_label.pack(side=LEFT, padx=10)

    # Treeview for Search History
    search_history_treeview = ttk.Treeview(
        history_frame,
        columns=("ID", "Search Query"),
        show="headings",
        height=5  # Make it smaller by limiting visible rows
    )
    search_history_treeview.heading("ID", text="ID")
    search_history_treeview.heading("Search Query", text="Search Query")
    search_history_treeview.column("ID", width=50, anchor="center")  # Centered text
    search_history_treeview.column("Search Query", width=300, anchor="center")  # Centered text

    search_history_treeview.pack(fill="y", padx=10, pady=5)

    search_history_treeview.bind("<Double-1>", lambda e: on_search_history_select(e, tree))

    # News Table
    table_frame = tb.Frame(app, bootstyle="dark")
    table_frame.pack(fill=BOTH, expand=YES, padx=15, pady=10)

    columns = ["ID", "Portal", "Title", "Description", "URL", "Category"]
    tree = ttk.Treeview(table_frame, columns=columns, show="headings")

    # Set up style for Treeview
    style = ttk.Style()
    style.configure("Treeview.Heading",
                    font=("Segoe UI", font_size, "bold"),
                    background="#343a40",  # Dark background for header
                    foreground="white",
                    relief="flat")  # Remove any border around header

    style.configure("Treeview",
                    font=("Segoe UI", font_size),
                    rowheight=28,
                    background="#2E2E2E",  # Dark background for rows
                    foreground="white",
                    fieldbackground="#2E2E2E",  # Matching background
                    relief="flat",  # Remove borders from rows
                    highlightthickness=0,  # Remove highlight when selecting rows
                    bd=0)  # Remove internal border

    # Vertical line simulation for Treeview columns (between columns)
    for i in range(1, len(columns)):
        style.configure(f"Treeview.Column{i}",
                        bordercolor="#444",  # Set border color
                        borderwidth=1)  # Set border width

    style.configure("Treeview",
                    relief="solid",  # Solid border around the entire Treeview
                    bordercolor="#444",  # Color of the border
                    borderwidth=1)  # Border width around the entire widget

    style.map("Treeview",
              background=[("selected", "#4CAF50")],  # Color when row is selected
              foreground=[("selected", "white")],  # Text color when row is selected
              relief=[("selected", "solid")])  # Solid border when row is selected

    # Treeview Columns configuration
    col_widths = {
        "ID": 50,
        "Portal": 100,
        "Title": 250,
        "Description": 300,
        "URL": 250,
        "Category": 100
    }
    for col in columns:
        tree.heading(col, text=col, anchor="center" if col == "ID" else "w")  # ID aligned center, others left
        tree.column(col, width=col_widths.get(col, 120), anchor="center" if col == "ID" else "w", minwidth=100)  # ID center, others left

    tree.pack(fill=BOTH, expand=YES)
    tree.bind("<Double-1>", lambda e: on_row_click(e, tree))

    footer = tb.Frame(app, bootstyle="success")
    footer.pack(fill=X, padx=15, pady=(0, 10))

    footer_label = tb.Label(
        footer,
        text="Last updated: --",
        font=("Segoe UI", font_size),
        anchor="w",
        bootstyle="inverse-success"
    )
    footer_label.pack(side=LEFT)

    app.bind("<KeyPress>", on_key_press)

    fetch_and_display_news(tree, status_label, footer_label, search_entry, loading_label)

    app.mainloop()

if __name__ == "__main__":
    launch_gui()
