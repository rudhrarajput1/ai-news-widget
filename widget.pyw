"""
AI/ML News Desktop Widget (Windows) - v3, with theme toggle
--------------------------------------------------------------
Make sure "app_icon.ico" is saved in this same folder before running.

HOW TO RUN (from inside the ai-news-widget folder):
    Double-click widget.pyw   (no terminal window)
    or:  python widget.pyw    (shows errors, useful while testing)
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

THEMES = {
    "dark": {
        "BG": "#1e1f26",
        "CARD_BG": "#2a2b35",
        "ACCENT": "#5aa9ff",
        "TEXT_MAIN": "#f0f0f2",
        "TEXT_SUB": "#9a9ba5",
        "BORDER": "#383946",
    },
    "light": {
        "BG": "#f4f3ee",
        "CARD_BG": "#ffffff",
        "ACCENT": "#2f6fd1",
        "TEXT_MAIN": "#2c2c2a",
        "TEXT_SUB": "#6b6a63",
        "BORDER": "#e4e2d9",
    },
}


class NewsWidget:
    def __init__(self, root):
        self.root = root
        self.theme_name = "dark"
        self.results_cache = {}

        root.title("AI / ML News")
        root.geometry("400x560+80+80")
        root.attributes("-topmost", True)

        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_icon.ico")
        if os.path.exists(icon_path):
            try:
                root.iconbitmap(icon_path)
            except Exception:
                pass

        self.header = tk.Frame(root)
        self.header.pack(fill="x", padx=16, pady=(16, 6))

        self.title_label = tk.Label(self.header, text="AI / ML News", font=("Segoe UI", 15, "bold"))
        self.title_label.pack(side="left")

        self.theme_btn = tk.Button(self.header, text="Theme", command=self.toggle_theme,
                                    relief="flat", font=("Segoe UI", 9, "bold"),
                                    padx=10, pady=4, cursor="hand2", bd=0)
        self.theme_btn.pack(side="right", padx=(6, 0))

        self.refresh_btn = tk.Button(self.header, text="Refresh", command=self.refresh,
                                      relief="flat", font=("Segoe UI", 9, "bold"),
                                      padx=12, pady=4, cursor="hand2", bd=0)
        self.refresh_btn.pack(side="right")

        self.status = tk.Label(root, font=("Segoe UI", 8))
        self.status.pack(fill="x", padx=16)

        self.container = tk.Frame(root)
        self.container.pack(fill="both", expand=True, padx=10, pady=8)

        self.canvas = tk.Canvas(self.container, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.container, orient="vertical", command=self.canvas.yview)
        self.list_frame = tk.Frame(self.canvas)

        self.list_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.list_frame, anchor="nw", width=370)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)

        self.apply_theme()
        self.refresh()

    def toggle_theme(self):
        self.theme_name = "light" if self.theme_name == "dark" else "dark"
        self.apply_theme()
        self._render(self.results_cache)

    def apply_theme(self):
        c = THEMES[self.theme_name]
        self.root.configure(bg=c["BG"])
        self.header.configure(bg=c["BG"])
        self.title_label.configure(bg=c["BG"], fg=c["TEXT_MAIN"])
        self.status.configure(bg=c["BG"], fg=c["TEXT_SUB"])
        self.container.configure(bg=c["BG"])
        self.canvas.configure(bg=c["BG"])
        self.list_frame.configure(bg=c["BG"])

        self.theme_btn.configure(bg=c["CARD_BG"], fg=c["TEXT_MAIN"],
                                  activebackground=c["BORDER"], activeforeground=c["TEXT_MAIN"])
        self.refresh_btn.configure(bg=c["ACCENT"], fg="#101114" if self.theme_name == "dark" else "#ffffff",
                                    activebackground=c["ACCENT"], activeforeground="#ffffff")

    def refresh(self):
        c = THEMES[self.theme_name]
        self.status.config(text="Refreshing...", fg=c["TEXT_SUB"])
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
        self.results_cache = results
        self.root.after(0, lambda: self._render(results))

    def _render(self, results):
        c = THEMES[self.theme_name]

        for widget in self.list_frame.winfo_children():
            widget.destroy()

        for section, items in results.items():
            tk.Label(self.list_frame, text=section.upper(), font=("Segoe UI", 10, "bold"),
                     bg=c["BG"], fg=c["ACCENT"], anchor="w").pack(fill="x", pady=(10, 4))

            if not items:
                tk.Label(self.list_frame, text="No items right now.", font=("Segoe UI", 9),
                         bg=c["BG"], fg=c["TEXT_SUB"], anchor="w").pack(fill="x")
                continue

            for source, title, link in items:
                card = tk.Frame(self.list_frame, bg=c["CARD_BG"], highlightbackground=c["BORDER"],
                                 highlightthickness=1, bd=0)
                card.pack(fill="x", pady=4)

                tk.Label(card, text=source, font=("Segoe UI", 8, "bold"), bg=c["CARD_BG"],
                         fg=c["TEXT_SUB"], anchor="w").pack(fill="x", padx=10, pady=(8, 2))

                link_label = tk.Label(card, text=title, font=("Segoe UI", 10), bg=c["CARD_BG"],
                                       fg=c["TEXT_MAIN"], anchor="w", justify="left",
                                       wraplength=330, cursor="hand2")
                link_label.pack(fill="x", padx=10, pady=(0, 10))
                if link:
                    link_label.bind("<Button-1>", lambda e, u=link: webbrowser.open(u))
                    link_label.bind("<Enter>", lambda e, w=link_label: w.config(fg=c["ACCENT"]))
                    link_label.bind("<Leave>", lambda e, w=link_label: w.config(fg=c["TEXT_MAIN"]))

        self.status.config(text="Up to date", fg=c["TEXT_SUB"])
        self.refresh_btn.config(state="normal")


if __name__ == "__main__":
    root = tk.Tk()
    app = NewsWidget(root)
    root.mainloop()
