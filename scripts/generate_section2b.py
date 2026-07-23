import json
import csv

file1 = "data/raw/community_comments/Blinkit_User_Comments_Verbatim.csv"
file2 = "data/raw/community_comments/user_comments.csv"

def load_reviews(filename):
    reviews = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                reviews.append({
                    "url": row.get("url", ""),
                    "text": row.get("text", ""),
                    "source": row.get("source", "Reddit")
                })
    except Exception as e:
        print(f"Error loading {filename}: {e}")
    return reviews

def main():
    r1 = load_reviews(file1)
    r2 = load_reviews(file2)
    all_reviews = r1 + r2
    
    unique_reviews = {}
    for r in all_reviews:
        if r['url'] or r['text']:
            key = (r['url'], r['text'])
            if key not in unique_reviews:
                unique_reviews[key] = r
                
    deduped = list(unique_reviews.values())
    
    with open("community_insights_raw.json", "r", encoding="utf-8") as f:
        insights = json.load(f)
        
    md = []
    md.append("## Section 2B: Supplementary Community Research Findings\n")
    md.append("The following insights were extracted directly from curated Reddit and forum comments discussing Blinkit, focusing on category discovery, trust, and shopping habits.\n")
    
    for i, insight in enumerate(insights):
        md.append(f"### Theme: {insight['theme']} ({insight['cluster_type']})")
        
        if insight.get('supported_research_questions'):
            md.append("\n**Key Findings:**")
            for q in insight['supported_research_questions']:
                md.append(f"- **{q['question']}**\n  {q['answer']}")
                
        if insight.get('pain_points'):
            md.append("\n**Pain Points:**")
            for pp in insight['pain_points']:
                md.append(f"- {pp}")
                
        if insight.get('pm_opportunities'):
            md.append("\n**PM Opportunities:**")
            for opp in insight['pm_opportunities']:
                md.append(f"- {opp}")
                
        if insight.get('representative_quotes'):
            md.append("\n**Representative Quotes:**")
            for q in insight['representative_quotes']:
                # Find matching URL
                matched_url = None
                for r in deduped:
                    if q in r['text'] or q.strip() in r['text'] or r['text'] in q:
                        matched_url = r['url']
                        break
                
                if matched_url:
                    md.append(f"- > \"{q}\" — [Source]({matched_url})")
                else:
                    # Try a more fuzzy match
                    for r in deduped:
                        if q[:20] in r['text'] or q[-20:] in r['text']:
                            matched_url = r['url']
                            break
                    if matched_url:
                        md.append(f"- > \"{q}\" — [Source]({matched_url})")
                    else:
                        md.append(f"- > \"{q}\"")
        md.append("\n---\n")
        
    with open("section_2b_draft.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md))
        
if __name__ == "__main__":
    main()
