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
    print(f"\nProceeding to analysis with {len(cleaned_reviews)} cleaned reviews...")
    
    if len(cleaned_reviews) > 0:
        # Phase 3: Analysis Pipeline
        embeddings = generate_embeddings(cleaned_reviews)
        reduced = reduce_dimensions(embeddings)
        labels = run_clustering(reduced)
        
        top_clusters, noise_count = build_clusters(cleaned_reviews, labels, top_k=6)
        
        print("\n=== CLUSTERING RESULTS ===")
        print(f"Total reviews processed: {len(cleaned_reviews)}")
        print(f"Noise reviews (-1 cluster): {noise_count} ({(noise_count/len(cleaned_reviews))*100:.1f}%)")
        print(f"Number of valid clusters found: {len(top_clusters)}")
        
        print("\n--- TOP CLUSTERS (By Rank) ---")
        # Build an easy lookup dictionary
        review_dict = {r.id: r for r in cleaned_reviews}
        
        for c in top_clusters[:3]:
            print(f"\n[Cluster Rank {c.rank}]")
            print(f"Size: {c.size} reviews")
            if c.average_rating:
                print(f"Average Rating: {c.average_rating:.2f}/5.0")
            print("Sample Snippets:")
            
            # Just grab the first 3 reviews as a sample for printing
            sample_ids = c.review_ids[:3]
            for r_id in sample_ids:
                safe_text = review_dict[r_id].text.encode('ascii', 'ignore').decode('ascii')
                print(f"  - {safe_text[:120]}...")
