#!/usr/bin/env python3
"""
Static site generator for alexandrugris.github.io
Converts Markdown posts to HTML, outputs to ./html/

Requirements: pip install markdown pyyaml pygments
"""

import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Dependency check
# ---------------------------------------------------------------------------

def _require(pkg, import_name=None):
    import importlib
    name = import_name or pkg
    try:
        return importlib.import_module(name)
    except ImportError:
        print(f"ERROR: Missing package '{pkg}'. Run: pip install {pkg}")
        sys.exit(1)

yaml      = _require("pyyaml", "yaml")
_require("markdown")
_require("pygments")

import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.tables import TableExtension
from markdown.extensions.toc import TocExtension

# ---------------------------------------------------------------------------
# Site configuration
# ---------------------------------------------------------------------------

SITE_TITLE       = "From The Trenches - The Code"
SITE_DESCRIPTION = (
    "Sometimes I take a few hours over the weekends or in the airports to try "
    "new things. I love technology and the randomness of the topics below is "
    "largely driven by my curiosity and the experiments I have done during "
    "these periods."
)
SITE_AUTHOR  = "Alexandru Gris"
SITE_EMAIL   = "alexandru.gris2006@gmail.com"
GITHUB_USER  = "alexandrugris"
TWITTER_USER = "alexandrugris"

POSTS_DIR  = Path("posts")
ASSETS_SRC = Path("assets")
OUT_DIR    = Path("html")

# Minima SCSS variables (compiled values)
_BRAND      = "#841212"
_TEXT       = "#454545"
_BG         = "#fdfdfd"
_GREY       = "#828282"
_GREY_LIGHT = "#d5d5d5"   # lighten(#828282, 40%)
_GREY_DARK  = "#2B2B2B"
_SPACING    = 30           # px
_WIDTH      = 800          # px

# ---------------------------------------------------------------------------
# CSS — faithfully compiled from the Minima SCSS source
# ---------------------------------------------------------------------------

