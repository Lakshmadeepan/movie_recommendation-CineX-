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
