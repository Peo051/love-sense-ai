import pandas as pd
import json
from pathlib import Path

def load_raw_data(raw_dir: str) -> pd.DataFrame:
    """Load raw data from directory"""
    data_files = Path(raw_dir).glob("*.json")
    all_data = []
    
    for file in data_files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            all_data.extend(data)
    
    return pd.DataFrame(all_data)

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and preprocess data"""
    # Remove duplicates
    df = df.drop_duplicates(subset=['text'])
    
    # Remove empty texts
    df = df[df['text'].str.strip() != '']
    
    # Remove null values
    df = df.dropna()
    
    return df

def save_processed_data(df: pd.DataFrame, output_path: str):
    """Save processed data"""
    df.to_csv(output_path, index=False, encoding='utf-8')
    print(f"Saved {len(df)} samples to {output_path}")

if __name__ == "__main__":
    raw_dir = "training/datasets/raw"
    output_path = "training/datasets/processed/dataset.csv"
    
    print("Loading raw data...")
    df = load_raw_data(raw_dir)
    
    print("Cleaning data...")
    df = clean_data(df)
    
    print("Saving processed data...")
    save_processed_data(df, output_path)
