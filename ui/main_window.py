from __future__ import annotations

import csv
import json
import os
import random
import re
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

        self.algorithm_var = tk.StringVar(value="kmp")
        self.result_var = tk.StringVar(value="No analysis yet")
        self.last_run_result: dict[str, float | int | str] | None = None
        self.last_compare_results: list[dict[str, float | int | str]] = []
        self.last_corpus_results: list[dict[str, float | int | str]] = []
        self.corpus_folder: str | None = None
        
        self.mode_var = tk.StringVar(value="Auto Plagiarism (Chunking)")
        self.pattern_var = tk.StringVar(value="")
        self.corpus_view_var = tk.StringVar(value="")
        self.corpus_combobox: ttk.Combobox | None = None
        
        self.suspect_text_widget: tk.Text | None = None
        self.corpus_text_widget: tk.Text | None = None

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
        if hasattr(self, 'corpus_combobox') and self.corpus_combobox:
            self.corpus_combobox['values'] = self.corpus_files
            if self.corpus_files and not self.corpus_view_var.get():
                self.corpus_combobox.current(0)
                self._on_corpus_view_select()
                
        self.result_var.set(
            "Corpus selected | "
            f"manual: {len(self.manual_corpus_files)} | "
            f"folder: {len(self.folder_corpus_files)} | "
            f"total unique: {len(self.corpus_files)}"
        )

    def _on_corpus_view_select(self, event=None) -> None:
        selected_file = self.corpus_view_var.get()
        if not selected_file: return
        try:
            content = read_text_file(selected_file)
            if self.corpus_text_widget:
                self.corpus_text_widget.delete("1.0", tk.END)
                self.corpus_text_widget.insert(tk.END, content)
                self.corpus_text_widget.tag_remove("match", "1.0", tk.END)
        except Exception as e:
            messagebox.showerror("Error", f"Could not read corpus file: {e}")

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

    def _chunk_text(self, text: str, chunk_size: int = 10) -> list[tuple[str, int, int]]:
        chunks = []
        # Tách văn bản thành các từ, gom thành cụm (chunk_size từ / block)
        words = list(re.finditer(r'\S+', text))
        for i in range(0, len(words), chunk_size):
            chunk_words = words[i:i + chunk_size]
            start_idx = chunk_words[0].start()
            end_idx = chunk_words[-1].end()
            chunks.append((text[start_idx:end_idx], start_idx, end_idx))
        return chunks

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

        ttk.Button(top, text="Upload Suspect Document", command=self._on_upload).pack(side=tk.LEFT)
        ttk.Button(top, text="Select Corpus Files", command=self._on_select_corpus).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(top, text="Select Corpus Folder", command=self._on_select_corpus_folder).pack(side=tk.LEFT, padx=(8, 0))

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

        # --- New Control Bar ---
        control_bar = ttk.Frame(self.tab_interactive, padding=10)
        control_bar.pack(fill=tk.X)

        ttk.Label(control_bar, text="Mode:").pack(side=tk.LEFT)
        mode_box = ttk.Combobox(
            control_bar,
            textvariable=self.mode_var,
            values=["Pattern Match (Manual)", "Auto Plagiarism (Chunking)"],
            width=25,
            state="readonly"
        )
        mode_box.pack(side=tk.LEFT, padx=(5, 15))
        
        ttk.Label(control_bar, text="Pattern:").pack(side=tk.LEFT)
        ttk.Entry(control_bar, textvariable=self.pattern_var, width=30).pack(side=tk.LEFT, padx=(5, 15))

        ttk.Label(control_bar, text="View Corpus:").pack(side=tk.LEFT)
        self.corpus_combobox = ttk.Combobox(
            control_bar,
            textvariable=self.corpus_view_var,
            values=[],
            width=40,
            state="readonly"
        )
        self.corpus_combobox.pack(side=tk.LEFT, padx=(5, 0))
        self.corpus_combobox.bind("<<ComboboxSelected>>", self._on_corpus_view_select)
        # -----------------------

        paned_window = ttk.PanedWindow(self.tab_interactive, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left Frame: Suspect Document
        suspect_frame = ttk.LabelFrame(paned_window, text="Suspect Document")
        paned_window.add(suspect_frame, weight=1)

        y_scroll_susp = ttk.Scrollbar(suspect_frame, orient=tk.VERTICAL)
        x_scroll_susp = ttk.Scrollbar(suspect_frame, orient=tk.HORIZONTAL)

        self.suspect_text_widget = tk.Text(
            suspect_frame,
            wrap=tk.NONE,
            font=("Consolas", 11),
            yscrollcommand=y_scroll_susp.set,
            xscrollcommand=x_scroll_susp.set,
        )
        y_scroll_susp.config(command=self.suspect_text_widget.yview)
        x_scroll_susp.config(command=self.suspect_text_widget.xview)

        self.suspect_text_widget.grid(row=0, column=0, sticky="nsew")
        y_scroll_susp.grid(row=0, column=1, sticky="ns")
        x_scroll_susp.grid(row=1, column=0, sticky="ew")
        suspect_frame.rowconfigure(0, weight=1)
        suspect_frame.columnconfigure(0, weight=1)

        self.suspect_text_widget.tag_config("match", background="#FFE08A")

        # Right Frame: Corpus Document
        corpus_frame = ttk.LabelFrame(paned_window, text="Corpus Document")
        paned_window.add(corpus_frame, weight=1)

        y_scroll_corp = ttk.Scrollbar(corpus_frame, orient=tk.VERTICAL)
        x_scroll_corp = ttk.Scrollbar(corpus_frame, orient=tk.HORIZONTAL)

        self.corpus_text_widget = tk.Text(
            corpus_frame,
            wrap=tk.NONE,
            font=("Consolas", 11),
            yscrollcommand=y_scroll_corp.set,
            xscrollcommand=x_scroll_corp.set,
        )
        y_scroll_corp.config(command=self.corpus_text_widget.yview)
        x_scroll_corp.config(command=self.corpus_text_widget.xview)

        self.corpus_text_widget.grid(row=0, column=0, sticky="nsew")
        y_scroll_corp.grid(row=0, column=1, sticky="ns")
        x_scroll_corp.grid(row=1, column=0, sticky="ew")
        corpus_frame.rowconfigure(0, weight=1)
        corpus_frame.columnconfigure(0, weight=1)

        self.corpus_text_widget.tag_config("match", background="#FFE08A")

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
            title="Select suspect document",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not file_path:
            return

        try:
            self.text_content = read_text_file(file_path)
            if self.suspect_text_widget:
                self.suspect_text_widget.delete("1.0", tk.END)
                self.suspect_text_widget.insert(tk.END, self.text_content)
                self.suspect_text_widget.tag_remove("match", "1.0", tk.END)
            if self.corpus_text_widget:
                self.corpus_text_widget.delete("1.0", tk.END)
                self.corpus_text_widget.tag_remove("match", "1.0", tk.END)
                
            # Triger read corpus view selected if any
            if self.corpus_view_var.get():
                self._on_corpus_view_select()
                
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
            messagebox.showwarning("Missing document", "Please upload a suspect document first.")
            return

        mode = self.mode_var.get()
        algorithm = self.algorithm_var.get()

        if mode == "Pattern Match (Manual)":
            pattern = self.pattern_var.get().strip()
            if not pattern:
                messagebox.showwarning("Missing pattern", "Please enter a pattern to search.")
                return
            
            selected_corpus = self.corpus_view_var.get()
            if not selected_corpus:
                messagebox.showwarning("Missing corpus", "Please select a corpus file to compare against.")
                return
                
            self.result_var.set("Running Pattern Match... Please wait.")
            threading.Thread(target=self._run_pattern_match_thread, args=(algorithm, pattern, selected_corpus), daemon=True).start()
            
        else: # Auto Plagiarism (Chunking)
            if not self.corpus_files:
                messagebox.showwarning("Missing corpus", "Please select corpus files or folder first.")
                return

            chunks = self._chunk_text(self.text_content, chunk_size=10)
            if not chunks:
                messagebox.showinfo("Analysis", "No valid text found to chunk in suspect document.")
                return

            selected_corpus = self.corpus_view_var.get()
            if not selected_corpus:
                messagebox.showwarning("Missing corpus", "Please select a corpus file to compare against.")
                return

            self.result_var.set("Running Auto Plagiarism (Chunking)... Please wait.")
            threading.Thread(target=self._run_auto_chunking_thread, args=(algorithm, chunks, selected_corpus), daemon=True).start()

    def _run_pattern_match_thread(self, algorithm: str, pattern_raw: str, corpus_path: str) -> None:
        search_map = {
            "brute_force": brute_force_search,
            "kmp": kmp_search,
            "rabin_karp": rabin_karp_search,
            "boyer_moore": boyer_moore_search,
        }
        search_fn = search_map[algorithm]
        
        timer = Timer()
        timer.start()

        # 1. Search in Suspect
        susp_norm, susp_map = self._normalize_with_map(self.text_content)
        pattern_norm = normalize_text(pattern_raw)
        
        susp_matches = []
        if pattern_norm:
            m_susp = search_fn(pattern_norm, susp_norm)
            if m_susp:
                for m_idx in m_susp:
                    m_len = len(pattern_norm)
                    if m_idx + m_len - 1 < len(susp_map):
                        start_raw = susp_map[m_idx]
                        end_raw = susp_map[m_idx + m_len - 1] + 1
                        susp_matches.append((start_raw, end_raw))

        # 2. Search in Corpus
        corp_matches = []
        try:
            c_text = read_text_file(corpus_path)
            c_norm, c_map = self._normalize_with_map(c_text)
            if pattern_norm:
                m_corp = search_fn(pattern_norm, c_norm)
                if m_corp:
                    for m_idx in m_corp:
                        m_len = len(pattern_norm)
                        if m_idx + m_len - 1 < len(c_map):
                            start_raw = c_map[m_idx]
                            end_raw = c_map[m_idx + m_len - 1] + 1
                            corp_matches.append((start_raw, end_raw))
        except Exception:
            pass
            
        elapsed_ms = timer.stop()

        def update_ui() -> None:
            self._highlight_intervals(susp_matches, self.suspect_text_widget)
            self._highlight_intervals(corp_matches, self.corpus_text_widget)
            self.result_var.set(f"Pattern Match | Found {len(susp_matches)} in Suspect, {len(corp_matches)} in Corpus | Time: {elapsed_ms:.2f}ms")
            
            self.last_run_result = {
                "algorithm": algorithm,
                "matches": len(susp_matches) + len(corp_matches),
                "elapsed_ms": elapsed_ms,
                "similarity": 0.0,
                "pattern": pattern_raw,
                "text_len": len(self.text_content),
            }
            self.last_compare_results = []
            self.last_corpus_results = []
            
        self.root.after(0, update_ui)

    def _run_auto_chunking_thread(self, algorithm: str, chunks: list[tuple[str, int, int]], corpus_path: str) -> None:
        search_map = {
            "brute_force": brute_force_search,
            "kmp": kmp_search,
            "rabin_karp": rabin_karp_search,
            "boyer_moore": boyer_moore_search,
        }
        search_fn = search_map[algorithm]
        
        try:
            c_text = read_text_file(corpus_path)
            c_norm, c_map = self._normalize_with_map(c_text)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showwarning("Corpus Error", f"Could not read corpus file: {e}"))
            return
            
        timer = Timer()
        timer.start()

        susp_matched_intervals = []
        corp_matched_intervals = []
        total_matches = 0

        for chunk, start_raw, end_raw in chunks:
            norm_chunk = normalize_text(chunk)
            if not norm_chunk: continue
            
            matches = search_fn(norm_chunk, c_norm)
            if matches:
                susp_matched_intervals.append((start_raw, end_raw))
                total_matches += len(matches)
                for m_idx in matches:
                    m_len = len(norm_chunk)
                    if m_idx + m_len - 1 < len(c_map):
                        c_start = c_map[m_idx]
                        c_end = c_map[m_idx + m_len - 1] + 1
                        corp_matched_intervals.append((c_start, c_end))

        elapsed_ms = timer.stop()
        
        unique_susp_intervals = sorted(list(set(susp_matched_intervals)))
        matched_chars = sum(end - start for start, end in unique_susp_intervals)
        total_chars = max(1, len(self.text_content))
        similarity = (matched_chars / total_chars) * 100
        
        def update_ui() -> None:
            self._highlight_intervals(unique_susp_intervals, self.suspect_text_widget)
            self._highlight_intervals(corp_matched_intervals, self.corpus_text_widget)
            self.result_var.set(f"Auto Plagiarism | Similarity with {Path(corpus_path).name}: {similarity:.2f}% | Time: {elapsed_ms:.2f}ms")
            
            self.last_run_result = {
                "algorithm": algorithm,
                "matches": total_matches,
                "elapsed_ms": elapsed_ms,
                "similarity": similarity,
                "pattern": f"Chunked ({len(chunks)} chunks)",
                "text_len": total_chars,
            }
            self.last_compare_results = []
            self.last_corpus_results = []
            
        self.root.after(0, update_ui)

    def _on_compare(self) -> None:
        if not self.corpus_files:
            messagebox.showwarning("Missing corpus", "Please select corpus files or folder first.")
            return

        mode = self.mode_var.get()
        
        if mode == "Pattern Match (Manual)":
            pattern = self.pattern_var.get().strip()
            if not pattern:
                messagebox.showwarning("Missing pattern", "Please enter a pattern to compare.")
                return
            self.result_var.set("Comparing algorithms (Pattern)... Please wait.")
            threading.Thread(target=self._compare_pattern_thread, args=(pattern,), daemon=True).start()
        else:
            if not self.text_content:
                messagebox.showwarning("Missing document", "Please upload a suspect document first.")
                return
            chunks = self._chunk_text(self.text_content, chunk_size=10)
            if not chunks:
                messagebox.showinfo("Analysis", "No valid text found to chunk in suspect document.")
                return
            self.result_var.set("Comparing algorithms (Chunking)... Please wait.")
            threading.Thread(target=self._compare_chunking_thread, args=(chunks,), daemon=True).start()

    def _compare_pattern_thread(self, pattern_raw: str) -> None:
        corpus_data = []
        for corpus_path in self.corpus_files:
            try:
                c_text = read_text_file(corpus_path)
                c_norm, _ = self._normalize_with_map(c_text)
                corpus_data.append((corpus_path, c_norm))
            except Exception:
                continue

        if not corpus_data:
            self.root.after(0, lambda: messagebox.showwarning("Corpus Error", "Could not read any corpus files."))
            self.root.after(0, lambda: self.result_var.set("Comparison failed."))
            return

        pattern_norm = normalize_text(pattern_raw)
        if not pattern_norm:
            self.root.after(0, lambda: messagebox.showwarning("Invalid Pattern", "Pattern is empty after normalization."))
            self.root.after(0, lambda: self.result_var.set("Comparison failed."))
            return

        results: list[dict[str, float | int | str]] = []
        search_map = {
            "brute_force": brute_force_search,
            "kmp": kmp_search,
            "rabin_karp": rabin_karp_search,
            "boyer_moore": boyer_moore_search,
        }

        all_algo_intervals = {}
        
        susp_norm, susp_map = None, None
        if self.text_content:
            susp_norm, susp_map = self._normalize_with_map(self.text_content)

        for name, search_fn in search_map.items():
            timer = Timer()
            timer.start()

            total_matches = 0
            for _, c_norm in corpus_data:
                matches = search_fn(pattern_norm, c_norm)
                if matches:
                    total_matches += len(matches)

            elapsed_ms = timer.stop()

            unique_intervals = []
            if susp_norm and susp_map:
                susp_matches = search_fn(pattern_norm, susp_norm)
                if susp_matches:
                    for m_idx in susp_matches:
                        m_len = len(pattern_norm)
                        if m_idx + m_len - 1 < len(susp_map):
                            start_raw = susp_map[m_idx]
                            end_raw = susp_map[m_idx + m_len - 1] + 1
                            unique_intervals.append((start_raw, end_raw))
            all_algo_intervals[name] = unique_intervals

            similarity = 100.0 if total_matches > 0 else 0.0

            results.append(
                {
                    "algorithm": name,
                    "matches": total_matches,
                    "elapsed_ms": elapsed_ms,
                    "similarity": similarity,
                }
            )

        def update_ui() -> None:
            selected_algo = self.algorithm_var.get()
            if selected_algo in all_algo_intervals and self.suspect_text_widget:
                self._highlight_intervals(all_algo_intervals[selected_algo], self.suspect_text_widget)

            self.last_compare_results = results
            self.last_run_result = None
            self.last_corpus_results = []
            self.result_var.set(format_compare_summary(results))

        self.root.after(0, update_ui)

    def _compare_chunking_thread(self, chunks: list[tuple[str, int, int]]) -> None:
        corpus_data = []
        for corpus_path in self.corpus_files:
            try:
                c_text = read_text_file(corpus_path)
                c_norm, _ = self._normalize_with_map(c_text)
                corpus_data.append((corpus_path, c_norm))
            except Exception:
                continue

        if not corpus_data:
            self.root.after(0, lambda: messagebox.showwarning("Corpus Error", "Could not read any corpus files."))
            self.root.after(0, lambda: self.result_var.set("Comparison failed."))
            return

        results: list[dict[str, float | int | str]] = []
        all_algo_intervals = {}

        search_map = {
            "brute_force": brute_force_search,
            "kmp": kmp_search,
            "rabin_karp": rabin_karp_search,
            "boyer_moore": boyer_moore_search,
        }

        for name, search_fn in search_map.items():
            timer = Timer()
            timer.start()

            matched_intervals = []
            total_matches = 0

            for chunk, start_raw, end_raw in chunks:
                norm_chunk = normalize_text(chunk)
                if not norm_chunk: continue

                chunk_matched = False
                for _, c_norm in corpus_data:
                    matches = search_fn(norm_chunk, c_norm)
                    if matches:
                        chunk_matched = True
                        total_matches += len(matches)

                if chunk_matched:
                    matched_intervals.append((start_raw, end_raw))

            elapsed_ms = timer.stop()

            unique_intervals = sorted(list(set(matched_intervals)))
            matched_chars = sum(end - start for start, end in unique_intervals)
            similarity = (matched_chars / max(1, len(self.text_content))) * 100

            all_algo_intervals[name] = unique_intervals

            results.append(
                {
                    "algorithm": name,
                    "matches": total_matches,
                    "elapsed_ms": elapsed_ms,
                    "similarity": similarity,
                }
            )

        def update_ui() -> None:
            selected_algo = self.algorithm_var.get()
            if selected_algo in all_algo_intervals:
                self._highlight_intervals(all_algo_intervals[selected_algo], self.suspect_text_widget)

            self.last_compare_results = results
            self.last_run_result = None
            self.last_corpus_results = []
            self.result_var.set(format_compare_summary(results))

        self.root.after(0, update_ui)

    def _on_rank_corpus(self) -> None:
        if not self.corpus_files:
            messagebox.showwarning("Missing corpus", "Please select corpus files first.")
            return

        mode = self.mode_var.get()
        algorithm = self.algorithm_var.get()

        if mode == "Pattern Match (Manual)":
            pattern = self.pattern_var.get().strip()
            if not pattern:
                messagebox.showwarning("Missing pattern", "Please enter a pattern to search.")
                return
            self.result_var.set("Ranking corpus (Pattern)... Please wait.")
            threading.Thread(target=self._rank_corpus_pattern_thread, args=(algorithm, pattern), daemon=True).start()
        else:
            if not self.text_content:
                messagebox.showwarning("Missing document", "Please upload a suspect document first.")
                return
            chunks = self._chunk_text(self.text_content, chunk_size=10)
            if not chunks:
                messagebox.showinfo("Analysis", "No valid text found to chunk in suspect document.")
                return
            self.result_var.set("Ranking corpus (Chunking)... Please wait.")
            threading.Thread(target=self._rank_corpus_chunking_thread, args=(algorithm, chunks), daemon=True).start()

    def _rank_corpus_pattern_thread(self, algorithm: str, pattern_raw: str) -> None:
        search_map = {
            "brute_force": brute_force_search,
            "kmp": kmp_search,
            "rabin_karp": rabin_karp_search,
            "boyer_moore": boyer_moore_search,
        }
        search_fn = search_map[algorithm]
        pattern_norm = normalize_text(pattern_raw)

        if not pattern_norm:
            self.root.after(0, lambda: messagebox.showwarning("Invalid Pattern", "Pattern is empty after normalization."))
            self.root.after(0, lambda: self.result_var.set("Ranking failed."))
            return

        results: list[dict[str, float | int | str]] = []
        for corpus_path in self.corpus_files:
            try:
                text_raw = read_text_file(corpus_path)
                c_norm, _ = self._normalize_with_map(text_raw)
            except Exception:
                continue

            timer = Timer()
            timer.start()
            
            matches = search_fn(pattern_norm, c_norm)
            total_matches_for_corpus = len(matches) if matches else 0

            elapsed_ms = timer.stop()

            # For pattern matching, similarity could just be proportional to matches, or 100% if > 0.
            # We calculate a ratio per 1000 characters as a pseudo similarity, but capped at 100.
            ratio = (total_matches_for_corpus * len(pattern_norm) / max(1, len(c_norm))) * 100
            similarity = min(100.0, ratio)

            results.append(
                {
                    "algorithm": algorithm,
                    "file_path": corpus_path,
                    "file_name": Path(corpus_path).name,
                    "matches": total_matches_for_corpus,
                    "elapsed_ms": elapsed_ms,
                    "similarity": similarity,
                }
            )

        def update_ui() -> None:
            if not results:
                messagebox.showwarning("No result", "Could not analyze selected corpus files.")
                self.result_var.set("Ranking failed.")
                return

            results.sort(key=lambda item: (-int(item["matches"]), float(item["elapsed_ms"])))

            if results:
                top = results[0]
                try:
                    top_c_text = read_text_file(str(top["file_path"]))
                    top_c_norm, top_c_map = self._normalize_with_map(top_c_text)
                    
                    if self.corpus_text_widget:
                        self.corpus_text_widget.delete("1.0", tk.END)
                        self.corpus_text_widget.insert(tk.END, top_c_text)
                        
                        if self.corpus_combobox and str(top["file_path"]) in self.corpus_combobox['values']:
                            self.corpus_view_var.set(str(top["file_path"]))

                    corpus_matched_intervals = []
                    matches = search_fn(pattern_norm, top_c_norm)
                    if matches:
                        for m_idx in matches:
                            m_len = len(pattern_norm)
                            if m_idx + m_len - 1 < len(top_c_map):
                                c_start = top_c_map[m_idx]
                                c_end = top_c_map[m_idx + m_len - 1] + 1
                                corpus_matched_intervals.append((c_start, c_end))

                    self._highlight_intervals(corpus_matched_intervals, self.corpus_text_widget)
                    
                    if self.text_content:
                        susp_norm, susp_map = self._normalize_with_map(self.text_content)
                        susp_matches = search_fn(pattern_norm, susp_norm)
                        susp_intervals = []
                        if susp_matches:
                            for m_idx in susp_matches:
                                m_len = len(pattern_norm)
                                if m_idx + m_len - 1 < len(susp_map):
                                    start_raw = susp_map[m_idx]
                                    end_raw = susp_map[m_idx + m_len - 1] + 1
                                    susp_intervals.append((start_raw, end_raw))
                        self._highlight_intervals(susp_intervals, self.suspect_text_widget)

                except Exception:
                    pass

            self.last_corpus_results = results
            self.last_compare_results = []
            self.last_run_result = None
            self.result_var.set(format_corpus_top_summary(results, top_n=5))

        self.root.after(0, update_ui)

    def _rank_corpus_chunking_thread(self, algorithm: str, chunks: list[tuple[str, int, int]]) -> None:
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
                c_norm, _ = self._normalize_with_map(text_raw)
            except Exception:
                continue

            timer = Timer()
            timer.start()
            
            matched_intervals_for_corpus = []
            total_matches_for_corpus = 0

            for chunk, start_raw, end_raw in chunks:
                norm_chunk = normalize_text(chunk)
                if not norm_chunk: continue
                
                matches = search_fn(norm_chunk, c_norm)
                if matches:
                    matched_intervals_for_corpus.append((start_raw, end_raw))
                    total_matches_for_corpus += len(matches)

            elapsed_ms = timer.stop()

            unique_intervals = sorted(list(set(matched_intervals_for_corpus)))
            matched_chars = sum(end - start for start, end in unique_intervals)
            similarity = (matched_chars / max(1, len(self.text_content))) * 100

            similarity = min(100.0, similarity)

            results.append(
                {
                    "algorithm": algorithm,
                    "file_path": corpus_path,
                    "file_name": Path(corpus_path).name,
                    "matches": total_matches_for_corpus,
                    "elapsed_ms": elapsed_ms,
                    "similarity": similarity,
                }
            )

        def update_ui() -> None:
            if not results:
                messagebox.showwarning("No result", "Could not analyze selected corpus files.")
                self.result_var.set("Ranking failed.")
                return

            results.sort(key=lambda item: (-float(item["similarity"]), -int(item["matches"]), float(item["elapsed_ms"])))

            if results:
                top = results[0]
                try:
                    top_c_text = read_text_file(str(top["file_path"]))
                    top_c_norm, top_c_map = self._normalize_with_map(top_c_text)
                    
                    if self.corpus_text_widget:
                        self.corpus_text_widget.delete("1.0", tk.END)
                        self.corpus_text_widget.insert(tk.END, top_c_text)
                        
                        if self.corpus_combobox and str(top["file_path"]) in self.corpus_combobox['values']:
                            self.corpus_view_var.set(str(top["file_path"]))

                    top_matched_intervals = []
                    corpus_matched_intervals = []
                    for chunk, start_raw, end_raw in chunks:
                        norm_chunk = normalize_text(chunk)
                        if not norm_chunk: continue
                        
                        matches = search_fn(norm_chunk, top_c_norm)
                        if matches:
                            top_matched_intervals.append((start_raw, end_raw))
                            for m_idx in matches:
                                m_len = len(norm_chunk)
                                if m_idx + m_len - 1 < len(top_c_map):
                                    c_start = top_c_map[m_idx]
                                    c_end = top_c_map[m_idx + m_len - 1] + 1
                                    corpus_matched_intervals.append((c_start, c_end))

                    self._highlight_intervals(top_matched_intervals, self.suspect_text_widget)
                    self._highlight_intervals(corpus_matched_intervals, self.corpus_text_widget)
                except Exception:
                    pass

            self.last_corpus_results = results
            self.last_compare_results = []
            self.last_run_result = None
            self.result_var.set(format_corpus_top_summary(results, top_n=5))

        self.root.after(0, update_ui)

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

    def _highlight_intervals(self, intervals: list[tuple[int, int]], widget: tk.Text | None = None) -> None:
        target_widget = widget if widget else self.suspect_text_widget
        if not target_widget:
            return
        target_widget.tag_remove("match", "1.0", tk.END)
        for start_raw, end_raw in intervals:
            start_idx = f"1.0+{start_raw}c"
            end_idx = f"1.0+{end_raw}c"
            target_widget.tag_add("match", start_idx, end_idx)

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