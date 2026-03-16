#!/usr/bin/env python3
"""Fetch RSS feed from Hatena Blog and output as JSON."""

import json
import urllib.request
import xml.etree.ElementTree as ET

RSS_URL = "https://giginet.hateblo.jp/rss"
OUTPUT_PATH = "data/posts.json"

def main():
    with urllib.request.urlopen(RSS_URL) as response:
        xml_data = response.read()

    root = ET.fromstring(xml_data)
    items = root.findall(".//item")

    posts = []
    for item in items:
        title = item.findtext("title", "")
        link = item.findtext("link", "")
        pub_date = item.findtext("pubDate", "")
        posts.append({"title": title, "link": link, "pubDate": pub_date})

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(posts)} posts to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
