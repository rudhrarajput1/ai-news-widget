"""'''
AI/ML News Desktop Widget (Windows)
------------------------------------
A small always-on-top window that pulls the latest AI and ML headlines
directly from real news sites' public RSS feeds, with a Refresh button.

SETUP (one-time):
1. Install Python from https://www.python.org/downloads/  (check "Add to PATH" during install)
2. Open Command Prompt and run:
       pip install feedparser requests
3. Run the widget:
       pythonw ai_news_widget.py
   (use "pythonw" instead of "python" so no black console window appears)

Optional: create a desktop shortcut to the command above, or add it to your
Windows Startup folder (Win+R -> shell:startup) so it opens automatically.
"""

import tkinter as tk
from tkinter import ttk
import webbrowser
import threading
import feedparser
import os
import ctypes
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass


FEEDS = {
    "AI": [
        ("TechCrunch AI", "https://techcrunch.com/category/artificial-intelligence/feed/"),
        ("VentureBeat AI", "https://venturebeat.com/category/ai/feed/"),
    ],
    "ML": [
        ("MIT Tech Review", "https://www.technologyreview.com/feed/"),
    ],
}

MAX_ITEMS_PER_FEED = 4


class NewsWidget:
    def __init__(self, root):
        self.root = root
        root.title("AI / ML News")
        root.geometry("380x520+80+80")
        root.attributes("-topmost", True)
        root.configure(bg="#f4f3ee")

        header = tk.Frame(root, bg="#f4f3ee")
        header.pack(fill="x", padx=12, pady=(10, 4))

        tk.Label(header, text="AI / ML news", font=("Segoe UI", 14, "bold"),
                 bg="#f4f3ee", fg="#2c2c2a").pack(side="left")

        self.refresh_btn = tk.Button(header, text="Refresh", command=self.refresh,
                                      relief="flat", bg="#e4e2d9", fg="#2c2c2a",
                                      padx=10, pady=2, cursor="hand2")
        self.refresh_btn.pack(side="right")

        self.status = tk.Label(root, text="Loading...", font=("Segoe UI", 8),
                                bg="#f4f3ee", fg="#9a9990")
        self.status.pack(fill="x", padx=12)

        container = tk.Frame(root, bg="#f4f3ee")
        container.pack(fill="both", expand=True, padx=8, pady=6)

        canvas = tk.Canvas(container, bg="#f4f3ee", highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.list_frame = tk.Frame(canvas, bg="#f4f3ee")

        self.list_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.list_frame, anchor="nw", width=350)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        def _on_mousewheel(event):
         canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        self.refresh()

    def refresh(self):
        self.status.config(text="Refreshing...")
        self.refresh_btn.config(state="disabled")
        threading.Thread(target=self._fetch_all, daemon=True).start()

    def _fetch_all(self):
        results = {}
        for section, feeds in FEEDS.items():
            items = []
            for name, url in feeds:
                try:
                    parsed = feedparser.parse(url)
                    for entry in parsed.entries[:MAX_ITEMS_PER_FEED]:
                        items.append((name, entry.get("title", "Untitled"), entry.get("link", "")))
                except Exception:
                    pass
            results[section] = items
        self.root.after(0, lambda: self._render(results))

    def _render(self, results):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        for section, items in results.items():
            tk.Label(self.list_frame, text=section, font=("Segoe UI", 11, "bold"),
                     bg="#f4f3ee", fg="#378ADD", anchor="w").pack(fill="x", pady=(8, 2))

            if not items:
                tk.Label(self.list_frame, text="No items right now.", font=("Segoe UI", 9),
                         bg="#f4f3ee", fg="#9a9990", anchor="w").pack(fill="x")
                continue

            for source, title, link in items:
                card = tk.Frame(self.list_frame, bg="#ffffff", bd=0)
                card.pack(fill="x", pady=3)

                tk.Label(card, text=source, font=("Segoe UI", 8), bg="#ffffff",
                         fg="#9a9990", anchor="w").pack(fill="x", padx=8, pady=(4, 0))

                link_label = tk.Label(card, text=title, font=("Segoe UI", 10), bg="#ffffff",
                                       fg="#2c2c2a", anchor="w", justify="left", wraplength=320, cursor="hand2")
                link_label.pack(fill="x", padx=8, pady=(0, 6))
                if link:
                    link_label.bind("<Button-1>", lambda e, u=link: webbrowser.open(u))

        self.status.config(text="Up to date")
        self.refresh_btn.config(state="normal")


if __name__ == "__main__":
    root = tk.Tk()
    app = NewsWidget(root)
    root.mainloop() 