<<<<<<< HEAD
import json
import os
from typing import List, Dict, Any, Optional

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.neighbors import NearestNeighbors
    import numpy as np
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class MovieRecommender:
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.movies: List[Dict[str, Any]] = []
        self.movie_map: Dict[int, Dict[str, Any]] = {}
        self.indices_map: Dict[int, int] = {}
        self.feature_matrix = None
        self.knn_model = None
        self.load_data()

    def load_data(self):
        if not os.path.exists(self.data_path):
            return
        with open(self.data_path, "r", encoding="utf-8") as f:
            self.movies = json.load(f)
        
        self.movie_map = {m["id"]: m for m in self.movies}
        self.indices_map = {m["id"]: idx for idx, m in enumerate(self.movies)}
        self._fit_recommender()

    def _fit_recommender(self):
        if not self.movies:
            return

        # Prepare rich text representation for each movie (genres, director, cast, language, overview)
        soup_features = []
        for m in self.movies:
            genres_str = " ".join(m.get("genres", []))
            director_str = m.get("director", "")
            cast_str = " ".join([c.get("name", "") for c in m.get("cast", [])])
            lang_str = m.get("language", "")
            overview_str = m.get("overview", "")
            
            # Weighted feature string
            soup = f"{genres_str} {genres_str} {director_str} {cast_str} {lang_str} {overview_str}"
            soup_features.append(soup)

        if SKLEARN_AVAILABLE and len(soup_features) > 1:
            try:
                self.vectorizer = TfidfVectorizer(stop_words="english")
                self.feature_matrix = self.vectorizer.fit_transform(soup_features)
                
                # KNN with cosine metric
                n_neighbors = min(len(self.movies), 10)
                self.knn_model = NearestNeighbors(n_neighbors=n_neighbors, metric="cosine")
                self.knn_model.fit(self.feature_matrix)
            except Exception as e:
                print(f"Error training recommender: {e}")
                self.knn_model = None

    def get_recommendations(self, movie_id: int, top_n: int = 6) -> List[Dict[str, Any]]:
        if movie_id not in self.indices_map:
            return []

        target_idx = self.indices_map[movie_id]
        target_movie = self.movie_map[movie_id]

        if self.knn_model is not None and self.feature_matrix is not None:
            try:
                distances, indices = self.knn_model.kneighbors(
                    self.feature_matrix[target_idx], 
                    n_neighbors=min(top_n + 1, len(self.movies))
                )
                recommended = []
                for idx in indices[0]:
                    rec_movie = self.movies[idx]
                    if rec_movie["id"] != movie_id:
                        recommended.append(rec_movie)
                    if len(recommended) >= top_n:
                        break
                return recommended
            except Exception:
                pass

        # Heuristic fallback (genre + language overlap)
        scored = []
        for m in self.movies:
            if m["id"] == movie_id:
                continue
            score = 0
            # Common genres
            common_genres = set(m.get("genres", [])).intersection(set(target_movie.get("genres", [])))
            score += len(common_genres) * 3
            # Same language
            if m.get("language") == target_movie.get("language"):
                score += 2
            # Same director
            if m.get("director") == target_movie.get("director"):
                score += 4
            # Rating similarity
            score += (10 - abs(m.get("rating", 0) - target_movie.get("rating", 0))) * 0.1
            scored.append((score, m))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored[:top_n]]

    def search_movies(self, query: str) -> List[Dict[str, Any]]:
        q = query.lower().strip()
        if not q:
            return self.movies

        results = []
        for m in self.movies:
            title_match = q in m.get("title", "").lower()
            lang_match = q in m.get("language", "").lower()
            genre_match = any(q in g.lower() for g in m.get("genres", []))
            director_match = q in m.get("director", "").lower()
            cast_match = any(q in c.get("name", "").lower() for c in m.get("cast", []))

            if title_match or lang_match or genre_match or director_match or cast_match:
                results.append(m)

        return results

    def get_all(self, genre: Optional[str] = None, language: Optional[str] = None) -> List[Dict[str, Any]]:
        filtered = self.movies
        if genre:
            filtered = [m for m in filtered if genre.lower() in [g.lower() for g in m.get("genres", [])]]
        if language:
            filtered = [m for m in filtered if m.get("language", "").lower() == language.lower()]
        return filtered
