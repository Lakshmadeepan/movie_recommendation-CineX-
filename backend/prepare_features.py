import pandas as pd
import re
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer


# ============================================================
# PATHS
# ============================================================

INPUT_FILE = "../dataset/master_movies.csv"

OUTPUT_MOVIES = "../dataset/movies_features.csv"
OUTPUT_MATRIX = "../dataset/tfidf_matrix.pkl"
OUTPUT_VECTORIZER = "../dataset/tfidf_vectorizer.pkl"


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(value):
    """
    Clean and normalize movie text.
    """

    if pd.isna(value):
        return ""

    value = str(value).lower()

    # Remove special characters
    value = re.sub(r"[^a-z0-9\s]", " ", value)

    # Remove extra spaces
    value = re.sub(r"\s+", " ", value)

    return value.strip()


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("MOVIE FEATURE ENGINEERING")
    print("=" * 60)

    # --------------------------------------------------------
    # Load master dataset
    # --------------------------------------------------------

    df = pd.read_csv(INPUT_FILE)

    print("\nMovies loaded:", len(df))

    # --------------------------------------------------------
    # Make sure required columns exist
    # --------------------------------------------------------

    required_columns = [
        "title",
        "overview",
        "genres",
        "director",
        "cast",
        "language"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:

        print("\nERROR!")
        print("Missing columns:")

        for column in missing_columns:
            print("-", column)

        return

    # --------------------------------------------------------
    # Fill missing values
    # --------------------------------------------------------

    for column in required_columns:

        df[column] = df[column].fillna("")

    # --------------------------------------------------------
    # Clean individual features
    # --------------------------------------------------------

    for column in required_columns:

        df[column] = df[column].apply(clean_text)

    # --------------------------------------------------------
    # Create combined content
    # --------------------------------------------------------

    # We repeat important fields so TF-IDF gives them
    # slightly more importance.

    df["content"] = (
        df["genres"] + " "
        + df["genres"] + " "
        + df["director"] + " "
        + df["cast"] + " "
        + df["language"] + " "
        + df["overview"]
    )

    # --------------------------------------------------------
    # Remove movies with no usable content
    # --------------------------------------------------------

    df = df[
        df["content"].str.strip() != ""
    ].copy()

    df.reset_index(
        drop=True,
        inplace=True
    )

    print(
        "Movies after feature preparation:",
        len(df)
    )

    # --------------------------------------------------------
    # TF-IDF
    # --------------------------------------------------------

    print("\nCreating TF-IDF matrix...")

    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=50000,
        ngram_range=(1, 2),
        min_df=2
    )

    tfidf_matrix = vectorizer.fit_transform(
        df["content"]
    )

    # --------------------------------------------------------
    # Information
    # --------------------------------------------------------

    print(
        "\nTF-IDF matrix shape:",
        tfidf_matrix.shape
    )

    print(
        "Number of features:",
        len(vectorizer.get_feature_names_out())
    )

    # --------------------------------------------------------
    # Save movie metadata
    # --------------------------------------------------------

    df.to_csv(
        OUTPUT_MOVIES,
        index=False,
        encoding="utf-8-sig"
    )

    # --------------------------------------------------------
    # Save TF-IDF matrix
    # --------------------------------------------------------

    joblib.dump(
        tfidf_matrix,
        OUTPUT_MATRIX
    )

    # --------------------------------------------------------
    # Save vectorizer
    # --------------------------------------------------------

    joblib.dump(
        vectorizer,
        OUTPUT_VECTORIZER
    )

    # --------------------------------------------------------
    # Show sample
    # --------------------------------------------------------

    print("\nSample combined features:")

    print(
        df[
            [
                "title",
                "genres",
                "director",
                "language",
                "content"
            ]
        ].head(5).to_string(index=False)
    )

    print("\n" + "=" * 60)
    print("FEATURE ENGINEERING COMPLETED")
    print("=" * 60)

    print("\nCreated files:")

    print("1.", OUTPUT_MOVIES)
    print("2.", OUTPUT_MATRIX)
    print("3.", OUTPUT_VECTORIZER)


if __name__ == "__main__":
    main()