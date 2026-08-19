# AI / ML News Widget

A small Windows desktop app that shows the latest AI, ML, and Tech headlines in a clean, always-on-top window — pulled directly from real news sites' public RSS feeds.

## Features
- Live headlines from TechCrunch AI, VentureBeat AI, MIT Technology Review, TechCrunch, and The Verge
- Three news categories (AI / ML / Tech) plus a Saved tab — swipe or use arrow keys to switch between them
- Bookmark any headline with a star, saved locally so it persists between sessions
- One-click Refresh to pull the latest news anytime
- Dark / Light theme toggle
- Click any headline to open the full article in your browser
- Custom app icon

## Built with
- Python
- Tkinter (GUI)
- feedparser (RSS parsing)
- Built with help from Claude (Anthropic)

## How to run it

1. Install Python from [python.org](https://www.python.org/downloads/) (check "Add to PATH" during setup)
2. Install the required packages:
   ```
   python -m pip install feedparser requests
   ```
3. Run the widget:
   ```
   python widget.pyw
   ```

## Note
Windows may show an "unrecognized app" warning if you run a compiled `.exe` version, since it isn't digitally signed. This is expected for small/hobby projects and doesn't mean the app is unsafe — you can review the full source code above.

## Author
Built as a personal learning project while exploring Python and desktop app development.
