from typing import Dict

import pandas as pd
from morphdb_utils.api import ref, send_email

# The `data` variable prepares the data for processing in the main functions.
# For more information, please read the documentation at https://docs.morphdb.io/dbutils
data: Dict[str, pd.DataFrame] = {}


# The main function runs on the cloud when you click "Run".
# It's used by the data pipeline on the canvas to execute your Directed Acyclic Graph (DAG).
def main(data: Dict[str, pd.DataFrame]) -> None:
    # This is where you write your code.
    print("====================================")
    print('send_email(ref("example_python_cell"), ...)')
    send_email(
        [ref("example_python_cell")],
        ["yuki.ogino@queue-inc.com"],
        "Hello, World!",
        "Hello, World!",
    )