def build_css() -> str:
    return f"""
/* ===== Reset ===== */
body,h1,h2,h3,h4,h5,h6,p,blockquote,pre,hr,dl,dd,ol,ul,figure{{margin:0;padding:0}}

/* ===== Base ===== */
body{{
  font: 400 16px/1.5 "Palatino Linotype","Book Antiqua",Palatino,serif;
  color:{_TEXT};
  background-color:{_BG};
  font-kerning:normal;
}}
h1,h2,h3,h4,h5,h6,p,blockquote,pre,ul,ol,dl,figure{{margin-bottom:{_SPACING//2}px}}
img{{max-width:100%;vertical-align:middle}}
figure>img{{display:block}}
ul,ol{{margin-left:{_SPACING}px}}
li>ul,li>ol{{margin-bottom:0}}
h1,h2,h3,h4,h5,h6{{font-weight:400}}

a{{color:{_BRAND};text-decoration:none}}
a:visited{{color:#6e0f0f}}
a:hover{{color:{_TEXT};text-decoration:underline}}

blockquote{{
  color:{_GREY};
  border-left:4px solid {_GREY_LIGHT};
  padding-left:{_SPACING//2}px;
  font-size:18px;
  letter-spacing:-1px;
  font-style:italic;
}}
blockquote>:last-child{{margin-bottom:0}}

/* ===== Code ===== */
pre,code{{
  font-size:12px;
  font-family:SFMono-Regular,Consolas,"Liberation Mono",Menlo,Monaco,monospace;
  border:1px solid #E3EDF3;
  background-color:{_GREY_DARK};
}}
code{{
  padding:1px 5px;
  border-radius:5px;
  color:#a9b7c6;
}}
/* inline code — light background */
code:not(pre code){{
  color:{_GREY_DARK};
  background-color:#f7fafb;
  border-color:#E3EDF3;
}}
pre{{
  padding:8px 12px;
  overflow-x:auto;
  border-radius:5px;
  border-width:0;
  color:#a9b7c6;
}}
pre>code{{border:0;padding:0;background:transparent;color:inherit;border-radius:0}}

/* ===== Wrapper ===== */
.wrapper{{
  max-width:calc({_WIDTH}px - ({_SPACING}px * 2));
  margin-right:auto;
  margin-left:auto;
  padding-right:{_SPACING}px;
  padding-left:{_SPACING}px;
}}
.wrapper::after{{content:"";display:table;clear:both}}

/* ===== Site header ===== */
.site-header{{
  border-top:5px solid {_BG};
  border-bottom:1px solid {_GREY_LIGHT};
  min-height:56px;
  padding-top:20px;
  padding-bottom:20px;
  position:relative;
}}
.site-title{{
  font-size:36px;
  font-weight:300;
  line-height:56px;
  margin-bottom:0;
  text-align:center;
  display:block;
  color:{_BRAND};
}}
.site-title:visited{{color:{_BRAND}}}
.site-title:hover{{color:{_TEXT};text-decoration:underline}}
.site-nav{{text-align:center;line-height:56px}}
.site-nav .menu-icon{{display:none}}
.site-nav .page-link{{color:{_TEXT};line-height:1.5}}
.site-nav .page-link:not(:last-child){{margin-right:20px}}

/* ===== Site footer ===== */
.site-footer{{border-top:1px solid {_GREY_LIGHT};padding:{_SPACING}px 0}}
.footer-heading{{font-size:18px;margin-bottom:{_SPACING//2}px}}
.contact-list,.social-media-list{{list-style:none;margin-left:0}}
.footer-col-wrapper{{font-size:15px;color:{_GREY};margin-left:-{_SPACING//2}px}}
.footer-col-wrapper::after{{content:"";display:table;clear:both}}
.footer-col{{float:left;margin-bottom:{_SPACING//2}px;padding-left:{_SPACING//2}px}}
.footer-col-1{{width:calc(35% - {_SPACING//2}px)}}
.footer-col-2{{width:calc(20% - {_SPACING//2}px)}}
.footer-col-3{{width:calc(45% - {_SPACING//2}px)}}

/* ===== Page content ===== */
.page-content{{padding:{_SPACING}px 0;flex:1}}
.page-heading{{font-size:20px}}

/* ===== Post list ===== */
.post-list{{margin-left:0;list-style:none}}
.post-list>li{{margin-bottom:{_SPACING}px}}
.post-excerpt p{{font-size:smaller}}
.post-meta{{font-size:14px;color:{_GREY}}}
.post-link{{display:block;font-size:24px}}
.rss-subscribe{{margin-top:10px}}

/* ===== Posts ===== */
.post-header{{margin-bottom:{_SPACING}px}}
.post-title{{font-size:28px;line-height:1.3}}
.post-content{{margin-bottom:{_SPACING}px}}
.post-content h2{{font-size:24px;margin-top:{_SPACING}px;margin-bottom:{_SPACING}px}}
.post-content h3{{font-size:20px;margin-top:{_SPACING}px;margin-bottom:{_SPACING}px}}
.post-content h4{{font-size:16px;margin-top:{_SPACING}px;margin-bottom:{_SPACING}px}}
.post-content img{{display:block;margin:1em auto;max-width:100%}}
.post-content table{{border-collapse:collapse;width:100%;margin:1em 0;font-size:15px}}
.post-content th,.post-content td{{border:1px solid {_GREY_LIGHT};padding:6px 10px;text-align:left}}
.post-content th{{background:#f6f8fa;font-weight:600}}

/* ===== Profile image ===== */
.face-alex-gris{{
  border-width:0;
  border-radius:50%;
  max-width:200px;
  max-height:200px;
  margin-left:auto;
  margin-right:auto;
  display:block;
  margin-bottom:25px;
}}

/* ===== Page layout ===== */
.page-wrapper{{display:flex;flex-direction:column;min-height:100vh}}

/* ===== Syntax highlighting — dark (JetBrains Darcula) ===== */
div.codehilite{{
  color:#a9b7c6;
  background-color:{_GREY_DARK};
  border:0;
  border-radius:5px;
  margin-bottom:{_SPACING//2}px;
  overflow-x:auto;
}}
div.codehilite pre{{
  background-color:transparent;
  border:0;
  border-radius:5px;
  padding:8px 12px;
  color:#a9b7c6;
  margin-bottom:0;
}}
div.codehilite pre>code{{background:transparent;border:0;color:inherit;padding:0}}

.codehilite .hll{{background-color:#49483e}}
.codehilite .c  {{color:#C7DD0C;font-style:italic}}
.codehilite .err{{color:#fdfdfd}}
.codehilite .k  {{color:#cc7832;font-weight:bold}}
.codehilite .o  {{font-weight:bold}}
.codehilite .cm {{color:#C7DD0C;font-style:italic}}
.codehilite .cp {{color:#C7DD0C;font-weight:bold}}
.codehilite .c1 {{color:#C7DD0C;font-style:italic}}
.codehilite .cs {{color:#C7DD0C;font-weight:bold;font-style:italic}}
.codehilite .gd {{color:#000;background-color:#fdd}}
.codehilite .ge {{font-style:italic}}
.codehilite .gr {{color:#a00}}
.codehilite .gh {{color:#999}}
.codehilite .gi {{color:#000;background-color:#dfd}}
.codehilite .go {{color:#888}}
.codehilite .gp {{color:#555}}
.codehilite .gs {{font-weight:bold}}
.codehilite .gu {{color:#aaa}}
.codehilite .gt {{color:#a00}}
.codehilite .kc {{font-weight:bold}}
.codehilite .kd {{color:#cc7832;font-weight:bold}}
.codehilite .kn {{color:#cc7832;font-weight:bold}}
.codehilite .kp {{color:#cc7832;font-weight:bold}}
.codehilite .kr {{font-weight:bold}}
.codehilite .kt {{color:#cc7832;font-weight:bold}}
.codehilite .m  {{color:#099}}
.codehilite .s  {{color:#9876aa}}
.codehilite .na {{color:#a9b7c6}}
.codehilite .nb {{color:#a9b7c6}}
.codehilite .nc {{color:#a9b7c6;font-weight:bold}}
.codehilite .no {{color:#008080}}
.codehilite .ni {{color:#800080}}
.codehilite .ne {{color:#a9b7c6;font-weight:bold}}
.codehilite .nf {{color:#a9b7c6;font-weight:bold}}
.codehilite .nn {{color:#555}}
.codehilite .nt {{color:#000080}}
.codehilite .nv {{color:#008080}}
.codehilite .ow {{font-weight:bold}}
.codehilite .w  {{color:#bbb}}
.codehilite .mf {{color:#099}}
.codehilite .mh {{color:#099}}
.codehilite .mi {{color:#099}}
.codehilite .mo {{color:#099}}
.codehilite .sb {{color:#9876aa}}
.codehilite .sc {{color:#9876aa}}
.codehilite .sd {{color:#9876aa}}
.codehilite .s2 {{color:#9876aa}}
.codehilite .se {{color:#9876aa}}
.codehilite .sh {{color:#9876aa}}
.codehilite .si {{color:#9876aa}}
.codehilite .sx {{color:#9876aa}}
.codehilite .sr {{color:#009926}}
.codehilite .s1 {{color:#9876aa}}
.codehilite .ss {{color:#990073}}
.codehilite .bp {{color:#999}}
.codehilite .vc {{color:#008080}}
.codehilite .vg {{color:#008080}}
.codehilite .vi {{color:#008080}}
.codehilite .il {{color:#099}}

/* ===== Responsive ===== */
@media(max-width:800px){{
  .wrapper{{max-width:calc({_WIDTH}px - {_SPACING}px);padding-right:{_SPACING//2}px;padding-left:{_SPACING//2}px}}
  .footer-col-1,.footer-col-2{{width:calc(50% - {_SPACING//2}px)}}
  .footer-col-3{{width:calc(100% - {_SPACING//2}px)}}
  .post-title{{font-size:24px}}
  .post-content h2{{font-size:20px}}
  .post-content h3{{font-size:16px}}
  .post-content h4{{font-size:14px}}
}}
@media(max-width:600px){{
  body{{font-size:14px}}
  .site-title{{font-size:19.2px}}
  .face-alex-gris{{max-width:100px;max-height:100px}}
  .footer-col{{float:none;width:calc(100% - {_SPACING//2}px)}}
  .post-title{{font-size:20px}}
  .post-content h2{{font-size:16px}}
  .post-content h3{{font-size:14px}}
  .post-content h4{{font-size:12px}}
}}
"""


