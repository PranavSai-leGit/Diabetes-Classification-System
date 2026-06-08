import pandas as pd

# Load Data

def load_data(path: str):

    try:
        return pd.read_csv(path)

    except FileNotFoundError:
        print("Dataset not found")
        return None
