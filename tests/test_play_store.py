import logging
from blinkit.ingest.play_store import fetch_play_store_reviews

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
    print("Testing Play Store Scraper for Blinkit (com.grofers.customerapp)...")
    reviews = fetch_play_store_reviews(count=150)
    
    print(f"\nSuccessfully fetched {len(reviews)} reviews.")
    
    if reviews:
        print("\n--- SAMPLE REVIEWS ---")
        for i, r in enumerate(reviews[:5]):
            print(f"[{i+1}] Rating: {r.rating}/5 | Date: {r.date.date()}")
            print(f"Text: {r.text[:150]}...\n")