# ---------------------------------------------------------------------------
# Front matter parser
# ---------------------------------------------------------------------------

def parse_front_matter(content: str):
    if not content.startswith("---"):
        return {}, content
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not m:
        return {}, content
    meta = yaml.safe_load(m.group(1)) or {}
    return meta, content[m.end():]


# ---------------------------------------------------------------------------
# URL / path helpers
# ---------------------------------------------------------------------------

def post_url(meta: dict, slug: str) -> str:
    cats = meta.get("categories", "")
    if isinstance(cats, list):
        cat_path = "/".join(c.lower() for c in cats)
    else:
        cat_path = "/".join(cats.lower().split())
    date = _parse_date(meta.get("date"))
    return f"{cat_path}/{date.strftime('%Y/%m/%d')}/{slug}.html"


def _parse_date(raw) -> datetime:
    if raw is None:
        return datetime(2000, 1, 1)
    if isinstance(raw, datetime):
        return raw
    if hasattr(raw, "year"):
        return datetime(raw.year, raw.month, raw.day)
    s = str(raw).split("+")[0].strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return datetime(2000, 1, 1)


def depth_prefix(url: str) -> str:
    levels = len(url.strip("/").split("/")) - 1
    return "../" * levels if levels else ""


# ---------------------------------------------------------------------------
# Markdown → HTML
# ---------------------------------------------------------------------------

