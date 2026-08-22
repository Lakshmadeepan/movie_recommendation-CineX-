import pandas as pd
import numpy as np
import re
import joblib
import os

from sklearn.feature_extraction.text import TfidfVectorizer

# ============================================================
# PATHS
# ============================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(SCRIPT_DIR, "..", "dataset")

INPUT_FILE = os.path.join(DATASET_DIR, "master_movies.csv")
OUTPUT_MOVIES = os.path.join(DATASET_DIR, "movies_features.csv")
OUTPUT_MATRIX = os.path.join(DATASET_DIR, "tfidf_matrix.pkl")
OUTPUT_VECTORIZER = os.path.join(DATASET_DIR, "tfidf_vectorizer.pkl")

# Common noise words in movie summaries that do not indicate thematic similarity
STOP_WORDS_GENERIC = {
    "movie", "movies", "film", "films", "story", "stories", "presentation",
    "storyline", "unknown", "director", "starring", "actor", "actress",
    "character", "characters", "scene", "scenes", "plot", "synopsis",
    "released", "nan", "none", "null", "undefined", "title", "full", "watch"
}


# ============================================================
# TEXT CLEANING & FEATURE EXTRACTION
# ============================================================

def clean_feature_text(value: str) -> str:
    """
    Clean and normalize feature text, removing punctuation and generic noise tokens.
    """
    if pd.isna(value):
        return ""

    value = str(value).lower()
    value = re.sub(r"[^a-z0-9\s]", " ", value)
    
    tokens = [
        w for w in value.split()
        if len(w) > 1 and w not in STOP_WORDS_GENERIC
    ]

    return " ".join(tokens)


def get_top_cast(cast_value: str, limit: int = 4) -> str:
    """Extract and clean only the top N lead actors."""
    if not cast_value or pd.isna(cast_value):
        return ""
    c_str = str(cast_value).strip()
    if c_str.startswith("[") and c_str.endswith("]"):
        items = [x.strip(" '\"") for x in c_str[1:-1].split(",")]
    else:
        items = [x.strip() for x in c_str.split(",")]
    cleaned = [clean_feature_text(x) for x in items if clean_feature_text(x)]
    return " ".join(cleaned[:limit])


def build_movie_content(row: pd.Series) -> str:
    """
    Combines movie metadata into a weighted, high-quality feature document:
    - TITLE (3x): Strong keyword identity (e.g. 'interstellar', 'avatar', 'batman')
    - GENRES (4x): Primary thematic anchor (e.g. 'sci-fi adventure', 'crime thriller')
    - DIRECTOR (3x): Stylistic & directorial synergy
    - TOP CAST (2x): Key lead actor collaboration (top 4 leads)
    - OVERVIEW (2x): In-depth narrative context & plot keywords
    - LANGUAGE (1x): Supporting linguistic signal
    """
    title_clean = clean_feature_text(row.get("title", ""))
    genres_clean = clean_feature_text(row.get("genres", ""))
    director_clean = clean_feature_text(row.get("director", ""))
    cast_clean = get_top_cast(row.get("cast", ""), limit=4)
    overview_clean = clean_feature_text(row.get("overview", ""))
    language_clean = clean_feature_text(row.get("language", ""))

    content_parts = [
        title_clean,
        title_clean,
        title_clean,
        genres_clean,
        genres_clean,
        genres_clean,
        genres_clean,
        director_clean,
        director_clean,
        director_clean,
        cast_clean,
        cast_clean,
        overview_clean,
        overview_clean,
        language_clean,
    ]

    combined = " ".join(p for p in content_parts if p).strip()
    return combined if combined else f"{title_clean} cinema"


# ============================================================
# MAIN FEATURE ENGINEERING PIPELINE
# ============================================================

def main():
    print("=" * 65)
    print("CINEX MOVIE FEATURE ENGINEERING & TF-IDF REBUILD")
    print("=" * 65)

    # 1. Load Master Dataset
    df = pd.read_csv(INPUT_FILE, low_memory=False)
    print(f"\nLoaded {len(df):,} movies from: {INPUT_FILE}")

    required_columns = ["title", "overview", "genres", "director", "cast", "language"]
    for col in required_columns:
        if col not in df.columns:
            df[col] = ""
        df[col] = df[col].fillna("")

    # 2. Build feature content documents
    print("\nBuilding weighted content features (Title 3x, Genres 4x, Director 3x, Cast 2x, Overview 2x)...")
    df["content"] = df.apply(build_movie_content, axis=1)

    # 3. Filter out completely empty entries
    df = df[df["content"].str.strip() != ""].copy()
    df.reset_index(drop=True, inplace=True)
    df["movie_id"] = range(1, len(df) + 1)
    print(f"Total movies with valid features: {len(df):,}")

    # 4. Fit TF-IDF Vectorizer
    print("\nFitting TfidfVectorizer (stop_words='english', ngram_range=(1,2), sublinear_tf=True)...")
    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=60000,
        ngram_range=(1, 2),
        min_df=1,
        sublinear_tf=True
    )

    tfidf_matrix = vectorizer.fit_transform(df["content"])
    print(f"TF-IDF Matrix Shape: {tfidf_matrix.shape}")
    print(f"Vocabulary Size     : {len(vectorizer.get_feature_names_out()):,}")

    # 5. Remove old artifacts if existing
    for p in [OUTPUT_MOVIES, OUTPUT_MATRIX, OUTPUT_VECTORIZER]:
        if os.path.exists(p):
            try:
                os.remove(p)
                print(f"Removed previous artifact: {os.path.basename(p)}")
            except Exception:
                pass

    # 6. Save new artifacts
    print("\nSaving new artifacts...")
    df.to_csv(OUTPUT_MOVIES, index=False, encoding="utf-8-sig")
    print(f"  [1/3] Saved movie features: {OUTPUT_MOVIES}")

    joblib.dump(tfidf_matrix, OUTPUT_MATRIX)
    print(f"  [2/3] Saved TF-IDF matrix : {OUTPUT_MATRIX}")

    joblib.dump(vectorizer, OUTPUT_VECTORIZER)
    print(f"  [3/3] Saved vectorizer    : {OUTPUT_VECTORIZER}")

    # 7. Print Sample Inspections for Target Movies
    print("\n" + "=" * 65)
    print("FEATURE SAMPLES FOR KEY MOVIES:")
    print("=" * 65)

    test_titles = ["Interstellar", "Inception", "Vada Chennai", "Vikram", "Jai Bhim"]
    for t in test_titles:
        match = df[df["title"].str.lower() == t.lower()]
        if len(match) > 0:
            row = match.iloc[0]
            print(f"\nTitle: {row['title']} ({row['year']})")
            print(f"  Genres  : {row['genres']}")
            print(f"  Director: {row['director']}")
            print(f"  Cast    : {str(row['cast'])[:70]}...")
            print(f"  Features: {str(row['content'])[:140]}...")

    print("\n" + "=" * 65)
    print("FEATURE ENGINEERING COMPLETED SUCCESSFULLY!")
    print("=" * 65)


if __name__ == "__main__":
    main()