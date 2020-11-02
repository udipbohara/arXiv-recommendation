from pathlib import Path
import pandas as pd

data_dir = Path('graph/calculated_similarities.parquet/')
full_df = pd.concat(
    pd.read_parquet(parquet_file)
    for parquet_file in data_dir.glob('*.parquet')
)
full_df.to_csv('similarities.csv', index=True)