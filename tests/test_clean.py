import logging
from blinkit.ingest.play_store import fetch_play_store_reviews
from blinkit.clean import clean_and_normalize

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
    print("Fetching ~2000 Play Store reviews...")
    raw_reviews = fetch_play_store_reviews(count=2000)
    
    print(f"\nTotal raw reviews fetched: {len(raw_reviews)}")
    
    cleaned_reviews = clean_and_normalize(raw_reviews, min_length=15)
    
    filtered_out = len(raw_reviews) - len(cleaned_reviews)
    print(f"Total reviews after cleaning: {len(cleaned_reviews)}")
    print(f"Reviews filtered out (noise/duplicates): {filtered_out}")
    
    print("\n--- SAMPLE CLEANED REVIEWS ---")
    for i, r in enumerate(cleaned_reviews[:5]):
        print(f"[{i+1}] Rating: {r.rating}/5 | ID: {r.id}")
        # Encode and decode to safely print emojis to Windows console
        safe_text = r.text.encode('ascii', 'ignore').decode('ascii')
        print(f"Text: {safe_text}\n")
