import os
import re
import time
import difflib
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
    "singam": {
        "poster": "https://images.unsplash.com/photo-1509347528160-9a9e33742cdb?w=500&h=750&fit=crop&auto=format",
        "backdrop": "https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=1400&h=600&fit=crop&auto=format",
        "trailerId": "23jQ8z8Q9wE",
        "director": "Hari",
        "year": 2010,
        "rating": 7.5,
        "language": "Tamil",
        "genres": ["Action", "Crime"],
    }
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

def _normalize_title_str(text: str) -> str:
    """Normalize title for exact and fuzzy comparisons."""
    if not text:
        return ""
    cleaned = re.sub(r"[^a-zA-Z0-9\s]", " ", str(text).lower())
    return re.sub(r"\s+", " ", cleaned).strip()

def _extract_tokens_and_numbers(title: str) -> Tuple[List[str], set]:
    """Extract individual words and numeric/roman parts for sequence matching."""
    norm = _normalize_title_str(title)
    tokens = norm.split()
    numbers = set()
    for t in tokens:
        if t.isdigit():
            numbers.add(t)
        elif t in {"i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x"}:
            roman_map = {"i": "1", "ii": "2", "iii": "3", "iv": "4", "v": "5", "vi": "6", "vii": "7", "viii": "8", "ix": "9", "x": "10"}
            numbers.add(roman_map[t])
    return tokens, numbers

def _get_unique_poster(title: str) -> str:
    """Deterministic unique poster from pool based on title hash."""
    idx = abs(hash(title.lower().strip())) % len(UNIQUE_POSTER_POOL)
    return UNIQUE_POSTER_POOL[idx]


