"""Download and load the candidate datasets for decision D-004."""
from __future__ import annotations

import hashlib
import json
import zipfile
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
from huggingface_hub import HfApi, hf_hub_download

# Paths are resolved from this file, so they work no matter where you run the code from
ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
INTERIM = ROOT / "data" / "interim"
MANIFEST = ROOT / "data" / "MANIFEST.json"

def _check(condition: bool, message: str) -> None:
    """Fail loudly instead of returning bad data."""
    if not condition:
        raise ValueError(message)

def sha256_of(path: Path) -> str:
    """Content fingerprint of a file: changes if a single byte changes."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)

    return h.hexdigest()

def _update_manifest(key: str, entry: dict, manifest_path: Path = MANIFEST) -> None:
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    manifest[key] = entry
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")

def _download_pinned(repo_id: str, filename: str, revision: str | None, dest: Path) -> Path:
    """Download one file from Hugging Face dataset repo at a fixed commit."""
    if revision is None:
        revision = HfApi().dataset_info(repo_id=repo_id).sha
        print(f"revision is empty, current commit {revision}. Pin it.")
    path = Path(hf_hub_download(
        repo_id=repo_id,
        repo_type="dataset",
        filename=filename,
        revision=revision,
        local_dir=dest,
    ))
    _update_manifest(f"{repo_id}/{filename}", {
        "revision": revision, 
        "sha256": sha256_of(path), 
        "downloaded_at": datetime.now(UTC).isoformat(timespec="seconds")
    })
    return path

PHRASEBANK_REPO = "takala/financial_phrasebank"
PHRASEBANK_ZIP = "data/FinancialPhraseBank-v1.0.zip"
PHRASEBANK_REVISION = "8d3fe0c36d5feec6b3cc5e455b0fcb4820fb9964"

def download_phrasebank() -> Path:
    return _download_pinned(PHRASEBANK_REPO, PHRASEBANK_ZIP, PHRASEBANK_REVISION, RAW / "phrasebank")

TWITTER_REPO = "zeroshot/twitter-financial-news-sentiment"
TWITTER_FILES = ["sent_train.csv", "sent_valid.csv"]
TWITTER_REVISION = "ccbe24de388e287beb92dd393a335c376b350ac3"

def download_twitter() -> dict:
    return {file: _download_pinned(TWITTER_REPO, file, TWITTER_REVISION, RAW / "twitter") for file in TWITTER_FILES}

# Files Sentences_*.txt don't have bytes between 0x80 and 0x9F, meaning latin-1 
# and cp1252 give identical text here. This is because that is the only range 
# in which both encodings differ.
PHRASEBANK_LABELS = {"negative", "neutral", "positive"}
PHRASEBANK_ENCODING = "latin-1"
PHRASEBANK_FILES = {
    100: "FinancialPhraseBank-v1.0/Sentences_AllAgree.txt",
    75: "FinancialPhraseBank-v1.0/Sentences_75Agree.txt",
    66: "FinancialPhraseBank-v1.0/Sentences_66Agree.txt",
    50: "FinancialPhraseBank-v1.0/Sentences_50Agree.txt",
}
PHRASEBANK_ROWS = {100: 2264, 75: 3453, 66: 4217, 50: 4846}

def load_phrasebank(zip_path: Path, expected_rows: dict[int, int] = PHRASEBANK_ROWS) -> pd.DataFrame:
    """Parse the four agreement files straight from the zip, keeping original order."""
    frames = []
    with zipfile.ZipFile(zip_path) as zf:
        for agreement, member in PHRASEBANK_FILES.items():
            text = zf.read(member).decode(PHRASEBANK_ENCODING)
            rows = []
            for i, line in enumerate(text.splitlines()):
                if not line.strip():
                    continue
                sentence, sep, label = line.rpartition("@")
                _check(sep == "@", f"{member}, line {i}: no '@' separator")
                rows.append({
                    "text": sentence.strip(),
                    "label": label.strip(),
                    "agreement": agreement,
                    "row_in_file": i,
                })
            df = pd.DataFrame(rows)
            expected = expected_rows[agreement]
            _check(len(df) == expected, f"{member}: {len(df)} rows, expected {expected}")
            df["source_file"] = member
            frames.append(df)
    out = pd.concat(frames, ignore_index=True)
    labels = set(out["label"])
    _check(labels == PHRASEBANK_LABELS, f"unexpected labels {labels}")
    _check((out["text"].str.len() > 0).all(), "empty sentence found")

    return out

TWITTER_LABELS = {0: "bearish", 1: "bullish", 2: "neutral"}
TWITTER_EXPECTED_ROWS: dict[str, int | None] = {"sent_train.csv": 9543, "sent_valid.csv": 2388}

def load_twitter(paths: dict[str, Path], expected_rows: dict[str, int | None] = TWITTER_EXPECTED_ROWS) -> pd.DataFrame:
    """Read the CSVs, keeping original order and file of origin"""
    frames = []
    for name, path in paths.items():
        df = pd.read_csv(path)
        expected_cols = ["text", "label"]
        _check(list(df.columns) == expected_cols, f"file {name} has {list(df.columns)}, expected {expected_cols}")
        expected = expected_rows.get(name)
        if expected is not None:
            _check(len(df) == expected, f"file {name} has {len(df)} rows, expected {expected}")
        df["label_name"] = df["label"].map(TWITTER_LABELS)
        _check(df["label_name"].notna().all(), "after mapping the expected label values there are still NaN values")
        df["source_file"] = name
        df["row_in_file"] = range(len(df))
        frames.append(df)

    return pd.concat(frames, ignore_index=True)