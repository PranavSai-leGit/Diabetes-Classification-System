import pandas as pd

# Load Data

def load_data(path: str):

    try:
        return pd.read_csv(path)

    except FileNotFoundError:
        print("Dataset not found")
        return None

    except pd.errors.EmptyDataError:
        print("Error: CSV file is empty")
        return None

    except pd.errors.ParserError:
        print("Error: Problem parsing CSV file")
        return None

    except Exception as e:
        print(f"Unexpected Error:{e}")
        return None