import os
import random
import string

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SOURCE_DIR = os.path.join(BASE_DIR, "data", "corpus_grouped")
TEST_DIR = os.path.join(BASE_DIR, "data", "test_cases")

CATEGORIES = ["exact", "partial", "noise", "clean", "paraphrase"]


for cat in CATEGORIES:
    os.makedirs(os.path.join(TEST_DIR, cat), exist_ok=True)


def encode_path(path):
    rel_path = os.path.relpath(path, BASE_DIR)

    if rel_path.endswith(".txt"):
        rel_path = rel_path[:-4]

    return rel_path.replace("\\", "@").replace("/", "@")


def add_noise(text, noise_level=0.02):
    chars = list(text)
    num_changes = int(len(chars) * noise_level)

    for _ in range(num_changes):
        idx = random.randint(0, len(chars) - 1)
        chars[idx] = random.choice(string.ascii_lowercase + " ")

    return "".join(chars)


def create_partial(text):
    if len(text) < 100:
        return text

    start = random.randint(0, len(text) - 100)
    end = start + random.randint(80, 200)
    return text[start:end]


def generate_clean_text(length):
    words = [
        "alpha", "beta", "gamma", "delta",
        "random", "noise", "dummy", "test"
    ]
    return " ".join(random.choices(words, k=length))


def simple_paraphrase(text):
    synonyms = {
        "data": "information",
        "model": "structure",
        "system": "framework",
        "analysis": "examination",
        "learning": "training"
    }

    words = text.split()
    return " ".join([synonyms.get(w.lower(), w) for w in words])


def run():
    random.seed(42)
    count = 1

    print("🚀 Generating test cases...")

    for root, _, files in os.walk(SOURCE_DIR):
        for filename in files:
            if not filename.endswith(".txt"):
                continue

            filepath = os.path.join(root, filename)

            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()

            if len(text) < 500:
                continue

            start = random.randint(0, len(text) - 300)
            segment_text = text[start:start + 300]

            encoded = encode_path(filepath)
            name = f"test_{count}_from_{encoded}.txt"

            # EXACT
            with open(os.path.join(TEST_DIR, "exact", name), "w", encoding="utf-8") as f:
                f.write(segment_text)

            # PARTIAL
            with open(os.path.join(TEST_DIR, "partial", name), "w", encoding="utf-8") as f:
                f.write(create_partial(segment_text))

            # NOISE
            with open(os.path.join(TEST_DIR, "noise", name), "w", encoding="utf-8") as f:
                f.write(add_noise(segment_text))

            # PARAPHRASE
            with open(os.path.join(TEST_DIR, "paraphrase", name), "w", encoding="utf-8") as f:
                f.write(simple_paraphrase(segment_text))

            # CLEAN
            clean_name = f"test_{count}_clean.txt"
            with open(os.path.join(TEST_DIR, "clean", clean_name), "w", encoding="utf-8") as f:
                f.write(generate_clean_text(len(segment_text.split())))

            count += 1

            if count > 100:
                break

        if count > 100:
            break

    print(f"✅ Generated {count - 1} test cases at: {TEST_DIR}")


if __name__ == "__main__":
    run()