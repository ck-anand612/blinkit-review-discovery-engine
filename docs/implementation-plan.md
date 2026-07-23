# Blinkit Category Discovery Engine — Phase-Wise Implementation Plan

This document outlines the step-by-step implementation plan for building the AI-Powered Discovery Engine as defined in the [Problem Statement](problemStatement.md) and [Architecture](architecture.md). 

The development is broken down into 5 sequential phases to ensure each pipeline component can be tested independently before integration.

---

## Phase 1: Project Setup & Data Models
**Goal**: Establish the foundational environment, directory structure, and data contracts.

1. **Environment Setup**
   - Initialize the Python project and virtual environment (Python 3.11+).
   - Create `requirements.txt` with necessary dependencies: `google-play-scraper`, `sentence-transformers`, `umap-learn`, `hdbscan`, `groq`, `pydantic`, `python-dotenv`.
2. **Directory Structure**
   - Setup project folders: `blinkit/` (core package), `config/`, `data/raw/` (with subfolders for Play Store and community CSVs), `data/reports/`.
3. **Data Models**
   - Define strict Pydantic schemas in `blinkit/models.py`:
     - `Review`: ID, text, rating, date, source (Play Store vs Reddit/Community).
     - `Cluster`: Rank, size, average rating, date range, list of review IDs, centroid/embeddings.
     - `Insight`: Theme name, summary, pain points, action ideas, representative quotes.
     - `Report`: Aggregate data containing all clusters, noise metrics, and validation scores for both sources.

---

## Phase 2: Dual-Source Data Ingestion & Cleaning
**Goal**: Successfully gather and normalize raw customer feedback from both Play Store and Community CSVs.

1. **Google Play Store Scraper (`blinkit/ingest/play_store.py`)** [Source A]
   - Implement scraping logic targeting `com.grofers.customerapp`.
   - Configure to pull up to 10,000 recent English reviews from India.
2. **Community CSV Loader** [Source B]
   - Implement CSV parsing logic to load curated Reddit/forum datasets.
3. **Data Normalization (`blinkit/clean.py`)**
   - Implement deduplication using MD5 hashing on text (and URL for Source B).
   - Build PII scrubbers (regex for phone numbers, emails, UPI IDs).
   - Filter out noise (e.g., reviews < 15 characters).
4. **Milestone Test**: Run ingestion independently to ensure clean, valid data sets are saved to `data/raw/reviews_normalized.json` and parsed CSVs are ready.

---

## Phase 3: Analysis Engine (ML Pipeline) - Source A Only
**Goal**: Group raw unstructured Play Store reviews into distinct semantic themes. (Source B skips this phase as it is pre-curated).

1. **Embeddings (`blinkit/analysis/embeddings.py`)**
   - Integrate `sentence-transformers` with `BAAI/bge-small-en-v1.5`.
   - Create functions to batch-process review text into 384-dimensional vectors.
2. **Dimensionality Reduction (`blinkit/analysis/reduce.py`)**
   - Implement UMAP reduction (cosine metric, `n_components=5`).
3. **Clustering (`blinkit/analysis/cluster.py`)**
   - Apply HDBSCAN clustering on the reduced UMAP embeddings.
   - Implement a composite scoring function (size, severity, recency) to rank the top-K (e.g., top 6) clusters.
   - Identify and separate noise (-1 cluster).
4. **Milestone Test**: Input the JSON from Phase 2 and output structured JSON of ranked clusters containing grouped review texts.

---

## Phase 4: Insight Generation & Validation (Both Sources)
**Goal**: Translate mathematical clusters (Source A) and grouped CSVs (Source B) into human-readable product insights without hallucinations.

1. **LLM Summarization (`blinkit/summarize.py`)**
   - Integrate the Groq API (`llama-3.3-70b-versatile`).
   - Craft a highly specific system prompt focused on *category discovery, habit loops, and trust signals*.
   - Send cluster snippets/batches to Groq and parse the JSON response (theme, summary, quotes, pain points, actions).
2. **Quote Validation**
   - Implement logic to strictly verify that every LLM-generated quote exists verbatim in the source texts. Build automatic retry logic if hallucinated quotes are detected.
3. **Theme Validation (`blinkit/validate.py`)**
   - Implement secondary LLM check: Sample raw reviews per cluster/batch and ask the LLM to score how well they match the generated theme.
4. **Milestone Test**: Input the clusters/batches and output validated Insight models for both data streams.

---

## Phase 5: Reporting & Orchestration
**Goal**: Tie everything together into a single command-line execution and render the final report.

1. **Report Rendering (`blinkit/render.py`)**
   - Write a markdown generator that takes the final data and formats it.
   - Include sections: Executive Summary, Play Store Discovery/Operational Insights, Supplementary Community Findings.
2. **Orchestrator (`run_pipeline.py`)**
   - Build the main CLI script that orchestrates the dual-source pipeline.
   - Add comprehensive logging to track progress during execution.
3. **Milestone Test**: Run `python run_pipeline.py` from scratch. The output should be a complete, actionable markdown file in `data/reports/` that directly answers the research questions in the Problem Statement using both sources.