_MD_EXT = [
    FencedCodeExtension(),
    CodeHiliteExtension(guess_lang=True, linenums=False, use_pygments=True),
    TableExtension(),
    TocExtension(permalink=False),
    "markdown.extensions.nl2br",
    "markdown.extensions.sane_lists",
]


def md_to_html(text: str) -> str:
    return markdown.markdown(text, extensions=_MD_EXT)


def fix_asset_paths(html: str, prefix: str) -> str:
    html = re.sub(r'(src|href)="\.\.\/assets\/', rf'\1="{prefix}assets/', html)
    html = re.sub(r'(src|href)="assets\/', rf'\1="{prefix}assets/', html)
    return html


def extract_excerpt(html: str, max_chars: int = 300) -> str:
    m = re.search(r"<p>(.*?)</p>", html, re.DOTALL)
    if not m:
        return ""
    text = re.sub(r"<[^>]+>", "", m.group(1)).replace("\n", " ").strip()
    if len(text) > max_chars:
        text = text[:max_chars].rsplit(" ", 1)[0] + "…"
    return text


# ---------------------------------------------------------------------------
# HTML page template  (matching default.html + header.html + footer.html)
# ---------------------------------------------------------------------------

def page_html(title: str, body: str, prefix: str, description: str = "") -> str:
    css_href = f"{prefix}assets/main.css"
    meta_desc = _esc(description or SITE_DESCRIPTION)
    page_title = _esc(title) if title == SITE_TITLE else f"{_esc(title)} | {_esc(SITE_TITLE)}"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{page_title}</title>
  <meta name="description" content="{meta_desc}">
  <link rel="stylesheet" href="{css_href}">
  <link rel="alternate" type="application/rss+xml" title="{_esc(SITE_TITLE)}" href="{prefix}feed.xml">
</head>
<body>
<div class="page-wrapper">

