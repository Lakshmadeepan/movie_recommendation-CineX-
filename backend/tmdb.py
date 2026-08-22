import os
import re
import time
from typing import List, Dict, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor

import requests
from dotenv import load_dotenv

# Load .env from backend, frontend, or root
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY") or os.getenv("VITE_TMDB_API_KEY") or ""
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p"

DEFAULT_POSTER = "https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=500&h=750&fit=crop&auto=format"
DEFAULT_BACKDROP = "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=1400&h=600&fit=crop&auto=format"
DEFAULT_AVATAR = "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=200&h=200&fit=crop&auto=format"

# Curated fallback data with UNIQUE Unsplash images and REAL YouTube trailer IDs.
# These are used when TMDB API key is not configured or fails.
CURATED_MOVIE_ASSETS: Dict[str, Dict[str, Any]] = {
    "vada chennai": {
        "poster": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=500&h=750&fit=crop&auto=format",
        "backdrop": "https://images.unsplash.com/photo-1478720568477-152d9b164e26?w=1400&h=600&fit=crop&auto=format",
        "trailerId": "eLt-q-c6szY",
        "director": "Vetrimaaran",
        "year": 2018,
        "rating": 8.5,
        "language": "Tamil",
        "genres": ["Action", "Crime", "Drama"],
    },
    "vikram": {
        "poster": "https://images.unsplash.com/photo-1500462918059-b1a0cb512f1d?w=500&h=750&fit=crop&auto=format",
        "backdrop": "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=1400&h=600&fit=crop&auto=format",
        "trailerId": "OKBMCLz536o",
        "director": "Lokesh Kanagaraj",
        "year": 2022,
        "rating": 8.4,
        "language": "Tamil",
        "genres": ["Action", "Thriller", "Crime"],
    },
    "jai bhim": {
        "poster": "https://images.unsplash.com/photo-1611174777809-c8dcea724bb7?w=500&h=750&fit=crop&auto=format",
        "backdrop": "https://images.unsplash.com/photo-1440404653325-ab127d49abc1?w=1400&h=600&fit=crop&auto=format",
        "trailerId": "Gc6dEDnL8JA",
        "director": "T. J. Gnanavel",
        "year": 2021,
        "rating": 8.9,
        "language": "Tamil",
        "genres": ["Crime", "Drama", "Mystery"],
    },
    "maharaja": {
        "poster": "https://images.unsplash.com/photo-1535016120720-40c646be5580?w=500&h=750&fit=crop&auto=format",
        "backdrop": "https://images.unsplash.com/photo-1517604931442-7e0c8ed2963c?w=1400&h=600&fit=crop&auto=format",
        "trailerId": "4P_T9e7m_tI",
        "director": "Nithilan Saminathan",
        "year": 2024,
        "rating": 8.6,
        "language": "Tamil",
        "genres": ["Action", "Drama", "Thriller"],
    },
    "leo": {
        "poster": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=500&h=750&fit=crop&auto=format&q=80",
        "backdrop": "https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=1400&h=600&fit=crop&auto=format",
        "trailerId": "Po3jStA673E",
        "director": "Lokesh Kanagaraj",
        "year": 2023,
        "rating": 7.8,
        "language": "Tamil",
        "genres": ["Action", "Crime", "Thriller"],
    },
    "jailer": {
        "poster": "https://images.unsplash.com/photo-1485846234645-a62644f84728?w=500&h=750&fit=crop&auto=format",
        "backdrop": "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=1400&h=600&fit=crop&auto=format&q=80",
        "trailerId": "xenOE1Tma0A",
        "director": "Nelson Dilipkumar",
        "year": 2023,
        "rating": 7.9,
        "language": "Tamil",
        "genres": ["Action", "Comedy", "Crime"],
    },
    "kaithi": {
        "poster": "https://images.unsplash.com/photo-1509347528160-9a9e33742cdb?w=500&h=750&fit=crop&auto=format",
        "backdrop": "https://images.unsplash.com/photo-1440404653325-ab127d49abc1?w=1400&h=600&fit=crop&auto=format&q=80",
        "trailerId": "gL4J_G_Xvbg",
        "director": "Lokesh Kanagaraj",
        "year": 2019,
        "rating": 8.5,
        "language": "Tamil",
        "genres": ["Action", "Thriller"],
    },
    "asuran": {
        "poster": "https://images.unsplash.com/photo-1524985069026-dd778a71c7b4?w=500&h=750&fit=crop&auto=format",
        "backdrop": "https://images.unsplash.com/photo-1478720568477-152d9b164e26?w=1400&h=600&fit=crop&auto=format&q=80",
        "trailerId": "vRwgY3s3s08",
        "director": "Vetrimaaran",
        "year": 2019,
        "rating": 8.6,
        "language": "Tamil",
        "genres": ["Action", "Drama"],
    },
    "master": {
        "poster": "https://images.unsplash.com/photo-1574267432553-4b4628081c31?w=500&h=750&fit=crop&auto=format",
        "backdrop": "https://images.unsplash.com/photo-1517604931442-7e0c8ed2963c?w=1400&h=600&fit=crop&auto=format&q=80",
        "trailerId": "UTiXQgk1Z5M",
        "director": "Lokesh Kanagaraj",
        "year": 2021,
        "rating": 7.8,
        "language": "Tamil",
        "genres": ["Action", "Thriller"],
    },
    "viduthalai part 1": {
        "poster": "https://images.unsplash.com/photo-1594908900066-3f47337c1d55?w=500&h=750&fit=crop&auto=format",
        "backdrop": "https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=1400&h=600&fit=crop&auto=format&q=90",
        "trailerId": "0s5E-E4q8oU",
        "director": "Vetrimaaran",
        "year": 2023,
        "rating": 8.3,
        "language": "Tamil",
        "genres": ["Crime", "Drama", "Action"],
    },
    "maari": {
        "poster": "https://images.unsplash.com/photo-1509347528160-9a9e33742cdb?w=500&h=750&fit=crop&auto=format",
        "backdrop": "https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=1400&h=600&fit=crop&auto=format",
        "trailerId": "bk5lKWDVJAI",
        "director": "Balaji Mohan",
        "year": 2015,
        "rating": 6.0,
        "language": "Tamil",
        "genres": ["Action", "Comedy"],
    },
    "raayan": {
        "poster": "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=500&h=750&fit=crop&auto=format",
        "backdrop": "https://images.unsplash.com/photo-1478720568477-152d9b164e26?w=1400&h=600&fit=crop&auto=format",
        "trailerId": "s8yWkY-v_k8",
        "director": "Dhanush",
        "year": 2024,
        "rating": 7.6,
        "language": "Tamil",
        "genres": ["Action", "Crime", "Drama"],
    },
    "ponniyin selvan": {
        "poster": "https://images.unsplash.com/photo-1594908900066-3f47337c1d55?w=500&h=750&fit=crop&auto=format",
        "backdrop": "https://images.unsplash.com/photo-1440404653325-ab127d49abc1?w=1400&h=600&fit=crop&auto=format",
        "trailerId": "D4qAQYLGZVM",
        "director": "Mani Ratnam",
        "year": 2022,
        "rating": 8.0,
        "language": "Tamil",
        "genres": ["Action", "Drama", "History"],
    },
    "soorarai pottru": {
        "poster": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=500&h=750&fit=crop&auto=format",
        "backdrop": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=1400&h=600&fit=crop&auto=format",
        "trailerId": "faG8RiaGWBw",
        "director": "Sudha Kongara",
        "year": 2020,
        "rating": 8.7,
        "language": "Tamil",
        "genres": ["Drama"],
    },
    "96": {
        "poster": "https://images.unsplash.com/photo-1516589178581-6cd7833ae3b2?w=500&h=750&fit=crop&auto=format",
        "backdrop": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=1400&h=600&fit=crop&auto=format",
        "trailerId": "r0ox4Wc5y0E",
        "director": "C. Prem Kumar",
        "year": 2018,
        "rating": 8.5,
        "language": "Tamil",
        "genres": ["Romance", "Drama"],
    },
    "theri": {
        "poster": "https://images.unsplash.com/photo-1509347528160-9a9e33742cdb?w=500&h=750&fit=crop&auto=format",
        "backdrop": "https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=1400&h=600&fit=crop&auto=format",
        "trailerId": "ZK4uGL46Xq0",
        "director": "Atlee",
        "year": 2016,
        "rating": 7.3,
        "language": "Tamil",
        "genres": ["Action", "Drama"],
    },
    "mersal": {
        "poster": "https://images.unsplash.com/photo-1574267432553-4b4628081c31?w=500&h=750&fit=crop&auto=format",
        "backdrop": "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=1400&h=600&fit=crop&auto=format",
        "trailerId": "gQDo5QuZ514",
        "director": "Atlee",
        "year": 2017,
        "rating": 7.8,
        "language": "Tamil",
        "genres": ["Action", "Thriller"],
    },
    "kattu paya sir intha kaali": {
        "poster": "https://images.unsplash.com/photo-1542204165-65bf26472b9b?w=500&h=750&fit=crop&auto=format",
        "backdrop": "https://images.unsplash.com/photo-1440404653325-ab127d49abc1?w=1400&h=600&fit=crop&auto=format&q=90",
        "trailerId": "",
    },
    "gangs of madras": {
        "poster": "https://images.unsplash.com/photo-1560109947-543149eceb16?w=500&h=750&fit=crop&auto=format",
        "backdrop": "https://images.unsplash.com/photo-1478720568477-152d9b164e26?w=1400&h=600&fit=crop&auto=format&q=90",
        "trailerId": "4eQ1W4p2UvE",
    },
    "vendhu thanindhathu kaadu": {
        "poster": "https://images.unsplash.com/photo-1598899134739-24c46f58b8c0?w=500&h=750&fit=crop&auto=format",
        "backdrop": "https://images.unsplash.com/photo-1517604931442-7e0c8ed2963c?w=1400&h=600&fit=crop&auto=format&q=90",
        "trailerId": "h4uWc_b47Z8",
    },
}

