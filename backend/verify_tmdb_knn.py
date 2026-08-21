import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from main import (
    root,
    health_check,
    search_movies,
    get_recommendations,
    get_movie_by_id,
    get_tamil_movies,
    get_trending,
    get_popular,
    get_now_playing,
    get_top_rated
)

print("=" * 60)
print("CINEX FULL SYSTEM VERIFICATION SUITE")
print("=" * 60)

# 1. Root & Health
print("\n[1] Testing Root & Health:")
print("    Root:", root())
print("    Health:", health_check())

# 2. Search Vada Chennai
print("\n[2] Testing Search 'Vada Chennai':")
search_results = search_movies("Vada Chennai", limit=5)
print(f"    Found {len(search_results)} results:")
for i, m in enumerate(search_results[:3], 1):
    print(f"    {i}. {m['title']} ({m.get('year')}) [{m.get('language')}] - ID: {m['id']}")
assert len(search_results) > 0, "Search returned 0 results"
target = search_results[0]

# 3. Recommendations for Vada Chennai
print(f"\n[3] Testing KNN + TMDB Recommendations for '{target['title']}' (ID: {target['id']}):")
recs = get_recommendations(target['id'], limit=10)
print(f"    Returned {len(recs)} recommended movies:")
for i, r in enumerate(recs, 1):
    poster_preview = (r.get("poster") or "")[:45]
    print(
        f"    {i:2d}. {r['title']} ({r.get('year')}) [{r.get('language')}] "
        f"| Dir: {r.get('director')} | Sim: {r.get('similarity', 0):.1%} | Poster: {poster_preview}..."
    )

assert len(recs) == 10, f"Expected 10 recommendations, got {len(recs)}"
assert not any(r['title'].strip().lower() == target['title'].strip().lower() for r in recs), "Selected movie was found in recommendations!"
print("    [PASS] Target movie is NEVER in recommendations!")

# 4. Search Other Tamil Favorites
print("\n[4] Testing Search for Other Major Tamil Movies:")
for q in ["Jai Bhim", "Vikram", "Maharaja"]:
    res = search_movies(q, limit=3)
    titles = [m['title'] for m in res]
    print(f"    - Query '{q}': found {len(res)} -> {titles}")
    assert len(res) > 0, f"Search for {q} failed"

# 5. Discovery Endpoints
print("\n[5] Testing Discovery Endpoints:")
tamil_list = get_tamil_movies(limit=8)
print(f"    - Tamil Movies ({len(tamil_list)}): {[m['title'] for m in tamil_list[:4]]}")
assert len(tamil_list) == 8

trend_list = get_trending(limit=6)
print(f"    - Trending ({len(trend_list)}): {[m['title'] for m in trend_list[:3]]}")
assert len(trend_list) == 6

pop_list = get_popular(limit=6)
print(f"    - Popular ({len(pop_list)}): {[m['title'] for m in pop_list[:3]]}")
assert len(pop_list) == 6

now_list = get_now_playing(limit=6)
print(f"    - Now Playing ({len(now_list)}): {[m['title'] for m in now_list[:3]]}")
assert len(now_list) == 6

# 6. Movie Details & Watch Providers
print("\n[6] Testing Movie Details by ID:")
detail = get_movie_by_id(target['id'])
print(f"    Title: {detail['title']}")
print(f"    Director: {detail['director']}")
print(f"    Cast Count: {len(detail.get('cast', []))}")
print(f"    Streaming Providers: {detail.get('streaming', [])}")
print(f"    Trailer ID: {detail.get('trailerId')}")
print(f"    Poster: {detail.get('poster')[:50]}...")
print(f"    Backdrop: {detail.get('backdrop')[:50]}...")

print("\n" + "=" * 60)
print("ALL SYSTEM VERIFICATIONS PASSED WITH 100% SUCCESS!")
print("=" * 60)
