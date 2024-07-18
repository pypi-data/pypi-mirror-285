from typing import Dict

import pandas as pd
from morphdb_utils.annotations import transform

# The `data` variable prepares the data for processing in the main functions.
# For more information, please read the documentation at https://docs.morphdb.io/dbutils
data: Dict[str, pd.DataFrame] = {}


# The main function runs on the cloud when you click "Run".
# It's used by the data pipeline on the canvas to execute your Directed Acyclic Graph (DAG).
@transform
def main(data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    # This is where you write your code.
    example = {
        "Name": ["John Doe", "Jane Smith", "Emily Zhang"],
        "Age": [28, 34, 22],
        "Occupation": ["Software Engineer", "Data Scientist", "Marketing Manager"],
    }
    return pd.DataFrame(example)
