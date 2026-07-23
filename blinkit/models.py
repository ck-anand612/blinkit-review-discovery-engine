from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class Review(BaseModel):
    id: str = Field(
        description="Unique identifier for the review (e.g., Play Store review ID or Reddit post/comment ID)")
    text: str = Field(description="The normalized text content of the review")
    rating: Optional[int] = Field(
        None, description="Rating from 1-5 (applicable for Play Store, null for Reddit)")
    date: datetime = Field(description="Date the review was posted")
    source: str = Field(
        description="Source of the review, typically 'play_store'")


class Cluster(BaseModel):
    rank: int = Field(
        description="The assigned rank of the cluster based on importance (1 is highest)")
    size: int = Field(description="Number of reviews in this cluster")
    average_rating: Optional[float] = Field(
        None, description="Average rating of reviews in this cluster, if applicable")
    earliest_date: datetime = Field(
        description="Date of the oldest review in this cluster")
    latest_date: datetime = Field(
        description="Date of the newest review in this cluster")
    review_ids: List[str] = Field(
        description="List of review IDs that belong to this cluster")


class ResearchAnswer(BaseModel):
    question_number: int
    question: str
    answer: str
    evidence_count: int


class Insight(BaseModel):
    theme: str = Field(description="Short PM-focused theme")
    cluster_type: str = Field(description="Discovery | Operational")
    confidence: str = Field(description="High | Medium | Low")
    supported_research_questions: List[ResearchAnswer] = Field(
        description="List of answered research questions")
    representative_quotes: List[str] = Field(
        description="Verbatim quotes extracted from raw reviews")
    pain_points: List[str] = Field(
        description="List of specific pain points mentioned by users")
    pm_opportunities: List[str] = Field(
        description="Concrete product opportunities inferred from evidence")


class ClusterDetail(BaseModel):
    cluster: Cluster
    insight: Insight
    validation_score: Optional[float] = Field(
        None,
        description="LLM validation score (0.0 to 1.0) indicating how well sampled reviews match the theme")
    validation_notes: Optional[str] = Field(
        None, description="LLM feedback on why the validation score was given")


class Report(BaseModel):
    total_reviews_processed: int = Field(
        description="Total number of valid reviews passed into the clustering engine")
    noise_reviews_count: int = Field(
        description="Number of reviews that could not be clustered (noise / -1 cluster)")
    play_store_count: int = Field(
        description="Number of reviews sourced from Google Play Store")
    date_generated: datetime = Field(
        description="Date this report was generated")
    clusters: List[ClusterDetail] = Field(
        description="Detailed insights and metrics for each identified cluster")
