import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

try:
    from backend.models import Movie, MovieListResponse, RecommendationResponse, HealthResponse
    from backend.recommender import MovieRecommender
except ImportError:
    from models import Movie, MovieListResponse, RecommendationResponse, HealthResponse
    from recommender import MovieRecommender

app = FastAPI(
    title="CineX Movie Recommendation API",
    description="Backend API for CineX Movie Discovery and Recommendation Platform",
    version="1.0.0"
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "movies.json")
recommender = MovieRecommender(DATA_PATH)


@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Welcome to CineX Movie Recommendation API",
        "docs": "/docs",
        "status": "online"
    }


@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        movies_count=len(recommender.movies)
    )


@app.get("/api/movies", response_model=List[Movie], tags=["Movies"])
def get_movies(
    genre: Optional[str] = Query(None, description="Filter by genre"),
    language: Optional[str] = Query(None, description="Filter by language"),
    sort_by: Optional[str] = Query("default", description="Sort order: rating, year, title")
):
    movies = recommender.get_all(genre=genre, language=language)
    if sort_by == "rating":
        movies = sorted(movies, key=lambda m: m.get("rating", 0), reverse=True)
    elif sort_by == "year":
        movies = sorted(movies, key=lambda m: m.get("year", 0), reverse=True)
    elif sort_by == "title":
        movies = sorted(movies, key=lambda m: m.get("title", ""))
    return movies


@app.get("/api/movies/trending", response_model=List[Movie], tags=["Movies"])
def get_trending():
    return recommender.movies[:8]


@app.get("/api/movies/top-rated", response_model=List[Movie], tags=["Movies"])
def get_top_rated():
    return sorted(recommender.movies, key=lambda m: m.get("rating", 0), reverse=True)


@app.get("/api/movies/tamil", response_model=List[Movie], tags=["Movies"])
def get_tamil_movies():
    return [m for m in recommender.movies if m.get("language") == "Tamil"]


@app.get("/api/movies/{movie_id}", response_model=Movie, tags=["Movies"])
def get_movie_by_id(movie_id: int):
    if movie_id not in recommender.movie_map:
        raise HTTPException(status_code=404, detail="Movie not found")
    return recommender.movie_map[movie_id]


@app.get("/api/movies/{movie_id}/recommendations", response_model=List[Movie], tags=["Recommendations"])
def get_recommendations(movie_id: int, limit: int = Query(6, ge=1, le=20)):
    if movie_id not in recommender.movie_map:
        raise HTTPException(status_code=404, detail="Target movie not found")
    
    recommendations = recommender.get_recommendations(movie_id, top_n=limit)
    return recommendations


@app.get("/api/search", response_model=List[Movie], tags=["Search"])
def search_movies(q: str = Query("", description="Search term")):
    return recommender.search_movies(q)


@app.get("/api/genres", response_model=List[str], tags=["Metadata"])
def get_genres():
    genres_set = set()
    for m in recommender.movies:
        for g in m.get("genres", []):
            genres_set.add(g)
    return sorted(list(genres_set))


@app.get("/api/languages", response_model=List[str], tags=["Metadata"])
def get_languages():
    languages_set = set(m.get("language", "") for m in recommender.movies if m.get("language"))
    return sorted(list(languages_set))
