import logging
from typing import List
from google_play_scraper import Sort, reviews as gps_reviews

from blinkit.models import Review

logger = logging.getLogger(__name__)


def fetch_play_store_reviews(
    app_id: str = "com.grofers.customerapp",
    count: int = 200,
    lang: str = "en",
    country: str = "in"
) -> List[Review]:
    """
    Fetch reviews from the Play Store and normalize them to Review models.
    """
    logger.info(f"Fetching up to {count} reviews for {app_id}...")

    fetched_reviews: List[Review] = []
    continuation_token = None

    # Calculate how many batches to fetch (count per page is up to 199 in gps)
    # gps_reviews fetches a specific count but we can just ask for `count` directly,
    # it handles pagination internally up to a certain point, or we can just
    # paginate manually.

    # Actually, google_play_scraper's `reviews` function handles pagination
    # and we can just request the desired count directly. Let's do it in batches
    # to be safe if the count is large, but for 200 it's fine.

    while len(fetched_reviews) < count:
        batch_size = min(199, count - len(fetched_reviews))
        if batch_size <= 0:
            break

        try:
            result, continuation_token = gps_reviews(
                app_id,
                lang=lang,
                country=country,
                sort=Sort.NEWEST,
                count=batch_size,
                continuation_token=continuation_token,
            )
        except Exception as exc:
            logger.warning("Scraper error: %s", exc)
            break

        if not result:
            logger.info("No more reviews returned from Play Store.")
            break

        for item in result:
            review_text = item.get("content", "").strip()

            # Simple pre-filter for completely empty texts
            if not review_text:
                continue

            fetched_reviews.append(
                Review(
                    id=item["reviewId"],
                    text=review_text,
                    rating=item["score"],
                    date=item["at"],
                    source="play_store"
                )
            )

        if not continuation_token:
            break

    logger.info(
        f"Successfully fetched {
            len(fetched_reviews)} reviews from Play Store.")
    return fetched_reviews[:count]
