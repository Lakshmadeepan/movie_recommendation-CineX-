import pandas as pd
import numpy as np
import re
import ast
import os

# ============================================================
# CONFIGURATION
# ============================================================

DATASET_DIR = "../dataset"
OUTPUT_FILE = "../dataset/master_movies.csv"

DATASET_1 = os.path.join(DATASET_DIR, "dataset1.csv")
DATASET_2 = os.path.join(DATASET_DIR, "dataset2.csv")
DATASET_3 = os.path.join(DATASET_DIR, "dataset3.csv")
DATASET_4 = os.path.join(DATASET_DIR, "dataset4.csv")


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def clean_text(value):
    """
    Convert any value into clean text.
    Handles NaN, lists stored as strings, etc.
    """

    if pd.isna(value):
        return ""

    value = str(value).strip()

    # Handle strings like:
    # ['Action', 'Drama', 'Thriller']
    if value.startswith("[") and value.endswith("]"):
        try:
            parsed = ast.literal_eval(value)

            if isinstance(parsed, list):
                return ", ".join(str(x) for x in parsed)

        except Exception:
            pass

    return value


def normalize_text(value):
    """
    Normalize text for comparison/deduplication.
    """

    value = clean_text(value).lower()

    value = re.sub(r"[^a-z0-9\s]", " ", value)

    value = re.sub(r"\s+", " ", value).strip()

    return value


def clean_title(value):
    """
    Clean movie title.
    """

    value = clean_text(value)

    # Remove year written inside title
    # Example:
    # Kab? Kyoon? Aur Kahan?: (1970)
    value = re.sub(r"\s*[:(]\s*\d{4}\s*\)?\s*$", "", value)

    return value.strip()


def first_existing(df, columns):
    """
    Return the first column that exists in the dataframe.
    """

    for column in columns:
        if column in df.columns:
            return df[column]

    return pd.Series([""] * len(df), index=df.index)


def numeric_column(series):
    """
    Convert a column into numeric values.
    Invalid values become NaN.
    """

    return pd.to_numeric(series, errors="coerce")


# ============================================================
# STANDARD MASTER COLUMNS
# ============================================================

MASTER_COLUMNS = [
    "movie_id",
    "title",
    "imdb_id",
    "overview",
    "genres",
    "director",
    "cast",
    "language",
    "year",
    "rating",
    "votes",
    "runtime_minutes",
    "poster",
    "backdrop",
    "trailer",
    "popularity",
    "budget_crores",
    "revenue_crores",
    "production_company",
    "release_date",
    "source"
]


# ============================================================
# DATASET 1
# ============================================================

def process_dataset_1(path):

    print("\nLoading Dataset 1...")

    df = pd.read_csv(path)

    print("Rows:", len(df))

    result = pd.DataFrame(index=df.index)

    result["movie_id"] = first_existing(
        df,
        ["id"]
    )

    result["title"] = first_existing(
        df,
        ["title"]
    )

    result["imdb_id"] = first_existing(
        df,
        ["imdb_id"]
    )

    result["overview"] = first_existing(
        df,
        ["overview"]
    )

    result["genres"] = first_existing(
        df,
        ["genres"]
    )

    result["director"] = first_existing(
        df,
        ["director"]
    )

    result["cast"] = first_existing(
        df,
        ["cast"]
    )

    result["language"] = first_existing(
        df,
        ["language"]
    )

    result["year"] = first_existing(
        df,
        ["year"]
    )

    result["rating"] = first_existing(
        df,
        ["rating"]
    )

    result["votes"] = first_existing(
        df,
        ["votes"]
    )

    result["runtime_minutes"] = first_existing(
        df,
        ["runtime_minutes"]
    )

    result["poster"] = first_existing(
        df,
        ["poster"]
    )

    result["backdrop"] = first_existing(
        df,
        ["backdrop"]
    )

    result["trailer"] = first_existing(
        df,
        ["trailerId"]
    )

    result["popularity"] = first_existing(
        df,
        ["popularity"]
    )

    result["budget_crores"] = first_existing(
        df,
        ["budget_crores"]
    )

    result["revenue_crores"] = first_existing(
        df,
        ["revenue_crores"]
    )

    result["production_company"] = ""

    result["release_date"] = ""

    result["source"] = "dataset_1"

    return result


# ============================================================
# DATASET 2
# ============================================================

