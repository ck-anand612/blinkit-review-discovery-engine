import json
import logging
from datetime import datetime
from blinkit.models import Review
from blinkit.summarize import summarize_cluster

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_clusters(filepath: str, target_ranks: list):
    """Parse clusters_utf8.txt and extract reviews for target ranks."""
    clusters = {rank: [] for rank in target_ranks}
    current_rank = None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith("[Cluster Rank"):
                try:
                    rank_str = line.split(" ")[2].replace("]", "")
                    current_rank = int(rank_str)
                except:
                    current_rank = None
            elif line.startswith("-") and current_rank in target_ranks:
                text = line[1:].strip()
                clusters[current_rank].append(text)
                
    return clusters

if __name__ == "__main__":
    target_ranks = [3, 8, 11, 12]
    print(f"Loading clusters {target_ranks} from clusters_utf8.txt...")
    
    cluster_texts = parse_clusters('clusters_utf8.txt', target_ranks)
    
    for rank in target_ranks:
        texts = cluster_texts[rank]
        if not texts:
            print(f"\n[Warning] No reviews found for Cluster Rank {rank}")
            continue
            
        print(f"\n========================================")
        print(f"SUMMARIZING CLUSTER RANK {rank} ({len(texts)} snippets)")
        print(f"========================================")
        
        # Build mock reviews
        reviews = [
            Review(
                id=f"mock_{rank}_{i}",
                text=t,
                rating=None,
                date=datetime.now(),
                source="play_store"
            ) for i, t in enumerate(texts)
        ]
        
        # Call Groq
        insight = summarize_cluster(reviews)
        
        # Print full JSON output
        print(insight.model_dump_json(indent=2))
