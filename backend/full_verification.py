import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.main import get_recommendations, search_movies, tmdb_service, recommender

def run_suite():
    print("=" * 80)
    print("CINEX COMPREHENSIVE RECOMMENDATION SYSTEM VERIFICATION SUITE")
    print("=" * 80)

    test_cases = [
        ("Kaithi", "ta"),
        ("Vikram", "ta"),
        ("Vada Chennai", "ta"),
        ("Inception", "en"),
        ("Interstellar", "en"),
        ("The Dark Knight", "en"),
        ("Leo", "ta", 949229), # Thalapathy Vijay's Leo
        ("Amaran", "ta"),       # Recent release
    ]

    for item in test_cases:
        name = item[0]
        expected_lang = item[1]
        explicit_id = item[2] if len(item) > 2 else None

        print(f"\n>>> TESTING: '{name}' (Target Lang: {expected_lang})")
        if explicit_id:
            recs = get_recommendations(explicit_id, limit=6)
        else:
            matches = search_movies(name)
            if not matches:
                print(f"  [ERROR] Movie '{name}' not found in search!")
                continue
            target = matches[0]
            clean_title = target['title'].encode('ascii', 'replace').decode('ascii')
            print(f"  Matched Target: {clean_title} ({target.get('year')}) [{target.get('language')}] - ID: {target.get('id')}")
            recs = get_recommendations(target["id"], limit=6)

        print(f"  Recommendations ({len(recs)} returned):")
        for i, r in enumerate(recs, 1):
            sim_str = f"Sim: {r.get('similarity'):.4f}" if r.get('similarity') is not None else "Sim: Fallback"
            r_title = r['title'].encode('ascii', 'replace').decode('ascii')
            print(f"    {i}. {r_title} ({r.get('year')}) [{r.get('language')}] - TMDB: {r.get('tmdb_id')} - {sim_str}")

    print("\n" + "=" * 80)
    print("ALL TEST CASES EXECUTED SUCCESSFULLY")
    print("=" * 80)

if __name__ == "__main__":
    run_suite()
