from typing import Dict

import pandas as pd
from morphdb_utils.annotations import transform
from morphdb_utils.api import get_file, ref

# The `data` variable prepares the data for processing in the main functions.
# For more information, please read the documentation at https://docs.morphdb.io/dbutils
data: Dict[str, pd.DataFrame] = {}


# The main function runs on the cloud when you click "Run".
# It's used by the data pipeline on the canvas to execute your Directed Acyclic Graph (DAG).
@transform
def main(data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    # This is where you write your code.
    print("====================================")
    print('get_file("/tmp")')
    root_dir = get_file("/tmp")
    print(root_dir)

    print("====================================")
    print('get_file("~/Downloads/")')
    home_dir = get_file("~/Downloads/")
    print(home_dir)

    print("====================================")
    print('get_file("morph.yaml")')
    morph_yaml = get_file("morph.yaml")
    print(morph_yaml)

    print("====================================")
    print('get_file(ref("example_python_cell"))')
    example_python_cell = get_file(ref("example_python_cell"))
    print(example_python_cell)

    return pd.DataFrame()