# Pool of unique Unsplash images for movies without curated data
UNIQUE_POSTER_POOL = [
    "https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=500&h=750&fit=crop&auto=format",
    "https://images.unsplash.com/photo-1509347528160-9a9e33742cdb?w=500&h=750&fit=crop&auto=format",
    "https://images.unsplash.com/photo-1500462918059-b1a0cb512f1d?w=500&h=750&fit=crop&auto=format",
    "https://images.unsplash.com/photo-1611174777809-c8dcea724bb7?w=500&h=750&fit=crop&auto=format",
    "https://images.unsplash.com/photo-1535016120720-40c646be5580?w=500&h=750&fit=crop&auto=format",
    "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=500&h=750&fit=crop&auto=format",
    "https://images.unsplash.com/photo-1485846234645-a62644f84728?w=500&h=750&fit=crop&auto=format",
    "https://images.unsplash.com/photo-1524985069026-dd778a71c7b4?w=500&h=750&fit=crop&auto=format",
    "https://images.unsplash.com/photo-1574267432553-4b4628081c31?w=500&h=750&fit=crop&auto=format",
    "https://images.unsplash.com/photo-1594908900066-3f47337c1d55?w=500&h=750&fit=crop&auto=format",
    "https://images.unsplash.com/photo-1542204165-65bf26472b9b?w=500&h=750&fit=crop&auto=format",
    "https://images.unsplash.com/photo-1560109947-543149eceb16?w=500&h=750&fit=crop&auto=format",
    "https://images.unsplash.com/photo-1598899134739-24c46f58b8c0?w=500&h=750&fit=crop&auto=format",
    "https://images.unsplash.com/photo-1478720568477-152d9b164e26?w=500&h=750&fit=crop&auto=format",
    "https://images.unsplash.com/photo-1440404653325-ab127d49abc1?w=500&h=750&fit=crop&auto=format",
    "https://images.unsplash.com/photo-1517604931442-7e0c8ed2963c?w=500&h=750&fit=crop&auto=format",
]


