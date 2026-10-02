# AI News Widget

A dark-themed desktop app that shows live AI/ML/Tech headlines, with
bookmarking and a dedicated saved-news view — built so I can check
AI news without opening a browser tab.

> **Why:** I wanted a lightweight, always-available news check for
> AI/ML and Tech without the clutter of a browser or a news site's UI.

## Architecture

```
Tkinter UI (category slider: AI / ML / Tech)
       │
       ▼
feedparser → RSS feeds (per category)
       │
       ▼
bookmarks.json (save/star, local only)
```

## Tech stack

`Python` · `Tkinter` · `feedparser` · `JSON`

## Features

- Category browsing (AI / ML / Tech) via a horizontal slider
- Save/star any headline as a bookmark
- Dedicated "Saved" view with live search/filter by title or source
- Theme toggle
- Refresh with an "up to date" status indicator

## Why these design choices

- **Tkinter**: ships with Python, no extra install step for a
  personal desktop tool — avoided a heavier GUI framework for
  something this small.
- **JSON over a database**: bookmarks are a simple, low-volume list
  for single-user local use; a database would be overkill.

## Limitations

- News sources are fixed per category (not user-configurable yet)
- No retry/backoff if a feed is temporarily unreachable
- Desktop-only (Tkinter), not a web or mobile app

## Setup

```bash
pip install -r requirements.txt
python3 ai_news_widget.py
```

## License

MIT — see [LICENSE](LICENSE)

## Status

Actively developed — next planned addition is configurable feed
sources per category.
