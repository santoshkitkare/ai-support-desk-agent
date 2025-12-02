import pandas as pd


def extract_text_from_csv(path: str) -> str:
    df = pd.read_csv(path)
    # Simple: flatten all cells into text
    return "\n".join(
        df.astype(str).apply(lambda row: " | ".join(row.values), axis=1).tolist()
    )
