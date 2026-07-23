import logging
import hashlib
import re
from typing import List

from blinkit.models import Review

logger = logging.getLogger(__name__)

# Regex patterns for PII
PHONE_REGEX = re.compile(r'\b(?:\+?91[\-\s]?)?[6-9]\d{9}\b')
EMAIL_REGEX = re.compile(
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b')
UPI_REGEX = re.compile(r'\b[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}\b')


def scrub_pii(text: str) -> str:
    """Removes sensitive info like phone numbers, emails, and UPI IDs."""
    text = PHONE_REGEX.sub("[PHONE_REDACTED]", text)
    text = EMAIL_REGEX.sub("[EMAIL_REDACTED]", text)
    # Be careful with UPI matching valid emails, but since we scrub email
    # first, this catches remaining upi formats
    text = UPI_REGEX.sub("[UPI_REDACTED]", text)
    return text


def compute_hash(text: str) -> str:
    """Generate MD5 hash for deduplication based on normalized text."""
    # Normalize: lowercase and strip extra whitespace
    normalized = " ".join(text.lower().split())
    return hashlib.md5(normalized.encode('utf-8')).hexdigest()


def clean_and_normalize(
        reviews: List[Review], min_length: int = 15) -> List[Review]:
    """
    Cleans PII, deduplicates by text hash, and filters out noise/short reviews.
    """
    logger.info(f"Starting cleaning for {len(reviews)} reviews...")

    seen_hashes = set()
    cleaned_reviews = []

    for r in reviews:
        # Scrub PII
        scrubbed_text = scrub_pii(r.text)

        # Filter noise (short reviews)
        if len(scrubbed_text.strip()) < min_length:
            continue

        # Deduplicate
        text_hash = compute_hash(scrubbed_text)
        if text_hash in seen_hashes:
            continue

        seen_hashes.add(text_hash)

        # Add to final list with updated text
        # Pydantic models are usually immutable if frozen, but ours aren't, so we can reassign or create new
        # Best practice is to create a copy or just update since we own the
        # object
        r.text = scrubbed_text.strip()
        cleaned_reviews.append(r)

    filtered_count = len(reviews) - len(cleaned_reviews)
    logger.info(
        f"Cleaning complete: {
            len(cleaned_reviews)} reviews kept, {filtered_count} discarded as noise or duplicates.")

    return cleaned_reviews