def process_dataset_2(path):

    print("\nLoading Dataset 2...")

    df = pd.read_csv(path)

    print("Rows:", len(df))

    result = pd.DataFrame(index=df.index)

    result["movie_id"] = ""

    result["title"] = first_existing(
        df,
        ["movie title"]
    )

    result["imdb_id"] = first_existing(
        df,
        ["imdb id"]
    )

    result["overview"] = first_existing(
        df,
        ["plot"]
    )

    result["genres"] = first_existing(
        df,
        ["genres"]
    )

    result["director"] = first_existing(
        df,
        ["director"]
    )

    result["cast"] = first_existing(
        df,
        ["cast"]
    )

    result["language"] = first_existing(
        df,
        ["language", "languages"]
    )

    result["year"] = first_existing(
        df,
        ["year"]
    )

    result["rating"] = first_existing(
        df,
        ["rating"]
    )

    result["votes"] = first_existing(
        df,
        ["votes"]
    )

    result["runtime_minutes"] = first_existing(
        df,
        ["runtime"]
    )

    result["poster"] = first_existing(
        df,
        ["poster"]
    )

    result["backdrop"] = ""

    result["trailer"] = first_existing(
        df,
        ["trailer"]
    )

    result["popularity"] = ""

    result["budget_crores"] = ""

    result["revenue_crores"] = ""

    result["production_company"] = ""

    result["release_date"] = ""

    result["source"] = "dataset_2"

    return result


# ============================================================
# DATASET 3 — TAMIL DATASET
# ============================================================

def process_dataset_3(path):

    print("\nLoading Dataset 3...")

    df = pd.read_csv(path)

    print("Rows:", len(df))

    result = pd.DataFrame(index=df.index)

    result["movie_id"] = first_existing(
        df,
        ["index"]
    )

    result["title"] = first_existing(
        df,
        ["title", "tittle"]
    )

    result["imdb_id"] = ""

    result["overview"] = first_existing(
        df,
        ["overview"]
    )

    result["genres"] = first_existing(
        df,
        ["genre", "genres"]
    )

    result["director"] = first_existing(
        df,
        ["director"]
    )

    result["cast"] = first_existing(
        df,
        ["cast"]
    )

    # Dataset 3 is specifically Tamil.
    result["language"] = "Tamil"

    result["year"] = ""

    result["rating"] = ""

    result["votes"] = ""

    result["runtime_minutes"] = ""

    result["poster"] = ""

    result["backdrop"] = ""

    result["trailer"] = ""

    result["popularity"] = ""

    result["budget_crores"] = ""

    result["revenue_crores"] = ""

    result["production_company"] = ""

    result["release_date"] = ""

    result["source"] = "dataset_3_tamil"

    return result


# ============================================================
# DATASET 4 — NEWER MOVIES
# ============================================================

def process_dataset_4(path):

    print("\nLoading Dataset 4...")

    df = pd.read_csv(path)

    print("Rows:", len(df))

    result = pd.DataFrame(index=df.index)

    result["movie_id"] = first_existing(
        df,
        ["Movie_ID"]
    )

    result["title"] = first_existing(
        df,
        ["Title"]
    )

    result["imdb_id"] = ""

    result["overview"] = first_existing(
        df,
        ["Overview"]
    )

    result["genres"] = first_existing(
        df,
        ["Genres"]
    )

    result["director"] = first_existing(
        df,
        ["Director"]
    )

    result["cast"] = first_existing(
        df,
        ["Cast"]
    )

    result["language"] = ""

    result["year"] = first_existing(
        df,
        ["Release_Year"]
    )

    result["rating"] = first_existing(
        df,
        ["Vote_Average"]
    )

    result["votes"] = first_existing(
        df,
        ["Vote_Count"]
    )

    result["runtime_minutes"] = first_existing(
        df,
        ["Runtime_Minutes"]
    )

    result["poster"] = ""

    result["backdrop"] = ""

    result["trailer"] = ""

    result["popularity"] = first_existing(
        df,
        ["Popularity_Score"]
    )

    result["budget_crores"] = first_existing(
        df,
        ["Budget_Crores"]
    )

    result["revenue_crores"] = first_existing(
        df,
        ["Revenue_Crores"]
    )

    result["production_company"] = first_existing(
        df,
        ["Production_Company"]
    )

    result["release_date"] = first_existing(
        df,
        ["Release_Date"]
    )

    result["source"] = "dataset_4"

    return result


# ============================================================
# CLEAN STANDARDIZED DATA
# ============================================================

