# Portfolio Maintenance Guide

This portfolio (https://giginet.me/) is a static site hosted via GitHub Pages from `giginet/giginet.github.io`. It is updated daily by a GitHub Action that fetches blog RSS and GitHub stargazer counts.

## Project Structure

```
.
├── index.html           # Single-page site
├── css/style.css        # All styles (pop red theme, rounded fonts)
├── data/
│   ├── posts.json       # Generated from Hatena Blog RSS
│   └── stars.json       # Generated from GitHub API
├── scripts/
│   ├── fetch-rss.py     # Refreshes posts.json
│   └── fetch-stars.py   # Refreshes stars.json
├── images/              # Avatar and footer icon (pixel-art PNGs)
├── .github/workflows/deploy.yml  # Daily cron + on-push build
└── CNAME                # giginet.me
```

## Local Preview

1Password CLI is required to read `CONNPASS_TOKEN` from `.envrc`.

```sh
python3 -m http.server 8080 &
open http://localhost:8080
```

Use the Playwright MCP to verify layout changes, especially on mobile widths.
When done, stop the server with `lsof -ti:8080 | xargs kill`.

## Adding Entries

All entries are hand-edited in `index.html`. Keep sections in reverse chronological order.

### Conference Talks (`#talks`)

Each year is a `<details class="talk-year">` block. Years 2024+ have `open`; earlier years collapse by default.

**Item template:**

```html
<div class="talk-item">
  <span class="talk-event">Event Name</span>
  <a href="SLIDE_URL" class="talk-title" target="_blank" rel="noopener">Talk Title</a>
  <a href="VIDEO_URL">🎥 Video</a>   <!-- optional -->
</div>
```

- `talk-event` labels that start with `#` or contain `\(` are fine; keep them short enough to not wrap the date column.
- Title links point at Speaker Deck (2016+) or SlideShare (2011–2015). If no slide exists, use `<span class="talk-title">` instead of `<a>`.
- Video links are styled by `.talk-item a.talk-title ~ a` — any sibling `<a>` after the title will render as a Video link. Do not use the old `.talk-links` wrapper.
- On mobile (≤640px) the grid collapses to one column; no extra changes needed.

**Finding a talk via connpass API**

```sh
op run --env-file=.envrc -- sh -c \
  'curl -s "https://connpass.com/api/v2/users/giginet/presenter_events/?count=100&order=2" \
   -H "X-API-Key: $CONNPASS_TOKEN"'
```

Match the `id` / `started_at` against Speaker Deck to discover the slide URL.

### Interviews & Media (`#media`)

```html
<a href="EVENT_OR_ARTICLE_URL" class="post-item media-item" target="_blank" rel="noopener">
  <span class="post-date">YYYY-MM</span>
  <span class="post-title">Original Japanese title</span>
  <span class="media-source">Publisher Name</span>
</a>
<a href="VIDEO_URL" class="media-video" target="_blank" rel="noopener">🎥 Video</a>  <!-- optional -->
```

- Keep Japanese titles as-is for Japanese publications.
- `media-video` is a sibling `<a>` after the `media-item`. CSS (`.post-item.media-item:has(+ .media-video)`) removes the bottom border from the parent item to avoid double lines.

### OSS Projects (`#oss`)

Two subsections: the main grid, and **Maintainer / Contributor**. To add a new repo:

1. Add a `<a class="project-card" href="https://github.com/OWNER/REPO">` block with an empty `<span class="project-stars"></span>`. The JS at the bottom of `index.html` injects the star count from `data/stars.json` by matching the href.
2. Append `"OWNER/REPO"` to the `REPOS` list in `scripts/fetch-stars.py` and run it once locally to update `data/stars.json`. CI refreshes it daily.

### Published Apps (`#apps`)

```html
<a href="APP_STORE_URL" class="app-card" target="_blank" rel="noopener">
  <img src="ARTWORK_URL" alt="App Name" class="app-icon">
  <div class="app-info">
    <h3 class="app-name">App Name</h3>
    <p class="app-desc">Short description in Japanese (1–2 sentences).</p>
  </div>
</a>
```

**Auto-fetch app metadata via iTunes Search API**

Developer page: https://apps.apple.com/jp/developer/gigi-net-net/id447763559 (developer ID `447763559`).

List every app by the developer and grab the 512×512 artwork URL:

```sh
curl -s "https://itunes.apple.com/lookup?id=447763559&entity=software&country=jp&limit=50" \
  | python3 -c "
import json, sys
for r in json.load(sys.stdin)['results']:
    if r.get('wrapperType') == 'software':
        print(f\"{r['trackId']} | {r['trackName']} | {r.get('artworkUrl512') or r['artworkUrl100']}\")"
```

- Use the artwork URL as-is for `<img src=…>` — it's a stable Apple CDN URL.
- App Store page URL: `https://apps.apple.com/jp/app/SLUG/id{trackId}` (iTunes lookup returns `trackViewUrl` with the canonical URL-encoded slug).
- Japanese descriptions come from the App Store page; keep them 1–2 sentences.

### Writing (`#writing`)

**Books:** `book-item` entry with `.book-year` and `.book-title`. Link to publisher page (e.g. `gihyo.jp`).

**Tech Blog Articles:** grouped by company (`LY Corp`, `Cookpad`) under `<h4 class="subsubsection-title">`. Regular `.post-item` rows. Add new LY Corp entries at the top of the LY block.

**Personal Blog:** rendered dynamically from `data/posts.json`. No manual edits needed — the daily CI run refreshes it from the Hatena RSS feed.

### Career (`#career`)

Three subsections: `Work Experience`, `Technical Advisor`, `Education`. `career-item` grid with `.career-period` (dash-separated date range) and `.career-detail` (org name + optional role).

## Styling Conventions

- Red accent: `var(--color-accent)` = `#e60012` (Nintendo red).
- Fonts: **M PLUS Rounded 1c** for body, **Nunito** for headings.
- Buttons are pill-shaped (`border-radius: 999px`). Hero buttons use external favicons (`github.com/favicon.ico`, etc.) via `<img class="icon">` — prefer this over inline SVG logos to stay on-brand with each service.
- `talk-year` uses `<details>` + `<summary>`; the `+`/`−` indicator is generated by CSS `::after`.

## Pitfalls

- **Do not nest `<a>` inside `<a>`.** This silently corrupts the DOM in browsers (seen during the media-video layout fixes). If you need a clickable link inside another clickable card, put it as a sibling and rely on CSS grid positioning.
- **Regex-based HTML edits are dangerous.** Past bulk substitutions broke `</div>` pairing. Prefer explicit `Edit` on a single block and verify with `grep -c '<div' | <lhs> == grep -c '</div>'`.
- **`talk-event` wrap is visible on narrow screens.** Keep event names short (e.g. shorten `HAKATA.swift feat. Japan-\(region).swift #1` to `HAKATA.swift #1`).
- **CNAME and GitHub Pages config** must stay intact. Don't delete `CNAME`; `giginet.me` depends on it.
- **English vs Japanese.** Talks / project descriptions are English. Writing (books, tech blog posts, personal blog, interviews) use original Japanese titles.

## Deployment

Every push to `main` triggers `.github/workflows/deploy.yml`. The workflow also runs daily at 00:00 UTC, which re-fetches RSS + GitHub stars and redeploys. No manual step required after `git push`.
