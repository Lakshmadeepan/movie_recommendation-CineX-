"""
CineX Movie Dataset Cleaning & Merging Pipeline
===============================================
Cleans and combines:
1. Primary Dataset: dataset/movie_dataset/Movies (1970-2023).csv (21,895 rows)
2. Second Dataset: dataset/movie_dataset/movie_dataset_2/tamil_movies_2015_2026.csv (2,333 rows)

Generates:
- dataset/cleaned_movies.csv (Unified Master CSV)
- dataset/cleaned_tamil_movies.csv (Dedicated Cleaned Tamil CSV)
- backend/data/movies.json (Complete production dataset for CineX API & Recommender)
"""

import os
import re
import ast
import json
import html
import unicodedata
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np

# Curated High-Quality Genre Poster & Backdrop Fallbacks (Cinematic Unsplash URLs)
GENRE_MEDIA_FALLBACKS = {
    "action": {
        "poster": "https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=400&h=600&fit=crop&auto=format",
        "backdrop": "https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=1400&h=600&fit=crop&auto=format"
    },
    "drama": {
        "poster": "https://images.unsplash.com/photo-1485846234645-a62644f84728?w=400&h=600&fit=crop&auto=format",
        "backdrop": "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=1400&h=600&fit=crop&auto=format"
    },
    "comedy": {
        "poster": "https://images.unsplash.com/photo-1514306191717-452ec28c7814?w=400&h=600&fit=crop&auto=format",
        "backdrop": "https://images.unsplash.com/photo-1518173946687-a4c8a383392e?w=1400&h=600&fit=crop&auto=format"
    },
    "thriller": {
        "poster": "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=400&h=600&fit=crop&auto=format",
        "backdrop": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=1400&h=600&fit=crop&auto=format"
    },
    "romance": {
        "poster": "https://images.unsplash.com/photo-1518895949257-7621c3c786d7?w=400&h=600&fit=crop&auto=format",
        "backdrop": "https://images.unsplash.com/photo-1518199266791-5375a83190b7?w=1400&h=600&fit=crop&auto=format"
    },
    "sci-fi": {
        "poster": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=400&h=600&fit=crop&auto=format",
        "backdrop": "https://images.unsplash.com/photo-1506703719100-a0f3a48c0f86?w=1400&h=600&fit=crop&auto=format"
    },
    "horror": {
        "poster": "https://images.unsplash.com/photo-1509248961158-e54f6934749c?w=400&h=600&fit=crop&auto=format",
        "backdrop": "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=1400&h=600&fit=crop&auto=format"
    },
    "crime": {
        "poster": "https://images.unsplash.com/photo-1478720568477-152d9b164e26?w=400&h=600&fit=crop&auto=format",
        "backdrop": "https://images.unsplash.com/photo-1518929458119-e5bf444c30f4?w=1400&h=600&fit=crop&auto=format"
    },
    "adventure": {
        "poster": "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=400&h=600&fit=crop&auto=format",
        "backdrop": "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=1400&h=600&fit=crop&auto=format"
    },
    "animation": {
        "poster": "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=400&h=600&fit=crop&auto=format",
        "backdrop": "https://images.unsplash.com/photo-1579783902614-a3fb3927b675?w=1400&h=600&fit=crop&auto=format"
    },
    "fantasy": {
        "poster": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=400&h=600&fit=crop&auto=format",
        "backdrop": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=1400&h=600&fit=crop&auto=format"
    },
    "mystery": {
        "poster": "https://images.unsplash.com/photo-1500462918059-b1a0cb512f1d?w=400&h=600&fit=crop&auto=format",
        "backdrop": "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=1400&h=600&fit=crop&auto=format"
    },
    "default": {
        "poster": "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=400&h=600&fit=crop&auto=format",
        "backdrop": "https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=1400&h=600&fit=crop&auto=format"
    }
}