<header class="site-header" role="banner">
  <div class="wrapper">
    <div class="site-nav">
      <a class="site-title" href="{prefix}index.html">{_esc(SITE_TITLE)}</a>
    </div>
    <nav class="site-nav">
      <div class="trigger">
        <a class="page-link" href="{prefix}index.html">Home</a>
        <a class="page-link" href="{prefix}about/index.html">About</a>
        <a class="page-link" href="{prefix}sm/index.html">Social Media</a>
        <a class="page-link" href="https://alexandrugris.ro/" target="_blank" rel="noopener noreferrer">alexandrugris.ro<span aria-hidden="true"> ↗</span><span class="visually-hidden"> (opens in a new tab)</span></a>
      </div>
    </nav>
  </div>
</header>

<main class="page-content" aria-label="Content">
  <div class="wrapper">
{body}
  </div>
</main>

<footer class="site-footer">
  <div class="wrapper">
    <h2 class="footer-heading">{_esc(SITE_TITLE)}</h2>
    <div class="footer-col-wrapper">
      <div class="footer-col footer-col-1">
        <ul class="contact-list">
          <li>{_esc(SITE_AUTHOR)}</li>
          <li><a href="mailto:{SITE_EMAIL}">{_esc(SITE_EMAIL)}</a></li>
        </ul>
      </div>
      <div class="footer-col footer-col-2">
        <ul class="social-media-list">
          <li><a href="https://github.com/{GITHUB_USER}" target="_blank" rel="noopener">
            <svg viewBox="0 0 16 16" width="16" height="16" style="fill:#828282;vertical-align:middle;margin-right:4px"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>
            {GITHUB_USER}</a></li>
          <li><a href="https://twitter.com/{TWITTER_USER}" target="_blank" rel="noopener">
            <svg viewBox="0 0 16 16" width="16" height="16" style="fill:#828282;vertical-align:middle;margin-right:4px"><path d="M15.969 3.058a.5.5 0 0 0-.179.245l-.003.019a.5.5 0 0 0-.025.125V3.5a.5.5 0 0 0 .511.5h.001l-.002-.001h-.001a6.942 6.942 0 0 1-1.008.34 3.97 3.97 0 0 0 .732-1.722.5.5 0 0 0-.806-.355 8 8 0 0 1-2.588 1.178A4 4 0 0 0 8 2a4 4 0 0 0-4 4 4 4 0 0 0 .04.54A11.5 11.5 0 0 1 .96 2.755a.5.5 0 0 0-.81.05 4 4 0 0 0 1.17 5.098A3.98 3.98 0 0 1 .5 7.5a.5.5 0 0 0-.5.542 4 4 0 0 0 2.668 3.588 3.98 3.98 0 0 1-1.166.116.5.5 0 0 0-.362.844A4 4 0 0 0 4 13.5a8 8 0 0 1-5 1.5.5.5 0 0 0-.285.916A11.5 11.5 0 0 0 5.5 17 11.5 11.5 0 0 0 17 5.5a11.5 11.5 0 0 0-.029-.632 8 8 0 0 0 1.845-1.908.5.5 0 0 0-.847-.052z"/></svg>
            {TWITTER_USER}</a></li>
        </ul>
      </div>
      <div class="footer-col footer-col-3">
        <p>{_esc(SITE_DESCRIPTION)}</p>
      </div>
    </div>
  </div>
</footer>

