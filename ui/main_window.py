from __future__ import annotations

import csv
import json
import os
import random
import threading
import time
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from algorithms import (
    boyer_moore_search,
    brute_force_search,
    kmp_search,
    rabin_karp_search,
)
from ui.result_view import format_compare_summary, format_corpus_top_summary, format_result_summary
from utils.file_loader import list_text_files, read_text_file
from utils.text_normalizer import normalize_text
from utils.timer import Timer


MISSING_PATTERN_TITLE = "Missing pattern"
MISSING_PATTERN_MSG = "Please enter a pattern to search."


class MainWindow:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Plagiarism Detection - String Matching")
        self.root.geometry("1000x700")

        # --- Interactive Variables ---
        self.text_content = ""
        self.corpus_files: list[str] = []
        self.manual_corpus_files: list[str] = []
        self.folder_corpus_files: list[str] = []

        self.pattern_var = tk.StringVar()
        self.algorithm_var = tk.StringVar(value="kmp")
        self.result_var = tk.StringVar(value="No analysis yet")
        self.last_run_result: dict[str, float | int | str] | None = None
        self.last_compare_results: list[dict[str, float | int | str]] = []
        self.last_corpus_results: list[dict[str, float | int | str]] = []
        self.corpus_folder: str | None = None
        self.text_widget: tk.Text | None = None

        # --- Benchmark Variables ---
        self.benchmark_test_dir = tk.StringVar(value="Not selected")
        self.benchmark_corpus_dir = tk.StringVar(value="Not selected")
        self.benchmark_status_var = tk.StringVar(value="Ready")
        self.benchmark_log_widget: tk.Text | None = None
        self.benchmark_progress: ttk.Progressbar | None = None
        self.benchmark_results: list[dict] = []

    def _merge_corpus_files(self) -> list[str]:
        seen: set[str] = set()
        merged: list[str] = []
        for file_path in [*self.manual_corpus_files, *self.folder_corpus_files]:
            key = str(Path(file_path).resolve())
            if key in seen:
                continue
            seen.add(key)
            merged.append(file_path)
        return merged

    def _refresh_corpus_selection(self) -> None:
        self.corpus_files = self._merge_corpus_files()
        self.result_var.set(
            "Corpus selected | "
            f"manual: {len(self.manual_corpus_files)} | "
            f"folder: {len(self.folder_corpus_files)} | "
            f"total unique: {len(self.corpus_files)}"
        )

    def _normalize_with_map(self, text: str) -> tuple[str, list[int]]:
        normalized_chars: list[str] = []
        index_map: list[int] = []
        prev_space = False

        for raw_idx, ch in enumerate(text):
            lower = ch.lower()
            if lower.isspace():
                if normalized_chars and not prev_space:
                    normalized_chars.append(" ")
                    index_map.append(raw_idx)
                prev_space = True
                continue

            normalized_chars.append(lower)
            index_map.append(raw_idx)
            prev_space = False

        if normalized_chars and normalized_chars[-1] == " ":
            normalized_chars.pop()
            index_map.pop()

        return "".join(normalized_chars), index_map

    def setup_ui(self) -> None:
        # Tách tab Notebook
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.tab_interactive = ttk.Frame(notebook)
        self.tab_benchmark = ttk.Frame(notebook)

        notebook.add(self.tab_interactive, text="Interactive Analysis")
        notebook.add(self.tab_benchmark, text="Batch Benchmark")

        self._setup_interactive_tab()
        self._setup_benchmark_tab()

    def _setup_interactive_tab(self) -> None:
        top = ttk.Frame(self.tab_interactive, padding=10)
        top.pack(fill=tk.X)

        ttk.Button(top, text="Upload Text File", command=self._on_upload).pack(side=tk.LEFT)
        ttk.Button(top, text="Select Corpus Files", command=self._on_select_corpus).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(top, text="Select Corpus Folder", command=self._on_select_corpus_folder).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Label(top, text="Pattern:").pack(side=tk.LEFT, padx=(12, 4))
        ttk.Entry(top, textvariable=self.pattern_var, width=30).pack(side=tk.LEFT)

        algo_box = ttk.Combobox(
            top,
            textvariable=self.algorithm_var,
            values=["brute_force", "kmp", "rabin_karp", "boyer_moore"],
            width=14,
            state="readonly",
        )
        algo_box.pack(side=tk.LEFT, padx=8)

        ttk.Button(top, text="Run Analysis", command=self._on_run).pack(side=tk.LEFT)
        ttk.Button(top, text="Compare Algorithms", command=self._on_compare).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(top, text="Rank Corpus", command=self._on_rank_corpus).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(top, text="Export Result", command=self._on_export).pack(side=tk.LEFT, padx=(8, 0))

        text_frame = ttk.Frame(self.tab_interactive)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        y_scroll = ttk.Scrollbar(text_frame, orient=tk.VERTICAL)
        x_scroll = ttk.Scrollbar(text_frame, orient=tk.HORIZONTAL)

        self.text_widget = tk.Text(
            text_frame,
            wrap=tk.NONE,
            font=("Consolas", 11),
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set,
        )
        y_scroll.config(command=self.text_widget.yview)
        x_scroll.config(command=self.text_widget.xview)

        self.text_widget.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        text_frame.rowconfigure(0, weight=1)
        text_frame.columnconfigure(0, weight=1)

        self.text_widget.tag_config("match", background="#FFE08A")
        ttk.Label(self.tab_interactive, textvariable=self.result_var, anchor="w").pack(fill=tk.X, padx=10, pady=(0, 10))

    def _setup_benchmark_tab(self) -> None:
        control_frame = ttk.Frame(self.tab_benchmark, padding=10)
        control_frame.pack(fill=tk.X)

        row1 = ttk.Frame(control_frame)
        row1.pack(fill=tk.X, pady=5)
        ttk.Button(row1, text="Select Test Cases Folder", command=self._on_select_benchmark_test).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(row1, textvariable=self.benchmark_test_dir).pack(side=tk.LEFT)

        row2 = ttk.Frame(control_frame)
        row2.pack(fill=tk.X, pady=5)
        ttk.Button(row2, text="Select Corpus Grouped Folder", command=self._on_select_benchmark_corpus).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(row2, textvariable=self.benchmark_corpus_dir).pack(side=tk.LEFT)

        row3 = ttk.Frame(control_frame)
        row3.pack(fill=tk.X, pady=15)
        ttk.Button(row3, text="▶ Run Batch Benchmark", command=self._on_run_benchmark_thread).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(row3, text="💾 Export Benchmark CSV", command=self._on_export_benchmark).pack(side=tk.LEFT)
        
        self.benchmark_progress = ttk.Progressbar(control_frame, orient="horizontal", mode="determinate")
        self.benchmark_progress.pack(fill=tk.X, pady=5)
        ttk.Label(control_frame, textvariable=self.benchmark_status_var).pack(anchor="w")

        log_frame = ttk.Frame(self.tab_benchmark, padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        y_scroll = ttk.Scrollbar(log_frame, orient=tk.VERTICAL)
        self.benchmark_log_widget = tk.Text(log_frame, wrap=tk.WORD, font=("Consolas", 10), yscrollcommand=y_scroll.set)
        y_scroll.config(command=self.benchmark_log_widget.yview)
        
        self.benchmark_log_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    # --- Interactive Tab Methods ---
    def _on_upload(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Select text file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not file_path:
            return

        try:
            self.text_content = read_text_file(file_path)
            if self.text_widget:
                self.text_widget.delete("1.0", tk.END)
                self.text_widget.insert(tk.END, self.text_content)
            self.result_var.set(f"Loaded: {file_path}")
        except Exception as exc:
            messagebox.showerror("Read error", str(exc))

    def _on_select_corpus(self) -> None:
        file_paths = filedialog.askopenfilenames(
            title="Select corpus files",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not file_paths:
            return

        self.manual_corpus_files = list(file_paths)
        self._refresh_corpus_selection()

    def _on_select_corpus_folder(self) -> None:
        folder_path = filedialog.askdirectory(title="Select corpus folder")
        if not folder_path:
            return

        try:
            text_files = list_text_files(folder_path)
        except Exception as exc:
            messagebox.showerror("Corpus read error", str(exc))
            return

        if not text_files:
            messagebox.showwarning("Empty corpus", "No .txt files found in selected folder.")
            return

        self.corpus_folder = folder_path
        self.folder_corpus_files = [str(path) for path in text_files]
        self._refresh_corpus_selection()

    def _on_run(self) -> None:
        if not self.text_content:
            messagebox.showwarning("Missing text", "Please upload a text file first.")
            return

        pattern = normalize_text(self.pattern_var.get())
        if not pattern:
            messagebox.showwarning(MISSING_PATTERN_TITLE, MISSING_PATTERN_MSG)
            return

        text, index_map = self._normalize_with_map(self.text_content)
        algorithm = self.algorithm_var.get()

        search_map = {
            "brute_force": brute_force_search,
            "kmp": kmp_search,
            "rabin_karp": rabin_karp_search,
            "boyer_moore": boyer_moore_search,
        }

        timer = Timer()
        timer.start()
        matches = search_map[algorithm](pattern, text)
        elapsed_ms = timer.stop()
        similarity = (len(matches) * len(pattern) / max(1, len(text))) * 100

        self._highlight_matches(matches, len(pattern), index_map=index_map)
        self.last_run_result = {
            "algorithm": algorithm,
            "matches": len(matches),
            "elapsed_ms": elapsed_ms,
            "similarity": similarity,
            "pattern": pattern,
            "text_len": len(text),
        }
        self.last_compare_results = []
        self.last_corpus_results = []
        self.result_var.set(format_result_summary(algorithm, len(matches), elapsed_ms, len(pattern), len(text)))

    def _on_compare(self) -> None:
        if not self.text_content:
            messagebox.showwarning("Missing text", "Please upload a text file first.")
            return

        pattern = normalize_text(self.pattern_var.get())
        if not pattern:
            messagebox.showwarning(MISSING_PATTERN_TITLE, MISSING_PATTERN_MSG)
            return

        text, index_map = self._normalize_with_map(self.text_content)
        results: list[dict[str, float | int | str]] = []

        search_map = {
            "brute_force": brute_force_search,
            "kmp": kmp_search,
            "rabin_karp": rabin_karp_search,
            "boyer_moore": boyer_moore_search,
        }

        for name, search_fn in search_map.items():
            timer = Timer()
            timer.start()
            matches = search_fn(pattern, text)
            elapsed_ms = timer.stop()
            similarity = (len(matches) * len(pattern) / max(1, len(text))) * 100
            results.append(
                {
                    "algorithm": name,
                    "matches": len(matches),
                    "elapsed_ms": elapsed_ms,
                    "similarity": similarity,
                }
            )

        selected = self.algorithm_var.get()
        selected_row = next((r for r in results if r["algorithm"] == selected), None)
        if selected_row is not None:
            self._highlight_matches(search_map[selected](pattern, text), len(pattern), index_map=index_map)

        self.last_compare_results = results
        self.last_run_result = None
        self.last_corpus_results = []
        self.result_var.set(format_compare_summary(results))

    def _on_rank_corpus(self) -> None:
        if not self.corpus_files:
            messagebox.showwarning("Missing corpus", "Please select corpus files first.")
            return

        pattern = normalize_text(self.pattern_var.get())
        if not pattern:
            messagebox.showwarning(MISSING_PATTERN_TITLE, MISSING_PATTERN_MSG)
            return

        algorithm = self.algorithm_var.get()
        search_map = {
            "brute_force": brute_force_search,
            "kmp": kmp_search,
            "rabin_karp": rabin_karp_search,
            "boyer_moore": boyer_moore_search,
        }
        search_fn = search_map[algorithm]

        results: list[dict[str, float | int | str]] = []
        for corpus_path in self.corpus_files:
            try:
                text_raw = read_text_file(corpus_path)
                text, _ = self._normalize_with_map(text_raw)
            except Exception:
                continue

            timer = Timer()
            timer.start()
            matches = search_fn(pattern, text)
            elapsed_ms = timer.stop()
            similarity = (len(matches) * len(pattern) / max(1, len(text))) * 100
            similarity = min(100.0, similarity)

            results.append(
                {
                    "algorithm": algorithm,
                    "file_path": corpus_path,
                    "file_name": Path(corpus_path).name,
                    "matches": len(matches),
                    "elapsed_ms": elapsed_ms,
                    "similarity": similarity,
                }
            )

        if not results:
            messagebox.showwarning("No result", "Could not analyze selected corpus files.")
            return

        results.sort(key=lambda item: (-float(item["similarity"]), -int(item["matches"]), float(item["elapsed_ms"])))

        top = results[0]
        try:
            top_text_raw = read_text_file(str(top["file_path"]))
            top_text, top_index_map = self._normalize_with_map(top_text_raw)
            top_matches = search_fn(pattern, top_text)
            if self.text_widget:
                self.text_widget.delete("1.0", tk.END)
                self.text_widget.insert(tk.END, top_text_raw)
            self._highlight_matches(top_matches, len(pattern), index_map=top_index_map)
        except Exception:
            pass

        self.last_corpus_results = results
        self.last_compare_results = []
        self.last_run_result = None
        self.result_var.set(format_corpus_top_summary(results, top_n=5))

    def _on_export(self) -> None:
        if not self.last_run_result and not self.last_compare_results and not self.last_corpus_results:
            messagebox.showwarning("No result", "Please run analysis or compare algorithms first.")
            return

        file_path = filedialog.asksaveasfilename(
            title="Export result",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("JSON files", "*.json")],
        )
        if not file_path:
            return

        try:
            if file_path.lower().endswith(".json"):
                self._export_json(file_path)
            else:
                self._export_csv(file_path)
            self.result_var.set(f"Exported: {file_path}")
        except Exception as exc:
            messagebox.showerror("Export error", str(exc))

    def _export_csv(self, file_path: str) -> None:
        if self.last_corpus_results:
            rows = self.last_corpus_results
            fieldnames = ["algorithm", "file_name", "matches", "elapsed_ms", "similarity", "file_path"]
        elif self.last_compare_results:
            rows = self.last_compare_results
            fieldnames = ["algorithm", "matches", "elapsed_ms", "similarity"]
        else:
            rows = [self.last_run_result] if self.last_run_result else []
            fieldnames = ["algorithm", "matches", "elapsed_ms", "similarity"]

        with open(file_path, "w", newline="", encoding="utf-8") as output:
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                payload: dict[str, str | int | float] = {
                    "algorithm": str(row.get("algorithm", "")),
                    "matches": int(row.get("matches", 0)),
                    "elapsed_ms": f"{float(row.get('elapsed_ms', 0.0)):.3f}",
                    "similarity": f"{float(row.get('similarity', 0.0)):.2f}",
                }
                if "file_name" in fieldnames:
                    payload["file_name"] = str(row.get("file_name", ""))
                    payload["file_path"] = str(row.get("file_path", ""))
                writer.writerow(payload)

    def _export_json(self, file_path: str) -> None:
        payload: dict[str, object]
        if self.last_corpus_results:
            payload = {"mode": "corpus_ranking", "results": self.last_corpus_results}
        elif self.last_compare_results:
            payload = {"mode": "compare", "results": self.last_compare_results}
        else:
            payload = {"mode": "single", "result": self.last_run_result}

        with open(file_path, "w", encoding="utf-8") as output:
            json.dump(payload, output, ensure_ascii=False, indent=2)

    def _highlight_matches(self, matches: list[int], pattern_len: int, index_map: list[int] | None = None) -> None:
        if not self.text_widget:
            return
        self.text_widget.tag_remove("match", "1.0", tk.END)

        if pattern_len <= 0:
            return

        if index_map is None:
            for pos in matches:
                start = f"1.0+{pos}c"
                end = f"1.0+{pos + pattern_len}c"
                self.text_widget.tag_add("match", start, end)
            return

        for pos in matches:
            end_pos = pos + pattern_len - 1
            if pos < 0 or end_pos >= len(index_map):
                continue
            start_raw = index_map[pos]
            end_raw_exclusive = index_map[end_pos] + 1
            start = f"1.0+{start_raw}c"
            end = f"1.0+{end_raw_exclusive}c"
            self.text_widget.tag_add("match", start, end)

    # --- Benchmark Tab Methods ---
    def _on_select_benchmark_test(self) -> None:
        folder = filedialog.askdirectory(title="Select test_cases folder (contains exact, noise...)")
        if folder: self.benchmark_test_dir.set(folder)

    def _on_select_benchmark_corpus(self) -> None:
        folder = filedialog.askdirectory(title="Select corpus_grouped folder (contains small, medium...)")
        if folder: self.benchmark_corpus_dir.set(folder)

    def _log_benchmark(self, msg: str) -> None:
        if self.benchmark_log_widget:
            self.benchmark_log_widget.insert(tk.END, msg + "\n")
            self.benchmark_log_widget.see(tk.END)

    def _on_run_benchmark_thread(self) -> None:
        test_dir = self.benchmark_test_dir.get()
        corpus_dir = self.benchmark_corpus_dir.get()

        if not os.path.exists(test_dir) or not os.path.exists(corpus_dir):
            messagebox.showwarning("Missing Paths", "Please select both test_cases and corpus_grouped folders.")
            return

        # Start thread
        threading.Thread(target=self._run_benchmark_logic, args=(test_dir, corpus_dir), daemon=True).start()

    def _run_benchmark_logic(self, test_dir: str, corpus_dir: str) -> None:
        self.root.after(0, lambda: self.benchmark_status_var.set("Running benchmark... Please wait."))
        if self.benchmark_log_widget:
            self.root.after(0, lambda: self.benchmark_log_widget.delete("1.0", tk.END))
        self.benchmark_results = []

        self.root.after(0, lambda: self._log_benchmark(f"Starting batch benchmark...\nTest Dir: {test_dir}\nCorpus Dir: {corpus_dir}\n"))

        algorithms = {
            "BruteForce": brute_force_search,
            "KMP": kmp_search,
            "RabinKarp": rabin_karp_search,
            "BoyerMoore": boyer_moore_search,
        }

        def calc_similarity(pattern_len, match_count):
            if pattern_len == 0 or match_count == 0:
                return 0.0
            return 100.0

        def get_random_corpus():
            all_files = []
            for root, _, files in os.walk(corpus_dir):
                for f in files:
                    if f.endswith(".txt"):
                        all_files.append(os.path.join(root, f))
            return random.choice(all_files) if all_files else None

        test_files_paths = []
        try:
            for test_type in os.listdir(test_dir):
                type_path = os.path.join(test_dir, test_type)
                if not os.path.isdir(type_path): continue
                for f in os.listdir(type_path):
                    if f.endswith(".txt"):
                        test_files_paths.append((test_type, f, os.path.join(type_path, f)))
        except Exception as e:
            self.root.after(0, lambda err=e: messagebox.showerror("Directory Error", f"Failed to read test cases: {err}"))
            self.root.after(0, lambda: self.benchmark_status_var.set("Ready"))
            return

        total_files = len(test_files_paths)
        if total_files == 0:
            self.root.after(0, lambda: messagebox.showwarning("Empty", "No test cases (.txt) found in the selected folder."))
            self.root.after(0, lambda: self.benchmark_status_var.set("Ready"))
            return

        self.root.after(0, lambda: self.benchmark_progress.configure(maximum=total_files, value=0))

        for idx, (test_type, test_file, pattern_path) in enumerate(test_files_paths):
            try:
                pattern_raw = read_text_file(pattern_path)
                pattern = normalize_text(pattern_raw)

                target_files = []
                if "_from_" in test_file:
                    encoded = test_file.split("_from_")[1].replace(".txt", "")
                    parts = encoded.split("@")

                    if len(parts) >= 2:
                        corpus_category = parts[-2]
                        corpus_name = parts[-1] + ".txt"
                        corpus_path = os.path.join(corpus_dir, corpus_category, corpus_name)
                    else:
                        corpus_path = os.path.join(corpus_dir, parts[-1] + ".txt")

                    if os.path.exists(corpus_path):
                        target_files.append(corpus_path)
                    else:
                        self.root.after(0, lambda f=corpus_path: self._log_benchmark(f"[WARNING] Missing corpus: {f}"))
                else:
                    random_file = get_random_corpus()
                    if random_file:
                        target_files.append(random_file)

                for corpus_path in target_files:
                    text_raw = read_text_file(corpus_path)
                    text = normalize_text(text_raw)

                    corpus_filename = os.path.basename(corpus_path)
                    corpus_category = os.path.basename(os.path.dirname(corpus_path))

                    for algo_name, algo_func in algorithms.items():
                        start = time.perf_counter()
                        try:
                            matches = algo_func(pattern, text)
                        except Exception as e:
                            self.root.after(0, lambda a=algo_name, err=e: self._log_benchmark(f"[ERROR] {a}: {err}"))
                            matches = []
                        end = time.perf_counter()

                        exec_time = round(end - start, 6)
                        match_count = len(matches) if matches else 0
                        similarity = calc_similarity(len(pattern), match_count)

                        self.benchmark_results.append({
                            "Algorithm": algo_name,
                            "Test_Type": test_type,
                            "Corpus_Size": corpus_category,
                            "Test_File": test_file,
                            "Corpus_File": corpus_filename,
                            "Match_Count": match_count,
                            "Similarity": f"{similarity}%",
                            "Execution_Time(s)": exec_time
                        })

            except Exception as e:
                self.root.after(0, lambda err=e, tf=test_file: self._log_benchmark(f"[ERROR] Processing {tf}: {err}"))

            if idx % 5 == 0 or idx == total_files - 1:
                self.root.after(0, lambda current=idx+1: self.benchmark_progress.configure(value=current))

        self.root.after(0, lambda: self._log_benchmark(f"\n[DONE] Benchmark completed for {total_files} test files."))
        self.root.after(0, lambda: self.benchmark_status_var.set("Benchmark completed."))

    def _on_export_benchmark(self) -> None:
        if not getattr(self, "benchmark_results", None):
            messagebox.showwarning("No Data", "No benchmark data to export. Please run benchmark first.")
            return

        file_path = filedialog.asksaveasfilename(
            title="Export Benchmark Result", defaultextension=".csv", filetypes=[("CSV files", "*.csv")]
        )
        if not file_path:
            return

        try:
            with open(file_path, "w", newline="", encoding="utf-8") as output:
                fieldnames = ["Algorithm", "Test_Type", "Corpus_Size", "Test_File", "Corpus_File", "Match_Count", "Similarity", "Execution_Time(s)"]
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                for row in self.benchmark_results:
                    writer.writerow(row)
            messagebox.showinfo("Success", f"Exported benchmark to:\n{file_path}")
        except Exception as exc:
            messagebox.showerror("Export Error", str(exc))

    def run(self) -> None:
        self.setup_ui()
        self.root.mainloop()