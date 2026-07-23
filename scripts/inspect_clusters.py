import logging
from blinkit.ingest.play_store import fetch_play_store_reviews
from blinkit.clean import clean_and_normalize
from blinkit.analysis.embeddings import generate_embeddings
from blinkit.analysis.reduce import reduce_dimensions
from blinkit.analysis.cluster import run_clustering, build_clusters

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
    print("Fetching ~2000 Play Store reviews...")
    raw_reviews = fetch_play_store_reviews(count=2000)
    cleaned_reviews = clean_and_normalize(raw_reviews, min_length=15)
    
    if len(cleaned_reviews) > 0:
        embeddings = generate_embeddings(cleaned_reviews)
        reduced = reduce_dimensions(embeddings)
        labels = run_clustering(reduced)
        
        # Get ALL clusters (up to 50)
        all_clusters, noise_count = build_clusters(cleaned_reviews, labels, top_k=50)
        
        print("\n=== ALL CLUSTERS ===")
        review_dict = {r.id: r for r in cleaned_reviews}
        
        for c in all_clusters:
            print(f"\n[Cluster Rank {c.rank}] - Size: {c.size} reviews")
            
            # Print up to 15 snippets to manually inspect for discovery/category themes
            sample_ids = c.review_ids[:15]
            for r_id in sample_ids:
                safe_text = review_dict[r_id].text.encode('ascii', 'ignore').decode('ascii').replace('\n', ' ')
                print(f"  - {safe_text}")
