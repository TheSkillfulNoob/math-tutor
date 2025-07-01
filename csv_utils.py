import pandas as pd
import os
from io import StringIO


def read_or_create_csv(path, columns):
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame(columns=columns)


def save_csv_buffer(df):
    buf = StringIO()
    df.to_csv(buf, index=False)
    return buf.getvalue()

# Example: loading mastery levels
def load_levels(path):
    cols = ["topic","mastery"]
    return read_or_create_csv(path, cols)