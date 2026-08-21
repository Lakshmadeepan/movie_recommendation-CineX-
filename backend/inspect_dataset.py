import os
import glob
import pandas as pd

# Set pandas display options for clean terminal output
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 20)
pd.set_option('display.width', 1000)

def find_dataset_files():
    possible_roots = [
        os.path.join(os.path.dirname(__file__), "..", "dataset"),
        os.path.join(os.path.dirname(__file__), "dataset"),
        "dataset",
        r"c:\Users\laksh\OneDrive\Desktop\cinex-movie-recommendation\dataset",
        r"c:\Users\laksh\Downloads\frontend_movie_recommendation\dataset"
    ]
    
    csv_files = []
    for root in possible_roots:
        if os.path.exists(root):
            for path in glob.glob(os.path.join(root, "**", "*.csv"), recursive=True):
                abs_path = os.path.abspath(path)
                if abs_path not in csv_files:
                    csv_files.append(abs_path)
    return csv_files

def inspect_csv(file_path: str):
    file_name = os.path.basename(file_path)
    print("=" * 80)
    print(f"DATASET INSPECTION: {file_name}")
    print(f"Full Path: {file_path}")
    print("=" * 80)

    try:
        df = pd.read_csv(file_path, low_memory=False)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return

    # 1. Number of rows and columns
    rows, cols = df.shape
    print(f"\n[1] Shape of Dataset:")
    print(f"    - Total Rows   : {rows:,}")
    print(f"    - Total Columns: {cols}")

    # 2. Column names
    print(f"\n[2] All Column Names ({len(df.columns)}):")
    for idx, col in enumerate(df.columns, start=1):
        print(f"    {idx:2d}. {col}")

    # 3. First 5 rows
    print(f"\n[3] First 5 Rows (Head):")
    print(df.head(5))

    # 4. Column data types
    print(f"\n[4] Column Data Types (dtypes):")
    for col, dtype in df.dtypes.items():
        print(f"    - {col:<30}: {dtype}")

    # 5. Missing values in every column
    print(f"\n[5] Missing Values (Null Counts & Percentages):")
    null_counts = df.isnull().sum()
    for col in df.columns:
        count = null_counts[col]
        pct = (count / rows) * 100 if rows > 0 else 0
        print(f"    - {col:<30}: {count:6,d} nulls ({pct:6.2f}%)")

    # 6. Duplicate rows
    duplicates = df.duplicated().sum()
    print(f"\n[6] Duplicate Rows:")
    print(f"    - Total duplicate rows: {duplicates:,}")

    # 7. Language-related columns analysis
    lang_cols = [c for c in df.columns if any(kw in c.lower() for kw in ['lang', 'origin', 'country'])]
    print(f"\n[7] Language / Origin Analysis:")
    if lang_cols:
        for col in lang_cols:
            print(f"\n    Top 15 values in column '{col}':")
            top_vals = df[col].value_counts(dropna=False).head(15)
            for val, cnt in top_vals.items():
                print(f"      * {str(val):<25}: {cnt:6,d} movies")
    else:
        print("    No explicit language column name found.")

    # 8. Genre-related columns analysis
    genre_cols = [c for c in df.columns if any(kw in c.lower() for kw in ['genre', 'category', 'type'])]
    print(f"\n[8] Genre / Category Analysis:")
    if genre_cols:
        for col in genre_cols:
            print(f"\n    Sample & Top values in column '{col}':")
            top_genres = df[col].value_counts(dropna=False).head(15)
            for val, cnt in top_genres.items():
                print(f"      * {str(val):<45}: {cnt:6,d} movies")
    else:
        print("    No explicit genre column name found.")

    print("\n" + "=" * 80 + "\n")

def main():
    csv_files = find_dataset_files()
    if not csv_files:
        print("No CSV files found in dataset/ folder.")
        return

    # Prioritize 'Movies (1970-2023).csv' first
    csv_files.sort(key=lambda p: (0 if "1970-2023" in os.path.basename(p) else 1, p))

    print(f"Found {len(csv_files)} CSV file(s) in dataset folder:\n")
    for f in csv_files:
        print(f" - {f}")
    print("\nStarting inspection...\n")

    for f in csv_files:
        inspect_csv(f)

if __name__ == "__main__":
    main()
