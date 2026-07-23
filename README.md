# Blinkit Category Discovery Engine

## Problem
Blinkit's Product Growth team needs to understand why users stick to habitual categories and what friction prevents them from discovering and purchasing from new, non-habitual categories (e.g., Electronics, Beauty, Niche items like Yarn). App Store reviews and community discussions are goldmines of customer feedback, but they are overwhelmingly skewed towards operational complaints (delivery delays, missing items, refund issues), making it nearly impossible to extract rare "Discovery" signals using traditional analysis.

## Solution
This project implements a **DUAL-SOURCE** Natural Language Processing (NLP) pipeline that aggressively isolates high-value discovery signals from two complementary data streams:
- **Source A:** Google Play Store reviews (10,000 scraped → cleaned → embedded → UMAP/HDBSCAN clustered → keyword-filtered discovery subset → LLM summarized).
- **Source B:** Curated community/Reddit/forum comments (AI-assisted secondary research from publicly available Reddit and community discussions, curated into a structured dataset., saved as CSVs, deduplicated, passed directly through the same LLM summarization function — no clustering needed since already pre-filtered).

We use state-of-the-art embedding models (BAAI/bge-small-en-v1.5), dimensionality reduction (UMAP), and clustering (HDBSCAN) for unstructured Play Store data. Finally, a PM-persona LLM (Llama 3.3 70B via Groq) summarizes both streams into actionable product opportunities and directly answers our core research questions with validated verbatim evidence.


## Dataset Summary

| Source | Count |
|--------|------:|
| Google Play Reviews (Raw) | 10,000 |
| Google Play Reviews (Cleaned) | 4,281 |
| Discovery-focused Reviews | 125 |
| Community Discussions | 134 |
| Discovery Clusters | 5 |

## Research Questions Addressed
This engine explicitly seeks to answer 8 core research questions, which are mapped directly to findings in the final report:

| # | Research Question | Where Answered |
|---|---|---|
| 1 | Why do users repeatedly buy from the same categories? | Category Discovery Findings |
| 2 | What prevents users from exploring new categories? | Trust & Authenticity Barriers, Category Discovery Findings |
| 3 | How do users discover products today? | Category Discovery Findings |
| 4 | What role do habits play in shopping behavior? | Category Discovery Findings |
| 5 | What information do users need before trying a new category? | Trust & Authenticity Barriers, Category Discovery Findings |
| 6 | What frustrations emerge repeatedly? | Operational Themes, Category Discovery Findings |
| 7 | Which user segments are more likely to experiment? | Category Discovery Findings |
| 8 | What unmet needs emerge consistently across discussions? | PM Opportunities across all themes |

## How This Engine Demonstrates Discovery Quality
1. **How the workflow gathers and analyzes data:** The engine utilizes a dual-source approach, combining a fully coded scraping pipeline for quantitative scale (Google Play Store) with curated qualitative research (Reddit/forums). Both streams feed into the exact same standardized LLM analysis pipeline to ensure consistent evaluation.
2. **How themes are identified:** For the massive, unstructured Play Store dataset, themes are algorithmically surfaced using dense embeddings, UMAP dimensionality reduction, and HDBSCAN density clustering. For the pre-curated community data, direct LLM classification is applied to extract nuanced themes without losing sparse signals.
3. **How insights are generated:** A specialized PM-persona LLM prompt via Groq processes the structured text. The prompt is strictly instructed to classify clusters as "Discovery" vs "Operational", and is forced to answer only research-question-grounded findings rather than generic summaries.
4. **How insight quality was validated:** The pipeline enforces strict verbatim quote validation against the raw source text to prevent LLM hallucinations. Furthermore, insight quality is demonstrated via cross-source convergence—both Play Store analysis and community research independently pointed to trust and authenticity as key barriers. Sample-size transparency (evidence count) is included in all findings.

## Architecture
1. **Ingestion**: Scrapes up to 10,000 recent reviews from the Google Play Store (`google-play-scraper`) and ingests curated community CSVs.
2. **Cleaning & Normalization**: Strips emojis, URLs, and short/low-effort reviews. Deduplicates all data.
3. **Keyword Filtering**: A regex-based funnel isolates reviews containing discovery-intent keywords (for Source A).
4. **Embeddings & Clustering**: Text is embedded and clustered using UMAP + HDBSCAN to find behavioral themes (for Source A).
5. **Summarization**: The PM-persona LLM classifies each cluster/batch as "Discovery" or "Operational" and extracts pain points, PM opportunities, and verbatim quotes (for both Source A and Source B).
6. **Orchestration & Reporting**: The pipeline generates a comprehensive markdown report detailing the findings from both sources.

## Tech Stack
- **Python 3.12+**
- **Scraping**: `google-play-scraper`
- **Embeddings**: `sentence-transformers` (BAAI/bge-small-en-v1.5)
- **Clustering**: `umap-learn`, `hdbscan`, `scikit-learn`
- **LLM**: `groq` (llama-3.3-70b-versatile)
- **Modeling**: `pydantic`

## How to Run
1. Clone the repository and navigate to the project root.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set your Groq API key in a `.env` file:
   ```env
   GROQ_API_KEY=your_api_key_here
   ```
4. Run the end-to-end pipeline orchestrator:
   ```bash
   python scripts/run_pipeline.py
   ```
   *Note: Generating embeddings for ~4000+ cleaned reviews will take a few minutes.*

## Results
The complete findings of our dual-source analysis are available in the final report. The report details our methodology, reveals our top category discovery insights from both the Play Store and community sources, and provides the necessary operational context for Blinkit's app health.

**[View the Final Research Report](data/reports/blinkit_discovery_report.md)**
