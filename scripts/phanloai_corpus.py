import os
import shutil
import json

# ===== CONFIG ĐƯỜNG DẪN TUYỆT ĐỐI =====
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SOURCE_DIR = os.path.join(BASE_DIR, "data", "corpus")
TARGET_DIR = os.path.join(BASE_DIR, "data", "corpus_grouped")
META_FILE = os.path.join(BASE_DIR, "data", "metadata.json")

SMALL = 500
MEDIUM = 2000

os.makedirs(os.path.join(TARGET_DIR, "small"), exist_ok=True)
os.makedirs(os.path.join(TARGET_DIR, "medium"), exist_ok=True)
os.makedirs(os.path.join(TARGET_DIR, "large"), exist_ok=True)

# ===== PROCESS =====
def run():
    # Load metadata
    if os.path.exists(META_FILE):
        with open(META_FILE, "r", encoding="utf-8") as f:
            try:
                metadata = json.load(f)
            except json.JSONDecodeError:
                metadata = {}
    else:
        metadata = {}

    stats = {"small": 0, "medium": 0, "large": 0}
    
    if not os.path.exists(SOURCE_DIR):
        print(f"Lỗi: Không tìm thấy {SOURCE_DIR}")
        return

    for filename in os.listdir(SOURCE_DIR):
        if not filename.endswith(".txt"):
            continue

        filepath = os.path.join(SOURCE_DIR, filename)

        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()

        word_count = len(text.split())

        if word_count < SMALL:
            category = "small"
        elif word_count < MEDIUM:
            category = "medium"
        else:
            category = "large"

        # copy file
        target_path = os.path.join(TARGET_DIR, category, filename)
        shutil.copy(filepath, target_path)

        # update metadata
        if filename not in metadata:
            metadata[filename] = {}
        metadata[filename]["words"] = word_count
        metadata[filename]["size"] = category

        stats[category] += 1
        print(f"Phân loại: {filename} -> {category} ({word_count} words)")

    # Save updated metadata
    with open(META_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print("\nStats phân loại:", stats)
    print("Done Phân loại corpus!")

if __name__ == "__main__":
    run()