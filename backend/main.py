import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

try:
    from backend.models import Movie, MovieListResponse, RecommendationResponse, HealthResponse
    from backend.recommender import MovieRecommender
<<<<<<< HEAD
except ImportError:
    from models import Movie, MovieListResponse, RecommendationResponse, HealthResponse
    from recommender import MovieRecommender

app = FastAPI(
    title="CineX Movie Recommendation API",
    description="Backend API for CineX Movie Discovery and Recommendation Platform",
    version="1.0.0"
)

# Enable CORS for local development
=======
    from backend.tmdb import tmdb_service
except ImportError:
    from models import Movie, MovieListResponse, RecommendationResponse, HealthResponse
    from recommender import MovieRecommender
    from tmdb import tmdb_service

app = FastAPI(
    title="CineX Movie Recommendation API",
    description="Production Machine Learning & Dynamic TMDB Discovery API for CineX Movie Platform",
    version="2.0.0"
)

# Enable CORS for frontend integration
>>>>>>> 12d9995 (feat: CineX ML movie recommendation system with TMDB trailer modal, reviews, and watchlists)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

<<<<<<< HEAD
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "movies.json")
=======
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "dataset", "movies_features.csv")
>>>>>>> 12d9995 (feat: CineX ML movie recommendation system with TMDB trailer modal, reviews, and watchlists)
recommender = MovieRecommender(DATA_PATH)


@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Welcome to CineX Movie Recommendation API",
<<<<<<< HEAD
        "docs": "/docs",
        "status": "online"
=======
        "version": "2.0.0",
        "docs": "/docs",
        "status": "online",
        "tmdb_connected": tmdb_service.is_configured(),
        "total_movies": len(recommender.movies)
>>>>>>> 12d9995 (feat: CineX ML movie recommendation system with TMDB trailer modal, reviews, and watchlists)
    }


@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    return HealthResponse(
        status="healthy",
<<<<<<< HEAD
        version="1.0.0",
=======
        version="2.0.0",
>>>>>>> 12d9995 (feat: CineX ML movie recommendation system with TMDB trailer modal, reviews, and watchlists)
        movies_count=len(recommender.movies)
    )


