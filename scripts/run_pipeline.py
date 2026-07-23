import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import logging
from datetime import datetime

from blinkit.ingest.play_store import fetch_play_store_reviews
from blinkit.clean import clean_and_normalize
from blinkit.filter_discovery import filter_discovery_reviews
from blinkit.analysis.embeddings import generate_embeddings
from blinkit.analysis.reduce import reduce_dimensions
from blinkit.analysis.cluster import run_clustering, build_clusters
from blinkit.summarize import summarize_cluster

# Fix Windows console unicode printing errors
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_markdown_report(discovery_insights, operational_insights, total_raw, total_cleaned, total_discovery, discovery_clusters_count):
    report = f"""# Blinkit Product Discovery Research Report
*Generated on: {datetime.now().strftime('%Y-%m-%d')}*

## 1. Executive Summary
**Methodology:** {total_raw} raw Play Store reviews \u2192 {total_cleaned} cleaned reviews \u2192 dual pipeline.
The dual pipeline consists of a full-dataset operational analysis, and a keyword-filtered discovery analysis which isolated {total_discovery} reviews and identified {discovery_clusters_count} specific discovery clusters.

**Top-line Finding:**
While the vast majority of Blinkit reviews revolve around operational logistics (delivery speed, pricing, and refunds), a distinct subset of users are actively trying to discover new categories but are blocked by limited assortment, poor search discovery, and lack of competitive pricing/reviews. Users are habitual in their core categories but desire a wider catalog (like beauty, niche items like yarn) if trust and pricing barriers can be overcome.

## 2. Category Discovery Insights
*These insights were extracted from the targeted {total_discovery}-review discovery subset.*

"""
    for idx, insight in enumerate(discovery_insights):
        if insight.cluster_type == "Discovery":
            report += f"### Insight {idx+1}: {insight.theme}\n\n"
            report += "**Research Questions Answered:**\n"
            for q in insight.supported_research_questions:
                report += f"- **Q{q.question_number}: {q.question}**\n"
                report += f"  - *Answer:* {q.answer} (Evidence Count: {q.evidence_count})\n"
            
            report += "\n**Representative Evidence (Verbatim):**\n"
            for quote in insight.representative_quotes:
                report += f"- \"{quote}\"\n"
                
            report += "\n**PM Opportunities:**\n"
            for opp in insight.pm_opportunities:
                report += f"- {opp}\n"
            report += "\n---\n"
            
    report += f"""## 3. Overall App Health / Operational Themes
*Contextual insights extracted from the broader operational dataset (top 5 largest macro clusters).*

"""
    for idx, insight in enumerate(operational_insights):
        report += f"### {insight.theme}\n"
        report += f"**Pain Points:** {', '.join(insight.pain_points)}\n"
        report += "\n**PM Opportunities:**\n"
        for opp in insight.pm_opportunities:
            report += f"- {opp}\n"
        report += "\n"
            
    report += f"""## 4. Validation Methodology
- **Classification Logic**: The LLM acts as a Senior PM, explicitly instructed to classify a cluster as "Discovery" only if it contains evidence about browsing, habits, trust, or category assortment. Clusters focused purely on delivery delays or refunds are tagged "Operational".
- **Verbatim Validation**: Every quote extracted by the LLM is programmatically validated against the raw review text to prevent hallucination.
- **Targeted Filtering**: Because Play Store reviews heavily skew towards operational complaints, we used a regex keyword filter to isolate the sparse (but high-value) discovery signals before clustering, preventing them from being drowned out by logistical noise.

## 5. Limitations
- **Operational Skew**: Play Store reviews are fundamentally skewed towards operational issues (complaints about delivery or bugs). The category-discovery signal is real but rare (only {total_discovery} of {total_cleaned} reviews, ~{round((total_discovery/total_cleaned)*100, 2) if total_cleaned > 0 else 0}%).
- **Need for Primary Research**: Because App Store reviews lack deep contextual user intent, these findings are directional. This motivates why primary user interviews (Part 2 of the project) are essential to validate these findings and dig deeper into the "why" behind the behaviors.
"""
    return report

def main():
    logger.info("Starting Blinkit Review Analysis Pipeline...")
    
    # 1. Ingest
    logger.info("Fetching up to 10000 Play Store reviews...")
    raw_reviews = fetch_play_store_reviews(count=10000)
    total_raw = len(raw_reviews)
    
    # 2. Clean
    cleaned_reviews = clean_and_normalize(raw_reviews, min_length=15)
    total_cleaned = len(cleaned_reviews)
    logger.info(f"Total cleaned reviews: {total_cleaned}")
    
    # 3. Filter Discovery Subset
    discovery_reviews = filter_discovery_reviews(cleaned_reviews)
    total_discovery = len(discovery_reviews)
    logger.info(f"Filtered discovery reviews: {total_discovery}")
    
    discovery_insights = []
    discovery_clusters_count = 0
    if total_discovery > 0:
        logger.info("Generating embeddings for Discovery subset...")
        d_embeddings = generate_embeddings(discovery_reviews)
        d_reduced = reduce_dimensions(d_embeddings)
        d_labels = run_clustering(d_reduced, min_cluster_size=7, min_samples=3)
        d_clusters, _ = build_clusters(discovery_reviews, d_labels, top_k=20)
        discovery_clusters_count = len(d_clusters)
        
        review_dict = {r.id: r for r in discovery_reviews}
        for c in d_clusters:
            c_reviews = [review_dict[r_id] for r_id in c.review_ids]
            insight = summarize_cluster(c_reviews)
            discovery_insights.append(insight)
            
    # 4. Process Operational (Full Dataset) Subset
    operational_insights = []
    logger.info("Generating embeddings for Full Operational dataset...")
    o_embeddings = generate_embeddings(cleaned_reviews)
    o_reduced = reduce_dimensions(o_embeddings)
    o_labels = run_clustering(o_reduced, min_cluster_size=50) # high cluster size for macro themes
    o_clusters, _ = build_clusters(cleaned_reviews, o_labels, top_k=5)
    
    all_review_dict = {r.id: r for r in cleaned_reviews}
    for c in o_clusters:
        c_reviews = [all_review_dict[r_id] for r_id in c.review_ids]
        insight = summarize_cluster(c_reviews)
        operational_insights.append(insight)

    # 5. Generate Report
    report_md = generate_markdown_report(
        discovery_insights=discovery_insights,
        operational_insights=operational_insights,
        total_raw=total_raw,
        total_cleaned=total_cleaned,
        total_discovery=total_discovery,
        discovery_clusters_count=discovery_clusters_count
    )
    
    os.makedirs("data/reports", exist_ok=True)
    report_path = "data/reports/blinkit_discovery_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_md)
        
    logger.info(f"Pipeline complete! Report saved to {report_path}")

if __name__ == "__main__":
    main()
