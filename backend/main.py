import os
import time
from typing import List, Optional, Dict, Tuple
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


@app.api_route("/", methods=["GET", "HEAD"], tags=["Root"])
def root():
    return {
        "message": "Welcome to CineX Movie Recommendation API",
        "version": "2.0.0",
        "docs": "/docs",
        "status": "online",
        "tmdb_connected": tmdb_service.is_configured(),
        "total_movies": len(recommender.movies)
    }


@app.api_route("/health", methods=["GET", "HEAD"], response_model=HealthResponse, tags=["Health"])
@app.api_route("/api/health", methods=["GET", "HEAD"], response_model=HealthResponse, tags=["Health"])
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
    # 1. Check TMDB directly by TMDB ID (standard frontend ID)
    if tmdb_service.is_configured():
        details = tmdb_service.get_movie_details(movie_id)
        if details:
            return details

    # 2. Check local ML dataset
    if movie_id in recommender.movie_map:
        local_movie = recommender.movie_map[movie_id]
        return tmdb_service.enrich_movie(local_movie)

    raise HTTPException(status_code=404, detail="Movie not found")


_recommendations_cache: Dict[str, Tuple[float, List[dict]]] = {}
_search_endpoint_cache: Dict[str, Tuple[float, List[dict]]] = {}
CACHE_TTL = 1800  # 30 minutes


