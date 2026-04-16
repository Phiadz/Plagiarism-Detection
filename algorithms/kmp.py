import re
import time

# ===============================
# Chuẩn hóa text
# ===============================
def normalize(text):
    return re.sub(r'\s+', ' ', text.lower()).strip()


# ===============================
# KMP - build LPS
# ===============================
def build_lps(pattern):
    lps = [0] * len(pattern)
    j = 0

    for i in range(1, len(pattern)):
        while j > 0 and pattern[i] != pattern[j]:
            j = lps[j - 1]

        if pattern[i] == pattern[j]:
            j += 1
            lps[i] = j

    return lps


# ===============================
# KMP - search
# ===============================
def kmp_search(pattern, text):
    if not pattern or len(pattern) > len(text):
        return []

    lps = build_lps(pattern)
    result = []
    j = 0

    for i in range(len(text)):
        while j > 0 and text[i] != pattern[j]:
            j = lps[j - 1]

        if text[i] == pattern[j]:
            j += 1

        if j == len(pattern):
            result.append(i - j + 1)
            j = lps[j - 1]

    return result


# ===============================
# HÀM CHẠY CHUNG
# ===============================
def run_kmp(text, pattern):
    text = normalize(text)
    pattern = normalize(pattern)

    start = time.perf_counter()
    result = kmp_search(pattern, text)
    end = time.perf_counter()

    return result, end - start


# ===============================
# MAIN
# ===============================
if __name__ == "__main__":
    print("===== PHÁT HIỆN ĐẠO VĂN (KMP) =====")

    text = input("Nhập văn bản: ")
    pattern = input("Nhập đoạn nghi ngờ: ")

    result, t = run_kmp(text, pattern)

    print("\nKết quả:", result)
    print("Số lần:", len(result))

    for pos in result:
        print(f"- \"{text[pos:pos+len(pattern)]}\"")

    print(f"Thời gian: {t:.6f}s")
