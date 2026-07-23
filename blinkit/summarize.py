import logging
import json
import os
import re
from typing import List
from groq import Groq
from dotenv import load_dotenv

from blinkit.models import Insight, Review, ResearchAnswer

load_dotenv()
logger = logging.getLogger(__name__)

# System prompt optimized for Blinkit category discovery
SYSTEM_PROMPT = """You are a Senior Product Manager conducting customer discovery for Blinkit's Growth Team.
The goal is NOT to summarize reviews.
The goal is to identify evidence explaining why users do or do not explore new product categories on Blinkit.
The LLM must answer ONLY the research questions that are directly supported by evidence in the cluster.
Never infer, speculate, or invent answers.
If a research question is not supported by the reviews in that cluster, simply omit it.

## Research Questions
1. Why do users repeatedly buy from the same categories?
2. What prevents users from exploring new categories?
3. How do users currently discover products?
4. What role do habits play in shopping behavior?
5. What information or reassurance do users need before trying a new category?
6. What frustrations specifically related to category discovery appear repeatedly?
7. Which user segments appear more willing to experiment with new categories?
8. What unmet needs emerge around product categories?

## Important Rules

First determine whether the cluster is Discovery OR Operational.

A cluster is **Operational** if it mainly discusses:
- delivery delays
- refunds
- payment failures
- customer support
- damaged products
- missing items
- app bugs
and contains NO evidence about category discovery or shopping behaviour.

For Operational clusters:
- Set cluster_type = "Operational"
- Explain briefly why it is not relevant to category discovery in pm_opportunities.
- Do NOT force answers to the research questions.
- Set "supported_research_questions" to an empty array [].
- Still extract useful operational pain points.

A cluster is **Discovery** if it contains ANY evidence (even just one review) about:
- shopping habits
- buying behaviour
- browsing behaviour
- search behaviour
- trying new products
- awareness of categories
- product variety
- trust before purchase
- niche category requests
- comparison with competitors
- category availability

## Output JSON

Return ONLY valid JSON. Do not wrap the JSON in markdown code fences or add any explanatory text before or after it.

{
  "theme": "Short PM-focused theme",
  "cluster_type": "Discovery | Operational",
  "confidence": "High | Medium | Low",
  "supported_research_questions": [
    {
      "question_number": 2,
      "question": "What prevents users from exploring new categories?",
      "answer": "Grounded answer based ONLY on reviews.",
      "evidence_count": 8
    }
  ],
  "representative_quotes": [
    "Exact review text...",
    "Exact review text..."
  ],
  "pain_points": [
    "..."
  ],
  "pm_opportunities": [
    "Concrete product opportunity inferred from the evidence."
  ]
}

## Additional Constraints
- Every answer must be directly supported by the reviews.
- Never hallucinate.
- Never generalize beyond the supplied reviews.
- Quotes must be copied verbatim.
- If confidence is Low, state it — but still include the cluster in the output rather than dropping it; flag it as tentative signal.
- Ignore cluster size when interpreting meaning.
- Think like a Product Manager performing discovery research, not a review summarizer.
"""

def _get_client() -> Groq:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        raise ValueError("GROQ_API_KEY environment variable is not set correctly.")
    return Groq(api_key=api_key)

def summarize_cluster(reviews: List[Review], max_retries: int = 2) -> Insight:
    """Send cluster reviews to Groq LLM to generate an Insight object."""
    if not reviews:
        raise ValueError("Cannot summarize an empty cluster.")
        
    client = _get_client()
    
    # We take up to 50 reviews to ensure we don't miss sparse discovery signals
    sample_reviews = reviews[:50]
    reviews_text = "\n\n".join([f"Review {i+1}: {r.text}" for i, r in enumerate(sample_reviews)])
    
    prompt = f"Analyze the following user reviews:\n\n{reviews_text}"
    logger.info(f"Sending {len(sample_reviews)} reviews to Groq for PM summarization...")
    
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1500,
            )
            
            response_content = completion.choices[0].message.content
            
            # Clean up potential markdown code fences from the LLM output
            cleaned_content = re.sub(r'^```json\s*', '', response_content, flags=re.IGNORECASE)
            cleaned_content = re.sub(r'^```\s*', '', cleaned_content)
            cleaned_content = re.sub(r'\s*```$', '', cleaned_content)
            
            data = json.loads(cleaned_content)
            
            # Build research answers
            answers = []
            for item in data.get("supported_research_questions", []):
                answers.append(ResearchAnswer(
                    question_number=item.get("question_number", 0),
                    question=item.get("question", ""),
                    answer=item.get("answer", ""),
                    evidence_count=item.get("evidence_count", 0)
                ))
            
            insight = Insight(
                theme=data.get("theme", "Unknown Theme"),
                cluster_type=data.get("cluster_type", "Unknown"),
                confidence=data.get("confidence", "Low"),
                supported_research_questions=answers,
                pain_points=data.get("pain_points", []),
                pm_opportunities=data.get("pm_opportunities", []),
                representative_quotes=data.get("representative_quotes", [])
            )
            
            # Simple Quote Validation
            valid_quotes = []
            full_raw_text = " ".join([r.text for r in sample_reviews])
            for q in insight.representative_quotes:
                if q in full_raw_text or q.strip() in full_raw_text:
                    valid_quotes.append(q.strip())
                else:
                    logger.warning(f"Hallucinated quote discarded: {q}")
                        
            insight.representative_quotes = valid_quotes
            return insight
            
        except json.JSONDecodeError as e:
            logger.warning(f"Attempt {attempt + 1}: JSON decode error: {e}. Output was: {response_content[:100]}...")
            last_error = e
        except Exception as e:
            logger.error(f"Error during LLM summarization: {e}")
            last_error = e
            
    # Return fallback on error
    return Insight(
        theme="Summarization Error",
        cluster_type="Operational",
        confidence="Low",
        supported_research_questions=[],
        pain_points=[],
        pm_opportunities=[f"Failed to summarize cluster after retries. Error: {str(last_error)}"],
        representative_quotes=[]
    )