@app.get("/api/movies/{movie_id}/recommendations", response_model=List[Movie], tags=["Recommendations"])
def get_recommendations(movie_id: int, limit: int = Query(10, ge=1, le=30)):
    """
    Intelligent Language-Aware Recommendation Pipeline:
    1. Resolve target movie language (Tamil -> ta, English -> en, Telugu -> te, Hindi -> hi) and metadata.
    2. Retrieve high-quality candidates from local KNN and/or TMDB discovery endpoints.
    3. Validate every candidate on TMDB (original_language, genres, title, release date, poster).
    4. Apply multi-factor language-aware ranking:
       Final Score = ML Similarity + Language Priority Bonus + Genre Synergy + Director/Cast Affinity.
       Tamil target -> Maximum relevant Tamil movies.
       English target -> Prioritizes relevant English movies.
    5. Deduplicate by TMDB ID and normalized title.
    6. Strict self-exclusion of target movie.
    7. Return clean, unique recommendations with genuine ML similarity.
    """
    cache_key = f"rec_{movie_id}_{limit}"
    now = time.time()
    if cache_key in _recommendations_cache:
        ts, cached = _recommendations_cache[cache_key]
        if now - ts < CACHE_TTL:
            return cached

    target_idx: Optional[int] = None
    target_movie: Optional[dict] = None
    target_movie_title: str = ""
    target_tmdb_id: Optional[int] = None
    tmdb_details: Optional[dict] = None
    target_lang = ""
    target_orig_lang = ""

    # 1. Primary: Resolve TMDB details by ID (standard frontend movie_id is TMDB ID)
    if tmdb_service.is_configured():
        target_tmdb_id = movie_id
        tmdb_details = tmdb_service.get_movie_details(movie_id)
        if tmdb_details:
            target_movie_title = tmdb_details.get("title", "")
            target_lang = tmdb_details.get("language", "")
            target_orig_lang = tmdb_details.get("original_language", "")
            # Check if matching movie exists in local dataset with language & year alignment
            target_idx = recommender.find_movie(
                target_movie_title,
                min_similarity=0.90,
                language=target_lang,
                year=tmdb_details.get("year")
            )
            if target_idx is not None:
                target_movie = recommender.movies[target_idx]

    # 1b. Fallback: Check local ML dataset by ID if TMDB details were not found
    if target_movie is None and movie_id in recommender.indices_map:
        target_idx = recommender.indices_map[movie_id]
        target_movie = recommender.movies[target_idx]
        target_movie_title = target_movie.get("title", "")
        target_lang = target_movie.get("language", "")
        lang_to_code = {"tamil": "ta", "telugu": "te", "malayalam": "ml", "hindi": "hi", "kannada": "kn", "english": "en"}
        target_orig_lang = lang_to_code.get(target_lang.lower(), "")

    raw_candidates: List[dict] = []
    is_tmdb_fallback = False

    if target_idx is not None and target_movie:
        # Existing movie in local KNN dataset: fetch 2x candidate pool for language filtering & deduplication
        raw_candidates = recommender.get_recommendations(target_movie["id"], top_n=max(limit * 2, 20))
    elif tmdb_details:
        # Movie exists on TMDB but NOT in local ML dataset: Use TMDB Discovery + Dynamic Feature Space KNN
        is_tmdb_fallback = True
        tmdb_recs = tmdb_service.get_tmdb_fallback_recommendations(movie_id, limit=limit * 2)
        dynamic_knn = recommender.recommend_for_new_movie(tmdb_details, top_n=limit * 2)
        raw_candidates = tmdb_recs + dynamic_knn
    else:
        # Final fallback to top rated movies
        raw_candidates = recommender.get_top_rated(limit=limit * 2)

    # 2. Enrich candidates with TMDB metadata & perform post-enrichment deduplication
    enriched_candidates = tmdb_service.enrich_movies_batch(raw_candidates, deduplicate=True)

    # 3. Dynamic Language-Aware Multi-Factor Ranking
    t_orig = target_orig_lang.lower() if target_orig_lang else ""
    t_lang = target_lang.lower() if target_lang else ""
    is_target_tamil = t_orig == "ta" or t_lang == "tamil"
    is_target_indian = is_target_tamil or t_orig in {"te", "hi", "ml", "kn"} or t_lang in {"telugu", "hindi", "malayalam", "kannada"}

    t_dir = ""
    if target_movie:
        t_dir = str(target_movie.get("director", "")).strip().lower()
    elif tmdb_details:
        t_dir = str(tmdb_details.get("director", "")).strip().lower()

    t_genres = set()
    if target_movie:
        t_genres = set((g if isinstance(g, str) else g.get("name", "")).lower() for g in target_movie.get("genres", []))
    elif tmdb_details:
        t_genres = set(g.lower() for g in tmdb_details.get("genres", []))

    def compute_final_ranking(m: dict) -> float:
        base_sim = float(m.get("similarity") or 0.0)
        score = base_sim * 0.45

        cand_orig = (m.get("original_language") or "").lower()
        cand_lang = (m.get("language") or "").lower()
        spoken = [str(s).lower() for s in m.get("spoken_languages", [])]

        is_cand_tamil = cand_orig == "ta" or cand_lang == "tamil" or "ta" in spoken or "tamil" in spoken
        is_cand_indian = is_cand_tamil or cand_orig in {"te", "hi", "ml", "kn"} or cand_lang in {"telugu", "hindi", "malayalam", "kannada"}
        is_same_lang = (
            (t_orig and cand_orig == t_orig) or
            (t_lang and cand_lang == t_lang) or
            (is_target_tamil and is_cand_tamil)
        )

        m["language_match"] = is_same_lang

        # 1. Language Prioritization
        if is_target_tamil:
            if is_cand_tamil:
                score += 0.55  # Significant priority for Tamil movies
            elif is_cand_indian:
                score += 0.18  # Regional Indian neighbor
            else:
                score -= 0.15  # Deprioritize unrelated Western films
        elif is_same_lang:
            score += 0.50
        elif is_target_indian and is_cand_indian:
            score += 0.18

        # 2. Director synergy
        c_dir = str(m.get("director", "")).strip().lower()
        if t_dir and c_dir and t_dir not in {"unknown director", "nan", "various"} and t_dir == c_dir:
            score += 0.20

        # 3. Genre overlap
        c_genres = set((g if isinstance(g, str) else g.get("name", "")).lower() for g in m.get("genres", []))
        if t_genres and c_genres:
            overlap = len(t_genres.intersection(c_genres)) / len(t_genres.union(c_genres))
            score += overlap * 0.15

        # 4. Rating quality tie-breaker
        rating = float(m.get("rating", 0.0) or 0.0)
        score += (rating / 10.0) * 0.04

        return score

    enriched_candidates.sort(key=compute_final_ranking, reverse=True)

    # 4. Strict Self-Exclusion & Deduplication
    clean_target_norm = recommender.normalize_text(target_movie_title)
    final_recommendations: List[dict] = []
    seen_tmdb_ids = {str(movie_id)}
    if target_tmdb_id:
        seen_tmdb_ids.add(str(target_tmdb_id))
    seen_titles = {clean_target_norm} if clean_target_norm else set()

    for m in enriched_candidates:
        m_tmdb_id = str(m.get("tmdb_id") or m.get("id") or "")
        m_norm = recommender.normalize_text(m.get("title", ""))
        m_year = m.get("year", 0)
        t_key = f"{m_norm}_{m_year}"

        # Never recommend target movie itself
        if (m_tmdb_id and m_tmdb_id in seen_tmdb_ids) or m_norm in seen_titles or t_key in seen_titles:
            continue

        if m_tmdb_id:
            seen_tmdb_ids.add(m_tmdb_id)
        seen_titles.add(m_norm)
        seen_titles.add(t_key)

        # Ensure similarity is null if not computed by ML model
        if is_tmdb_fallback and "similarity" not in m:
            m["similarity"] = None

        final_recommendations.append(m)
        if len(final_recommendations) >= limit:
            break

    _recommendations_cache[cache_key] = (now, final_recommendations)
    return final_recommendations


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

    cache_key = f"search_{q_str.lower()}_{lim}"
    now = time.time()
    if cache_key in _search_endpoint_cache:
        ts, cached = _search_endpoint_cache[cache_key]
        if now - ts < CACHE_TTL:
            return cached

    # 1. Run local smart fuzzy search on ML dataset
    local_results = recommender.search_movies(q_str, limit=lim)

    # 2. If TMDB is configured, fetch TMDB live search results
    tmdb_results: List[dict] = []
    if tmdb_service.is_configured():
        tmdb_results = tmdb_service.search_tmdb(q_str, limit=lim)

    # If no TMDB configured, return enriched local results
    if not tmdb_results:
        res = tmdb_service.enrich_movies_batch(local_results)
        _search_endpoint_cache[cache_key] = (now, res)
        return res

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

        # Popularity & Vote count ranking
        score += float(m.get("rating", 0.0) or 0.0) * 2.0
        votes = float(m.get("votes", 0) or m.get("vote_count", 0) or 0)
        score += min(votes * 0.5, 300.0)
        pop = float(m.get("popularity", 0.0) or 0.0)
        score += min(pop * 5.0, 400.0)
        return score

    # Combine candidates from both TMDB live search and local dataset
    all_candidates = tmdb_results + [dict(m) for m in local_results[:10]]

    # Sort all candidates by relevance score
    all_candidates.sort(key=get_match_score, reverse=True)

    for movie in all_candidates:
        m_title_norm = recommender.normalize_text(movie.get("title", ""))
        m_year = movie.get("year", 0)
        t_key = f"{m_title_norm}_{m_year}"

        cand_ids = []
        if movie.get("tmdb_id"):
            cand_ids.append(str(movie["tmdb_id"]))
        if movie.get("id"):
            cand_ids.append(str(movie["id"]))
        if movie.get("movie_id"):
            cand_ids.append(str(movie["movie_id"]))

        # If any ID or year-title combination already seen, skip duplicate
        if (cand_ids and any(cid in seen_ids for cid in cand_ids)) or t_key in seen_titles:
            continue

        for cid in cand_ids:
            seen_ids.add(cid)
        seen_titles.add(t_key)
        merged_results.append(movie)

        if len(merged_results) >= lim:
            break

    _search_endpoint_cache[cache_key] = (now, merged_results)
    return merged_results


@app.get("/api/genres", response_model=List[str], tags=["Metadata"])
def get_genres():
    return recommender.get_genres()


@app.get("/api/languages", response_model=List[str], tags=["Metadata"])
def get_languages():
    return recommender.get_languages()
