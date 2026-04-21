import os
import requests
from bs4 import BeautifulSoup
import time
import json
import re

# ===== CONFIG =====
SAVE_DIR = "data/corpus"
META_FILE = "data/metadata.json"

BASE_URL = "https://en.wikipedia.org/wiki/"
SEED_PAGES = [
    "Data_science",
    "Artificial_intelligence",
    "Machine_learning",
    "Big_data",
    "Data_analysis"
]

MAX_PAGES = 1000
DELAY = 0.3

visited = set()
to_visit = list(SEED_PAGES)
metadata = {}

os.makedirs(SAVE_DIR, exist_ok=True)
os.makedirs("data", exist_ok=True)

# ===== CLEAN TEXT =====
def clean_text(text):
    text = text.lower()
    text = re.sub(r"\[[0-9]*\]", "", text)
    # giữ newline
    text = re.sub(r"[^\w\s\n]", " ", text)
    # xử lý từng dòng
    lines = text.split("\n")
    lines = [re.sub(r"\s+", " ", line).strip() for line in lines]

    return "\n".join(lines)

# ===== CRAWL =====
def crawl_page(title):
    url = BASE_URL + title
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        res = requests.get(url, headers=headers, timeout=10)

        if res.status_code != 200:
            print("Failed:", url)
            return None, None

        soup = BeautifulSoup(res.text, "html.parser")

        paragraphs = soup.find_all("p")
        text = "\n".join(p.get_text() for p in paragraphs)

        text = clean_text(text)

        print("Length:", len(text))

        if len(text) < 200:
            print("Too short, skip")
            return None, None

        return text, soup

    except Exception as e:
        print("Error:", e)
        return None, None

# ===== MAIN =====
count = 0

while to_visit and count < MAX_PAGES:
    title = to_visit.pop(0)

    if title in visited:
        continue

    print(f"[{count+1}] Crawling:", title)
    visited.add(title)

    text, soup = crawl_page(title)

    if text:
        filename = f"doc_{count+1}.txt"
        filepath = os.path.join(SAVE_DIR, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(text)

        # lưu metadata
        metadata[filename] = {
            "source": "Wikipedia",
            "url": BASE_URL + title,
            "topic": title
        }

        count += 1

        # lấy link mới
        links = soup.select("a[href^='/wiki/']")
        for link in links:
            href = link.get("href")

            if ":" in href:
                continue

            new_title = href.replace("/wiki/", "")

            if new_title not in visited and new_title not in to_visit:
                to_visit.append(new_title)

    time.sleep(DELAY)

# ===== SAVE METADATA =====
with open(META_FILE, "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=2)

print(f"\nDone! Collected {count} documents.")