# Avatar photos for cast members
DEFAULT_CAST_PHOTOS = [
    "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&h=200&fit=crop&auto=format",
    "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200&h=200&fit=crop&auto=format",
    "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=200&h=200&fit=crop&auto=format",
    "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=200&h=200&fit=crop&auto=format",
    "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=200&h=200&fit=crop&auto=format",
    "https://images.unsplash.com/photo-1519345182560-3f2917c472ef?w=200&h=200&fit=crop&auto=format",
    "https://images.unsplash.com/photo-1520813792240-56fc4a3765a7?w=200&h=200&fit=crop&auto=format"
]

# Standard streaming platform assignments
STREAMING_PLATFORMS = [
    {"name": "Amazon Prime", "logo": "▶", "color": "#00A8E1"},
    {"name": "Netflix", "logo": "N", "color": "#E50914"},
    {"name": "Disney+ Hotstar", "logo": "✦", "color": "#0A3CA8"},
    {"name": "Zee5", "logo": "Z", "color": "#8230C6"},
    {"name": "SonyLIV", "logo": "S", "color": "#FF5722"},
    {"name": "Apple TV+", "logo": "", "color": "#000000"}
]


def clean_text(text: Any) -> str:
    """Clean and normalize string, fix mojibake and HTML entities."""
    if text is None or pd.isna(text):
        return ""
    s = str(text)
    # Decode HTML entities
    s = html.unescape(s)
    # Replace common mojibake characters
    s = s.replace("\ufffd", "'")
    s = s.replace("\u2018", "'").replace("\u2019", "'")
    s = s.replace("\u201c", '"').replace("\u201d", '"')
    s = s.replace("\u2014", "—").replace("\u2013", "–")
    # Normalize unicode
    s = unicodedata.normalize("NFKD", s)
    # Normalize whitespace
    s = re.sub(r"\s+", " ", s).strip()
    return s


def clean_title_and_year(raw_title: Any, raw_year: Any) -> Tuple[str, int]:
    """Clean movie title, strip ': (YYYY)' and extract year."""
    title = clean_text(raw_title)
    extracted_year = None

    # Check for YYYY at end of title: ': (YYYY)' or ' (YYYY)'
    m = re.search(r':?\s*\((\d{4})\)\s*$', title)
    if m:
        extracted_year = int(m.group(1))
        title = title[:m.start()].strip()
    
    # Strip any trailing ' - IMDb: (<NA>)' or ' - IMDb: ...'
    title = re.sub(r'\s*-\s*IMDb.*$', '', title, flags=re.IGNORECASE).strip()
    # Strip any lingering ': (<NA>)'
    title = re.sub(r':?\s*\(<NA>\)\s*$', '', title).strip()

    # Determine year
    final_year = 2000
    if raw_year is not None and not pd.isna(raw_year):
        try:
            y = int(float(raw_year))
            if 1900 <= y <= 2030:
                final_year = y
            elif extracted_year:
                final_year = extracted_year
        except Exception:
            if extracted_year:
                final_year = extracted_year
    elif extracted_year:
        final_year = extracted_year

    return title if title else "Untitled Movie", final_year


def clean_plot(raw_plot: Any, title: str, genres: List[str]) -> str:
    """Clean plot/overview, remove author tags, impute if missing."""
    plot = clean_text(raw_plot)
    # Strip author tags like '—rAjOo (gunwanti@hotmail.com)', 'Written by...', etc.
    plot = re.sub(r'\s*[—–-]\s*[a-zA-Z0-9_.]+\s*\([^)]*@.*\)\s*$', '', plot)
    plot = re.sub(r'\s*Written\s+by\s+.*$', '', plot, flags=re.IGNORECASE)
    plot = re.sub(r'\s*\(gunwanti@hotmail\.com\)', '', plot, flags=re.IGNORECASE)
    plot = plot.strip()

    if not plot or len(plot) < 15:
        # Generate clean descriptive fallback synopsis
        genre_desc = ", ".join(genres) if genres else "cinematic drama"
        plot = f"{title} is an engaging {genre_desc} featuring compelling characters, intense narratives, and captivating storytelling."
    
    return plot


