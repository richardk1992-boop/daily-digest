#!/usr/bin/env python3
"""Regenerate index.html from digests/*.html and .meta/*.json."""
from pathlib import Path
import json
import re
from html import escape

ROOT = Path(__file__).resolve().parent.parent
DIGEST_DIR = ROOT / "digests"
META_DIR = ROOT / ".meta"
INDEX = ROOT / "index.html"


def parse_title_from_html(html_path: Path) -> str:
    """Best-effort: pull the first h1 text from the HTML."""
    try:
        text = html_path.read_text(encoding="utf-8")
    except Exception:
        return ""
    m = re.search(r"<h1[^>]*>(.*?)</h1>", text, re.S | re.I)
    if not m:
        return ""
    raw = re.sub(r"<[^>]+>", "", m.group(1)).strip()
    raw = re.sub(r"\s+", " ", raw)
    return raw[:140]


def collect_entries():
    entries = []
    for html_path in sorted(DIGEST_DIR.glob("*.html"), reverse=True):
        date = html_path.stem  # e.g. 2026-06-01
        meta_path = META_DIR / f"{date}.json"
        vol = ""
        title = ""
        if meta_path.exists():
            try:
                m = json.loads(meta_path.read_text(encoding="utf-8"))
                vol = str(m.get("vol", "") or "")
                title = (m.get("title") or "").strip()
            except Exception:
                pass
        if not title:
            title = parse_title_from_html(html_path)
        if not title:
            title = f"Digest {date}"
        entries.append({"date": date, "vol": vol, "title": title, "href": f"digests/{date}.html"})
    return entries


HTML_TEMPLATE = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>MIRA · 每日阅读简报</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Barlow:wght@400;500;700;900&family=IBM+Plex+Mono:wght@400;500&family=Noto+Sans+SC:wght@400;500;700;900&display=swap" rel="stylesheet">
<style>
  :root {{
    --c-bg: #111111;
    --c-bg-alt: #1a1a18;
    --c-fg: #f0ece5;
    --c-accent: #e85d26;
    --c-border: #282826;
    --c-muted: #888880;
  }}
  * {{ box-sizing: border-box; }}
  html, body {{ margin: 0; padding: 0; background: var(--c-bg); color: var(--c-fg); }}
  body {{
    font-family: "Noto Sans SC", "Barlow", system-ui, -apple-system, sans-serif;
    font-size: 16px;
    line-height: 1.7;
    min-height: 100vh;
  }}
  .masthead {{
    border-bottom: 1px solid var(--c-border);
    padding: 56px 6vw 28px;
  }}
  .kicker {{
    font-family: "IBM Plex Mono", monospace;
    font-size: 12px;
    letter-spacing: 0.16em;
    color: var(--c-muted);
    text-transform: uppercase;
  }}
  h1 {{
    font-family: "Barlow", sans-serif;
    font-weight: 900;
    font-size: clamp(48px, 7vw, 96px);
    line-height: 0.95;
    letter-spacing: -0.02em;
    margin: 18px 0 16px;
  }}
  h1 .accent {{ color: var(--c-accent); }}
  .tagline {{
    color: var(--c-muted);
    font-size: 17px;
    max-width: 720px;
    margin: 0;
  }}
  main {{
    padding: 32px 6vw 96px;
    max-width: 1080px;
  }}
  .section-title {{
    font-family: "IBM Plex Mono", monospace;
    font-size: 12px;
    letter-spacing: 0.16em;
    color: var(--c-muted);
    text-transform: uppercase;
    padding-top: 24px;
    margin: 0 0 24px;
  }}
  .entry-list {{ list-style: none; margin: 0; padding: 0; }}
  .entry {{
    display: grid;
    grid-template-columns: 132px 1fr auto;
    gap: 24px;
    align-items: baseline;
    padding: 22px 0;
    border-top: 1px solid var(--c-border);
  }}
  .entry:last-child {{ border-bottom: 1px solid var(--c-border); }}
  .entry-date {{
    font-family: "IBM Plex Mono", monospace;
    font-size: 14px;
    color: var(--c-muted);
    letter-spacing: 0.02em;
  }}
  .entry-title {{
    font-family: "Barlow", "Noto Sans SC", sans-serif;
    font-weight: 700;
    font-size: 21px;
    line-height: 1.35;
    margin: 0;
  }}
  .entry-title a {{ color: var(--c-fg); text-decoration: none; }}
  .entry-title a:hover, .entry-title a:focus {{ color: var(--c-accent); }}
  .entry-vol {{
    font-family: "IBM Plex Mono", monospace;
    font-size: 12px;
    color: var(--c-accent);
    letter-spacing: 0.08em;
    white-space: nowrap;
  }}
  .empty {{ color: var(--c-muted); padding: 48px 0; text-align: center; font-family: "IBM Plex Mono", monospace; }}
  footer {{
    margin-top: 64px;
    padding: 24px 6vw;
    border-top: 1px solid var(--c-border);
    color: var(--c-muted);
    font-family: "IBM Plex Mono", monospace;
    font-size: 11px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }}
  @media (max-width: 640px) {{
    .entry {{ grid-template-columns: 1fr; gap: 6px; }}
    .entry-vol {{ order: -1; }}
  }}
</style>
</head>
<body>
<header class="masthead">
  <div class="kicker">MIRA · DAILY READING DIGEST</div>
  <h1>每日<span class="accent">阅读</span>简报</h1>
  <p class="tagline">Mira 每天清晨 6 点扫描过去 24 小时的阅读流，挑出值得深读的 1–2 篇，做 5 维评分、原文引用、中文翻译、判断批注，沉淀成可分享的杂志页。</p>
</header>
<main>
  <h2 class="section-title">All issues · {count} 篇</h2>
  {entries_html}
</main>
<footer>© Mira · Auto-published via GitHub Actions · Last build {build_time}</footer>
</body>
</html>
"""


def render(entries):
    from datetime import datetime, timezone, timedelta
    cst = timezone(timedelta(hours=8))
    build_time = datetime.now(cst).strftime("%Y-%m-%d %H:%M CST")

    if not entries:
        entries_html = '<div class="empty">No digests published yet.</div>'
    else:
        items = []
        for e in entries:
            vol_html = f'<span class="entry-vol">Vol.{escape(str(e["vol"]).zfill(3))}</span>' if e["vol"] else '<span class="entry-vol"></span>'
            items.append(
                '<li class="entry">'
                f'<span class="entry-date">{escape(e["date"])}</span>'
                f'<h3 class="entry-title"><a href="{escape(e["href"])}">{escape(e["title"])}</a></h3>'
                f'{vol_html}'
                '</li>'
            )
        entries_html = '<ul class="entry-list">' + "".join(items) + '</ul>'

    return HTML_TEMPLATE.format(
        count=len(entries),
        entries_html=entries_html,
        build_time=build_time,
    )


def main():
    DIGEST_DIR.mkdir(exist_ok=True)
    META_DIR.mkdir(exist_ok=True)
    entries = collect_entries()
    INDEX.write_text(render(entries), encoding="utf-8")
    print(f"Wrote {INDEX} ({len(entries)} entries)")


if __name__ == "__main__":
    main()
