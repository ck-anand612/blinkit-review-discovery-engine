import csv
import json
import os
from datetime import datetime
from blinkit.models import Review
from blinkit.summarize import summarize_cluster
from dotenv import load_dotenv

load_dotenv()

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
        # Ignore empty strings or malformed rows
        if r['url'] or r['text']:
            key = (r['url'], r['text'])
            if key not in unique_reviews:
                unique_reviews[key] = r
            
    deduped = list(unique_reviews.values())
    print(f"Total deduplicated reviews: {len(deduped)}")
    
    # Convert to Review objects
    review_objs = []
    for i, r in enumerate(deduped):
        review_objs.append(Review(
            id=f"reddit_{i}",
            text=r['text'],
            rating=None,
            date=datetime.now(),
            source=r['source']
        ))
        
    # Chunk into 50s because summarize_cluster takes sample_reviews = reviews[:50]
    chunk_size = 50
    chunks = [review_objs[i:i + chunk_size] for i in range(0, len(review_objs), chunk_size)]
    
    insights = []
    for idx, chunk in enumerate(chunks):
        print(f"Summarizing chunk {idx+1}/{len(chunks)} with {len(chunk)} reviews...")
        insight = summarize_cluster(chunk)
        insights.append(insight.model_dump())
        
    with open("community_insights_raw.json", "w", encoding="utf-8") as f:
        json.dump(insights, f, indent=2)
        
    print("Summarization complete. Insights saved to community_insights_raw.json.")

if __name__ == "__main__":
    main()
