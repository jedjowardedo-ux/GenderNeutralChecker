"""
Gender Neutral Language Checker
Automata and Language Theory machine problem (BSCS 3A)

Approach : regular expressions (Python `re` module)
Interface: Tkinter desktop window (run with no arguments)
           or command line (run with a .txt file path as the argument)

Each rule below is a regular expression describing ONE gender-specific term
(including its plural/variant forms). Every rule is wrapped as

        \\b(?:RULE)\\b          compiled with re.IGNORECASE

\\b  = word boundary, so "he or she" is never found inside a longer word.
IGNORECASE = "Foreman", "FOREMAN" and "foreman" are all recognized.
"""

import re
import sys
from collections import namedtuple
from pathlib import Path

NO_TERMS_MESSAGE = "No predefined gender-specific terms were detected."
EMPTY_FILE_MESSAGE = "The selected file is empty. Please choose a file that contains text."
SUPPORTED_EXTENSION = ".txt"

Rule = namedtuple("Rule", "label pattern suggestion")
Hit = namedtuple("Hit", "label suggestion spans")   # spans = [(start, end), ...]

# label (shown in the table) | regular expression | suggested alternative
RULES = [
    Rule("spokesman",           r"spokes(?:man|men)",        "spokesperson"),
    Rule("cameraman",           r"camera(?:man|men)",        "camera operator"),
    Rule("mailman",             r"mail(?:man|men)",          "mail carrier"),
    Rule("housewife",           r"house(?:wife|wives)",      "homemaker"),
    Rule("headmaster",          r"headmasters?",             "school head / principal"),
    Rule("foreman",             r"fore(?:man|men)",          "supervisor"),
    Rule("layman",              r"lay(?:man|men)",           "layperson"),
    Rule("freshman",            r"fresh(?:man|men)",         "first-year student"),
    Rule("congressman",         r"congress(?:man|men)",      "legislator / member of congress"),
    Rule("craftsman",           r"crafts(?:man|men)",        "artisan"),
    Rule("repairman",           r"repair(?:man|men)",        "repairer / technician"),
    Rule("middleman",           r"middle(?:man|men)",        "intermediary"),
    Rule("man-hours",           r"man[- ]hours?",            "work hours / person-hours"),
    Rule("ladies and gentlemen", r"ladies\s+and\s+gentlemen", "everyone / distinguished guests"),
    Rule("he or she",           r"he\s+or\s+she",            "they"),
    Rule("his or her",          r"his\s+or\s+her",           "their"),
]

# Compile once: \b(?:pattern)\b  +  case-insensitive
COMPILED = [(rule, re.compile(rf"\b(?:{rule.pattern})\b", re.IGNORECASE)) for rule in RULES]


class InputProblem(Exception):
    """Raised with a user-friendly message when a file cannot be analyzed."""


def scan(text):
    """Return a Hit for every rule that matches at least once in `text`."""
    hits = []
    for rule, regex in COMPILED:
        spans = [m.span() for m in regex.finditer(text)]
        if spans:
            hits.append(Hit(rule.label, rule.suggestion, spans))
    return hits


def load_text_file(path):
    """Validate and read a .txt file; raise InputProblem with a clear message."""
    path = Path(path)
    if path.suffix.lower() != SUPPORTED_EXTENSION:
        shown = path.suffix if path.suffix else "(no extension)"
        raise InputProblem(
            f"Unsupported file format: {shown}\nOnly {SUPPORTED_EXTENSION} files are supported."
        )
    try:
        text = path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        raise InputProblem("This file could not be read as UTF-8 text.")
    except OSError as err:
        raise InputProblem(f"The file could not be opened: {err}")
    if not text.strip():
        raise InputProblem(EMPTY_FILE_MESSAGE)
    return text


# ----------------------------------------------------------------- command line
def run_cli(path):
    try:
        text = load_text_file(path)
    except InputProblem as problem:
        print(problem)
        return 1
    hits = scan(text)
    if not hits:
        print(NO_TERMS_MESSAGE)
        return 0
    print(f"{'Detected term':<24}{'Occurrences':<13}Suggested alternative")
    print("-" * 70)
    for hit in hits:
        print(f"{hit.label:<24}{len(hit.spans):<13}{hit.suggestion}")
    return 0


# ---------------------------------------------------------------------- desktop
LINE_COLOR = "#7f7f7f"   # color of the table lines
HEADER_BG = "#e8e8e8"


