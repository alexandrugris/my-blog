# From The Trenches — The Code

Personal tech blog at [alexandrugris.github.io](https://alexandrugris.github.io), built with a custom Python static site generator.

## Stack

- **Generator** — `build.py`, a single-file Python SSG (no Jekyll, no Hugo, no dependencies beyond `markdown`, `pyyaml`, `pygments`)
- **Hosting** — GitHub Pages via [`alexandrugris.github.io`](https://github.com/alexandrugris/alexandrugris.github.io)
- **Posts** — Markdown with Jekyll-compatible front matter

## Quick start

```bash
pip install markdown pyyaml pygments   # once
python3 build.py                        # build → html/
cd html && python3 -m http.server 8000  # preview
```

## Writing a post

Add a `.md` file to `posts/` with this front matter:

```yaml
---
layout: post
title:  "Post Title"
date:   2024-01-15 10:00:00 +0200
categories: programming
---
```

Then rebuild. Images go in `assets/` and are referenced as `../assets/image.png`.

## Publishing

```bash
./publish.sh
```

Builds the site, copies `html/` to the local clone of `alexandrugris.github.io`, commits, and pushes.
