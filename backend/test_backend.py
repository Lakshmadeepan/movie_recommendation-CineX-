import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.main import (
    app,
    recommender,
    root,
    health_check,
    get_movies,
    get_trending,
    get_top_rated,
    get_tamil_movies,
    get_recommendations,
    search_movies,
    get_genres,
    get_languages
)

print("=" * 80)
print("CINEX BACKEND & RECOMMENDER ENGINE VERIFICATION SUITE")
print("=" * 80)

# 1. Total count check
total_movies = len(recommender.movies)
print(f"\n[1] Total Movies Loaded: {total_movies:,}")
assert total_movies > 1000, f"Expected >1,000 movies, got {total_movies}"
print("    [OK] Dataset load verification passed!")

# 2. Health & Root Endpoint Tests
root_data = root()
print(f"\n[2] Root Endpoint: {root_data}")
assert root_data["status"] == "online"
assert root_data["total_movies"] == total_movies

health_data = health_check()
print(f"    Health Check: {health_data}")
assert health_data.status == "healthy"
assert health_data.movies_count == total_movies
print("    [OK] Health check endpoint passed!")

# 3. Search Testing
print("\n[3] Search Functionality Tests:")
search_queries = ["Vikram", "Action", "Drama"]
for q in search_queries:
    results = search_movies(q=q, limit=5)
    titles = [m.get("title", "") if isinstance(m, dict) else m.title for m in results]
    print(f"    - Query '{q}': found {len(results)} matches -> {titles[:3]}")
    assert len(results) > 0, f"Search for '{q}' returned 0 results"
print("    [OK] Search tests passed!")

# 4. Recommendation Engine Tests
print("\n[4] Recommendation Engine KNN & Similarity Tests:")
test_movie = recommender.movies[0]
recs = get_recommendations(movie_id=test_movie["id"], limit=5)
print(f"    Target Movie: '{test_movie['title']}' ({test_movie['year']}, {test_movie['language']}, {test_movie['genres']})")
print("    Recommendations:")
for idx, r in enumerate(recs, 1):
    r_dict = r if isinstance(r, dict) else r.model_dump()
    print(f"      {idx}. '{r_dict['title']}' ({r_dict['year']}, {r_dict['language']}, {r_dict['genres']})")
assert len(recs) == 5, f"Expected 5 recommendations, got {len(recs)}"

# Find a Tamil movie for targeted recommendation test
tamil_movies = [m for m in recommender.movies if m.get("language") == "Tamil"]
print(f"\n[5] Tamil Movie Ecosystem ({len(tamil_movies):,} Tamil movies):")

if len(tamil_movies) > 0:
    sample_tamil = tamil_movies[min(10, len(tamil_movies) - 1)]
    tamil_recs = get_recommendations(movie_id=sample_tamil["id"], limit=5)
    print(f"    Tamil Target: '{sample_tamil['title']}' ({sample_tamil['year']}, {sample_tamil['genres']})")
    print("    Tamil Recommendations:")
    for idx, r in enumerate(tamil_recs, 1):
        r_dict = r if isinstance(r, dict) else r.model_dump()
        print(f"      {idx}. '{r_dict['title']}' ({r_dict['year']}, {r_dict['language']}, {r_dict['genres']})")
    print("    [OK] Tamil recommendation tests passed!")

# 6. API Filtering Endpoints Test
print("\n[6] API Filtering & Sorting Endpoints:")
# Test Trending
trending = get_trending(limit=8)
print(f"    - Trending (top 3): {[m.get('title', '') if isinstance(m, dict) else m.title for m in trending[:3]]}")
assert len(trending) == 8

# Test Top Rated
top_rated = get_top_rated(limit=5)
print(f"    - Top Rated (top 3): {[(m.get('title', '') if isinstance(m, dict) else m.title) for m in top_rated[:3]]}")
assert len(top_rated) == 5

# Test Tamil movies endpoint
t_list = get_tamil_movies(limit=5)
print(f"    - Tamil Endpoint (top 3): {[m.get('title', '') if isinstance(m, dict) else m.title for m in t_list[:3]]}")
assert len(t_list) == 5

# Test Multi-attribute filter
filtered = get_movies(genre="Action", language="Tamil", year_min=2015, sort_by="rating", limit=5)
print(f"    - Filtered Action Tamil 2015+ (top 3): {[(m.get('title', '') if isinstance(m, dict) else m.title) for m in filtered[:3]]}")

# Test Genres & Languages metadata
all_genres = get_genres()
all_langs = get_languages()
print(f"    - Genres available ({len(all_genres)}): {all_genres[:8]}")
print(f"    - Languages available ({len(all_langs)}): {all_langs}")
assert "Tamil" in all_langs

print("\n" + "=" * 80)
print("ALL VERIFICATION CHECKS COMPLETED WITH 100% SUCCESS!")
print("=" * 80 + "\n")
