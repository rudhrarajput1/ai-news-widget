"""
AI/ML/Tech News Desktop Widget (Windows) - v6, slidable columns
--------------------------------------------------------------------
Make sure "app_icon.ico" is saved in this same folder before running.

HOW TO RUN (from inside the ai-news-widget folder):
    Double-click widget.pyw   (no terminal window)
    or:  python widget.pyw    (shows errors, useful while testing)

Switch categories with Left/Right arrow keys, or click-drag sideways.
"""

import tkinter as tk
from tkinter import ttk
import webbrowser
import threading
import feedparser
import os
import json
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
    "Tech": [
        ("TechCrunch", "https://techcrunch.com/feed/"),
        ("The Verge", "https://www.theverge.com/rss/index.xml"),
    ],
}

CATEGORY_ORDER = list(FEEDS.keys())  # ["AI", "ML", "Tech"] - controls slide order
MAX_ITEMS_PER_FEED = 6
WIN_WIDTH = 400

BOOKMARK_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bookmarks.json")

def load_bookmarks():
    if not os.path.exists(BOOKMARK_FILE):
        return []
    try:
        with open(BOOKMARK_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []
    
def save_bookmarks(bookmarks):
    try:
        with open(BOOKMARK_FILE, "w" , encoding= "utf-8") as f:
            json.dump(bookmarks, f , indent=2)
    except Exception:
        pass
    
    
THEMES = {
    "dark": {
        "BG": "#1e1f26",
        "CARD_BG": "#2a2b35",
        "ACCENT": "#5aa9ff",
        "TEXT_MAIN": "#f0f0f2",
        "TEXT_SUB": "#9a9ba5",
        "BORDER": "#383946",
        "STAR": "#e8c14d",
    },
    "light": {
        "BG": "#f4f3ee",
        "CARD_BG": "#ffffff",
        "ACCENT": "#2f6fd1",
        "TEXT_MAIN": "#2c2c2a",
        "TEXT_SUB": "#6b6a63",
        "BORDER": "#e4e2d9",
        "STAR": "#c9931f",
    },
}

CATEGORY_COLORS = {
    "dark": {
        "AI": "#2a3b3a",
        "ML": "#302b40",
        "Tech": "#3a3220",
        "Saved": "#332e2a",
    },
    "light": {
        "AI": "#e3efec",
        "ML": "#e9e6f4",
        "Tech": "#f3ecd8",
        "Saved": "#efe9e2",
    },
}

class NewsWidget:
    def __init__(self, root):
        self.root = root
        self.theme_name = "dark"
        self.results_cache = {}
        self.active_index = 0                 # which column (0=AI, 1=ML, 2=Tech) is currently in view
        self.dots = []                          # small position-indicator dots at the bottom
        self.drag_start_x = None  
        self.bookmarks = load_bookmarks()        # tracks mouse position during a click-drag swipe

        root.title("AI / ML News")
        root.geometry(f"{WIN_WIDTH}x560+80+80")
        root.attributes("-topmost", True)

        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_icon.ico")
        if os.path.exists(icon_path):
            try:
                root.iconbitmap(icon_path)
            except Exception:
                pass

        self.header = tk.Frame(root)
        self.header.pack(fill="x", padx=16, pady=(16, 4))

        self.title_label = tk.Label(self.header, font=("Segoe UI", 15, "bold"))
        self.title_label.pack(side="left")

        self.theme_canvas = tk.Canvas(self.header, width=26, height=26, highlightthickness=0, bd=0, cursor="hand2")
        self.theme_canvas.pack(side="right", padx=(6, 0))
        self.theme_canvas.bind("<Button-1>", lambda e: self.toggle_theme())

        self.refresh_btn = tk.Button(self.header, text="↻", command=self.refresh,
                                      relief="flat", font=("Segoe UI", 12, "bold"),
                                      width=2, height=1, cursor="hand2", bd=0,
                                      highlightthickness=0)
        self.refresh_btn.pack(side="right")

        self.status = tk.Label(root, font=("Segoe UI", 8))
        self.status.pack(fill="x", padx=16)

        # --- Sliding horizontal canvas: holds all 3 columns side by side ---
        self.slider_canvas = tk.Canvas(root, highlightthickness=0)
        self.slider_canvas.pack(fill="both", expand=True, padx=10, pady=(6, 4))

        self.column_frames = {}
        for i, category in enumerate(CATEGORY_ORDER):       
            col = tk.Frame(self.slider_canvas, width=WIN_WIDTH - 20)
            col.pack_propagate(False)

            scroll_canvas = tk.Canvas(col, highlightthickness=0)
            scrollbar = ttk.Scrollbar(col, orient="vertical", command=scroll_canvas.yview)
            list_frame = tk.Frame(scroll_canvas)

            list_frame.bind("<Configure>", lambda e, cv=scroll_canvas: cv.configure(scrollregion=cv.bbox("all")))
            scroll_canvas.create_window((0, 0), window=list_frame, anchor="nw", width=WIN_WIDTH - 44)
            scroll_canvas.configure(yscrollcommand=scrollbar.set)

            scroll_canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
               
           
           
            self.slider_canvas.create_window(i * WIN_WIDTH, 0, window=col, anchor="nw",
                                              width=WIN_WIDTH - 20, height=440)

            self.column_frames[category] = {"list_frame": list_frame, "col": col, "scroll_canvas": scroll_canvas}

        self.slider_canvas.configure(scrollregion=(0, 0, WIN_WIDTH * len(CATEGORY_ORDER), 440))

        def _on_mousewheel(event):
            active_canvas = self.column_frames[CATEGORY_ORDER[self.active_index]]["scroll_canvas"]
            active_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        root.bind_all("<MouseWheel>", _on_mousewheel)

        # --- Dot indicators (bottom) ---
        self.dots_bar = tk.Frame(root)
        self.dots_bar.pack(fill="x", pady=(0, 12))
        for i, category in enumerate(CATEGORY_ORDER):
            dot = tk.Label(self.dots_bar, text="●", font=("Segoe UI", 9))
            dot.pack(side="left", expand=True)
            self.dots.append(dot)

        # --- Navigation: arrow keys ---
        root.bind("<Left>", lambda e: self.go_to(self.active_index - 1))
        root.bind("<Right>", lambda e: self.go_to(self.active_index + 1))

        # --- Navigation: click-and-drag swipe ---
        self.slider_canvas.bind("<ButtonPress-1>", self._on_drag_start)
        self.slider_canvas.bind("<ButtonRelease-1>", self._on_drag_end)

        self.apply_theme()
        self.refresh()

    def _on_drag_start(self, event):
        self.drag_start_x = event.x

    def _on_drag_end(self, event):
        if self.drag_start_x is None:
            return
        delta = event.x - self.drag_start_x
        self.drag_start_x = None
        if delta > 40:
            self.go_to(self.active_index - 1)   # dragged right -> go to previous
        elif delta < -40:
            self.go_to(self.active_index + 1)   # dragged left -> go to next

    def go_to(self, index):
        index = max(0, min(len(CATEGORY_ORDER) - 1, index))   # clamp, no wraparound
        self.active_index = index
        target_x = index * WIN_WIDTH
        total_width = WIN_WIDTH * len(CATEGORY_ORDER)
        fraction = target_x / total_width
        self.slider_canvas.xview_moveto(fraction)
        self.title_label.config(text=f"{CATEGORY_ORDER[index]} News")
        self.update_dots()

    def update_dots(self):
        c = THEMES[self.theme_name]
        for i, dot in enumerate(self.dots):
            dot.configure(fg=c["ACCENT"] if i == self.active_index else c["BORDER"])

    def toggle_theme(self):
        self.theme_name = "light" if self.theme_name == "dark" else "dark"
        self.apply_theme()
        self._render(self.results_cache)

    def draw_theme_icon(self):
        c = THEMES[self.theme_name]
        self.theme_canvas.delete("all")
        self.theme_canvas.configure(bg=c["BG"])
        self.theme_canvas.create_arc(2, 2, 24, 24, start=90, extent=180, fill="#f0f0f2", outline="")
        self.theme_canvas.create_arc(2, 2, 24, 24, start=270, extent=180, fill="#1e1f26", outline="")
        self.theme_canvas.create_oval(15, 6, 19, 10, fill="#1e1f26", outline="")
        self.theme_canvas.create_oval(7, 16, 11, 20, fill="#f0f0f2", outline="")

    def apply_theme(self):
        c = THEMES[self.theme_name]
        self.root.configure(bg=c["BG"])
        self.header.configure(bg=c["BG"])
        self.title_label.configure(bg=c["BG"], fg=c["TEXT_MAIN"],
                                    text=f"{CATEGORY_ORDER[self.active_index]} News")
        self.status.configure(bg=c["BG"], fg=c["TEXT_SUB"])
        self.slider_canvas.configure(bg=c["BG"])
        self.dots_bar.configure(bg=c["BG"])

        for category, refs in self.column_frames.items():
            refs["col"].configure(bg=c["BG"])
            refs["scroll_canvas"].configure(bg=c["BG"])
            refs["list_frame"].configure(bg=c["BG"])

        self.refresh_btn.configure(bg=c["BG"], fg=c["TEXT_MAIN"],
                                    activebackground=c["BG"], activeforeground=c["ACCENT"])
        self.draw_theme_icon()
        self.update_dots()

    def refresh(self):
        c = THEMES[self.theme_name]
        self.status.config(text="Refreshing...", fg=c["TEXT_SUB"])
        self.refresh_btn.config(state="disabled")
        threading.Thread(target=self._fetch_all, daemon=True).start()

    def _fetch_all(self):
        results = {}
        for category, feeds in FEEDS.items():
            items = []
            for name, url in feeds:
                try:
                    parsed = feedparser.parse(url)
                    for entry in parsed.entries[:MAX_ITEMS_PER_FEED]:
                        items.append((name, entry.get("title", "Untitled"), entry.get("link", "")))
                except Exception:
                    pass
            results[category] = items
        self.results_cache = results
        self.root.after(0, lambda: self._render(results))


    def is_bookmarked(self, link):
        return any (b["link"] == link for b in self.bookmarks)
    
    def toggle_bookmark(self, source, title, link):
        if self.is_bookmarked(link):
            self.bookmarks = [b for b in self.bookmarks if b["link"] != link]
        else:
            self.bookmarks.append({"source": source, "title": title, "link": link})
        save_bookmarks(self.bookmarks)
        self._render(self.results_cache)

    def _render(self, results):
        c = THEMES[self.theme_name]

        for category, refs in self.column_frames.items():
            list_frame = refs["list_frame"]
            for widget in list_frame.winfo_children():
                widget.destroy()


            if category == "Saved":
                items = [(b["source"], b["title"], b["link"]) for b in self.bookmarks]
            else:
                items = results.get(category, [])
            if not items:
                tk.Label(list_frame, text="No items right now.", font=("Segoe UI", 9),
                         bg=c["BG"], fg=c["TEXT_SUB"], anchor="w").pack(fill="x", pady=(10, 0))
                continue

            for source, title, link in items:
                card_bg = CATEGORY_COLORS[self.theme_name].get(category, c["BG"])
                card  = tk.Frame(list_frame, bg=card_bg, padx=10, pady=10)
                card.pack(fill="x", pady=(0, 8))

                top_row= tk.Frame(card, bg=card_bg)
                top_row.pack(fill="x")

                tk.Label(top_row, text=source, font=("Segoe UI", 8, "bold"), bg=card_bg,
                         fg=c["TEXT_SUB"], anchor="w").pack(side="left", pady=(0, 2))

                star_text = "★" if self.is_bookmarked(link) else "☆"
                star_btn = tk.Label(top_row, text=star_text, font=("Segoe UI", 11), bg=card_bg,
                                     fg=c["STAR"] if self.is_bookmarked(link) else c["TEXT_SUB"],
                                     cursor="hand2")
                star_btn.pack(side="right")
                star_btn.bind("<Button-1>", lambda e, s=source, t=title, l=link: self.toggle_bookmark(s, t, l))
               
               
                link_label = tk.Label(card, text=title, font=("Segoe UI", 10), bg=card_bg,
                                       fg=c["TEXT_MAIN"], anchor="w", justify="left",
                                       wraplength=310, cursor="hand2")
                link_label.pack(fill="x", pady=(0, 8))

                
                if link:
                    link_label.bind("<Button-1>", lambda e, u=link: webbrowser.open(u))
                    link_label.bind("<Enter>", lambda e, w=link_label: w.config(fg=c["ACCENT"]))
                    link_label.bind("<Leave>", lambda e, w=link_label: w.config(fg=c["TEXT_MAIN"]))

        self.status.config(text="Up to date", fg=c["TEXT_SUB"])
        self.refresh_btn.config(state="normal")


if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = NewsWidget(root)
        root.mainloop()
    except Exception as e:
        import traceback
        traceback.print_exc()
        input("Press Enter to close...")
        