</div>
</body>
</html>"""


def _esc(s: str) -> str:
    return (str(s)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


# ---------------------------------------------------------------------------
# Index page  (matching home.html)
# ---------------------------------------------------------------------------

def render_index(posts: list) -> str:
    items = []
    for p in posts:
        date_str = p["date"].strftime("%b %-d, %Y")
        excerpt_html = f'<p>{_esc(p["excerpt"])}</p>' if p["excerpt"] else ""
        items.append(f"""    <li>
      <span class="post-meta">{date_str}</span>
      <h2><a class="post-link" href="{p["url"]}">{_esc(p["title"])}</a></h2>
      <div class="post-excerpt">{excerpt_html}</div>
    </li>""")

    body = f"""<div class="home">

  <img src="assets/alexandrugris.webp" class="face-alex-gris" alt="This is me">

  <h2>Welcome to my technology blog</h2>
  <p>Sometimes I take a few hours over the weekends or in the airports to try new things.
  I love technology and the randomness of the topics below is largely driven by my curiosity
  and the experiments I have done during these periods. All the code is written by me and its
  only purpose is learning, experimentation and fun. When analyzing data, I either use public
  sources or generate it myself to play with a certain algorithm.</p>

  <h1 class="page-heading">Posts</h1>

  <ul class="post-list">
{chr(10).join(items)}
  </ul>

  <p class="rss-subscribe">subscribe <a href="feed.xml">via RSS</a></p>

</div>"""

    return page_html(SITE_TITLE, body, prefix="")


# ---------------------------------------------------------------------------
# Post page  (matching post.html)
# ---------------------------------------------------------------------------

def render_post(post: dict, prev_post, next_post) -> str:
    prefix = depth_prefix(post["url"])
    date_str = post["date"].strftime("%b %-d, %Y")
    content_html = fix_asset_paths(post["html"], prefix)

    nav_parts = []
    if next_post:  # older
        nav_parts.append(
            f'<span>← <a href="{prefix}{next_post["url"]}">{_esc(next_post["title"])}</a></span>'
        )
    if prev_post:  # newer
        nav_parts.append(
            f'<span><a href="{prefix}{prev_post["url"]}">{_esc(prev_post["title"])}</a> →</span>'
        )
    nav_html = ""
    if nav_parts:
        nav_html = (f'\n  <div class="post-nav" style="margin-top:30px;padding-top:20px;'
                    f'border-top:1px solid {_GREY_LIGHT};display:flex;'
                    f'justify-content:space-between;font-size:14px;">'
                    + "".join(nav_parts) + "</div>")

    body = f"""<article class="post" itemscope itemtype="http://schema.org/BlogPosting">

  <header class="post-header">
    <h1 class="post-title" itemprop="name headline">{_esc(post["title"])}</h1>
    <p class="post-meta">
      <time datetime="{post["date"].strftime("%Y-%m-%d")}" itemprop="datePublished">{date_str}</time>
    </p>
  </header>

  <div class="post-content" itemprop="articleBody">
{content_html}
  </div>{nav_html}

</article>"""

    return page_html(post["title"], body, prefix=prefix, description=post["excerpt"])


# ---------------------------------------------------------------------------
# Static pages  (matching page.html)
# ---------------------------------------------------------------------------

def render_about() -> str:
    body = """<article class="post">
  <header class="post-header">
    <h1 class="post-title">About</h1>
  </header>
  <div class="post-content">
    <img src="../assets/alexandrugris.webp" class="face-alex-gris" alt="Alexandru Gris">
    <p>Software engineer and technology enthusiast. I experiment with C++, Go, Python,
    machine learning, cryptography, distributed systems and everything in between.
    This blog is a collection of weekend experiments and notes to my future self.</p>
    <p>Find me on
      <a href="https://github.com/alexandrugris" target="_blank" rel="noopener">GitHub</a>,
      <a href="https://twitter.com/alexandrugris" target="_blank" rel="noopener">Twitter</a>, or
      <a href="mailto:alexandru.gris2006@gmail.com">email</a>.
    </p>
  </div>
</article>"""
    return page_html("About", body, prefix="../")


def render_sm() -> str:
    body = """<article class="post">
  <header class="post-header">
    <h1 class="post-title">Social Media</h1>
  </header>
  <div class="post-content">
    <ul>
      <li><strong>GitHub:</strong>
        <a href="https://github.com/alexandrugris" target="_blank" rel="noopener">github.com/alexandrugris</a></li>
      <li><strong>Twitter:</strong>
        <a href="https://twitter.com/alexandrugris" target="_blank" rel="noopener">twitter.com/alexandrugris</a></li>
      <li><strong>Email:</strong>
        <a href="mailto:alexandru.gris2006@gmail.com">alexandru.gris2006@gmail.com</a></li>
    </ul>
  </div>