=======
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
            self.indices_map[int(idx)] = int(idx)

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
    # MOVIE SEARCH / LOOKUP
    # ========================================================

    @staticmethod
    def normalize_text(text: Any) -> str:
        if pd.isna(text) or text is None:
            return ""
        s = str(text).lower()
        s = re.sub(r"[^a-z0-9\s]", " ", s)
        s = re.sub(r"\s+", " ", s)
        return s.strip()

    def find_movie(self, movie_title: str) -> Optional[int]:
        """Finds row index for a given movie title string."""
        query = self.normalize_text(movie_title)
        if not query:
            return None

        # 1. Exact normalized title match
        for idx, m in enumerate(self.movies):
            if self.normalize_text(m["title"]) == query or self.normalize_text(m["raw_title"]) == query:
                return idx

        # 2. Starts-with match
        for idx, m in enumerate(self.movies):
            t_norm = self.normalize_text(m["title"])
            if t_norm.startswith(query):
                return idx

        # 3. Substring / contains match
        for idx, m in enumerate(self.movies):
            t_norm = self.normalize_text(m["title"])
            if query in t_norm:
                return idx

        # 4. Words match (all query words present in title)
        q_words = query.split()
        for idx, m in enumerate(self.movies):
            t_norm = self.normalize_text(m["title"])
            if all(w in t_norm for w in q_words):
                return idx

        return None

    # ========================================================
    # RECOMMENDATION ENGINE
    # ========================================================

    def get_recommendations(
        self,
        movie_id: Union[int, str],
        top_n: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Returns top N nearest movie recommendations using KNN cosine distance.
        Guarantees the target movie is never recommended.
        """
        # Resolve target row index
        target_idx: Optional[int] = None

        if movie_id in self.indices_map:
            target_idx = self.indices_map[movie_id]
        else:
            # Fallback search by ID or string
            for idx, m in enumerate(self.movies):
                if str(m.get("id")) == str(movie_id) or str(m.get("movie_id")) == str(movie_id):
                    target_idx = idx
                    break

        if target_idx is None or target_idx < 0 or target_idx >= len(self.movies):
            return []

        target_movie = self.movies[target_idx]
        target_norm_title = self.normalize_text(target_movie["title"])

        # KNN cosine recommendation
        if self.knn_model is not None and self.feature_matrix is not None:
            try:
                fetch_k = min(top_n + 35, len(self.movies))
                distances, indices = self.knn_model.kneighbors(
                    self.feature_matrix[target_idx],
                    n_neighbors=fetch_k
                )

                recommendations = []
                seen_titles = {target_norm_title}

                for dist, idx in zip(distances[0], indices[0]):
                    if idx == target_idx:
                        continue

                    candidate = self.movies[idx]
                    cand_norm_title = self.normalize_text(candidate["title"])

                    # Avoid recommending same movie or duplicates
                    if cand_norm_title in seen_titles:
                        continue

                    seen_titles.add(cand_norm_title)

                    rec_dict = dict(candidate)
                    rec_dict["similarity"] = round(float(max(0.0, 1.0 - dist)), 4)
                    recommendations.append(rec_dict)

                    if len(recommendations) >= top_n:
                        break

                if recommendations:
                    return recommendations
            except Exception as e:
                print(f"[MovieRecommender] KNN inference error: {e}")

        # Fallback Heuristic Matcher if KNN has an issue
        return self._heuristic_recommendations(target_movie, top_n)

    def _heuristic_recommendations(
        self,
        target_movie: Dict[str, Any],
        top_n: int = 10
    ) -> List[Dict[str, Any]]:
        target_genres = set(g.lower() for g in target_movie.get("genres", []))
        target_lang = target_movie.get("language", "").lower()
        target_dir = target_movie.get("director", "").lower()
        target_norm_title = self.normalize_text(target_movie["title"])

        scored = []
        for m in self.movies:
            if self.normalize_text(m["title"]) == target_norm_title:
                continue

            score = 0.0
            common_genres = set(g.lower() for g in m.get("genres", [])).intersection(target_genres)
            score += len(common_genres) * 4.0

            if m.get("language", "").lower() == target_lang and target_lang:
                score += 5.0

            if target_dir and m.get("director", "").lower() == target_dir and target_dir != "unknown director":
                score += 6.0

            score += max(0.0, 10.0 - abs(m.get("rating", 7.0) - target_movie.get("rating", 7.0))) * 0.2
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

        scored_results: List[Tuple[float, Dict[str, Any]]] = []

        for m in self.movies:
            title_norm = self.normalize_text(m.get("title", ""))
            dir_norm = self.normalize_text(m.get("director", ""))
            lang_norm = self.normalize_text(m.get("language", ""))
            genres_norm = [self.normalize_text(g) for g in m.get("genres", [])]
            cast_names = [self.normalize_text(c.get("name", "")) for c in m.get("cast", [])]
            overview_norm = self.normalize_text(m.get("overview", ""))

            score = 0.0

            if q == title_norm:
                score += 100.0
            elif title_norm.startswith(q):
                score += 50.0
            elif q in title_norm:
                score += 25.0

            if any(q == c for c in cast_names):
                score += 20.0
            elif any(q in c for c in cast_names):
                score += 10.0

            if q in dir_norm and dir_norm != "unknown director":
                score += 15.0

            if q == lang_norm:
                score += 12.0
            elif q in lang_norm:
                score += 6.0

            if any(q in g for g in genres_norm):
                score += 10.0

            if q in overview_norm:
                score += 3.0

            if score > 0:
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
>>>>>>> 12d9995 (feat: CineX ML movie recommendation system with TMDB trailer modal, reviews, and watchlists)
