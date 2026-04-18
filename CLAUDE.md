# CLAUDE.md

This file provides guidance to Claude Code when working in this repository.

## Quick reference

| Task | Command |
|------|---------|
| Install deps (once) | `pip install markdown pyyaml pygments` |
| Build site | `python3 build.py` |
| Preview | `cd html && python3 -m http.server 8000` |
| Publish to GitHub Pages | `./publish.sh` |

## Repository layout

```
posts/          Markdown blog posts (Jekyll-compatible front matter)
assets/         Images, data files, main.scss (source; never edit html/assets directly)
build.py        Single-file static site generator — no external config or templates
publish.sh      Build + rsync to alexandrugris.github.io + git push
html/           Generated output (do not edit manually)
```

## Adding or editing posts

Post files live in `posts/` and must have YAML front matter:

```yaml
---
layout: post
title:  "Post Title"
date:   2024-01-15 10:00:00 +0200
categories: category subcategory
---
```

- `categories` is a space-separated string or YAML list; each word becomes a URL path segment.
- Images: reference as `../assets/filename.png` — the build rewrites paths automatically.
- Rebuild after any change: `python3 build.py`.

## How build.py works

Everything is in `build.py` — no config files, no templates directory.

1. **Parse** — `parse_front_matter()` splits YAML front matter from Markdown body. Posts without front matter are skipped.
2. **URL** — `post_url()` produces `{categories}/{YYYY}/{MM}/{DD}/{slug}.html`. Slug = filename with leading `YYYY-MM-DD-` stripped and spaces → `-`.
3. **Markdown → HTML** — `md_to_html()` uses python-markdown with: fenced code blocks, CodeHilite (Pygments), tables, TOC, nl2br, sane_lists.
4. **Path fixing** — `fix_asset_paths()` rewrites `../assets/` and `assets/` to the correct `../../…/assets/` depth prefix computed by `depth_prefix()`.
5. **Template** — `page_html()` is the single shared HTML template; uses `prefix` for all hrefs so the site works from any subdirectory.
6. **Output** — writes `html/assets/` (copied source assets + generated `main.css`), all post HTML files, `index.html`, `about/index.html`, `sm/index.html`, `feed.xml`, `404.html`.

## Site configuration

- **Metadata** (title, author, email, GitHub/Twitter handles): constants at the top of `build.py` (lines 43–51).
- **CSS tokens** (brand color `#841212`, font Palatino, content width 800px, text `#454545`): inside `build_css()`.
- **About page**: `render_about()` — hardcoded HTML, edit directly.
- **Social Media page**: `render_sm()` — hardcoded HTML, edit directly.

## Publishing

`publish.sh` assumes the `alexandrugris.github.io` repo is cloned at `../alexandrugris.github.io` relative to this directory. Override with:

```bash
PAGES_DIR=/path/to/alexandrugris.github.io ./publish.sh
```

If the pages repo isn't cloned yet:

```bash
git clone https://github.com/alexandrugris/alexandrugris.github.io.git ../alexandrugris.github.io
```

## Source repository

`https://github.com/alexandrugris/my-blog`
