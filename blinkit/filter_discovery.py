import re
from typing import List
from blinkit.models import Review

DISCOVERY_PATTERNS = [
    r"\b(category|categories|section)\b",
    r"\b(explore|discover|browsing|browse|search|find)\b",
    r"\b(wish they had|wish it had|don't have|doesn't have|should add|please add)\b",
    r"\b(only buy|always buy|never tried|never buy|don't buy)\b",
    r"\b(compare|comparison|vs zepto|vs instamart|vs bigbasket|vs jiomart|vs amazon)\b",
    r"\b(variety|range|catalog|collection)\b",
    r"\b(trust|fake|genuine|authentic|quality concern)\b",
    r"\b(electronics|personal care|beauty|pet|baby|yarn|craft|hobby)\b"
]

def filter_discovery_reviews(reviews: List[Review]) -> List[Review]:
    """Filter reviews that match any discovery-related keyword patterns."""
    compiled_patterns = [re.compile(p, re.IGNORECASE) for p in DISCOVERY_PATTERNS]
    
    filtered = []
    for review in reviews:
        text = review.text
        if any(p.search(text) for p in compiled_patterns):
            filtered.append(review)
            
    return filtered