def parse_genres(raw_genres: Any) -> List[str]:
    """Parse genres from Python list string or comma-separated string."""
    if raw_genres is None or pd.isna(raw_genres):
        return ["Drama"]
    
    s = str(raw_genres).strip()
    genres_list = []

    # Try literal eval for "['Action', 'Comedy']"
    if s.startswith("[") and s.endswith("]"):
        try:
            parsed = ast.literal_eval(s)
            if isinstance(parsed, (list, tuple)):
                genres_list = [clean_text(g) for g in parsed if clean_text(g)]
        except Exception:
            genres_list = re.findall(r"'([^']+)'|\"([^\"]+)\"", s)
            genres_list = [clean_text(g[0] or g[1]) for g in genres_list if (g[0] or g[1])]
    
    if not genres_list:
        # Try comma-separated
        parts = s.split(",")
        genres_list = [clean_text(p) for p in parts if clean_text(p)]

    # Standardize names
    standardized = []
    genre_alias_map = {
        "sci_fi": "Sci-Fi",
        "scifi": "Sci-Fi",
        "science fiction": "Sci-Fi",
        "romantic": "Romance",
        "musical": "Music",
        "action & adventure": "Action"
    }

    for g in genres_list:
        g_clean = g.strip().title()
        lower_g = g_clean.lower()
        if lower_g in genre_alias_map:
            g_clean = genre_alias_map[lower_g]
        if g_clean and g_clean not in standardized and len(g_clean) > 1:
            standardized.append(g_clean)

    return standardized if standardized else ["Drama"]


def parse_cast(raw_cast: Any) -> Tuple[List[str], List[Dict[str, str]]]:
    """Parse cast into clean list of names and structured cast objects."""
    if raw_cast is None or pd.isna(raw_cast):
        return [], []

    s = str(raw_cast).strip()
    names = []

    # Check if list string
    if s.startswith("[") and s.endswith("]"):
        try:
            parsed = ast.literal_eval(s)
            if isinstance(parsed, (list, tuple)):
                names = [clean_text(n) for n in parsed if clean_text(n)]
        except Exception:
            matches = re.findall(r"'([^']+)'|\"([^\"]+)\"", s)
            names = [clean_text(m[0] or m[1]) for m in matches if (m[0] or m[1])]
    
    if not names:
        parts = s.split(",")
        names = [clean_text(p) for p in parts if clean_text(p)]

    # Clean & deduplicate names
    clean_names = []
    for n in names:
        if n and n not in clean_names and len(n) > 1 and not n.isdigit():
            clean_names.append(n)

    # Build rich cast objects (top 6 actors)
    structured_cast = []
    for idx, name in enumerate(clean_names[:6]):
        photo = DEFAULT_CAST_PHOTOS[idx % len(DEFAULT_CAST_PHOTOS)]
        structured_cast.append({
            "name": name,
            "role": "Lead Cast" if idx == 0 else "Supporting Cast",
            "photo": photo
        })

    return clean_names, structured_cast


def parse_runtime(raw_runtime: Any) -> Tuple[str, int]:
    """Parse runtime into formatted 'Xh Ym' and integer minutes."""
    if raw_runtime is None or pd.isna(raw_runtime):
        return "2h 00m", 120
    
    s = str(raw_runtime).strip()
    mins = 120
    m = re.search(r'(\d+)', s)
    if m:
        val = int(m.group(1))
        if 15 <= val <= 400:
            mins = val
        elif val > 400:
            mins = 150

    h = mins // 60
    rem_m = mins % 60
    return f"{h}h {rem_m:02d}m", mins


def extract_trailer_id(raw_trailer: Any) -> str:
    """Extract YouTube video ID from embed URL or link."""
    if raw_trailer is None or pd.isna(raw_trailer):
        return ""
    s = str(raw_trailer).strip()
    m = re.search(r'(?:embed/|v=|youtu\.be/|vi/|watch\?v=)([a-zA-Z0-9_-]{11})', s)
    if m:
        return m.group(1)
    if len(s) == 11 and re.match(r'^[a-zA-Z0-9_-]+$', s):
        return s
    return ""


