# Financial News Sentiment on Google Cloud

Which approach is worth it for classifying the sentiment of financial news headlines: a classical classifier, an open model used as-is, the same open model fine-tuned with LoRA, or a managed model (Gemini)? This project will answer that question with a data-backed recommendation, written as a deliverable for a client. "Fine-tuning is not worth it" is an acceptable answer.

> **Work in progress — currently in Phase 1.** Data acquisition and the data-quality audit are done. No model has been trained and nothing runs on Google Cloud yet. See [Status](#status).

## Status

_Last updated: November 7, 2026_

| Phase | Scope | Status |
|---|---|---|
| 0. Setup | GCP free-trial project; compute route under a zero GPU quota | Done |
| 1. Data and baseline | Pinned data, quality audit, fixed split, Cloud Storage and BigQuery, TF-IDF baseline | In progress (data and quality audit done) |
| 2. Open model, no tuning | Gemma with prompting, same evaluation as the baseline | Planned |
| 3. LoRA fine-tuning | Gemma fine-tuned on the training split | Planned |
| 4. Deployment | Container on Cloud Run (CPU), prediction and latency logging | Planned |
| 5. Comparison | Gemini as reference; macro-F1, cost and latency for all four options | Planned |
| 6. Final write-up | Client-style recommendation | Planned |

## What's done so far

- **Pinned, fingerprinted downloads.** Both candidate datasets are downloaded from Hugging Face at a fixed commit, and every file's SHA-256 is recorded in [`data/MANIFEST.json`](data/MANIFEST.json), which is under version control. If an upstream file ever changes, re-downloading it shows up as a diff in the manifest. Code: [`src/data.py`](src/data.py).
- **Loaders that fail loudly.** The readers check row counts, columns and label sets against expected values, and raise an error instead of returning bad data.
- **Data-quality audit.** [`src/quality.py`](src/quality.py) finds exact duplicates on a normalized key (lowercase, URLs removed, whitespace collapsed) and texts that appear with conflicting labels. On Twitter Financial News Sentiment: 11,931 rows, 98 repeated texts, 3 of them with conflicting labels; after cleaning, **11,776 unique texts**. The audit also found that 39 of the 2,388 rows (1.6%) in the dataset author's validation split already appear in its training split. Notebook: [`notebooks/02_d004_measurements.ipynb`](notebooks/02_d004_measurements.ipynb).
- **Dataset choice with criteria fixed before measuring.** The selection criteria were committed ([eca8351](https://github.com/IAM2203/financial-news-sentiment-gcp/commit/eca8351)) before any measurement ran, so the results could not shape the rules. Twitter Financial News Sentiment won over Financial PhraseBank on the pre-set tie-breaker: 3.1% vs. 25% of repeated texts with conflicting labels. The write-up also documents why that tie-breaker is fragile (PhraseBank's 25% comes from only 2 of 8 repeated texts). Full decision: [D-004](decisiones/D-004-eleccion-de-dataset.md) (in Spanish).

## Known limitations so far

- **Near-duplicates are not checked yet.** The audit only catches exact matches after normalization. Near-duplicates could still leak between train and test; they will be checked when the split is built.
- **Distribution shift.** The headlines date from late 2019 to early 2020, while a deployed model would see current news, so test-set scores will likely overestimate real-world performance.
- **Undocumented labeling.** The dataset does not describe how its labels were produced, and some labels are ambiguous.

## Planned approach

| Option | What it is |
|---|---|
| Classical baseline | TF-IDF + logistic regression |
| Open model, no tuning | Gemma (tentatively Gemma 3 1B), prompting only |
| Open model, fine-tuned | The same Gemma model, fine-tuned with LoRA on the training split |
| Managed model | Gemini through Gemini Enterprise Agent Platform (formerly Vertex AI), as a reference |

- **Same test set for all four.** The data will live in BigQuery with a fixed `split` column (train / val / test). The test split stays untouched until the final comparison.
- **Three metrics:** macro-F1, cost per 1,000 predictions, and latency.
- **Planned pipeline:** Cloud Storage → BigQuery → models → the fine-tuned model in a container (Cloud Build → Artifact Registry → Cloud Run on CPU), with predictions and latencies logged.
- **Designed around a constraint.** The free-trial GPU quota is 0, so LoRA training will run on a university GPU cluster (Colab as fallback) while serving stays on Cloud Run with CPU. That is why the served model has to be small.

## Data and license

- **Main dataset:** [Twitter Financial News Sentiment](https://huggingface.co/datasets/zeroshot/twitter-financial-news-sentiment) (MIT), pinned at revision `ccbe24de388e287beb92dd393a335c376b350ac3`. Labels: 0 = bearish, 1 = bullish, 2 = neutral.
- **The raw text is not committed.** `data/raw/` and `data/interim/` are git-ignored because it is unclear who owns the text of the tweets; `src/data.py` downloads it at the pinned revision.
- **Financial PhraseBank** (CC BY-NC-SA 3.0) was used only in the dataset comparison.

## Repository layout

```
├── data/MANIFEST.json              # pinned revision + SHA-256 of every downloaded file
├── decisiones/                     # one file per decision (in Spanish)
├── notebooks/
│   ├── 01_eda_datasets.ipynb       # offline tests, download, load, parquet round-trip
│   └── 02_d004_measurements.ipynb  # data-quality measurements for D-004
├── src/
│   ├── data.py                     # pinned downloads and validated loaders
│   └── quality.py                  # duplicate, conflict and overlap checks
├── DECISIONES.md                   # decision log index (in Spanish)
└── README.md
```

## Decision log

Every decision with real alternatives is recorded with its options, criteria and trade-offs. The log is in Spanish; one-line summaries:

| ID | Decision |
|---|---|
| [D-001](decisiones/D-001-ruta-sin-gpus.md) | No GPUs on GCP (free-trial quota is 0): train off-cloud, serve on Cloud Run with CPU |
| [D-002](decisiones/D-002-proyecto-sin-organizacion.md) | GCP project without an organization, to avoid default organization policies |
| [D-003](decisiones/D-003-gpu-saptiva.md) | Train on a university GPU cluster; Colab as fallback |
| [D-004](decisiones/D-004-eleccion-de-dataset.md) | Dataset: Twitter Financial News Sentiment, deduplicated, with a custom split |

## Environment

Python 3.12. Runtime dependencies are pinned in [`requirements.txt`](requirements.txt); development tools (Jupyter, matplotlib, ruff) in [`requirements-dev.txt`](requirements-dev.txt).

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```