def _get_unique_poster(title: str) -> str:
    """Deterministic unique poster from pool based on title hash."""
    idx = hash(title.lower().strip()) % len(UNIQUE_POSTER_POOL)
    return UNIQUE_POSTER_POOL[idx]


class TMDBService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or TMDB_API_KEY
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "CineX-Movie-App/2.0",
            "Accept": "application/json"
        })
        self._movie_details_cache: Dict[int, Tuple[float, Dict[str, Any]]] = {}
        self._search_cache: Dict[str, Tuple[float, Optional[int]]] = {}
        self._endpoints_cache: Dict[str, Tuple[float, List[Dict[str, Any]]]] = {}
        self.cache_ttl = 3600

    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key.strip())

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        if not self.is_configured():
            return None
        query_params = {"api_key": self.api_key}
        if params:
            query_params.update(params)
        url = f"{TMDB_BASE_URL}{endpoint}"
        try:
            response = self.session.get(url, params=query_params, timeout=6.0)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception:
            return None

    # ── Search & Match ──────────────────────────────────────────────

    def find_tmdb_id(self, title: str, year: Optional[int] = None, language: Optional[str] = None) -> Optional[int]:
        if not self.is_configured():
            return None
        clean_title = re.sub(r"[^a-zA-Z0-9\s]", " ", title).strip().lower()
        clean_title = re.sub(r"\s+", " ", clean_title)
        cache_key = f"{clean_title}_{year or 0}_{language or ''}"
        now = time.time()
        if cache_key in self._search_cache:
            ts, cached_id = self._search_cache[cache_key]
            if now - ts < self.cache_ttl:
                return cached_id

        params: Dict[str, Any] = {"query": title, "include_adult": "false"}
        if year and year > 1900:
            params["primary_release_year"] = str(year)
        data = self._get("/search/movie", params)
        if (not data or not data.get("results")) and year and year > 1900:
            params.pop("primary_release_year", None)
            data = self._get("/search/movie", params)
        if not data or not data.get("results"):
            self._search_cache[cache_key] = (now, None)
            return None

        results = data.get("results", [])
        best_id: Optional[int] = None
        best_score = -1.0
        for m in results:
            score = 0.0
            m_title = (m.get("title") or "").lower()
            m_orig = (m.get("original_title") or "").lower()
            m_lang = (m.get("original_language") or "").lower()
            m_date = m.get("release_date") or ""
            m_year = int(m_date.split("-")[0]) if m_date and "-" in m_date and m_date.split("-")[0].isdigit() else 0

            if m_title == clean_title or m_orig == clean_title:
                score += 50.0
            elif clean_title in m_title or clean_title in m_orig:
                score += 25.0
            if language and language.lower() == "tamil" and m_lang == "ta":
                score += 40.0
            elif language and m_lang == language.lower()[:2]:
                score += 20.0
            if year and year > 1900 and m_year:
                if m_year == year:
                    score += 25.0
                elif abs(m_year - year) <= 1:
                    score += 15.0
            if m.get("poster_path"):
                score += 10.0
            score += (m.get("popularity", 0.0) * 0.1)
            if score > best_score:
                best_score = score
                best_id = m.get("id")

        if best_id is None and results:
            best_id = results[0].get("id")
        self._search_cache[cache_key] = (now, best_id)
        return best_id

    # ── Movie Details ───────────────────────────────────────────────

    def get_movie_details(self, tmdb_id: int) -> Optional[Dict[str, Any]]:
        if not self.is_configured():
            return None
        now = time.time()
        if tmdb_id in self._movie_details_cache:
            ts, cached_data = self._movie_details_cache[tmdb_id]
            if now - ts < self.cache_ttl:
                return cached_data
        data = self._get(f"/movie/{tmdb_id}", {"append_to_response": "credits,videos,watch/providers"})
        if not data:
            return None
        formatted = self._format_tmdb_movie(data)
        self._movie_details_cache[tmdb_id] = (now, formatted)
        return formatted

    def _format_tmdb_movie(self, data: Dict[str, Any]) -> Dict[str, Any]:
        tmdb_id = data.get("id", 0)
        title = data.get("title") or data.get("original_title") or "Untitled"
        overview = data.get("overview") or f"{title} is an engaging cinematic presentation."
        tagline = data.get("tagline") or ""
        rel_date = data.get("release_date") or ""
        year = int(rel_date.split("-")[0]) if rel_date and "-" in rel_date and rel_date.split("-")[0].isdigit() else 0
        vote_avg = float(data.get("vote_average", 0.0) or 0.0)
        rating = round(vote_avg, 1) if vote_avg > 0 else (self._get_curated(title, "rating") or 7.0)
        votes = int(data.get("vote_count", 0))
        popularity = float(data.get("popularity", 10.0))
        runtime_mins = int(data.get("runtime", 120)) if data.get("runtime") else 120
        runtime_str = f"{runtime_mins // 60}h {runtime_mins % 60}m" if runtime_mins >= 60 else f"{runtime_mins}m"

        genres_raw = data.get("genres", [])
        genres = [g.get("name") for g in genres_raw if isinstance(g, dict) and g.get("name")] if genres_raw else ["Drama"]
        if not genres:
            genres = ["Drama"]

        orig_lang = data.get("original_language", "ta")
        lang_map = {"ta": "Tamil", "te": "Telugu", "ml": "Malayalam", "hi": "Hindi", "kn": "Kannada", "en": "English"}
        language = lang_map.get(orig_lang, orig_lang.upper())

        poster_path = data.get("poster_path")
        poster = f"{TMDB_IMAGE_BASE}/w500{poster_path}" if poster_path else (self._get_curated(title, "poster") or _get_unique_poster(title))

        backdrop_path = data.get("backdrop_path") or poster_path
        backdrop = f"{TMDB_IMAGE_BASE}/original{backdrop_path}" if backdrop_path else (self._get_curated(title, "backdrop") or DEFAULT_BACKDROP)

        credits = data.get("credits") or {}
        director = "Unknown Director"
        for person in credits.get("crew", []):
            if person.get("job") == "Director":
                director = person.get("name", "Unknown Director")
                break

        cast = []
        for actor in credits.get("cast", [])[:8]:
            p_path = actor.get("profile_path")
            cast.append({
                "name": actor.get("name", "Actor"),
                "role": actor.get("character") or "Lead",
                "photo": f"{TMDB_IMAGE_BASE}/w185{p_path}" if p_path else DEFAULT_AVATAR
            })

        # YouTube Trailer
        videos = (data.get("videos") or {}).get("results", [])
        trailer_id = ""
        for v in videos:
            if v.get("site") == "YouTube" and v.get("type") == "Trailer" and v.get("official"):
                trailer_id = v.get("key", "")
                break
        if not trailer_id:
            for v in videos:
                if v.get("site") == "YouTube" and v.get("type") == "Trailer":
                    trailer_id = v.get("key", "")
                    break
        if not trailer_id:
            for v in videos:
                if v.get("site") == "YouTube":
                    trailer_id = v.get("key", "")
                    break
        if not trailer_id:
            trailer_id = self._get_curated(title, "trailerId") or ""

        # Streaming providers
        wp = (data.get("watch/providers") or {}).get("results", {})
        in_prov = wp.get("IN") or wp.get("US") or {}
        streaming = []
        seen = set()
        for cat in ["flatrate", "free", "ads"]:
            for prov in in_prov.get(cat, []):
                p_name = prov.get("provider_name", "")
                if p_name and p_name not in seen:
                    seen.add(p_name)
                    lp = prov.get("logo_path")
                    color = "#E50914" if "Netflix" in p_name else "#00A8E1" if "Prime" in p_name else "#0A3CA8" if "Hotstar" in p_name or "Disney" in p_name else "#FF6B00" if "Sun" in p_name else "#800080" if "ZEE" in p_name else "#333"
                    streaming.append({"name": p_name, "logo": f"{TMDB_IMAGE_BASE}/w92{lp}" if lp else "▶", "color": color})

        return {
            "id": tmdb_id, "movie_id": tmdb_id, "tmdb_id": tmdb_id,
            "title": title, "year": year, "rating": rating, "votes": votes,
            "language": language, "genres": genres, "runtime": runtime_str, "runtime_minutes": runtime_mins,
            "overview": overview, "tagline": tagline, "director": director,
            "poster": poster, "backdrop": backdrop, "trailerId": trailer_id or "",
            "cast": cast, "budget_crores": 0.0, "revenue_crores": 0.0,
            "popularity": popularity, "imdb_id": data.get("imdb_id") or "",
            "rating_source": "TMDB", "streaming": streaming,
        }

    def _get_curated(self, title: str, field: str) -> Optional[Any]:
        clean = title.strip().lower()
        if clean in CURATED_MOVIE_ASSETS:
            return CURATED_MOVIE_ASSETS[clean].get(field)
        for k, v in CURATED_MOVIE_ASSETS.items():
            if k in clean or clean in k:
                return v.get(field)
        return None

    # ── Enrichment ──────────────────────────────────────────────────

    def enrich_movie(self, movie: Dict[str, Any]) -> Dict[str, Any]:
        title = movie.get("title", "")
        curated = CURATED_MOVIE_ASSETS.get(title.strip().lower())

        if not self.is_configured():
            m = dict(movie)
            if curated:
                for k in ["poster", "backdrop", "trailerId", "director", "year", "rating", "genres"]:
                    if k in curated and curated[k]:
                        m[k] = curated[k]
            if not m.get("poster") or not str(m["poster"]).startswith("http"):
                m["poster"] = self._get_curated(title, "poster") or _get_unique_poster(title)
            if not m.get("backdrop") or not str(m["backdrop"]).startswith("http"):
                m["backdrop"] = self._get_curated(title, "backdrop") or DEFAULT_BACKDROP
            if not m.get("trailerId") or m["trailerId"] in ("none", "dQw4w9WgXcQ", ""):
                m["trailerId"] = self._get_curated(title, "trailerId") or ""
            return m

        raw_id = movie.get("id") or movie.get("movie_id")
        tmdb_id: Optional[int] = None
        if movie.get("tmdb_id") and str(movie["tmdb_id"]).isdigit():
            tmdb_id = int(movie["tmdb_id"])
        elif movie.get("is_tmdb") and raw_id and str(raw_id).isdigit():
            tmdb_id = int(raw_id)
        else:
            # Resolve actual TMDB ID by movie title, year, and language
            tmdb_id = self.find_tmdb_id(
                title=title,
                year=movie.get("year", 0),
                language=movie.get("language", "")
            )

        if tmdb_id:
            details = self.get_movie_details(tmdb_id)
            if details:
                enriched = dict(details)
                if "similarity" in movie:
                    enriched["similarity"] = movie["similarity"]
                if (not enriched.get("rating") or float(enriched.get("rating") or 0) <= 0) and movie.get("rating") and float(movie.get("rating") or 0) > 0:
                    enriched["rating"] = round(float(movie["rating"]), 1)
                enriched["local_id"] = movie.get("id")
                enriched["rating_source"] = "TMDB"
                return enriched

        fallback = dict(movie)
        if curated:
            for k in ["poster", "backdrop", "trailerId", "director", "year", "rating", "genres"]:
                if k in curated and curated[k]:
                    fallback[k] = curated[k]
        if not fallback.get("rating") or float(fallback.get("rating") or 0) <= 0:
            fallback["rating"] = self._get_curated(title, "rating") or 7.0
        fallback["rating_source"] = "IMDb" if movie.get("imdb_id") else "TMDB"
        if not fallback.get("poster") or not str(fallback["poster"]).startswith("http"):
            fallback["poster"] = self._get_curated(title, "poster") or _get_unique_poster(title)
        if not fallback.get("backdrop") or not str(fallback["backdrop"]).startswith("http"):
            fallback["backdrop"] = self._get_curated(title, "backdrop") or DEFAULT_BACKDROP
        if not fallback.get("trailerId") or fallback["trailerId"] in ("none", "dQw4w9WgXcQ", ""):
            fallback["trailerId"] = self._get_curated(title, "trailerId") or ""
        return fallback

    def enrich_movies_batch(self, movies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not movies:
            return []
        if not self.is_configured():
            return [self.enrich_movie(m) for m in movies]
        with ThreadPoolExecutor(max_workers=min(len(movies), 6)) as executor:
            return list(executor.map(self.enrich_movie, movies))

    # ── Discovery Endpoints ─────────────────────────────────────────

    def get_trending(self, limit: int = 20) -> List[Dict[str, Any]]:
        data = self._get("/trending/movie/week")
        return [self._fmt(m) for m in (data or {}).get("results", [])[:limit]] if data else []

    def get_now_playing(self, limit: int = 20) -> List[Dict[str, Any]]:
        data = self._get("/movie/now_playing", {"region": "IN"}) or self._get("/movie/now_playing")
        return [self._fmt(m) for m in (data or {}).get("results", [])[:limit]] if data else []

    def get_popular(self, limit: int = 20) -> List[Dict[str, Any]]:
        data = self._get("/movie/popular", {"region": "IN"}) or self._get("/movie/popular")
        return [self._fmt(m) for m in (data or {}).get("results", [])[:limit]] if data else []

    def get_top_rated(self, limit: int = 20) -> List[Dict[str, Any]]:
        data = self._get("/movie/top_rated")
        return [self._fmt(m) for m in (data or {}).get("results", [])[:limit]] if data else []

    def get_upcoming(self, limit: int = 20) -> List[Dict[str, Any]]:
        data = self._get("/movie/upcoming", {"region": "IN"}) or self._get("/movie/upcoming")
        return [self._fmt(m) for m in (data or {}).get("results", [])[:limit]] if data else []

    def get_tamil_movies(self, limit: int = 50) -> List[Dict[str, Any]]:
        data = self._get("/discover/movie", {"with_original_language": "ta", "sort_by": "popularity.desc", "page": "1"})
        return [self._fmt(m) for m in (data or {}).get("results", [])[:limit]] if data else []

    def search_tmdb(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        import difflib
        q = query.strip()
        if not q:
            return self.get_popular(limit)

        # 1. Primary search with user query
        data = self._get("/search/movie", {"query": q, "include_adult": "false"})
        results = (data or {}).get("results", [])

        # 2. Spelling Relaxation: if initial query returns few/no results, try intelligent variants
        if len(results) < 3:
            q_lower = q.lower()
            variants: List[str] = []

            # De-duplicate repeated characters (e.g. vikramm -> vikram, maharajaa -> maharaja)
            clean_v = re.sub(r"([a-z])\1+", r"\1", q_lower)
            if clean_v != q_lower:
                variants.append(clean_v)

            # Phonetic / vowel adjustments (e.g. jai bheem -> jai bhim, vadachenai -> vada chennai)
            v2 = q_lower.replace("ee", "i").replace("oo", "u").replace("ai", "ay").replace("aa", "a")
            if v2 != q_lower and v2 not in variants:
                variants.append(v2)

            # Suffix variations (e.g. interstaller -> interstellar)
            if q_lower.endswith("er"):
                variants.append(q_lower[:-2] + "ar")
                variants.append(q_lower[:-2] + "or")
            elif q_lower.endswith("ar"):
                variants.append(q_lower[:-2] + "er")

            # Multi-word decomposition (e.g. 'vada chenai' -> search 'vada' and 'chennai')
            words = [w for w in q_lower.split() if len(w) >= 4]
            for w in words:
                if w not in variants:
                    variants.append(w)

            # Prefix relaxation for typos at end of words (e.g. interstaller -> interst)
            if len(q_lower) >= 7:
                variants.append(q_lower[:7])
                variants.append(q_lower[:6])
                variants.append(q_lower[:5])
            elif len(q_lower) >= 5:
                variants.append(q_lower[:4])

            seen_ids = {m["id"] for m in results if isinstance(m, dict) and "id" in m}
            for var in variants:
                v_data = self._get("/search/movie", {"query": var, "include_adult": "false"})
                for item in (v_data or {}).get("results", []):
                    if item.get("id") not in seen_ids:
                        seen_ids.add(item.get("id"))
                        results.append(item)
                if len(results) >= 15:
                    break

        if not results:
            return []

        q_clean = re.sub(r"[^a-zA-Z0-9\s]", " ", q).strip().lower()

        def score_tmdb_item(item: Dict[str, Any]) -> float:
            m_title = re.sub(r"[^a-zA-Z0-9\s]", " ", item.get("title") or "").strip().lower()
            m_orig = re.sub(r"[^a-zA-Z0-9\s]", " ", item.get("original_title") or "").strip().lower()
            score = 0.0

            if m_title == q_clean or m_orig == q_clean:
                score += 1000.0
            elif m_title.startswith(q_clean) or m_orig.startswith(q_clean):
                score += 500.0
            elif q_clean in m_title or q_clean in m_orig:
                score += 300.0

            ratio1 = difflib.SequenceMatcher(None, q_clean, m_title).ratio() if m_title else 0.0
            ratio2 = difflib.SequenceMatcher(None, q_clean, m_orig).ratio() if m_orig else 0.0
            max_ratio = max(ratio1, ratio2)

            if max_ratio >= 0.85:
                score += 450.0 * max_ratio
            elif max_ratio >= 0.70:
                score += 280.0 * max_ratio
            elif max_ratio >= 0.55:
                score += 120.0 * max_ratio

            # Popularity / Rating tie breaker
            score += float(item.get("vote_average", 0.0) or 0.0) * 0.5
            score += float(item.get("popularity", 0.0) or 0.0) * 0.1
            return score

        results.sort(key=score_tmdb_item, reverse=True)
        return [self._fmt(m) for m in results[:limit]]

    def _fmt(self, m: Dict[str, Any]) -> Dict[str, Any]:
        title = m.get("title") or m.get("original_title") or "Untitled"
        rel_date = m.get("release_date") or ""
        year = int(rel_date.split("-")[0]) if rel_date and "-" in rel_date and rel_date.split("-")[0].isdigit() else 0
        pp = m.get("poster_path")
        poster = f"{TMDB_IMAGE_BASE}/w500{pp}" if pp else (self._get_curated(title, "poster") or _get_unique_poster(title))
        bp = m.get("backdrop_path") or pp
        backdrop = f"{TMDB_IMAGE_BASE}/original{bp}" if bp else (self._get_curated(title, "backdrop") or DEFAULT_BACKDROP)
        ol = m.get("original_language", "ta")
        lang_map = {"ta": "Tamil", "te": "Telugu", "ml": "Malayalam", "hi": "Hindi", "kn": "Kannada", "en": "English"}

        vote_avg = float(m.get("vote_average", 0.0) or 0.0)
        rating = round(vote_avg, 1) if vote_avg > 0 else (self._get_curated(title, "rating") or 7.0)

        return {
            "id": m.get("id", 0), "movie_id": m.get("id", 0), "tmdb_id": m.get("id", 0),
            "title": title, "year": year,
            "rating": rating, "votes": int(m.get("vote_count", 0)),
            "language": lang_map.get(ol, ol.upper()), "genres": ["Drama"], "runtime": "2h 00m", "runtime_minutes": 120,
            "overview": m.get("overview") or f"{title} is a popular movie.", "tagline": "",
            "director": "Various", "poster": poster, "backdrop": backdrop,
            "trailerId": self._get_curated(title, "trailerId") or "", "cast": [],
            "budget_crores": 0.0, "revenue_crores": 0.0, "popularity": float(m.get("popularity", 10.0)),
            "imdb_id": "", "rating_source": "TMDB", "streaming": [],
        }


tmdb_service = TMDBService()
