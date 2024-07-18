from typing import Dict

import pandas as pd
from morphdb_utils.annotations import transform
from morphdb_utils.api import read_dir

# The `data` variable prepares the data for processing in the main functions.
# For more information, please read the documentation at https://docs.morphdb.io/dbutils
data: Dict[str, pd.DataFrame] = {}


# The main function runs on the cloud when you click "Run".
# It's used by the data pipeline on the canvas to execute your Directed Acyclic Graph (DAG).
@transform
def main(data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    # This is where you write your code.
    print("====================================")
    print("read_dir()")
    default_dir = read_dir()
    print(default_dir)

    print("====================================")
    print('read_dir("/")')
    root_dir = read_dir("/")
    print(root_dir)

    print("====================================")
    print('read_dir("~")')
    home_dir = read_dir("~")
    print(home_dir)

    return pd.DataFrame()
