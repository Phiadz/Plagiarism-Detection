from __future__ import annotations


def _build_bad_char(pattern: str) -> dict[str, int]:
    table: dict[str, int] = {}
    for i, ch in enumerate(pattern):
        table[ch] = i
    return table


def _build_suffix_lengths(pattern: str) -> list[int]:
    m = len(pattern)
    suffix = [0] * m
    suffix[m - 1] = m

    g = m - 1
    f = 0
    for i in range(m - 2, -1, -1):
        if i > g and suffix[i + m - 1 - f] < i - g:
            suffix[i] = suffix[i + m - 1 - f]
        else:
            if i < g:
                g = i
            f = i
            while g >= 0 and pattern[g] == pattern[g + m - 1 - f]:
                g -= 1
            suffix[i] = f - g

    return suffix


def _build_good_suffix(pattern: str) -> list[int]:
    m = len(pattern)
    if m == 1:
        return [1]

    good_suffix = [m] * m
    suffix = _build_suffix_lengths(pattern)

    j = 0
    for i in range(m - 1, -1, -1):
        if suffix[i] == i + 1:
            while j < m - 1 - i:
                if good_suffix[j] == m:
                    good_suffix[j] = m - 1 - i
                j += 1

    for i in range(m - 1):
        good_suffix[m - 1 - suffix[i]] = m - 1 - i

    return [max(1, shift) for shift in good_suffix]


def search(pattern: str, text: str) -> list[int]:
    """Return all start indices where pattern appears in text (Boyer-Moore)."""
    if not pattern or not text or len(pattern) > len(text):
        return []

    m = len(pattern)
    n = len(text)
    bad_char = _build_bad_char(pattern)
    good_suffix = _build_good_suffix(pattern)
    matches: list[int] = []

    shift = 0
    while shift <= n - m:
        j = m - 1

        while j >= 0 and pattern[j] == text[shift + j]:
            j -= 1

        if j < 0:
            matches.append(shift)
            shift += good_suffix[0]
        else:
            mismatch = text[shift + j]
            bad_char_shift = j - bad_char.get(mismatch, -1)
            good_suffix_shift = good_suffix[j]
            shift += max(1, bad_char_shift, good_suffix_shift)

    return matches
