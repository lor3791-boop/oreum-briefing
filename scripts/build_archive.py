"""public/YYYY-MM-DD/ 폴더를 읽어 지난 브리핑 목록을 만든다.

생성물
- public/archive.json : 날짜·라벨·요약 (최신순) — 각 페이지 사이드바가 읽음
- public/archive/index.html : 지난 브리핑 전체 목록 페이지
- public/index.html : 최신 날짜로 리다이렉트
배포 워크플로에서 매번 실행되므로 수동으로 고칠 필요 없음.
"""
import datetime
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent / "public"
DAYS = "월화수목금토일"
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def meta(text, prop):
    m = re.search(r'<meta property="%s" content="([^"]*)"' % re.escape(prop), text)
    return html.unescape(m.group(1)) if m else ""


def main():
    items = []
    for d in sorted(ROOT.iterdir(), reverse=True):
        if not (d.is_dir() and DATE_RE.match(d.name) and (d / "index.html").exists()):
            continue
        dt = datetime.date.fromisoformat(d.name)
        text = (d / "index.html").read_text(encoding="utf-8")
        items.append({
            "date": d.name,
            "label": f"{dt.month}월 {dt.day}일 ({DAYS[dt.weekday()]})",
            "summary": meta(text, "og:description"),
        })
    if not items:
        return

    (ROOT / "archive.json").write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")

    latest = items[0]["date"]
    (ROOT / "index.html").write_text(
        f'<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0; url=/{latest}/">'
        f'<title>돈되는 오름브리핑</title><a href="/{latest}/">오늘 브리핑 보기</a>',
        encoding="utf-8",
    )

    rows = "\n".join(
        f'<a href="/{i["date"]}/" style="display:block;background:#FFFFFF;border-radius:14px;padding:16px 20px;text-decoration:none;color:#1C1C1A">'
        f'<div style="font-size:17px;font-weight:700">{i["date"][:4]}년 {html.escape(i["label"])} 브리핑</div>'
        f'<div style="font-size:14px;color:#5B5A55;margin-top:4px">{html.escape(i["summary"])}</div></a>'
        for i in items
    )
    page = f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>지난 브리핑 · 돈되는 오름브리핑</title>
<meta property="og:title" content="지난 브리핑 · 돈되는 오름브리핑">
<meta property="og:image" content="https://oreum-briefing.web.app/img/logo.png">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap">
<style>body{{margin:0;background:#F7F6F3;font-family:'Noto Sans KR',sans-serif;color:#1C1C1A}}a:hover{{outline:2px solid #D9001B}}</style></head>
<body>
<header style="background:#FFFFFF;border-bottom:4px solid #D9001B"><div style="max-width:760px;margin:0 auto;padding:12px 20px;display:flex;align-items:center;justify-content:space-between;gap:12px">
<a href="/" style="display:flex;align-items:center;gap:4px;text-decoration:none;outline:none"><img src="/img/logo.png" alt="돈" style="height:40px"><span style="font-weight:900;font-size:20px;color:#1C1C1A">되는 <span style="color:#D9001B">오름브리핑</span></span></a>
<a href="/" style="font-weight:700;color:#D9001B;text-decoration:none;outline:none">오늘 브리핑 →</a></div></header>
<main style="max-width:760px;margin:0 auto;padding:24px 20px 48px;display:flex;flex-direction:column;gap:10px">
<h1 style="font-size:24px;margin:0 0 8px">지난 브리핑</h1>
{rows}
</main></body></html>
"""
    (ROOT / "archive").mkdir(exist_ok=True)
    (ROOT / "archive" / "index.html").write_text(page, encoding="utf-8")


if __name__ == "__main__":
    main()