class TMDBService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or TMDB_API_KEY
        self.session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(pool_connections=40, pool_maxsize=40, max_retries=1)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        self.session.headers.update({
            "User-Agent": "CineX-Movie-App/2.0",
            "Accept": "application/json"
        })
        self._raw_get_cache: Dict[str, Tuple[float, Any]] = {}
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

        now = time.time()
        # Fast query cache lookup
        cache_key = f"{endpoint}_{tuple(sorted(query_params.items()))}"
        if cache_key in self._raw_get_cache:
            ts, data = self._raw_get_cache[cache_key]
            if now - ts < self.cache_ttl:
                return data

        url = f"{TMDB_BASE_URL}{endpoint}"
        try:
            response = self.session.get(url, params=query_params, timeout=5.0)
            if response.status_code == 200:
                res_data = response.json()
                self._raw_get_cache[cache_key] = (now, res_data)
                return res_data
            return None
        except Exception:
            return None

    # ── Intelligent TMDB Matching ─────────────────────────────────────

    def find_tmdb_id(
        self,
        title: str,
        year: Optional[int] = None,
        language: Optional[str] = None
    ) -> Optional[int]:
        """
        Intelligently find the correct TMDB ID for a movie query.
        Uses a weighted multi-factor scoring function:
        - Exact normalized title match bonus
        - Exact original title match bonus
        - Token similarity ratio
        - Number/sequel alignment (e.g. 'Singam' vs 'Singam 2')
        - Year match & proximity bonus
        - Language alignment bonus
        - Release date relevance
        - Secondary popularity tie-breaker
        Never blindly picks results[0] unless it meets a confidence threshold.
        """
        if not self.is_configured():
            return None

        q_clean = _normalize_title_str(title)
        if not q_clean:
            return None

        cache_key = f"{q_clean}_{year or 0}_{language or ''}"
        now = time.time()
        if cache_key in self._search_cache:
            ts, cached_id = self._search_cache[cache_key]
            if now - ts < self.cache_ttl:
                return cached_id

        # 1. First search with primary release year if provided
        params: Dict[str, Any] = {"query": title, "include_adult": "false"}
        if year and year > 1900:
            params["primary_release_year"] = str(year)

        data = self._get("/search/movie", params)
        results = (data or {}).get("results", [])

        # If year-restricted search returned 0 results, retry without year filter
        if not results and year and year > 1900:
            params.pop("primary_release_year", None)
            data = self._get("/search/movie", params)
            results = (data or {}).get("results", [])

        if not results:
            self._search_cache[cache_key] = (now, None)
            return None

        q_tokens, q_nums = _extract_tokens_and_numbers(title)

        best_id: Optional[int] = None
        best_score = -1000.0

        for m in results:
            score = 0.0
            m_title = m.get("title") or ""
            m_orig = m.get("original_title") or ""
            m_clean = _normalize_title_str(m_title)
            m_orig_clean = _normalize_title_str(m_orig)

            m_tokens, m_nums = _extract_tokens_and_numbers(m_title)
            m_orig_tokens, m_orig_nums = _extract_tokens_and_numbers(m_orig)

            # 1. Exact Title Match
            if m_clean == q_clean or m_orig_clean == q_clean:
                score += 500.0
            else:
                ratio1 = difflib.SequenceMatcher(None, q_clean, m_clean).ratio() if m_clean else 0.0
                ratio2 = difflib.SequenceMatcher(None, q_clean, m_orig_clean).ratio() if m_orig_clean else 0.0
                max_ratio = max(ratio1, ratio2)

                if max_ratio >= 0.90:
                    score += 350.0 * max_ratio
                elif max_ratio >= 0.75:
                    score += 200.0 * max_ratio
                elif max_ratio >= 0.60:
                    score += 100.0 * max_ratio

            # 2. Number / Sequel Penalty or Bonus
            combined_m_nums = m_nums.union(m_orig_nums)
            if q_nums:
                if q_nums == combined_m_nums:
                    score += 200.0
                elif not q_nums.intersection(combined_m_nums):
                    score -= 250.0
            else:
                # Query has NO number
                if combined_m_nums:
                    score -= 150.0

            # 3. Year Proximity Bonus
            m_date = m.get("release_date") or ""
            m_year = int(m_date.split("-")[0]) if m_date and "-" in m_date and m_date.split("-")[0].isdigit() else 0

            if year and year > 1900 and m_year:
                diff = abs(m_year - year)
                if diff == 0:
                    score += 250.0
                elif diff == 1:
                    score += 120.0
                elif diff <= 2:
                    score += 50.0
                else:
                    score -= (diff * 25.0)

            # 4. Language Match Bonus & Mismatch Penalty
            m_lang = (m.get("original_language") or "").lower()
            if language:
                lang_lower = language.strip().lower()
                lang_code_map = {
                    "tamil": "ta", "telugu": "te", "malayalam": "ml",
                    "hindi": "hi", "kannada": "kn", "english": "en"
                }
                expected_code = lang_code_map.get(lang_lower, lang_lower[:2])
                if m_lang == expected_code:
                    score += 180.0
                elif m_lang in {"ta", "te", "ml", "kn", "hi"} and expected_code in {"ta", "te", "ml", "kn", "hi"}:
                    score += 40.0
                else:
                    # Penalize completely different language family (e.g. English when searching Tamil)
                    score -= 80.0

            # 5. Media Presence
            if m.get("poster_path"):
                score += 20.0
            if m.get("backdrop_path"):
                score += 10.0

            # 6. Secondary Popularity Tie-Breaker
            pop = float(m.get("popularity", 0.0) or 0.0)
            score += min(pop * 0.05, 30.0)

            if score > best_score:
                best_score = score
                best_id = m.get("id")

        if best_score < 40.0:
            best_id = None

        self._search_cache[cache_key] = (now, best_id)
        return best_id

    # ── Movie Details & Formatting ────────────────────────────────────

    def get_movie_details(self, tmdb_id: int, full_details: bool = True) -> Optional[Dict[str, Any]]:
        if not self.is_configured():
            return None
        now = time.time()
        cache_key = (tmdb_id, full_details)
        if cache_key in self._movie_details_cache:
            ts, cached_data = self._movie_details_cache[cache_key]
            if now - ts < self.cache_ttl:
                return cached_data

        params = {"append_to_response": "credits,videos,watch/providers"} if full_details else None
        data = self._get(f"/movie/{tmdb_id}", params)
        if not data:
            return None

        formatted = self._format_tmdb_movie(data)
        self._movie_details_cache[cache_key] = (now, formatted)
        return formatted

    def _format_tmdb_movie(self, data: Dict[str, Any]) -> Dict[str, Any]:
        tmdb_id = data.get("id", 0)
        title = data.get("title") or data.get("original_title") or "Untitled"
        overview = data.get("overview") or f"{title} is an engaging cinematic presentation."
        tagline = data.get("tagline") or ""
        rel_date = data.get("release_date") or ""
        status = data.get("status") or "Released"
        year = int(rel_date.split("-")[0]) if rel_date and "-" in rel_date and rel_date.split("-")[0].isdigit() else 0

        vote_avg = float(data.get("vote_average", 0.0) or 0.0)
        votes = int(data.get("vote_count", 0) or 0)
        popularity = float(data.get("popularity", 10.0) or 10.0)

        # For unreleased or upcoming movies with 0 votes, keep rating as 0.0 or actual TMDB rating
        # Do NOT fake a 7.0 score for upcoming/unrated movies
        if votes > 0 and vote_avg > 0:
            rating = round(vote_avg, 1)
        elif self._get_curated(title, "rating"):
            rating = self._get_curated(title, "rating")
        else:
            rating = round(vote_avg, 1) if vote_avg > 0 else 0.0

        runtime_mins = int(data.get("runtime", 120)) if (data.get("runtime") and int(data.get("runtime")) > 0) else 120
        runtime_str = f"{runtime_mins // 60}h {runtime_mins % 60}m" if runtime_mins >= 60 else f"{runtime_mins}m"

        genres_raw = data.get("genres", [])
        genres = [g.get("name") for g in genres_raw if isinstance(g, dict) and g.get("name")] if genres_raw else []
        if not genres:
            genres = ["Drama"]

        orig_lang = data.get("original_language", "ta")
        lang_map = {
            "ta": "Tamil", "te": "Telugu", "ml": "Malayalam",
            "hi": "Hindi", "kn": "Kannada", "en": "English",
            "ja": "Japanese", "ko": "Korean", "fr": "French", "es": "Spanish"
        }
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

        orig_title = data.get("original_title") or title
        spoken_langs = [l.get("iso_639_1") or l.get("name") for l in data.get("spoken_languages", []) if isinstance(l, dict)]

        return {
            "id": tmdb_id,
            "movie_id": tmdb_id,
            "tmdb_id": tmdb_id,
            "title": title,
            "original_title": orig_title,
            "year": year,
            "release_date": rel_date,
            "rating": rating,
            "votes": votes,
            "language": language,
            "original_language": orig_lang,
            "spoken_languages": spoken_langs,
            "language_match": None,
            "genres": genres,
            "runtime": runtime_str,
            "runtime_minutes": runtime_mins,
            "overview": overview,
            "tagline": tagline,
            "status": status,
            "director": director,
            "poster": poster,
            "backdrop": backdrop,
            "trailerId": trailer_id or "",
            "cast": cast,
            "budget_crores": 0.0,
            "revenue_crores": 0.0,
            "popularity": popularity,
            "imdb_id": data.get("imdb_id") or "",
            "rating_source": "TMDB",
            "streaming": streaming,
            "similarity": None
        }

    def _get_curated(self, title: str, field: str) -> Optional[Any]:
        clean = title.strip().lower()
        if clean in CURATED_MOVIE_ASSETS:
            return CURATED_MOVIE_ASSETS[clean].get(field)
        for k, v in CURATED_MOVIE_ASSETS.items():
            if k == clean or k in clean or clean in k:
                return v.get(field)
        return None

    # ── TMDB Recommendations & Similar Endpoints ──────────────────────

    def get_tmdb_recommendations(self, tmdb_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch movie recommendations generated by TMDB discovery algorithm."""
        data = self._get(f"/movie/{tmdb_id}/recommendations")
        raw_results = (data or {}).get("results", [])
        return [self._fmt(m) for m in raw_results[:limit]]

    def get_tmdb_similar(self, tmdb_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch similar movies based on genres and keywords from TMDB."""
        data = self._get(f"/movie/{tmdb_id}/similar")
        raw_results = (data or {}).get("results", [])
        return [self._fmt(m) for m in raw_results[:limit]]

    def get_tmdb_fallback_recommendations(self, tmdb_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Comprehensive TMDB fallback when a movie is outside the local dataset:
        1. Query TMDB recommendations
        2. Query TMDB similar movies
        3. Deduplicate against target movie and each other
        4. Return clean, formatted movies with similarity: None
        """
        recs = self.get_tmdb_recommendations(tmdb_id, limit=limit * 2)
        sims = self.get_tmdb_similar(tmdb_id, limit=limit * 2)

        combined = recs + sims
        unique_results: List[Dict[str, Any]] = []
        seen_ids = {str(tmdb_id)}
        seen_titles = set()

        for m in combined:
            m_id = str(m.get("tmdb_id") or m.get("id"))
            m_title_norm = _normalize_title_str(m.get("title", ""))

            if m_id in seen_ids or m_title_norm in seen_titles:
                continue

            seen_ids.add(m_id)
            seen_titles.add(m_title_norm)
            m["similarity"] = None
            unique_results.append(m)

            if len(unique_results) >= limit:
                break

        return unique_results

    # ── Enrichment & Batch Processing with Deduplication ──────────────

    def enrich_movie(self, movie: Dict[str, Any], full_details: bool = False) -> Dict[str, Any]:
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

        # Fast path for already-populated movies in batch list views
        if not full_details and movie.get("poster") and str(movie["poster"]).startswith("http") and movie.get("rating") and (movie.get("tmdb_id") or movie.get("is_tmdb")):
            m = dict(movie)
            if curated:
                for k in ["poster", "backdrop", "trailerId", "director", "year", "rating", "genres"]:
                    if k in curated and curated[k]:
                        m[k] = curated[k]
            return m

        raw_id = movie.get("id") or movie.get("movie_id")
        tmdb_id: Optional[int] = None
        if movie.get("tmdb_id") and str(movie["tmdb_id"]).isdigit():
            tmdb_id = int(movie["tmdb_id"])
        elif movie.get("is_tmdb") and raw_id and str(raw_id).isdigit():
            tmdb_id = int(raw_id)
        else:
            # Resolve actual TMDB ID by intelligent title matching
            tmdb_id = self.find_tmdb_id(
                title=title,
                year=movie.get("year", 0),
                language=movie.get("language", "")
            )

        if tmdb_id:
            details = self.get_movie_details(tmdb_id, full_details=full_details)
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
            fallback["rating"] = self._get_curated(title, "rating") or 0.0
        fallback["rating_source"] = "IMDb" if movie.get("imdb_id") else "TMDB"
        if not fallback.get("poster") or not str(fallback["poster"]).startswith("http"):
            fallback["poster"] = self._get_curated(title, "poster") or _get_unique_poster(title)
        if not fallback.get("backdrop") or not str(fallback["backdrop"]).startswith("http"):
            fallback["backdrop"] = self._get_curated(title, "backdrop") or DEFAULT_BACKDROP
        if not fallback.get("trailerId") or fallback["trailerId"] in ("none", "dQw4w9WgXcQ", ""):
            fallback["trailerId"] = self._get_curated(title, "trailerId") or ""
        return fallback

    def enrich_movies_batch(
        self,
        movies: List[Dict[str, Any]],
        deduplicate: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Enriches a list of movies with TMDB metadata.
        Crucial: Applies post-enrichment deduplication by TMDB ID and normalized title
        so that multiple dataset records resolving to the same TMDB movie only produce ONE card.
        """
        if not movies:
            return []

        if not self.is_configured():
            enriched_list = [self.enrich_movie(m) for m in movies]
        else:
            with ThreadPoolExecutor(max_workers=min(len(movies), 20)) as executor:
                enriched_list = list(executor.map(self.enrich_movie, movies))

        if not deduplicate:
            return enriched_list

        # Strict post-enrichment deduplication
        unique_results: List[Dict[str, Any]] = []
        seen_tmdb_ids = set()
        seen_titles = set()

        for m in enriched_list:
            t_id = m.get("tmdb_id") or m.get("id")
            t_id_str = str(t_id) if t_id else ""
            t_norm = _normalize_title_str(m.get("title", ""))

            # If TMDB ID already seen, skip duplicate
            if t_id_str and t_id_str in seen_tmdb_ids:
                continue

            # If title is identical and year is identical, skip duplicate
            t_year = m.get("year", 0)
            title_year_key = f"{t_norm}_{t_year}"
            if title_year_key in seen_titles:
                continue

            if t_id_str:
                seen_tmdb_ids.add(t_id_str)
            seen_titles.add(title_year_key)
            unique_results.append(m)

        return unique_results

    # ── Discovery Endpoints ─────────────────────────────────────────

    def get_trending(self, limit: int = 20) -> List[Dict[str, Any]]:
        cache_key = f"trending_{limit}"
        now = time.time()
        if cache_key in self._endpoints_cache:
            ts, data = self._endpoints_cache[cache_key]
            if now - ts < 900:
                return data
        data = self._get("/trending/movie/week")
        results = [self._fmt(m) for m in (data or {}).get("results", [])] if data else []
        final_list = self._deduplicate_list(results)[:limit]
        self._endpoints_cache[cache_key] = (now, final_list)
        return final_list

    def get_now_playing(self, limit: int = 20) -> List[Dict[str, Any]]:
        cache_key = f"now_playing_{limit}"
        now = time.time()
        if cache_key in self._endpoints_cache:
            ts, data = self._endpoints_cache[cache_key]
            if now - ts < 900:
                return data
        data = self._get("/movie/now_playing", {"region": "IN"}) or self._get("/movie/now_playing")
        results = [self._fmt(m) for m in (data or {}).get("results", [])] if data else []
        final_list = self._deduplicate_list(results)[:limit]
        self._endpoints_cache[cache_key] = (now, final_list)
        return final_list

    def get_popular(self, limit: int = 20) -> List[Dict[str, Any]]:
        cache_key = f"popular_{limit}"
        now = time.time()
        if cache_key in self._endpoints_cache:
            ts, data = self._endpoints_cache[cache_key]
            if now - ts < 900:
                return data
        data = self._get("/movie/popular", {"region": "IN"}) or self._get("/movie/popular")
        results = [self._fmt(m) for m in (data or {}).get("results", [])] if data else []
        final_list = self._deduplicate_list(results)[:limit]
        self._endpoints_cache[cache_key] = (now, final_list)
        return final_list

    def get_top_rated(self, limit: int = 20) -> List[Dict[str, Any]]:
        cache_key = f"top_rated_{limit}"
        now = time.time()
        if cache_key in self._endpoints_cache:
            ts, data = self._endpoints_cache[cache_key]
            if now - ts < 900:
                return data
        data = self._get("/movie/top_rated")
        results = [self._fmt(m) for m in (data or {}).get("results", [])] if data else []
        final_list = self._deduplicate_list(results)[:limit]
        self._endpoints_cache[cache_key] = (now, final_list)
        return final_list

    def get_upcoming(self, limit: int = 20) -> List[Dict[str, Any]]:
        cache_key = f"upcoming_{limit}"
        now = time.time()
        if cache_key in self._endpoints_cache:
            ts, data = self._endpoints_cache[cache_key]
            if now - ts < 900:
                return data
        data = self._get("/movie/upcoming", {"region": "IN"}) or self._get("/movie/upcoming")
        results = [self._fmt(m) for m in (data or {}).get("results", [])] if data else []
        final_list = self._deduplicate_list(results)[:limit]
        self._endpoints_cache[cache_key] = (now, final_list)
        return final_list

    def get_tamil_movies(self, limit: int = 50) -> List[Dict[str, Any]]:
        cache_key = f"tamil_{limit}"
        now = time.time()
        if cache_key in self._endpoints_cache:
            ts, data = self._endpoints_cache[cache_key]
            if now - ts < 900:
                return data
        data = self._get("/discover/movie", {"with_original_language": "ta", "sort_by": "popularity.desc", "page": "1"})
        results = [self._fmt(m) for m in (data or {}).get("results", [])] if data else []
        final_list = self._deduplicate_list(results)[:limit]
        self._endpoints_cache[cache_key] = (now, final_list)
        return final_list

    def search_tmdb(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        q = query.strip()
        if not q:
            return self.get_popular(limit)

        cache_key = f"tmdb_search_{q.lower()}_{limit}"
        now = time.time()
        if cache_key in self._endpoints_cache:
            ts, data = self._endpoints_cache[cache_key]
            if now - ts < 900:
                return data

        data = self._get("/search/movie", {"query": q, "include_adult": "false"})
        results = (data or {}).get("results", [])

        # Spelling Relaxation for few/no results
        if len(results) < 3:
            q_lower = q.lower()
            variants: List[str] = []

            # De-duplicate repeated characters (e.g. vikramm -> vikram)
            clean_v = re.sub(r"([a-z])\1+", r"\1", q_lower)
            if clean_v != q_lower:
                variants.append(clean_v)

            # Phonetic / vowel adjustments
            v2 = q_lower.replace("ee", "i").replace("oo", "u").replace("ai", "ay").replace("aa", "a")
            if v2 != q_lower and v2 not in variants:
                variants.append(v2)

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

        q_clean = _normalize_title_str(q)
        q_tokens, q_nums = _extract_tokens_and_numbers(q)

        def score_tmdb_item(item: Dict[str, Any]) -> float:
            m_title = item.get("title") or ""
            m_orig = item.get("original_title") or ""
            m_clean = _normalize_title_str(m_title)
            m_orig_clean = _normalize_title_str(m_orig)

            score = 0.0
            if m_clean == q_clean or m_orig_clean == q_clean:
                score += 1000.0
            elif m_clean.startswith(q_clean) or m_orig_clean.startswith(q_clean):
                score += 500.0
            elif q_clean in m_clean or q_clean in m_orig_clean:
                score += 300.0

            ratio1 = difflib.SequenceMatcher(None, q_clean, m_clean).ratio() if m_clean else 0.0
            ratio2 = difflib.SequenceMatcher(None, q_clean, m_orig_clean).ratio() if m_orig_clean else 0.0
            max_ratio = max(ratio1, ratio2)

            if max_ratio >= 0.85:
                score += 450.0 * max_ratio
            elif max_ratio >= 0.70:
                score += 280.0 * max_ratio
            elif max_ratio >= 0.55:
                score += 120.0 * max_ratio

            # Number alignment
            m_tokens, m_nums = _extract_tokens_and_numbers(m_title)
            if q_nums:
                if q_nums == m_nums:
                    score += 150.0
                elif not q_nums.intersection(m_nums):
                    score -= 150.0
            else:
                if m_nums:
                    score -= 100.0

            # Tie breaker and popularity ranking
            score += float(item.get("vote_average", 0.0) or 0.0) * 1.5
            score += min(float(item.get("vote_count", 0) or 0) * 0.5, 300.0)
            score += min(float(item.get("popularity", 0.0) or 0.0) * 4.0, 400.0)
            return score

        results.sort(key=score_tmdb_item, reverse=True)
        formatted_list = [self._fmt(m) for m in results]
        final_list = self._deduplicate_list(formatted_list)[:limit]
        self._endpoints_cache[cache_key] = (now, final_list)
        return final_list

    def _deduplicate_list(self, movies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        unique = []
        seen_ids = set()
        seen_titles = set()
        for m in movies:
            m_id = str(m.get("tmdb_id") or m.get("id"))
            m_norm = _normalize_title_str(m.get("title", ""))
            m_year = m.get("year", 0)
            t_key = f"{m_norm}_{m_year}"
            if m_id in seen_ids or t_key in seen_titles:
                continue
            seen_ids.add(m_id)
            seen_titles.add(t_key)
            unique.append(m)
        return unique

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
        votes = int(m.get("vote_count", 0) or 0)
        rating = round(vote_avg, 1) if (votes > 0 and vote_avg > 0) else (self._get_curated(title, "rating") or 0.0)

        return {
            "id": m.get("id", 0),
            "movie_id": m.get("id", 0),
            "tmdb_id": m.get("id", 0),
            "title": title,
            "original_title": m.get("original_title") or title,
            "year": year,
            "release_date": rel_date,
            "rating": rating,
            "votes": votes,
            "language": lang_map.get(ol, ol.upper()),
            "original_language": ol,
            "spoken_languages": [ol] if ol else [],
            "language_match": None,
            "genres": ["Drama"],
            "runtime": "2h 00m",
            "runtime_minutes": 120,
            "overview": m.get("overview") or f"{title} is a cinematic presentation.",
            "tagline": "",
            "status": "Released" if year and year <= 2025 else "Upcoming",
            "director": "Various",
            "poster": poster,
            "backdrop": backdrop,
            "trailerId": self._get_curated(title, "trailerId") or "",
            "cast": [],
            "budget_crores": 0.0,
            "revenue_crores": 0.0,
            "popularity": float(m.get("popularity", 10.0) or 10.0),
            "imdb_id": "",
            "rating_source": "TMDB",
            "streaming": [],
            "similarity": None
        }


tmdb_service = TMDBService()
