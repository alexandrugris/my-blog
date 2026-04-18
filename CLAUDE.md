# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build

```bash
# Install dependencies (once)
pip install markdown pyyaml pygments

# Build the site
python3 build.py
```

Output goes to `./html/`. The entire `html/` folder is what gets deployed — copy it to GitHub Pages or an nginx `www` root as-is.

To preview locally:
```bash
cd html && python3 -m http.server 8000
```

## Repository layout

```
posts/          49 Markdown blog posts (Jekyll front matter)
assets/         Images, data files, main.scss (source reference only)
build.py        Single-file static site generator
html/           Generated output (do not edit manually)
```

## How build.py works

Everything is in `build.py` — no config files, no templates directory. The pipeline is:

1. **Parse** — `parse_front_matter()` splits YAML front matter from body. Posts without front matter are skipped.
2. **URL generation** — `post_url()` produces Jekyll-compatible URLs: `{categories}/{YYYY}/{MM}/{DD}/{slug}.html`. The slug is the filename with the leading `YYYY-MM-DD-` stripped and spaces replaced by `-`.
3. **Markdown → HTML** — `md_to_html()` uses python-markdown with fenced code blocks, CodeHilite (Pygments syntax highlighting), tables, TOC, nl2br, and sane_lists extensions.
4. **Path fixing** — `fix_asset_paths()` rewrites `../assets/` and `assets/` references to the correct relative depth prefix (e.g. a post 5 directories deep gets `../../../../../assets/`). The depth is computed by `depth_prefix()`.
5. **Rendering** — `page_html()` is the single HTML template shared by all pages. It uses `prefix` (the `../../` string) for all hrefs so the site works from any subdirectory.
6. **Output** — `html/assets/` gets the copied source assets plus a generated `main.css`. Post HTML, `index.html`, `about/index.html`, `sm/index.html`, `feed.xml`, and `404.html` (copy of index for GitHub Pages 404 fallback) are written.

## Adding or editing posts

Post files live in `posts/` and must have this front matter:

```yaml
---
layout: post
title:  "Post Title"
date:   2024-01-15 10:00:00 +0200
categories: category subcategory
---
```

- `categories` can be a space-separated string or a YAML list; each word becomes a path segment in the URL.
- Images referenced as `../assets/filename.png` in Markdown are automatically rewritten to the correct relative path on build.
- Re-run `python3 build.py` after any change to posts or assets.

## Site configuration

All site metadata (title, author, email, GitHub/Twitter handles) is defined as constants at the top of `build.py` (lines 43–51). CSS design tokens (brand color `#841212`, font Palatino, content width 800px, text color `#454545`) are in `build_css()`.

The About and Social Media pages are rendered as hardcoded HTML inside `render_about()` and `render_sm()` — edit those functions to change page content.
