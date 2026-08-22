import pandas as pd
import numpy as np
import re
import ast
import os

# ============================================================
# CONFIGURATION
# ============================================================

DATASET_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(DATASET_DIR, "master_movies.csv")

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
    if value.lower() in ("nan", "none", "null", "undefined"):
        return ""
    if value.startswith("[") and value.endswith("]"):
        try:
            parsed = ast.literal_eval(value)
            if isinstance(parsed, list):
                return ", ".join(str(x).strip() for x in parsed if str(x).strip())
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
    Clean movie title by removing trailing year patterns and colons.
    Examples:
    'Interstellar: (2014)' -> 'Interstellar'
    'Inception: (2010)' -> 'Inception'
    """
    value = clean_text(value)
    # Remove patterns like ': (2014)', '(2014)', ': 2014', etc.
    value = re.sub(r"\s*[:(]\s*\d{4}\s*\)?\s*$", "", value)
    value = re.sub(r"\s*\(?\d{4}\)?\s*$", "", value)
    value = re.sub(r"[:\s]+$", "", value)
    return value.strip()


def extract_year_from_title(value):
    """Extract release year if present inside raw title string."""
    if not value or pd.isna(value):
        return 0
    m = re.search(r"[:(]\s*(\d{4})\s*\)?", str(value))
    if m:
        try:
            yr = int(m.group(1))
            if 1900 <= yr <= 2030:
                return yr
        except Exception:
            pass
    return 0


def first_existing(df, columns):
    """Return the first column that exists in the dataframe."""
    for column in columns:
        if column in df.columns:
            return df[column]
    return pd.Series([""] * len(df), index=df.index)


def numeric_column(series):
    """Convert a column into numeric values. Invalid values become NaN."""
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
# DATASET 1 (Rich Global & Indian Dataset)
# ============================================================

def process_dataset_1(path):
    print("\nLoading Dataset 1 (Global & Indian)...")
    if not os.path.exists(path):
        print("Dataset 1 not found at:", path)
        return pd.DataFrame(columns=MASTER_COLUMNS)

    df = pd.read_csv(path, low_memory=False)
    print("Rows:", len(df))

    result = pd.DataFrame(index=df.index)

    # In dataset1.csv: 'movie title', 'imdb id', 'cast', 'plot', 'director', 'rating', 'genres', 'poster', 'language cinema', 'votes', 'year', 'runtime', 'languages', 'trailer'
    raw_titles = first_existing(df, ["movie title", "title"])
    result["title"] = raw_titles.apply(clean_title)
    
    # Year: use existing year column or extract from title
    years = numeric_column(first_existing(df, ["year", "release_year"]))
    extracted_years = raw_titles.apply(extract_year_from_title)
    result["year"] = years.fillna(extracted_years).fillna(0).astype(int)

    result["movie_id"] = first_existing(df, ["imdb id", "id"])
    result["imdb_id"] = first_existing(df, ["imdb id", "imdb_id"])
    result["overview"] = first_existing(df, ["plot", "overview"])
    result["genres"] = first_existing(df, ["genres", "genre"])
    result["director"] = first_existing(df, ["director"])
    result["cast"] = first_existing(df, ["cast"])

    # Language
    lang_cinema = first_existing(df, ["language cinema", "languages", "language"])
    result["language"] = lang_cinema

    result["rating"] = first_existing(df, ["rating"])
    result["votes"] = first_existing(df, ["votes"])
    result["runtime_minutes"] = first_existing(df, ["runtime", "runtime_minutes"])
    result["poster"] = first_existing(df, ["poster"])
    result["backdrop"] = ""
    result["trailer"] = first_existing(df, ["trailer", "trailerId"])
    result["popularity"] = ""
    result["budget_crores"] = ""
    result["revenue_crores"] = ""
    result["production_company"] = ""
    result["release_date"] = ""
    result["source"] = "dataset_1"

    return result


# ============================================================
# DATASET 2 (Curated Cinema Dataset)
# ============================================================

def process_dataset_2(path):
    print("\nLoading Dataset 2...")
    if not os.path.exists(path):
        print("Dataset 2 not found at:", path)
        return pd.DataFrame(columns=MASTER_COLUMNS)

    df = pd.read_csv(path, low_memory=False)
    print("Rows:", len(df))

    result = pd.DataFrame(index=df.index)

    # In dataset2.csv: 'index', 'tittle', 'genre', 'overview', 'director', 'cast'
    result["movie_id"] = first_existing(df, ["index", "id"])
    result["title"] = first_existing(df, ["tittle", "title", "movie title"]).apply(clean_title)
    result["imdb_id"] = ""
    result["overview"] = first_existing(df, ["overview", "plot"])
    result["genres"] = first_existing(df, ["genre", "genres"])
    result["director"] = first_existing(df, ["director"])
    result["cast"] = first_existing(df, ["cast"])
    result["language"] = "Tamil"
    result["year"] = 0
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
    result["source"] = "dataset_2"

    return result


# ============================================================
# DATASET 3 (Tamil Cinema Master)
# ============================================================

def process_dataset_3(path):
    print("\nLoading Dataset 3 (Tamil Master)...")
    if not os.path.exists(path):
        print("Dataset 3 not found at:", path)
        return pd.DataFrame(columns=MASTER_COLUMNS)

    df = pd.read_csv(path, low_memory=False)
    print("Rows:", len(df))

    result = pd.DataFrame(index=df.index)

    # In dataset3.csv: 'id', 'title', 'year', 'rating', 'votes', 'language', 'genres', 'runtime', 'runtime_minutes', 'director', 'cast', 'overview', 'poster', 'backdrop', 'trailerId', 'budget_crores', 'revenue_crores', 'popularity', 'imdb_id'
    result["movie_id"] = first_existing(df, ["id", "movie_id"])
    result["title"] = first_existing(df, ["title"]).apply(clean_title)
    result["imdb_id"] = first_existing(df, ["imdb_id"])
    result["overview"] = first_existing(df, ["overview"])
    result["genres"] = first_existing(df, ["genres"])
    result["director"] = first_existing(df, ["director"])
    result["cast"] = first_existing(df, ["cast"])
    result["language"] = first_existing(df, ["language"])
    result["year"] = numeric_column(first_existing(df, ["year"])).fillna(0).astype(int)
    result["rating"] = first_existing(df, ["rating"])
    result["votes"] = first_existing(df, ["votes"])
    result["runtime_minutes"] = first_existing(df, ["runtime_minutes", "runtime"])
    result["poster"] = first_existing(df, ["poster"])
    result["backdrop"] = first_existing(df, ["backdrop"])
    result["trailer"] = first_existing(df, ["trailerId", "trailer"])
    result["popularity"] = first_existing(df, ["popularity"])
    result["budget_crores"] = first_existing(df, ["budget_crores"])
    result["revenue_crores"] = first_existing(df, ["revenue_crores"])
    result["production_company"] = ""
    result["release_date"] = ""
    result["source"] = "dataset_3_tamil"

    return result


# ============================================================
# DATASET 4 (New Releases & Box Office Dataset)
# ============================================================

def process_dataset_4(path):
    print("\nLoading Dataset 4 (Box Office & Features)...")
    if not os.path.exists(path):
        print("Dataset 4 not found at:", path)
        return pd.DataFrame(columns=MASTER_COLUMNS)

    df = pd.read_csv(path, low_memory=False)
    print("Rows:", len(df))

    result = pd.DataFrame(index=df.index)

    # In dataset4.csv: 'Movie_ID', 'Title', 'Overview', 'Genres', 'Director', 'Cast', 'Production_Company', 'Release_Date', 'Release_Year', 'Runtime_Minutes', 'Budget_Crores', 'Revenue_Crores', 'Popularity_Score', 'Vote_Average', 'Vote_Count'
    result["movie_id"] = first_existing(df, ["Movie_ID", "id"])
    result["title"] = first_existing(df, ["Title", "title"]).apply(clean_title)
    result["imdb_id"] = ""
    result["overview"] = first_existing(df, ["Overview", "overview"])
    result["genres"] = first_existing(df, ["Genres", "genres"])
    result["director"] = first_existing(df, ["Director", "director"])
    result["cast"] = first_existing(df, ["Cast", "cast"])
    result["language"] = "Tamil"
    result["year"] = numeric_column(first_existing(df, ["Release_Year", "year"])).fillna(0).astype(int)
    result["rating"] = first_existing(df, ["Vote_Average", "rating"])
    result["votes"] = first_existing(df, ["Vote_Count", "votes"])
    result["runtime_minutes"] = first_existing(df, ["Runtime_Minutes"])
    result["poster"] = ""
    result["backdrop"] = ""
    result["trailer"] = ""
    result["popularity"] = first_existing(df, ["Popularity_Score", "popularity"])
    result["budget_crores"] = first_existing(df, ["Budget_Crores"])
    result["revenue_crores"] = first_existing(df, ["Revenue_Crores"])
    result["production_company"] = first_existing(df, ["Production_Company"])
    result["release_date"] = first_existing(df, ["Release_Date"])
    result["source"] = "dataset_4"

    return result


# ============================================================
# CLEAN & DEDUPLICATE MASTER DATAFRAME
# ============================================================

def clean_master_dataframe(df):
    print("\nCleaning standardized master data...")

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

    df["title"] = df["title"].apply(clean_title)

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

    df["year"] = df["year"].fillna(0).astype(int)

    # Normalize language
    df["language"] = (
        df["language"]
        .str.replace("[", "", regex=False)
        .str.replace("]", "", regex=False)
        .str.replace("'", "", regex=False)
        .str.replace('"', "", regex=False)
        .str.strip()
    )

    # Map cinema terms to clean language names
    lang_map = {
        "american": "English",
        "british": "English",
        "hollywood": "English",
        "bollywood": "Hindi",
        "kollywood": "Tamil",
        "tollywood": "Telugu",
        "mollywood": "Malayalam",
        "sandalwood": "Kannada"
    }
    for k, v in lang_map.items():
        mask = df["language"].str.lower() == k
        df.loc[mask, "language"] = v

    # Remove rows without title or with corrupt numeric titles
    df = df[df["title"].str.strip().str.len() > 0].copy()
    df = df[~df["title"].str.lower().isin(["nan", "none", "null", "untitled", "776724537"])].copy()

    # Deduplicate by normalized title + year (prefer entries with more overview/genres/director metadata)
    df["title_norm"] = df["title"].apply(normalize_text)
    df["meta_len"] = (
        df["overview"].str.len()
        + df["genres"].str.len() * 2
        + df["director"].str.len() * 2
        + df["cast"].str.len()
    )

    # Sort so most informative row comes first
    df = df.sort_values(by=["meta_len", "rating"], ascending=[False, False])

    # Deduplicate: exact title_norm + year
    df = df.drop_duplicates(subset=["title_norm", "year"], keep="first")

    # For titles with year 0, deduplicate against matching title_norm with known year
    known_year_titles = set(df[df["year"] > 0]["title_norm"])
    df = df[~((df["year"] == 0) & (df["title_norm"].isin(known_year_titles)))].copy()

    # Drop helper columns
    df.drop(columns=["title_norm", "meta_len"], inplace=True)

    # Sequential unique movie_id
    df.reset_index(drop=True, inplace=True)
    df["movie_id"] = range(1, len(df) + 1)

    return df


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 65)
    print("CINEX MASTER MOVIE DATASET CREATION")
    print("=" * 65)

    df1 = process_dataset_1(DATASET_1)
    df2 = process_dataset_2(DATASET_2)
    df3 = process_dataset_3(DATASET_3)
    df4 = process_dataset_4(DATASET_4)

    print("\nDataset sizes:")
    print("Dataset 1 (Global/Indian) :", len(df1))
    print("Dataset 2 (Curated)        :", len(df2))
    print("Dataset 3 (Tamil Master)   :", len(df3))
    print("Dataset 4 (Box Office)     :", len(df4))

    print("\nMerging datasets...")
    master = pd.concat([df3, df4, df1, df2], ignore_index=True)
    print("Total rows before deduplication:", len(master))

    master = clean_master_dataframe(master)

    # Sort alphabetically by title
    master = master.sort_values(by="title", ascending=True)
    master.reset_index(drop=True, inplace=True)
    master["movie_id"] = range(1, len(master) + 1)

    # Save master dataset
    master.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    print("\n" + "=" * 65)
    print("MASTER DATASET CREATED SUCCESSFULLY")
    print("=" * 65)
    print("Final movie count :", len(master))
    print("Final columns     :", len(master.columns))
    print("Saved to          :", OUTPUT_FILE)

    # Verify key target movies exist
    test_titles = ["Interstellar", "Inception", "Vada Chennai", "Vikram", "Jai Bhim", "Maharaja", "The Dark Knight", "Tenet"]
    print("\nTarget Movie Check:")
    for t in test_titles:
        found = master[master["title"].str.contains(f"^{re.escape(t)}$", case=False, na=False, regex=True)]
        if len(found) > 0:
            row = found.iloc[0]
            print(f"  [FOUND] '{row['title']}' ({row['year']}) | Lang: {row['language']} | Dir: {row['director']} | Genres: {row['genres']}")
        else:
            partial = master[master["title"].str.contains(re.escape(t), case=False, na=False)]
            if len(partial) > 0:
                row = partial.iloc[0]
                print(f"  [PARTIAL] '{row['title']}' ({row['year']}) | Lang: {row['language']} | Dir: {row['director']} | Genres: {row['genres']}")
            else:
                print(f"  [MISSING] '{t}'")

    print("\nSample movies (first 10):")
    print(master[["movie_id", "title", "year", "language", "genres", "director"]].head(10).to_string(index=False))


if __name__ == "__main__":
    main()