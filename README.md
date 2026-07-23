# Blinkit AI Discovery Engine

An AI-powered dual-source research platform that mines **10,000 Google Play Store reviews** and **134 curated community discussions** to surface evidence-backed product insights for Blinkit Product Managers.

> **Live Dashboard →** [blinkit-review-discovery-engine.vercel.app](https://blinkit-review-discovery-engine.vercel.app)
> **GitHub Repository →** [ck-anand612/blinkit-review-discovery-engine](https://github.com/ck-anand612/blinkit-review-discovery-engine)

---

## Problem

Blinkit's Growth team needs to understand why users stay locked in habitual purchase categories and what friction prevents them from discovering new ones (e.g., Electronics, Beauty, Personal Care, Baby Care). App Store reviews are rich data but overwhelmingly skewed toward operational complaints — making rare **"discovery intent" signals** nearly impossible to isolate through manual or keyword-only analysis.

## Solution

A **dual-source NLP pipeline** that:

1. Scrapes, cleans, and semantically clusters 10,000 Play Store reviews using `sentence-transformers` + UMAP + HDBSCAN
2. Processes 134 curated Reddit/forum discussions through the same LLM summarization function
3. Uses a PM-persona Groq/LLaMA 3 prompt to classify clusters as **Discovery** vs **Operational** and extract structured findings
4. Validates every extracted quote verbatim against source text (zero hallucination tolerance)
5. Renders findings into a markdown report and an interactive AI Discovery Dashboard

---

## Dataset

| Source | Count |
|--------|------:|
| Google Play Store reviews (raw) | 10,000 |
| Google Play Store reviews (cleaned) | 4,281 |
| Discovery-focused reviews (keyword-filtered) | 125 |
| Community discussions (Reddit / forums) | 134 |
| Discovery clusters identified | 5 |

---

## Research Questions

The pipeline is structured to answer 8 core research questions, each grounded in verbatim evidence:

| # | Research Question | Report Section |
|---|---|---|
| Q1 | Why do users repeatedly buy from the same categories? | Category Discovery Insights |
| Q2 | What prevents users from exploring new categories? | Trust & Authenticity Barriers |
| Q3 | How do users currently discover products on Blinkit? | Category Discovery Insights |
| Q4 | What role do habits play in shopping behavior? | Category Discovery Insights |
| Q5 | What information do users need before trying a new category? | Trust & Authenticity Barriers |
| Q6 | What frustrations emerge repeatedly? | Operational Themes |
| Q7 | Which user segments are more willing to experiment? | Category Discovery Insights |
| Q8 | What unmet needs emerge consistently? | PM Opportunities |

---

## Architecture

```
Google Play Store          Community CSVs
(com.grofers.customerapp)  (Reddit / Forums)
        │                        │
        ▼                        ▼
  blinkit/ingest/          blinkit/ingest/
  play_store.py            (CSV loader)
        │                        │
        └────────────────────────┘
                   │
                   ▼
           blinkit/clean.py
     (Dedup · PII scrub · noise filter)
                   │
        ┌──────────┴──────────┐
        │ Source A             │ Source B
        ▼                     │ (pre-filtered)
 blinkit/analysis/            │
 embeddings.py → reduce.py    │
 → cluster.py                 │
        │                     │
        └──────────┬──────────┘
                   ▼
           blinkit/summarize.py
      (Groq LLaMA 3 · PM persona prompt)
                   │
                   ▼
         Quote & theme validation
                   │
                   ▼
     data/reports/blinkit_discovery_report.md
                   │
                   ▼
         dashboard/index.html
    (AI Discovery Dashboard · Vercel)
```

See [docs/architecture.md](docs/architecture.md) for a detailed component breakdown with Mermaid diagram.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12+ |
| Scraping | `google-play-scraper ≥ 1.2` |
| Embeddings | `sentence-transformers ≥ 3.0` — `BAAI/bge-small-en-v1.5` |
| Dimensionality Reduction | `umap-learn ≥ 0.5` |
| Clustering | `hdbscan ≥ 0.8` |
| LLM Inference | `groq ≥ 0.9` — `llama-3.3-70b-versatile` |
| Data Validation | `pydantic ≥ 2.0` |
| Dashboard | Vanilla HTML/CSS/JS · Chart.js · Vercel (static deploy) |

---

## Repository Structure

```
blinkit-review-discovery-engine/
├── blinkit/                        # Core Python package
│   ├── ingest/
│   │   └── play_store.py           # Google Play scraper (com.grofers.customerapp)
│   ├── analysis/
│   │   ├── embeddings.py           # BAAI/bge-small-en-v1.5 sentence embeddings
│   │   ├── reduce.py               # UMAP dimensionality reduction (5D, cosine)
│   │   └── cluster.py              # HDBSCAN clustering + composite ranking
│   ├── clean.py                    # Dedup (MD5) · PII scrub · noise filter
│   ├── filter_discovery.py         # Regex keyword filter → discovery subset
│   ├── summarize.py                # Groq LLaMA 3 PM-persona summarization
│   └── models.py                   # Pydantic schemas: Review, Cluster, Insight, Report
│
├── scripts/
│   ├── run_pipeline.py             # Main end-to-end orchestrator (entry point)
│   ├── run_discovery_pipeline.py   # Discovery-only pipeline run
│   ├── run_summarization.py        # Standalone LLM summarization step
│   ├── apply_pm_updates.py         # Applies PM-layer updates to report
│   ├── generate_section2b.py       # Generates community analysis section
│   └── inspect_clusters.py         # Debug: inspect cluster contents
│
├── data/
│   ├── raw/
│   │   └── community_comments/
│   │       ├── Blinkit_User_Comments_Verbatim.csv  # 134 curated discussions
│   │       └── user_comments.csv
│   ├── outputs/                    # Intermediate JSON/CSV pipeline caches
│   └── reports/
│       └── blinkit_discovery_report.md             # Final research report
│
├── dashboard/
│   └── index.html                  # AI Discovery Dashboard (static, Vercel-deployed)
│
├── docs/
│   ├── problemStatement.md         # Business context and research questions
│   ├── architecture.md             # System design and component breakdown
│   ├── implementation-plan.md      # Phase-by-phase build log
│   └── edge-cases.md               # Failure modes and mitigations
│
├── tests/
│   ├── test_clean.py
│   ├── test_cluster.py
│   ├── test_play_store.py
│   └── test_summarize.py
│
├── config/                         # Configuration files
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## Setup & Run

### Prerequisites

- Python 3.12+
- A free [Groq API key](https://console.groq.com)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/ck-anand612/blinkit-review-discovery-engine.git
cd blinkit-review-discovery-engine

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
.venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Edit .env and set:  GROQ_API_KEY=your_api_key_here
```

### Run the Full Pipeline

```bash
python scripts/run_pipeline.py
```

This executes the complete dual-source pipeline in sequence:

1. **Ingest** — Fetches up to 10,000 Play Store reviews + loads community CSVs
2. **Clean** — Deduplicates, PII-scrubs, and noise-filters all reviews
3. **Filter** — Regex keyword pass isolates discovery-intent reviews (→ 125)
4. **Embed** — Generates 384-dimensional sentence embeddings (BAAI/bge-small-en-v1.5)
5. **Reduce** — UMAP reduces embeddings to 5D (cosine metric)
6. **Cluster** — HDBSCAN groups reviews into semantic clusters (→ 5 discovery clusters)
7. **Summarize** — Groq LLaMA 3 classifies and extracts structured PM insights
8. **Validate** — Verbatim quote validation against source text
9. **Report** — Outputs `data/reports/blinkit_discovery_report.md`

> **Note:** Embedding ~4,000+ reviews takes 3–5 minutes on CPU. The model downloads automatically on first run.

### Run Individual Steps

```bash
# Discovery pipeline only (no operational clusters)
python scripts/run_discovery_pipeline.py

# LLM summarization step only (requires cached cluster data)
python scripts/run_summarization.py

# Inspect cluster contents for debugging
python scripts/inspect_clusters.py
```

### Tests

```bash
pytest tests/
```

---

## Key Findings

The full report is at [`data/reports/blinkit_discovery_report.md`](data/reports/blinkit_discovery_report.md).

**Top-line insight:** Blinkit users are deeply habitual in their grocery and essentials categories. Cross-category exploration is blocked by three compounding barriers: **trust deficits** (fake/damaged products in non-grocery categories), **price perception** (non-grocery items appear expensive vs. Amazon/local stores), and **limited assortment** (low brand variety outside core categories).

The 2.92% discovery signal (125 of 4,281 reviews) represents a coherent, high-LTV user segment actively seeking catalog expansion — underserved by the current experience.

| Finding | Confidence |
|---|---|
| Trust & authenticity are the #1 barrier to non-grocery exploration | 97% |
| Price perception blocks category switching | 95% |
| Passive home-feed browsing is the primary discovery surface (not search) | 88% |
| Explorer segment skews toward convenience-first, multi-category users | 80% |

---

## Dashboard

The AI Discovery Dashboard presents all findings in an interactive internal PM workspace.

**Live:** [blinkit-review-discovery-engine.vercel.app](https://blinkit-review-discovery-engine.vercel.app)

Features:
- **AI Discovery Assistant** — Select from 8 pre-loaded research questions or ask your own; returns structured answers with Executive Summary, Key Findings, Verbatim Quotes, PM Insight, Confidence Score, and Source attribution
- **Dataset Overview** — Animated stat cards (10,000 → 4,281 → 125 → 134 → 5)
- **Top Discovery Insights** — 6 expandable evidence cards mapped to research questions
- **Trust & Authenticity Section** — Pain points + PM opportunities + verbatim community quotes
- **Pain Point Frequency Chart** — Operational vs Discovery split (Chart.js bar chart)
- **Pipeline Architecture** — Interactive 6-step horizontal flow diagram
- **Global Navigation** — Dashboard · AI Research · Customer Signals · Product Opportunities · Insights Library

---

## Deployment

The dashboard is a static HTML file deployed to [Vercel](https://vercel.com) via GitHub auto-deployment.

```
Repository: ck-anand612/blinkit-review-discovery-engine
Branch:     master
Build:      None (static HTML, no build step required)
Output:     dashboard/index.html
```

Any push to `master` triggers an automatic Vercel redeploy.

---

## Documentation

| Document | Description |
|---|---|
| [docs/problemStatement.md](docs/problemStatement.md) | Business context, research questions, and success criteria |
| [docs/architecture.md](docs/architecture.md) | System design, component breakdown, and Mermaid flow diagram |
| [docs/implementation-plan.md](docs/implementation-plan.md) | Phase-by-phase build log of what was implemented |
| [docs/edge-cases.md](docs/edge-cases.md) | Failure modes, edge cases, and mitigations by pipeline stage |

---