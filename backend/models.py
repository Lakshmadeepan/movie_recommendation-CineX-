from typing import List, Optional
from pydantic import BaseModel, Field

class CastMember(BaseModel):
    name: str
    role: str
    photo: str

class StreamingPlatform(BaseModel):
    name: str
    logo: str
    color: str

class Movie(BaseModel):
    id: int
    title: str
    year: int
    rating: float
    votes: Optional[int] = 0
    language: str
    genres: List[str]
    runtime: str
    runtime_minutes: Optional[int] = 120
    overview: str
    tagline: str = ""
    director: str
    poster: str
    backdrop: str
    trailerId: str
    cast: List[CastMember] = Field(default_factory=list)
    budget_crores: Optional[float] = 0.0
    revenue_crores: Optional[float] = 0.0
    popularity: Optional[float] = 0.0
    imdb_id: Optional[str] = ""
    tmdb_id: Optional[int] = None
    original_language: Optional[str] = None
    original_title: Optional[str] = None
    spoken_languages: List[str] = Field(default_factory=list)
    language_match: Optional[bool] = None
    release_date: Optional[str] = ""
    similarity: Optional[float] = None
    status: Optional[str] = "Released"
    rating_source: Optional[str] = "TMDB"
    streaming: List[StreamingPlatform] = Field(default_factory=list)

class MovieListResponse(BaseModel):
    total: int
    movies: List[Movie]

class RecommendationResponse(BaseModel):
    target_movie_id: int
    target_movie_title: str
    recommendations: List[Movie]

class HealthResponse(BaseModel):
    status: str
    version: str
    movies_count: int
