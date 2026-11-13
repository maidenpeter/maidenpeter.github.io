"""Fail if any text file holds a non-ASCII character or a phrase that reads as machine-written.

    python tools/check_text.py

Covers every text file in the repo (HTML, CSS, JS, Python, Markdown, JSON, XML, SVG, YAML, TXT).
Plain ASCII punctuation only: no em or en dashes, curly quotes, arrows, middle dots or ellipsis characters.
"""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEXT = {".html", ".css", ".js", ".py", ".md", ".json", ".xml", ".svg", ".yml", ".yaml", ".txt", ".gitignore", ""}
SKIP_DIRS = {".git", "__pycache__", "node_modules"}
# Phrases that make writing sound generated. Whole words, case-insensitive.
BANNED = [
    "delve", "leverage", "leveraging", "seamless", "seamlessly", "robust", "not just", "not only", "in today's",
    "fast-paced", "cutting-edge", "game-changer", "game changer", "unlock", "unleash", "empower", "elevate",
    "tapestry", "testament to", "dive into", "deep dive", "harness", "synergy", "holistic", "streamline",
    "revolutionize", "revolutionise", "best-in-class", "world-class", "state-of-the-art", "furthermore", "moreover",
    "in conclusion", "worth noting", "it is important to note", "navigate the", "ever-evolving", "embark",
    "realm", "showcase", "meticulous", "pivotal", "paramount", "supercharge", "next-level", "journey",
]
PATTERN = re.compile(r"\b(" + "|".join(re.escape(b) for b in BANNED) + r")\b", re.I)
SELF = Path(__file__).resolve()


def files():
    for p in ROOT.rglob("*"):
        if p.is_file() and not (set(p.relative_to(ROOT).parts) & SKIP_DIRS) and p.suffix.lower() in TEXT:
            if p.name == "local_paths.json":
                continue  # untracked, holds local file paths only
            yield p


def main():
    problems = []
    count = 0
    for p in files():
        count += 1
        raw = p.read_bytes()
        rel = p.relative_to(ROOT).as_posix()
        for i, line in enumerate(raw.split(b"\n"), 1):
            bad = [b for b in line if b > 127]
            if bad:
                text = line.decode("utf-8", "replace")
                chars = sorted({c for c in text if ord(c) > 127})
                problems.append(f"{rel}:{i}: non-ASCII {', '.join('U+%04X' % ord(c) for c in chars)}")
            if p.resolve() != SELF:
                for m in PATTERN.finditer(line.decode("ascii", "replace")):
                    problems.append(f"{rel}:{i}: phrase '{m.group(0)}'")
    print(f"{count} text files checked.")
    if problems:
        print(f"{len(problems)} problems:")
        for x in problems:
            print("  " + x)
        sys.exit(1)
    print("All plain ASCII, no flagged phrases.")


if __name__ == "__main__":
    main()
