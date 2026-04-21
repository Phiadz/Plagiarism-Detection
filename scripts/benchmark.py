import os
import time
import csv
import random
import sys

# ===== FIX IMPORT =====
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

# ===== IMPORT =====
from algorithms.brute_force import search as brute_search
from algorithms.kmp import kmp_search
from algorithms.rabin_karp import search as rk_search
from algorithms.boyer_moore import search as bm_search

from utils.text_normalizer import normalize_text   # 🔥 QUAN TRỌNG

# ===== CONFIG =====
TEST_DIR = os.path.join(BASE_DIR, "data", "test_cases")
CORPUS_DIR = os.path.join(BASE_DIR, "data", "corpus_grouped")
RESULT_FILE = os.path.join(BASE_DIR, "data", "results", "benchmark.csv")

ALGORITHMS = {
    "BruteForce": brute_search,
    "KMP": kmp_search,
    "RabinKarp": rk_search,
    "BoyerMoore": bm_search
}

RANDOM_SEED = 42


# ===== HELPER =====

def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def calc_similarity(pattern_len, match_count):
    if pattern_len == 0:
        return 0.0
    if match_count == 0:
        return 0.0

    # Nếu tìm thấy khớp, trả về 100% cho exact match
    return round(100, 2)


def decode_path(encoded):
    rel_path = encoded.replace("@", os.sep)
    return os.path.join(BASE_DIR, rel_path)


def get_random_corpus():
    all_files = []
    for root, _, files in os.walk(CORPUS_DIR):
        for f in files:
            if f.endswith(".txt"):
                all_files.append(os.path.join(root, f))
    return random.choice(all_files) if all_files else None


def run_algorithm(algo_func, text, pattern):
    try:
        matches = algo_func(pattern, text)
        return list(matches) if matches else []
    except Exception as e:
        print(f"[ERROR] {algo_func.__name__}: {e}")
        return []


# ===== MAIN =====

def run():
    random.seed(RANDOM_SEED)
    results = []

    print("[1] Running benchmark...\n")

    for test_type in os.listdir(TEST_DIR):
        test_path = os.path.join(TEST_DIR, test_type)

        if not os.path.isdir(test_path):
            continue

        for test_file in os.listdir(test_path):
            if not test_file.endswith(".txt"):
                continue

            pattern_path = os.path.join(test_path, test_file)

            # 🔥 NORMALIZE
            pattern = normalize_text(read_file(pattern_path))

            target_files = []

            if "_from_" in test_file:
                encoded = test_file.split("_from_")[1]
                corpus_path = decode_path(encoded)

                if os.path.exists(corpus_path):
                    target_files.append(corpus_path)
                else:
                    print(f"[WARNING] Missing corpus: {corpus_path}")
                    continue
            else:
                random_file = get_random_corpus()
                if random_file:
                    target_files.append(random_file)

            for corpus_path in target_files:
                text = normalize_text(read_file(corpus_path))  # 🔥 NORMALIZE

                corpus_filename = os.path.basename(corpus_path)
                corpus_category = os.path.basename(os.path.dirname(corpus_path))

                for algo_name, algo_func in ALGORITHMS.items():
                    start = time.perf_counter()

                    matches = run_algorithm(algo_func, text, pattern)

                    end = time.perf_counter()

                    exec_time = round(end - start, 6)
                    match_count = len(matches)

                    similarity = calc_similarity(len(pattern), match_count)

                    results.append([
                        algo_name,
                        test_type,
                        corpus_category,
                        test_file,
                        corpus_filename,
                        match_count,
                        f"{similarity}%",
                        exec_time
                    ])

    save_results(results)


def save_results(results):
    print("\n[2] Saving results...")

    os.makedirs(os.path.dirname(RESULT_FILE), exist_ok=True)

    with open(RESULT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        writer.writerow([
            "Algorithm",
            "Test_Type",
            "Corpus_Size",
            "Test_File",
            "Corpus_File",
            "Match_Count",
            "Similarity",
            "Execution_Time(s)"
        ])

        writer.writerows(results)

    print(f"[DONE] Saved → {RESULT_FILE}")


if __name__ == "__main__":
    run()