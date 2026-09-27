"""Load corpus markdown docs into Doc(metadata, body).

architecture.md §5 step 1. Reads corpus/*.md (except README.md), splits YAML
frontmatter from the markdown body, and validates required metadata keys.
"""
from __future__ import annotations

import glob
import os
from dataclasses import dataclass

import yaml

import config

REQUIRED_KEYS = ("doc_id", "scheme", "source_url", "nav_as_of")


@dataclass
class Doc:
    metadata: dict
    body: str


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Split leading YAML frontmatter (--- ... ---) from the markdown body."""
    text = text.lstrip("﻿")  # strip BOM if present
    if not text.startswith("---"):
        return {}, text
    lines = text.split("\n")
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return {}, text
    meta = yaml.safe_load("\n".join(lines[1:end])) or {}
    body = "\n".join(lines[end + 1:]).lstrip("\n")
    return meta, body


def load_corpus(corpus_dir: str = config.CORPUS_DIR) -> list[Doc]:
    """Return one Doc per scheme markdown file in corpus_dir (README excluded)."""
    docs: list[Doc] = []
    for path in sorted(glob.glob(os.path.join(corpus_dir, "*.md"))):
        name = os.path.basename(path)
        if name.lower() == "readme.md":
            continue
        with open(path, encoding="utf-8") as f:
            meta, body = parse_frontmatter(f.read())
        missing = [k for k in REQUIRED_KEYS if not meta.get(k)]
        if missing:
            raise ValueError(f"{name}: missing frontmatter keys: {missing}")
        docs.append(Doc(metadata=meta, body=body))
    if not docs:
        raise FileNotFoundError(f"No corpus .md files found in {corpus_dir!r}")
    return docs