class GridTable:
    """Results table with a visible line between every row and every column."""

    def __init__(self, parent, tk, ttk, headers, min_widths, weights, max_height=330):
        self.tk = tk
        self.ncols = len(headers)
        self.max_height = max_height
        self.next_row = 0
        self.cells = []

        self.frame = tk.Frame(parent)
        self.canvas = tk.Canvas(self.frame, bg=LINE_COLOR, highlightthickness=0, height=28)
        self.scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)

        # The inner frame's background is the line color; each cell is 1 px
        # smaller than its grid slot, so the background shows as a thin line.
        self.inner = tk.Frame(self.canvas, bg=LINE_COLOR)
        self.window = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        for col in range(self.ncols):
            self.inner.grid_columnconfigure(col, weight=weights[col], minsize=min_widths[col])
        self.inner.bind("<Configure>", self._update_size)
        self.canvas.bind("<Configure>", self._fit_width)
        self.canvas.bind("<Enter>", lambda e: self.canvas.bind_all("<MouseWheel>", self._wheel))
        self.canvas.bind("<Leave>", lambda e: self.canvas.unbind_all("<MouseWheel>"))

        self._add(headers, header=True)

    def pack(self, **options):
        self.frame.pack(**options)

    def _add(self, values, header=False):
        row = self.next_row
        self.next_row += 1
        last = self.ncols - 1
        created = []
        for col, value in enumerate(values):
            cell = self.tk.Label(
                self.inner, text=str(value), anchor="center",
                bg=HEADER_BG if header else "white",
                font=("Arial", 10, "bold" if header else "normal"),
            )
            cell.grid(row=row, column=col, sticky="nsew", ipady=4,
                      padx=(1, 1 if col == last else 0), pady=(1, 0))
            created.append(cell)
        return created

    def add_row(self, values):
        self.cells.extend(self._add(values))

    def clear(self):
        for cell in self.cells:
            cell.destroy()
        self.cells = []
        self.next_row = 1          # row 0 is the header
        self.canvas.yview_moveto(0)

    def _fit_width(self, event):
        self.canvas.itemconfigure(self.window, width=event.width)

    def _update_size(self, event=None):
        bbox = self.canvas.bbox("all")
        if not bbox:
            return
        height = bbox[3] + 1       # +1 px for the bottom line
        self.canvas.configure(scrollregion=(0, 0, bbox[2], height),
                              height=min(height, self.max_height))
        if height > self.max_height:
            self.scrollbar.pack(side="right", fill="y", before=self.canvas)
        else:
            self.scrollbar.pack_forget()

    def _wheel(self, event):
        self.canvas.yview_scroll(int(-event.delta / 120), "units")


class CheckerApp:
    def __init__(self, root, tk, ttk, filedialog, messagebox):
        self.tk, self.filedialog, self.messagebox = tk, filedialog, messagebox
        self.root = root
        root.title("Gender Neutral Language Checker")
        root.geometry("820x700")
        root.minsize(680, 480)

        top = ttk.Frame(root, padding=12)
        top.pack(fill="x")
        ttk.Label(top, text="Gender Neutral Language Checker",
                  font=("Arial", 16, "bold")).pack()
        bar = ttk.Frame(top)
        bar.pack(pady=(8, 0))          # no fill: the button and file name stay centered
        ttk.Button(bar, text="Upload .txt file", command=self.on_open).pack(side="left")
        self.file_label = ttk.Label(bar, text="  No file selected")
        self.file_label.pack(side="left")
        self.status = ttk.Label(top, text="Upload a text file to begin.",
                                justify="center", anchor="center", wraplength=760)
        self.status.pack(pady=(8, 0))

        self.table = GridTable(
            root, tk, ttk,
            headers=("Detected term", "Occurrences", "Suggested alternative"),
            min_widths=(250, 130, 320),
            weights=(25, 13, 32),
        )
        self.table.pack(fill="x", padx=12)

        ttk.Label(root, text="Document preview (detected terms highlighted):",
                  padding=(12, 10, 12, 2)).pack()
        prev = ttk.Frame(root, padding=(12, 0, 12, 12))
        prev.pack(fill="both", expand=True)
        self.preview = tk.Text(prev, wrap="word", state="disabled", height=10)
        self.preview.tag_configure("hit", background="#ffe58a")
        psb = ttk.Scrollbar(prev, orient="vertical", command=self.preview.yview)
        self.preview.configure(yscrollcommand=psb.set)
        self.preview.pack(side="left", fill="both", expand=True)
        psb.pack(side="right", fill="y")

    def _reset(self):
        self.table.clear()
        self.preview.config(state="normal")
        self.preview.delete("1.0", "end")
        self.preview.config(state="disabled")

    def on_open(self):
        chosen = self.filedialog.askopenfilename(
            title="Choose a text file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not chosen:
            return
        path = Path(chosen)
        self._reset()
        self.file_label.config(text=f"  File: {path.name}")
        try:
            text = load_text_file(path)
        except InputProblem as problem:
            self.status.config(text=str(problem).replace("\n", " "))
            self.messagebox.showwarning("Cannot analyze file", str(problem))
            return

        hits = scan(text)
        self.preview.config(state="normal")
        self.preview.insert("1.0", text)
        for hit in hits:
            for start, end in hit.spans:
                self.preview.tag_add("hit", f"1.0+{start}c", f"1.0+{end}c")
        self.preview.config(state="disabled")

        if not hits:
            self.status.config(text=NO_TERMS_MESSAGE)
            return
        for hit in hits:
            self.table.add_row((hit.label, len(hit.spans), hit.suggestion))
        total = sum(len(h.spans) for h in hits)
        self.status.config(
            text=f"{len(hits)} term(s) found, {total} occurrence(s) in total. "
                 "Suggestions are for review; choose wording that fits the context."
        )


def run_gui():
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
    root = tk.Tk()
    CheckerApp(root, tk, ttk, filedialog, messagebox)
    root.mainloop()


def main():
    if len(sys.argv) > 1:
        sys.exit(run_cli(sys.argv[1]))
    run_gui()


if __name__ == "__main__":
    main()