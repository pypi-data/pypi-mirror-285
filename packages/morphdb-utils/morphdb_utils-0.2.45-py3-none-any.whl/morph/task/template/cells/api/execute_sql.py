from typing import Dict

import pandas as pd
from morphdb_utils.annotations import transform
from morphdb_utils.api import execute_sql

# The `data` variable prepares the data for processing in the main functions.
# For more information, please read the documentation at https://docs.morphdb.io/dbutils
# The `execute_sql` function executes the specified SQL query and returns the result as a pandas dataframe.
data: Dict[str, pd.DataFrame] = {
    "tables": execute_sql(
        "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
    )
}


# The main function runs on the cloud when you click "Run".
# It's used by the data pipeline on the canvas to execute your Directed Acyclic Graph (DAG).
@transform
def main(data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    # This is where you write your code.

    # NOTE: 下記はmorph.yamlのexample_sql_cellにconnectionを追加した場合に動作する
    # connection_test = execute_sql(ref("example_sql_cell"))
    # print("connection_test", connection_test)

    return pd.DataFrame(data["tables"])
