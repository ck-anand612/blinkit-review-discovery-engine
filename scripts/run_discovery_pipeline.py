import logging
import sys
from blinkit.ingest.play_store import fetch_play_store_reviews
from blinkit.clean import clean_and_normalize
from blinkit.filter_discovery import filter_discovery_reviews
from blinkit.analysis.embeddings import generate_embeddings
from blinkit.analysis.reduce import reduce_dimensions
from blinkit.analysis.cluster import run_clustering, build_clusters
from blinkit.summarize import summarize_cluster
from blinkit.models import Review

# Fix Windows console unicode printing errors
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
    print("Fetching up to 10000 Play Store reviews...")
    raw_reviews = fetch_play_store_reviews(count=10000)
    cleaned_reviews = clean_and_normalize(raw_reviews, min_length=15)
    print(f"Total cleaned reviews: {len(cleaned_reviews)}")
    
    discovery_reviews = filter_discovery_reviews(cleaned_reviews)
    print(f"Filtered discovery reviews: {len(discovery_reviews)}")
    
    if len(discovery_reviews) > 0:
        embeddings = generate_embeddings(discovery_reviews)
        reduced = reduce_dimensions(embeddings)
        
        # We lower min_cluster_size because the subset is much smaller
        labels = run_clustering(reduced, min_cluster_size=7, min_samples=3)
        
        all_clusters, noise_count = build_clusters(discovery_reviews, labels, top_k=20)
        
        print("\n=== DISCOVERY CLUSTERS ===")
        review_dict = {r.id: r for r in discovery_reviews}
        
        for c in all_clusters:
            print(f"\n========================================")
            print(f"SUMMARIZING CLUSTER RANK {c.rank} (Size: {c.size})")
            print(f"========================================")
            
            cluster_reviews = [review_dict[r_id] for r_id in c.review_ids]
            
            print("Samples:")
            for r in cluster_reviews[:3]:
                print(f"  - {r.text.encode('ascii', 'ignore').decode('ascii').replace(chr(10), ' ')}")
            
            insight = summarize_cluster(cluster_reviews)
            print("\nJSON SUMMARY:")
            print(insight.model_dump_json(indent=2))