</article>"""
    return page_html("Social Media", body, prefix="../")


# ---------------------------------------------------------------------------
# RSS feed
# ---------------------------------------------------------------------------

def render_feed(posts: list) -> str:
    items = []
    for p in posts[:20]:
        pub = p["date"].strftime("%a, %d %b %Y 00:00:00 +0000")
        items.append(f"""  <item>
    <title>{_esc(p["title"])}</title>
    <link>https://{GITHUB_USER}.github.io/{p["url"]}</link>
    <pubDate>{pub}</pubDate>
    <description>{_esc(p["excerpt"])}</description>
  </item>""")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
  <title>{_esc(SITE_TITLE)}</title>
  <link>https://{GITHUB_USER}.github.io/</link>
  <description>{_esc(SITE_DESCRIPTION)}</description>
{"".join(items)}
</channel>
</rss>"""


# ---------------------------------------------------------------------------
# Main build
# ---------------------------------------------------------------------------

def build():
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)

    assets_dst = OUT_DIR / "assets"
    if ASSETS_SRC.exists():
        shutil.copytree(ASSETS_SRC, assets_dst)
        print(f"Copied assets → {assets_dst}")
    else:
        assets_dst.mkdir(parents=True)
        print("WARNING: assets/ not found")

    css_path = assets_dst / "main.css"
    css_path.write_text(build_css(), encoding="utf-8")
    print(f"Wrote CSS → {css_path}")

    posts = []
    for md_file in sorted(POSTS_DIR.glob("*.md")):
        raw = md_file.read_text(encoding="utf-8")
        meta, body = parse_front_matter(raw)
        if not meta:
            print(f"  SKIP (no front matter): {md_file.name}")
            continue

        stem = md_file.stem
        slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", stem)
        slug = re.sub(r"\s+", "-", slug)

        html_content = md_to_html(body)
        excerpt = extract_excerpt(html_content)
        date = _parse_date(meta.get("date"))

        cats_raw = meta.get("categories", "")
        cats = cats_raw if isinstance(cats_raw, list) else (cats_raw.split() if cats_raw else [])

        url = post_url(meta, slug)
        title = meta.get("title", slug.replace("-", " ").title())

        posts.append({
            "slug": slug, "title": title, "date": date,
            "categories": cats, "url": url,
            "html": html_content, "excerpt": excerpt,
        })
        print(f"  {md_file.name}  →  {url}")

    posts.sort(key=lambda p: p["date"], reverse=True)

    for i, post in enumerate(posts):
        prev_post = posts[i - 1] if i > 0 else None
        next_post = posts[i + 1] if i < len(posts) - 1 else None
        out_path = OUT_DIR / post["url"]
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(render_post(post, prev_post, next_post), encoding="utf-8")

    print(f"\nWrote {len(posts)} posts.")

    (OUT_DIR / "index.html").write_text(render_index(posts), encoding="utf-8")
    print("Wrote index.html")

    (OUT_DIR / "about").mkdir(exist_ok=True)
    (OUT_DIR / "about" / "index.html").write_text(render_about(), encoding="utf-8")

    (OUT_DIR / "sm").mkdir(exist_ok=True)
    (OUT_DIR / "sm" / "index.html").write_text(render_sm(), encoding="utf-8")
    print("Wrote about/ and sm/")

    (OUT_DIR / "feed.xml").write_text(render_feed(posts), encoding="utf-8")
    shutil.copy(OUT_DIR / "index.html", OUT_DIR / "404.html")
    print("Wrote feed.xml + 404.html")

    total = sum(1 for _ in OUT_DIR.rglob("*") if _.is_file())
    print(f"\nBuild complete → {OUT_DIR}/  ({len(posts)} posts, {total} files)")


if __name__ == "__main__":
    os.chdir(Path(__file__).parent)
    build()