def standardize_language(lang_cinema: Any, languages_raw: Any) -> str:
    """Map language cinema / languages to standard language name."""
    cinema_str = clean_text(lang_cinema).title()
    
    cinema_map = {
        "American": "English",
        "Hollywood": "English",
        "English": "English",
        "Hindi": "Hindi",
        "Tamil": "Tamil",
        "Telugu": "Telugu",
        "Kannada": "Kannada",
        "Marathi": "Marathi",
        "Malayalam": "Malayalam",
        "Bengali": "Bengali"
    }

    if cinema_str in cinema_map:
        return cinema_map[cinema_str]

    # Try checking languages_raw
    if languages_raw and not pd.isna(languages_raw):
        s = str(languages_raw)
        for key, val in cinema_map.items():
            if key.lower() in s.lower():
                return val

    return "English"


def get_movie_media(poster_url: Any, genres: List[str], movie_id: int) -> Tuple[str, str]:
    """Get valid high quality poster and backdrop image URLs."""
    primary_genre = genres[0].lower() if genres else "default"
    fallback = GENRE_MEDIA_FALLBACKS.get(primary_genre, GENRE_MEDIA_FALLBACKS["default"])
    
    poster = fallback["poster"]
    if poster_url and not pd.isna(poster_url):
        p_str = str(poster_url).strip()
        if p_str.startswith("http") and ("amazon.com" in p_str or "media-amazon" in p_str or "tmdb.org" in p_str or "unsplash.com" in p_str):
            poster = p_str
    
    backdrop = fallback["backdrop"]
    return poster, backdrop


def get_streaming_platforms(movie_id: int, rating: float) -> List[Dict[str, str]]:
    """Assign plausible streaming platforms based on movie properties."""
    p1 = STREAMING_PLATFORMS[movie_id % len(STREAMING_PLATFORMS)]
    p2 = STREAMING_PLATFORMS[(movie_id + 2) % len(STREAMING_PLATFORMS)]
    if rating >= 7.5:
        return [p1, p2]
    return [p1]


