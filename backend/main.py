import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

try:
    from backend.models import Movie, MovieListResponse, RecommendationResponse, HealthResponse
    from backend.recommender import MovieRecommender
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "dataset", "movies_features.csv")
recommender = MovieRecommender(DATA_PATH)


@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Welcome to CineX Movie Recommendation API",
        "version": "2.0.0",
        "docs": "/docs",
        "status": "online",
        "tmdb_connected": tmdb_service.is_configured(),
        "total_movies": len(recommender.movies)
    }


@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    return HealthResponse(
        status="healthy",
        version="2.0.0",
        movies_count=len(recommender.movies)
    )


@app.get("/api/movies", response_model=List[Movie], tags=["Movies"])
def get_movies(
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


@app.get("/api/movies/{movie_id}", response_model=Movie, tags=["Movies"])
def get_movie_by_id(movie_id: int):
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
    Step 1: If movie is in local KNN dataset -> run KNN recommendations.
    Step 2: If movie is NEW / TMDB-only (not in local dataset) -> dynamically extract TMDB metadata,
            transform with existing tfidf_vectorizer.pkl (NO retraining), and compute nearest KNN neighbors.
    Step 3: Guarantees the target movie itself is NEVER recommended.
    Step 4: Enriches each recommended movie with dynamic TMDB metadata (posters, backdrops, trailers, cast, streaming).
    """
    target_idx: Optional[int] = None
    target_movie_title: str = ""
    tmdb_details: Optional[dict] = None

    # 1. Check local ML dataset by ID
    if movie_id in recommender.indices_map:
        target_idx = recommender.indices_map[movie_id]
        target_movie = recommender.movies[target_idx]
        target_movie_title = target_movie.get("title", "")
    elif tmdb_service.is_configured():
        # Fetch TMDB details for the ID
        tmdb_details = tmdb_service.get_movie_details(movie_id)
        if tmdb_details:
            target_movie_title = tmdb_details.get("title", "")
            # Check if title exists in local dataset with high confidence
            target_idx = recommender.find_movie(target_movie_title, min_similarity=0.88)

    raw_recommendations: List[dict] = []

    if target_idx is not None:
        # Existing movie in KNN dataset
        target_movie = recommender.movies[target_idx]
        raw_recommendations = recommender.get_recommendations(target_movie["id"], top_n=limit)
    elif tmdb_details:
        # NEW MOVIE RELEASE (exists in TMDB, not in static ML dataset)
        # Uses existing TF-IDF vectorizer + KNN cosine distance fallback
        raw_recommendations = recommender.recommend_for_new_movie(tmdb_details, top_n=limit)
    else:
        # Fallback to top-rated
        raw_recommendations = recommender.get_top_rated(limit=limit)

    # SAFETY CHECK: Ensure target movie is NEVER in recommendations
    clean_target_norm = recommender.normalize_text(target_movie_title)
    safe_recommendations = []
    seen_titles = {clean_target_norm} if clean_target_norm else set()
    seen_ids = {str(movie_id)}

    for rec in raw_recommendations:
        rec_id_str = str(rec.get("id") or rec.get("movie_id"))
        rec_norm = recommender.normalize_text(rec.get("title", ""))

        if rec_norm in seen_titles or rec_id_str in seen_ids:
            continue

        seen_titles.add(rec_norm)
        seen_ids.add(rec_id_str)
        safe_recommendations.append(rec)
        if len(safe_recommendations) >= limit:
            break

    # Enrich recommendations with TMDB metadata
    return tmdb_service.enrich_movies_batch(safe_recommendations)


@app.get("/api/search", response_model=List[Movie], tags=["Search"])
def search_movies(
    q: str = Query("", description="Search term across titles, actors, directors, genres"),
    limit: int = Query(50, ge=1, le=100)
):
    """
    Smart Search with Spelling & Typo Tolerance:
    Search priority:
    1. Exact title
    2. Very close spelling match (fuzzy string similarity)
    3. Partial title / token match
    4. Relevant TMDB results
    """
    q_str = q.strip() if isinstance(q, str) else ""
    lim = limit if isinstance(limit, int) else 50

    if not q_str:
        return get_trending(limit=lim)

    # 1. Run local smart fuzzy search on ML dataset
    local_results = recommender.search_movies(q_str, limit=lim)

    # 2. If TMDB is configured, fetch TMDB live search results
    tmdb_results: List[dict] = []
    if tmdb_service.is_configured():
        tmdb_results = tmdb_service.search_tmdb(q_str, limit=lim)

    # If no TMDB configured, return enriched local results
    if not tmdb_results:
        return tmdb_service.enrich_movies_batch(local_results)

    # 3. Merge and rank results according to search priority
    q_norm = recommender.normalize_text(q_str)
    merged_results: List[dict] = []
    seen_titles = set()
    seen_ids = set()

    def get_match_score(m: dict) -> float:
        t_norm = recommender.normalize_text(m.get("title", ""))
        score = 0.0
        if t_norm == q_norm:
            score += 1000.0
        elif t_norm.startswith(q_norm):
            score += 500.0
        elif q_norm in t_norm:
            score += 300.0

        ratio = recommender.calculate_similarity_ratio(q_norm, t_norm)
        if ratio >= 0.85:
            score += 400.0 * ratio
        elif ratio >= 0.70:
            score += 250.0 * ratio

        # Popularity / Rating small tie-breaker
        score += float(m.get("rating", 0.0) or 0.0) * 0.5
        score += float(m.get("popularity", 0.0) or 0.0) * 0.05
        return score

    # Combine candidates from both local dataset and TMDB
    # Enrich top local results so they have proper posters/backdrops
    enriched_local = tmdb_service.enrich_movies_batch(local_results[:15])
    all_candidates = enriched_local + tmdb_results

    # Sort all candidates by relevance score
    all_candidates.sort(key=get_match_score, reverse=True)

    for movie in all_candidates:
        m_title_norm = recommender.normalize_text(movie.get("title", ""))
        m_id_str = str(movie.get("id") or movie.get("tmdb_id") or movie.get("movie_id"))

        if m_title_norm in seen_titles or m_id_str in seen_ids:
            continue

        seen_titles.add(m_title_norm)
        seen_ids.add(m_id_str)
        merged_results.append(movie)

        if len(merged_results) >= lim:
            break

    return merged_results


@app.get("/api/genres", response_model=List[str], tags=["Metadata"])
def get_genres():
    return recommender.get_genres()


@app.get("/api/languages", response_model=List[str], tags=["Metadata"])
def get_languages():
    return recommender.get_languages()