def clean_master_dataframe(df):

    print("\nCleaning standardized data...")

    # -----------------------------
    # Clean text columns
    # -----------------------------

    text_columns = [
        "title",
        "imdb_id",
        "overview",
        "genres",
        "director",
        "cast",
        "language",
        "poster",
        "backdrop",
        "trailer",
        "production_company",
        "release_date",
        "source"
    ]

    for column in text_columns:

        df[column] = df[column].apply(clean_text)

    # -----------------------------
    # Clean title
    # -----------------------------

    df["title"] = df["title"].apply(clean_title)

    # -----------------------------
    # Numeric columns
    # -----------------------------

    numeric_columns = [
        "year",
        "rating",
        "votes",
        "runtime_minutes",
        "popularity",
        "budget_crores",
        "revenue_crores"
    ]

    for column in numeric_columns:

        df[column] = numeric_column(df[column])

    # -----------------------------
    # Fix year
    # -----------------------------

    df["year"] = df["year"].fillna(0).astype(int)

    # -----------------------------
    # Fix IMDb IDs
    # -----------------------------

    df["imdb_id"] = df["imdb_id"].str.lower().str.strip()

    # Remove invalid IMDb IDs

    invalid_imdb = [
        "",
        "nan",
        "none",
        "null"
    ]

    df.loc[
        df["imdb_id"].isin(invalid_imdb),
        "imdb_id"
    ] = ""

    # -----------------------------
    # Normalize language
    # -----------------------------

    df["language"] = (
        df["language"]
        .str.replace("[", "", regex=False)
        .str.replace("]", "", regex=False)
        .str.replace("'", "", regex=False)
        .str.replace('"', "", regex=False)
        .str.strip()
    )

    # -----------------------------
    # Remove rows without title
    # -----------------------------

    df = df[
        df["title"].str.len() > 0
    ].copy()

    # -----------------------------
    # Remove exact duplicate IMDb IDs
    # -----------------------------

    imdb_mask = (
        df["imdb_id"].notna()
        & (df["imdb_id"] != "")
    )

    imdb_rows = df[imdb_mask].copy()

    imdb_rows = imdb_rows.drop_duplicates(
        subset=["imdb_id"],
        keep="first"
    )

    non_imdb_rows = df[~imdb_mask].copy()

    df = pd.concat(
        [imdb_rows, non_imdb_rows],
        ignore_index=True
    )

    # -----------------------------
    # Create normalized title
    # -----------------------------

    df["title_normalized"] = (
        df["title"]
        .apply(normalize_text)
    )

    # -----------------------------
    # Remove duplicate title + year
    # -----------------------------

    df = df.drop_duplicates(
        subset=[
            "title_normalized",
            "year"
        ],
        keep="first"
    )

    # -----------------------------
    # Remove helper column
    # -----------------------------

    df.drop(
        columns=["title_normalized"],
        inplace=True
    )

    # -----------------------------
    # Reset index
    # -----------------------------

    df.reset_index(
        drop=True,
        inplace=True
    )

    return df


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("MOVIE MASTER DATASET CREATION")
    print("=" * 60)

    # -----------------------------
    # Load and standardize datasets
    # -----------------------------

    df1 = process_dataset_1(DATASET_1)

    df2 = process_dataset_2(DATASET_2)

    df3 = process_dataset_3(DATASET_3)

    df4 = process_dataset_4(DATASET_4)

    # -----------------------------
    # Show individual counts
    # -----------------------------

    print("\nDataset sizes:")

    print("Dataset 1:", len(df1))
    print("Dataset 2:", len(df2))
    print("Dataset 3:", len(df3))
    print("Dataset 4:", len(df4))

    # -----------------------------
    # Merge
    # -----------------------------

    print("\nMerging datasets...")

    master = pd.concat(
        [
            df1,
            df2,
            df3,
            df4
        ],
        ignore_index=True
    )

    print(
        "Rows before deduplication:",
        len(master)
    )

    # -----------------------------
    # Clean + deduplicate
    # -----------------------------

    master = clean_master_dataframe(master)

    # -----------------------------
    # Sort by title
    # -----------------------------

    master = master.sort_values(
        by="title",
        ascending=True
    )

    master.reset_index(
        drop=True,
        inplace=True
    )

    # -----------------------------
    # Save
    # -----------------------------

    master.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    # -----------------------------
    # Statistics
    # -----------------------------

    print("\n" + "=" * 60)
    print("MASTER DATASET CREATED")
    print("=" * 60)

    print(
        "Final movie count:",
        len(master)
    )

    print(
        "Final columns:",
        len(master.columns)
    )

    print(
        "Saved to:",
        OUTPUT_FILE
    )

    # -----------------------------
    # Language statistics
    # -----------------------------

    print("\nLanguage distribution:")

    language_counts = (
        master["language"]
        .replace("", np.nan)
        .dropna()
        .str.split(",")
        .explode()
        .str.strip()
        .str.title()
        .value_counts()
    )

    print(
        language_counts.head(20)
    )

    # -----------------------------
    # Tamil count
    # -----------------------------

    tamil_mask = (
        master["language"]
        .str.lower()
        .str.contains("tamil", na=False)
    )

    print(
        "\nTamil-labelled movies:",
        tamil_mask.sum()
    )

    # -----------------------------
    # Show sample
    # -----------------------------

    print("\nSample movies:")

    print(
        master[
            [
                "title",
                "year",
                "language",
                "genres",
                "director"
            ]
        ].head(10).to_string(index=False)
    )

    print("\nDone!")


if __name__ == "__main__":
    main()