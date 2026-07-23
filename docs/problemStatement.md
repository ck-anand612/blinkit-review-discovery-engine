# Problem Statement — Blinkit Category Discovery Analysis

## Project Context

I am acting as a Product Manager on the Growth Team at Blinkit, a leading 
quick-commerce platform in India.

Blinkit has successfully become part of users' weekly shopping routines. Many 
customers regularly purchase groceries, snacks & beverages, and household 
essentials. While these recurring purchases drive engagement, shopping behavior 
gradually becomes repetitive. Most users continue purchasing from the same 
categories month after month and rarely explore other categories available on 
the platform, such as Personal Care, Pet Supplies, Baby Care, Beauty, Home 
Improvement, or Electronics.

This limits users' awareness of Blinkit's broader catalog and reduces 
opportunities for cross-category growth.

## Business Goal

Increase the percentage of Monthly Active Customers (MAC) who purchase products 
from at least one NEW category every month.

Examples of the target behavior:
- A grocery shopper purchasing from the Personal Care category for the first time
- A snacks buyer discovering Pet Supplies
- A household essentials customer purchasing Baby Care products

Achieving this goal can increase customer engagement, basket size, purchase 
frequency, and long-term customer lifetime value.

## Project Objective

Before proposing any product solution, build an AI-Powered Discovery Engine 
that analyzes user feedback at scale to understand why users continue 
purchasing from the same categories and what prevents them from exploring 
new ones.

The objective is to generate evidence-based product insights rather than 
assumptions.

## Research Questions Addressed

The AI Discovery Engine should help answer the following questions. Each is mapped to the pipeline stage/report section that answers it:

1. **Why do users repeatedly purchase from the same categories?** (Answered via LLM Summarization prompt applied to both sources; covered in Discovery Insights)
2. **What prevents users from exploring new product categories?** (Answered via LLM Summarization prompt; covered in Trust & Authenticity Barriers and Discovery Insights)
3. **How do users currently discover products on Blinkit?** (Answered via LLM Summarization prompt; covered in Discovery Insights)
4. **What role do habits play in shopping behavior?** (Answered via LLM Summarization prompt; covered in Discovery Insights)
5. **What information or reassurance do users need before trying a new category?** (Answered via LLM Summarization prompt; covered in Trust & Authenticity Barriers and Discovery Insights)
6. **What frustrations repeatedly emerge across user feedback?** (Answered via LLM Summarization prompt; covered in Operational Themes and Discovery Insights)
7. **Which user segments appear more willing to experiment?** (Answered via LLM Summarization prompt; covered in Discovery Insights)
8. **What unmet needs consistently appear across customer discussions?** (Answered via LLM Summarization prompt; covered in PM Opportunities across all themes)

## Scope of Phase 1

The AI Discovery Engine will analyze publicly available customer feedback from a **DUAL-SOURCE** pipeline:

- **Source A: Google Play Store reviews** (10,000 scraped → cleaned → embedded → UMAP/HDBSCAN clustered → keyword-filtered discovery subset → LLM summarized).
- **Source B: Curated community/Reddit/forum comments** (AI-assisted secondary research from publicly available Reddit and community discussions, curated into a structured dataset., saved as CSVs, deduplicated, passed directly through the same LLM summarization function — no clustering needed since already pre-filtered).

These two sources were selected as the highest-signal, most accessible channels 
for quick-commerce user feedback within the project timeline.

The system should automatically identify recurring themes, behavioral patterns, 
pain points, and opportunities from this feedback.

Pipeline approach: gather → clean/normalize → (if Source A: embed → cluster) → summarize → validate.

## What the Engine Must Demonstrate

- How the workflow gathers and analyzes review data (Play Store + Community data)
- How themes/clusters are identified from raw text
- How insights are generated from those themes
- How insight quality is validated (e.g., sampling raw reviews per theme and 
  confirming they genuinely match the assigned theme, verbatim quote validation)

## Success Criteria (Phase 1)

- At least 1,500 valid, cleaned Play Store reviews collected + high-quality curated community comments processed
- Reviews successfully normalized (deduped, PII-scrubbed, noise-filtered)
- Dual-source output saved as a structured file ready for analysis
- Synthesized insights presented across both streams

## Expected Outcome

The AI Discovery Engine should produce validated product insights that will:

- Identify the most promising opportunity for increasing cross-category adoption
- Help select a target user segment for further research
- Guide 5-6 primary user interviews to validate or challenge the AI-generated findings
- Form the foundation for defining the product problem and designing an 
  AI-native MVP in later phases

This phase focuses entirely on problem discovery and insight generation, not 
on proposing or building a product solution.

## Out of Scope (for this phase)

- No feature design or MVP building happens in this phase
- No delivery integrations (no Google Docs/Gmail/Slack delivery)
- No scheduled/recurring automation — this is a one-time analysis run
