import os

def update_file(filepath, operations):
    if not os.path.exists(filepath):
        print(f"Skipping {filepath}, does not exist.")
        return
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    for old_text, new_text in operations:
        content = content.replace(old_text, new_text)
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Updated {filepath}")

def main():
    base_ops = [
        ("Supplementary Community Research Findings", "Community Discussion Insights (Secondary Evidence)"),
        ("*Answer:*", "*AI-generated Hypothesis:*"),
        ("manually researched via Gemini/ChatGPT deep research", "AI-assisted secondary research from publicly available Reddit and community discussions, curated into a structured dataset.")
    ]
    
    files_to_base_update = [
        "README.md",
        "docs/problemStatement.md",
        "docs/problem statement.txt",
        "docs/architecture.md",
        "docs/implementation-plan.md",
        "docs/edge-cases.md",
        "data/reports/blinkit_discovery_report.md"
    ]
    
    for f in files_to_base_update:
        update_file(f, base_ops)
        
    # README specific updates
    dataset_summary = """
## Dataset Summary

| Source | Count |
|--------|------:|
| Google Play Reviews (Raw) | 10,000 |
| Google Play Reviews (Cleaned) | 4,281 |
| Discovery-focused Reviews | 125 |
| Community Discussions | 134 |
| Discovery Clusters | 5 |
"""
    readme_path = "README.md"
    with open(readme_path, 'r', encoding='utf-8') as f:
        readme_content = f.read()
    if "## Dataset Summary" not in readme_content:
        readme_content = readme_content.replace("## Research Questions Addressed", dataset_summary + "\n## Research Questions Addressed")
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print("Added Dataset Summary to README.md")

    # Report specific updates
    report_path = "data/reports/blinkit_discovery_report.md"
    with open(report_path, 'r', encoding='utf-8') as f:
        report_content = f.read()

    # Soften causal statements
    report_content = report_content.replace(
        "Users tend to buy from the same categories because they are familiar with the products",
        "The available evidence suggests users tend to buy from the same categories because they are familiar with the products"
    )
    report_content = report_content.replace(
        "Some users are prevented from exploring new categories because",
        "Reviews indicate some users are prevented from exploring new categories because"
    )
    report_content = report_content.replace(
        "Users currently discover products through browsing",
        "A recurring pattern observed is that users currently discover products through browsing"
    )
    report_content = report_content.replace(
        "Users need reassurance about the availability",
        "The available evidence suggests users need reassurance about the availability"
    )
    report_content = report_content.replace(
        "Users who are looking for convenience",
        "Reviews indicate users who are looking for convenience"
    )
    report_content = report_content.replace(
        "Unmet needs include the desire for",
        "A recurring pattern observed is that unmet needs include the desire for"
    )
    report_content = report_content.replace(
        "Users repeatedly buy from the same categories because of",
        "The available evidence suggests users repeatedly buy from the same categories because of"
    )
    report_content = report_content.replace(
        "High prices compared to local stores and other competing apps prevent users",
        "Reviews indicate high prices compared to local stores and other competing apps prevent users"
    )
    report_content = report_content.replace(
        "Users discover products through the app's",
        "A recurring pattern observed is that users discover products through the app's"
    )
    report_content = report_content.replace(
        "Users need competitive pricing and a wide range",
        "The available evidence suggests users need competitive pricing and a wide range"
    )
    
    # Executive Summary Rewrite
    old_exec_summary = """## 1. Executive Summary
**Methodology:** 10000 raw Play Store reviews → 4281 cleaned reviews → dual pipeline.
The dual pipeline consists of a full-dataset operational analysis, and a keyword-filtered discovery analysis which isolated 125 reviews and identified 5 specific discovery clusters.

**Top-line Finding:**
While the vast majority of Blinkit reviews revolve around operational logistics (delivery speed, pricing, and refunds), a distinct subset of users are actively trying to discover new categories but are blocked by limited assortment, poor search discovery, and lack of competitive pricing/reviews. Users are habitual in their core categories but desire a wider catalog (like beauty, niche items like yarn) if trust and pricing barriers can be overcome."""
    
    new_exec_summary = """## 1. Executive Summary
**Methodology:** Our Dual-Source AI Discovery Engine analyzed a massive scale of data to generate early product hypotheses: 10,000 raw Play Store reviews (filtered down to 4,281 cleaned reviews, yielding 125 high-intent discovery reviews across 5 clusters) and 134 curated community discussions.

**Top-line AI-generated Hypothesis:**
While the vast majority of Blinkit feedback revolves around operational logistics (delivery speed, pricing, and refunds), the available evidence suggests a distinct subset of users are actively trying to discover new categories. However, reviews indicate they are blocked by limited assortment, poor search discovery, and a lack of competitive pricing or trust markers. The recurring pattern observed is that users are habitual in their core categories but desire a wider catalog (e.g., beauty, niche items) if trust and pricing barriers can be overcome. **These AI-generated hypotheses will serve as critical inputs for Part 2 primary user interviews to validate the underlying user friction.**"""
    
    report_content = report_content.replace(old_exec_summary, new_exec_summary)

    # Insert Dataset Summary after Exec Summary in Report
    if "## Dataset Summary" not in report_content:
        report_content = report_content.replace(
            "## 2. Category Discovery Insights", 
            dataset_summary + "\n## 2. Category Discovery Insights"
        )
        print("Added Dataset Summary to Report")

    # Add Key Takeaways at the end
    key_takeaways = """
## 6. Key Takeaways & Prioritized Hypotheses
*The following AI-generated product hypotheses are ranked by potential business impact for cross-category growth. These will be directly validated in Part 2 user interviews.*

1. **Hypothesis 1 (Trust & Authenticity as a Blocker):** Users hesitate to buy high-value or personal care items (e.g., beauty, electronics) because they doubt product authenticity and face difficult return processes compared to Amazon/Flipkart.
2. **Hypothesis 2 (Assortment & Search Friction):** Users are willing to explore new categories, but often abandon the intent because of limited brand variety and a search experience optimized for known grocery items rather than discovery.
3. **Hypothesis 3 (Price Perception outside Groceries):** Users perceive Blinkit as a premium-priced option for non-grocery items, requiring clear competitive pricing or discounting to break their habitual reliance on local stores.
4. **Hypothesis 4 (Quality Assurance Need):** The lack of detailed product information and user reviews on Blinkit creates a high barrier to entry for unfamiliar categories where quality verification is paramount.
"""
    if "## 6. Key Takeaways" not in report_content:
        report_content += "\n" + key_takeaways
        print("Added Key Takeaways to Report")

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
        
if __name__ == "__main__":
    main()
