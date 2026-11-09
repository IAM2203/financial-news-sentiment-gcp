"""Data-quality measurements for decision D-004, reused later to verify the split."""

from __future__ import annotations

import itertools

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors


def normalize_text(s: pd.Series) -> pd.Series:
    """Comparison key: lowercase, URLs removed, whitespace collapsed."""
    return (
        s.str.lower()
        .str.replace(r"https?://\S+", " ", regex=True)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

def exact_duplicates(df: pd.DataFrame, text_col: str = "text", label_col: str = "label") -> pd.DataFrame:
    """One row per normalized text that appears more than once, with how many labels it got."""
    keyed = df.assign(key=normalize_text(df[text_col]))
    out = keyed.groupby("key").agg(n=(label_col, "size"), n_labels=(label_col, "nunique"))

    return out[out["n"] > 1].sort_values("n", ascending=False)

def cross_overlap(a: pd.DataFrame, b: pd.DataFrame, text_col: str = "text") -> pd.DataFrame:
    """Rows of b whose normalized text also appears in a."""
    keys_a = set(normalize_text(a[text_col]))

    return b[normalize_text(b[text_col]).isin(keys_a)]

def check_nesting(df: pd.DataFrame, level_col: str = "agreement", text_col: str = "text", label_col: str = "label") -> pd.DataFrame:
    """For each pair of consecutive levels: stricter texts missing from the looser one,
    and texts whose label differs between the two."""
    levels = sorted(df[level_col].unique(), reverse=True)
    rows = []
    for hi, lo in itertools.pairwise(levels):
        a = df[df[level_col] == hi].drop_duplicates(text_col).set_index(text_col)[label_col]
        b = df[df[level_col] == lo].drop_duplicates(text_col).set_index(text_col)[label_col]
        common = a.index.intersection(b.index)
        rows.append({
            "stricter": hi,
            "looser": lo,
            "n_stricter": len(a),
            "missing_in_looser": len(a.index.difference(b.index)),
            "label_changes": int((a[common] != b[common]).sum()),
        })

    return pd.DataFrame(rows)

def nearest_neighbors(reference: pd.Series, query: pd.Series | None = None) -> pd.DataFrame:
    """For each query text, its most similar reference text (cosine similarity on TF-IDF).
    
    With query=None, compares reference against itself and never matches a row with itself.
    Positions are 0-based row positions, not index labels.
    """
    same = query is None

    ref_key = normalize_text(reference)
    qry_key = ref_key if same else normalize_text(query)

    vec = TfidfVectorizer().fit(ref_key if same else pd.concat([ref_key, qry_key]))
    R = vec.transform(ref_key)
    Q = vec.transform(qry_key)

    nn = NearestNeighbors(n_neighbors=2 if same else 1, metric="cosine").fit(R)
    dist, idx = nn.kneighbors(Q)

    rows = np.arange(Q.shape[0])
    pick = np.where(idx[:, 0] == rows, 1, 0) if same else np.zeros(len(rows), dtype=int)

    return pd.DataFrame({
        "query_pos": rows,
        "match_pos": idx[rows, pick],
        "similarity": 1 - dist[rows, pick],
    })