@app.get("/api/movies", response_model=List[Movie], tags=["Movies"])
def get_movies(
<<<<<<< HEAD
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
=======
    genre: Optional[str] = Query(None, description="Filter by genre (e.g. Action, Drama, Comedy)"),
    language: Optional[str] = Query(None, description="Filter by language (e.g. Tamil, English, Hindi, Telugu)"),
    year_min: Optional[int] = Query(None, description="Minimum release year"),
    year_max: Optional[int] = Query(None, description="Maximum release year"),
    min_rating: Optional[float] = Query(None, description="Minimum IMDb rating (0-10)"),
    sort_by: Optional[str] = Query("popularity", description="Sort by: popularity, rating, revenue, year, title"),
    limit: int = Query(50, ge=1, le=200, description="Number of movies to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    g_val = genre if isinstance(genre, str) else None
    l_val = language if isinstance(language, str) else None
    y_min = year_min if isinstance(year_min, int) else None
    y_max = year_max if isinstance(year_max, int) else None
    r_min = min_rating if isinstance(min_rating, (int, float)) else None
    s_by = sort_by if isinstance(sort_by, str) else "popularity"
    lim = limit if isinstance(limit, int) else 50
    off = offset if isinstance(offset, int) else 0

    raw_movies = recommender.get_all(
        genre=g_val,
        language=l_val,
        year_min=y_min,
        year_max=y_max,
        min_rating=r_min,
        sort_by=s_by,
        limit=lim,
        offset=off
    )
    return tmdb_service.enrich_movies_batch(raw_movies)


@app.get("/api/movies/trending", response_model=List[Movie], tags=["Discovery"])
def get_trending(limit: int = Query(12, ge=1, le=50)):
    lim = limit if isinstance(limit, int) else 12
    if tmdb_service.is_configured():
        tmdb_trending = tmdb_service.get_trending(limit=lim)
        if tmdb_trending:
            return tmdb_trending
    raw = recommender.get_trending(limit=lim)
    return tmdb_service.enrich_movies_batch(raw)


@app.get("/api/movies/now-playing", response_model=List[Movie], tags=["Discovery"])
def get_now_playing(limit: int = Query(12, ge=1, le=50)):
    lim = limit if isinstance(limit, int) else 12
    if tmdb_service.is_configured():
        now_playing = tmdb_service.get_now_playing(limit=lim)
        if now_playing:
            return now_playing
    raw = recommender.get_trending(limit=lim)
    return tmdb_service.enrich_movies_batch(raw)


@app.get("/api/movies/popular", response_model=List[Movie], tags=["Discovery"])
def get_popular(limit: int = Query(12, ge=1, le=50)):
    lim = limit if isinstance(limit, int) else 12
    if tmdb_service.is_configured():
        popular = tmdb_service.get_popular(limit=lim)
        if popular:
            return popular
    raw = recommender.get_trending(limit=lim)
    return tmdb_service.enrich_movies_batch(raw)


@app.get("/api/movies/upcoming", response_model=List[Movie], tags=["Discovery"])
def get_upcoming(limit: int = Query(12, ge=1, le=50)):
    lim = limit if isinstance(limit, int) else 12
    if tmdb_service.is_configured():
        upcoming = tmdb_service.get_upcoming(limit=lim)
        if upcoming:
            return upcoming
    raw = recommender.get_trending(limit=lim)
    return tmdb_service.enrich_movies_batch(raw)


@app.get("/api/movies/top-rated", response_model=List[Movie], tags=["Discovery"])
def get_top_rated(
    limit: int = Query(12, ge=1, le=50),
    language: Optional[str] = Query(None, description="Optional language filter for top-rated")
):
    lim = limit if isinstance(limit, int) else 12
    lang = language if isinstance(language, str) else None
    if tmdb_service.is_configured() and not lang:
        top_tmdb = tmdb_service.get_top_rated(limit=lim)
        if top_tmdb:
            return top_tmdb
    raw = recommender.get_top_rated(limit=lim, language=lang)
    return tmdb_service.enrich_movies_batch(raw)


@app.get("/api/movies/tamil", response_model=List[Movie], tags=["Discovery"])
def get_tamil_movies(
    sort_by: str = Query("popularity", description="Sort order: popularity, rating, revenue, year"),
    limit: int = Query(24, ge=1, le=100)
):
    s_by = sort_by if isinstance(sort_by, str) else "popularity"
    lim = limit if isinstance(limit, int) else 24

    if tmdb_service.is_configured():
        tamil_tmdb = tmdb_service.get_tamil_movies(limit=lim)
        if tamil_tmdb:
            return tamil_tmdb

    raw = recommender.get_tamil_movies(limit=lim, sort_by=s_by)
    return tmdb_service.enrich_movies_batch(raw)


@app.get("/api/movies/box-office", response_model=List[Movie], tags=["Discovery"])
def get_box_office_hits(limit: int = Query(12, ge=1, le=50)):
    lim = limit if isinstance(limit, int) else 12
    raw = recommender.get_all(sort_by="revenue", limit=lim)
    return tmdb_service.enrich_movies_batch(raw)
>>>>>>> 12d9995 (feat: CineX ML movie recommendation system with TMDB trailer modal, reviews, and watchlists)


@app.get("/api/movies/{movie_id}", response_model=Movie, tags=["Movies"])
def get_movie_by_id(movie_id: int):
<<<<<<< HEAD
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
=======
    # 1. Check local ML dataset
    if movie_id in recommender.movie_map:
        local_movie = recommender.movie_map[movie_id]
        return tmdb_service.enrich_movie(local_movie)

    # 2. Check TMDB directly by TMDB ID
    if tmdb_service.is_configured():
        details = tmdb_service.get_movie_details(movie_id)
        if details:
            return details

    raise HTTPException(status_code=404, detail="Movie not found")


@app.get("/api/movies/{movie_id}/recommendations", response_model=List[Movie], tags=["Recommendations"])
def get_recommendations(movie_id: int, limit: int = Query(10, ge=1, le=30)):
    """
    Step 1: KNN computes genuinely nearest movies using TF-IDF cosine distance.
    Step 2: Never recommends the target movie itself.
    Step 3: Enriches each recommended movie with dynamic TMDB metadata (Posters, Trailers, Cast, Providers).
    """
    # Find matching target movie in local dataset or via title search
    target_idx: Optional[int] = None

    if movie_id in recommender.indices_map:
        target_idx = recommender.indices_map[movie_id]
    elif tmdb_service.is_configured():
        # If ID came from TMDB, find corresponding title in recommender
        tmdb_details = tmdb_service.get_movie_details(movie_id)
        if tmdb_details:
            target_idx = recommender.find_movie(tmdb_details["title"])

    if target_idx is None:
        # If target movie couldn't be matched in recommender, fallback to top-rated
        fallback_recs = recommender.get_top_rated(limit=limit)
        return tmdb_service.enrich_movies_batch(fallback_recs)

    target_movie = recommender.movies[target_idx]

    # Run KNN Recommendation
    raw_recommendations = recommender.get_recommendations(target_movie["id"], top_n=limit)

    # Enrich recommendations with TMDB metadata
    enriched_recommendations = tmdb_service.enrich_movies_batch(raw_recommendations)
    return enriched_recommendations


@app.get("/api/search", response_model=List[Movie], tags=["Search"])
def search_movies(
    q: str = Query("", description="Search term across titles, actors, directors, genres"),
    limit: int = Query(50, ge=1, le=100)
):
    q_str = q.strip() if isinstance(q, str) else ""
    lim = limit if isinstance(limit, int) else 50

    if not q_str:
        return get_trending(limit=lim)

    # Prefer TMDB live search when available
    if tmdb_service.is_configured():
        tmdb_results = tmdb_service.search_tmdb(q_str, limit=lim)
        if tmdb_results:
            return tmdb_results

    # Fallback to ML dataset search + TMDB enrichment
    raw_results = recommender.search_movies(q_str, limit=lim)
    return tmdb_service.enrich_movies_batch(raw_results)
>>>>>>> 12d9995 (feat: CineX ML movie recommendation system with TMDB trailer modal, reviews, and watchlists)


@app.get("/api/genres", response_model=List[str], tags=["Metadata"])
def get_genres():
<<<<<<< HEAD
    genres_set = set()
    for m in recommender.movies:
        for g in m.get("genres", []):
            genres_set.add(g)
    return sorted(list(genres_set))
=======
    return recommender.get_genres()
>>>>>>> 12d9995 (feat: CineX ML movie recommendation system with TMDB trailer modal, reviews, and watchlists)


@app.get("/api/languages", response_model=List[str], tags=["Metadata"])
def get_languages():
<<<<<<< HEAD
    languages_set = set(m.get("language", "") for m in recommender.movies if m.get("language"))
    return sorted(list(languages_set))
=======
    return recommender.get_languages()
>>>>>>> 12d9995 (feat: CineX ML movie recommendation system with TMDB trailer modal, reviews, and watchlists)
