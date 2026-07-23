# Blinkit Category Discovery Engine — Edge Cases & Mitigations

This document outlines potential edge cases, failure modes, and corner cases for the AI-Powered Discovery Engine, mapped to the phases defined in the [Architecture](architecture.md) and [Implementation Plan](implementation-plan.md). It also details how the system should handle these scenarios gracefully across both data sources.

## 1. Data Ingestion & Cleaning

### 1.1 Source A (Play Store) API Rate Limits & Failures
* **Edge Case**: The `google-play-scraper` encounters undocumented API changes or gets rate-limited by Google.
* **Mitigation**: Implement exponential backoff for retries. If the scraper completely fails, fail the pipeline loudly with a clear error rather than proceeding with 0 reviews.

### 1.2 Source B (Community CSVs) Parsing Issues
* **Edge Case**: Curated CSV files are missing expected columns (e.g., `text`, `url`) or are malformed.
* **Mitigation**: Implement strict error handling during `csv.DictReader` loading. Log missing rows or columns and skip them gracefully without crashing the pipeline, while reporting the number of successfully parsed rows.

### 1.3 Data Sparsity & Quality
* **Edge Case**: The query parameters (date range, sorting) yield significantly fewer than 1,500 Play Store reviews.
* **Mitigation**: Add a sanity check after ingestion. If total reviews < 500, log a prominent warning that clustering quality may be degraded due to low sample size.
* **Edge Case**: Heavy use of "Hinglish" or localized slang that the BAAI embedding model struggles to understand.
* **Mitigation**: While BAAI is an English model, it generally handles some mixed text gracefully. If the text is purely Hindi written in Latin script, it may cluster poorly. We accept this as a known limitation for Phase 1.
* **Edge Case**: After PII scrubbing, a review becomes completely empty.
* **Mitigation**: The noise filter (discarding reviews < 15 characters) must run *after* the PII scrubber to catch and discard these empty or near-empty strings.

## 2. Analysis Engine (Embeddings & Clustering - Source A)

### 2.1 Clustering Extremes
* **Edge Case**: HDBSCAN marks 90%+ of the Play Store dataset as noise (-1 cluster).
* **Mitigation**: If the noise ratio exceeds 60%, the orchestrator should log a warning indicating that the feedback is highly disparate and lacks strong cohesive themes.
* **Edge Case**: "Mega-cluster" formation — 80% of reviews are grouped into a single massive cluster (e.g., "General complaints").
* **Mitigation**: Rely on the `cluster_selection_method="leaf"` parameter in HDBSCAN to aggressively break down large clusters into finer-grained, specific themes.
* **Edge Case**: Zero valid clusters are found (everything is noise or falls below `min_cluster_size`).
* **Mitigation**: The pipeline must gracefully halt and output a report stating that no statistically significant themes were detected in the current data snapshot.

### 2.2 Resource Constraints
* **Edge Case**: Out of Memory (OOM) errors during embedding generation.
* **Mitigation**: Process embeddings in manageable batches (e.g., batch size of 32 or 64) rather than loading all strings into the model at once.

## 3. Insight Generation & Validation (LLM - Both Sources)

### 3.1 LLM Formatting & Hallucination
* **Edge Case**: The LLM (Groq) hallucinates a quote that does not exist in the source snippets.
* **Mitigation**: The Quote Validation module strictly checks if the generated quote is a substring of the input (using simple string matching). If it fails, the system automatically triggers a retry (up to 2 times). If it still fails, the quote is dropped or replaced with a generic fallback.
* **Edge Case**: The LLM returns raw markdown text instead of the requested JSON schema.
* **Mitigation**: Use robust regex to strip markdown code blocks before passing the output to Python's `json.loads`. Retry the LLM call if parsing still fails.

### 3.2 Context Limits
* **Edge Case**: The combined text of the sampled snippets exceeds the LLM's context window.
* **Mitigation**: The pipeline will strictly limit the input (e.g. to the top 50 reviews or top 5 most representative snippets per cluster) and truncate individual reviews to 1,000 characters if necessary.

### 3.3 Theme Validation Discrepancy
* **Edge Case**: The LLM Theme Validator gives a cluster a score of 0, stating the sampled reviews do not match the generated theme.
* **Mitigation**: Include the low validation score prominently in the final markdown report. Do not delete the cluster, but flag it as "Low Confidence" so the PM knows the insight is shaky.

## 4. Orchestration

* **Edge Case**: Partial pipeline failure midway (e.g., crashes during LLM summarization).
* **Mitigation**: The pipeline should cache intermediate results (e.g., JSON/CSV caches). This prevents having to re-scrape or re-embed if a downstream step fails and needs to be re-run.
* **Edge Case**: Missing environment variables (`.env` not found).
* **Mitigation**: Fail fast during the initial setup/validation check in `run_pipeline.py` before making any API calls or loading heavy models.
