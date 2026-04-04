"""
Download/prepare the movie dataset for the application.
Ensures the CSV file is available in the data/ directory.
"""
import os
import shutil


DATA_DIR = "data"
CSV_FILENAME = "tmdb_top_movies_cleaned.csv"
SOURCE_PATH = CSV_FILENAME  # CSV in project root
TARGET_PATH = os.path.join(DATA_DIR, CSV_FILENAME)


def prepare_data():
    """Ensure the dataset is available in the data/ directory."""
    # Create data directory if it doesn't exist
    os.makedirs(DATA_DIR, exist_ok=True)

    if os.path.exists(TARGET_PATH):
        print(f"✓ Dataset already exists at {TARGET_PATH}")
        return True

    # Try copying from project root
    if os.path.exists(SOURCE_PATH):
        print(f"Copying dataset from {SOURCE_PATH} to {TARGET_PATH}...")
        shutil.copy2(SOURCE_PATH, TARGET_PATH)
        print(f"✓ Dataset ready at {TARGET_PATH}")
        return True

    print(
        f"✗ Dataset not found. Please place '{CSV_FILENAME}' in the project root "
        f"or '{DATA_DIR}/' directory.\n"
        f"  Download from: https://www.kaggle.com/datasets/ (TMDB Movies Dataset)"
    )
    return False


if __name__ == "__main__":
    prepare_data()
