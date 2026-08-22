import os
import re
from typing import List, Dict, Any, Optional, Tuple, Union

import joblib
import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors


class MovieRecommender:
    """
    Production-grade KNN Movie Recommendation Engine using TF-IDF feature matrix.
    Compatible with master_movies.csv / movies_features.csv and FastAPI / React frontend.
    """

    def __init__(self, data_path: Optional[str] = None):
        # Determine dataset directory and default paths
        base_dir = os.path.dirname(os.path.abspath(__file__))
        default_data_path = os.path.join(base_dir, "..", "dataset", "movies_features.csv")
        
        if data_path:
            if os.path.exists(data_path):
                self.data_path = os.path.abspath(data_path)
            elif os.path.exists(os.path.join(base_dir, data_path)):
                self.data_path = os.path.abspath(os.path.join(base_dir, data_path))
            else:
                self.data_path = data_path
        else:
            self.data_path = default_data_path

        # If pointing to movies.json or another file that doesn't exist/is json, fallback to movies_features.csv
        if (not os.path.exists(self.data_path) or self.data_path.endswith(".json")) and os.path.exists(default_data_path):
            self.data_path = default_data_path

        self.dataset_dir = os.path.dirname(self.data_path)
        self.df: pd.DataFrame = pd.DataFrame()
        self.movies: List[Dict[str, Any]] = []
        self.movie_map: Dict[Union[int, str], Dict[str, Any]] = {}
        self.indices_map: Dict[Union[int, str], int] = {}
        
        self.id_column: str = "id"
        self.feature_matrix = None
        self.vectorizer = None
        self.knn_model = None

        self.load_data()

    # ========================================================
    # DATA LOADING & INITIALIZATION
    # ========================================================

    def load_data(self):
        print(f"[MovieRecommender] Loading: {self.data_path}")

        if not os.path.exists(self.data_path):
            print(f"[MovieRecommender] ERROR: Dataset not found: {self.data_path}")
            return

        # Load CSV
        try:
            self.df = pd.read_csv(self.data_path, low_memory=False)
        except Exception as e:
            print(f"[MovieRecommender] ERROR reading CSV: {e}")
            return

        print(f"[MovieRecommender] Loaded {len(self.df):,} movies.")

        # Detect primary ID column
        if "id" in self.df.columns:
            self.id_column = "id"
        elif "movie_id" in self.df.columns:
            self.id_column = "movie_id"
        elif "imdb_id" in self.df.columns:
            self.id_column = "imdb_id"
        else:
            self.id_column = self.df.columns[0]

        print(f"[MovieRecommender] Detected ID column: '{self.id_column}'")

        # ----------------------------------------------------
        # Load Precomputed TF-IDF Matrix & Vectorizer
        # ----------------------------------------------------
        matrix_path = os.path.join(self.dataset_dir, "tfidf_matrix.pkl")
        vectorizer_path = os.path.join(self.dataset_dir, "tfidf_vectorizer.pkl")

        if os.path.exists(matrix_path):
            try:
                self.feature_matrix = joblib.load(matrix_path)
                print(f"[MovieRecommender] TF-IDF matrix shape: {self.feature_matrix.shape}")
            except Exception as e:
                print(f"[MovieRecommender] ERROR loading TF-IDF matrix: {e}")
        else:
            print(f"[MovieRecommender] WARNING: tfidf_matrix.pkl not found at {matrix_path}")

        if os.path.exists(vectorizer_path):
            try:
                self.vectorizer = joblib.load(vectorizer_path)
            except Exception as e:
                print(f"[MovieRecommender] WARNING loading vectorizer: {e}")

        # ----------------------------------------------------
        # Clean & Transform Dataset into standard Records
        # ----------------------------------------------------
        self._process_records()

        # ----------------------------------------------------
        # Fit KNN model with Cosine Distance
        # ----------------------------------------------------
        self._fit_knn()

    def _process_records(self):
        """Converts DataFrame into robust, cleanly structured movie dictionaries."""
        self.movies = []
        self.movie_map = {}
        self.indices_map = {}

        used_ids = set()

        for idx, row in self.df.iterrows():
            # Determine unique integer ID for compatibility
            raw_id = row.get(self.id_column, None)
            movie_id: int
            if pd.notna(raw_id) and str(raw_id).strip() != "" and str(raw_id).replace(".", "", 1).isdigit():
                try:
                    val = int(float(raw_id))
                    if val not in used_ids and val > 0:
                        movie_id = val
                    else:
                        movie_id = 1000000 + int(idx)
                except Exception:
                    movie_id = 1000000 + int(idx)
            else:
                movie_id = 1000000 + int(idx)

            used_ids.add(movie_id)

            # Title
            raw_title = str(row.get("title", "") if pd.notna(row.get("title")) else "").strip()
            title = raw_title.title() if raw_title.islower() else (raw_title or "Untitled")

            # Overview / Description
            raw_overview = row.get("overview", "")
            overview = str(raw_overview).strip() if pd.notna(raw_overview) else ""
            if not overview:
                overview = f"{title} is a cinematic presentation featuring compelling drama and storytelling."

            # Genres
            raw_genres = row.get("genres", "")
            if pd.isna(raw_genres) or not str(raw_genres).strip():
                genres_list = ["Drama"]
            else:
                g_str = str(raw_genres).replace(",", " ").strip()
                genres_list = [w.capitalize() for w in re.split(r"[\s,]+", g_str) if w]
                if not genres_list:
                    genres_list = ["Drama"]

            # Cast
            raw_cast = row.get("cast", "")
            cast_list = []
            if pd.notna(raw_cast) and str(raw_cast).strip():
                cast_names = [c.strip().title() for c in re.split(r"[,]+", str(raw_cast)) if c.strip()]
                if not cast_names:
                    cast_names = [w.capitalize() for w in str(raw_cast).split() if len(w) > 2]
                for c_name in cast_names[:6]:
                    cast_list.append({"name": c_name, "role": "Lead", "photo": ""})

            # Director
            raw_dir = row.get("director", "")
            director = str(raw_dir).strip().title() if pd.notna(raw_dir) and str(raw_dir).strip() else "Unknown Director"

            # Language
            raw_lang = row.get("language", "")
            if pd.notna(raw_lang) and str(raw_lang).strip():
                lang_val = str(raw_lang).strip().capitalize()
            else:
                lang_val = "Tamil"  # Default priority

            # Year
            raw_year = row.get("year", 0)
            try:
                year_val = int(float(raw_year)) if pd.notna(raw_year) else 0
            except Exception:
                year_val = 0

            # Rating
            raw_rating = row.get("rating", 0.0)
            try:
                rating_val = round(float(raw_rating), 1) if pd.notna(raw_rating) else 7.0
            except Exception:
                rating_val = 7.0

            # Votes
            raw_votes = row.get("votes", 0)
            try:
                votes_val = int(float(raw_votes)) if pd.notna(raw_votes) else 500
            except Exception:
                votes_val = 500

            # Runtime
            raw_runtime = row.get("runtime_minutes", 120)
            try:
                runtime_mins = int(float(raw_runtime)) if (pd.notna(raw_runtime) and float(raw_runtime) > 0) else 120
            except Exception:
                runtime_mins = 120
            runtime_str = f"{runtime_mins // 60}h {runtime_mins % 60}m" if runtime_mins >= 60 else f"{runtime_mins}m"

            # Financials & Popularity
            def safe_float(col_name: str, default: float = 0.0) -> float:
                val = row.get(col_name, default)
                try:
                    return float(val) if pd.notna(val) else default
                except Exception:
                    return default

            popularity = safe_float("popularity", 10.0)
            budget = safe_float("budget_crores", 0.0)
            revenue = safe_float("revenue_crores", 0.0)

            # Media URLs
            def safe_str(col_name: str) -> str:
                val = row.get(col_name, "")
                return str(val).strip() if pd.notna(val) else ""

            poster = safe_str("poster")
            backdrop = safe_str("backdrop")
            trailer = safe_str("trailer")
            imdb_id = safe_str("imdb_id")

            movie_record: Dict[str, Any] = {
                "id": movie_id,
                "movie_id": movie_id,
                "title": title,
                "raw_title": str(row.get("title", "")).strip().lower(),
                "year": year_val,
                "rating": rating_val,
                "votes": votes_val,
                "language": lang_val,
                "genres": genres_list,
                "runtime": runtime_str,
                "runtime_minutes": runtime_mins,
                "overview": overview,
                "tagline": "",
                "director": director,
                "poster": poster,
                "backdrop": backdrop,
                "trailerId": trailer or "",
                "cast": cast_list,
                "budget_crores": budget,
                "revenue_crores": revenue,
                "popularity": popularity,
                "imdb_id": imdb_id,
                "streaming": [],
                "_index": int(idx)
            }

            self.movies.append(movie_record)
            self.movie_map[movie_id] = movie_record
            self.movie_map[str(movie_id)] = movie_record
            self.indices_map[movie_id] = int(idx)
            self.indices_map[str(movie_id)] = int(idx)

    # ========================================================
    # KNN MODEL TRAINING
    # ========================================================

    def _fit_knn(self):
        if self.feature_matrix is None or len(self.movies) == 0:
            return

        n_neighbors = min(50, len(self.movies))
        self.knn_model = NearestNeighbors(
            n_neighbors=n_neighbors,
            metric="cosine",
            algorithm="brute"
        )
        self.knn_model.fit(self.feature_matrix)
        print("[MovieRecommender] KNN model fitted successfully.")

    # ========================================================
    # TEXT NORMALIZATION & CLEANING
    # ========================================================

    @staticmethod
    def clean_text(value: Any) -> str:
        """
        Clean and normalize text using the EXACT same rules as prepare_features.py.
        """
        if pd.isna(value) or value is None:
            return ""
        val = str(value).lower()
        val = re.sub(r"[^a-z0-9\s]", " ", val)
        val = re.sub(r"\s+", " ", val)
        return val.strip()

    @staticmethod
    def normalize_text(text: Any) -> str:
        if pd.isna(text) or text is None:
            return ""
        s = str(text).lower()
        s = re.sub(r"[^a-z0-9\s]", " ", s)
        s = re.sub(r"\s+", " ", s)
        return s.strip()

    @staticmethod
    def calculate_similarity_ratio(s1: str, s2: str) -> float:
        """Calculate string similarity ratio using difflib SequenceMatcher."""
        import difflib
        if not s1 or not s2:
            return 0.0
        return difflib.SequenceMatcher(None, s1, s2).ratio()

    # ========================================================
    # MOVIE SEARCH / LOOKUP (SMART FUZZY MATCHING)
    # ========================================================

    def find_movie(self, movie_title: str, min_similarity: float = 0.70) -> Optional[int]:
        """
        Finds row index for a given movie title string with fuzzy spelling tolerance.
        Priority:
        1. Exact normalized title match
        2. Starts-with match
        3. Substring / words match
        4. High-confidence fuzzy spelling match (e.g. 'vada chenai' -> 'Vada Chennai', 'vikramm' -> 'Vikram')
        """
        query = self.normalize_text(movie_title)
        if not query:
            return None

        # 1. Exact normalized title match
        for idx, m in enumerate(self.movies):
            t_norm = self.normalize_text(m.get("title", ""))
            raw_norm = self.normalize_text(m.get("raw_title", ""))
            if t_norm == query or raw_norm == query:
                return idx

        # 2. Starts-with match
        for idx, m in enumerate(self.movies):
            t_norm = self.normalize_text(m.get("title", ""))
            if t_norm.startswith(query):
                return idx

        # 3. Substring / contains match
        for idx, m in enumerate(self.movies):
            t_norm = self.normalize_text(m.get("title", ""))
            if len(query) >= 4 and (query in t_norm or t_norm in query):
                return idx

        # 4. Words match (all query words present in title)
        q_words = query.split()
        if len(q_words) > 1:
            for idx, m in enumerate(self.movies):
                t_norm = self.normalize_text(m.get("title", ""))
                if all(w in t_norm for w in q_words):
                    return idx

        # 5. Fuzzy spelling similarity match
        best_idx: Optional[int] = None
        best_ratio = 0.0

        for idx, m in enumerate(self.movies):
            t_norm = self.normalize_text(m.get("title", ""))
            if not t_norm:
                continue

            ratio = self.calculate_similarity_ratio(query, t_norm)
            if ratio > best_ratio:
                best_ratio = ratio
                best_idx = idx

        if best_idx is not None and best_ratio >= min_similarity:
            return best_idx

        return None

    # ========================================================
    # RECOMMENDATION ENGINE (KNN & DYNAMIC FALLBACK)
    # ========================================================

    def _rank_and_filter_candidates(
        self,
        target_movie: Dict[str, Any],
        distances: np.ndarray,
        indices: np.ndarray,
        top_n: int = 10,
        min_threshold: float = 0.08
    ) -> List[Dict[str, Any]]:
        """
        Ranks and filters KNN candidates with:
        - True cosine similarity from TF-IDF representation
        - Subtle director & cast affinity synergy
        - Minimum quality/similarity threshold
        - Strict self-exclusion
        """
        target_norm_title = self.normalize_text(target_movie.get("title", ""))
        target_id_str = str(target_movie.get("id") or target_movie.get("movie_id") or "")
        target_dir = str(target_movie.get("director", "")).strip().lower()
        target_genres = set(
            (g if isinstance(g, str) else g.get("name", "")).lower()
            for g in target_movie.get("genres", [])
        )

        # Parse target cast
        raw_t_cast = target_movie.get("cast", [])
        if isinstance(raw_t_cast, list):
            target_cast = set(
                (c.get("name", "") if isinstance(c, dict) else str(c)).strip().lower()
                for c in raw_t_cast[:6]
                if (isinstance(c, dict) and c.get("name")) or (isinstance(c, str) and c)
            )
        elif isinstance(raw_t_cast, str):
            target_cast = set(x.strip().lower() for x in raw_t_cast.split(",")[:6] if x.strip())
        else:
            target_cast = set()

        seen_titles = {target_norm_title}
        seen_ids = {target_id_str} if target_id_str else set()
        scored_candidates: List[Dict[str, Any]] = []

        for dist, idx in zip(distances[0], indices[0]):
            candidate = self.movies[idx]
            cand_id_str = str(candidate.get("id"))
            cand_norm_title = self.normalize_text(candidate["title"])

            # Never recommend target movie itself or duplicates
            if cand_norm_title in seen_titles or (cand_id_str and cand_id_str in seen_ids):
                continue

            seen_titles.add(cand_norm_title)
            if cand_id_str:
                seen_ids.add(cand_id_str)

            base_sim = float(max(0.0, 1.0 - dist))
            score = base_sim

            # 1. Director affinity (same director = strong stylistic and cinematic synergy)
            cand_dir = str(candidate.get("director", "")).strip().lower()
            if cand_dir and target_dir and cand_dir != "unknown director" and cand_dir != "nan" and cand_dir == target_dir:
                score += 0.08

            # 2. Cast collaboration affinity
            raw_c_cast = candidate.get("cast", [])
            if isinstance(raw_c_cast, list):
                cand_cast = set(
                    (c.get("name", "") if isinstance(c, dict) else str(c)).strip().lower()
                    for c in raw_c_cast[:6]
                )
            elif isinstance(raw_c_cast, str):
                cand_cast = set(x.strip().lower() for x in raw_c_cast.split(",")[:6] if x.strip())
            else:
                cand_cast = set()

            shared_actors = target_cast.intersection(cand_cast)
            if shared_actors:
                score += min(len(shared_actors) * 0.04, 0.08)

            # 3. Filter out weak/generic recommendations below relevance threshold
            if score >= min_threshold:
                rec_dict = dict(candidate)
                rec_dict["similarity"] = round(score, 4)
                scored_candidates.append(rec_dict)

        scored_candidates.sort(key=lambda x: x["similarity"], reverse=True)
        return scored_candidates[:top_n]

    def get_recommendations(
        self,
        movie_id: Union[int, str],
        top_n: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Returns top N nearest movie recommendations using KNN cosine distance with thematic & language weighting.
        Guarantees the target movie is never recommended.
        """
        target_idx: Optional[int] = None

        if movie_id in self.indices_map:
            target_idx = self.indices_map[movie_id]
        else:
            for idx, m in enumerate(self.movies):
                if str(m.get("id")) == str(movie_id) or str(m.get("movie_id")) == str(movie_id):
                    target_idx = idx
                    break

        if target_idx is None or target_idx < 0 or target_idx >= len(self.movies):
            return []

        target_movie = self.movies[target_idx]

        # KNN cosine recommendation with smart ranking
        if self.knn_model is not None and self.feature_matrix is not None:
            try:
                fetch_k = min(80, len(self.movies))
                distances, indices = self.knn_model.kneighbors(
                    self.feature_matrix[target_idx],
                    n_neighbors=fetch_k
                )
                recommendations = self._rank_and_filter_candidates(
                    target_movie=target_movie,
                    distances=distances,
                    indices=indices,
                    top_n=top_n
                )
                if recommendations:
                    return recommendations
            except Exception as e:
                print(f"[MovieRecommender] KNN inference error: {e}")

        # Fallback Heuristic Matcher if KNN has an issue
        return self._heuristic_recommendations(target_movie, top_n)

    def recommend_for_new_movie(
        self,
        movie_metadata: Dict[str, Any],
        top_n: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Dynamic Fallback for New / TMDB-Only Movie Releases:
        1. Takes available metadata (title, genres, overview, director, cast, language).
        2. Cleans fields and creates feature content text using the exact same weighted structure:
           Title 3x, Genres 4x, Director 3x, Cast 2x, Overview 2x, Language 1x.
        3. Transforms the new movie into a TF-IDF vector using the existing tfidf_vectorizer.pkl.
        4. Compares against the existing tfidf_matrix.pkl using KNN / cosine distance.
        5. Excludes the target movie itself and returns nearest similar movies.
        """
        target_title = self.clean_text(movie_metadata.get("title", ""))

        # Extract & format metadata
        raw_genres = movie_metadata.get("genres", [])
        if isinstance(raw_genres, list):
            genre_names = [g if isinstance(g, str) else g.get("name", "") for g in raw_genres]
            genres_clean = self.clean_text(" ".join(genre_names))
        else:
            genres_clean = self.clean_text(str(raw_genres))

        raw_cast = movie_metadata.get("cast", [])
        if isinstance(raw_cast, list):
            cast_names = [c.get("name", "") if isinstance(c, dict) else str(c) for c in raw_cast[:4]]
            cast_clean = self.clean_text(" ".join(cast_names))
        else:
            cast_clean = self.clean_text(str(raw_cast))

        director_clean = self.clean_text(movie_metadata.get("director", ""))
        language_clean = self.clean_text(movie_metadata.get("language", "Tamil"))
        overview_clean = self.clean_text(movie_metadata.get("overview", ""))

        # Exact same weighted content feature combination formula used in prepare_features.py
        feature_content = (
            f"{target_title} {target_title} {target_title} "
            f"{genres_clean} {genres_clean} {genres_clean} {genres_clean} "
            f"{director_clean} {director_clean} {director_clean} "
            f"{cast_clean} {cast_clean} "
            f"{overview_clean} {overview_clean} "
            f"{language_clean}"
        ).strip()

        if not feature_content:
            feature_content = f"{target_title} cinema"

        if self.vectorizer is not None and self.knn_model is not None and self.feature_matrix is not None:
            try:
                new_vec = self.vectorizer.transform([feature_content])
                fetch_k = min(80, len(self.movies))
                distances, indices = self.knn_model.kneighbors(
                    new_vec,
                    n_neighbors=fetch_k
                )

                recommendations = self._rank_and_filter_candidates(
                    target_movie=movie_metadata,
                    distances=distances,
                    indices=indices,
                    top_n=top_n
                )
                if recommendations:
                    return recommendations
            except Exception as e:
                print(f"[MovieRecommender] Dynamic new movie KNN inference error: {e}")

        # Fallback to heuristic recommendation based on target metadata
        return self._heuristic_recommendations(movie_metadata, top_n=top_n)

    def _heuristic_recommendations(
        self,
        target_movie: Dict[str, Any],
        top_n: int = 10
    ) -> List[Dict[str, Any]]:
        target_genres = set(
            (g if isinstance(g, str) else g.get("name", "")).lower()
            for g in target_movie.get("genres", [])
        )
        target_lang = target_movie.get("language", "").lower()
        target_dir = target_movie.get("director", "").lower()
        target_norm_title = self.normalize_text(target_movie.get("title", ""))
        target_id_str = str(target_movie.get("id") or target_movie.get("movie_id") or "")

        scored = []
        for m in self.movies:
            cand_norm_title = self.normalize_text(m["title"])
            cand_id_str = str(m.get("id"))

            # Exclude self
            if cand_norm_title == target_norm_title or (target_id_str and cand_id_str == target_id_str):
                continue

            score = 0.0
            common_genres = set(g.lower() for g in m.get("genres", [])).intersection(target_genres)
            score += len(common_genres) * 4.0

            if m.get("language", "").lower() == target_lang and target_lang:
                score += 5.0

            if target_dir and m.get("director", "").lower() == target_dir and target_dir != "unknown director":
                score += 6.0

            score += max(0.0, 10.0 - abs(m.get("rating", 7.0) - float(target_movie.get("rating", 7.0) or 7.0))) * 0.2
            scored.append((score, m))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [dict(item[1]) for item in scored[:top_n]]

    def recommend_by_title(
        self,
        movie_title: str,
        top_n: int = 10
    ) -> List[Dict[str, Any]]:
        """Recommends movies by matching a movie title query."""
        target_idx = self.find_movie(movie_title)
        if target_idx is None:
            return []

        target_movie = self.movies[target_idx]
        return self.get_recommendations(target_movie["id"], top_n=top_n)

    # ========================================================
    # PUBLIC DISCOVERY & QUERY APIS
    # ========================================================

    def search_movies(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        q = self.normalize_text(query)
        if not q:
            return self.movies[:limit]

        q_words = [w for w in q.split() if len(w) > 1]
        scored_results: List[Tuple[float, Dict[str, Any]]] = []

        for m in self.movies:
            title_norm = self.normalize_text(m.get("title", ""))
            raw_title_norm = self.normalize_text(m.get("raw_title", ""))
            dir_norm = self.normalize_text(m.get("director", ""))
            lang_norm = self.normalize_text(m.get("language", ""))
            genres_norm = [self.normalize_text(g) for g in m.get("genres", [])]
            cast_names = [self.normalize_text(c.get("name", "")) for c in m.get("cast", [])]
            overview_norm = self.normalize_text(m.get("overview", ""))

            score = 0.0

            # 1. Exact Title Match
            if q == title_norm or q == raw_title_norm:
                score += 1000.0
            # 2. Title Starts-With
            elif title_norm.startswith(q) or (raw_title_norm and raw_title_norm.startswith(q)):
                score += 400.0
            # 3. Substring in title
            elif len(q) >= 3 and (q in title_norm or (raw_title_norm and q in raw_title_norm)):
                score += 250.0

            # 4. Fuzzy Title Similarity (Handles spelling errors like 'vada chenai', 'vikramm', 'jai bheem', 'interstaller')
            sim_ratio = self.calculate_similarity_ratio(q, title_norm)
            if raw_title_norm and raw_title_norm != title_norm:
                sim_ratio = max(sim_ratio, self.calculate_similarity_ratio(q, raw_title_norm))

            if sim_ratio >= 0.85:
                score += 500.0 * sim_ratio
            elif sim_ratio >= 0.70:
                score += 300.0 * sim_ratio
            elif sim_ratio >= 0.60 and len(q) >= 5:
                score += 150.0 * sim_ratio

            # 5. Token words match in title
            if q_words:
                title_words = title_norm.split()
                matched_words = sum(1 for qw in q_words if any(qw == tw or self.calculate_similarity_ratio(qw, tw) >= 0.80 for tw in title_words))
                if matched_words == len(q_words) and len(q_words) > 1:
                    score += 350.0
                elif matched_words > 0 and len(q_words) > 1:
                    score += 120.0 * (matched_words / len(q_words))

            # 6. Cast, Director, Language, Genre matching
            if any(q == c for c in cast_names):
                score += 120.0
            elif any(q in c for c in cast_names if len(q) >= 4):
                score += 60.0

            if q in dir_norm and dir_norm != "unknown director":
                score += 90.0

            if q == lang_norm:
                score += 70.0

            if any(q == g for g in genres_norm):
                score += 50.0

            if len(q) >= 4 and q in overview_norm:
                score += 15.0

            # Filter out single-letter/negligible accidental matches
            if score >= 35.0:
                score += (m.get("rating", 0.0) * 0.5)
                scored_results.append((score, m))

        scored_results.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored_results[:limit]]

    def get_all(
        self,
        genre: Optional[str] = None,
        language: Optional[str] = None,
        year_min: Optional[int] = None,
        year_max: Optional[int] = None,
        min_rating: Optional[float] = None,
        sort_by: Optional[str] = "default",
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        filtered = self.movies

        if genre and isinstance(genre, str):
            g_target = genre.strip().lower()
            filtered = [m for m in filtered if any(g_target in g.lower() for g in m.get("genres", []))]

        if language and isinstance(language, str):
            l_target = language.strip().lower()
            filtered = [m for m in filtered if m.get("language", "").strip().lower() == l_target]

        if year_min is not None:
            filtered = [m for m in filtered if m.get("year", 0) >= year_min]

        if year_max is not None:
            filtered = [m for m in filtered if m.get("year", 0) <= year_max]

        if min_rating is not None:
            filtered = [m for m in filtered if m.get("rating", 0.0) >= min_rating]

        if sort_by == "rating":
            filtered = sorted(filtered, key=lambda m: (m.get("rating", 0.0), m.get("votes", 0)), reverse=True)
        elif sort_by == "popularity":
            filtered = sorted(filtered, key=lambda m: m.get("popularity", 0.0), reverse=True)
        elif sort_by == "revenue":
            filtered = sorted(filtered, key=lambda m: m.get("revenue_crores", 0.0), reverse=True)
        elif sort_by == "year":
            filtered = sorted(filtered, key=lambda m: m.get("year", 0), reverse=True)
        elif sort_by == "title":
            filtered = sorted(filtered, key=lambda m: m.get("title", ""))

        return filtered[offset:offset + limit]

    def get_trending(self, limit: int = 12) -> List[Dict[str, Any]]:
        pool = [m for m in self.movies if m.get("votes", 0) >= 50 or m.get("popularity", 0) > 5]
        if not pool:
            pool = self.movies
        trending = sorted(pool, key=lambda m: (m.get("popularity", 0.0), m.get("rating", 0.0)), reverse=True)
        return trending[:limit]

    def get_top_rated(self, limit: int = 12, language: Optional[str] = None) -> List[Dict[str, Any]]:
        pool = self.movies
        if language and isinstance(language, str):
            pool = [m for m in pool if m.get("language", "").strip().lower() == language.strip().lower()]

        # Bayesian weighted score
        mean_rating = 6.5
        min_votes = 100

        def weighted_score(m):
            v = m.get("votes", 0)
            r = m.get("rating", 0.0)
            return (v / (v + min_votes)) * r + (min_votes / (v + min_votes)) * mean_rating

        top = sorted(pool, key=weighted_score, reverse=True)
        return top[:limit]

    def get_tamil_movies(self, limit: int = 50, sort_by: str = "popularity") -> List[Dict[str, Any]]:
        return self.get_all(language="Tamil", sort_by=sort_by, limit=limit)

    def get_genres(self) -> List[str]:
        genres_set = set()
        for m in self.movies:
            for g in m.get("genres", []):
                if g:
                    genres_set.add(g)
        return sorted(list(genres_set))

    def get_languages(self) -> List[str]:
        languages_set = set()
        for m in self.movies:
            lang = m.get("language", "")
            if lang:
                languages_set.add(lang)
        return sorted(list(languages_set))


# ============================================================
# STANDALONE KNN TEST CLI
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("MOVIE RECOMMENDER - KNN TEST")
    print("=" * 60)

    recommender = MovieRecommender()

    try:
        user_input = input("\nEnter a movie title: ").strip()
    except (EOFError, KeyboardInterrupt):
        user_input = "Vada Chennai"

    query_title = user_input if user_input else "Vada Chennai"

    target_idx = recommender.find_movie(query_title)

    if target_idx is None:
        print(f"\nMovie '{query_title}' not found in dataset.")
    else:
        target_movie = recommender.movies[target_idx]
        print(f"\n[Debug] Selected movie index : {target_idx}")
        print(f"[Debug] Selected movie title : {target_movie['title']}")
        print(f"[Debug] Detected ID column   : {recommender.id_column}")
        print(f"[Debug] Dataset path         : {recommender.data_path}")
        print(f"[Debug] Total movies loaded  : {len(recommender.movies):,}")
        if recommender.feature_matrix is not None:
            print(f"[Debug] TF-IDF matrix shape  : {recommender.feature_matrix.shape}")

        print(f"\nSelected movie: {target_movie['title']} ({target_movie['year']}) [{target_movie['language']}]")

        recommendations = recommender.get_recommendations(target_movie["id"], top_n=10)

        if not recommendations:
            print("\nNo recommendations found.")
        else:
            print("\nRecommended Movies:")
            for i, rec in enumerate(recommendations, 1):
                sim_str = f" - Similarity: {rec.get('similarity', 0.0):.1%}" if "similarity" in rec else ""
                genres_str = ", ".join(rec.get("genres", []))
                print(
                    f"{i:2d}. {rec['title']} ({rec.get('year', 'N/A')}) "
                    f"[{rec.get('language', 'Unknown')}]{sim_str} | "
                    f"Director: {rec.get('director', 'Unknown')} | "
                    f"Genres: {genres_str}"
                )