def clean_and_merge_datasets():
    print("=" * 80)
    print("STARTING CINEX MOVIE DATASET CLEANING & ETL PIPELINE")
    print("=" * 80)

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    d1_path = os.path.join(base_dir, "dataset", "movie_dataset", "Movies (1970-2023).csv")
    d2_path = os.path.join(base_dir, "dataset", "movie_dataset", "movie_dataset_2", "tamil_movies_2015_2026.csv")

    if not os.path.exists(d1_path):
        raise FileNotFoundError(f"Dataset 1 not found at {d1_path}")
    if not os.path.exists(d2_path):
        raise FileNotFoundError(f"Dataset 2 not found at {d2_path}")

    print(f"\n[1] Loading Dataset 1: {d1_path}")
    df1 = pd.read_csv(d1_path, low_memory=False)
    print(f"    Loaded {len(df1):,} rows, {len(df1.columns)} columns.")

    print(f"\n[2] Loading Dataset 2: {d2_path}")
    df2 = pd.read_csv(d2_path, low_memory=False)
    print(f"    Loaded {len(df2):,} rows, {len(df2.columns)} columns.")

    # -------------------------------------------------------------
    # PROCESS DATASET 2 FIRST (High Quality Tamil Movies 2015-2026)
    # -------------------------------------------------------------
    print("\n[3] Cleaning Dataset 2 (Tamil Movies 2015-2026)...")
    d2_movies_map = {}  # key: (normalized_title, year) -> dict

    for idx, row in df2.iterrows():
        raw_title = row.get("Title", "")
        raw_year = row.get("Release_Year", 2020)
        title, year = clean_title_and_year(raw_title, raw_year)
        
        genres = parse_genres(row.get("Genres"))
        cast_names, cast_structured = parse_cast(row.get("Cast"))
        director = clean_text(row.get("Director")) or "Unknown Director"
        plot = clean_plot(row.get("Overview"), title, genres)
        runtime_str, runtime_mins = parse_runtime(row.get("Runtime_Minutes", 150))
        
        # Ratings
        try:
            rating = round(float(row.get("Vote_Average", 6.5)), 1)
            if rating <= 0 or rating > 10:
                rating = 6.5
        except Exception:
            rating = 6.5

        try:
            votes = int(float(row.get("Vote_Count", 100)))
        except Exception:
            votes = 100

        try:
            budget_cr = round(float(row.get("Budget_Crores", 0.0)), 2)
            revenue_cr = round(float(row.get("Revenue_Crores", 0.0)), 2)
            popularity = round(float(row.get("Popularity_Score", 10.0)), 2)
            roi = round(float(row.get("ROI_Percent", 0.0)), 2)
        except Exception:
            budget_cr, revenue_cr, popularity, roi = 0.0, 0.0, 10.0, 0.0

        production = clean_text(row.get("Production_Company")) or ""
        
        # Normalized key for matching
        norm_title = re.sub(r'[^a-zA-Z0-9]', '', title.lower())
        key = (norm_title, year)

        d2_movies_map[key] = {
            "title": title,
            "year": year,
            "language": "Tamil",
            "genres": genres,
            "cast_names": cast_names,
            "cast": cast_structured,
            "director": director,
            "overview": plot,
            "runtime": runtime_str,
            "runtime_minutes": runtime_mins,
            "rating": rating,
            "votes": votes,
            "budget_crores": budget_cr,
            "revenue_crores": revenue_cr,
            "popularity": popularity,
            "roi_percent": roi,
            "production": production,
            "source": "dataset_2"
        }

    print(f"    Processed {len(d2_movies_map):,} unique records from Dataset 2.")

    # -------------------------------------------------------------
    # PROCESS DATASET 1 (Multi-Language Global Movies 1970-2023)
    # -------------------------------------------------------------
    print("\n[4] Cleaning Dataset 1 (Movies 1970-2023) & Merging...")
    
    cleaned_master = []
    seen_keys = set()
    matched_d2_keys = set()
    next_id = 1

    for idx, row in df1.iterrows():
        raw_title = row.get("movie title", "")
        raw_year = row.get("year", None)
        title, year = clean_title_and_year(raw_title, raw_year)

        language = standardize_language(row.get("language cinema"), row.get("languages"))
        genres = parse_genres(row.get("genres"))
        cast_names, cast_structured = parse_cast(row.get("cast"))
        director = clean_text(row.get("director")) or "Unknown Director"
        plot = clean_plot(row.get("plot"), title, genres)
        runtime_str, runtime_mins = parse_runtime(row.get("runtime"))
        
        # Rating & votes
        try:
            r_val = float(row.get("rating"))
            rating = round(r_val, 1) if not pd.isna(r_val) and 0 <= r_val <= 10 else 6.5
        except Exception:
            rating = 6.5

        try:
            v_val = float(row.get("votes"))
            votes = int(v_val) if not pd.isna(v_val) and v_val >= 0 else 500
        except Exception:
            votes = 500

        imdb_id = str(row.get("imdb id", "")).strip()
        trailer_id = extract_trailer_id(row.get("trailer"))
        poster_raw = row.get("poster")
        poster, backdrop = get_movie_media(poster_raw, genres, next_id)

        norm_title = re.sub(r'[^a-zA-Z0-9]', '', title.lower())
        key = (norm_title, year)

        # Check if already in cleaned_master (deduplication)
        dedup_key = (norm_title, year, language)
        if dedup_key in seen_keys:
            continue
        seen_keys.add(dedup_key)

        # Check for merge with Dataset 2 (Tamil movie overlap)
        matched_d2 = None
        if key in d2_movies_map:
            matched_d2 = d2_movies_map[key]
            matched_d2_keys.add(key)
        elif language == "Tamil":
            # Search by title only if year is within 1 year
            for (t_k, y_k), d2_entry in d2_movies_map.items():
                if t_k == norm_title and abs(y_k - year) <= 1:
                    matched_d2 = d2_entry
                    matched_d2_keys.add((t_k, y_k))
                    break

        if matched_d2:
            # Intelligent Merge:
            # 1. Overview: Pick whichever is longer / richer
            if len(matched_d2["overview"]) > len(plot):
                plot = matched_d2["overview"]
            # 2. Genres: Union of genres
            all_genres = list(dict.fromkeys(genres + matched_d2["genres"]))
            # 3. Cast: Combine cast
            all_cast_names = list(dict.fromkeys(cast_names + matched_d2["cast_names"]))
            if matched_d2["cast"]:
                cast_structured = matched_d2["cast"]
            # 4. Ratings: weighted average
            if matched_d2["rating"] > 0:
                rating = round((rating * 0.5) + (matched_d2["rating"] * 0.5), 1)
            # 5. Financials & Popularity
            budget_cr = matched_d2["budget_crores"]
            revenue_cr = matched_d2["revenue_crores"]
            popularity = matched_d2["popularity"]
        else:
            all_genres = genres
            budget_cr = 0.0
            revenue_cr = 0.0
            # Cap popularity at 50 for D1-only movies (no real TMDB score)
            # so they don't outrank D2 Tamil movies that have real TMDB popularity scores
            raw_pop = float(rating * 3.0 + min(votes / 5000.0, 20.0))
            popularity = round(min(raw_pop, 50.0), 1)

        streaming = get_streaming_platforms(next_id, rating)

        cleaned_master.append({
            "id": next_id,
            "title": title,
            "year": year,
            "rating": rating,
            "votes": votes,
            "language": language,
            "genres": all_genres,
            "runtime": runtime_str,
            "runtime_minutes": runtime_mins,
            "overview": plot,
            "tagline": f"Experience the acclaimed {language} {all_genres[0]} masterwork." if all_genres else "A cinematic journey.",
            "director": director,
            "poster": poster,
            "backdrop": backdrop,
            "trailerId": trailer_id if trailer_id else "dQw4w9WgXcQ",
            "cast": cast_structured,
            "budget_crores": budget_cr,
            "revenue_crores": revenue_cr,
            "popularity": popularity,
            "imdb_id": imdb_id,
            "streaming": streaming
        })
        next_id += 1

    print(f"    Cleaned & deduplicated Dataset 1 into {len(cleaned_master):,} records.")
    print(f"    Merged with {len(matched_d2_keys):,} overlapping Tamil movies from Dataset 2.")

    # -------------------------------------------------------------
    # ADD REMAINING DATASET 2 TAMIL MOVIES (Non-overlapping 2015-2026)
    # -------------------------------------------------------------
    print("\n[5] Adding non-overlapping modern Tamil movies (2015-2026) from Dataset 2...")
    added_d2_count = 0

    for key, d2_entry in d2_movies_map.items():
        if key in matched_d2_keys:
            continue
        
        dedup_key = (key[0], d2_entry["year"], "Tamil")
        if dedup_key in seen_keys:
            continue
        seen_keys.add(dedup_key)

        poster, backdrop = get_movie_media(None, d2_entry["genres"], next_id)
        streaming = get_streaming_platforms(next_id, d2_entry["rating"])

        cleaned_master.append({
            "id": next_id,
            "title": d2_entry["title"],
            "year": d2_entry["year"],
            "rating": d2_entry["rating"],
            "votes": d2_entry["votes"],
            "language": "Tamil",
            "genres": d2_entry["genres"],
            "runtime": d2_entry["runtime"],
            "runtime_minutes": d2_entry["runtime_minutes"],
            "overview": d2_entry["overview"],
            "tagline": f"Tamil {d2_entry['genres'][0]} hit released in {d2_entry['year']}." if d2_entry['genres'] else "Tamil cinema presentation.",
            "director": d2_entry["director"],
            "poster": poster,
            "backdrop": backdrop,
            "trailerId": "dQw4w9WgXcQ",
            "cast": d2_entry["cast"],
            "budget_crores": d2_entry["budget_crores"],
            "revenue_crores": d2_entry["revenue_crores"],
            "popularity": d2_entry["popularity"],
            "imdb_id": "",
            "streaming": streaming
        })
        next_id += 1
        added_d2_count += 1

    print(f"    Added {added_d2_count:,} brand-new Tamil movies from Dataset 2.")
    print(f"    TOTAL UNIFIED MASTER MOVIES: {len(cleaned_master):,}")

    # -------------------------------------------------------------
    # EXPORT CLEANED OUTPUTS
    # -------------------------------------------------------------
    print("\n[6] Exporting Cleaned Datasets...")

    # 1. Master JSON for Backend & Recommender
    data_dir = os.path.join(base_dir, "backend", "data")
    os.makedirs(data_dir, exist_ok=True)
    json_path = os.path.join(data_dir, "movies.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(cleaned_master, f, indent=2, ensure_ascii=False)
    print(f"    -> Successfully written {json_path} ({os.path.getsize(json_path) / 1024 / 1024:.2f} MB)")

    # 2. Master Cleaned CSV
    master_df = pd.DataFrame([
        {
            "id": m["id"],
            "title": m["title"],
            "year": m["year"],
            "rating": m["rating"],
            "votes": m["votes"],
            "language": m["language"],
            "genres": ", ".join(m["genres"]),
            "runtime": m["runtime"],
            "runtime_minutes": m["runtime_minutes"],
            "director": m["director"],
            "cast": ", ".join([c["name"] for c in m["cast"]]),
            "overview": m["overview"],
            "poster": m["poster"],
            "backdrop": m["backdrop"],
            "trailerId": m["trailerId"],
            "budget_crores": m["budget_crores"],
            "revenue_crores": m["revenue_crores"],
            "popularity": m["popularity"],
            "imdb_id": m["imdb_id"]
        }
        for m in cleaned_master
    ])

    out_csv_path = os.path.join(base_dir, "dataset", "cleaned_movies.csv")
    master_df.to_csv(out_csv_path, index=False, encoding="utf-8")
    print(f"    -> Successfully written {out_csv_path} ({len(master_df):,} rows)")

    # 3. Dedicated Cleaned Tamil Movies CSV
    tamil_df = master_df[master_df["language"] == "Tamil"]
    tamil_csv_path = os.path.join(base_dir, "dataset", "cleaned_tamil_movies.csv")
    tamil_df.to_csv(tamil_csv_path, index=False, encoding="utf-8")
    print(f"    -> Successfully written {tamil_csv_path} ({len(tamil_df):,} Tamil rows)")

    # -------------------------------------------------------------
    # DATASET QUALITY & SUMMARY REPORT
    # -------------------------------------------------------------
    print("\n" + "=" * 80)
    print("DATASET CLEANING & INTEGRATION SUMMARY")
    print("=" * 80)
    print(f"Total Unified Movies : {len(cleaned_master):,}")
    print("\nLanguage Breakdown:")
    for lang, count in master_df["language"].value_counts().items():
        print(f"  - {lang:<15}: {count:6,d} movies ({count / len(master_df) * 100:5.1f}%)")

    print("\nTop 10 Genres:")
    all_genres_flattened = [g for m in cleaned_master for g in m["genres"]]
    for genre, count in pd.Series(all_genres_flattened).value_counts().head(10).items():
        print(f"  - {genre:<15}: {count:6,d} movies")

    print("\nRating Statistics:")
    print(f"  - Average Rating   : {master_df['rating'].mean():.2f}")
    print(f"  - Min / Max Rating : {master_df['rating'].min()} / {master_df['rating'].max()}")

    print("\nYear Range:")
    print(f"  - Earliest Year    : {master_df['year'].min()}")
    print(f"  - Latest Year      : {master_df['year'].max()}")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    clean_and_merge_datasets()
