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
    language: str
    genres: List[str]
    runtime: str
    overview: str
    tagline: str = ""
    director: str
    poster: str
    backdrop: str
    trailerId: str
    cast: List[CastMember] = Field(default_factory=list)
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
