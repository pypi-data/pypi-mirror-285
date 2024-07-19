from typing import Dict, Optional

import pandas as pd
from morphdb_utils.annotations import transform
from morphdb_utils.api import load_data, ref

# The `data` variable prepares the data for processing in the main functions.
# For more information, please read the documentation at https://docs.morphdb.io/dbutils
data: Dict[str, Optional[pd.DataFrame]] = {
    "example": load_data(ref("example_python_cell")),
    "tables": load_data(ref("execute_sql")),
}


# The main function runs on the cloud when you click "Run".
# It's used by the data pipeline on the canvas to execute your Directed Acyclic Graph (DAG).
@transform
def main(data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    # This is where you write your code.
    print(data)
    return pd.DataFrame()
