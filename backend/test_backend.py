import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.main import app, recommender

print("=== CineX Backend Verification ===")
print(f"Total movies loaded: {len(recommender.movies)}")

# Test search
results = recommender.search_movies("Vikram")
print(f"Search for 'Vikram' returned: {len(results)} movie(s) -> {[m['title'] for m in results]}")

# Test recommendations
recs = recommender.get_recommendations(1, top_n=3)
print(f"Recommendations for Maari (id=1): {[m['title'] for m in recs]}")

# Test Tamil movies
tamil = [m['title'] for m in recommender.movies if m.get('language') == 'Tamil']
print(f"Tamil movies: {tamil}")

print("Backend verification SUCCESSFUL!")
